"""Scientific screening figures; all points are executed data, no performance claims."""
from pathlib import Path
import json,math
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
ROOT=Path(__file__).resolve().parents[1];STUDY=ROOT/'candidateStudy'
records=json.loads((STUDY/'data/processed/screen_summary.json').read_text())
fig,axes=plt.subplots(1,3,figsize=(15,4.2),layout='constrained')
for mode,marker in [('none','o'),('localInternal','x'),('speciesFlux','s'),('conservativeState','^'),('blockConservative','D')]:
    rows=[r for r in records if r['kind']=='F' and r['mode']==mode and not r.get('MPIProfile',False) and not r['formationAblation']['elementGauge'] and r['formationAblation']['scale']==1 and 'pilot' not in r['name'] and 'EOS2' not in r['name']]
    axes[0].scatter([r['solverWall'] for r in rows],[max(abs(r['signedEnergyDrift']),1e-16) for r in rows],label=mode,marker=marker,s=38)
axes[0].set(xlabel='Executed solver wall time (s)',ylabel='Absolute relative energy drift',yscale='log',title='Reacting screen; accuracy gates still required')
axes[0].legend(fontsize=7)
wave=json.loads((STUDY/'data/processed/candidate_wave.json').read_text())
for mode in ['none','conservativeState']:
    rows=sorted([r for r in wave if r['mode']==mode and r['dt']==20e-9],key=lambda r:r['nx'])
    axes[1].loglog([r['nx'] for r in rows],[r['errors']['T']['L1'] for r in rows],'-o',label=mode)
axes[1].set(xlabel='Cells along entropy wave',ylabel='Analytic temperature L1 error (K)',title='Same constant-Cp, inviscid model')
axes[1].legend(fontsize=8)
ref=json.loads((STUDY/'data/processed/cantera_reference.json').read_text())
for mode in ['none','conservativeState']:
    rows=sorted([r for r in ref['comparisons'] if r['mode']==mode and r['name'].endswith('_oneColumn')],key=lambda r:r['dt'])
    axes[2].loglog([r['dt']*1e6 for r in rows],[r['errors']['T']['Linf'] for r in rows],'-o',label=mode)
axes[2].set(xlabel='Timestep (us)',ylabel='Cantera endpoint T error (K)',title='0D: verified phase and kinetic conventions')
axes[2].legend(fontsize=8)
for ax in axes:ax.grid(True,which='both',alpha=.2)
out=ROOT/'figures/candidates';out.mkdir(exist_ok=True)
fig.savefig(out/'screening_evidence.png',dpi=180);fig.savefig(out/'screening_evidence.pdf')
print(out/'screening_evidence.png')
