#!/usr/bin/env python3
"""Bounded clipping sensitivity and Python cost-construction overhead."""
import csv,json,statistics,time
from study import ROOT,newcase,decomp
from foamio import write_scalar,patches
from models import composite,metrics
trace={}
with (ROOT/'data/raw/training/postProcessing/performance/cellCost.csv').open() as f:
    for r in csv.DictReader(f):
        if int(r['timeIndex'])>60:trace.setdefault(int(r['cell']),[]).append(float(r['wall']))
costs=[statistics.median(trace[i]) for i in range(4000)]
rows=[]
for low,high in [(.05,100),(.5,2),(.1,1.5),(1,1)]:
    c=newcase(f'clipping/lo{low}_hi{high}')
    timings=[]
    for _ in range(100):
        t=time.perf_counter();w=composite(costs,1,lo=low,hi=high);timings.append(time.perf_counter()-t)
    write_scalar(c/'0/cellWeight',w,patches(c/'constant/polyMesh/boundary'))
    dt,parts=decomp(c,4,weighted=True)
    rows.append({'status':'MEASURED assignment; DERIVED workload','gamma':1,'low':low,'high':high,'weightMin':min(w),'weightMax':max(w),'meanWeight':statistics.mean(w),
        'constructionMedian':statistics.median(timings),'constructionTrials':100,'decompositionWall':dt,
        'predictedChemistryImbalance':metrics([sum(costs[i] for i in p['ids']) for p in parts])['imbalance'],
        'cellImbalance':metrics([p['nCells'] for p in parts])['imbalance'],'processorFaces':sum(p['processorFaces'] for p in parts)//2,
        'case':str(c.relative_to(ROOT))})
out=ROOT/'data/processed/clipping_sensitivity.csv'
with out.open('w',newline='') as f:
    wr=csv.DictWriter(f,fieldnames=list(rows[0]));wr.writeheader();wr.writerows(rows)
print('TESTED clipping native partitions',rows)
