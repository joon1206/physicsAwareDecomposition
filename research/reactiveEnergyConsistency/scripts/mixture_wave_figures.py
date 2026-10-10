"""Exact mixture-wave errors and pressure disturbance from executed fields."""
from pathlib import Path
import json
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.ticker import NullLocator
from foamio import read_field
ROOT=Path(__file__).resolve().parents[1];STUDY=ROOT/'candidateStudy'
def main():
    rows=json.loads((STUDY/'data/processed/mixture_wave.json').read_text())
    fig,axs=plt.subplots(2,2,figsize=(11.5,8),layout='constrained')
    for mode,color in [('none','tab:red'),('conservativeState','tab:green'),('blockConservative','tab:purple'),('central','tab:blue'),('hllc','tab:orange')]:
        rr=sorted([r for r in rows if r['mode']==mode],key=lambda r:r['nx']);nx=[r['nx'] for r in rr]
        for ax,y in [(axs[0,0],[r['errors']['T']['L1'] for r in rr]),(axs[0,1],[r['errors']['p']['Linf'] for r in rr]),(axs[1,0],[max(abs(r['signedEnergyDrift']),1e-16) for r in rr])]:
            ax.plot(nx,y,'o-',color=color,label=mode)
        r=rr[-1];n=r['nx'];path=STUDY/'data/raw'/r['name']/format(r['TF'],'.12g')/'p'
        axs[1,1].plot([20*(i+.5)/n for i in range(n)],[p-101325 for p in read_field(path,n)],color=color,label=mode)
    for ax in [axs[0,0],axs[0,1],axs[1,0]]:
        ax.set(xscale='log',yscale='log',xlabel='Cells');ax.set_xticks([32,64,128],['32','64','128']);ax.xaxis.set_minor_locator(NullLocator())
    axs[0,0].set(ylabel='Temperature L1 error (K)',title='Independent analytic temperature error');axs[0,0].legend(fontsize=8)
    axs[0,1].set(ylabel='Pressure Linf error (Pa)',title='Exact pressure equilibrium is disturbed')
    axs[1,0].set(ylabel='Absolute relative energy drift',title='Conservation differs from solution accuracy')
    axs[1,1].axhline(0,color='black',linestyle='--',linewidth=1,label='Exact');axs[1,1].set(xlabel='Position (mm)',ylabel='Pressure minus exact value (Pa)',title='nx128 endpoint pressure disturbance')
    for ax in axs.flat:ax.grid(alpha=.2,which='both');ax.set_axisbelow(True)
    fig.suptitle('Analytic H2/N2 mixture transport at 20 us\nNASA thermodynamics; no chemistry or diffusion; dt=20 ns',fontsize=12)
    out=ROOT/'figures/candidates';fig.savefig(out/'mixture_wave_compatibility.png',dpi=180);fig.savefig(out/'mixture_wave_compatibility.pdf')
    print(out/'mixture_wave_compatibility.png')
if __name__=='__main__':main()
