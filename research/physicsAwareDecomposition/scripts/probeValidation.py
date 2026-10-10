#!/usr/bin/env python3
"""Native stock/instrumented probe-history regression."""
import json,re
from study import ROOT,newcase,config,decomp,solver,record
results={}
function = 'functions { validationProbes { type probes; libs ("libsampling.so"); writeControl timeStep; writeInterval 1; fields (T p U CH4 O2 CO2 H2O N2); probeLocations ((0.005 0 0) (0.014 0 0) (0.018 0 0)); } }'
for ranks,cost in [(1,False),(2,False),(1,True),(2,True)]:
    cases=[]
    for exe in ['reactingFoam','reactingFoamPAD']:
        c=newcase(f'probeValidation/p{ranks}_cost{int(cost)}/{exe}')
        config(c,end=10,cost=cost if exe.endswith('PAD') else False)
        with (c/'system/controlDict').open('a') as f:f.write('\n'+function+'\n')
        dt,parts=decomp(c,ranks);elapsed=solver(c,ranks,exe)
        record(c,'probeValidation',{'ranks':ranks,'cost':cost and exe.endswith('PAD')},elapsed,dt,parts)
        cases.append(c)
    norms={}
    for field in ['T','p','U','CH4','O2','CO2','H2O','N2']:
        data=[]
        for c in cases:
            paths=list((c/'postProcessing/validationProbes').glob('*/'+field))
            if len(paths)!=1:raise RuntimeError('Missing probe output '+str(c))
            nums=[]
            for line in paths[0].read_text().splitlines():
                if line.strip() and not line.startswith('#'):
                    nums.append([float(x) for x in re.findall(r'[-+]?(?:\d+\.?\d*|\.\d+)(?:[eE][-+]?\d+)?',line)])
            data.append(nums)
        if len(data[0])<10 or len(data[0])!=len(data[1]):raise RuntimeError('incomplete history')
        norms[field]={'samples':len(data[0]),'identical':data[0]==data[1],'Linf':max(abs(a-b) for ra,rb in zip(*data) for a,b in zip(ra,rb))}
        if not norms[field]['identical']:raise RuntimeError('Probe histories differ')
    results[f'p{ranks}_cost{int(cost)}']={'status':'VERIFIED','fields':norms}
out=ROOT/'data/processed/probe_validation.json';out.write_text(json.dumps(results,indent=2)+'\n')
print('VERIFIED identical native probe histories',out)
