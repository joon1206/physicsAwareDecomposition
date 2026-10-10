"""MPI operation counts; concurrent first screens are excluded from timing claims."""
from pathlib import Path
import csv,json,math
ROOT=Path(__file__).resolve().parents[1];STUDY=ROOT/'candidateStudy';records=[]
for meta in (STUDY/'data/raw').glob('*_mpi/result.json'):
    case=meta.parent;config=json.loads(meta.read_text())
    config['timingContext']=('Sequential loose-block instrumentation after the logical campaigns; operation counts only, timing excluded from the paired three-trial comparison.'
        if case.name.endswith('_tol0.0001_mpi') else config.get('timingContext','Concurrent 0D tolerance campaign: operation counts retained; timing excluded from uncontended performance comparisons.'))
    rows=[]
    for p in case.glob('mpiProfile/mpi_rank*.csv'):
        with p.open() as f:rows.append({k:float(v) for k,v in next(csv.DictReader(f)).items()})
    if len(rows)!=config['ranks']:raise RuntimeError('Missing rank counter '+case.name)
    totals={k:math.fsum(r[k] for r in rows) for k in rows[0] if k!='rank'}
    records.append(dict(name=case.name,rankCounters=rows,sumRankCounters=totals,timingContext=config['timingContext']))
    print(case.name,'collectives',totals['collectives'],'sends',totals['sends'],'payload',totals['sendPayloadBytes'])
(STUDY/'data/processed/mpi_counts.json').write_text(json.dumps(records,indent=2)+'\n')
