"""Static scientific figures from the exact diffusion-control evidence."""
from pathlib import Path
import json
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
ROOT=Path(__file__).resolve().parents[1];STUDY=ROOT/'candidateStudy'

def main():
    rows=json.loads((STUDY/'data/processed/diffusion_wave.json').read_text())
    if any(r.get('transportRevision')=='_coupledSync' for r in rows):
        rows=[r for r in rows if r.get('compatibleSpeciesHeatFlux') is None or r.get('transportRevision')=='_coupledSync']
    fig,axes=plt.subplots(2,2,figsize=(11,8),constrained_layout=True)
    styles=[('none',None,'Baseline','o','#444444'),('conservativeState',None,'G','s','#bb6a19'),('blockConservative',None,'Block','^','#b33757'),('none',True,'Baseline + flux','o','#207dba'),('conservativeState',True,'G + flux','s','#319555')]
    for mode,flag,label,marker,color in styles:
        rr=sorted([r for r in rows if r['mode']==mode and r.get('compatibleSpeciesHeatFlux') is flag and r['Pr']==.7],key=lambda r:r['nx'])
        x=[r['nx'] for r in rr]
        for ax,(f,norm) in zip(axes.flat,[('T','L1'),('p','Linf'),('A','L1')]):
            ax.semilogy(x,[r['errors'][f][norm] for r in rr],marker+'-',color=color,label=label)
        axes[1,1].semilogy(x,[max(abs(r['signedEnergyDrift']),1e-16) for r in rr],marker+'-',color=color,label=label)
    labels=['Temperature L1 error (K)','Pressure Linf error (Pa)','Species YA L1 error','Absolute relative energy drift']
    for ax,label in zip(axes.flat,labels):
        ax.set_xlabel('Cells');ax.set_xticks([32,64,128]);ax.set_ylabel(label);ax.grid(alpha=.2)
    axes[0,0].legend(fontsize=8,ncol=2)
    fig.suptitle('Exact unequal-Cp diffusion control, Pr=0.7')
    fig.supxlabel('Known species enthalpy flux restores constant T/p; species discretization error remains.\nPr=1 on/off controls and flag-off/parent fields coincide.',fontsize=10)
    dest=ROOT/'figures/candidates';dest.mkdir(exist_ok=True)
    fig.savefig(dest/'species_diffusion_compatibility.png',dpi=180);fig.savefig(dest/'species_diffusion_compatibility.pdf');plt.close(fig)
if __name__=='__main__':main()
