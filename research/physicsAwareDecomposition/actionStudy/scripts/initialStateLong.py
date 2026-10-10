"""Does the initialization-only repair change the full physical budget?"""
import csv,json,re
from caseFactory import ROOT,make_case,decompose,solve,command,latest_time
from mapping import assemble

def main():
    records=[]
    for dt,correctors in [(2e-6,1),(.03125e-6,4)]:
        name=f'initialStateLong/moving_dt{dt}_pressure{correctors}'
        case=ROOT/'data/raw'/name
        if not (case/'manifest.json').exists():
            make_case(name,'heldoutMoving',nx=32,ny=8,dt=dt,steps=round(.00024/dt))
            path=case/'system/fvSolution'
            text,count=re.subn(r'(\bnCorrectors\s+)\d+',lambda m:m[1]+str(correctors),path.read_text())
            assert count==1;path.write_text(text)
            decompose(case,4)
            wall=solve(case,4,exe='reactingFoamPADInitialState',timeout=900)
            (case/'manifest.json').write_text(json.dumps(dict(dt=dt,nCorrectors=correctors,nOuterCorrectors=1,solverWall=wall,
                executable='reactingFoamPADInitialState',performanceDataChanged=False)))
            print('MEASURED long initialization control',dt,correctors,wall,flush=True)
        command(['mpirun','--bind-to','core','--map-by','core','--nooversubscribe','-np','4','padNativeInventory','-parallel','-time','0:'],case,case/'inventory.log')
        ranks=[]
        for path in case.glob('processor*/postProcessing/inventory/rank*.csv'):
            with path.open() as stream:ranks.extend({k:float(v) for k,v in row.items()} for row in csv.DictReader(stream))
        totals=[]
        for t in sorted({r['time'] for r in ranks}):
            group=[r for r in ranks if r['time']==t]
            totals.append(dict(time=t,mass=sum(r['mass'] for r in group),totalEnergy=sum(r['totalEnergy'] for r in group)))
        initial,end=totals[0],totals[-1]
        T=assemble(case,latest_time(case,True),'T',256)
        row=dict(dt=dt,nCorrectors=correctors,nOuterCorrectors=1,nx=32,ny=8,initial=initial,end=end,Tmax=max(T),
                 relativeMassDrift=(end['mass']-initial['mass'])/initial['mass'],
                 relativeEnergyDrift=(end['totalEnergy']-initial['totalEnergy'])/abs(initial['totalEnergy']),
                 path=str(case.relative_to(ROOT)),scope='Full 240 μs diagnostic using initialization-only correction. Frozen performance trials and their eligibility unchanged.')
        records.append(row)
        (ROOT/'data/processed/initial_state_long.json').write_text(json.dumps(dict(records=records,performanceDataChanged=False),indent=2))
        print('LONG INITIALIZATION BUDGET',row['relativeMassDrift'],row['relativeEnergyDrift'],flush=True)
    assert all(abs(r['relativeMassDrift'])<1e-9 for r in records)

if __name__=='__main__':main()
