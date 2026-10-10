#!/usr/bin/env python3
"""Publication figures, each with retained source JSON. Matplotlib Agg."""
import csv,hashlib,json,os,sys
from pathlib import Path
ROOT=Path(os.environ.get('PAD_OUTPUT_ROOT',Path(__file__).resolve().parents[1]))
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'build/pydeps'))
os.environ.setdefault('MPLCONFIGDIR',str(ROOT/'build/mplconfig'))
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
from foamio import read_field,proc_metrics
from models import weights,metrics,correlation
plt.rcParams.update({'font.size':10,'axes.spines.top':False,'axes.spines.right':False,'figure.dpi':120,'savefig.dpi':220,'font.family':'DejaVu Sans'})
FIG=ROOT/'figures';FIG.mkdir(exist_ok=True,parents=True);CAP=[]
def read(name):
    p=ROOT/'data/processed'/name
    rows=list(csv.DictReader(p.open()))
    for r in rows:
        for k,v in r.items():
            try:r[k]=float(v)
            except (ValueError,TypeError):pass
    return rows
def save(name,rows,caption):
    plt.gcf().tight_layout()
    for ext in ['png','pdf','svg']:plt.savefig(FIG/(name+'.'+ext),bbox_inches='tight')
    (FIG/(name+'.source.json')).write_text(json.dumps({'status':'MEASURED or DERIVED as caption specifies','caption':caption,'data':rows},indent=2))
    CAP.append('## '+name+'\n\n'+caption+'\n');plt.close()
def axis(ax,x,y):ax.set_xlabel(x);ax.set_ylabel(y);ax.grid(alpha=.18)
summary=read('tight/reactive_summary.csv');no=read('noChem/reactive_summary.csv')
sc=[r for r in summary if r['method']=='scotch']
main=[r for r in sc if r['ranks']==4]
sel=lambda g:next(r for r in main if (r['gamma']==g or (g is None and r['gamma']=='')))
for fname,col,y in [('03_chemistry_imbalance','chemistryImbalance','Chemistry max / mean rank time'),('04_step_imbalance','stepImbalance','Step max / mean rank time')]:
    fig,ax=plt.subplots(figsize=(6,3.4))
    for g,label in [('', 'Scotch'),(1.,'Weighted gamma=1')]:
        rows=sorted([r for r in sc if r['gamma']==g or (r['ranks']==1 and r['gamma']=='')],key=lambda r:r['ranks'])
        ax.plot([r['ranks'] for r in rows],[r[col] for r in rows],'o-',label=label)
    axis(ax,'MPI ranks',y);ax.set_ylim(0,1.1) if col=='stepImbalance' else ax.set_ylim(bottom=0);ax.legend()
    save(fname,summary,'Measured strict-tolerance LTS run medians. Step wall includes MPI waiting; near-unity step imbalance does not establish balanced compute.')
scale=read('tight/scaling.csv')
for name,col,y in [('05_strong_scaling','speedup','Whole-run strong-scaling speedup'),('06_parallel_efficiency','efficiency','Whole-run parallel efficiency')]:
    fig,ax=plt.subplots(figsize=(6,3.4))
    for g,label in [('', 'Scotch'),(1.,'Weighted gamma=1')]:
        rows=sorted([r for r in scale if r['method']=='scotch' and (r['gamma']==g or r['ranks']==1)],key=lambda r:r['ranks'])
        ax.plot([r['ranks'] for r in rows],[r[col] for r in rows],'o-',label=label)
    ax.plot([1,4],[1,4] if col=='speedup' else [1,1],'k--',alpha=.4,label='Ideal')
    axis(ax,'MPI ranks',y);ax.set_ylim(bottom=0);ax.legend();save(name,scale,'Measured 1/2/4-core WSL strong scaling, including MPI launch and final output. No extrapolation beyond tested ranks.')
parts=read('tight/rank_partitions.csv')
for fname,col,y in [('07_workload_by_rank','predictedCost','Predicted chemistry cost (s per iteration)'),('08_cells_by_rank','nCells','Cells per rank'),('09_faces_by_rank','processorFaces','Processor faces per rank')]:
    fig,ax=plt.subplots(figsize=(6,3.5))
    for j,(suffix,label) in enumerate([('p4_scotch_gNone_r0','Scotch'),('p4_scotch_g1_r0','Weighted gamma=1')]):
        rows=sorted([r for r in parts if r['case'].endswith(suffix)],key=lambda r:r['rank'])
        ax.bar(np.array([r['rank'] for r in rows])+j*.36-.18,[r[col] for r in rows],width=.36,label=label)
    axis(ax,'MPI rank',y);ax.set_xticks(range(4));ax.legend();save(fname,parts,'Native partition metrics; predicted cost is summed from the independent serial training trace, not measured parallel chemistry time.')
