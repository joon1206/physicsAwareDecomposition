"""Native mass/species/energy inventories on actual four-action endpoints."""
import csv,json,statistics
from analysis import ROOT
from caseFactory import command

def main():
    rows=json.loads((ROOT/'data/processed/oracle_raw.json').read_text());out=[]
    for row in rows:
        if row['repeat']!=0 or row['checkpoint']!='4e-05' or row['horizonSteps'] not in [20 if row['regime']=='chemistryDominated' else 80]:continue
        case=ROOT/row['relativeDirectory']
        command(['mpirun','--bind-to','core','--map-by','core','--nooversubscribe','-np','4','padNativeInventory','-parallel','-time','0:'],case,case/'inventory.log')
        ranks=[]
        for f in case.glob('processor*/postProcessing/inventory/rank*.csv'):
            with f.open() as stream:ranks.extend({k:float(v) for k,v in r.items()} for r in csv.DictReader(stream))
        times=sorted(set(r['time'] for r in ranks));snapshots=[]
        for t in times:
            group=[r for r in ranks if r['time']==t]
            totals={k:sum(r[k] for r in group) for k in group[0] if k not in ['rank','time','nCells','minT','maxT','sumYError']}
            totals.update(time=t,sumYError=max(r['sumYError'] for r in group));snapshots.append(totals)
        first,last=snapshots[0],snapshots[-1]
        out.append(dict(regime=row['regime'],action=row['action'],checkpoint=row['checkpoint'],endTime=last['time'],snapshots=snapshots,
            relativeMassDrift=(last['mass']-first['mass'])/first['mass'],
            relativeEnergyDrift=(last['totalEnergy']-first['totalEnergy'])/max(abs(first['totalEnergy']),1e-30)))
    (ROOT/'data/processed/action_inventories.json').write_text(json.dumps(out,indent=2))
    print('VERIFIED native budgets',len(out),'representative action trajectories')

if __name__=='__main__':main()
