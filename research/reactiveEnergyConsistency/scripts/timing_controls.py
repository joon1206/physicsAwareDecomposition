"""Randomized, repeated timing of the audit overhead, no method speed claim."""
from pathlib import Path
import random,json,statistics
from campaign import run,ROOT
def main():
    for enabled in [False,True]:run('timing_warmup_'+str(enabled),enabled=enabled)
    order=[(enabled,i) for enabled in [False,True] for i in range(3)]
    random.Random(20261006).shuffle(order);records=[]
    for enabled,i in order:
        case=run(f'timing_ledger{int(enabled)}_trial{i}',enabled=enabled)
        records.append(json.loads((case/'result.json').read_text()))
    statistics_out={}
    for enabled in [False,True]:
        wall=[r['solverWall'] for r in records if r['enabled']==enabled]
        statistics_out[str(enabled)]=dict(n=len(wall),median=statistics.median(wall),mean=statistics.mean(wall),std=statistics.stdev(wall),samples=wall)
    overhead=statistics_out['True']['median']/statistics_out['False']['median']-1
    (ROOT/'data/processed/timing_controls.json').write_text(json.dumps(dict(seed=20261006,order=order,records=records,statistics=statistics_out,medianAuditOverhead=overhead,
        scope='Three local bound-MPI process-wall trials per audit setting after warmup; includes startup and endpoint I/O; no corrected method or large-scale inference; no bootstrap interval with n=3.'),indent=2)+'\n')
    print('TIMING measured audit overhead',overhead,flush=True)
if __name__=='__main__':main()