synth=read('synthetic.csv')
fig,axes=plt.subplots(1,2,figsize=(9,3.4))
for ax,mesh in zip(axes,['32x16','64x32']):
    rows=[r for r in synth if r['mesh']==mesh and r['ranks']==4 and r['kind']=='gaussian' and r['width']==.15 and r['centreX']==.25 and r['method']=='scotch']
    for w,label in [(0,'Scotch'),(1,'Weighted')]:
        q=sorted([r for r in rows if r['weighted']==w],key=lambda r:r['amplitude'])
        ax.plot([r['amplitude'] for r in q],[r['imbalance'] for r in q],'o-',label=label)
    axis(ax,'Gaussian amplitude A','Predicted max / mean workload');ax.set_ylim(bottom=0);ax.set_title(mesh);ax.legend()
save('10_synthetic_amplitude',synth,'Derived workload imbalance from measured native assignments, using actual cell centres. These are predicted work sums, not CFD runtime.')
for fname,col,y in [('11_gamma_speedup','wallSpeedup','Whole-run speedup over Scotch'),('12_gamma_faces','processorFaces','Unique processor interface faces'),('13_gamma_neighbours','maxNeighbours','Maximum rank neighbours'),('19_decomposition_overhead','decompositionMedian','Decomposition process wall (s)')]:
    fig,ax=plt.subplots(figsize=(6,3.4))
    for p in [2,4]:
        rows=sorted([r for r in sc if r['ranks']==p and r['gamma']!=''],key=lambda r:r['gamma'])
        x=[r['gamma'] for r in rows];yvals=[r[col] for r in rows]
        if col=='wallSpeedup':ax.errorbar(x,yvals,yerr=[[r[col]-r['wallSpeedupCI_low'] for r in rows],[r['wallSpeedupCI_high']-r[col] for r in rows]],fmt='o-',capsize=3,label=f'{p} ranks')
        else:ax.plot(x,yvals,'o-',label=f'{p} ranks')
    ax.set_xscale('symlog',linthresh=.25);axis(ax,'Chemistry weight gamma',y);ax.set_ylim(bottom=0);ax.legend()
    if col=='wallSpeedup':ax.axhline(1,color='k',ls='--',alpha=.4)
    save(fname,summary,'Measured strict LTS medians. Speedup error bars are pointwise 95% bootstrap intervals from five whole-run trials; exploratory gamma selection is not corrected.')
fig,ax=plt.subplots(figsize=(6,3.4))
for p in [2,4]:
    rows=[r for r in sc if r['ranks']==p and r['gamma']!=''];ax.scatter([r['chemistryFraction'] for r in rows],[r['wallSpeedup'] for r in rows],label=f'{p} ranks')
axis(ax,'Measured chemistry fraction (includes wrapper overhead)','Whole-run speedup');ax.axhline(1,c='k',ls='--',alpha=.4);ax.legend()
save('14_chemistry_fraction',summary,'Measured samples only. Chemistry fraction depends on partition and MPI waits in other phases; it is not an independently controlled explanatory variable.')
fig,ax=plt.subplots(figsize=(6,3.4))
for p in [2,4]:
    rows=[r for r in sc if r['ranks']==p];ax.scatter([r['predictedCostImbalance'] for r in rows],[r['chemistryImbalance'] for r in rows],label=f'{p} ranks')
