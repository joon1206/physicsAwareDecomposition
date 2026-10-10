"""Bounded supplemental experiments. Run only after the oracle, sequentially."""
import argparse,csv,json,random,shutil,time
from pathlib import Path
from caseFactory import ROOT,PAD,make_case,decompose,solve,set_control,command,latest_time
from oracle import run_branch,copy_checkpoint,action_setup
from features import extract,rank_costs
from mapping import canonical_directory,assemble,metrics
from validation import numerical_gate

def horizons():
    jobs=[(regime,H,a,r) for regime in ['persistent','translating','transportDominated']
          for H in [20,320] for a in ['A0','AC','AM','AH'] for r in range(5)]
    random.Random(31731).shuffle(jobs)
    for regime,H,a,r in jobs:
        path=ROOT/'data/raw/oracle'/regime/f'cp4e-05_H{H}_{a}_r{r}'
        if (path/'manifest.json').exists():continue
        run_branch(ROOT/'data/raw/histories'/regime,'4e-05',a,H,r)
    from oracle import collect
    collect()

def profiles():
    rows=[]
    jobs=[(regime,a,profile,r) for regime in ['persistent','transportDominated']
          for a in ['A0','AC','AM','AH'] for profile in [False,True] for r in range(3)]
    random.Random(332).shuffle(jobs)
    for regime,a,profile,r in jobs:
        campaign='profilesOn' if profile else 'profilesOff'
        path=ROOT/'data/raw'/campaign/regime/f'cp4e-05_H80_{a}_r{r}'
        if not (path/'manifest.json').exists():run_branch(ROOT/'data/raw/histories'/regime,'4e-05',a,80,r,campaign,profile)
        row=json.loads((path/'manifest.json').read_text())
        parts=metrics(path);row['parts']=[{k:v for k,v in part.items() if k!='ids'} for part in parts]
        row['processorFaces']=sum(p['processorFaces'] for p in parts)/2
        if profile:
            row['MPI']=[next(csv.DictReader(f.open())) for f in (path/'mpiProfile').glob('mpi*.csv')]
            row['migrationMPI']=[next(csv.DictReader(f.open())) for f in (path/'migrationMPI').glob('mpi*.csv')]
            reference=ROOT/'data/raw/profilesOff'/regime/f'cp4e-05_H80_{a}_r{r}'
            if (reference/'manifest.json').exists():
                info=row['case'];fields=['T','p','U','Qdot']+info['species'];end=latest_time(path,True)
                row['gate']=numerical_gate(canonical_directory(reference,end,fields,info['nCells']),canonical_directory(path,end,fields,info['nCells']),info)
        rows.append(row)
    # Complete gates after both randomized arms have finished.
    for row in rows:
        if not row['profile']:continue
        regime=row['regime'];a=row['action'];r=row['repeat'];info=row['case']
        pair=[ROOT/'data/raw'/c/regime/f'cp4e-05_H80_{a}_r{r}' for c in ['profilesOff','profilesOn']]
        end=latest_time(pair[0],True);fields=['T','p','U','Qdot']+info['species']
        row['gate']=numerical_gate(*[canonical_directory(c,end,fields,info['nCells']) for c in pair],info)
    (ROOT/'data/processed/profiles.json').write_text(json.dumps(rows,indent=2))

