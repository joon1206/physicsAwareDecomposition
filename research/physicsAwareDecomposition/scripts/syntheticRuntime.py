#!/usr/bin/env python3
"""Measured synthetic workloads, separate from any chemistry/CFD claim."""
import argparse,csv,json,os,random,shutil,statistics
from study import ROOT,run,solver,record
from foamio import read_field,write_scalar,proc_metrics
from models import weights,metrics
def main(pilot=False,communication=False):
    campaign=('communicationPilot' if pilot else 'communicationDominated') if communication else ('syntheticRuntimePilot' if pilot else 'syntheticRuntime')
    specs=[(32,16,2,'gaussian',20,1,w) for w in [False,True]] if pilot else [(nx,ny,p,k,a,h,w) for nx,ny in [(32,16),(64,32)] for p in [2,4] for k,a in [('uniform',0),('gaussian',20),('half',20),('extreme',50)] for h in [1,32] for w in [False,True]]
    if communication:specs=[(64,32,4,k,a,2048,w) for k,a in [('gaussian',20),('uniform',0)] for w in [False,True]]
    jobs=[(rep,*s) for rep in range(1 if pilot else 5) for s in specs];random.Random(576).shuffle(jobs)
    for rep,nx,ny,p,k,a,h,w in jobs:
        base=ROOT/f'data/raw/synthetic/mesh_{nx}x{ny}';pts=read_field(base/'0/C',nx*ny)
        c=ROOT/f'data/raw/{campaign}/m{nx}_p{p}_{k}_h{h}_w{int(w)}_r{rep}'
        c.mkdir(parents=True);shutil.copytree(base/'constant',c/'constant',copy_function=os.link);shutil.copytree(base/'system',c/'system');(c/'0').mkdir()
        ws=weights(pts,k,a,.15,(.25,.5,.005));write_scalar(c/'0/cellWeight',ws,[('walls','wall'),('frontAndBack','empty')])
        (c/'system/decomposeParDict').write_text('FoamFile {version 2.0; format ascii; class dictionary; object decomposeParDict;}\n'+f'numberOfSubdomains {p}; method scotch;\n'+('weightField cellWeight;\n' if w else ''))
        (c/'constant/workloadProperties').write_text('FoamFile {version 2.0; format ascii; class dictionary; object workloadProperties;}\n'+f'baseIterations 100; chemistryIterations 100; haloPasses {h}; steps 30;')
        dt=run(['decomposePar','-time','0'],c,c/'decompose.log');parts=proc_metrics(c)
        for part in parts:
            ids=part.pop('ids');part['predictedCost']=sum(ws[i] for i in ids)
            local=read_field(c/f"processor{part['rank']}/0/cellWeight",len(ids))
            if max(abs(ws[i]-v) for i,v in zip(ids,local))>1e-5:raise RuntimeError('weights corrupted in decomposition')
        elapsed=solver(c,p,'padWorkloadFoam')
        record(c,'syntheticRuntime',{'ranks':p,'nx':nx,'ny':ny,'kind':k,'amplitude':a,'haloPasses':h,'weighted':w,'repeat':rep,'steps':30,'warmupSteps':5,'baseIterations':100,'chemistryIterations':100,'meaning':'synthetic trigonometric CPU work; halo exchange, not reactive chemistry'},elapsed,dt,parts)
        print('MEASURED synthetic runtime',c.name,round(elapsed,5),flush=True)
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--pilot',action='store_true');p.add_argument('--communication',action='store_true');a=p.parse_args();main(a.pilot,a.communication)