axis(ax,'Predicted chemistry cost max / mean','Measured chemistry time max / mean');ax.plot([1,3.5],[1,3.5],'k--',alpha=.4);ax.legend()
save('15_prediction_vs_timing',summary,'Predicted serial-clock workload versus measured parallel chemistry phase imbalance. Neither is total timestep makespan.')
fig,ax=plt.subplots(figsize=(6,3.4));rows=[sel(None),sel(1.)];ax.bar(['Scotch','Weighted gamma=1'],[r['wallMedian'] for r in rows],yerr=[r['wallStd'] for r in rows],capsize=4,color=['#526d82','#b65330']);axis(ax,'4 MPI ranks','Whole solver process wall (s)')
save('16_reactive_runtime',rows,'Five strict-tolerance trials; bars are medians and whiskers are sample standard deviations. Includes launch/output, excludes training/decomposition.')
pred=read('tight/predictor.csv');smooth=read('tight/smoothing.csv')
fig,ax=plt.subplots(figsize=(6,3.4));lags=sorted(set(r['lag'] for r in pred))
data=[[r['wallCorrelation'] for r in pred if r['lag']==lag and isinstance(r['wallCorrelation'],float)] for lag in lags]
ax.boxplot(data,tick_labels=[str(int(x)) for x in lags]);axis(ax,'Lag (LTS iterations)','Spatial cell-clock correlation');ax.set_ylim(-1,1)
save('17_cost_persistence',pred,'Measured per-cell wall-clock correlations from serial training. Temporal persistence is in LTS iteration space, not physical time.')
over=read('tight/instrumentation_overhead.csv');fig,ax=plt.subplots(figsize=(7,3.4))
ax.bar([r['variant'] for r in over],[100*r['overheadVsStock'] for r in over],color='#526d82');ax.axhline(0,c='k',lw=.7);axis(ax,'Instrumentation configuration','Median whole-run overhead vs stock (%)')
save('18_instrumentation_overhead',over,'Seven randomized repetitions, 80 LTS iterations. Small differences overlap run variability; full per-cell tracing is materially more costly. Disabled negative estimates are noise, not an optimization claim.')
fig,ax=plt.subplots(figsize=(6,3.5))
rows=[r for r in main if r['gamma']!='']+no
a=ax.scatter([r['chemistryFraction'] for r in rows],[r['predictedCostImbalance'] for r in rows],c=[r['wallSpeedup'] for r in rows],cmap='coolwarm',vmin=.65,vmax=1.2,s=80)
axis(ax,'Measured chemistry phase fraction','Predicted chemistry imbalance');fig.colorbar(a,ax=ax,label='Whole-run speedup over Scotch')
save('20_measured_regimes',rows,'Measured regime samples, including stale weights after chemistry is disabled. Sparse samples do not establish a universal crossover surface.')
for fname,phase,y in [('01_rank_chemistry','chemistryWall','Rank chemistry wall (ms)'),('02_timestep_makespan','stepWall','Max rank step wall (ms)')]:
    fig,axes=plt.subplots(1,2,figsize=(10,3.5),sharey=True)
    source=[]
    for ax,g,label in zip(axes,['None','1'],['Scotch','Weighted gamma=1']):
        c=ROOT/f'data/raw/reactiveTight/p4_scotch_g{g}_r0';mat=[]
        for rank in range(4):
            q=list(csv.DictReader((c/f'processor{rank}/postProcessing/performance/rank{rank:04d}.csv').open()));source+=q;mat.append(q)
            if phase=='chemistryWall':ax.plot([int(r['timeIndex']) for r in q],[1000*float(r[phase]) for r in q],label=f'Rank {rank}',lw=1)
        if phase=='stepWall':
            ax.plot([int(r['timeIndex']) for r in mat[0]],[1000*max(float(mat[r][i][phase]) for r in range(4)) for i in range(len(mat[0]))],lw=1)
        axis(ax,'LTS iteration',y);ax.set_ylim(bottom=0);ax.set_title(label)
        if phase=='chemistryWall':ax.legend(fontsize=8)
    save(fname,source,'Measured local wall durations from strict repeat 0. Step includes waits and final output; the maximum is an offline per-iteration proxy, not an added barrier.')
# Native spatial fields and ownership in identical coordinates.
base=ROOT/'data/raw/reactiveTight/p4_scotch_gNone_r0';weighted=ROOT/'data/raw/reactiveTight/p4_scotch_g1_r0'
owners=[]
for c in [base,weighted]:
    own=np.zeros(4000)
    for part in proc_metrics(c):own[part['ids']]=part['rank']
    owners.append(own.reshape(40,100))
