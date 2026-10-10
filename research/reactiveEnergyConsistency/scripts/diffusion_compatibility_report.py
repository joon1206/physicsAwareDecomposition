"""Report the exact diffusion control and immutable on/off field comparisons."""
from pathlib import Path
import json, math
from foamio import read_field
ROOT=Path(__file__).resolve().parents[1];STUDY=ROOT/'candidateStudy';RAW=STUDY/'data/raw'

def field_difference(a,b):
    n=a['nx'];end=format(a['TF'],'.12g');out={}
    for f in ['T','p','rho','h','U','A','B']:
        va=read_field(RAW/a['name']/end/f,n);vb=read_field(RAW/b['name']/end/f,n)
        ds=[math.sqrt(math.fsum((x-y)**2 for x,y in zip(u,v))) if isinstance(u,tuple) else abs(u-v) for u,v in zip(va,vb)]
        out[f]=dict(L1=math.fsum(ds)/n,Linf=max(ds))
    return out

def main():
    rows=json.loads((STUDY/'data/processed/diffusion_wave.json').read_text())
    if any(r.get('transportRevision')=='_coupledSync' for r in rows):
        rows=[r for r in rows if r.get('compatibleSpeciesHeatFlux') is None or r.get('transportRevision')=='_coupledSync']
    pairs=[]
    for r in rows:
        flag=r.get('compatibleSpeciesHeatFlux')
        if flag is False:
            parent=next(q for q in rows if q.get('compatibleSpeciesHeatFlux') is None and (q['mode'],q['nx'],q['Pr'],q['dt'])==(r['mode'],r['nx'],r['Pr'],r['dt']))
            pairs.append(dict(kind='flagOffVersusParent',a=parent['name'],b=r['name'],fields=field_difference(parent,r)))
        if flag is True and r['Pr']==1:
            off=next(q for q in rows if q.get('compatibleSpeciesHeatFlux') is False and (q['mode'],q['nx'],q['Pr'],q['dt'])==(r['mode'],r['nx'],r['Pr'],r['dt']))
            pairs.append(dict(kind='Pr1FlagOnVersusOff',a=off['name'],b=r['name'],fields=field_difference(off,r)))
    orders=[]
    for mode,flag in [('none',None),('conservativeState',None),('blockConservative',None),('none',True),('conservativeState',True)]:
        rr=sorted([r for r in rows if r['mode']==mode and r.get('compatibleSpeciesHeatFlux') is flag and r['Pr']==.7],key=lambda x:x['nx'])
        for a,b in zip(rr,rr[1:]):
            orders.append(dict(mode=mode,compatibleSpeciesHeatFlux=flag,coarse=a['nx'],fine=b['nx'],speciesOrder=math.log(a['errors']['A']['L1']/b['errors']['A']['L1'],2)))
    data=dict(records=rows,comparisons=pairs,orders=orders,
              scope='Equal-W unequal-constant-Cp exact advection-diffusion. T/p/u constant. Only species errors above roundoff support convergence estimates. A known-physics transport correction, not a novel method or resolved hydrogen validation.')
    (STUDY/'data/processed/diffusion_compatibility.json').write_text(json.dumps(data,indent=2)+'\n')
    lines=['# Sensible species-diffusion compatibility: executed control','',
           'The known species enthalpy face flux removes the local temperature error',
           'in the declared equal-W/unequal-Cp diffusion test. It does not repair the',
           'original zero-transport kernel density defect or establish method novelty.',
           'Derivation and pre-test predictions: candidates/speciesSensibleDiffusion.md.','',
           'All cases: L=20 mm, T=800 K, p=101325 Pa, u=40 m/s, D=.01 m2/s,',
           'TF=100 us, dt=.2 us; Cp_A=1000, Cp_B=2000 J/(kg K), equal W=28.0134.',
           'Exact species solution is translating exponential diffusion of a cosine.',
           'The physical species enthalpy flux keeps T/p/rho/u constant.','',
           '| Pr | nx | Method | Compatible flux | T L1 (K) | p Linf (Pa) | YA L1 | Relative energy drift | Cell closure (J) |',
           '|---:|---:|---|---|---:|---:|---:|---:|---:|']
    for r in sorted(rows,key=lambda r:(r['Pr'],r['nx'],r['mode'],str(r.get('compatibleSpeciesHeatFlux')))):
        flag=r.get('compatibleSpeciesHeatFlux');label='parent' if flag is None else 'on' if flag else 'off'
        lines.append(f"| {r['Pr']:g} | {r['nx']} | {r['mode']} | {label} | {r['errors']['T']['L1']:.7g} | {r['errors']['p']['Linf']:.7g} | {r['errors']['A']['L1']:.7g} | {r['signedEnergyDrift']:+.5e} | {r['maxLocalEnergyResidual']:.4e} |")
    lines+=['','Flag-off/parent and Pr=1 on/off endpoint field comparisons are recorded',
            'for T/p/rho/h/U/A/B in diffusion_compatibility.json. Maximum comparison',
            f"Linf over all recorded fields: {max(v['Linf'] for r in pairs for v in r['fields'].values()):.5g}.",
            'Pr=.7 parent temperature errors increase toward a nonzero model-error',
            'floor while the compatible flux leaves only recorded roundoff/solve error.',
            'That is a local transport-model result; global energy alone misses it.','',
            '| Method | Flux | Mesh pair | Observed YA L1 order |',
            '|---|---|---|---:|']
    for r in orders:lines.append(f"| {r['mode']} | {'on' if r['compatibleSpeciesHeatFlux'] else 'parent'} | {r['coarse']}→{r['fine']} | {r['speciesOrder']:.5f} |")
    lines+=['','The correction uses post-species composition and predictor p/T, frozen',
            'through the conservative energy inversion. Its divergence is included',
            'in both the actual residual and local transport ledger. A separate',
            'DextraSensibleTransport column reports its signed local contribution;',
            'absExtraSensibleTransport distinguishes nonzero local redistribution',
            'from its zero periodic-domain sum. Positivity and EOS are recorded',
            'for every case. This special constant-temperature control does not',
            'prove a general nonlinear face chain rule, time order or entropy stability.',
            'The shared Sutherland reacting controls are interpreted separately.','']
    (ROOT/'docs/diffusion_compatibility_results.md').write_text('\n'.join(lines))
    print('Diffusion cases:',len(rows),'field equivalence comparisons:',len(pairs),'max Linf',max(v['Linf'] for r in pairs for v in r['fields'].values()))
if __name__=='__main__':main()
