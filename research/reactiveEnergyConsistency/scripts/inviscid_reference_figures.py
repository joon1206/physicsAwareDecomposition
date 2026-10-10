"""Executed reference profiles and uncertainty; no exact reacting-error claim."""
from pathlib import Path
import json, math
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.ticker import NullLocator
from inviscid_field_compare import state, ROOT, RAW, STUDY

def main():
    report=json.loads((STUDY/'data/processed/inviscid_cross_reference.json').read_text())
    fig,axs=plt.subplots(2,3,figsize=(13.5,8),layout='constrained')
    for family,color in [('central','tab:blue'),('hllc','tab:orange')]:
        ref=next(r for r in report['references'] if r['family']==family)
        st=state(RAW/ref['name']);n=st['config']['nx'];x=[20*(i+.5)/n for i in range(n)]
        for ax,f,ylabel in zip(axs[0],['T','H2O','U'],['Temperature (K)','H2O mass fraction','Velocity x (m/s)']):
            y=[v[0] for v in st['primitive'][f]] if f=='U' else st['primitive'][f]
            ax.plot(x,y,color=color,label=f'{family}, nx={n}')
            ax.set(xlabel='Position (mm)',ylabel=ylabel,title='Finest executed reference profiles')
    for mode,color in [('none','tab:red'),('conservativeState','tab:green'),('blockConservative','tab:purple')]:
        paths=[p.parent for p in RAW.glob('InvF_'+mode+'_*/result.json')]
        st=max((state(p) for p in paths),key=lambda s:s['config']['nx']);n=st['config']['nx'];x=[20*(i+.5)/n for i in range(n)]
        for ax,f in zip(axs[0],['T','H2O','U']):
            y=[v[0] for v in st['primitive'][f]] if f=='U' else st['primitive'][f]
            ax.plot(x,y,color=color,alpha=.7,linewidth=1,label=f'{mode}, nx={n}')
    axs[0,0].legend(fontsize=7,ncol=1)
    for ax,field,ylabel in zip(axs[1],['T','H2O','U'],['Temperature L1 difference (K)','H2O L1 difference','Velocity L1 difference (m/s)']):
        for family,style in [('central','-'),('hllc','--')]:
            for mode,color in [('none','tab:red'),('conservativeState','tab:green'),('blockConservative','tab:purple')]:
                rows=sorted([r for r in report['records'] if r['referenceFamily']==family and r['mode']==mode],key=lambda r:r['nx'])
                ax.plot([r['nx'] for r in rows],[r['differences'][field]['L1'] for r in rows],style,marker='o',color=color,label=f'{mode} vs {family}')
        ax.set(xscale='log',yscale='log',xlabel='Pressure-method cells',ylabel=ylabel,title='Conservative restriction; numerical differences')
        ax.set_xticks([32,64,128],['32','64','128'])
        ax.xaxis.set_minor_locator(NullLocator())
    for ax in axs.flat:ax.grid(alpha=.2);ax.set_axisbelow(True)
    fig.suptitle('Inviscid H2 kernel at 240 us: reference uncertainty remains\nNumerical differences, not exact errors. Bottom: solid vs central; dashed vs HLLC.',fontsize=12)
    out=ROOT/'figures/candidates';out.mkdir(exist_ok=True)
    fig.savefig(out/'inviscid_reference_uncertainty.png',dpi=180);fig.savefig(out/'inviscid_reference_uncertainty.pdf')
    print(out/'inviscid_reference_uncertainty.png')
if __name__=='__main__':main()
