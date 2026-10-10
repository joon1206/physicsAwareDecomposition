"""Additional independent homogeneous Cv source controls, retained separately."""
from pathlib import Path
import csv,json,math
from caseFactory import make_case,field,solve,command
from campaign import change
from candidate_cv_chemistry import chemistry_version
from candidate_mixture_wave import version
from candidate_analyze import totals
from analyze import summarize
from foamio import read_field
ROOT=Path(__file__).resolve().parents[1];STUDY=ROOT/'candidateStudy';RAW=STUDY/'data/raw';TF=240e-6
def run(ref,mode,exe='reactingEnergyCandidates',component=None,tag=''):
    prefix='CvRegime' if component is None else 'RoundoffCvRegime'
    tag=tag+('' if component is None else '_component'+('On' if component else 'Off'))
    name=f"{prefix}_{ref['label']}_{mode}_dt1e-06_dfdt0{tag}";case=RAW/name
    for filename in ['regime_result.json','failure.json']:
        if (case/filename).exists():return json.loads((case/filename).read_text())
    if case.exists():raise RuntimeError('Retained incomplete '+str(case))
    make_case(name,'uniform',nx=8,ny=1,dt=1e-6,steps=240)
    field(case/'0/T',ref['Tinitial'],'[0 0 0 1 0 0 0]')
    field(case/'0/p',ref['pInitial'],'[1 -1 -2 0 0 0 0]')
    field(case/'0/U',(0,0,0),'[0 1 -1 0 0 0 0]',True)
    chemistry=case/'constant/chemistryProperties';chemistry.write_text(chemistry.read_text().replace('solver costOde','solver cvOde'))
    chemistry.open('a').write('odeThermalPath constantVolume;\n');change(chemistry,'relTol',1e-10);change(chemistry,'absTol',1e-16)
    control=case/'system/controlDict';control.write_text(control.read_text().replace('libs (','libs ("libcvChemistry.so" '))
    control.open('a').write(f'\nenergyLedger true; cellEnergyLedger true; cellLedgerEvery 0; energyCorrection {mode};\n')
    if component is not None:control.open('a').write('componentEnergyTolerance '+('true' if component else 'false')+';\n')
    cfg=dict(name=name,kind='CvRegime',regime=ref['label'],mode=mode,dt=1e-6,steps=240,nCells=8,ranks=1,
             Tinitial=ref['Tinitial'],pInitial=ref['pInitial'],odeThermalPath='constantVolume',
             odeRelativeTolerance=1e-10,odeAbsoluteTolerance=1e-16,matchedMechanismSHA256=ref['matchedMechanismSHA256'],
             **version(exe),**chemistry_version(),componentEnergyTolerance=component,scope='Declared additional homogeneous source regime; independent matched Cantera reference, no spatial/convergence/new-method claim.')
    (case/'experiment.json').write_text(json.dumps(cfg,indent=2)+'\n')
    try:
        wall=solve(case,1,exe=cfg['executable'],timeout=900)
        command(['padNativeInventory','-time','0:'],case,case/'inventory.log')
    except RuntimeError as e:
        failure=dict(cfg,error=str(e));(case/'failure.json').write_text(json.dumps(failure,indent=2)+'\n');print('RETAINED FAILURE',name,flush=True);return failure
    (case/'result.json').write_text(json.dumps(dict(cfg,solverWall=wall),indent=2)+'\n')
    result,_,_=summarize(case);local=totals(case);n=8;target=ref['records'][-1]['end'];errors={}
    species=json.loads((case/'case.json').read_text())['species']
    for f in ['T','p','rho']+species:
        values=read_field(case/format(TF,'.12g')/f,n);d=[abs(v-target[f]) for v in values]
        errors[f]=dict(L1=math.fsum(d)/n,L2=math.sqrt(math.fsum(x*x for x in d)/n),Linf=max(d))
    with next(case.glob('**/cvChemistry/rank0000.csv')).open() as stream:source=[{k:float(v) for k,v in row.items()} for row in csv.DictReader(stream)]
    result.update(errors=errors,referenceTemperatureToleranceContrast=ref['toleranceEndpointDifference']['T'],
                  maxCellClosure=max(r['maxCellClosure'] for r in local),maxEOSRelative=max(r['maxEOSRelative'] for r in local),
                  maxSourceRelativeMassChange=max(abs(r['rhoFinal']-r['rhoInitial'])/r['rhoInitial'] for r in source),
                  maxSourceRelativeEnergyChange=max(abs(r['energyFinal']-r['energyInitial'])/max(abs(r['energyInitial']),1.) for r in source),
                  minAcceptedConcentration=min(r['minConcentration'] for r in source))
    if component is not None:
        with next(case.glob('**/componentEnergyTolerance/*/rank0000.csv')).open() as stream:trace=[{k:float(v) for k,v in row.items()} for row in csv.DictReader(stream)]
        accepted=[r for r in trace if r['accepted']]
        result.update(maxAcceptedEnergyResidual=max(r['globalMaxResidual'] for r in accepted),maxAcceptedScaledResidual=max(r['globalMaxScaledResidual'] for r in accepted),
                      maxComponentAllowance=max(r['maxLocalAllowance'] for r in accepted),acceptedAboveOldCutoff=sum(r['globalMaxResidual']>=5e-18 for r in accepted))
    (case/'regime_result.json').write_text(json.dumps(result,indent=2)+'\n')
    print(name,'Terror',errors['T']['Linf'],'E',result['signedEnergyDrift'],flush=True);return result
def main():
    refs=json.loads((STUDY/'data/processed/cantera_cv_regimes.json').read_text());rows=[]
    for ref in refs:
        for mode in ['none','conservativeState']:rows.append(run(ref,mode))
    (STUDY/'data/processed/cv_chemistry_regimes.json').write_text(json.dumps(rows,indent=2)+'\n')
if __name__=='__main__':main()
