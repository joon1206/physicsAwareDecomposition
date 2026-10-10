"""Sequential, retained candidate screens and controlled thermochemical ablations."""
from pathlib import Path
import hashlib,json,math,re,sys
import shutil
from caseFactory import make_case,decompose,solve,command,field
from campaign import change
from thermo_reference import parse_nasa,ha,RU,ATOMIC
ROOT=Path(__file__).resolve().parents[1]
STUDY=ROOT/'candidateStudy'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def alter_formation(case,scale=1.,element_gauge=0.):
    path=case/'chemkin/therm.dat';nasa=parse_nasa(path);lines=path.read_text().splitlines()
    for i,line in enumerate(lines):
        if len(line)<80 or line[79]!='1':continue
        name=line[:18].strip().split()[0];spec=nasa[name]
        # An H-element reference shift conserves reaction heat for balanced reactions.
        ze=spec['elements'].get('H',0)*ATOMIC['H']/spec['w']
        g=(scale-1)*ha(spec,298.15)+element_gauge*ze
        for j,col in [(i+2,0),(i+3,30)]:
            value=float(lines[j][col:col+15])+g*spec['w']/RU
            replacement=f'{value:15.8E}';assert len(replacement)==15
            lines[j]=lines[j][:col]+replacement+lines[j][col+15:]
    path.write_text('\n'.join(lines)+'\n')
    altered=parse_nasa(path)
    delta=max(abs((ha(altered[s],1200)-ha(altered[s],298.15))-(ha(nasa[s],1200)-ha(nasa[s],298.15))) for s in nasa)
    return dict(scale=scale,elementGauge=element_gauge,maxSensibleEnthalpyRepresentationChange=delta,
      interpretation='scale changes reacting heat/equilibrium thermochemistry; elemental gauge leaves ideal balanced reaction physics invariant up to NASA text precision')
