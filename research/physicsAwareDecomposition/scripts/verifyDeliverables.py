#!/usr/bin/env python3
"""Fail on missing evidence, broken numerical gates or corrupted matrices."""
import json,pathlib,py_compile
from study import ROOT
source=pathlib.Path(__file__).resolve().parents[1]
for p in (source/'scripts').glob('*.py'):py_compile.compile(str(p),doraise=True)
for folder in ['tight','noChem']:
    paths=list((ROOT/'data/processed'/folder).glob('partition_validation*.json'))
    if not paths:raise RuntimeError('Missing partition validation '+folder)
    for p in paths:
        if not json.loads(p.read_text())['pass']:raise RuntimeError('Numerical gate failed '+str(p))
if not json.loads((ROOT/'data/processed/transient_validation.json').read_text())['pass']:raise RuntimeError('Transient norm gate failed')
for p in (ROOT/'figures').glob('*.png'):
    for ext in ['pdf','svg','source.json']:
        if not p.with_suffix('.'+ext).is_file():raise RuntimeError('Incomplete figure '+str(p))
print('VERIFIED source syntax, accepted partition gates, transient norm gate and figure companions')
