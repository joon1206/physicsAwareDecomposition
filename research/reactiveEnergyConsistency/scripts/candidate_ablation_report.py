"""Absolute and common-gauge ablation measurements; no altered baseline evidence."""
from pathlib import Path
import csv,json,math
from analyze import compare
ROOT=Path(__file__).resolve().parents[1];STUDY=ROOT/'candidateStudy'
results=json.loads((STUDY/'data/processed/screen_summary.json').read_text())
base=next(x for x in results if x['name']=='F_none_dt2e-06_s1_g0_o1_p1')
mix=next(x for x in results if x['name']=='Mix_none_dt2e-06_s1_g0_o1_p1')
rows=[]
for r in results:
    terms=r['cellCumulativeTerms'];de=r['end']['E_stored']-r['initial']['E_stored']
    rows.append(dict(name=r['name'],dt=r['dt'],E0=r['initial']['E_stored'],DE=de,
        commonNormalizedDE=de/abs(base['initial']['E_stored']),DrhoH=terms['DrhoH'],DrhoC=terms['DrhoC'],
        densityPair=terms['DrhoH']+terms['DrhoC'],densityAbsoluteSpaceTimeNorm=r['densityAbsoluteSpaceTimeNorm'],
        massDrift=r['massDrift'],elements=r['elementDrift'],maxCellClosure=r['maxCellClosure']))
comparisons={}
for r in results:
    if r['kind']=='Mix' and r['formationAblation']['scale']!=1:
        comparisons[r['name']]=compare(STUDY/'data/raw'/mix['name'],STUDY/'data/raw'/r['name'])
out=dict(rows=rows,mixFieldComparisons=comparisons,
  cautions=['Relative energy uses a reference-dependent initial denominator; the common normalization uses physical F E0.',
            'Scale ablations change reacting thermochemistry; ODE failures are not conservative-method failures.',
            'Cell prototype pBeforeProjection denotes pressure at energy assembly, renamed pEnergyAssembly in later source.'])
(STUDY/'data/processed/ablation_analysis.json').write_text(json.dumps(out,indent=2)+'\n')
for row in rows:
    if row['name'].startswith(('Mix_','F_none')) and 'pilot' not in row['name']:
        print(row['name'],f"DE={row['DE']:.9e} Hs={row['DrhoH']:.9e} Hc={row['DrhoC']:.9e} L1rhoHa={row['densityAbsoluteSpaceTimeNorm']:.9e}")
for name,norms in comparisons.items():print(name,'Mix T Linf',norms['T']['Linf'],'rho Linf',norms['rho']['Linf'])
