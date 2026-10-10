"""Standalone scientific figures from retained machine evidence."""
from pathlib import Path
import json,math
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from thermo_continuity import sha
ROOT=Path(__file__).resolve().parents[1];P=ROOT/'candidateStudy/data/processed';FIG=ROOT/'candidateStudy/figures'

def main():
    names=['clean_thermo_campaign.json','clean_gri_campaign.json','clean_thermo_reference.json','invariant_projection_valid_data.json']
    h2=json.loads((P/names[0]).read_text());gri=json.loads((P/names[1]).read_text())
    ref=json.loads((P/names[2]).read_text())['records'];projection=json.loads((P/names[3]).read_text())['records']
    selected=[r for r in ref if r['Tinitial']==999 and r['rtol']==1e-12]
    eligible=[r for r in projection if not r['projected']['failed']]
    FIG.mkdir(exist_ok=True)
    plt.rcParams.update({'font.size':9,'axes.spines.top':False,'axes.spines.right':False,'savefig.dpi':180})
    fig,axes=plt.subplots(2,2,figsize=(10.8,7.6),layout='constrained')
    colors={'legacy':'#4f6070','HS':'#de9655','CpHS':'#2b927a'}
    for ax,records,thermos,title in [(axes[0,0],h2,['legacy','HS','CpHS'],'(a) H2: coupling drift survives continuity'),(axes[0,1],gri,['legacy','CpHS'],'(b) GRI: matched thermo-only controls')]:
        for i,t in enumerate(thermos):
            values=[100*next(r['signedEnergyDrift'] for r in records if r['dt']==dt and r['thermoControl']==t and r.get('sourcePathControl','native')=='native') for dt in [2e-6,1e-6]]
            offset=(i-(len(thermos)-1)/2)*.22
            ax.bar([offset,1+offset],values,width=.21,color=colors[t],label=t)
        ax.axhline(0,color='#888',linewidth=.6);ax.set_xticks([0,1],['dt = 2 us','dt = 1 us'])
        ax.set_ylabel('Endpoint total-energy change (%)');ax.set_title(title);ax.legend(frameon=False,ncol=len(thermos))
    ax=axes[1,0];mechs=['legacy','HS','CpHS','GRI','Alzueta']
    for i,constraint in enumerate(['CV','CP']):
        values=[next(r['relativeInvariantChange'] for r in selected if r['mechanism']==m and r['constraint']==constraint) for m in mechs]
        ax.bar([j+(i-.5)*.34 for j in range(5)],values,width=.32,label=constraint,color=['#4b77a5','#c67f45'][i])
    ax.set_yscale('log');ax.set_ylim(1e-16,1e-6);ax.set_ylabel('Relative E (CV) / H (CP) drift')
    ax.set_xticks(range(5),['H2 legacy','H2 HS','H2 CpHS','GRI','Alzueta'],rotation=17)
    ax.set_title('(c) Independent source controls: T0 = 999 K');ax.legend(frameon=False)
    ax.text(.01,.03,'Different mechanisms do not isolate thermo-only effects.',transform=ax.transAxes,fontsize=8)
    ax=axes[1,1]
    for label,c in [('H2','#4b77a5'),('GRI','#c67f45')]:
      for constraint,marker in [('CV','o'),('CP','^')]:
        group=[r for r in eligible if r['mechanism']==label and r['constraint']==constraint]
        ax.scatter([max(r['temperatureError'],1e-13) for r in group],[max(r['projected']['temperatureError'],1e-13) for r in group],s=25,marker=marker,color=c,label=f'{label} {constraint}',alpha=.8)
    ax.plot([1e-11,1],[1e-11,1],color='#777',linewidth=.8)
    ax.set_xscale('log');ax.set_yscale('log');ax.set_xlim(1e-11,1);ax.set_ylim(1e-11,1)
    ax.set_xlabel('Temperature error before recovery (K)');ax.set_ylabel('Temperature error after recovery (K)')
    ax.set_title('(d) Scalar recovery: 25/40 observed T errors increase');ax.legend(frameon=False,ncol=2,fontsize=8)
    ax.text(.42,.04,'Above diagonal: error increases',transform=ax.transAxes,fontsize=8)
    fig.savefig(FIG/'thermochemical_attribution.png');fig.savefig(FIG/'thermochemical_attribution.pdf');plt.close(fig)
    (P/'thermochemical_figure_data.json').write_text(json.dumps(dict(driverSHA256=sha(__file__),inputSHA256={n:sha(P/n) for n in names},sourceControls=selected,projectionPoints=[dict(mechanism=r['mechanism'],constraint=r['constraint'],Tinitial=r['Tinitial'],rtol=r['rtol'],before=r['temperatureError'],after=r['projected']['temperatureError'],referenceToleranceContrast=r['referenceToleranceContrast']) for r in eligible],scope='Endpoint temperature-error comparisons use the declared strict-tolerance reference, not an exact solution. Raw ratios near the reference contrast are not resolved accuracy rankings.'),indent=2)+'\n')
    print('Created thermochemical_attribution PNG/PDF from retained JSON')
if __name__=='__main__':main()
