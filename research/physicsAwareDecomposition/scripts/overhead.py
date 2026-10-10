#!/usr/bin/env python3
"""Randomized repeated whole-run instrumentation cost measurements."""
import random
from study import ROOT,newcase,config,decomp,solver,record
jobs=[(rep,name) for rep in range(7) for name in ['stock','disabled','timed','counters','cellclock','trace']]
random.Random(4096).shuffle(jobs)
for rep,name in jobs:
    c=newcase(f'overhead/{name}_{rep}')
    config(c,end=80,timing=name not in ['stock','disabled'],cost=name in ['counters','cellclock','trace'],trace=1 if name=='trace' else 0,cell_timing=name!='counters')
    elapsed=solver(c,1,'reactingFoam' if name=='stock' else 'reactingFoamPAD')
    record(c,'overhead',{'ranks':1,'variant':name,'repeat':rep,'steps':80},elapsed,0,[{'rank':0,'nCells':4000,'processorFaces':0,'nNeighbours':0}])
    print('MEASURED overhead',name,rep,round(elapsed,5),flush=True)
