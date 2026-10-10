#!/usr/bin/env python3
"""Bounded sequential OpenFOAM experiment driver. All runs retained."""
import argparse,csv,datetime,hashlib,json,math,os,random,re,shutil,statistics,subprocess,time,threading
from pathlib import Path
from foamio import read_field,write_scalar,patches,proc_metrics
from models import weights,composite,metrics,lpt
ROOT=Path(os.environ.get('PAD_OUTPUT_ROOT',Path(__file__).resolve().parents[1]))
TUTORIAL=Path(os.environ['FOAM_TUTORIALS'])/'combustion/reactingFoam/laminar/counterFlowFlame2DLTS'
def run(args,case,log,timeout=180):
    start=time.perf_counter()
    with Path(log).open('w') as f:
        p=subprocess.Popen(args,cwd=case,stdout=f,stderr=subprocess.STDOUT)
        expired=[]
        def stop():
            expired.append(True);p.kill()
        watchdog=threading.Timer(timeout,stop);watchdog.start()
        try:p.wait()
        finally:watchdog.cancel()
        if expired:raise RuntimeError('timeout: '+str(log))
    elapsed=time.perf_counter()-start
    if p.returncode:raise RuntimeError(str(args)+' failed: '+str(log))
    return elapsed
def setentry(path,name,value):
    s=path.read_text();pattern=r'(?m)^(\s*)'+re.escape(name)+r'\s+[^;\n]+;'
    if re.search(pattern,s):s=re.sub(pattern,lambda m:m[1]+name+' '+str(value)+';',s)
    else:s+='\n'+name+' '+str(value)+';\n'
    path.write_text(s)
def newcase(name):
    p=ROOT/'data/raw'/name
    if p.exists():raise RuntimeError('Refusing to overwrite existing run '+str(p))
    p.mkdir(parents=True)
    for sub in ['0','constant','system']:shutil.copytree(TUTORIAL/sub,p/sub)
    setentry(p/'system/controlDict','writePrecision',14)
    setentry(p/'system/controlDict','runTimeModifiable','false')
    run(['blockMesh'],p,p/'blockMesh.log')
    return p
def decomp(case,p,method='scotch',weighted=False,start=0):
    if p==1:return 0.,[{'rank':0,'nCells':4000,'processorFaces':0,'nNeighbours':0,'ids':list(range(4000))}]
    s='FoamFile {version 2.0; format ascii; class dictionary; object decomposeParDict;}\n'
    s+=f'numberOfSubdomains {p};\nmethod {method};\n'
    if weighted:s+='weightField cellWeight;\n'
    s+=f'simpleCoeffs {{ n ({p} 1 1); delta 0.001; }}\nhierarchicalCoeffs {{ n ({p} 1 1); order xyz; delta 0.001; }}\n'
    (case/'system/decomposeParDict').write_text(s)
    elapsed=run(['decomposePar','-time',str(start)],case,case/'decompose.log')
    return elapsed,proc_metrics(case)
def solver(case,p=1,exe='reactingFoamPAD'):
    args=[exe]
    if p>=1:args=['mpirun','--bind-to','core','--map-by','core','--nooversubscribe','--report-bindings','-np',str(p),exe]+(['-parallel'] if p>1 else [])
    return run(args,case,case/'solver.log',timeout=240)
def config(case,end=40,start=0,timing=True,cost=False,trace=0,alpha=1,cell_timing=True):
    for k,v in {'startTime':start,'endTime':end,'writeInterval':end-start,'padTiming':str(timing).lower(),'writePrecision':14}.items():
        setentry(case/'system/controlDict',k,v)
    if cost:
        setentry(case/'system/controlDict','libs','("libcostChemistry.so")')
        setentry(case/'constant/chemistryProperties','solver','costEulerImplicit')
        for k,v in {'costAlpha':alpha,'costTraceInterval':trace,'cellTiming':str(cell_timing).lower()}.items():
            setentry(case/'constant/chemistryProperties',k,v)
def record(case,kind,meta,elapsed,dt,parts):
    m={'status':'MEASURED','timestamp':datetime.datetime.now(datetime.timezone.utc).isoformat(),
       'gitRevision':subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),
       'gitStatus':subprocess.check_output(['git','status','--short'],text=True),
       'machineManifest':'data/machine.json','case':str(case.relative_to(ROOT)),
       'caseSource':str(TUTORIAL),'kind':kind,'solverWall':elapsed,'decompositionWall':dt,
       'rankMapping':('--bind-to core --map-by core --nooversubscribe' if 'MCW rank' in (case/'solver.log').read_text() else 'unbound serial in early validation/pilot'),'OMP_NUM_THREADS':os.getenv('OMP_NUM_THREADS'),
       **meta,'parts':parts}
    m['inputHashes']={str(p.relative_to(case)):hashlib.sha256(p.read_bytes()).hexdigest() for d in ['system','constant','0'] for p in (case/d).rglob('*') if p.is_file() and 'polyMesh' not in p.parts}
    (case/'manifest.json').write_text(json.dumps(m,indent=2)+'\n');return m
