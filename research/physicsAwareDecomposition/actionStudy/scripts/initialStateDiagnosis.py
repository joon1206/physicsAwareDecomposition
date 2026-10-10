"""Test whether missing initial psi.oldTime explains the mass offset."""
import csv
import json
from caseFactory import ROOT,PAD,make_case,decompose,set_control,solve,command


def main():
    command(['bash',PAD/'actionStudy/scripts/buildInitialState.sh'],PAD,
            ROOT/'data/raw/build/initialStateBuildDriver.log',timeout=600)
    from fluxDiagnosis import main as flux_diagnosis
    flux_diagnosis()
    records=[]
    for dt in [2e-6,.25e-6]:
        for variant,exe in [('nativeInitialization','reactingFoamPADRestart'),
                            ('initialPsiPreserved','reactingFoamPADInitialState')]:
            name=f'initialState/{variant}_dt{dt}';case=ROOT/'data/raw'/name
            if not (case/'manifest.json').exists():
                make_case(name,'heldoutMoving',nx=32,ny=8,dt=dt,steps=2)
                set_control(case,dt=dt,steps=2,write_interval=1,restart_state=True)
                decompose(case,4);wall=solve(case,4,exe=exe)
                (case/'manifest.json').write_text(json.dumps(dict(dt=dt,variant=variant,solverWall=wall,steps=2)))
            command(['mpirun','--bind-to','core','--map-by','core','--nooversubscribe','-np','4','padNativeInventory','-parallel','-time','0:'],case,case/'inventory.log')
            rank=[]
            for path in case.glob('processor*/postProcessing/inventory/rank*.csv'):
                with path.open() as stream:rank.extend({k:float(v) for k,v in row.items()} for row in csv.DictReader(stream))
            totals=[]
            for t in sorted({r['time'] for r in rank}):
                group=[r for r in rank if r['time']==t]
                totals.append(dict(time=t,mass=sum(r['mass'] for r in group),totalEnergy=sum(r['totalEnergy'] for r in group)))
            assert len(totals)==3
            initial=totals[0]['mass']
            for row in totals:row['relativeMassDrift']=(row['mass']-initial)/initial
            record=dict(dt=dt,variant=variant,inventories=totals,path=str(case.relative_to(ROOT)))
            records.append(record);print('INITIAL STATE',variant,dt,[r['relativeMassDrift'] for r in totals],flush=True)
    fixed=[r for r in records if r['variant']=='initialPsiPreserved']
    native=[r for r in records if r['variant']=='nativeInitialization']
    passed=all(max(abs(s['relativeMassDrift']) for s in r['inventories'])<1e-9 for r in fixed)
    result=dict(records=records,initialMassConservationPassed=passed,
                originalInitializationShowsOffset=all(abs(r['inventories'][1]['relativeMassDrift'])>1e-8 for r in native),
                performanceDataChanged=False,
                scope='Two-step initialization diagnosis only. The separate executable preallocates psi.oldTime before the first initial thermodynamic update. It is not used for the frozen oracle/controller performance data, and does not by itself prove long-time energy or flame convergence.')
    (ROOT/'data/processed/initial_state_diagnosis.json').write_text(json.dumps(result,indent=2))
    if not passed:raise RuntimeError('Initial coefficient hypothesis failed; retain and investigate.')


if __name__=='__main__':main()
