"""Regenerate scientific figures only from the current processed epoch.

Each figure has a machine-readable source slice, caption, PNG, SVG and PDF.
Run after timed experiments; plotting competes for CPU resources.
"""
import collections,json,math,os,statistics,shutil
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap,TwoSlopeNorm
from analysis import ROOT,ACTIONS,TEST,predict,design,summary,interval

OUT=ROOT/'figures';OUT.mkdir(parents=True,exist_ok=True)
plt.rcParams.update({'font.size':9,'axes.spines.top':False,'axes.spines.right':False,
    'figure.dpi':150,'savefig.dpi':220,'pdf.fonttype':42,'svg.fonttype':'none',
    'svg.hashsalt':'pad-state-preserving-action-study-v3'})
COLORS={'A0':'#667085','AC':'#147d92','AM':'#dc862c','AH':'#9061bd'}
INDEX=[]
def data(name):return json.loads((ROOT/f'data/processed/{name}.json').read_text())
def save(number,name,fig,source,caption):
    stem=f'{number:02d}_{name}';fig.tight_layout()
    for ext in ['png','pdf','svg']:
        metadata={'CreationDate':None,'ModDate':None} if ext=='pdf' else {'Date':None} if ext=='svg' else None
        fig.savefig(OUT/(stem+'.'+ext),bbox_inches='tight',metadata=metadata)
    plt.close(fig)
    (OUT/(stem+'.source.json')).write_text(json.dumps(source,indent=2))
    INDEX.append(dict(number=number,name=stem,caption=caption,source=stem+'.source.json'))
def chart(figsize=(7,4)):return plt.subplots(figsize=figsize)
def spatial(ax,record,field,title,vmin=None,vmax=None,cmap='inferno'):
    info=record['info'];values=record['owner'] if field=='owner' else record['fields'][field]
    image=np.asarray(values).reshape(info['ny'],info['nx'])
    im=ax.imshow(image,origin='lower',extent=[0,20,0,8],aspect='equal',cmap=cmap,vmin=vmin,vmax=vmax)
    ax.set(xlabel='x (mm)',ylabel='y (mm)',title=title);return im
def rank_sums(raw,regime='persistent',action='A0'):
    return next(r for r in raw if r['regime']==regime and r['action']==action and r['checkpoint']=='4e-05' and r['horizonSteps']==80 and r['repeat']==0)['phaseRankSums']

