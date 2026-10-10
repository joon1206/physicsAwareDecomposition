"""New retained matched thermo-only controls, original applications unchanged."""
from pathlib import Path
import csv,json,math,shutil,sys
from caseFactory import make_case,decompose,solve,command,field
from campaign import change
from candidate_mixture_wave import version
from candidate_cv_chemistry import chemistry_version
from candidate_analyze import totals as cell_totals, CELL_TERMS
from analyze import summarize,fields,compare
from thermo_continuity import CONTROL,sha
ROOT=Path(__file__).resolve().parents[1];STUDY=ROOT/'candidateStudy';RAW=STUDY/'data/raw';P=STUDY/'data/processed'
def run(mode,dt,source,thermo):
    name=f'CleanThermo_{thermo}_{source}_{mode}_dt{dt:g}';case=RAW/name
    if (case/'result.json').exists() or (case/'failure.json').exists():return case
    if case.exists():raise RuntimeError('Retained incomplete '+str(case))
    make_case(name,'heldoutMoving',nx=32,ny=8,dt=dt,steps=round(240e-6/dt))
    shutil.copy2(CONTROL/f'{thermo}.dat',case/'chemkin/therm.dat')
    change(case/'system/fvSolution','nCorrectors',1);change(case/'system/fvSolution','nOuterCorrectors',1)
    control=case/'system/controlDict';control.open('a').write(f'\nenergyLedger true; cellEnergyLedger true; cellLedgerEvery 1; energyCorrection {mode};\n')
    extension={}
    if source=='CV':
        chemistry=case/'constant/chemistryProperties';chemistry.write_text(chemistry.read_text().replace('solver costOde','solver cvOde'))
        chemistry.open('a').write('odeThermalPath constantVolume;\n');change(chemistry,'relTol',1e-10);change(chemistry,'absTol',1e-16)
        control.write_text(control.read_text().replace('libs (','libs ("libcvChemistry.so" '));extension=chemistry_version()
    cfg=dict(name=name,kind='F',mode=mode,dt=dt,steps=round(240e-6/dt),nCells=256,ranks=4,nCorrectors=1,nOuterCorrectors=1,
             thermoControl=thermo,sourcePathControl=source,**version('reactingEnergyCandidates'),**extension,
             driverSHA256=sha(__file__),thermoSHA256=sha(case/'chemkin/therm.dat'),kineticsSHA256=sha(case/'chemkin/chem.inp'),
             controlManifestSHA256=sha(CONTROL/'manifest.json'),scope='Thermo-only matched sensitivity control. Exact native kinetics/transport/fields/discretization retained; equilibrium reverse rates may change with thermo. Walls excluded from cost claims.')
    (case/'experiment.json').write_text(json.dumps(cfg,indent=2)+'\n')
    decompose(case,4)
    try:
        wall=solve(case,4,exe='reactingEnergyCandidates',timeout=900)
        command(['mpirun','--bind-to','core','--map-by','core','--nooversubscribe','-np','4','padNativeInventory','-parallel','-time','0:'],case,case/'inventory.log')
    except RuntimeError as e:
        (case/'failure.json').write_text(json.dumps(dict(cfg,error=str(e)),indent=2)+'\n');print('RETAINED FAILURE',name,flush=True);return case
    (case/'result.json').write_text(json.dumps(dict(cfg,solverWall=wall),indent=2)+'\n');print('EXECUTED',name,flush=True);return case
def record(case,thermo,source,mode,dt):
    if (case/'failure.json').exists():return json.loads((case/'failure.json').read_text())
    r,b,_=summarize(case);local=cell_totals(case)
    r.update(thermoControl=thermo,sourcePathControl=source,cellCumulativeTerms={k:math.fsum(x.get(k,0) for x in local) for k in CELL_TERMS},
             maxCellClosure=max(x['maxCellClosure'] for x in local),maxCellGlobalClosure=max(abs(x['closure']) for x in local),
             maxEOSRelative=max(x['maxEOSRelative'] for x in local),meanTemperature=math.fsum(fields(case,4,240e-6,'T',256))/256)
    traces=[]
    for trace in case.glob('**/cvChemistry/rank*.csv'):
        with trace.open() as stream:traces.extend({k:float(v) for k,v in row.items()} for row in csv.DictReader(stream))
    if traces:
        errors=[abs(x['energyFinal']-x['energyInitial'])/max(abs(x['energyInitial']),1) for x in traces]
        r.update(sourceCalls=len(traces),failedSourceEnergyCalls=sum(e>1e-10 for e in errors),maxSourceRelativeEnergyChange=max(errors),
                 maxSourceEnergyChange=max(abs(x['energyFinal']-x['energyInitial']) for x in traces),sourceEnergyUnits='J/m3',sourceGate=1e-10,
                 maxSourceRelativeMassChange=max(abs(x['rhoFinal']-x['rhoInitial'])/x['rhoInitial'] for x in traces))
    else:r['sourceEnergyObservation']='Native costOde does not retain source endpoint energy traces; finite species/Qdot cancellation is measured separately in Dchemistry.'
    return r
def main():
    rows=[]
    for source,modes in [('native',['none']),('CV',['none','conservativeState'])]:
      for dt in [2e-6,1e-6]:
       for mode in modes:
        legacy=RAW/(f'F_{mode}_dt{dt:g}_s1_g0_o1_p1'+('_cvSource_rtol1e-10_dfdt0' if source=='CV' else ''))
        rows.append(record(legacy,'legacy',source,mode,dt))
        for thermo in ['HS','CpHS']:
            case=run(mode,dt,source,thermo);r=record(case,thermo,source,mode,dt)
            if 'signedEnergyDrift' in r:r['legacyFieldContrast']=compare(legacy,case)
            rows.append(r)
            print(r['name'],'E',r.get('signedEnergyDrift'),'densityPair',sum(r.get('cellCumulativeTerms',{}).get(k,0) for k in ['DrhoH','DrhoC']),'sourceFails',r.get('failedSourceEnergyCalls'),flush=True)
        (P/'clean_thermo_campaign.json').write_text(json.dumps(rows,indent=2)+'\n')
    print('Matched attribution records',len(rows),flush=True)
if __name__=='__main__':main()
