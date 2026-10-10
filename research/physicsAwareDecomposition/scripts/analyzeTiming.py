#!/usr/bin/env python3
"""Strict offline aggregation and deterministic bootstrap; no MPI-time inference."""
import os,argparse,csv,json,math,random,statistics
from pathlib import Path
from collections import defaultdict
from models import metrics,correlation,break_even
from foamio import read_field
from compareFields import compare
ROOT=Path(os.environ.get('PAD_OUTPUT_ROOT',Path(__file__).resolve().parents[1]));OUT=ROOT/'data/processed';OUT.mkdir(parents=True,exist_ok=True)
def csvout(path,rows):
    if not rows:return
    with path.open('w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
def bootstrap(a,b,samples=5000):
    rng=random.Random(7349);v=[]
    for _ in range(samples):
        x=statistics.median(rng.choices(a,k=len(a)));y=statistics.median(rng.choices(b,k=len(b)));v.append(x/y)
    v.sort();return [v[int(.025*samples)],v[int(.975*samples)]]
def stats(a):
    return {'median':statistics.median(a),'mean':statistics.fmean(a),'std':statistics.stdev(a) if len(a)>1 else 0,'min':min(a),'max':max(a),'cv':statistics.pstdev(a)/statistics.fmean(a) if statistics.fmean(a) else 0}
def timing(case,p,warmup=0):
    paths=[case/'postProcessing/performance/rank0000.csv'] if p==1 else [case/f'processor{r}/postProcessing/performance/rank{r:04d}.csv' for r in range(p)]
    data={}
    for rank,path in enumerate(paths):
        rows=list(csv.DictReader(path.open()))
        if not rows:raise ValueError('empty timing file')
        for row in rows:
            if int(row['rank'])!=rank:raise ValueError('rank metadata mismatch')
            for k in ['stepWall','chemistryWall','speciesWall','energyWall','momentumWall','pressureWall','rhoWall','turbulenceWall','ioWall']:
                if not math.isfinite(float(row[k])) or float(row[k])<0:raise ValueError('invalid timing')
            index=int(row['timeIndex']);data.setdefault(index,{})[rank]=row
    if any(len(v)!=p for v in data.values()):raise ValueError('incomplete rank/time matrix')
    ts=sorted(data);selected=ts[warmup:-1] if len(ts)>warmup+1 else ts
    phases=['stepWall','chemistryWall','speciesWall','energyWall','momentumWall','pressureWall','ioWall']
    rows=[]
    for t in ts:
        d={'timeIndex':t}
        for phase in phases:
            m=metrics([float(data[t][r][phase]) for r in range(p)])
            d.update({phase+'_'+k:v for k,v in m.items()})
        d['chemistryFraction']=sum(float(data[t][r]['chemistryWall']) for r in range(p))/sum(float(data[t][r]['stepWall']) for r in range(p))
        rows.append(d)
    totals={phase:[sum(float(data[t][r][phase]) for t in selected) for r in range(p)] for phase in phases}
    return {'steadySteps':len(selected),'steadyMaxRankSum':max(totals['stepWall']),'steadySumStepMax':sum(max(float(data[t][r]['stepWall']) for r in range(p)) for t in selected),
       'steadyStepMedianMax':statistics.median([row['stepWall_max'] for row in rows if row['timeIndex'] in selected]),
       'chemistryFraction':sum(totals['chemistryWall'])/sum(totals['stepWall']),
       'chemistryImbalance':metrics(totals['chemistryWall'])['imbalance'],'stepImbalance':metrics(totals['stepWall'])['imbalance'],
       'phaseTotals':totals,'rows':rows}
def main(campaign='reactive',output='data/processed'):
    global OUT
    OUT=ROOT/output;OUT.mkdir(parents=True,exist_ok=True)
    runs=[];groups=defaultdict(list);ranks=[]
    for mpath in sorted((ROOT/('data/raw/'+campaign)).glob('*/manifest.json')):
        m=json.loads(mpath.read_text());t=timing(mpath.parent,m['ranks'],m['warmupSteps'])
        csvout(OUT/(mpath.parent.name+'_rank_metrics.csv'),t['rows'])
        key=(m['ranks'],m['method'],m['gamma']);groups[key].append((m,t))
        runs.append({'case':m['case'],'ranks':m['ranks'],'method':m['method'],'gamma':m['gamma'],'repeat':m['repeat'],'solverWall':m['solverWall'],'decompositionWall':m['decompositionWall'],
            **{k:v for k,v in t.items() if k not in ['rows','phaseTotals']}})
        for part in m['parts']:ranks.append({'case':m['case'],**part})
    csvout(OUT/'reactive_runs.csv',runs);csvout(OUT/'rank_partitions.csv',ranks)
    summary=[]
    for key,v in sorted(groups.items(),key=lambda kv:str(kv[0])):
        p,method,gamma=key;base=groups[(p,'scotch',None)]
        wall=[m['solverWall'] for m,t in v];bw=[m['solverWall'] for m,t in base]
        body=[t['steadyMaxRankSum'] for m,t in v];bb=[t['steadyMaxRankSum'] for m,t in base]
        ci=bootstrap(bw,wall)
        row={'ranks':p,'method':method,'gamma':gamma,'trials':len(v),'wallMedian':statistics.median(wall),'wallStd':stats(wall)['std'],'wallMin':min(wall),'wallMax':max(wall),'wallCV':stats(wall)['cv'],
            'wallSpeedup':statistics.median(bw)/statistics.median(wall),'wallSpeedupCI_low':ci[0],'wallSpeedupCI_high':ci[1],
            'steadyMaxRankMedian':statistics.median(body),'steadySpeedup':statistics.median(bb)/statistics.median(body),
            'chemistryFraction':statistics.median(t['chemistryFraction'] for m,t in v),
            'chemistryImbalance':statistics.median(t['chemistryImbalance'] for m,t in v),'stepImbalance':statistics.median(t['stepImbalance'] for m,t in v),
            'decompositionMedian':statistics.median(m['decompositionWall'] for m,t in v),
            'processorFaces':sum(part['processorFaces'] for part in v[0][0]['parts'])//2,
            'maxNeighbours':max(part['nNeighbours'] for part in v[0][0]['parts']),
            'predictedCostImbalance':metrics([part['predictedCost'] for part in v[0][0]['parts']])['imbalance']}
        # First reconstructed replicate; norm-scale gate change is disclosed in the report.
        if p>1:
            ref=ROOT/base[0][0]['case']
            # locate repeat 0 reference/test rather than sorted manifest order
            ref=ROOT/next(m['case'] for m,t in base if m['repeat']==0)
            test=ROOT/next(m['case'] for m,t in v if m['repeat']==0)
            end=str(v[0][0]['start']+v[0][0]['steps'])
            comp=compare(ref/end,test/end,4000,atol=1e-5,rtol=1e-4)
            row['partitionValidationPass']=comp['pass']
            (OUT/f'partition_validation_p{p}_{method}_g{gamma}.json').write_text(json.dumps(comp,indent=2)+'\n')
        else:row['partitionValidationPass']=True
        summary.append(row)
    csvout(OUT/'reactive_summary.csv',summary)
    if (1,'scotch',None) in groups:
        serial=statistics.median(m['solverWall'] for m,t in groups[(1,'scotch',None)])
        scale=[{'ranks':r['ranks'],'method':r['method'],'gamma':r['gamma'],'speedup':serial/r['wallMedian'],'efficiency':serial/r['wallMedian']/r['ranks']} for r in summary]
        csvout(OUT/'scaling.csv',scale)
    over=defaultdict(list)
    for p in (ROOT/'data/raw/overhead').glob('*/manifest.json'):
        m=json.loads(p.read_text());over[m['variant']].append(m['solverWall'])
    if over:
        om=[{'variant':k,'trials':len(v),**stats(v),'overheadVsStock':statistics.median(v)/statistics.median(over['stock'])-1} for k,v in sorted(over.items())]
        csvout(OUT/'instrumentation_overhead.csv',om)
    # Cell-cost predictor accuracy, separated from cost magnitude.
    trace=defaultdict(dict)
    with (ROOT/'data/raw/training/postProcessing/performance/cellCost.csv').open() as f:
        for r in csv.DictReader(f):trace[int(r['timeIndex'])][int(r['cell'])]=(float(r['wall']),float(r['substeps']))
    pred=[]
    for lag in [1,5,10,20]:
        for t in range(11,81-lag):
            a=[trace[t][i][0] for i in range(4000)];b=[trace[t+lag][i][0] for i in range(4000)]
            sa=[trace[t][i][1] for i in range(4000)];sb=[trace[t+lag][i][1] for i in range(4000)]
            pred.append({'timeIndex':t,'lag':lag,'wallCorrelation':correlation(a,b),'substepsCorrelation':correlation(sa,sb),'costVsSubsteps':correlation(a,sa)})
    csvout(OUT/'predictor.csv',pred)
    smooth=[]
    for alpha in [0,.1,.25,.5,1]:
        previous=[trace[10][i][0] for i in range(4000)];corrs=[];errors=[]
        for t in range(11,80):
            obs=[trace[t][i][0] for i in range(4000)];future=[trace[t+1][i][0] for i in range(4000)]
            previous=[alpha*c+(1-alpha)*b for c,b in zip(obs,previous)]
            corrs.append(correlation(previous,future));errors.append(statistics.fmean(abs(x-y) for x,y in zip(previous,future))/statistics.fmean(future))
        smooth.append({'alpha':alpha,'medianCorrelation':statistics.median(x for x in corrs if x is not None),'meanRelativeMAE':statistics.fmean(errors)})
    csvout(OUT/'smoothing.csv',smooth)
    # Summaries include all negative results and validity flags.
    if summary:
        best=max((r for r in summary if r['gamma'] not in [None,0]),key=lambda r:r['wallSpeedup'])
        worst=min((r for r in summary if r['gamma'] not in [None,0]),key=lambda r:r['wallSpeedup'])
        (OUT/'key_results.json').write_text(json.dumps({'status':'MEASURED','best':best,'worst':worst,
            'note':'Exploratory selection across gamma; bootstrap intervals are pointwise, not corrected for selection. Five trials, WSL, reduced mechanism.'},indent=2)+'\n')
        print(json.dumps({'best':best,'worst':worst},indent=2))
if __name__=='__main__':
    a=argparse.ArgumentParser();a.add_argument('--campaign',default='reactive');a.add_argument('--output-dir',default='data/processed');o=a.parse_args();main(o.campaign,o.output_dir)
