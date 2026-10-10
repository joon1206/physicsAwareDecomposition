"""Roundoff-control evidence, including retained failure and policy refinement."""
from pathlib import Path
import json
ROOT=Path(__file__).resolve().parents[1];STUDY=ROOT/'candidateStudy';P=STUDY/'data/processed'
def main():
    initial=json.loads((P/'component_tolerance_allowance_only.json').read_text())
    stagnation=json.loads((P/'component_tolerance.json').read_text())
    current=json.loads((P/'component_tolerance_cap.json').read_text())
    regimes=json.loads((P/'cv_chemistry_regimes.json').read_text())
    lines=['# Conservative energy Newton: component scale and stagnation controls','',
           'The cold ten-atmosphere Cv/G control fails the fixed absolute stopping',
           'cutoff in its original iteration budget. All old-rule failures remain',
           'retained. A separate executable tests three stopping policies.',
           'This is established numerical stopping practice, IMPLEMENTATION_ONLY.','',
           'The first allowance-only rule accepts |r_i| <= 5e-18 + 64 eps S_i.',
           'S includes absolute time-inventory and individual matrix contribution',
           'magnitudes before cancellation. It completes the cold case, but stops',
           'earlier in warm/hot cases and increases drift. Exact period-one/two',
           'h,T,p repetition preserves warm controls but fails to complete cold.',
           'The final control retains the old cutoff throughout the solve and',
           'allows a component-bounded residual only at the original iteration',
           'cap. This is a residual fallback, not a certified accuracy bound.',
           'See candidates/componentEnergyTolerance.md for the pre-test derivations.','',
           '## Broader Cv source regimes using the original G cutoff','',
           '| Regime | Method | Status | T difference (K) | E drift (relative) |',
           '|---|---|---|---:|---:|']
    for r in regimes:
        if 'error' in r:lines.append(f"| {r['regime']} | {r['mode']} | failed / retained | — | — |")
        else:lines.append(f"| {r['regime']} | {r['mode']} | completed | {r['errors']['T']['Linf']:.7e} | {r['signedEnergyDrift']:+.7e} |")
    lines+=['','The cold 950 K/10 atm independent reference remains in induction:',
            'T changes by 5.87e-5 K over 240 us. Hot 1500 K/1 atm burns to about',
            '3003.21277 K. Both use the unchanged legacy-matched H2 mechanism,',
            'clone=False, verified density/molecular weights and two reference',
            'tolerances. These source-only checks do not validate flame structure.','',
            '## Stopping-rule replays','',
            '| Policy | Case | Flag | Status | T difference (K) | E drift (relative) | Max accepted residual (J) | Max scaled residual | Accepted above old cutoff |',
            '|---|---|---|---|---:|---:|---:|---:|---:|']
    for label,data in [('allowance-only',initial),('exact-cycle',stagnation),('cap-fallback',current)]:
        for r in data['records']:
            flag='on' if r['componentEnergyTolerance'] else 'off'
            if 'error' in r:
                lines.append(f"| {label} | {r['name']} | {flag} | failed / retained | — | — | — | — | — |")
            else:
                t=r.get('errors',{}).get('T',{}).get('Linf')
                text='—' if t is None else f'{t:.7e}'
                count=r.get('acceptedAboveOldCutoff',r.get('acceptedAboveOldCutoffRankSteps'))
                lines.append(f"| {label} | {r['name']} | {flag} | completed | {text} | {r['signedEnergyDrift']:+.7e} | {r['maxAcceptedEnergyResidual']:.7e} | {r['maxAcceptedScaledResidual']:.7e} | {count} |")
    lines+=['','Mixture-wave T differences are analytic transport errors; homogeneous',
            'ones are independent Cantera endpoint differences. F has no resolved',
            'field reference and is not assigned an exact-error number.','',
            '| Policy | Pair | T Linf (K) | p Linf (Pa) | Max of all field Linf values |',
            '|---|---|---:|---:|---:|']
    for label,data in [('allowance-only',initial),('exact-cycle',stagnation),('cap-fallback',current)]:
        for r in data['comparisons']:
            fields=r['fields'];lines.append(f"| {label} | {r['kind']} | {fields['T']['Linf']:.7e} | {fields['p']['Linf']:.7e} | {max(v['Linf'] for v in fields.values()):.7e} |")
    bounds=json.loads((P/'component_tolerance_bounds.json').read_text())
    lines+=['','## Accepted residual accumulation','',
            'Each accepted rank/time is counted exactly once. Weighting the recorded',
            'global maximum by each rank cell count bounds the sum of absolute',
            'assembled residuals over cells and steps. A second sum uses the rank',
            'maximum component allowance. Neither sum bounds solution error.','',
            '| Cold policy | Inventory change magnitude (J) | Residual magnitude upper sum (J) | Allowance upper sum (J) |',
            '|---|---:|---:|---:|']
    for r in bounds['records']:
        if 'coldHighPressure' in r['name']:
            lines.append(f"| {r['policy']} | {r['absoluteInventoryChange']:.7e} | {r['accumulatedResidualMagnitudeUpperSum']:.7e} | {r['accumulatedComponentAllowanceUpperSum']:.7e} |")
    lines+=['','## Interpretation and limits','',
            'The initial successful allowance-only replay does not justify relaxing',
            'every Newton solve. The failed exact-cycle explanation remains',
            'retained. Cap fallback preserves the old convergence checks before',
            'the iteration limit; the independent inventories, EOS',
            'and reference errors remain the scientific gates. A conservative',
            'rounding allowance is not a certified thermodynamic or truncation',
            'error bound, and may condition differently under an energy gauge.','',
            'Source snapshots/executable hashes identify each policy per case.',
            'The installed solvers and original candidates remain unchanged.',
            'Logical replays overlapped separate logical source screens; all their',
            'wall times are excluded from performance comparisons. Added component',
            'operators, state copies and MPI reductions have a cost; no low-cost',
            'or numerical-method novelty claim follows.','']
    (ROOT/'docs/component_tolerance_results.md').write_text('\n'.join(lines))
    print('Component report',len(initial['records']),'initial',len(current['records']),'current')
if __name__=='__main__':main()
