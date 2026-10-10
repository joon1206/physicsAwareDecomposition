"""Retain machine-readable linear iteration and existing per-phase timing data."""
from pathlib import Path
import json,re,csv,gzip
ROOT=Path(__file__).resolve().parents[1]
def main():
    result={}
    regex=re.compile(r'(\w+):\s+Solving for ([\w.]+), Initial residual = ([\deE.+-]+), Final residual = ([\deE.+-]+), No Iterations (\d+)')
    for meta in (ROOT/'data/raw').glob('*/result.json'):
        if meta.parent.name.startswith('timing_'):continue
        case=meta.parent;records=[]
        for log in sorted(case.glob('solver*.log')):
            t=0
            for line in log.read_text().splitlines():
                m=re.match(r'Time = ([\deE.+-]+)',line)
                if m:t=float(m[1])
                m=regex.search(line)
                if m:records.append(dict(time=t,solver=m[1],field=m[2],initialResidual=float(m[3]),finalResidual=float(m[4]),iterations=int(m[5]),log=log.name))
        phase=[]
        for fp in case.glob('**/performance/rank*.csv'):
            with fp.open() as f:phase.extend({k:float(v) for k,v in r.items()} for r in csv.DictReader(f))
        sums={}
        for r in phase:
            rank=int(r['rank']);sums.setdefault(rank,{k:0 for k in r if k.endswith('Wall')})
            for k in sums[rank]:sums[rank][k]+=r[k]
        result[case.name]=dict(linearSolves=records,phaseRankSums=sums,
            interpretation='phase timing includes full phase, not isolated matrix solve; instrumented wall times are diagnostic, single trials, not method performance claims')
    with gzip.open(ROOT/'data/processed/solver_metrics.json.gz','wt',compresslevel=6) as f:json.dump(result,f,separators=(',',':'))
    previous=ROOT/'data/processed/solver_metrics.json'
    if previous.exists():previous.unlink()
if __name__=='__main__':main()
