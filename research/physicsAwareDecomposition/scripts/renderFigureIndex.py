#!/usr/bin/env python3
"""Render a compact visual QA index of the exported figure PNGs."""
import os,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'build/pydeps'))
os.environ.setdefault('MPLCONFIGDIR',str(ROOT/'build/mplconfig'))
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from PIL import Image
out=ROOT/'build/qa';out.mkdir(exist_ok=True,parents=True)
paths=sorted((ROOT/'figures').glob('*.png'))
for start in range(0,len(paths),6):
    fig,axes=plt.subplots(2,3,figsize=(15,8),dpi=140)
    for ax in axes.flat:ax.axis('off')
    for ax,p in zip(axes.flat,paths[start:start+6]):
        ax.imshow(Image.open(p));ax.set_title(p.stem,fontsize=9)
    fig.tight_layout();fig.savefig(out/f'index_{start//6+1}.png');plt.close(fig)
print('Rendered visual QA index',len(paths),'figures')

