#!/usr/bin/env python3
"""Synthetic runtime, physical-time sensitivity, motion and validation tables."""
import csv,json,statistics
from collections import defaultdict
from pathlib import Path
from study import ROOT
from analyzeTiming import csvout,bootstrap,stats,timing
from compareFields import compare,FIELDS
from models import metrics,weights,correlation
from foamio import read_field,proc_metrics
OUT=ROOT/'data/processed';OUT.mkdir(parents=True,exist_ok=True)
groups=defaultdict(list);runs=[]
for p in sorted(list((ROOT/'data/raw/syntheticRuntime').glob('*/manifest.json'))+list((ROOT/'data/raw/communicationDominated').glob('*/manifest.json'))):
    m=json.loads(p.read_text());rankdata=[]
    for rank in range(m['ranks']):
        q=list(csv.DictReader((p.parent/f'processor{rank}/postProcessing/performance/rank{rank:04d}.csv').open()))[5:]
        if len(q)!=25:raise ValueError('unexpected synthetic step count')
        rankdata.append(q)
    phases=['stepWall','transportWall','chemistryWall','communicationWall','synchronizationWall']
    med={phase:statistics.median(max(float(q[t][phase]) for q in rankdata) for t in range(25)) for phase in phases}
    costs=[sum(float(q['transportWall'])+float(q['chemistryWall']) for q in rows) for rows in rankdata]
    r={'case':m['case'],'nx':m['nx'],'ny':m['ny'],'ranks':m['ranks'],'kind':m['kind'],'haloPasses':m['haloPasses'],'weighted':int(m['weighted']),'repeat':m['repeat'],'solverWall':m['solverWall'],**med,'computeImbalance':metrics(costs)['imbalance'],
        'processorFaces':sum(x['processorFaces'] for x in m['parts'])//2}
    runs.append(r);groups[(m['nx'],m['ranks'],m['kind'],m['haloPasses'],int(m['weighted']))].append(r)
csvout(OUT/'synthetic_runtime_runs.csv',runs);summary=[]
for key,v in sorted(groups.items()):
    nx,p,k,h,w=key;base=groups[(nx,p,k,h,0)];a=[r['stepWall'] for r in base];b=[r['stepWall'] for r in v];ci=bootstrap(a,b)
    summary.append({'nx':nx,'ranks':p,'kind':k,'haloPasses':h,'weighted':w,'trials':len(v),'stepMedian':statistics.median(b),'stepSpeedup':statistics.median(a)/statistics.median(b),'stepCI_low':ci[0],'stepCI_high':ci[1],
        'communicationMedian':statistics.median(r['communicationWall'] for r in v),'synchronizationMedian':statistics.median(r['synchronizationWall'] for r in v),
        'computeImbalance':statistics.median(r['computeImbalance'] for r in v),'processorFaces':v[0]['processorFaces']})
csvout(OUT/'synthetic_runtime_summary.csv',summary)
trans=defaultdict(list)
for p in (ROOT/'data/raw/transient').glob('*/manifest.json'):
    m=json.loads(p.read_text());trans[m['gamma']].append(m['solverWall'])
if trans:
    rows=[]
    for g,v in trans.items():
        ci=bootstrap(trans[None],v)
        rows.append({'gamma':g,'trials':len(v),**stats(v),'speedup':statistics.median(trans[None])/statistics.median(v),'CI_low':ci[0],'CI_high':ci[1]})
    csvout(OUT/'transient_summary.csv',rows)
    a=ROOT/'data/raw/transient/p4_scotch_gNone_r0/8e-05';b=ROOT/'data/raw/transient/p4_scotch_g1_r0/8e-05'
    transientResult=compare(a,b,4000,1e-5,1e-4,fields=[f for f in FIELDS if f!='rDeltaT'])
    (OUT/'transient_validation.json').write_text(json.dumps(transientResult,indent=2)+'\n')
# Analytic moving hotspot evaluated on measured native partitions.
source=list(csv.DictReader((OUT/'synthetic.csv').open()))
select=[r for r in source if r['mesh']=='64x32' and r['ranks']=='4' and r['method']=='scotch' and r['kind']=='gaussian' and r['amplitude']=='20' and r['width']=='0.15' and r['centreX']=='0.25']
if select:
    pts=read_field(ROOT/'data/raw/synthetic/mesh_64x32/0/C',2048);initial=weights(pts,'gaussian',20,.15,(.25,.5,.005))
    rows=[]
    for r in select:
        parts=proc_metrics(ROOT/r['case'])
        for speed in [0,.002,.02]:
            for step in range(26):
                x=min(.75,.25+speed*step);w=weights(pts,'gaussian',20,.15,(x,.5,.005))
                rows.append({'weighted':int(r['weighted']),'speedLPerIteration':speed,'iteration':step,'centreX':x,
                    'initialCorrelation':correlation(initial,w),'imbalance':metrics([sum(w[i] for i in q['ids']) for q in parts])['imbalance']})
    csvout(OUT/'moving_hotspot.csv',rows)
# Flat validation tables with physical units retained in field file headers.
rows=[]
for folder in ['tight','noChem']:
    for p in (OUT/folder).glob('partition_validation*.json'):
        d=json.loads(p.read_text())
        for field,v in d['fields'].items():
            rows.append({'comparison':p.stem,'campaign':folder,'field':field,'L1':v.get('L1'),'L2':v.get('L2'),'Linf':v.get('Linf'),'relativeL2':v.get('relativeL2'),'relativeLinf':v.get('relativeLinf'),'pass':v['pass'],'pointwisePass':v.get('pointwisePass')})
csvout(OUT/'numerical_norms.csv',rows)
if summary:print('Synthetic runtime records',len(runs),'configurations',len(summary))
if trans:print('Transient',rows if False else list(trans.keys()),'gate',transientResult.get('pass'))
