"""Retained native constant-volume source-path tests against matched Cantera."""
from pathlib import Path
import csv, hashlib, json, math, shutil, sys
from caseFactory import make_case, field, solve, command
from campaign import change
from candidate_mixture_wave import version
from candidate_screen import sha
from candidate_analyze import totals
from analyze import summarize
from foamio import read_field
ROOT=Path(__file__).resolve().parents[1];STUDY=ROOT/'candidateStudy';RAW=STUDY/'data/raw';TF=240e-6

def chemistry_version():
    app=ROOT/'src/cvChemistry';sources={str(p.relative_to(app)):sha(p) for p in [app/'cvOde.H',app/'cvChemistry.C',app/'Make/files',app/'Make/options']}
    digest=hashlib.sha256(json.dumps(sources,sort_keys=True).encode()).hexdigest();snapshot=STUDY/'chemistrySnapshots'/digest
    if not snapshot.exists():
        snapshot.mkdir(parents=True)
        for filename in sources:
            target=snapshot/filename;target.parent.mkdir(exist_ok=True);shutil.copy2(app/filename,target)
    return dict(chemistrySource=sources,chemistrySourceSnapshot=str(snapshot.relative_to(ROOT)),
                chemistryLibrary='libcvChemistry.so',chemistryLibrarySHA256=sha(ROOT/'build/lib/libcvChemistry.so'))

def run(mode,dt,rtol=1e-10,atol=1e-16,thermal_path='constantVolume'):
    prefix='CV' if thermal_path=='constantVolume' else 'CPFD'
    name=f'{prefix}_B_{mode}_dt{dt:g}_rtol{rtol:g}_dfdt0';case=RAW/name
    for filename in ['cv_result.json','failure.json']:
        if (case/filename).exists():return json.loads((case/filename).read_text())
    if case.exists():raise RuntimeError('Retained incomplete '+str(case))
    n=8;make_case(name,'uniform',nx=n,ny=1,dt=dt,steps=round(TF/dt))
    field(case/'0/T',1100.,'[0 0 0 1 0 0 0]');field(case/'0/U',(0,0,0),'[0 1 -1 0 0 0 0]',True)
    chemistry=case/'constant/chemistryProperties';chemistry.write_text(chemistry.read_text().replace('solver costOde','solver cvOde'))
    change(chemistry,'relTol',rtol);change(chemistry,'absTol',atol)
    chemistry.open('a').write(f'odeThermalPath {thermal_path};\n')
    control=case/'system/controlDict';control.write_text(control.read_text().replace('libs (','libs ("libcvChemistry.so" '))
    control.open('a').write(f'\nenergyLedger true; cellEnergyLedger true; cellLedgerEvery 0; energyCorrection {mode};\n')
    cfg=dict(name=name,kind=prefix+'_B',mode=mode,dt=dt,steps=round(TF/dt),nCells=n,nx=n,ranks=1,odeThermalPath=thermal_path,
             odeRelativeTolerance=rtol,odeAbsoluteTolerance=atol,**version('reactingEnergyCandidates'),**chemistry_version(),
             driverSHA256=sha(Path(__file__)),scope='Homogeneous fixed-volume native-source path control; established Cv physics with matched public NASA/H2 rates. No higher-order CFD or new-method claim.')
    (case/'experiment.json').write_text(json.dumps(cfg,indent=2)+'\n')
    try:
        wall=solve(case,1,exe=cfg['executable'],timeout=600)
        command(['padNativeInventory','-time','0:'],case,case/'inventory.log')
    except RuntimeError as e:
        result=dict(cfg,error=str(e),failed=True);(case/'failure.json').write_text(json.dumps(result,indent=2)+'\n');print('RETAINED FAILURE',name,flush=True);return result
    (case/'result.json').write_text(json.dumps(dict(cfg,solverWall=wall),indent=2)+'\n')
    record,_,_=summarize(case);local=totals(case)
    species=json.loads((case/'case.json').read_text())['species'];ref=json.loads((STUDY/'data/processed/cantera_reference.json').read_text())['records'][-1]['end'];errors={}
    for f in ['T','p','rho']+species:
        values=read_field(case/format(TF,'.12g')/f,n);ds=[abs(v-ref[f]) for v in values]
        errors[f]=dict(L1=math.fsum(ds)/n,L2=math.sqrt(math.fsum(d*d for d in ds)/n),Linf=max(ds))
    with next(case.glob('**/cvChemistry/rank0000.csv')).open() as stream:source=[{k:float(v) for k,v in row.items()} for row in csv.DictReader(stream)]
    record.update(errors=errors,maxCellClosure=max(r['maxCellClosure'] for r in local),maxEOSRelative=max(r['maxEOSRelative'] for r in local),
                  maxSourceRelativeMassChange=max(abs(r['rhoFinal']-r['rhoInitial'])/r['rhoInitial'] for r in source),
                  maxSourceRelativeEnergyChange=max(abs(r['energyFinal']-r['energyInitial'])/max(abs(r['energyInitial']),1.) for r in source),
                  maxSourcePressureSlotRelativeMismatch=max(abs(r['pIntegrated']-r['pEOS'])/r['pEOS'] for r in source),
                  minAcceptedConcentration=min(r['minConcentration'] for r in source),sourceCalls=len(source))
    (case/'cv_result.json').write_text(json.dumps(record,indent=2)+'\n');print(name,'Terror',errors['T']['Linf'],'E',record['signedEnergyDrift'],'sourceE',record['maxSourceRelativeEnergyChange'],flush=True);return record

