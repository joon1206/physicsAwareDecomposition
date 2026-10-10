"""Exact sensible-species diffusion compatibility diagnostic, fixed public algebra."""
from pathlib import Path
import csv, json, math, sys
from caseFactory import make_case, header, field, solve
from campaign import change
from candidate_mixture_wave import version
from thermo_reference import RU
from foamio import read_field
ROOT=Path(__file__).resolve().parents[1]; STUDY=ROOT/'candidateStudy';RAW=STUDY/'data/raw'
W=28.0134;R=RU/W;P=101325.;T0=800.;U0=40.;D=.01;TF=100e-6;CP={'A':1000.,'B':2000.};RHO=P/(R*T0);MU=RHO*D
def composition(n,t):
    a=[.5+.2*math.cos(2*math.pi*((i+.5)/n-U0*t/.02))*math.exp(-D*(2*math.pi/.02)**2*t) for i in range(n)]
    return a,[1-y for y in a]
def run(mode,n,pr,dt=200e-9,compatible=None,revision=''):
    suffix='' if compatible is None else '_transport'+('On' if compatible else 'Off')
    name=f'DiffWave_{mode}_nx{n}_Pr{pr:g}_dt{dt:g}{suffix}{revision}';case=RAW/name
    for fname in ['wave_result.json','failure.json']:
        if (case/fname).exists():return json.loads((case/fname).read_text())
    if case.exists():raise RuntimeError('Retained incomplete '+str(case))
    make_case(name,'uniform',nx=n,ny=1,dt=dt,steps=round(TF/dt))
    info=json.loads((case/'case.json').read_text());info['species']=['A','B'];(case/'case.json').write_text(json.dumps(info,indent=2)+'\n')
    aa,bb=composition(n,0);field(case/'0/A',aa);field(case/'0/B',bb);field(case/'0/T',T0,'[0 0 0 1 0 0 0]');field(case/'0/U',(U0,0,0),'[0 1 -1 0 0 0 0]',True)
    (case/'constant/thermophysicalProperties').write_text(header('thermophysicalProperties')+'thermoType { type hePsiThermo; mixture reactingMixture; transport const; thermo hConst; energy sensibleEnthalpy; equationOfState perfectGas; specie specie; }\ninertSpecie B; chemistryReader foamChemistryReader; foamChemistryFile "<case>/constant/reactions"; foamChemistryThermoFile "<case>/constant/thermo";\n')
    (case/'constant/reactions').write_text(header('reactions')+'species (A B); reactions {}\n')
    (case/'constant/thermo').write_text(header('thermo')+'\n'.join(f'{s} {{ specie {{ molWeight {W}; }} thermodynamics {{ Cp {cp}; Hf 0; }} transport {{ mu {MU:.17g}; Pr {pr}; }} }}' for s,cp in CP.items())+'\n')
    change(case/'constant/chemistryProperties','chemistry','off');chem=case/'constant/chemistryProperties';chem.write_text(chem.read_text().replace('solver costOde','solver ode'))
    (case/'system/controlDict').open('a').write(f'\nenergyLedger true; cellEnergyLedger true; cellLedgerEvery 0; energyCorrection {mode};\n')
    exe='reactingEnergyBlockCandidates' if mode=='blockConservative' else 'reactingEnergyCandidates'
    if compatible is not None:
        if mode=='blockConservative':raise ValueError('The transport control has no block-pressure implementation')
        exe='reactingEnergyTransportCandidates'
        (case/'system/controlDict').open('a').write('\ncompatibleSpeciesHeatFlux '+('true' if compatible else 'false')+';\n')
    cfg=dict(name=name,mode=mode,kind='DiffWave',nx=n,nCells=n,dt=dt,TF=TF,steps=round(TF/dt),ranks=1,Pr=pr,D=D,mu=MU,Cp=CP,**version(exe),scope='Synthetic equal-W unequal-Cp nonreacting advection/diffusion; exact constant T,p,U with physical species enthalpy diffusion, not a flame benchmark')
    cfg['compatibleSpeciesHeatFlux']=compatible
    cfg['transportRevision']=revision
    (case/'wave_experiment.json').write_text(json.dumps(cfg,indent=2)+'\n')
    try:wall=solve(case,1,exe=exe,timeout=600)
    except RuntimeError as e:
        result={**cfg,'failed':True,'error':str(e)};(case/'failure.json').write_text(json.dumps(result,indent=2)+'\n');print('RETAINED FAILURE',name,flush=True);return result
    end=case/format(TF,'.12g');actual={f:read_field(end/f,n) for f in ['rho','T','p','A','B']};vel=read_field(end/'U',n);actual['Ux']=[u[0] for u in vel]
    ea,eb=composition(n,TF);exact=dict(rho=[RHO]*n,T=[T0]*n,p=[P]*n,Ux=[U0]*n,A=ea,B=eb);errors={}
    for f in actual:
        ds=[abs(x-y) for x,y in zip(actual[f],exact[f])];errors[f]=dict(L1=math.fsum(ds)/n,L2=math.sqrt(math.fsum(x*x for x in ds)/n),Linf=max(ds))
    v=.02*.008*.001/n
    E0=v*math.fsum(RHO*((CP['A']*a+CP['B']*b)*(T0-298.15)+U0*U0/2)-P for a,b in zip(aa,bb))
    Ef=v*math.fsum(actual['rho'][i]*((CP['A']*actual['A'][i]+CP['B']*actual['B'][i])*(actual['T'][i]-298.15)+math.fsum(x*x for x in vel[i])/2)-actual['p'][i] for i in range(n))
    with next(case.glob('**/cellEnergyLedger/*/totals_rank0000.csv')).open() as stream:budget=[{k:float(v) for k,v in row.items()} for row in csv.DictReader(stream)]
    result=dict(**cfg,wall=wall,errors=errors,signedEnergyDrift=(Ef-E0)/abs(E0),massDrift=(math.fsum(actual['rho'])/n-RHO)/RHO,
                sumYError=max(abs(a+b-1) for a,b in zip(actual['A'],actual['B'])),minY=min(actual['A']+actual['B']),maxLocalEnergyResidual=max(r['maxCellClosure'] for r in budget),maxEOSRelative=max(r['maxEOSRelative'] for r in budget),maxMomentumDeltaU=max(r['maxMomentumDeltaU'] for r in budget))
    if compatible is not None:
        result.update(maxExtraFluxNetStepEnergy=max(abs(r['DextraSensibleTransport']) for r in budget),
                      maxExtraFluxAbsStepEnergy=max(r['absExtraSensibleTransport'] for r in budget))
    (case/'wave_result.json').write_text(json.dumps(result,indent=2)+'\n');print(name,'T L1',errors['T']['L1'],'T Linf',errors['T']['Linf'],'E',result['signedEnergyDrift'],flush=True);return result
def main():
    action=sys.argv[1] if len(sys.argv)>1 else 'all'
    sizes=[32] if action=='pilot' or action.endswith('Pilot') else [32,64,128]
    for pr in [.7,1.]:
        for n in sizes:
            if action.startswith('transport'):
                for mode in ['none','conservativeState']:
                    for compatible in [False,True]:run(mode,n,pr,compatible=compatible,revision='_coupledSync' if 'Sync' in action else '')
            else:
                for mode in ['none','conservativeState','blockConservative']:run(mode,n,pr)
    rows=[json.loads(p.read_text()) for p in sorted(RAW.glob('DiffWave_*/wave_result.json'))];(STUDY/'data/processed/diffusion_wave.json').write_text(json.dumps(rows,indent=2)+'\n')
if __name__=='__main__':main()
