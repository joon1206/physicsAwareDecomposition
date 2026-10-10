"""Generate exact-mixture-wave evidence without promoting conservation as accuracy."""
from pathlib import Path
import json, math
ROOT=Path(__file__).resolve().parents[1]; STUDY=ROOT/'candidateStudy'
def main():
    rows=json.loads((STUDY/'data/processed/mixture_wave.json').read_text());identity=json.loads((STUDY/'data/processed/mixture_mixing_identity.json').read_text())
    text=['# Unequal-thermodynamic analytic contact-wave results','',
          'The chemistry-off, inviscid periodic H2/N2 wave has exact constant pressure',
          '101325 Pa and velocity 40 m/s. Temperature and composition translate with',
          'that velocity. The installed NASA7 thermodynamics are used in both the',
          'case and independent inventory/analytic evaluation. See the pre-test',
          'derivation in candidates/mixturePressureCompatibility.md.','',
          '| Method | nx | T L1 (K) | H2 L1 | p Linf (Pa) | Ux Linf (m/s) | Relative energy drift | Max element drift | Max EOS residual |',
          '|---|---:|---:|---:|---:|---:|---:|---:|---:|']
    for r in sorted(rows,key=lambda r:(r['mode'],r['nx'])):
        e=r['errors'];text.append(f"| {r['mode']} | {r['nx']} | {e['T']['L1']:.6g} | {e['H2']['L1']:.6g} | {e['p']['Linf']:.6g} | {e['Ux']['Linf']:.6g} | {r['signedEnergyDrift']:+.3e} | {max(abs(v) for v in r['elementDrift'].values()):.3e} | {r['maxEOSRelative']:.3e} |")
    text+=['','## Refinement and interpretation','',
           '| Method | Mesh pair | T L1 order | H2 L1 order | p Linf order |','|---|---|---:|---:|---:|']
    for mode in sorted(set(r['mode'] for r in rows)):
        rr=sorted([r for r in rows if r['mode']==mode],key=lambda r:r['nx'])
        for a,b in zip(rr,rr[1:]):
            order=lambda f,n:math.log(a['errors'][f][n]/b['errors'][f][n],2)
            text.append(f"| {mode} | {a['nx']}/{b['nx']} | {order('T','L1'):.4f} | {order('H2','L1'):.4f} | {order('p','Linf'):.4f} |")
    text+=['',
           'G and the tight pressure/species/energy block remove the recorded energy',
           'drift but do not preserve the exact mixture pressure. Their temperature',
           'errors closely track the baseline on this independent analytic problem.',
           'HLLC produces smaller pressure deviations but finite thermodynamic mixing',
           'error; its equal-property pressure-preservation result does not generalize',
           'to the unequal-NASA mixture. The central flux has larger temperature',
           'diffusion. These statements concern the displayed configurations, with',
           'common fixed dt20ns, rather than all possible fluxes or coupling methods.','',
           'The two-donor common-weight remap independently conserves partial mass',
           'and energy but changes EOS pressure. Enforcing pressure instead would',
           'change the conserved energy target. This is a known nonlinear thermodynamic',
           'compatibility problem, with the conditional proof and prior-art boundary',
           'recorded in the derivation. Formation-reference shifts cancel algebraically',
           'from the mixing mismatch and were checked numerically.','']
    r=next(r for r in identity['records'] if r['weight']==.5)
    text += [f"For the 50/50 example: pressure shift {r['conservativeRecovery']['p']-101325:.6f} Pa;",
             f"energy-density mismatch at enforced original pressure {r['energyDensityMismatch']:.6f} J/m3.",'',
             'No numerical-method contribution is asserted from this diagnostic.',
             'The raw wave inputs/fields/ledgers and exact executable/source hashes',
             'are retained. New methods would have to improve compatibility and the',
             'accuracy/cost frontier, beyond correcting the original global defect.','',
             'Sources: candidateStudy/data/processed/mixture_wave.json and',
             'mixture_mixing_identity.json.']
    path=ROOT/'docs/mixture_pressure_results.md';path.write_text('\n'.join(text)+'\n');print(path)
if __name__=='__main__':main()
