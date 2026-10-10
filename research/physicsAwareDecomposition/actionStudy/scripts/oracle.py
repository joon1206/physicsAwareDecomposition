"""Measured checkpoint action oracle, using restart-based mesh redistribution.

The mesh action is a native redistributePar operation between solver processes.
Its full process wall time is charged. This is not in-solver live migration.
All candidates start from exactly the same fields, mesh and chemDeltaT history.
"""
import argparse, csv, datetime, hashlib, json, os, random, re, shutil, subprocess, time
from pathlib import Path
from caseFactory import (PAD,ROOT,SPECS,make_case,decompose,solve,command,
                         set_control,set_chemistry,latest_time,reconstruct)
from features import extract,rank_costs,normalize
from foamio import read_field
from validation import numerical_gate
from mapping import ids,metrics,save_ids,canonical_directory

ACTIONS=['A0','AC','AM','AH']

def copy_checkpoint(source,target,time_name):
    if target.exists():raise RuntimeError(f'refusing overwrite {target}')
    target.mkdir(parents=True)
    for d in ['constant','system','chemkin']:shutil.copytree(source/d,target/d)
    shutil.copy2(source/'case.json',target/'case.json')
    if (source/'globalCellIds.json').exists():shutil.copy2(source/'globalCellIds.json',target/'globalCellIds.json')
    for p in source.glob('processor[0-9]*'):
        (target/p.name).mkdir()
        shutil.copytree(p/'constant',target/p.name/'constant')
        shutil.copytree(p/time_name,target/p.name/time_name)
    # Native redistributePar reads rank-local state; no serial reconstruction
    # is performed before migration. Reconstruction for validation is untimed.

def local_weights(case,time_name,global_weights):
    for p in case.glob('processor[0-9]*'):
        identity=ids(case,p)
        # Preserve the native constraint patch types by copying chemCost's
        # complete boundary dictionary, and replace only dimensions/values.
        source=(p/time_name/'chemCost').read_text()
        boundary=source[source.index('boundaryField'):]
        from caseFactory import header
        text=header('cellWeight','volScalarField')+'dimensions [0 0 0 0 0 0 0];\n'
        text+=f'internalField nonuniform List<scalar>\n{len(identity)}\n(\n'
        text+='\n'.join(f'{global_weights[i]:.17g}' for i in identity)+'\n);\n'+boundary
        (p/time_name/'cellWeight').write_text(text)
        id_text=header('padGlobalId','volScalarField')+'dimensions [0 0 0 0 0 0 0];\n'
        id_text+=f'internalField nonuniform List<scalar>\n{len(identity)}\n(\n'
        id_text+='\n'.join(str(i) for i in identity)+'\n);\n'+boundary
        (p/time_name/'padGlobalId').write_text(id_text)

def action_setup(case,action,time_name,cost,ranks,gamma=1.,profile=False,redistributor='redistributePar'):
    decision_start=time.perf_counter()
    set_chemistry(case,action,trace=0)
    if action in ['AM','AH']:
        weights=normalize(cost,gamma=gamma)
        local_weights(case,time_name,weights)
        f=case/'system/decomposeParDict'
        f.write_text(f'FoamFile {{version 2.0; format ascii; class dictionary; object decomposeParDict;}}\nnumberOfSubdomains {ranks};\nmethod scotch;\nweightField cellWeight;\n')
    decision=time.perf_counter()-decision_start
    migration=0.
    if action in ['AM','AH']:
        args=['mpirun','--bind-to','core','--map-by','core','--nooversubscribe',
              '-np',str(ranks),redistributor,'-parallel','-overwrite','-time',time_name]
        migration_start=time.perf_counter()
        env=os.environ.copy()
        if profile:
            directory=case/'migrationMPI';directory.mkdir(exist_ok=True)
            env['PAD_MPI_PROFILE_DIR']=str(directory)
            env['LD_PRELOAD']=str(PAD/'build/lib/libpadMPIProfile.so')
        command(args,case,case/'redistribute.log',timeout=180,env=env)
        save_ids(case,time_name)
        migration=time.perf_counter()-migration_start
    return decision,migration