def run(kind='F',mode='none',dt=2e-6,steps=None,ranks=4,scale=1.,gauge=0.,outer=1,pc=1,tag='',cells=32,every=1,action='A0',exe='reactingEnergyCandidates',ode_rtol=None,ode_atol=None,profile=False,block_tolerance=None,compatible_heat_flux=None,transport_as=None,transport_ts=None,thermo_corrections=None,chemistry_solver=None,chemistry_path=None,native_extension_metadata=None,component_energy_tolerance=None):
    if exe not in ['reactingEnergyCandidates','reactingEnergyBlockCandidates','reactingEnergyTransportCandidates','reactingEnergyRoundoffCandidates']:
        raise ValueError('Unsupported candidate executable '+exe)
    if compatible_heat_flux is not None and exe!='reactingEnergyTransportCandidates':
        raise ValueError('The compatible heat-flux flag requires the separate transport control')
    name=f'{kind}_{mode}_dt{dt:g}_s{scale:g}_g{gauge:g}_o{outer}_p{pc}{tag}'
    case=STUDY/'data/raw'/name
    if (case/'result.json').exists() or (case/'failure.json').exists():return case
    if case.exists():raise RuntimeError('Incomplete evidence retained: '+str(case))
    steps=steps if steps is not None else round(240e-6/dt)
    case=make_case(name,'heldoutMoving' if kind=='F' else 'uniform',nx=cells,ny=8,dt=dt,steps=steps,action=action)
    sol=case/'system/fvSolution';change(sol,'nCorrectors',pc);change(sol,'nOuterCorrectors',outer)
    control=case/'system/controlDict'
    control.open('a').write(f'\nenergyLedger true; cellEnergyLedger true; cellLedgerEvery {every}; energyCorrection {mode};\n')
    if compatible_heat_flux is not None:
        control.open('a').write('\ncompatibleSpeciesHeatFlux '+('true' if compatible_heat_flux else 'false')+';\n')
    if component_energy_tolerance is not None:
        if exe!='reactingEnergyRoundoffCandidates':raise ValueError('Component tolerance requires its separate executable')
        control.open('a').write('\ncomponentEnergyTolerance '+('true' if component_energy_tolerance else 'false')+';\n')
    if thermo_corrections is not None:
        change(control,'padThermoCorrections',thermo_corrections)
    if block_tolerance is not None:control.open('a').write(f'blockPressureTolerance {block_tolerance:.17g};\n')
    if mode=='scalarDensity':
        schemes=case/'system/fvSchemes';txt=schemes.read_text().replace('divSchemes\n{','divSchemes\n{\n    div(phi,deltaH) Gauss upwind;');schemes.write_text(txt)
    info=json.loads((case/'case.json').read_text())
    if kind=='A':
        field(case/'0/T',800.,'[0 0 0 1 0 0 0]');field(case/'0/U',(0,0,0),'[0 1 -1 0 0 0 0]',True)
        change(case/'constant/chemistryProperties','chemistry','off')
        for s in info['species']:field(case/'0'/s,1. if s=='N2' else 0.)
    elif kind=='B':
        field(case/'0/T',1100.,'[0 0 0 1 0 0 0]');field(case/'0/U',(0,0,0),'[0 1 -1 0 0 0 0]',True)
    elif kind=='Mix':
        change(case/'constant/chemistryProperties','chemistry','off')
        ts=[800+40*math.sin(2*math.pi*(i%cells+.5)/cells) for i in range(cells*8)]
        ys=[.1+.03*math.sin(2*math.pi*(i%cells+.5)/cells) for i in range(cells*8)]
        field(case/'0/T',ts,'[0 0 0 1 0 0 0]');field(case/'0/U',(40,0,0),'[0 1 -1 0 0 0 0]',True)
        for s in info['species']:field(case/'0'/s,ys if s=='H2' else [1-y for y in ys] if s=='N2' else 0.)
    thermo=alter_formation(case,scale,gauge) if scale!=1 or gauge else dict(scale=1.,elementGauge=0.,maxSensibleEnthalpyRepresentationChange=0.)
    if transport_as is not None:
        transport=case/'chemkin/transportProperties';text=transport.read_text()
        text,count=re.subn(r'(\bAs\s+)[^;]+;',lambda m:m[1]+format(transport_as,'.17g')+';',text)
        if count!=1:raise RuntimeError('Expected exactly one shared Sutherland As coefficient')
        if transport_ts is not None:
            text,count=re.subn(r'(\bTs\s+)[^;]+;',lambda m:m[1]+format(transport_ts,'.17g')+';',text)
            if count!=1:raise RuntimeError('Expected exactly one shared Sutherland Ts coefficient')
        transport.write_text(text)
    if ode_rtol is not None:change(case/'constant/chemistryProperties','relTol',ode_rtol)
    if ode_atol is not None:change(case/'constant/chemistryProperties','absTol',ode_atol)
    if chemistry_solver is not None:
        chemistry=case/'constant/chemistryProperties';text=chemistry.read_text()
        if text.count('solver costOde')!=1:raise RuntimeError('Expected the factory native chemistry solver')
        chemistry.write_text(text.replace('solver costOde','solver '+chemistry_solver))
        if chemistry_path is not None:chemistry.open('a').write(f'odeThermalPath {chemistry_path};\n')
        if chemistry_solver=='cvOde':control.write_text(control.read_text().replace('libs (','libs ("libcvChemistry.so" '))
    application=ROOT/'applications'/exe
    source={p.name:sha(p) for p in application.iterdir() if p.suffix in ['.H','.C']}
    version=hashlib.sha256(json.dumps(source,sort_keys=True).encode()).hexdigest()
    snapshot=STUDY/'sourceSnapshots'/version
    if not snapshot.exists():
        snapshot.mkdir(parents=True)
        for p in application.iterdir():
            if p.suffix in ['.H','.C']:shutil.copy2(p,snapshot/p.name)
        shutil.copytree(application/'Make',snapshot/'Make',ignore=shutil.ignore_patterns('linux*'))
    config=dict(name=name,kind=kind,mode=mode,dt=dt,steps=steps,ranks=ranks,nCells=info['nCells'],nCorrectors=pc,nOuterCorrectors=outer,
        formationAblation=thermo,source=source,sourceSnapshot=str(snapshot.relative_to(ROOT)),executable=exe,executableSHA256=sha(ROOT/'build/bin'/exe),action=action,odeRelativeTolerance=ode_rtol,odeAbsoluteTolerance=ode_atol,MPIProfile=profile,blockPressureTolerance=block_tolerance)
    config['compatibleSpeciesHeatFlux']=compatible_heat_flux
    config['transportSutherlandOverride']=None if transport_as is None else dict(As=transport_as,Ts=transport_ts)
    config['padThermoCorrections']=thermo_corrections
    config['componentEnergyTolerance']=component_energy_tolerance
    config['chemistrySolverOverride']=chemistry_solver;config['odeThermalPath']=chemistry_path
    if native_extension_metadata:
        if set(native_extension_metadata)&set(config):raise ValueError('Extension metadata overwrites native case metadata')
        config.update(native_extension_metadata)
    (case/'experiment.json').write_text(json.dumps(config,indent=2)+'\n')
    decompose(case,ranks)
    try:
        wall=solve(case,ranks,exe=exe,timeout=900,profile=profile)
        command(['mpirun','--bind-to','core','--map-by','core','--nooversubscribe','-np',str(ranks),'padNativeInventory']+(['-parallel'] if ranks>1 else [])+['-time','0:'],case,case/'inventory.log')
    except RuntimeError as error:
        (case/'failure.json').write_text(json.dumps({**config,'error':str(error)},indent=2)+'\n')
        print('RETAINED FAILURE',name,flush=True);return case
    (case/'result.json').write_text(json.dumps({**config,'solverWall':wall},indent=2)+'\n')
    print('EXECUTED',name,'wall',round(wall,3),flush=True);return case
def main():
    if len(sys.argv)>1 and sys.argv[1]=='pilot':
        run(kind='A',ranks=1,steps=2,tag='_pilot');run(steps=2,tag='_pilot');return
    if len(sys.argv)>1 and sys.argv[1]=='ablations':
        for kind in ['Mix','B','F']:
            for scale in [1.,0.,.5]:run(kind=kind,ranks=1 if kind=='B' else 4,scale=scale,every=4)
        run(kind='F',gauge=1e7,every=4)
        for dt in [1e-6,.5e-6,.25e-6]:run(dt=dt,every=round(2e-6/dt))
        return
    modes=['none','localInternal','scalarDensity']
    for mode in modes:
        for kind in ['A','B','F']:
            run(kind=kind,mode=mode,ranks=1 if kind in ['A','B'] else 4,steps=20 if kind=='A' else None,every=4)
        run(mode=mode,dt=1e-6,every=8)
if __name__=='__main__':main()
