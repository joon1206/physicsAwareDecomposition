"""Generate a bounded interpretation of the two flux-family references."""
import json
from inviscid_field_compare import state, norms, RAW, ROOT, STUDY

def main():
    data=json.loads((STUDY/'data/processed/inviscid_cross_reference.json').read_text())
    lines=['# Independent inviscid reference comparison','',
           'No reacting spatial order or exact field-error ranking is established.',
           'These cases solve the same periodic inviscid H2 kernel with native detailed',
           'chemistry, As=0 and Euler time integration. They are separate from the',
           '256-cell timing benchmark (which also has As=0). The one-column geometry and native ode controls differ. Wall times here are execution records, not a',
           'controlled performance comparison.','',
           '## Executed reference and pressure-method differences','',
           'Each reference is its flux family\'s finest executed mesh. Comparing meshes',
           'uses aligned volume averages of rho, rhoU, rhoY and rhoEa followed by',
           'independent NASA thermodynamic inversion. Field differences are not exact',
           'PDE errors. Initial inventory sampling differences and source hashes are',
           'retained in the source JSON.','',
           '| Family | Reference | Cells | dt (ns) |','|---|---|---:|---:|']
    for ref in data['references']:lines.append(f"| {ref['family']} | {ref['name']} | {ref['nx']} | {ref['dt']*1e9:g} |")
    lines+=['','| Reference family | Comparison | Cells | T L1 (K) | T Linf (K) | U L1 (m/s) | H2O L1 | Initial E relative difference |',
            '|---|---|---:|---:|---:|---:|---:|---:|']
    for r in data['records']:
        d=r['differences'];lines.append(f"| {r['referenceFamily']} | {r['name']} | {r['comparisonNx']} | {d['T']['L1']:.5f} | {d['T']['Linf']:.5f} | {d['U']['L1']:.5f} | {d['H2O']['L1']:.6g} | {r['initialEnergyRelativeDifference']:+.3e} |")
    lines+=['','## Same-mesh time check','']
    for nx in [128,256]:
      cases=[state(p.parent) for p in RAW.glob(f'HLLC_F_nx{nx}_*/central_result.json')]
      if len(cases)>=2:
        cases.sort(key=lambda s:s['config']['dt'],reverse=True);a,b=cases[0],cases[-1];d=norms(a['primitive'],b['primitive'])
        lines += [f"At nx{nx}, dt={a['config']['dt']*1e9:g} versus {b['config']['dt']*1e9:g} ns gives T L1 {d['T']['L1']:.5f} K,",
                  f"T Linf {d['T']['Linf']:.5f} K and U L1 {d['U']['L1']:.5f} m/s.",
                  'This estimates one time-refinement difference; it is not a proof of',
                  'negligible time error at all meshes or later phases.']
    lines+=['','## Interpretation','',
            'The central nx32/64/128 trajectories quenched; nx256/512 burned.',
            'The contact-resolving HLLC trajectory burns at nx32 and on all executed',
            'refinements. Its equal-property analytic-wave p/U errors are near roundoff,',
            'while its T/species errors remain first order. The analytic central wave is',
            'much more diffusive at the selected coarse meshes. This makes the central',
            'coarse quenching a discretization-sensitive outcome, not independent',
            'evidence of physical extinction. The known flux comparison isolates that',
            'source of uncertainty without establishing which finest trajectory is exact.','',
            'The pressure candidates preserve energy/mass/elements within recorded',
            'tolerances but show differing velocity and thermochemical profiles. Their',
            'differences from both flux families must be judged alongside the references\'',
            'own mesh differences. Current evidence does not justify a precise reacting',
            'accuracy/cost frontier, a resolved error floor, or a new-method claim.','',
            'Source: candidateStudy/data/processed/inviscid_cross_reference.json,',
            'hllc_verification.json, central_verification.json and inviscid_summary.json.',
            'All raw cases and failures remain retained. The figure',
            '../figures/candidates/inviscid_reference_uncertainty.png is generated',
            'from those data.']
    path=ROOT/'docs/inviscid_reference_results.md';path.write_text('\n'.join(lines)+'\n');print(path)
if __name__=='__main__':main()
