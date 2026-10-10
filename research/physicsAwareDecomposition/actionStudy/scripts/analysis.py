"""Statistics and case-held-out interpretable action models, stdlib only.

No held-out observations are used to fit coefficients, costs, or uncertainty.
Policy comparisons here are retrospective checkpoint replay, not live runs.
"""
import collections, csv, json, math, random, statistics, time,os
from pathlib import Path

ROOT=Path(os.environ.get('PAD_ACTION_ROOT',Path(__file__).resolve().parents[1]))
TRAIN=['persistent','translating','ignition','transportDominated','chemistryDominated']
VALID=['uniform','decay']
TEST=['heldoutMoving','heldoutIgnition','heldoutPersistent']
ACTIONS=['A0','AC','AM','AH']

def summary(x):
    m=statistics.mean(x);sd=statistics.stdev(x) if len(x)>1 else 0.
    return dict(n=len(x),median=statistics.median(x),mean=m,sd=sd,min=min(x),max=max(x),CV=sd/m)

def interval(x,y,seed=7923,B=4000):
    rng=random.Random(seed);ratios=[]
    for _ in range(B):
        a=[rng.choice(x) for _ in x];b=[rng.choice(y) for _ in y]
        ratios.append(statistics.median(a)/statistics.median(b))
    ratios.sort()
    return [ratios[int(.025*B)],ratios[int(.975*B)]]

def solve_linear(A,b):
    n=len(b);a=[list(row)+[y] for row,y in zip(A,b)]
    for k in range(n):
        pivot=max(range(k,n),key=lambda i:abs(a[i][k]));a[k],a[pivot]=a[pivot],a[k]
        if abs(a[k][k])<1e-14:raise ValueError('singular matrix')
        scale=a[k][k];a[k]=[v/scale for v in a[k]]
        for i in range(n):
            if i!=k:
                scale=a[i][k];a[i]=[x-scale*y for x,y in zip(a[i],a[k])]
    return [row[-1] for row in a]

def ridge(X,y,penalty=2.):
    columns=list(zip(*X));mu=[statistics.mean(v) for v in columns]
    scale=[max(statistics.pstdev(v),1e-12) for v in columns]
    Z=[[1.]+[(a-m)/s for a,m,s in zip(row,mu,scale)] for row in X]
    n=len(Z[0]);A=[[sum(row[i]*row[j] for row in Z)+(penalty if i==j and i>0 else 0) for j in range(n)] for i in range(n)]
    b=[sum(row[i]*v for row,v in zip(Z,y)) for i in range(n)]
    beta=solve_linear(A,b)
    return dict(mu=mu,scale=scale,beta=beta,penalty=penalty)

def predict(model,x):
    z=[1.]+[(a-m)/s for a,m,s in zip(x,model['mu'],model['scale'])]
    return sum(a*b for a,b in zip(z,model['beta']))

def design(f,H,variant='full'):
    chem=f['chemistrySeconds']*H
    excess=chem*max(0.,1-1/max(1.,f['chemistryImbalance']))
    persistence=min(H,f['lifetimeSteps'])/H
    transport=(f.get('transportSeconds',0)+f.get('pressureSeconds',0))*H
    communication=f['processorFaces']/f['nCells']
    if variant=='noPersistence':persistence=1.
    if variant=='noCommunication':communication=0.
    if variant=='onlyImbalance':return [f['chemistryImbalance']]
    if variant=='onlyPreviousCost':return [chem,f.get('previousImbalance',f['chemistryImbalance'])]
    if variant=='onlyEMA':return [chem,f.get('twoSnapshotEMAImbalance',f['chemistryImbalance'])]
    return [chem,excess,excess*persistence,transport,communication]