def scaling():
    from analysis import choose
    from caseFactory import set_chemistry
    model_path=ROOT/'data/processed/model.json';model=json.loads(model_path.read_text())
    sources={}
    # Each rank count has a genuinely measured past prefix. The three policies
    # at that rank count start from identical fields and cost history.
    for p in [1,2,4,6]:
        source=ROOT/f'data/raw/scalingSources/p{p}'
        if not (source/'history.json').exists():
            if source.exists():raise RuntimeError('incomplete scaling source retained')
            make_case(f'scalingSources/p{p}','persistent',nx=32,ny=16,steps=20,trace=1)
            setup,_=decompose(source,p);elapsed=solve(source,p)
            (source/'history.json').write_text(json.dumps(dict(wall=elapsed,decompositionWall=setup)))
        sources[p]=source
    jobs=[(p,a,r) for p in [1,2,4,6] for a in ['A0','AC','controller'] for r in range(5)]
    random.Random(557).shuffle(jobs);rows=[]
    for p,a,r in jobs:
        source=sources[p];info=json.loads((source/'case.json').read_text());cp=latest_time(source,p>1)
        target=ROOT/f'data/raw/scaling/p{p}_{a}_r{r}'
        if not (target/'manifest.json').exists():
            if p>1:copy_checkpoint(source,target,cp)
            else:
                target.mkdir(parents=True)
                for d in ['constant','system','chemkin',cp]:shutil.copytree(source/d,target/d)
                shutil.copy2(source/'case.json',target/'case.json')
            start=time.perf_counter();predictions={};f={};cost=[]
            if a=='controller' and p>1:
                f,cost=extract(source,cp,info);chosen,predictions=choose(model,f,40)
            else:chosen='A0' if a=='controller' else a
            feature=time.perf_counter()-start if a=='controller' else 0.
            decision,migration=action_setup(target,chosen,cp,cost,p)
            start=time.perf_counter();set_control(target,start=float(cp),steps=40,dt=info['dt']);decision+=time.perf_counter()-start
            wall=solve(target,p)
            row=dict(ranks=p,action=a,chosen=chosen,repeat=r,solverWall=wall,decompositionWall=0.,case=info,H=40,
                featureWall=feature,decisionWall=decision,migrationWall=migration,totalWall=wall+feature+decision+migration,predictions=predictions,features=f,
                scope='identical rank-specific checkpoint; continuation and action overhead; common prefix reported separately',
                extrapolation='frozen four-rank 256-cell model evaluated on 512 cells and 1/2/4/6 ranks; rank one has a mandatory no-action guard')
            (target/'manifest.json').write_text(json.dumps(row,indent=2));print('MEASURED scaling',p,a,r,wall,flush=True)
        row=json.loads((target/'manifest.json').read_text());row['path']=str(target.relative_to(ROOT));rows.append(row)
    gates=[]
    for row in rows:
        if row['action']=='A0':continue
        c=ROOT/row['path'];ref=c.with_name(c.name.replace('_'+row['action']+'_','_A0_'));p=row['ranks'];end=latest_time(c,p>1)
        info=row['case']
        fields=['T','p','U','Qdot']+info['species']
        dirs=[canonical_directory(x,end,fields,info['nCells']) for x in [ref,c]] if p>1 else [ref/end,c/end]
        gate=numerical_gate(*dirs,info);gate.update(ranks=p,action=row['action'],repeat=row['repeat']);gates.append(gate)
    (ROOT/'data/processed/scaling.json').write_text(json.dumps(rows,indent=2))
    (ROOT/'data/processed/scaling_validation.json').write_text(json.dumps(gates,indent=2))
    # A rank-specific reference alone does not establish that the strong-scaling
    # configurations solve equivalent trajectories. Compare physical endpoints.
    reference=ROOT/'data/raw/scaling/p1_A0_r0';end=latest_time(reference,False)
    info=json.loads((reference/'case.json').read_text());fields=['T','p','U','Qdot','h','rho']+info['species']
    cross_rank=[]
    for ranks in [2,4,6]:
        target=ROOT/f'data/raw/scaling/p{ranks}_A0_r0'
        if latest_time(target,True)!=end:raise RuntimeError('scaling rank endpoints differ')
        gate=numerical_gate(reference/end,canonical_directory(target,end,fields,info['nCells']),info)
        gate.update(referenceRanks=1,candidateRanks=ranks,scope='complete prefix and continuation at the same physical endpoint')
        cross_rank.append(gate)
    (ROOT/'data/processed/scaling_crossrank_validation.json').write_text(json.dumps(cross_rank,indent=2))
    if not all(g['pass_'] for g in cross_rank):raise RuntimeError('strong-scaling cross-rank trajectory gates failed')

def gamma():
    rows=[]
    jobs=[(regime,g,r) for regime in ['persistent','translating'] for g in [0,.25,1,4,16] for r in range(3)]
    random.Random(653831).shuffle(jobs)
    for regime,g,r in jobs:
        source=ROOT/'data/raw/histories'/regime;info=json.loads((source/'case.json').read_text())
        acquisition_start=time.perf_counter();cost,_=rank_costs(source,'4e-05',info['nCells']);acquisition=time.perf_counter()-acquisition_start
        c=ROOT/f'data/raw/gamma/{regime}_g{g}_r{r}'
        if not (c/'manifest.json').exists():
            copy_checkpoint(source,c,'4e-05');decision,migration=action_setup(c,'AM','4e-05',cost,4,g);decision+=acquisition
            start=time.perf_counter();set_control(c,start=4e-05,steps=80);decision+=time.perf_counter()-start
            wall=solve(c,4)
            from mapping import metrics
            parts=metrics(c)
            row=dict(regime=regime,gamma=g,repeat=r,solverWall=wall,decisionWall=decision,migrationWall=migration,
                totalWall=wall+decision+migration,processorFaces=sum(p['processorFaces'] for p in parts)/2,
                maxNeighbours=max(p['nNeighbours'] for p in parts))
            reference=ROOT/'data/raw/oracle'/regime/'cp4e-05_H80_A0_r0'
            end=latest_time(c,True);fields=['T','p','U','Qdot']+info['species']
            row['gate']=numerical_gate(*[canonical_directory(x,end,fields,info['nCells']) for x in [reference,c]],info)
            (c/'manifest.json').write_text(json.dumps(row,indent=2));print('MEASURED gamma',regime,g,r,wall,flush=True)
        rows.append(json.loads((c/'manifest.json').read_text()))
    (ROOT/'data/processed/gamma.json').write_text(json.dumps(rows,indent=2))

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('mode',choices=['horizons','profiles','scaling','gamma'])
    globals()[parser.parse_args().mode]()