def main():
    states=data('oracle_summary');raw=data('oracle_raw');sp=data('spatial');hist=data('histories')
    policies=data('policy_decisions');ps=data('policy_summary');model=data('model')
    base=sp['persistent_4e-05'];mesh=data('mesh_example');modified=dict(base,owner=mesh['owner'])
    for number,field,title,record,cmap in [(1,'T','Reactive kernel at 40 μs',base,'inferno'),
        (2,'chemCost','Measured chemistry cost at 40 μs',base,'viridis'),
        (3,'owner','Initial Scotch ownership',base,ListedColormap(list(COLORS.values()))),
        (4,'owner','Cost-weighted Scotch ownership',modified,ListedColormap(list(COLORS.values())))]:
        fig,ax=chart((7,3));im=spatial(ax,record,field,title,cmap=cmap);fig.colorbar(im,ax=ax,label={'T':'Temperature (K)','chemCost':'Cell integration wall (s)','owner':'MPI rank'}[field],ticks=range(4) if field=='owner' else None)
        save(number,field+('_weighted' if number==4 else '_initial'),fig,record,
            title+'. Same 32×8 grid and camera; ownership is assembled using migrated canonical cell IDs. Cell clocks are measured wall times, not reaction rates.')
    fig,axes=plt.subplots(1,2,figsize=(9,3))
    for ax,record,title in zip(axes,[base,modified],['Initial interfaces','Weighted interfaces']):
        spatial(ax,record,'T',title,vmin=min(base['fields']['T']),vmax=max(base['fields']['T']))
        owners=np.asarray(record['owner']).reshape(8,32)
        for y in range(8):
            for x in range(32):
                if x<31 and owners[y,x]!=owners[y,x+1]:ax.plot([(x+1)*20/32]*2,[y,(y+1)],color='cyan',lw=1)
                if y<7 and owners[y,x]!=owners[y+1,x]:ax.plot([x*20/32,(x+1)*20/32],[y+1]*2,color='cyan',lw=1)
    save(5,'processor_interfaces',fig,[base,modified],'Cyan lines mark internal ownership changes. Cyclic boundary interfaces also count in quantitative face totals but lie at box boundaries.')
    moving=[sp['heldoutMoving_'+t] for t in ['4e-05','0.00012','0.0002']]
    fig,axes=plt.subplots(1,3,figsize=(11,3))
    limits=[min(min(r['fields']['T']) for r in moving),max(max(r['fields']['T']) for r in moving)]
    for ax,record in zip(axes,moving):
        im=spatial(ax,record,'T',f"t = {record['time']*1e6:.0f} μs",*limits)
        fig.colorbar(im,ax=ax,label='Temperature (K)',shrink=.65)
    save(6,'moving_sequence',fig,moving,'Moving-condition temperature sequence with an identical camera and shared data-range color scale. These coarse controlled kernels are not validated flame fronts.')
    fig,ax=chart();cost=np.asarray(base['fields']['chemCost']);x=np.arange(4)
    for owner,label,offset in [(base['owner'],'Initial',-.18),(modified['owner'],'Weighted',.18)]:
        ax.bar(x+offset,[cost[np.asarray(owner)==i].sum() for i in x],.36,label=label)
    ax.set(xlabel='MPI rank',ylabel='Current cell-cost sum (s)',title='Redistribution of the measured checkpoint workload',xticks=x);ax.legend()
    save(7,'workload_by_rank',fig,[base,modified],'Checkpoint cell-clock sums assigned to old and new owners. This diagnostic does not assume that future cell costs stay fixed.')
    for number,phase,name in [(8,'chemistryWall','chemistry_by_rank'),(9,'stepWall','timestep_by_rank')]:
        fig,ax=chart();source={a:rank_sums(raw,action=a) for a in ACTIONS}
        for j,a in enumerate(ACTIONS):ax.bar(x+(j-1.5)*.19,[source[a][str(i)][phase] for i in x],.19,label=a,color=COLORS[a])
        ax.set(xlabel='MPI rank',ylabel='Integrated duration (s)',title=phase+' over 80 global steps',xticks=x);ax.legend(ncol=4)
        save(number,name,fig,source,'Rank-local integrated phase durations from repeat zero, persistent checkpoint 40 μs. Phases overlap across ranks and their maxima must not be added to infer a critical path.')
    fig,ax=chart((9,8));labels=[f"{s['regime']} / {float(s['checkpoint'])*1e6:g} μs / H{s['H']}" for s in states]
    values=np.array([[s['actions'][a]['total']['median'] for a in ACTIONS] for s in states])
    ratios=values/values[:,[0]]
    norm=TwoSlopeNorm(vcenter=1,vmin=min(float(ratios.min()),1-1e-12),vmax=max(float(ratios.max()),1+1e-12))
    im=ax.imshow(ratios,aspect='auto',cmap='RdYlBu_r',norm=norm)
    ax.set(xticks=range(4),xticklabels=ACTIONS,yticks=range(len(states)),yticklabels=labels,title='All measured actions: total cost relative to A0')
    fig.colorbar(im,ax=ax,label='Median J / median J(A0); lower is faster')
    save(10,'all_action_costs',fig,states,'Complete oracle state set, five randomized trials per action. Total cost includes action configuration, native mesh redistribution and solver process startup plus endpoint I/O.')
    scaling=data('scaling');scale_groups={(p,a):[r['totalWall'] for r in scaling if r['ranks']==p and r['action']==a] for p in [1,2,4,6] for a in ['A0','AC','controller']}
    for number,eff in [(11,False),(12,True)]:
        fig,ax=chart()
        for a in ['A0','AC','controller']:
            med=[statistics.median(scale_groups[p,a]) for p in [1,2,4,6]]
            yy=[med[0]/v/p for v,p in zip(med,[1,2,4,6])] if eff else med
            ax.plot([1,2,4,6],yy,'o-',label=a,color=COLORS.get(a,'#e05361'))
        ax.set(xlabel='Bound physical cores / MPI ranks',ylabel='Parallel efficiency' if eff else 'Continuation process wall (s)',title='Strong scaling: 512 cells, 40 global steps',xticks=[1,2,4,6]);ax.legend()
        save(number,'parallel_efficiency' if eff else 'strong_scaling',fig,scaling,'Five trials per configuration on one six-core WSL2 host. Per-case decomposition is recorded separately. This is a small-domain, single-node experiment, not network scaling.')
    selected=[s for s in states if s['H']==80];fig,ax=chart((8,7));y=np.arange(len(selected))
    for j,a in enumerate(['AC','AM','AH']):
        vals=[s['actions'][a]['speedup'] for s in selected];ci=[s['actions'][a]['speedupCI'] for s in selected]
        position=y+(j-1)*.18
        ax.scatter(vals,position,s=16,label=a,color=COLORS[a])
        ax.hlines(position,[c[0] for c in ci],[c[1] for c in ci],color=COLORS[a],lw=1)
    ax.axvline(1,color='black',lw=.8);ax.set(yticks=y,yticklabels=[s['regime']+' / '+s['checkpoint'] for s in selected],xlabel='A0 / action total wall',title='Global-timestep speedup and exploratory uncertainty');ax.legend()
    save(13,'speedup_intervals',fig,selected,'Pointwise 95% bootstrap intervals for independent median ratios (4000 resamples), five trials each. Multiple state selection is exploratory; intervals are not simultaneous or confirmatory.')
    gamma=data('gamma');fig,ax=chart()
    for regime in ['persistent','translating']:
        gg=sorted(set(r['gamma'] for r in gamma));ax.plot(gg,[statistics.median(r['processorFaces'] for r in gamma if r['regime']==regime and r['gamma']==g) for g in gg],'o-',label=regime)
    ax.set(xlabel='Chemistry weighting strength γ',ylabel='Unique processor faces',title='Partition communication geometry');ax.legend()
    save(14,'faces_vs_weight',fig,gamma,'Native redistributed mesh face counts, including cyclic processor interfaces. Weight clipping is fixed at [0.1,10]; stronger weighting need not change an integer partition monotonically.')
    profiles=data('profiles');fig,ax=chart();source=[]
    for a in ACTIONS:
        group=[r for r in profiles if r['regime']=='persistent' and r['action']==a and r['profile']]
        ranks=[{k:float(v) for k,v in r['MPI'][i].items()} for r in group for i in range(len(r['MPI']))]
        source.append(dict(action=a,ranks=ranks))
    keys=list(source[0]['ranks'][0]);wall_key=next(k for k in keys if 'seconds' in k.lower() or 'wall' in k.lower())
    ax.bar(ACTIONS,[statistics.mean(r[wall_key] for r in s['ranks']) for s in source],color=[COLORS[a] for a in ACTIONS])
    ax.set(ylabel='Mean rank MPI-call duration (s)',title='MPI time includes waiting and synchronization')
    save(15,'mpi_call_time',fig,source,'PMPI calls on the persistent condition. These durations include imbalance-induced waits; they are not pure network transfer times. No extra barriers or collectives are added by the profiler.')
    persistence=data('persistence');fig,ax=chart()
    for regime in ['persistent','translating','heldoutMoving','ignition','uniform','transportDominated']:
        g=[r for r in persistence if r['regime']==regime and r['index']==20];g.sort(key=lambda r:r['lag'])
        ax.plot([r['lag'] for r in g],[r['rho'] for r in g],'o-',ms=3,label=regime)
    ax.set(xlabel='Future lag (physical steps)',ylabel='Cell-cost Pearson correlation',title='Measured forecast persistence at step 20',ylim=(-1.05,1.05));ax.legend(fontsize=7,ncol=2)
    save(16,'persistence_correlation',fig,persistence,'Actual future costs are used only for this diagnostic. Controller inputs use previous and current costs. Timing noise and reaction evolution both affect correlations.')
    predrows=[]
    for s in states:
        for a in ACTIONS[1:]:
            predicted=predict(model['models'][a],design(s['features'],s['H']))
            actual=s['actions'][a]['solver']['median']-s['actions']['A0']['solver']['median']
            predrows.append(dict(regime=s['regime'],split=s['split'],action=a,predicted=predicted,actual=actual))
    fig,ax=chart()
    for split,marker in [('train','o'),('validation','s'),('test','^')]:
        g=[r for r in predrows if r['split']==split];ax.scatter([r['actual'] for r in g],[r['predicted'] for r in g],marker=marker,label=split,alpha=.75)
    bounds=[min(min(r['actual'],r['predicted']) for r in predrows),max(max(r['actual'],r['predicted']) for r in predrows)];ax.plot(bounds,bounds,'k--',lw=.7)
    ax.set(xlabel='Observed solver cost change (s)',ylabel='Ridge predicted cost change (s)',title='Interpretable model prediction');ax.legend()
    save(17,'prediction_accuracy',fig,predrows,'Coefficients fit on five entire training conditions; two whole validation conditions set conservative residual margins; three held-out conditions are untouched by fitting. Setup costs are excluded from this solver-delta plot.')
    decisions=[r for r in policies if r['split']=='test' and r['policy']=='wholeSolver'];matrix=np.zeros((4,4),dtype=int)
    for r in decisions:matrix[ACTIONS.index(r['oracle']),ACTIONS.index(r['chosen'])]+=1
    fig,ax=chart((5,4));im=ax.imshow(matrix,cmap='Blues');ax.set(xticks=range(4),xticklabels=ACTIONS,yticks=range(4),yticklabels=ACTIONS,xlabel='Predicted action',ylabel='Median oracle action',title='Held-out controller action confusion')
    for i in range(4):
        for j in range(4):ax.text(j,i,str(matrix[i,j]),ha='center',va='center')
    save(18,'confusion_matrix',fig,decisions,'Median oracle labels can change within runtime noise. This matrix covers six held-out checkpoint states, not independent flow trajectories.')
    names=['never','periodicChemistry','periodicMesh','persistenceBreakEven','wholeSolver','oracle'];fig,ax=chart((8,4))
    ax.boxplot([[r['regret'] for r in policies if r['split']=='test' and r['policy']==p] for p in names],labels=names,showfliers=True);ax.tick_params(axis='x',rotation=20)
    ax.set(ylabel='Regret relative to median oracle (s)',title='Held-out decision regret, including feature costs')
    save(19,'controller_regret',fig,[r for r in policies if r['split']=='test'],'Retrospective regret includes measured feature extraction for feature-driven policies. This is distinct from independent deployment and live end-to-end timings.')
    live=data('live');fig,ax=chart();live_example=[r for r in live if r['regime']=='heldoutMoving' and r['repeat']==0]
    for row in live_example:
        if row['events']:
            xx=[(e['time']+40*2e-6)*1e6 for e in row['events']];yy=[e['cumulativeWall'] for e in row['events']]
            eligible=row.get('gate',{'pass_':True})['pass_']
            ax.plot(xx,yy,'o-' if eligible else 'o--',label=row['policy'] if eligible else row['policy']+' (field gate failed)')
        else:ax.scatter([280],[row['totalWall']],label=row['policy'],marker='x')
    ax.set(xlabel='Physical end time (μs)',ylabel='Cumulative end-to-end wall (s)',title='Measured live rollout: moving held-out condition');ax.legend(fontsize=8)
    save(20,'cumulative_runtime',fig,live_example,'Repeat-zero measured rollout. All policies reach 280 μs. Dashed AM fails the predefined endpoint field gate and is descriptive timing evidence only. Uninterrupted arms provide an endpoint only; no interpolated cumulative clock is invented. No trial is removed.')
    events=[dict(regime=r['regime'],repeat=r['repeat'],**e) for r in live if r['policy']=='controller' for e in r['events']];fig,ax=chart((8,4))
    for j,regime in enumerate(TEST+['persistent','transportDominated']):
        for e in [e for e in events if e['regime']==regime]:ax.scatter(e['time']*1e6,j+(e['repeat']-1)*.12,c=COLORS[e['action']],marker='s',s=35)
    ax.set(yticks=range(5),yticklabels=TEST+['persistent','transportDominated'],xlabel='Decision checkpoint (μs)',title='Live controller decisions; color denotes A0 / AC / AM / AH')
    save(21,'rebalancing_events',fig,events,'Three actual rollouts per condition; features come only from the completed prefix of that same rollout. The frozen model has a forty-step cooldown.')
    fig,ax=chart();testpred=[r for r in predrows if r['split']=='test']
    for a in ACTIONS[1:]:
        g=[r for r in testpred if r['action']==a];ax.scatter([-r['actual'] for r in g],[-r['predicted'] for r in g],label=a,c=COLORS[a])
    ax.axhline(0,color='black',lw=.6);ax.axvline(0,color='black',lw=.6);ax.set(xlabel='Actual solver savings (s)',ylabel='Predicted solver savings (s)',title='Held-out predicted versus observed benefit');ax.legend()
    save(22,'predicted_benefit',fig,testpred,'Benefits are solver deltas before action setup and residual safety margins. Prediction error is reported even when the controller declines to act.')
    fig,ax=chart();values=[ps['test'][p]['aggregateSpeedup'] for p in names]
    ax.bar(names,values,color=['#667085','#147d92','#dc862c','#9061bd','#e05361','#1d2939']);ax.axhline(1,c='black',lw=.7);ax.tick_params(axis='x',rotation=20);ax.set(ylabel='Aggregate A0 / selected cost',title='Oracle headroom versus simpler policies')
    cis=[ps['test'][p]['aggregateSpeedupCI'] for p in names]
    for x,value,ci in zip(range(len(names)),values,cis):
        ax.plot([x,x],ci,color='black',lw=1);ax.plot([x-.07,x+.07],[ci[0]]*2,color='black',lw=1);ax.plot([x-.07,x+.07],[ci[1]]*2,color='black',lw=1)
    save(23,'oracle_controller_comparison',fig,ps['test'],'Aggregate ratios sum checkpoint median costs. Conditional 95% intervals resample runs within the same fixed test states, retaining frozen choices and observed oracle labels. They exclude model-fitting and case-population uncertainty. The hindsight oracle remains optimistic and is not executable online.')
    ab=[p for p in ps['test'] if p.startswith('ablation_')];fig,ax=chart((8,4));ax.barh(ab,[ps['test'][p]['aggregateSpeedup'] for p in ab]);ax.axvline(1,c='black',lw=.7);ax.set(xlabel='Aggregate held-out speedup',title='Ablations: measured utility, not assumed feature importance')
    save(24,'ablations',fig,{p:ps['test'][p] for p in ab},'Features are omitted according to documented variants. The initial communication feature is constant across same-grid states, so noCommunication cannot establish communication-model usefulness. EMA denotes a two-snapshot blend.')
    fig,ax=chart();uncertain=[]
    for s in states:
        a=s['winner'];ci=s['actions'][a]['speedupCI'];ambiguous=a=='A0' or ci[0]<=1<=ci[1]
        ax.scatter(s['features']['chemistryFraction'],s['features']['chemistryImbalance'],s=25+30*math.log10(1+s['features']['lifetimeSteps']),c=COLORS[a],edgecolors='black' if ambiguous else 'none',alpha=.8)
        uncertain.append(dict(regime=s['regime'],checkpoint=s['checkpoint'],H=s['H'],winner=a,ambiguous=ambiguous,features=s['features']))
    for a in ACTIONS:ax.scatter([],[],c=COLORS[a],label=a)
    ax.set(xlabel='Rank-mean chemistry fraction',ylabel='Current cell-clock rank imbalance',title='Empirical regime map with uncertain boundaries');ax.legend()
    save(25,'regime_map',fig,uncertain,'Marker size reflects the bounded past-cost lifetime estimate. Black outlines flag A0 or winner intervals crossing unity. No fitted boundary or unobserved winning region is imposed.')
    inventories=data('inventories')
    for number,key,name in [(26,'relativeMassDrift','mass_conservation'),(27,'relativeEnergyDrift','energy_conservation')]:
        fig,ax=chart()
        for regime in ['persistent','translating','heldoutMoving','uniform','chemistryDominated']:
            g=[r for r in inventories if r['regime']==regime];ax.plot([r['time']*1e6 for r in g],[100*r[key] for r in g],'o-',ms=3,label=regime)
        ax.set(xlabel='Physical time (μs)',ylabel='Drift from initial budget (%)',title='Closed-box '+name.replace('_',' '));ax.legend(fontsize=7)
        save(number,name,fig,inventories,'Native thermodynamic inventory uses stored h and rho when available. Total energy is ∑ρV(h+hc+|U|²/2)−∑pV. Agreement between actions does not establish physical conservation or mesh/timestep convergence.')
    refined=data('refinement');fig,ax=chart()
    for nx in [32,64]:
        g=sorted([r for r in refined if r['nx']==nx],key=lambda r:r['dt']);ax.plot([r['dt']*1e6 for r in g],[r['temporalT_Linf'] for r in g],'o-',label=f'{nx}×{nx//4}')
    ax.set(xlabel='Global timestep (μs)',ylabel='Temperature L∞ relative to 0.5 μs (K)',title='Temporal accuracy at 40 μs');ax.legend()
    save(28,'timestep_refinement',fig,refined,'Each grid uses its own 0.5 μs reference, which is not an exact solution. Spatial refinement and heat-release changes remain limitations for physical flame interpretation.')
    fine=data('fine_oracle_summary');fig,ax=chart();xx=np.arange(4)
    for j,regime in enumerate(['persistent','heldoutMoving']):
        g=[next(r for r in fine if r['regime']==regime and r['action']==a) for a in ACTIONS];v=[r['speedup'] for r in g];ci=[r['speedupCI'] for r in g]
        position=xx+(j-.5)*.16
        points=ax.scatter(position,v,label=regime)
        ax.vlines(position,[c[0] for c in ci],[c[1] for c in ci],color=points.get_facecolors()[0],lw=1)
    ax.axhline(1,c='black',lw=.6);ax.set(xticks=xx,xticklabels=ACTIONS,ylabel='A0 / action total wall',title='Fine timestep: 0.25 μs, same 160 μs horizon');ax.legend()
    save(29,'fine_timestep_actions',fig,fine,'Five trials per action. Eight times more physical steps over the same continuation duration; still the original coarse grid and hence not a validated resolved-flame benchmark.')
    fig,ax=chart();hstates=[s for s in states if s['regime'] in ['persistent','translating','transportDominated'] and s['checkpoint']=='4e-05']
    for regime in ['persistent','translating','transportDominated']:
        g=sorted([s for s in hstates if s['regime']==regime],key=lambda s:s['H']);ax.plot([s['H'] for s in g],[s['actions']['A0']['total']['median']-s['actions']['AM']['total']['median'] for s in g],'o-',label=regime)
    ax.axhline(0,c='black',lw=.7);ax.set(xlabel='Horizon H (physical steps)',ylabel='Measured net mesh-action savings (s)',title='Migration break-even: observed horizons');ax.legend()
    save(30,'migration_horizon',fig,hstates,'Net measured benefit includes the native redistribution process. No extrapolated crossing is called observed. Future work may change the compute and communication penalties.')
    fig,ax=chart();selected_hist=[r for r in hist if r['features']]
    for regime in sorted(set(r['regime'] for r in selected_hist)):
        g=[r for r in selected_hist if r['regime']==regime];ax.plot([r['time']*1e6 for r in g],[r['features']['chemistryFraction'] for r in g],'o-',ms=2,label=regime)
    ax.set(xlabel='Physical time (μs)',ylabel='Rank-mean chemistry / timestep wall',title='Measured chemistry fraction, including cold controls');ax.legend(fontsize=6,ncol=2)
    save(31,'chemistry_fraction',fig,selected_hist,'Rank means over the last five physical steps. Synchronized nonchemistry phases can contain chemistry imbalance waits; this ratio is explanatory, not an Amdahl bound.')
    fig,ax=chart();sample=next(s for s in states if s['regime']=='persistent' and s['checkpoint']=='4e-05' and s['H']==80);fields=['p','U','h','H2','O2']
    for j,a in enumerate(ACTIONS):ax.bar(np.arange(5)+(j-1.5)*.19,[sample['actions'][a]['linearIterations'].get(f,0) for f in fields],.19,label=a,color=COLORS[a])
    ax.set(xticks=range(5),xticklabels=fields,ylabel='Sum of logged linear iterations',title='Linear-solver work after each action');ax.legend(ncol=4)
    save(32,'linear_iterations',fig,sample,'Iteration counts parsed from native solver logs. Counts alone do not identify cache misses or pure halo-communication cost.')
    for number,name,boxes,caption in [(33,'architecture',['reactingFoamPAD\nphase clocks + cell clocks','Past-only state features\nchemistry / persistence / transport','Frozen action model\nuncertainty + cooldown','A0 / AC / AM / AH\ncharge action + future solver'], 'Architecture: chemistry tasks are offloaded inside the compatible Stuttgart library; mesh migration is native redistributePar between solver processes.'),
        (34,'methodology',['Identical physical checkpoints\nwhole-condition train / validation / test','Randomized four-action continuations\n5 repeats; physical endpoint assertions','Native field gates + inventories\nphase clocks + PMPI + scaling','Frozen deployment and live rollouts\nstatistics → figures → claim audit'],'Methodology preserves held-out conditions and distinguishes retrospective oracle labels from executed controller decisions.')]:
        fig,ax=chart((10,2.6));ax.axis('off')
        for i,box in enumerate(boxes):
            ax.text(.12+i*.25,.5,box,ha='center',va='center',transform=ax.transAxes,bbox=dict(boxstyle='round,pad=.5',fc='#edf5f7',ec='#147d92'),fontsize=8)
            if i<3:ax.annotate('',xy=(.25+i*.25,.5),xytext=(.21+i*.25,.5),xycoords='axes fraction',arrowprops=dict(arrowstyle='->'))
        save(number,name,fig,boxes,caption)
    # Independent third-party toy reproduction has its own integrator and MPI.
    if (ROOT/'data/processed/quicklb.json').exists():
        q=data('quicklb');fig,ax=chart();groups={a:[r['wall'] for r in q if r['algorithm']==a and r['repeat']!=99] for a in ['NONE','GREEDY','SORT','SORT2']}
        ax.bar(list(groups),[statistics.median(v) for v in groups.values()]);ax.set(ylabel='Toy reaction–diffusion wall (s)',title='Public QUICKLB library execution, separate from CFD')
        save(35,'quicklb_reproduction',fig,q,'Public version 0.02 on a 30×30 Gray–Scott kernel with SciPy BDF, four ranks, ten steps, three repeats. This reproduces library execution, not the INCA Spray-A performance paper.')
    fig,ax=chart();acquisition=sum(r['solverWall']+r['decisionWall']+r['migrationWall'] for r in raw if r['regime'] in model['trainingCases']+model['validationCases']);feature_med=statistics.median(r['featureExtractionWall'] for r in raw)
    ax.bar(['Oracle acquisition lower bound','Model coefficient fit','Feature extraction median'],[acquisition,model['trainingWall'],feature_med]);ax.set_yscale('log');ax.set(ylabel='Wall time (s, log scale)',title='Offline acquisition cost is much larger than fitting');ax.tick_params(axis='x',rotation=12)
    save(36,'model_acquisition_cost',fig,dict(trainingValidationTrialWall=acquisition,trainingWall=model['trainingWall'],medianFeatureWall=feature_med),'Acquisition lower bound sums actual train/validation trial costs; it additionally excludes shared history generation, experiment duplication and postprocessing. Offline training is not free merely because ridge fitting is fast.')
    fig,ax=chart();overheads=[]
    for a in ACTIONS:
        off=[r['solverWall'] for r in profiles if r['regime']=='persistent' and r['action']==a and not r['profile']];on=[r['solverWall'] for r in profiles if r['regime']=='persistent' and r['action']==a and r['profile']]
        ratio=statistics.median(on)/statistics.median(off);overheads.append(dict(action=a,on=on,off=off,ratio=ratio));ax.bar(a,ratio,color=COLORS[a])
    ax.axhline(1,c='black',lw=.7);ax.set(ylabel='PMPI on / off process wall',title='Profiler perturbation calibration')
    save(37,'profiling_overhead',fig,overheads,'Three randomized on/off trials per action. Main performance claims use profiling off; this small calibration cannot resolve sub-percent overhead.')
    fig,ax=chart();ax.scatter([s['actions'][s['winner']]['total']['CV']*100 for s in states],[s['margin']/s['actions'][s['winner']]['total']['median']*100 for s in states],c=[COLORS[s['winner']] for s in states]);ax.set(xlabel='Winner run-to-run CV (%)',ylabel='Best–second median margin (%)',title='How much oracle separation exceeds observed noise?')
    save(38,'oracle_margin_noise',fig,states,'A median winner does not establish a statistically separated action. CV and margin are different statistics; this plot flags weak separation without fabricating an oracle confidence bound.')
    fig,ax=chart();gates=data('oracle_validation');maxy=max(r['sumYError'] for r in gates);ax.hist([max(r['sumYError'],1e-17) for r in gates],bins=np.geomspace(1e-17,1e-10,25));ax.set_xscale('log');ax.set(xlabel='Maximum |ΣY−1|',ylabel='Validated continuations',title='Species normalization gate at actual endpoints')
    save(39,'species_normalization',fig,gates,'Every major action is checked against the same-repeat A0 endpoint. Exact zeros are displayed at 1e-17 to permit the logarithmic axis; raw values are retained. Species positivity and per-field scales are checked separately; normalization alone is insufficient.')
    fig,ax=chart();deployed=data('deployment_summary')
    for j,policy in enumerate(['AC','AM','controller']):
        g=[r for r in deployed if r['policy']==policy];ax.plot(range(len(g)),[r['speedup'] for r in g],'o-',label=policy)
    ax.axhline(1,c='black',lw=.7);ax.set(xticks=range(6),xticklabels=[r['regime'].removeprefix('heldout')+'\n'+f"{float(r['checkpoint'])*1e6:g} μs" for r in deployed if r['policy']=='A0'],ylabel='A0 / deployed policy wall',title='Independent held-out checkpoint deployment');ax.legend()
    save(40,'deployment',fig,deployed,'Five independent trials per policy. Controller feature extraction, inference and action setup are actually timed and charged. Training/validation data only fit the frozen model before this campaign.')
    cp=data('controller_profiles');fig,ax=chart();phases=['chemistryWall','speciesWall','energyWall','pressureWall','momentumWall','ioWall'];xx=np.arange(len(phases))
    for j,regime in enumerate(['persistent','transportDominated']):
        groups=[r for r in cp if r['regime']==regime and r['profile']]
        ax.bar(xx+(j-.5)*.35,[statistics.median(statistics.mean(p[k] for p in r['phaseRankSums']) for r in groups) for k in phases],.35,label=regime)
    ax.set(xticks=xx,xticklabels=[s.removesuffix('Wall') for s in phases],ylabel='Mean rank cumulative phase duration (s)',title='Frozen-controller representative execution');ax.legend()
    save(41,'controller_phase_profile',fig,cp,'Three profiled controller executions in each representative condition, with paired profiling-off trials and field gates. Feature extraction and inference are separately charged; rank phase sums include synchronization and are not additive critical-path estimates.')
    confirmations=[data('confirmation'),data('confirmation_negative')];fig,axes=plt.subplots(1,2,figsize=(9,4))
    for ax,r in zip(axes,confirmations):
        ax.boxplot([[v['totalWall'] for v in r['rows'] if v['action']==a] for a in ['A0','AC']],labels=['A0','AC'],showfliers=True)
        ax.set(title=f"{r['regime']}: {r['speedup']:.3f}×\n95% CI [{r['CI'][0]:.3f}, {r['CI'][1]:.3f}]",ylabel='Whole continuation cost (s)')
    save(42,'independent_confirmation',fig,confirmations,'Preselected moving positive and uniform negative conditions, twenty new randomized trials per action. No model refit or test-margin tuning. Same checkpoint 40 μs and 160 μs continuation, four ranks, 256 cells; complete action and process costs.')
    consequences=data('consequence_models');fig,ax=chart()
    for label,cases,marker in [('Training',model['trainingCases'],'o'),('Held out',TEST,'^')]:
        points=[r for r in consequences['points'] if r['regime'] in cases]
        ax.scatter([r['transportDeltaPerStep'] for r in points],[r['predictedTransportDeltaPerStep'] for r in points],marker=marker,label=label)
    bounds=[min(min(r['transportDeltaPerStep'],r['predictedTransportDeltaPerStep']) for r in consequences['points']),max(max(r['transportDeltaPerStep'],r['predictedTransportDeltaPerStep']) for r in consequences['points'])];ax.plot(bounds,bounds,'k--',lw=.7)
    ax.set(xlabel='Observed rank-mean transport/pressure change (s/step)',ylabel='Explanatory prediction (s/step)',title='Post-partition consequence model; inputs are not free');ax.legend()
    save(43,'transport_consequence_model',fig,consequences,'Training uses whole training conditions only. Geometry is observed after actual partitioning and is not a free deployed-controller input. Transport duration includes synchronization effects; this is not an identifiable network-time predictor.')
    diagnosis=data('conservation_diagnosis')+data('conservation_coupling_followup');fig,axes=plt.subplots(1,2,figsize=(9,4))
    for ax,key,label in zip(axes,['relativeMassDrift','relativeEnergyDrift'],['Mass drift (%)','Total-energy drift (%)']):
        coarse=sorted([r for r in diagnosis if r['nx']==32 and r['nCorrectors']==1 and r['nOuterCorrectors']==1],key=lambda r:r['dt'])
        ax.plot([r['dt']*1e6 for r in coarse],[r[key]*100 for r in coarse],'o-',label='32×8, 1 pressure / 1 outer')
        pressure4=sorted([r for r in diagnosis if r['nx']==32 and r['nCorrectors']==4 and r['nOuterCorrectors']==1],key=lambda r:r['dt'])
        ax.plot([r['dt']*1e6 for r in pressure4],[r[key]*100 for r in pressure4],'s-',label='32×8, 4 pressure / 1 outer')
        for r in diagnosis:
            if r in coarse or r in pressure4:continue
            ax.scatter(r['dt']*1e6,r[key]*100,label=f"{r['nx']}×{r['ny']}, {r['nCorrectors']} pressure / {r['nOuterCorrectors']} outer",marker='s')
        ax.axhline(0,color='black',lw=.6);ax.set(xlabel='Global timestep (μs)',ylabel=label,title='Moving condition, 240 μs');ax.legend(fontsize=7)
    save(44,'conservation_diagnosis',fig,diagnosis,'Seven independent physical-accuracy pilots plus two matched fine-time/four-pressure-corrector controls, following a nonconvergent moving-condition energy budget. Point/line distinctions identify grid, pressure-correction and PIMPLE outer-coupling changes; these are diagnostics, not controller tuning or an exact conservation reference.')
    mpi_model=consequences['MPIModel'];fig,ax=chart()
    for label,cases,marker in [('Training',model['trainingCases'],'o'),('Held out',TEST,'^')]:
        points=[r for r in mpi_model['points'] if r['regime'] in cases]
        ax.scatter([r['MPICallDeltaPerStep'] for r in points],[r['predictedMPICallDeltaPerStep'] for r in points],marker=marker,label=label)
    bounds=[min(min(r['MPICallDeltaPerStep'],r['predictedMPICallDeltaPerStep']) for r in mpi_model['points']),max(max(r['MPICallDeltaPerStep'],r['predictedMPICallDeltaPerStep']) for r in mpi_model['points'])]
    ax.plot(bounds,bounds,'k--',lw=.7);ax.set(xlabel='Observed mean rank MPI-call change (s/step)',ylabel='Explanatory prediction (s/step)',title='MPI includes synchronization, scheduling and transfers');ax.legend()
    save(45,'mpi_consequence_model',fig,mpi_model,'Two training conditions, one entirely held-out moving condition, three profiled repeats per action. Post-partition inputs are measured and not free online features. MPI-call durations do not identify pure network-transfer cost; independent physical sample size remains small.')
    mesh_controls=data('live_mesh_followup');fig,ax=chart()
    control_rows=mesh_controls['controls']
    if control_rows:
        normalized=[max(v['Linf']/(v['atol']+v['rtol']*v['referenceScale']) for v in r['gate']['fields'].values()) for r in control_rows]
        ax.bar(range(len(control_rows)),[max(v,1e-12) for v in normalized],color=['#e05361' if not r['gate']['pass_'] else '#147d92' for r in control_rows])
        ax.set(xticks=range(len(control_rows)),xticklabels=[r['label'] for r in control_rows],yscale='log',ylabel='Maximum field difference / predefined tolerance',title='Fixed rejected partition: bounded numerical controls')
        ax.axhline(1,color='black',lw=.7)
    else:ax.text(.5,.5,'No rejected live mesh endpoint',ha='center',va='center',transform=ax.transAxes);ax.axis('off')
    save(46,'live_mesh_numerical_controls',fig,mesh_controls,'Each control uses the same observed post-migration physical checkpoint and fixed mesh ownership. Original timestep, finer global timestep and tighter ODE tolerance are compared with matching A0 controls. The original rejected trial remains in the dataset; thresholds are unchanged and these controls do not replace its timing. Exact-zero normalized errors are displayed at 1e-12 for the logarithmic axis.')
    if (ROOT/'data/processed/flux_diagnosis.json').exists():
        flux=data('flux_diagnosis');fig,ax=chart()
        for field,label,marker in [('padDivPhi','Stored face flux','o'),('padDivReconstructedPhi','Flux reconstructed from cell rho/U','s')]:
            ax.plot([r['repeat'] for r in flux['records']],[r['Linf'][field] for r in flux['records']],marker+'-',label=label)
        ax.set_yscale('symlog',linthresh=1e-8)
        ax.set(xlabel='Original moving AM repeat',ylabel='Canonical divergence difference (kg m⁻³ s⁻¹)',xticks=range(3),title='Surface-state audit at the third migration checkpoint');ax.legend(fontsize=8)
        save(47,'mapped_flux_audit',fig,flux,'Stored mass-flux divergence is compared with A0 on canonical cells, along with flux divergence reconstructed from equivalent cell rho/U. Cell-centre differences are retained in the source data. A symmetric-log axis is linear within 1e-8 of zero; no values are replaced. These observations localize discrepancies and do not by themselves prove a corrected migration algorithm.')
    if (ROOT/'data/processed/initial_state_diagnosis.json').exists():
        initialization=data('initial_state_diagnosis');fig,axes=plt.subplots(1,2,figsize=(9,4))
        for ax,dt in zip(axes,sorted({r['dt'] for r in initialization['records']})):
            for variant,label,color in [('nativeInitialization','Original initialization','#dc862c'),('initialPsiPreserved','Initial psi preserved','#147d92')]:
                row=next(r for r in initialization['records'] if r['dt']==dt and r['variant']==variant)
                ax.plot(range(3),[r['relativeMassDrift']*100 for r in row['inventories']],'o-',label=label,color=color)
            ax.axhline(0,color='black',lw=.6);ax.set(xlabel='Physical timestep index',ylabel='Mass drift from initial state (%)',xticks=range(3),title=f'Global dt = {dt*1e6:g} μs');ax.legend(fontsize=7)
        save(48,'initial_coefficient_mass',fig,initialization,'A separate diagnostic executable preallocates initial psi.oldTime before the first thermodynamic update; two steps at each of two global timesteps locate the mass offset. The original oracle/controller executable and dataset are unchanged. This initialization check does not establish long-time energy or flame convergence.')
    if (ROOT/'data/processed/flux_repair.json').exists():
        repairs=data('flux_repair');fig,axes=plt.subplots(1,2,figsize=(9,4))
        original=data('live_mesh_followup')['controls'][0]['gate']['fields']['T']['Linf']
        for ax,rows,title in zip(axes,[[r for r in repairs['records'] if r['preserveFlux']],repairs['observedZeroRepairs']],['Pre-migration physical face snapshot','Copied original: zero coupled copy restored']):
            values=[r['gate']['fields']['T']['Linf'] for r in rows]
            ax.scatter(range(3),values,color='#147d92',s=35,zorder=3);ax.axhline(original,color='#e05361',ls='--',label='Original rejected endpoint')
            ax.set(yscale='log',xticks=range(3),xlabel='Observed ownership / original repeat',ylabel='Endpoint temperature L∞ versus A0 (K)',title=title);ax.legend(fontsize=7)
        save(49,'flux_preservation_controls',fig,repairs,'Separate controls preserve source flux on exact observed ownership maps or restore the exactly zero coupled copy from its existing nonzero periodic partner. Every delivered control passes the original full-field gate; original failed timings remain rejected. All values are positive and displayed without clipping; utility launch costs are retained. Axis-aligned stationary geometry only; the snapshot utility uses global face storage and is not a scalable general-purpose mapper.')
    from writeReport import aggregate
    lp=['nativeContinuous','continuous','ACContinuous','A0','AC','AM','imbalanceThreshold','persistenceBreakEven','controller']
    executed=aggregate(data('live'),lp,baseline='nativeContinuous')
    fig,ax=chart((9,4));shown=['nativeContinuous','ACContinuous','controller','imbalanceThreshold','persistenceBreakEven','AM']
    labels=['Native','Stuttgart AC','Controller','Threshold','Persistence','Mesh\nfailed gate']
    for i,p in enumerate(shown):
        r=executed[p];color='#dc862c' if not r['valid'] else '#147d92'
        ax.bar(i,r['speedup'],color=color,alpha=.85,hatch='//' if not r['valid'] else None)
        ax.vlines(i,r['CI'][0],r['CI'][1],color='black',lw=1.2)
        ax.hlines(r['CI'],i-.08,i+.08,color='black',lw=1.2)
    ax.axhline(1,color='black',lw=.7);ax.set(xticks=range(len(shown)),xticklabels=labels,
        ylabel='Native / executed total wall',title='Executed held-out policies: full orchestration cost')
    save(50,'live_heldout_costs',fig,executed,'Three original trials in each of three held-out conditions. Ratio of summed condition medians includes preprocessing, decomposition, prefix, controller decisions, migration and every continuation. Conditional 95% intervals resample runs within those fixed conditions and do not estimate a population of flows. The hatched mesh ratio is descriptive only: its original numerical gate failed. No failed trial is removed or replaced by a repair control.')
    full_initialization=data('initial_state_long');fig,axes=plt.subplots(1,2,figsize=(9,4))
    initial_rows=full_initialization['records']
    for ax,key,title in zip(axes,['relativeMassDrift','relativeEnergyDrift'],['Mass after the full 240 μs history','Residual total-energy drift']):
        ax.bar(range(len(initial_rows)),[r[key]*100 for r in initial_rows],color='#147d92')
        ax.axhline(0,color='black',lw=.7);ax.set(xticks=range(len(initial_rows)),
            xticklabels=[f"{r['dt']*1e6:g} μs\n{r['nCorrectors']} pressure" for r in initial_rows],ylabel='Drift from initial budget (%)',title=title)
    save(51,'full_history_initialization',fig,full_initialization,'Two full moving-condition histories use the separate initialization-only executable: original 2 μs / one pressure corrector and 0.03125 μs / four pressure correctors. The mass offset is removed throughout; residual energy drift quantifies a distinct limitation. These differ in timestep and pressure coupling and are not a single-variable convergence sweep. Original frozen performance data are unchanged.')
    (OUT/'index.json').write_text(json.dumps(INDEX,indent=2))
    (OUT/'README.md').write_text('# Scientific figure index\n\n'+ '\n\n'.join(f"## {r['number']:02d}. {r['name']}\n\n{r['caption']}\n\n![{r['name']}]({r['name']}.png)\n\nData: [{r['source']}]({r['source']})" for r in INDEX))
    highlight=OUT/'highlights';highlight.mkdir(exist_ok=True)
    for item in INDEX:
        if item['number'] in [1,4,8,11,13,23,25,33,34,40,42,50]:
            for ext in ['png','pdf','svg']:shutil.copy2(OUT/(item['name']+'.'+ext),highlight/(item['name']+'.'+ext))
    print('GENERATED',len(INDEX),'figures, each with source data and three export formats.')

if __name__=='__main__':main()