def run_branch(source,time_name,action,steps,repeat,campaign='oracle',profile=False):
    info=json.loads((source/'case.json').read_text())
    ranks=len(list(source.glob('processor[0-9]*')))
    target=ROOT/'data/raw'/campaign/source.name/f'cp{time_name}_H{steps}_{action}_r{repeat}'
    copy_checkpoint(source,target,time_name)
    feature_start=time.perf_counter()
    current,cost=extract(source,time_name,info)
    extraction=time.perf_counter()-feature_start
    decision,migration=action_setup(target,action,time_name,cost,ranks,profile=profile)
    if action in ['AM','AH']:decision+=extraction
    control_start=time.perf_counter()
    set_control(target,start=float(time_name),steps=steps,dt=info['dt'])
    decision+=time.perf_counter()-control_start
    wall=solve(target,ranks,timeout=300,profile=profile)
    row=dict(regime=source.name,checkpoint=time_name,horizonSteps=steps,
             horizonSeconds=steps*info['dt'],action=action,repeat=repeat,
             solverWall=wall,decisionWall=decision,migrationWall=migration,
             totalWall=wall+decision+migration,featureExtractionWall=extraction,
             weightAcquisitionCharged=action in ['AM','AH'],
             ranks=ranks,nodes=1,profile=profile,currentFeatures=current,
             timestamp=datetime.datetime.now(datetime.timezone.utc).isoformat(),
             gitSHA=subprocess.check_output(['git','rev-parse','HEAD'],cwd=PAD,text=True).strip(),
             upstreamSHA='c67d87052ec29375c5d3580888aa65a64917024b',
             OpenFOAM=os.environ['WM_PROJECT_VERSION'],case=info,
             timingMethod='blocking process wait with independent watchdog',
             rankPlacement='--bind-to core --map-by core --nooversubscribe',
             writeProtocol='state-preserving physical endpoint v3; solved he and dpdt restored; psi oldTime preallocated; endpoint and step count asserted',
             scope='restart continuation wall including solver startup/final IO; weight acquisition/construction and native redistribution charged for AM/AH; experiment duplication excluded; other analysis features excluded until required by a controller')
    (target/'manifest.json').write_text(json.dumps(row,indent=2))
    print('MEASURED',source.name,time_name,steps,action,repeat,round(wall,4),round(migration,4),flush=True)
    return target

def histories(regimes,ranks=4,nx=32,ny=8):
    for regime in regimes:
        path=ROOT/'data/raw/histories'/regime
        if path.exists() and (path/'history.json').exists():continue
        if path.exists():raise RuntimeError(f'incomplete history retained: {path}')
        # GRI's expensive ignition pilot establishes a shorter bounded budget.
        steps=40 if regime=='chemistryDominated' else 120
        c=make_case('histories/'+regime,regime,nx=nx,ny=ny,steps=steps,trace=1)
        set_control(c,steps=steps,dt=2e-6,write_interval=20)
        setup,parts=decompose(c,ranks)
        elapsed=solve(c,ranks,timeout=300)
        (c/'history.json').write_text(json.dumps(dict(solverWall=elapsed,decompositionWall=setup,ranks=ranks),indent=2))
        print('MEASURED history',regime,elapsed,flush=True)

