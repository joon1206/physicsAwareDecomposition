"""Export source-invariant branch controls directly from retained native/reference data."""
from pathlib import Path
import hashlib,json
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.ticker import NullLocator
ROOT=Path(__file__).resolve().parents[1];P=ROOT/'candidateStudy/data/processed'
native=json.loads((P/'cv_branch_probe.json').read_text());refs=json.loads((P/'cantera_branch_probe.json').read_text())
fig,axes=plt.subplots(1,2,figsize=(10,4.1))
cross=sorted([r for r in native if r['Tinitial']==999 and r['chunks']==1000],key=lambda r:r['odeRelativeTolerance'],reverse=True)
ctcross=next(r for r in refs if r['Tinitial']==999)['records']
axes[0].loglog([r['odeRelativeTolerance'] for r in cross],[r['relativeEnergyChange'] for r in cross],'o-',color='#1d6985',label='Native, T0=999 K',lw=1.8)
axes[0].loglog([r['rtol'] for r in ctcross],[abs(r['end']['energyDrift']) for r in ctcross],'s--',color='#bd4d36',label='Cantera, T0=999 K',lw=1.5)
axes[0].axhline(1e-10,color='#777777',ls=':',label='Original source-energy gate')
axes[0].set_ylim(3e-11,5e-7);axes[0].set_title('Crossing discrepancy persists',fontsize=11)
axes[0].legend(fontsize=8,loc='lower left')
axes[1].loglog([r['odeRelativeTolerance'] for r in cross],[r['relativeJumpUnexplainedEnergy'] for r in cross],'o-',color='#1d6985',label='Native crossing minus jump',lw=1.8)
for temp,color,marker in [(1001,'#bd4d36','s'),(1100,'#755298','^')]:
    rows=next(r for r in refs if r['Tinitial']==temp)['records']
    axes[1].loglog([r['rtol'] for r in rows],[abs(r['end']['energyDrift']) for r in rows],marker+'--',color=color,label=f'Cantera, T0={temp} K',lw=1.4)
axes[1].set_ylim(2e-15,5e-10);axes[1].set_title('Jump diagnostic and branch controls',fontsize=11)
axes[1].legend(fontsize=8,loc='upper right')
for ax in axes:
    ax.set_xlabel('Declared ODE relative tolerance');ax.set_ylabel('Absolute relative source energy change')
    ax.set_xlim(2e-8,5e-13);ax.set_xticks([1e-8,1e-10,1e-12]);ax.xaxis.set_minor_locator(NullLocator())
    ax.grid(True,which='both',alpha=.18)
fig.suptitle('Unchanged legacy NASA data — direct closed-volume H2/air source, 10 us',fontsize=12)
fig.text(.5,.018,'Native crossing concentrations use 1000 diagnostic intervals. Jump interpolation is approximate; solver tolerance norms differ.',ha='center',fontsize=8)
fig.tight_layout(rect=[0,.07,1,.93])
out=ROOT/'figures/candidates';out.mkdir(exist_ok=True)
for ext in ['png','pdf']:fig.savefig(out/f'chemistry_branch_invariant.{ext}',dpi=180)
(P/'chemistry_branch_figure_sources.json').write_text(json.dumps(dict(scriptSHA256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
    sources={name:hashlib.sha256((P/name).read_bytes()).hexdigest() for name in ['cv_branch_probe.json','cantera_branch_probe.json']}),indent=2)+'\n')
print('Saved chemistry branch-invariant PNG/PDF')