def dataset():
    raw=json.loads((ROOT/'data/processed/oracle_raw.json').read_text())
    gates=json.loads((ROOT/'data/processed/oracle_validation.json').read_text())
    failed={(g['regime'],g['checkpoint'],g['horizonSteps'],g['action']) for g in gates if not g['pass_']}
    groups=collections.defaultdict(lambda:collections.defaultdict(list))
    for r in raw:
        groups[(r['regime'],r['checkpoint'],r['horizonSteps'])][r['action']].append(r)
    states=[]
    for key,actions in sorted(groups.items()):
        if len(actions)!=4:continue
        s=dict(regime=key[0],checkpoint=key[1],H=key[2],features=actions['A0'][0]['currentFeatures'],actions={})
        # Recompute two-snapshot EMA diagnostics from retained past-only traces.
        # Original measured feature-extraction clocks remain in raw manifests.
        from features import extract
        info=actions['A0'][0]['case']
        updated,_=extract(ROOT/'data/raw/histories'/key[0],key[1],info)
        s['features'].update(updated)
        for a,runs in actions.items():
            total=[r['totalWall'] for r in runs];solver=[r['solverWall'] for r in runs]
            phases={}
            for name in ['chemistryWall','momentumWall','speciesWall','energyWall','pressureWall','stepWall','ioWall']:
                # Rank maximum integrated duration is an explanatory statistic,
                # not an additive critical path across MPI-overlapped phases.
                phases[name]=statistics.median(max(v[name] for v in r['phaseRankSums'].values()) for r in runs)
            s['actions'][a]=dict(total=summary(total),solver=summary(solver),phases=phases,
                setup=statistics.median(r['decisionWall']+r['migrationWall'] for r in runs),
                extraction=statistics.median(r['featureExtractionWall'] for r in runs),
                speedup=statistics.median([r['totalWall'] for r in actions['A0']])/statistics.median(total),
                speedupCI=[1.,1.] if a=='A0' else interval([r['totalWall'] for r in actions['A0']],total),
                valid=(key+(a,)) not in failed,processorFaces=statistics.median(r['processorFaces'] for r in runs),
                linearIterations={k:statistics.median(r['linearIterationSums'].get(k,0) for r in runs) for k in runs[0]['linearIterationSums']})
        valid=[a for a in ACTIONS if s['actions'][a]['valid']]
        ranked=sorted(valid,key=lambda a:s['actions'][a]['total']['median'])
        s['winner']=ranked[0];s['margin']=s['actions'][ranked[1]]['total']['median']-s['actions'][ranked[0]]['total']['median']
        s['split']='train' if s['regime'] in TRAIN else 'validation' if s['regime'] in VALID else 'test'
        states.append(s)
    return states

def fit(states,variant='full'):
    start=time.perf_counter();train=[s for s in states if s['split']=='train']
    models={};setup={};errors={}
    for a in ACTIONS[1:]:
        rows=[s for s in train if s['actions'][a]['valid']]
        if not rows:
            size=len(design(train[0]['features'],train[0]['H'],variant))
            models[a]=dict(mu=[0.]*size,scale=[1.]*size,beta=[1e6]+[0.]*size,penalty=2.)
            setup[a]=0.;errors[a]=1e6
            continue
        X=[design(s['features'],s['H'],variant) for s in rows]
        y=[s['actions'][a]['solver']['median']-s['actions']['A0']['solver']['median'] for s in rows]
        models[a]=ridge(X,y)
        setup[a]=statistics.median(s['actions'][a]['setup'] for s in rows)
        # Validation by complete cases; never test. Conservative absolute-error
        # margin also includes training error when validation is easy.
        candidates=rows+[s for s in states if s['split']=='validation' and s['actions'][a]['valid']]
        residual=[abs(predict(models[a],design(s['features'],s['H'],variant))-(s['actions'][a]['solver']['median']-s['actions']['A0']['solver']['median'])) for s in candidates]
        residual.sort();errors[a]=residual[min(len(residual)-1,math.ceil(.9*len(residual))-1)]
    return dict(models=models,setup=setup,uncertainty=errors,variant=variant,trainingCases=TRAIN,
        validationCases=VALID,testCases=TEST,trainingWall=time.perf_counter()-start)

def choose(model,f,H,previous='A0',elapsed=1000,variant=None):
    variant=variant or model['variant'];scores={'A0':0.};predictions={}
    for a in ACTIONS[1:]:
        delta=predict(model['models'][a],design(f,H,model['variant']))
        if variant=='noTransport':
            # A precisely defined omission: remove fitted transport term from
            # the inference prediction; do not claim a separate network model.
            x=design(f,H,model['variant']);x[3]=model['models'][a]['mu'][3]
            delta=predict(model['models'][a],x)
        setup=0 if variant=='noMigration' else model['setup'][a]
        error=0 if variant=='noUncertainty' else model['uncertainty'][a]
        margin=max(.02,.025*f['timestepSeconds']*H)
        scores[a]=delta+setup+error+margin
        predictions[a]=dict(solverDelta=delta,setup=setup,uncertainty=error,margin=margin,score=scores[a])
    chosen=min(scores,key=scores.get)
    # Hold at least 40 physical steps between changing ownership/scheduler.
    if chosen!=previous and elapsed<40:chosen=previous
    return chosen,predictions