cost=np.array(read_field(ROOT/'data/raw/training/80/chemCost',4000)).reshape(40,100)*1e6
T=np.array(read_field(weighted/'160/T',4000)).reshape(40,100)
fig,axes=plt.subplots(2,2,figsize=(10,6.5))
for ax,array,title,cmap,vmin,vmax in zip(axes.flat,[cost,owners[0],owners[1],T],['Chemistry cost (microseconds/cell)','Scotch ownership','Weighted ownership','Temperature (K)'],['magma',matplotlib.colors.ListedColormap(plt.get_cmap('tab10').colors[:4]),matplotlib.colors.ListedColormap(plt.get_cmap('tab10').colors[:4]),'inferno'],[0,-.5,-.5,293],[cost.max(),3.5,3.5,T.max()]):
    im=ax.imshow(array,origin='lower',extent=[0,20,-10,10],aspect='equal',cmap=cmap,vmin=vmin,vmax=vmax)
    ax.set_title(title);axis(ax,'x (mm)','y (mm)');fig.colorbar(im,ax=ax,shrink=.75,ticks=[0,1,2,3] if 'ownership' in title else None)
save('21_spatial_relationship',{'costMicroseconds':cost.tolist(),'baselineOwners':owners[0].tolist(),'weightedOwners':owners[1].tolist(),'T':T.tolist()},'Native training cost and reconstructed strict-solver temperature; processor maps come from cellProcAddressing. Identical camera and ownership color range.')
fig,axes=plt.subplots(1,2,figsize=(10,3.7));spatial={}
for ax,f,label in zip(axes,['Qdot','CH4'],['Heat release (W/m3)','Methane mass fraction']):
    arr=np.array(read_field(weighted/'160'/f,4000)).reshape(40,100);spatial[f]=arr.tolist()
    im=ax.imshow(arr,origin='lower',extent=[0,20,-10,10],cmap='magma',aspect='equal',vmin=0,vmax=arr.max());axis(ax,'x (mm)','y (mm)');fig.colorbar(im,ax=ax,label=label,shrink=.75)
save('22_heat_release_species',spatial,'Native strict-run reconstructed fields. These images establish localized reaction structure; they are not experimental validation of this one-step chemistry mechanism.')
fig,ax=plt.subplots(figsize=(6,3.4));q=sorted(no,key=lambda r:0 if r['gamma']=='' else r['gamma'])
ax.bar(['Scotch' if r['gamma']=='' else f"gamma={int(r['gamma'])}" for r in q],[r['wallMedian'] for r in q],yerr=[r['wallStd'] for r in q],capsize=4,color='#b65330');axis(ax,'Chemistry disabled; stale reactive weights','Whole solver wall (s)')
save('23_negative_control',q,'Five strict-tolerance trials. Static weights predict a chemistry workload that is absent, producing a clear transport imbalance regression.')
fig,ax=plt.subplots(figsize=(6,3.4));vals=[];source=[]
for folder in ['','tight/']:
    p=ROOT/('data/processed/'+folder+'partition_validation_p4_scotch_g1.json');d=json.loads(p.read_text());vals.append(d['fields']['T']['Linf']);source.append(d)
ax.bar(['Tutorial tolerances','Strict tolerances'],vals,color=['#b65330','#526d82']);ax.set_yscale('log');axis(ax,'Same iteration count, different partitions','Temperature difference Linf (K)')
save('24_numerical_failure_repair',source,'Log axis explicitly used to display orders of magnitude. Original loose LTS performance result fails the numerical gate and is excluded from accepted speedup conclusions.')
fig,ax=plt.subplots(figsize=(6,3.4));ax.plot([r['alpha'] for r in smooth],[r['medianCorrelation'] for r in smooth],'o-');axis(ax,'Exponential smoothing alpha','Median next-iteration spatial correlation');ax.set_ylim(-1,1)
save('25_smoothing_sensitivity',smooth,'Derived smoothing sensitivity from the same measured serial trace; it is predictor accuracy, not a measured solver-runtime optimization.')
# Counter-vs-clock quality.
fig,ax=plt.subplots(figsize=(6,3.4));q=[r for r in pred if r['lag']==1 and isinstance(r['costVsSubsteps'],float)]
ax.plot([r['timeIndex'] for r in q],[r['costVsSubsteps'] for r in q]);axis(ax,'Training LTS iteration','Correlation: cell clocks vs substep counts');ax.set_ylim(-1,1)
save('26_substeps_proxy',q,'Measured relationship between chemistry-loop substeps and elapsed cell cost. It is not an ODE RHS/Jacobian evaluation count.')
# Phase profile from native exclusive timers.
fig,ax=plt.subplots(figsize=(7,3.5));phases=['chemistryWall','speciesWall','energyWall','pressureWall','momentumWall','ioWall'];profile=[]
for j,(g,label) in enumerate([('None','Scotch'),('1','Weighted')]):
    c=ROOT/f'data/raw/reactiveTight/p4_scotch_g{g}_r0';totals={p:0. for p in phases}
    for rank in range(4):
        q=list(csv.DictReader((c/f'processor{rank}/postProcessing/performance/rank{rank:04d}.csv').open()))[10:-1]
        for phase in phases:totals[phase]+=sum(float(r[phase]) for r in q)
    profile.append({'method':label,**totals})
    ax.bar(np.arange(len(phases))+j*.35-.175,[totals[p] for p in phases],width=.35,label=label)
