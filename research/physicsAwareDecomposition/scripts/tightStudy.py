#!/usr/bin/env python3
"""Repeat partition experiments with stricter linear convergence."""
import argparse,random,shutil,statistics,csv
from study import ROOT,newcase,config,decomp,solver,record
from foamio import write_scalar,patches
from models import composite
from compareFields import compare
import json,re
def main(pilot=False,no_chemistry=False):
    trace={}
    with (ROOT/'data/raw/training/postProcessing/performance/cellCost.csv').open() as f:
        for row in csv.DictReader(f):
            if int(row['timeIndex'])>60:trace.setdefault(int(row['cell']),[]).append(float(row['wall']))
    costs=[statistics.median(trace[i]) for i in range(4000)]
    specs=[(4,'scotch',None),(4,'scotch',1)] if pilot else [(p,m,g) for p in [1,2,4] for m,g in [('scotch',None),('scotch',0),('scotch',.25),('scotch',1),('scotch',4),('scotch',16),('simple',None)] if p>1 or (m=='scotch' and g is None)]
    if no_chemistry:specs=[(4,'scotch',g) for g in [None,1,16]]
    jobs=[(rep,*spec) for rep in range(1 if pilot else 5) for spec in specs]
    random.Random(29785).shuffle(jobs)
    campaign='reactiveNoChem' if no_chemistry else ('tightPilot' if pilot else 'reactiveTight')
    for rep,p,m,g in jobs:
        name=f'{campaign}/p{p}_{m}_g{g}_r{rep}';c=newcase(name);config(c,start=80,end=160)
        if no_chemistry:
            from study import setentry
            setentry(c/'constant/chemistryProperties','chemistry','off')
        shutil.copytree(ROOT/'data/raw/training/80',c/'80')
        for field in ['chemCost','chemSubsteps']:(c/'80'/field).unlink()
        f=c/'system/fvSolution';s=f.read_text()
        s=re.sub(r'(tolerance\s+)[^;]+;',r'\g<1>1e-12;',s);s=re.sub(r'(relTol\s+)[^;]+;',r'\g<1>0;',s);f.write_text(s)
        if g is not None:write_scalar(c/'80/cellWeight',composite(costs,g),patches(c/'constant/polyMesh/boundary'))
        dt,parts=decomp(c,p,m,g is not None,80)
        for part in parts:part['predictedCost']=sum(costs[i] for i in part.pop('ids',[]))
        elapsed=solver(c,p)
        if rep==0 and p>1:run_reconstruct(c)
        record(c,'reactive',{'ranks':p,'method':m,'gamma':g,'repeat':rep,'start':80,'steps':80,'warmupSteps':10,'predictor':'median cell clocks training iterations 61-80','linearTolerance':1e-12,'relTol':0,'chemistryEnabled':not no_chemistry},elapsed,dt,parts)
        print('MEASURED',name,elapsed,flush=True)
    if pilot:
        r=compare(ROOT/'data/raw/tightPilot/p4_scotch_gNone_r0/160',ROOT/'data/raw/tightPilot/p4_scotch_g1_r0/160',4000,1e-5,1e-4)
        (ROOT/'data/processed/tight_pilot_validation.json').write_text(json.dumps(r,indent=2))
        print('TIGHT NUMERICAL GATE',r['pass'],{k:v.get('Linf') for k,v in r['fields'].items()},flush=True)
def run_reconstruct(c):
    from study import run
    run(['reconstructPar','-latestTime'],c,c/'reconstruct.log')
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--pilot',action='store_true');p.add_argument('--no-chemistry',action='store_true');a=p.parse_args();main(a.pilot,a.no_chemistry)
