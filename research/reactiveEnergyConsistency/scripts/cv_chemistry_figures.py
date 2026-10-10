"""Static scientific figure generated only from corrected chemistry evidence."""
from pathlib import Path
import json
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.ticker import NullLocator
ROOT=Path(__file__).resolve().parents[1]
data=json.loads((ROOT/'candidateStudy/data/processed/cv_chemistry_analysis.json').read_text())
fig,axes=plt.subplots(1,3,figsize=(12,3.9))
for mode,label,color in [('none','CV source, baseline','#bd4d36'),('conservativeState','CV source + G','#1d6985')]:
    rows=sorted([r for r in data['records'] if r['odeThermalPath']=='constantVolume' and r['mode']==mode and r['odeRelativeTolerance']==1e-10],key=lambda r:r['dt'])
    dt=[r['dt']*1e6 for r in rows]
    for ax,values in zip(axes,[[r['errors']['T']['Linf'] for r in rows],[abs(r['signedEnergyDrift']) for r in rows],[r['maxSourceRelativeEnergyChange'] for r in rows]]):
        ax.loglog(dt,values,'o-',color=color,label=label,lw=1.5,ms=5)
cp=next(r for r in data['records'] if r['odeThermalPath']=='constantPressure')
for ax,value in zip(axes,[cp['errors']['T']['Linf'],abs(cp['signedEnergyDrift']),cp['maxSourceRelativeEnergyChange']]):
    ax.loglog([cp['dt']*1e6],[value],'s',color='#74449a',ms=6,label='Matched CP source + G')
axes[0].axhspan(1e-10,data['referenceTemperatureToleranceContrast'],color='#b3b3b3',alpha=.25,label='Reference tolerance contrast')
axes[0].set_ylim(1e-10,1e-2)
for ax,title,ylabel in zip(axes,['Closed-volume endpoint','Final CFD conservation','Local source invariant'],['Temperature difference (K)','Absolute relative energy drift','Max relative source energy change']):
    ax.set_title(title,fontsize=11);ax.set_xlabel('CFD timestep (us)');ax.set_ylabel(ylabel);ax.grid(True,which='both',alpha=.2)
    ax.set_xticks([.125,.25,.5,1.]);ax.set_xticklabels(['0.125','0.25','0.5','1'])
    ax.xaxis.set_minor_locator(NullLocator())
axes[0].legend(fontsize=7.4,loc='upper left')
fig.suptitle('Known chemistry thermal paths — homogeneous H2/air at 240 us',fontsize=13)
fig.text(.5,.02,'Corrected autonomous ODE callback. Agreement below the reference contrast is not a resolved order estimate.',ha='center',fontsize=8)
fig.tight_layout(rect=[0,.07,1,.93])
out=ROOT/'figures/candidates';out.mkdir(exist_ok=True)
for ext in ['png','pdf']:fig.savefig(out/f'chemistry_thermal_path.{ext}',dpi=180)
print('Saved chemistry thermal-path figure')