def policy_actions(s,model):
    f=s['features'];H=s['H']
    excess=f['chemistrySeconds']*H*max(0.,1-1/max(1.,f['chemistryImbalance']))
    lifetime=min(H,f['lifetimeSteps'])/H
    return dict(never='A0',imbalanceThreshold='AC' if f['chemistryImbalance']>1.2 else 'A0',
        periodicChemistry='AC',periodicMesh='AM',stuttgartEveryStep='AC',
        persistenceBreakEven='AC' if excess*lifetime>model['setup']['AC']+.02 else 'A0',
        wholeSolver=choose(model,f,H)[0],oracle=s['winner'])

def metrics(decisions):
    if not decisions:return {}
    return dict(n=len(decisions),meanRegret=statistics.mean(r['regret'] for r in decisions),
        medianRegret=statistics.median(r['regret'] for r in decisions),worstRegret=max(r['regret'] for r in decisions),
        oracleOptimalFraction=statistics.mean(r['chosen']==r['oracle'] for r in decisions),
        harmfulFraction=statistics.mean(r['harmful'] for r in decisions),
        unnecessaryFraction=statistics.mean(r['chosen']!='A0' and r['oracle']=='A0' for r in decisions),
        missedFraction=statistics.mean(r['chosen']=='A0' and r['oracle']!='A0' for r in decisions),
        aggregateSpeedup=sum(r['baseline'] for r in decisions)/sum(r['cost'] for r in decisions))

def replay(states,model,ablations):
    """Evaluate frozen policies, sharing required mesh acquisition exactly once."""
    decisions=[]
    for s in states:
        policies=policy_actions(s,model)
        for v,m in ablations.items():policies['ablation_'+v]=choose(m,s['features'],s['H'])[0]
        for v in ['noTransport','noUncertainty','noMigration']:policies['ablation_'+v]=choose(model,s['features'],s['H'],variant=v)[0]
        for policy,a in policies.items():
            driven=policy.startswith(('whole','persistence','imbalance','ablation'))
            inference_start=time.perf_counter()
            if policy=='wholeSolver':a=choose(model,s['features'],s['H'])[0]
            elif policy.startswith('ablation_'):
                variant=policy.removeprefix('ablation_');a=choose(ablations.get(variant,model),s['features'],s['H'],variant=variant)[0]
            elif policy=='imbalanceThreshold':a='AC' if s['features']['chemistryImbalance']>1.2 else 'A0'
            elif policy=='persistenceBreakEven':
                f=s['features'];H=s['H'];excess=f['chemistrySeconds']*H*max(0.,1-1/max(1.,f['chemistryImbalance']))
                a='AC' if excess*min(H,f['lifetimeSteps'])/H>model['setup']['AC']+.02 else 'A0'
            inference=time.perf_counter()-inference_start if driven else 0.
            valid=s['actions'][a]['valid'];a=a if valid else 'A0'
            # J(AM/AH) already pays this same extraction pass for weights.
            # A controller can reuse its cost array, as the deployed path does.
            feature=s['actions'][a]['extraction'] if driven and a not in ['AM','AH'] else 0.
            overhead=feature+inference
            cost=s['actions'][a]['total']['median']+overhead;oracle=s['actions'][s['winner']]['total']['median']
            base=s['actions']['A0']['total']['median']
            decisions.append(dict(regime=s['regime'],checkpoint=s['checkpoint'],H=s['H'],split=s['split'],policy=policy,
                chosen=a,oracle=s['winner'],cost=cost,baseline=base,regret=cost-oracle,harmful=cost>base,
                numericalFallback=not valid,inferenceWall=inference,featureWall=feature,
                sharedWeightAcquisition=driven and a in ['AM','AH']))
    result={}
    for split in ['train','validation','test','all']:
        result[split]={p:metrics([r for r in decisions if r['policy']==p and (split=='all' or r['split']==split)]) for p in sorted(set(r['policy'] for r in decisions))}
    return decisions,result

def main():
    states=dataset();model=fit(states)
    variants=['full','noPersistence','noCommunication','onlyImbalance','onlyPreviousCost','onlyEMA']
    ablations={v:fit(states,v) for v in variants};decisions,result=replay(states,model,ablations)
    for name,data in [('oracle_summary',states),('model',model),('policy_decisions',decisions),('policy_summary',result),('ablation_models',ablations)]:
        (ROOT/f'data/processed/{name}.json').write_text(json.dumps(data,indent=2))
    print('ANALYZED states',len(states),'valid oracle winners',collections.Counter(s['winner'] for s in states))
    print('HELDOUT retrospective',json.dumps(result['test'],indent=2))

if __name__=='__main__':main()
