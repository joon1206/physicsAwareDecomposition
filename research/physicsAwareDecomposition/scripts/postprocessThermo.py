#!/usr/bin/env python3
"""Native OpenFOAM-derived sensible enthalpy and density, after timed runs."""
from study import ROOT,run
import json
for campaign in ['validation','reactiveTight','reactiveNoChem']:
    for path in (ROOT/'data/raw'/campaign).rglob('manifest.json'):
        m=json.loads(path.read_text())
        if campaign!='validation' and m['repeat']!=0:continue
        end=str(m.get('start',0)+m.get('steps',20))
        if campaign=='validation':end='20'
        if not (path.parent/end).is_dir():continue
        run(['reactingFoamPAD','-postProcess','-func','writeObjects(h,rho)','-time',end],path.parent,path.parent/'thermoPostprocess.log')
        print('VERIFIED native thermo output',path.parent.name,flush=True)