def main():
    action=sys.argv[1] if len(sys.argv)>1 else 'all';pilot=action in ['pilot','pathPilot']
    if action=='reactingScreen':
        from candidate_screen import run as screen
        cases=[]
        for dt in [2e-6,1e-6]:
            for mode in ['none','conservativeState']:
              for path,label in [('constantPressure','cpFDSource'),('constantVolume','cvSource')]:
                case=screen(kind='F',mode=mode,dt=dt,ranks=4,every=0,tag=f'_{label}_rtol1e-10_dfdt0',
                            chemistry_solver='cvOde',chemistry_path=path,
                            ode_rtol=1e-10,ode_atol=1e-16,native_extension_metadata=chemistry_version())
                if (case/'failure.json').exists():cases.append(json.loads((case/'failure.json').read_text()));continue
                r,_,_=summarize(case);local=totals(case)
                from analyze import fields
                temp=fields(case,4,dt*r['steps'],'T',r['nCells'])
                r.update(meanTemperature=math.fsum(temp)/len(temp),maxCellClosure=max(x['maxCellClosure'] for x in local),maxEOSRelative=max(x['maxEOSRelative'] for x in local))
                source=[]
                for trace in case.glob('**/cvChemistry/rank*.csv'):
                    with trace.open() as stream:source.extend({k:float(v) for k,v in row.items()} for row in csv.DictReader(stream))
                r.update(maxSourceRelativeMassChange=max(abs(x['rhoFinal']-x['rhoInitial'])/x['rhoInitial'] for x in source),
                         maxSourceRelativeEnergyChange=max(abs(x['energyFinal']-x['energyInitial'])/max(abs(x['energyInitial']),1.) for x in source),
                         maxSourcePressureSlotRelativeMismatch=max(abs(x['pIntegrated']-x['pEOS'])/x['pEOS'] for x in source),
                         minAcceptedConcentration=min(x['minConcentration'] for x in source),sourceCalls=len(source))
                cases.append(r);print(r['name'],'meanT',r['meanTemperature'],'E',r['signedEnergyDrift'],flush=True)
        (STUDY/'data/processed/cv_reacting_screen.json').write_text(json.dumps(cases,indent=2)+'\n');return
    if action=='tolerance':
        for rtol in [1e-10,1e-12]:run('conservativeState',1e-6,rtol=rtol,atol=1e-16)
    for dt in ([] if action=='tolerance' else [1e-6] if pilot else [1e-6,.5e-6,.25e-6,.125e-6]):
        for mode in (['conservativeState'] if pilot else ['none','conservativeState']):
            for path in (['constantPressure','constantVolume'] if action=='pathPilot' else ['constantVolume']):run(mode,dt,thermal_path=path)
    rows=[json.loads(p.read_text()) for p in sorted(list(RAW.glob('CV_B_*/cv_result.json'))+list(RAW.glob('CPFD_B_*/cv_result.json')))]
    current=[r for r in rows if r['name'].endswith('_dfdt0')]
    data=dict(records=current,superseded=[r for r in rows if not r['name'].endswith('_dfdt0')],
              supersededReason='The earlier adapter returned the reaction RHS as the Rosenbrock explicit-time derivative. Autonomous ODESystem requires zero. Earlier raw cases remain retained and are excluded from claims.')
    (STUDY/'data/processed/cv_chemistry.json').write_text(json.dumps(data,indent=2)+'\n')
if __name__=='__main__':main()