ax.set_xticks(range(len(phases)),[p.replace('Wall','') for p in phases]);axis(ax,'Exclusive phase (includes MPI waits)','Sum over ranks and steady steps (s)');ax.legend()
save('27_phase_profile',profile,'Lightweight measured phase profile. Pressure/species/energy times include solver communication and idle time; no MPI-only attribution is made.')
# Optional controlled synthetic timings.
p=ROOT/'data/processed/synthetic_runtime_summary.csv'
if p.exists():
    sr=read('synthetic_runtime_summary.csv');fig,ax=plt.subplots(figsize=(7,3.5))
    for h in [1,32]:
        q=[r for r in sr if r['nx']==64 and r['ranks']==4 and r['weighted']==1 and r['haloPasses']==h]
        ax.plot([r['kind'] for r in q],[r['stepSpeedup'] for r in q],'o-',label=f'{h} halo exchanges/step')
    axis(ax,'Synthetic cost distribution','Measured synchronous step speedup');ax.axhline(1,c='k',ls='--',alpha=.4);ax.legend()
    save('28_synthetic_compute_communication',sr,'Measured trigonometric CPU work with verified coupled processor halos and intentional step barriers. This controlled workload is separate from reactive CFD.')
# Additional communication-pressure and motion sensitivities.
sr=read('synthetic_runtime_summary.csv')
fig,ax=plt.subplots(figsize=(6.5,3.5))
q=sorted([r for r in sr if r['nx']==64 and r['ranks']==4 and r['kind']=='gaussian' and r['weighted']==1],key=lambda r:r['haloPasses'])
ax.errorbar([r['haloPasses'] for r in q],[r['stepSpeedup'] for r in q],yerr=[[r['stepSpeedup']-r['stepCI_low'] for r in q],[r['stepCI_high']-r['stepSpeedup'] for r in q]],fmt='o-',capsize=4)
ax.set_xscale('log');ax.axhline(1,c='k',ls='--',alpha=.4);axis(ax,'Halo exchanges per step (log scale)','Synthetic step speedup, weighted / Scotch')
save('29_communication_pressure',q,'Measured 64x32 four-rank Gaussian CPU/halo workload, five trials per sample. Benefit diminishes at high communication pressure; the high-halo interval includes unity. Low/high campaigns were separate, so this is not a causal universal crossover threshold.')
motion=read('moving_hotspot.csv')
fig,axes=plt.subplots(1,2,figsize=(9,3.5))
for w,label in [(0,'Scotch'),(1,'Weighted initial hotspot')]:
    q=[r for r in motion if r['weighted']==w and r['speedLPerIteration']==.02]
    axes[0].plot([r['iteration'] for r in q],[r['imbalance'] for r in q],'o-',ms=3,label=label)
q=[r for r in motion if r['weighted']==1 and r['speedLPerIteration']==.02]
axes[1].plot([r['iteration'] for r in q],[r['initialCorrelation'] for r in q],'o-',ms=3)
axis(axes[0],'Analytic hotspot translation iteration','Predicted workload max / mean');axes[0].set_ylim(bottom=0);axes[0].legend(fontsize=8)
axis(axes[1],'Analytic hotspot translation iteration','Spatial correlation with initial workload');axes[1].set_ylim(-1,1)
save('30_moving_hotspot',motion,'Derived work sums on measured native 64x32 four-rank static partitions. Hotspot translation is analytic, not moving chemistry or a dynamic migration experiment.')

(FIG/'captions.md').write_text('# Figure captions and evidence\n\n'+'\n'.join(CAP))
print('Generated',len(CAP),'figures in PNG/PDF/SVG with source data')