def validate(label,p,cost=False):
    from compareFields import compare
    cases=[]
    for exe,timing in [('reactingFoam',False),('reactingFoamPAD',True)]:
        c=newcase('validation/'+label+'/'+exe);config(c,end=20,cost=cost if timing else False)
        dt,parts=decomp(c,p);elapsed=solver(c,p,exe)
        if p>1:run(['reconstructPar','-latestTime'],c,c/'reconstruct.log')
        record(c,'validation',{'ranks':p,'cost':cost if timing else False},elapsed,dt,parts);cases.append(c)
    r=compare(cases[0]/'20',cases[1]/'20',4000)
    residual=lambda c: [line for line in (c/'solver.log').read_text().splitlines() if 'Solving for' in line]
    r['identicalResiduals']=residual(cases[0])==residual(cases[1])
    r['pass'] &= r['identicalResiduals']
    out=ROOT/'data/processed';out.mkdir(parents=True,exist_ok=True)
    (out/('validation_'+label+'.json')).write_text(json.dumps(r,indent=2)+'\n')
    if not r['pass']:raise RuntimeError('Numerical validation failed '+label)
    print('TESTED numerical equivalence',label,flush=True)
def train(name='training',end=80):
    c=newcase(name);config(c,end=end,cost=True,trace=1);elapsed=solver(c)
    record(c,'training',{'ranks':1,'end':end,'costTrace':1},elapsed,0,[{'rank':0,'nCells':4000,'processorFaces':0,'nNeighbours':0}])
    print('MEASURED training',elapsed,flush=True);return c
def reactive(campaign='reactive',repeats=5,steps=80):
    training=ROOT/'data/raw/training'
    last=80
    trace={}
    with (training/'postProcessing/performance/cellCost.csv').open() as f:
        for r in csv.DictReader(f):
            t=int(r['timeIndex'])
            if t>60:trace.setdefault(int(r['cell']),[]).append(float(r['wall']))
    costs=[statistics.median(trace[i]) for i in range(4000)]
    specs=[(p,m,g) for p in [1,2,4] for m,g in [('scotch',None),('scotch',0),('scotch',.25),('scotch',1),('scotch',4),('scotch',16),('simple',None)] if p>1 or (m=='scotch' and g is None)]
    jobs=[(rep,*spec) for rep in range(repeats) for spec in specs];random.Random(20261004).shuffle(jobs)
    for rep,p,m,g in jobs:
        name=f'{campaign}/p{p}_{m}_g{g}_r{rep}'
        c=newcase(name);config(c,end=last+steps,start=last)
        shutil.copytree(training/str(last),c/str(last))
        # Predictor fields are passive; exclude cost trace and diagnostic fields from timed solver.
        for f in ['chemCost','chemSubsteps']:
            q=c/str(last)/f
            if q.exists():q.unlink()
        if g is not None:write_scalar(c/str(last)/'cellWeight',composite(costs,g),patches(c/'constant/polyMesh/boundary') if (c/'constant/polyMesh/boundary').exists() else [('inlet', 'patch')])
        if not (c/'constant/polyMesh').exists():run(['blockMesh'],c,c/'blockMesh.log')
        if g is not None:write_scalar(c/str(last)/'cellWeight',composite(costs,g),patches(c/'constant/polyMesh/boundary'))
        dt,parts=decomp(c,p,m,g is not None,last)
        for part in parts:part['predictedCost']=sum(costs[i] for i in part.pop('ids',[]))
        elapsed=solver(c,p)
        if rep==0 and p>1:run(['reconstructPar','-latestTime'],c,c/'reconstruct.log')
        record(c,'reactive',{'ranks':p,'method':m,'gamma':g,'repeat':rep,'start':last,'steps':steps,'warmupSteps':10,'predictor':'median cell clocks from training iterations 61-80'},elapsed,dt,parts)
        print('MEASURED',name,round(elapsed,4),flush=True)
def smoke():
    for label,p,cost in [('serial',1,False),('parallel',2,False),('cost_serial',1,True),('cost_parallel',2,True)]:
        # Build each mesh before decomposition/solve.
        validate(label,p,cost)
if __name__=='__main__':
    a=argparse.ArgumentParser();a.add_argument('mode',choices=['smoke','train','reactive']);a.add_argument('--campaign',default='reactive');a.add_argument('--repeats',type=int,default=5);a.add_argument('--steps',type=int,default=80);o=a.parse_args()
    if o.mode=='smoke':smoke()
    elif o.mode=='train':train()
    else:reactive(o.campaign,o.repeats,o.steps)
