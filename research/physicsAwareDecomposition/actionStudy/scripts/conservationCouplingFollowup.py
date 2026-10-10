"""Matched time/pressure controls after the independent budget sweeps."""
import csv
import json
import re
from caseFactory import ROOT, make_case, decompose, solve, command, latest_time
from mapping import assemble


def main():
    records=[]
    # Existing same-grid fine-time and four-pressure-corrector pilots bound
    # this local work. The second halving tests the observed convergence trend.
    for dt in [.0625e-6,.03125e-6]:
        name=f'conservationCoupling/moving_dt{dt}_pressure4'
        case=ROOT/'data/raw'/name
        if not (case/'manifest.json').exists():
            make_case(name,'heldoutMoving',nx=32,ny=8,dt=dt,steps=round(.00024/dt))
            path=case/'system/fvSolution'
            text,count=re.subn(r'(\bnCorrectors\s+)\d+',r'\g<1>4',path.read_text())
            assert count==1;path.write_text(text)
            decompose(case,4)
            wall=solve(case,4,timeout=900)
            (case/'manifest.json').write_text(json.dumps(dict(dt=dt,nCorrectors=4,nOuterCorrectors=1,solverWall=wall)))
            print('MEASURED coupled conservation control',dt,wall,flush=True)
        command(['mpirun','--bind-to','core','--map-by','core','--nooversubscribe','-np','4','padNativeInventory','-parallel','-time','0:'],case,case/'inventory.log')
        rank=[]
        for path in case.glob('processor*/postProcessing/inventory/rank*.csv'):
            with path.open() as stream:rank.extend({k:float(v) for k,v in row.items()} for row in csv.DictReader(stream))
        totals=[]
        for t in sorted({r['time'] for r in rank}):
            group=[r for r in rank if r['time']==t]
            row={k:sum(r[k] for r in group) for k in group[0] if k not in ['time','rank','nCells','minT','maxT','sumYError']}
            row['time']=t;totals.append(row)
        initial,end=totals[0],totals[-1]
        T=assemble(case,latest_time(case,True),'T',256)
        row=dict(nx=32,ny=8,dt=dt,nCorrectors=4,nOuterCorrectors=1,initial=initial,end=end,Tmax=max(T),
                 relativeMassDrift=(end['mass']-initial['mass'])/initial['mass'],
                 relativeEnergyDrift=(end['totalEnergy']-initial['totalEnergy'])/abs(initial['totalEnergy']),
                 path=str(case.relative_to(ROOT)),scope='Diagnostic only; matched fine physical timestep plus pressure coupling, no controller refit or replacement of the original performance dataset.')
        records.append(row)
        (ROOT/'data/processed/conservation_coupling_followup.json').write_text(json.dumps(records,indent=2))
        print('COUPLED CONSERVATION',row['relativeMassDrift'],row['relativeEnergyDrift'],flush=True)


if __name__=='__main__':main()
