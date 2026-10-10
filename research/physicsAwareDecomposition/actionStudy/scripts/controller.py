"""Frozen-model checkpoint and live sequential runtime controllers.

The live path sees only fields and clocks produced by its own completed prefix.
This external process orchestrator charges every restart and field write. It is
not a low-latency in-solver redistribution implementation.
"""
import argparse,hashlib,json,random,time
from caseFactory import ROOT,PAD,make_case,decompose,solve,set_control,set_chemistry,latest_time,command
from oracle import copy_checkpoint,action_setup
from features import extract
from analysis import choose,TEST,summary,interval
from mapping import canonical_directory
from validation import numerical_gate

def checkpoint():
    model_path=ROOT/'data/processed/model.json';model=json.loads(model_path.read_text())
    jobs=[(regime,cp,policy,r) for regime in TEST for cp in ['4e-05','0.0002']
          for policy in ['A0','AC','AM','controller'] for r in range(5)]
    random.Random(62479).shuffle(jobs);rows=[]
    for regime,cp,policy,r in jobs:
        source=ROOT/'data/raw/histories'/regime;info=json.loads((source/'case.json').read_text())
        c=ROOT/f'data/raw/deployment/{regime}/cp{cp}_{policy}_r{r}'
        if not (c/'manifest.json').exists():
            copy_checkpoint(source,c,cp)
            start=time.perf_counter()
            if policy in ['AM','controller']:
                f,cost=extract(source,cp,info);feature_wall=time.perf_counter()-start
            else:f,cost,feature_wall={},[],0.
            inference_start=time.perf_counter()
            action,predictions=choose(model,f,80) if policy=='controller' else (policy,{})
            inference=time.perf_counter()-inference_start
            decision,migration=action_setup(c,action,cp,cost,4)
            control_start=time.perf_counter();set_control(c,start=float(cp),steps=80,dt=info['dt']);decision+=time.perf_counter()-control_start
            wall=solve(c,4)
            extra=feature_wall+inference if policy=='controller' else feature_wall if policy=='AM' else 0.
            row=dict(regime=regime,checkpoint=cp,policy=policy,repeat=r,action=action,solverWall=wall,
                decisionWall=decision,migrationWall=migration,featureWall=feature_wall if policy in ['controller','AM'] else 0,
                inferenceWall=inference if policy=='controller' else 0,totalWall=wall+decision+migration+extra,
                predicted=predictions,features=f,modelSHA256=hashlib.sha256(model_path.read_bytes()).hexdigest())
            (c/'manifest.json').write_text(json.dumps(row,indent=2));print('MEASURED deployment',regime,cp,policy,r,action,row['totalWall'],flush=True)
        row=json.loads((c/'manifest.json').read_text());row['path']=str(c.relative_to(ROOT));rows.append(row)
    for row in rows:
        if row['policy']=='A0':continue
        c=ROOT/row['path'];ref=c.with_name(c.name.replace('_'+row['policy']+'_','_A0_'))
        info=json.loads((c/'case.json').read_text());end=latest_time(c,True);fields=['T','p','U','Qdot']+info['species']
        row['gate']=numerical_gate(*[canonical_directory(x,end,fields,info['nCells']) for x in [ref,c]],info)
    result=[]
    for regime in TEST:
        for cp in ['4e-05','0.0002']:
            base=[r['totalWall'] for r in rows if r['regime']==regime and r['checkpoint']==cp and r['policy']=='A0']
            for policy in ['A0','AC','AM','controller']:
                group=[r for r in rows if r['regime']==regime and r['checkpoint']==cp and r['policy']==policy]
                times=[r['totalWall'] for r in group]
                result.append(dict(regime=regime,checkpoint=cp,policy=policy,stats=summary(times),speedup=summary(base)['median']/summary(times)['median'],
                    speedupCI=[1.,1.] if policy=='A0' else interval(base,times),valid=all(r.get('gate',dict(pass_=True))['pass_'] for r in group),
                    actions=[r['action'] for r in group]))
    (ROOT/'data/processed/deployment_raw.json').write_text(json.dumps(rows,indent=2))
    (ROOT/'data/processed/deployment_summary.json').write_text(json.dumps(result,indent=2))