def collect(validate=True):
    manifests=[]
    for m in (ROOT/'data/raw/oracle').glob('*/*/manifest.json'):
        row=json.loads(m.read_text());case=m.parent
        # The extraction pass was independently timed before every action.
        # It supplies AM/AH's weights and is therefore an actual required cost.
        # Older rows retain that exact measured duration; account for it once.
        if row['action'] in ['AM','AH'] and not row.get('weightAcquisitionCharged',False):
            row['decisionWall']+=row['featureExtractionWall'];row['totalWall']+=row['featureExtractionWall']
            row['weightAcquisitionCharged']=True
            row['accountingCorrection']='Required weight acquisition charged from its original per-run measured extraction timer; no rerun, estimate or timing removal.'
            m.write_text(json.dumps(row,indent=2))
        rank_rows=[]
        for p in case.glob('processor[0-9]*'):
            for f in (p/'postProcessing/performance').glob('rank*.csv'):
                with f.open() as stream:rank_rows.extend(csv.DictReader(stream))
        row['phaseRankSums']={}
        for rank in sorted(set(r['rank'] for r in rank_rows)):
            rows=[r for r in rank_rows if r['rank']==rank]
            row['phaseRankSums'][rank]={k:sum(float(r[k]) for r in rows) for k in rows[0] if k.endswith('Wall')}
        row['linearIterationSums']={}
        for field,iterations in re.findall(r'Solving for (\w+),[^\n]*No Iterations (\d+)',(case/'solver.log').read_text()):
            row['linearIterationSums'][field]=row['linearIterationSums'].get(field,0)+int(iterations)
        parts=metrics(case)
        row['parts']=[{k:v for k,v in p.items() if k!='ids'} for p in parts]
        row['processorFaces']=sum(p['processorFaces'] for p in parts)/2
        row['maxNeighbours']=max(p['nNeighbours'] for p in parts)
        row['normalExit']='\nEnd\n' in (case/'solver.log').read_text()
        row['relativeDirectory']=str(case.relative_to(ROOT))
        manifests.append(row)
    (ROOT/'data/processed/oracle_raw.json').write_text(json.dumps(manifests,indent=2))
    if validate:
        gates=[]
        for row in manifests:
            if row['action']=='A0':continue
            path=ROOT/row['relativeDirectory']
            reference=path.with_name(path.name.replace('_'+row['action']+'_','_A0_'))
            if not reference.exists():continue
            end=latest_time(path,True)
            fields=['T','p','U','Qdot']+row['case']['species']
            dirs=[canonical_directory(case,end,fields,row['case']['nCells']) for case in [reference,path]]
            gate=numerical_gate(*dirs,row['case'])
            gate.update(regime=row['regime'],checkpoint=row['checkpoint'],horizonSteps=row['horizonSteps'],action=row['action'])
            gate['repeat']=row['repeat'];gates.append(gate)
        (ROOT/'data/processed/oracle_validation.json').write_text(json.dumps(gates,indent=2))
        if not all(g['pass_'] for g in gates):raise RuntimeError('oracle numerical gate failure; retained rejected runs')
    return manifests

def main():
    parser=argparse.ArgumentParser();parser.add_argument('mode',choices=['pilot','small','full','collect','histories'])
    parser.add_argument('--repeats',type=int,default=5);args=parser.parse_args()
    if args.mode=='collect':collect();return
    regimes=list(SPECS)
    if args.mode=='pilot':regimes=['persistent','transportDominated']
    histories(regimes)
    if args.mode=='histories':return
    jobs=[]
    for regime in regimes:
        for checkpoint in ([20] if args.mode=='pilot' or regime=='chemistryDominated' else [20,100]):
            horizons=([20] if regime=='chemistryDominated' else [80])
            if args.mode=='full' and regime!='chemistryDominated':horizons=[20,80,320]
            for H in horizons:
                for rep in range(1 if args.mode=='pilot' else args.repeats):
                    for a in ACTIONS:jobs.append((regime,checkpoint,H,rep,a))
    random.Random(472981).shuffle(jobs)
    failures=[]
    for regime,cp,H,rep,action in jobs:
        source=ROOT/'data/raw/histories'/regime
        time_name=format(cp*2e-6,'.12g')
        target=ROOT/'data/raw/oracle'/regime/f'cp{time_name}_H{H}_{action}_r{rep}'
        if (target/'manifest.json').exists():continue
        try:run_branch(source,time_name,action,H,rep)
        except RuntimeError as error:
            failures.append(dict(regime=regime,cp=cp,H=H,repeat=rep,action=action,error=str(error)))
            (ROOT/'data/processed/oracle_failures.json').write_text(json.dumps(failures,indent=2))
            print('RETAINED failure',error,flush=True)
    collect()

if __name__=='__main__':main()
