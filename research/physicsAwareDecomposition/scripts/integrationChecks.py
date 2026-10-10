#!/usr/bin/env python3
"""Native thermo equivalence, invalid controls and persistent EMA restarts."""
import json,math,shutil
from study import ROOT,config,decomp,newcase,solver,setentry
from compareFields import compare
from foamio import read_field
results={}
for label in ['serial','parallel','cost_serial','cost_parallel']:
    p=ROOT/'data/raw/validation'/label
    r=compare(p/'reactingFoam/20',p/'reactingFoamPAD/20',4000)
    results[label]=r
    if not r['pass']:raise RuntimeError('native thermo equivalence failed '+label)
for ranks in [1,2]:
    c=newcase(f'robustness/emaRestart_p{ranks}')
    config(c,end=5,cost=True,alpha=0)
    decomp(c,ranks)
    solver(c,ranks)
    from study import run
    if ranks>1:run(['reconstructPar','-latestTime'],c,c/'reconstruct_first.log')
    before=read_field(c/'5/chemCost',4000)
    shutil.copyfile(c/'solver.log',c/'solver_first.log')
    config(c,end=6,start=5,cost=True,alpha=0)
    solver(c,ranks)
    if ranks>1:run(['reconstructPar','-latestTime'],c,c/'reconstruct_restart.log')
    after=read_field(c/'6/chemCost',4000)
    results[f'emaRestart_p{ranks}']={'status':'TESTED','alpha':0,'Linf':max(abs(a-b) for a,b in zip(before,after))}
    if before!=after:raise RuntimeError('EMA history not preserved')
for key,value in [('costAlpha','-0.1'),('costAlpha','1.1'),('costTraceInterval','-1')]:
    c=newcase('robustness/invalid_'+key+'_'+value.replace('-','minus'))
    config(c,end=1,cost=True)
    setentry(c/'constant/chemistryProperties',key,value)
    try:solver(c)
    except RuntimeError:
        log=(c/'solver.log').read_text()
        if 'costAlpha must be in [0,1]' not in log:raise
        results[c.name]={'status':'TESTED','rejected':True,'diagnostic':'costAlpha must be in [0,1]; costTraceInterval >= 0'}
    else:raise RuntimeError('invalid configuration accepted')
out=ROOT/'data/processed/final_smoke.json'
out.write_text(json.dumps(results,indent=2)+'\n')
print('TESTED native thermo, serial/decomposed EMA restart and invalid controls',out)
