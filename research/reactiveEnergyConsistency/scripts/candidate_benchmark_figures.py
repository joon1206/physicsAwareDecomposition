"""Executed cost/conservation/trajectory figure; self-reference explicitly labelled."""
from pathlib import Path
import json,math
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
ROOT=Path(__file__).resolve().parents[1];STUDY=ROOT/'candidateStudy'
data=json.loads((STUDY/'data/processed/benchmark_matrix.json').read_text());rows=data['records']
fig,axes=plt.subplots(2,2,figsize=(12.5,8.5),layout='constrained')
colors=plt.get_cmap('tab10').colors
for i,r in enumerate(rows):
    x=r['medianWallRatio'];lower=(r['wallMedian']-r['wallMin'])/rows[0]['wallMedian'];upper=(r['wallMax']-r['wallMedian'])/rows[0]['wallMedian']
    for ax,y in [(axes[0,0],max(abs(r['energyDrift']),1e-16)),(axes[0,1],r['T_L1'])]:
        ax.errorbar(x,y,xerr=[[lower],[upper]],fmt='o',color=colors[i],capsize=3,label=r['label'])
axes[0,0].set(xscale='log',yscale='log',xlabel='Median wall time / baseline (3 trials)',ylabel='Absolute relative energy drift',title='Conservation versus executed runtime')
axes[0,1].set(xscale='log',xlabel='Median wall time / baseline (3 trials)',ylabel='Temperature L1 difference (K)',title='Difference from block dt = 0.125 us\nSelf refinement; no exact-error claim')
axes[0,0].legend(fontsize=8,loc='center right')
labels=[r['label'].replace(' ','\n') for r in rows];x=list(range(len(rows)))
energy=[sum(v['solves'] for k,v in r['linearSolvers'].items() if k in ['h','deltaConservativeH','deltaHs','deltaH']) for r in rows]
pressure=[r['linearSolvers'].get('p',{}).get('solves',0) for r in rows]
axes[1,0].bar([i-.2 for i in x],energy,width=.4,label='Energy incl. corrections')
axes[1,0].bar([i+.2 for i in x],pressure,width=.4,label='Pressure')
axes[1,0].set(yscale='log',ylabel='Actual solver invocations',title='Counts from completed solver logs',xticks=x,xticklabels=labels)
axes[1,0].tick_params(axis='x',labelsize=7);axes[1,0].legend(fontsize=8)
mpi=[r for r in rows if 'MPI' in r];denom=rows[0]['MPI']['collectives']
axes[1,1].bar(range(len(mpi)),[r['MPI']['collectives']/denom for r in mpi],color=[colors[rows.index(r)] for r in mpi])
axes[1,1].set(ylabel='Collective calls / baseline',title='Separate matching instrumentation runs\nOperation counts; contended timings excluded',xticks=range(len(mpi)),xticklabels=[r['label'].replace(' ','\n') for r in mpi])
for ax in axes.flat:ax.grid(True,axis='y',which='both',alpha=.2);ax.set_axisbelow(True)
fig.suptitle('Periodic reacting kernel, same 256-cell mesh; every=0 ledger settings',fontsize=12)
out=ROOT/'figures/candidates';out.mkdir(exist_ok=True)
fig.savefig(out/'benchmark_cost_conservation.png',dpi=180);fig.savefig(out/'benchmark_cost_conservation.pdf')
print(out/'benchmark_cost_conservation.png')
