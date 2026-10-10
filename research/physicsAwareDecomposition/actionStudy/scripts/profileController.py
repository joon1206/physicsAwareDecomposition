"""Representative frozen-controller profiling with explicit controller costs."""
import csv,hashlib,json,random,time
from caseFactory import ROOT,solve,set_control,latest_time
from oracle import copy_checkpoint,action_setup
from features import extract
from analysis import choose
from mapping import canonical_directory
from validation import numerical_gate
def main():
    modelpath=ROOT/'data/processed/model.json';model=json.loads(modelpath.read_text());rows=[]
    jobs=[(c,p,r) for c in ['persistent','transportDominated'] for p in [False,True] for r in range(3)];random.Random(582199).shuffle(jobs)
    for condition,profile,repeat in jobs:
        source=ROOT/'data/raw/histories'/condition;info=json.loads((source/'case.json').read_text())
        target=ROOT/f'data/raw/controllerProfiles/{condition}_p{int(profile)}_r{repeat}'
        if not (target/'manifest.json').exists():
            copy_checkpoint(source,target,'4e-05');t=time.perf_counter();f,cost=extract(source,'4e-05',info);fw=time.perf_counter()-t
            t=time.perf_counter();action,pred=choose(model,f,80);iw=time.perf_counter()-t
            dw,mw=action_setup(target,action,'4e-05',cost,4,profile=profile)
            t=time.perf_counter();set_control(target,start=4e-05,steps=80);dw+=time.perf_counter()-t
            sw=solve(target,4,profile=profile)
            row=dict(regime=condition,profile=profile,repeat=repeat,action=action,features=f,predicted=pred,
                featureWall=fw,inferenceWall=iw,decisionWall=dw,migrationWall=mw,solverWall=sw,totalWall=fw+iw+dw+mw+sw,
                modelSHA256=hashlib.sha256(modelpath.read_bytes()).hexdigest())
            (target/'manifest.json').write_text(json.dumps(row,indent=2));print('PROFILED controller',condition,profile,action,row['totalWall'],flush=True)
        row=json.loads((target/'manifest.json').read_text());row['path']=str(target.relative_to(ROOT));ranks=[];mpi=[]
        for path in target.glob('processor*/postProcessing/performance/rank*.csv'):
            with path.open() as stream:rr=list(csv.DictReader(stream))
            ranks.append({k:sum(float(r[k]) for r in rr) for k in rr[0] if k.endswith('Wall')})
        for path in (target/'mpiProfile').glob('*.csv'):
            with path.open() as stream:mpi.extend(csv.DictReader(stream))
        row.update(phaseRankSums=ranks,MPI=mpi)
        ref=ROOT/f'data/raw/oracle/{condition}/cp4e-05_H80_A0_r{repeat}';fields=['T','h','rho','p','U','Qdot']+info['species']
        row['gate']=numerical_gate(*[canonical_directory(p,latest_time(target,True),fields,info['nCells']) for p in [ref,target]],info);rows.append(row)
    (ROOT/'data/processed/controller_profiles.json').write_text(json.dumps(rows,indent=2))
    if not all(r['gate']['pass_'] for r in rows):raise RuntimeError('controller profiling field gates failed')
if __name__=='__main__':main()