def live():
    # Build once between timed campaigns; standard oracle binary stays intact.
    command(['bash',str(PAD/'actionStudy/scripts/buildRestart.sh')],PAD,ROOT/'data/raw/build/restartBuildDriver.log')
    command(['bash',str(PAD/'actionStudy/scripts/buildRedistributor.sh')],PAD,ROOT/'data/raw/build/redistributorBuildDriver.log')
    if not (ROOT/'data/processed/repeated_migration_validation.json').exists():
        command(['bash',str(PAD/'actionStudy/scripts/run.sh'),'repeatedMigrationRegression.py'],PAD,ROOT/'data/raw/build/repeatedMigrationDriver.log')
    regression_path=ROOT/'data/processed/restart_regression.json'
    previous=json.loads(regression_path.read_text()) if regression_path.exists() else []
    if not previous or not all(g['pass_'] and g.get('protocol')=='restore he, psi oldTime and dpdt v4' for g in previous):
        if previous:
            tag=previous[0].get('protocol','dpdt_only').replace(' ','_')
            (ROOT/f'data/processed/restart_regression_{tag}_rejected.json').write_text(json.dumps(previous,indent=2))
        command(['bash',str(PAD/'actionStudy/scripts/run.sh'),'restartRegression.py'],PAD,ROOT/'data/raw/build/restartRegressionDriver.log')
    if not all(g['pass_'] for g in json.loads(regression_path.read_text())):raise RuntimeError('restart regression did not pass')
    model_path=ROOT/'data/processed/model.json';model=json.loads(model_path.read_text());rows=[]
    executable_hashes={name:hashlib.sha256((PAD/'build/bin'/name).read_bytes()).hexdigest() for name in ['reactingFoamPADRestart','redistributeParPAD']}
    (ROOT/'docs/live_execution_manifest.json').write_text(json.dumps(dict(executablesSHA256=executable_hashes,
        modelSHA256=hashlib.sha256(model_path.read_bytes()).hexdigest(),utilityPatch='redistribute_v2012.patch'),indent=2))
    jobs=[(regime,policy,r) for regime in TEST+['persistent','transportDominated']
          for policy in ['nativeContinuous','continuous','ACContinuous','A0','AC','AM','imbalanceThreshold','persistenceBreakEven','controller'] for r in range(3)]
    random.Random(6283).shuffle(jobs)
    for regime,policy,r in jobs:
        c=ROOT/f'data/raw/live/{regime}_{policy}_r{r}'
        if not (c/'manifest.json').exists():
            production_start=time.perf_counter()
            uninterrupted=policy in ['continuous','nativeContinuous','ACContinuous']
            make_case('live/'+c.name,regime,nx=32,ny=8,steps=140 if uninterrupted else 20,trace=0 if uninterrupted else 1)
            set_control(c,steps=140 if uninterrupted else 20,restart_state=True)
            if policy=='nativeContinuous':
                prop=c/'constant/chemistryProperties';prop.write_text(prop.read_text().replace('solver costOde;','solver ode;'))
            if policy=='ACContinuous':set_chemistry(c,action='AC',trace=0)
            info=json.loads((c/'case.json').read_text());setup,_=decompose(c,4)
            # A real measured prefix, not a copied trajectory with future data.
            elapsed=solve(c,4,exe='reactingFoamPADRestart');events=[];previous_cost=None;current_action='A0';last_change=-1000
            for index in ([] if uninterrupted else [20,60,100]):
                cp=latest_time(c,True)
                if abs(float(cp)-index*info['dt'])>1e-12:raise RuntimeError('live prefix is not at requested physical time')
                feature_start=time.perf_counter()
                if policy in ['controller','imbalanceThreshold','persistenceBreakEven','AM']:
                    f,cost=extract(c,cp,info,previous=previous_cost,lag_steps=40 if previous_cost is not None else None)
                    previous_cost=cost;fw=time.perf_counter()-feature_start
                else:f,cost,fw={},[],0.
                inference_start=time.perf_counter()
                if policy=='controller':action,pred=choose(model,f,40,previous=current_action,elapsed=index-last_change)
                elif policy=='imbalanceThreshold':action,pred=('AC' if f['chemistryImbalance']>1.2 else 'A0'),{}
                elif policy=='persistenceBreakEven':
                    expected=f['chemistrySeconds']*40*max(0.,1-1/max(1.,f['chemistryImbalance']))*min(40,f['lifetimeSteps'])/40
                    action,pred=('AC' if expected>model['setup']['AC']+.02 else 'A0'),dict(expectedSaved=expected,setup=model['setup']['AC'])
                else:action,pred=policy,{}
                iw=time.perf_counter()-inference_start
                if action!=current_action:last_change=index
                current_action=action
                dw,mw=action_setup(c,action,cp,cost,4,redistributor='redistributeParPAD')
                cs=time.perf_counter();set_control(c,start=float(cp),steps=40,dt=info['dt'],restart_state=True);dw+=time.perf_counter()-cs
                # Each process starts a new trace file; previous cost is retained
                # in controller memory rather than read from a future file.
                feature_policy=policy in ['controller','imbalanceThreshold','persistenceBreakEven','AM']
                sw=solve(c,4,exe='reactingFoamPADRestart');costwall=sw+dw+mw+(fw+iw if feature_policy else 0)
                elapsed+=costwall
                events.append(dict(index=index,time=float(cp),action=action,predicted=pred,features=f,
                    solverWall=sw,featureWall=fw if feature_policy else 0,inferenceWall=iw if feature_policy else 0,
                    decisionWall=dw,migrationWall=mw,cumulativeWall=time.perf_counter()-production_start,
                    cumulativeScope='direct wall since preprocessing began'))
            if abs(float(latest_time(c,True))-140*info['dt'])>1e-12:raise RuntimeError('live trajectory did not reach 140 physical steps')
            production_wall=time.perf_counter()-production_start
            component_wall=elapsed+setup+info['preprocessingWall']
            row=dict(regime=regime,policy=policy,repeat=r,totalWall=production_wall,componentWall=component_wall,orchestratorOtherWall=production_wall-component_wall,decompositionWall=setup,preprocessingWall=info['preprocessingWall'],
                events=events,modelSHA256=hashlib.sha256(model_path.read_bytes()).hexdigest(),executablesSHA256=executable_hashes,migrationUtility='redistributeParPAD' if any(e['action'] in ['AM','AH'] for e in events) else 'unused',restartState='solved he and dpdt restored; psi.oldTime preallocated before restart thermo update; opt-in state-preserving executable',scope='end to end 140 physical steps: preprocessing, decomposition, prefix, every process startup/write and controller action; offline reusable model acquisition reported separately')
            (c/'manifest.json').write_text(json.dumps(row,indent=2));print('MEASURED live',regime,policy,r,row['totalWall'],flush=True)
        row=json.loads((c/'manifest.json').read_text());row['path']=str(c.relative_to(ROOT));rows.append(row)
    for row in rows:
        if row['policy']=='nativeContinuous':continue
        c=ROOT/row['path'];ref=c.with_name(c.name.replace('_'+row['policy']+'_','_nativeContinuous_'))
        info=json.loads((c/'case.json').read_text());fields=['T','p','U','Qdot']+info['species'];end=latest_time(c,True)
        row['gate']=numerical_gate(*[canonical_directory(x,end,fields,info['nCells']) for x in [ref,c]],info)
    (ROOT/'data/processed/live.json').write_text(json.dumps(rows,indent=2))

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('mode',choices=['checkpoint','live']);globals()[p.parse_args().mode]()
