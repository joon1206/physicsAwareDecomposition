#!/usr/bin/env python3
"""Fixed global-dt time-accurate sensitivity; warm flame initial state."""
import csv,json,random,re,shutil,statistics
from study import ROOT,newcase,config,decomp,solver,record,setentry,run
from foamio import write_scalar,patches
from models import composite
from compareFields import compare,FIELDS
trace={}
with (ROOT/'data/raw/training/postProcessing/performance/cellCost.csv').open() as f:
    for row in csv.DictReader(f):
        if int(row['timeIndex'])>60:trace.setdefault(int(row['cell']),[]).append(float(row['wall']))
costs=[statistics.median(trace[i]) for i in range(4000)]
jobs=[(rep,g) for rep in range(5) for g in [None,1]];random.Random(375).shuffle(jobs)
for rep,g in jobs:
    c=newcase(f'transient/p4_scotch_g{g}_r{rep}')
    # Replace ONLY new case initialization with public tutorial's trained state.
    for f in (ROOT/'data/raw/training/80').iterdir():
        if f.is_file() and f.name not in ['rDeltaT','chemCost','chemSubsteps','phi']:shutil.copy2(f,c/'0'/f.name)
    s=c/'system/fvSchemes';s.write_text(s.read_text().replace('localEuler','Euler'))
    config(c,end=.00008);setentry(c/'system/controlDict','writeControl','timeStep');setentry(c/'system/controlDict','deltaT',.000001);setentry(c/'system/controlDict','writeInterval',80)
    f=c/'system/fvSolution';s=f.read_text();s=re.sub(r'(tolerance\s+)[^;]+;',r'\g<1>1e-12;',s);s=re.sub(r'(relTol\s+)[^;]+;',r'\g<1>0;',s);f.write_text(s)
    if g is not None:write_scalar(c/'0/cellWeight',composite(costs,g),patches(c/'constant/polyMesh/boundary'))
    dt,parts=decomp(c,4,'scotch',g is not None,0)
    for part in parts:part['predictedCost']=sum(costs[i] for i in part.pop('ids',[]))
    elapsed=solver(c,4)
    if rep==0:run(['reconstructPar','-latestTime'],c,c/'reconstruct.log')
    record(c,'transient',{'ranks':4,'method':'scotch','gamma':g,'repeat':rep,'start':0,'steps':80,'warmupSteps':10,'deltaT':1e-6,'end':8e-5,'linearTolerance':1e-12},elapsed,dt,parts)
    print('MEASURED fixed global dt',rep,g,elapsed,flush=True)
a=ROOT/'data/raw/transient/p4_scotch_gNone_r0/8e-05';b=ROOT/'data/raw/transient/p4_scotch_g1_r0/8e-05'
r=compare(a,b,4000,1e-5,1e-4,fields=[f for f in FIELDS if f!='rDeltaT'])
(ROOT/'data/processed/transient_validation.json').write_text(json.dumps(r,indent=2))
if not r['pass']:raise RuntimeError('transient partition gate failed')
