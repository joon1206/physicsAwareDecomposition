"""Executed benchmark matrix; self differences are never called exact errors."""
from pathlib import Path
import csv,json,math,re,statistics
from analyze import compare,fields
ROOT=Path(__file__).resolve().parents[1];STUDY=ROOT/'candidateStudy'
records=json.loads((STUDY/'data/processed/screen_summary.json').read_text());lookup={r['name']:r for r in records}
reference=STUDY/'data/raw/F_blockConservative_dt1.25e-07_s1_g0_o1_p1'
mpi=json.loads((STUDY/'data/processed/mpi_counts.json').read_text());mpiLookup={r['name']:r['sumRankCounters'] for r in mpi}
rows=[];failedComparators=[]
for mode,dt,pc,outer,label in [('none',1e-6,1,1,'Base'),('conservativeState',1e-6,1,1,'ConservativeState'),('blockConservative',1e-6,1,1,'Block'),('none',1e-6,2,1,'MorePressure'),('none',.5e-6,1,1,'Base dt/2'),('none',.25e-6,1,1,'Base dt/4'),('none',.25e-6,1,2,'MoreOuter at dt/4'),('none',1e-6,1,2,'MoreOuter same dt')]:
    stem=f'F_{mode}_dt{dt:g}_s1_g0_o{outer}_p{pc}'
    if not all(stem+f'_timing{i}' in lookup for i in [1,2,3]):
        failure=STUDY/'data/raw'/f'{stem}_timing1/failure.json'
        if failure.exists():failedComparators.append(dict(label=label,configuration=json.loads(failure.read_text())))
        else:failedComparators.append(dict(label=label,status='Three matching completed trials unavailable'))
        continue
    trials=[lookup[stem+f'_timing{i}'] for i in [1,2,3]];case=STUDY/'data/raw'/trials[0]['name'];r=trials[0]
    differences=compare(reference,case)
    Tref=fields(reference,4,240e-6,'T',256);T=fields(case,4,240e-6,'T',256)
    counts={}
    for name,iterations in re.findall(r'Solving for (\w+),[^\n]*No Iterations (\d+)',(case/'solver.log').read_text()):
        item=counts.setdefault(name,dict(solves=0,iterations=0));item['solves']+=1;item['iterations']+=int(iterations)
    item=dict(label=label,name=stem,dt=dt,pc=pc,outer=outer,energyDrift=r['signedEnergyDrift'],massDrift=r['massDrift'],
        maxElementDrift=max(abs(x) for x in r['elementDrift'].values()),T_L1=differences['T']['L1'],T_L2=differences['T']['L2'],T_Linf=differences['T']['Linf'],
        TmaxDifference=abs(max(T)-max(Tref)),H2O_L1=differences['H2O']['L1'],H2O_Linf=differences['H2O']['Linf'],
        wallMedian=statistics.median(t['solverWall'] for t in trials),wallMin=min(t['solverWall'] for t in trials),wallMax=max(t['solverWall'] for t in trials),
        trials=[dict(name=t['name'],wall=t['solverWall']) for t in trials],linearSolvers=counts,
        momentumMismatch=r['maxMomentumDeltaU'],fieldDifferences=differences)
    if stem+'_mpi' in mpiLookup:item['MPI']=mpiLookup[stem+'_mpi']
    rows.append(item)
base=rows[0]
for row in rows:
    row['medianWallRatio']=row['wallMedian']/base['wallMedian']
    ratios=[r['wall']/b['wall'] for r,b in zip(row['trials'],base['trials'])]
    row['timingDesign']='Three appended sequential trials, not paired in rotated blocks' if row['label']=='MoreOuter same dt' else 'Three sequential rotated-order trials'
    row['unpairedTrialIndexRatios' if row['label']=='MoreOuter same dt' else 'pairedWallRatios']=ratios
out=dict(reference=reference.name,referenceStatus='Block self-refinement reference, not independent exact solution',records=rows,failedComparators=failedComparators,
    timingScope='Original seven configurations: three sequential rotated-order four-rank trials. Same-dt MoreOuter: three appended sequential trials, not paired with the earlier baseline. Every=0 equal ledger settings; no concurrent CFD campaign during these timing trials. Ordinary host/background and brief analysis may affect noise. Small n gives no strong significance claim.',
    MPIScope='Operation counts from separately instrumented matching runs; their contended wall/latency measurements excluded from runtime comparison.',
    comparatorCaution='MoreOuter at dt/4 is not a same-dt substitute; coarse outer failure is retained. Reacting self-reference has not established spatial convergence.')
(STUDY/'data/processed/benchmark_matrix.json').write_text(json.dumps(out,indent=2)+'\n')
flat=[]
for r in rows:
    f={k:r[k] for k in ['label','dt','pc','outer','energyDrift','massDrift','maxElementDrift','T_L1','T_L2','T_Linf','TmaxDifference','H2O_L1','H2O_Linf','wallMedian','wallMin','wallMax','medianWallRatio','momentumMismatch']}
    f.update(energySolves=sum(v['solves'] for k,v in r['linearSolvers'].items() if k in ['h','deltaHs','deltaH','deltaConservativeH']),pressureSolves=r['linearSolvers'].get('p',{}).get('solves',0),MPICollectives=r.get('MPI',{}).get('collectives'),MPISends=r.get('MPI',{}).get('sends'))
    flat.append(f)
with (STUDY/'data/processed/benchmark_matrix.csv').open('w',newline='') as stream:
    writer=csv.DictWriter(stream,fieldnames=flat[0]);writer.writeheader();writer.writerows(flat)
for r in rows:print(r['label'],'median',r['wallMedian'],'ratio',r['medianWallRatio'],'E',r['energyDrift'],'T self L1',r['T_L1'])
