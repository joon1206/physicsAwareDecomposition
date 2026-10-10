"""Independent inventories, cellwise identities, ablations and screening gates."""
from pathlib import Path
import csv,json,math
from collections import defaultdict
from analyze import summarize,compare
ROOT=Path(__file__).resolve().parents[1];STUDY=ROOT/'candidateStudy'
CELL_TERMS=['Dpressure','Dkinetic','DrhoH','DrhoC','Dchemistry','DspeciesTransport','DspeciesResidual','Dequation','Dtransport','Dhistory','DpostH','DpostC']
def totals(case):
    groups=defaultdict(list)
    for fp in case.glob('**/cellEnergyLedger/*/totals_rank*.csv'):
        with fp.open() as f:
            for row in csv.DictReader(f):groups[float(row['time'])].append({k:float(v) for k,v in row.items()})
    out=[]
    for t,rows in sorted(groups.items()):
        r={'time':t,'ranks':len(rows)}
        for k in rows[0]:
            if k in ['time','rank','step']:continue
            r[k]=(max if k.startswith('max') else math.fsum)(x[k] for x in rows)
        out.append(r)
    return out
def main():
    results=[];alltotals={}
    for meta in sorted((STUDY/'data/raw').glob('*/result.json')):
        case=meta.parent;r,b,s=summarize(case);local=totals(case);alltotals[r['name']]=local
        r['cellCumulativeTerms']={k:math.fsum(x.get(k,0) for x in local) for k in CELL_TERMS}
        r['maxCellClosure']=max(x['maxCellClosure'] for x in local)
        r['maxCellGlobalClosure']=max(abs(x['closure']) for x in local)
        r['maxEOSRelative']=max(x['maxEOSRelative'] for x in local)
        r['maxMomentumDeltaU']=max(x['maxMomentumDeltaU'] for x in local)
        r['densityAbsoluteSpaceTimeNorm']=math.fsum(x['absDensityEnergy'] for x in local)
        r['sourceHeatConsistency']=max(abs(x['Dchemistry']) for x in local)
        r['localInventoryDifference']=math.fsum(x['DE'] for x in local)-(r['end']['E_stored']-r['initial']['E_stored'])
        r['screenGates']={'cellClosure':r['maxCellClosure']<1e-12,'globalClosure':r['maxCellGlobalClosure']<1e-12,
           'independentInventory':abs(r['independentNativeEnergyDifference'])<1e-12 and abs(r['thermoInventoryDifference'])<1e-10,
           'mass':abs(r['massDrift'])<1e-9,'elements':max(abs(v) for v in r['elementDrift'].values())<1e-6,
           'species':r['sumYError']<1e-12 and r['minY']>=-1e-14,'positivity':r['minT']>0 and r['minP']>0,'EOS':r['maxEOSRelative']<1e-10}
        if r['kind']=='F' and r['mode']=='none' and r['steps']==120 and r['dt']==2e-6:
            r['againstAcceptedBaseline']=compare(ROOT/'data/raw/F_dt2e-06_p1',case)
        results.append(r)
        print(r['name'],'energy',f"{r['signedEnergyDrift']:+.8e}",'local closure',f"{r['maxCellClosure']:.3e}",'rhoh+c',f"{r['cellCumulativeTerms']['DrhoH']+r['cellCumulativeTerms']['DrhoC']:+.5e}",flush=True)
    processed=STUDY/'data/processed';processed.mkdir(exist_ok=True)
    (processed/'screen_summary.json').write_text(json.dumps(results,indent=2)+'\n')
    (processed/'cell_totals.json').write_text(json.dumps(alltotals,indent=2)+'\n')
    failures=[json.loads(p.read_text()) for p in (STUDY/'data/raw').glob('*/failure.json')]
    (processed/'failures.json').write_text(json.dumps(failures,indent=2)+'\n')
if __name__=='__main__':main()
