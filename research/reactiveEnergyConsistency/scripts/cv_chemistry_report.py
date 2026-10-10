"""Report retained corrected chemistry controls and their limited inference."""
from pathlib import Path
import json,math
from roundoff_screen import compare
ROOT=Path(__file__).resolve().parents[1];STUDY=ROOT/'candidateStudy';PROCESSED=STUDY/'data/processed'
def main():
    data=json.loads((PROCESSED/'cv_chemistry.json').read_text());rows=data['records']
    reference=json.loads((PROCESSED/'cantera_reference.json').read_text())
    probe=json.loads((PROCESSED/'cv_chemistry_probe.json').read_text())
    reacting=json.loads((PROCESSED/'cv_reacting_screen.json').read_text()) if (PROCESSED/'cv_reacting_screen.json').exists() else []
    reactingComparisons=[]
    for dt in sorted({r['dt'] for r in reacting}):
        for mode in ['none','conservativeState']:
            pair=[next(r for r in reacting if r['dt']==dt and r['mode']==mode and r['odeThermalPath']==path) for path in ['constantPressure','constantVolume']]
            if all('error' not in r for r in pair):
                reactingComparisons.append(dict(dt=dt,mode=mode,a=pair[0]['name'],b=pair[1]['name'],
                                                fields=compare(STUDY/'data/raw'/pair[0]['name'],STUDY/'data/raw'/pair[1]['name'])))
    orders=[]
    for mode in ['none','conservativeState']:
        seq=sorted([r for r in rows if r['odeThermalPath']=='constantVolume' and r['odeRelativeTolerance']==1e-10 and r['mode']==mode],key=lambda r:r['dt'],reverse=True)
        for a,b in zip(seq,seq[1:]):
            orders.append(dict(mode=mode,coarseDt=a['dt'],fineDt=b['dt'],observedTemperatureOrder=math.log(a['errors']['T']['Linf']/b['errors']['T']['Linf'],2),
                               resolvedOrderEvidence=mode=='none',scope='CV+G endpoint differences are below the measured independent-reference tolerance contrast; their ratios are not resolved accuracy-order estimates.'))
    payload=dict(records=rows,orders=orders,reacting=reacting,reactingComparisons=reactingComparisons,probe=probe,supersededCases=[r['name'] for r in data['superseded']],
                 referenceTemperatureToleranceContrast=reference['toleranceEndpointDifference']['T'],scope='Known source thermal-path control with corrected autonomous ODE callback; no new method, resolved spatial reference, higher-order CFD, or comparative performance claim.')
    (PROCESSED/'cv_chemistry_analysis.json').write_text(json.dumps(payload,indent=2)+'\n')
    lines=['# Native chemistry thermal-path controls','',
           'The corrected constant-volume source and conservative CFD energy closure',
           'are tested separately. Constant-pressure and constant-volume RHS controls',
           'use the same FD Jacobian, native Rosenbrock34 solver and ODE tolerances.',
           'These are established chemistry equations, not a new numerical method.','',
           'The first adapter incorrectly returned the RHS in the ODESystem explicit',
           'time-derivative vector. Its ten homogeneous runs and interrupted F screen',
           'are retained as superseded evidence; they are excluded from current claims.',
           'Corrected cases carry dfdt0. The native probe checks the callback itself',
           'and continuous identities at 600–3000 K in both thermal paths.','',
           f"Probe: {len(probe)} states; explicit time derivative exactly zero; maximum",
           f"directional Jacobian discrepancy {max(r['directionalJacobianRelativeError'] for r in probe):.7e}",
           '(predeclared limit 1e-4). Continuous scaled mass/thermal/pressure residuals',
           f"are below {max(max(r[k] for k in ['massResidualRelative','thermalResidualRelative','pressureResidualRelative']) for r in probe):.7e}",
           '(predeclared limit 1e-12). This verifies the scoped interface, not global',
           'positivity, entropy stability or chemistry integration order.','',
           '## Homogeneous fixed-volume control','',
           'Thin 8-cell H2/air domain, 1100 K, p=101325 Pa, U=0, As=0, TF=240 us.',
           'All rows use atol=1e-16. The reference matches legacy molecular weights,',
           'NASA conventions and native reaction-rate conversions; reactor clone is',
           'disabled and the initialized phase identity is asserted. Strict reference',
           f"T={reference['records'][-1]['end']['T']:.12f} K; its rtol contrast gives",
           f"a temperature difference of {reference['toleranceEndpointDifference']['T']:.7e} K.",
           'Agreement below that contrast does not determine true endpoint error.','',
           '| Source path | CFD closure | dt (us) | ODE rtol | T Linf (K) | p Linf (Pa) | E drift (relative) | Source E change (relative, max) | Source calls |',
           '|---|---|---:|---:|---:|---:|---:|---:|---:|']
    for r in sorted(rows,key=lambda r:(r['odeThermalPath'],r['mode'],-r['dt'],r['odeRelativeTolerance'])):
        lines.append(f"| {r['odeThermalPath']} | {r['mode']} | {r['dt']*1e6:g} | {r['odeRelativeTolerance']:g} | {r['errors']['T']['Linf']:.8e} | {r['errors']['p']['Linf']:.8e} | {r['signedEnergyDrift']:+.8e} | {r['maxSourceRelativeEnergyChange']:.8e} | {r['sourceCalls']} |")
    lines+=['','Constant-pressure source internal-energy change is expected: that',
            'RHS is not the fixed-volume invariant. CPFD denotes the installed',
            'fixed-p, Cp/Ha thermal RHS at the same concentration/source abstraction;',
            'it is not a physically expanding constant-pressure reactor. Its final CFD',
            'inventory does not retroactively change temperatures sampled during',
            'reaction integration. Constant-volume source alone still does not',
            'supply the CFD pressure/species/energy conservation identity.','',
            'For the constant-volume source without CFD closure, observed T orders:',
            ', '.join(f"{r['observedTemperatureOrder']:.6f}" for r in orders if r['mode']=='none')+'.',
            'For G, ratios below the reference tolerance contrast are deliberately',
            'not promoted as time-order evidence. Homogeneous transport vanishes;',
            'this test supplies no higher-order reacting-flow theorem.','',
            '## Spatial reacting screen','']
    if reacting:
        lines+=['Same 256-cell original periodic F kernel, four ranks, TF=240 us,',
                'zero transport. CPFD/CV change only the declared thermal path at',
                'matched rtol=1e-10/atol=1e-16. Endpoint trajectories are not exact',
                'errors. Local ledgers and independent inventories remain enabled.','',
                '| Source | Closure | dt (us) | Status | T mean (K) | E drift (%) | Source E change (relative, max) | Cell closure (J) |',
                '|---|---|---:|---|---:|---:|---:|---:|']
        for r in reacting:
            if 'error' in r:
                lines.append(f"| {r['odeThermalPath']} | {r['mode']} | {r['dt']*1e6:g} | failed / retained | — | — | — | — |")
            else:lines.append(f"| {r['odeThermalPath']} | {r['mode']} | {r['dt']*1e6:g} | completed | {r['meanTemperature']:.8f} | {100*r['signedEnergyDrift']:+.8g} | {r['maxSourceRelativeEnergyChange']:.7e} | {r['maxCellClosure']:.7e} |")
        lines+=['','Both conservative paths quench at dt2 us (mean T about 727 K)',
                'and burn at dt1 us (about 2845 K), while conserving the recorded',
                'inventory. Changing the source thermal path therefore does not',
                'remove the coarse-step instability/accuracy gate. CV without G',
                'retains substantial CFD energy loss; source conservation alone',
                'cannot close the post-pressure thermochemical pair.','',
                '| dt (us) | Closure | CPFD/CV T L1 (K) | T Linf (K) | U L1 (m/s) |',
                '|---:|---|---:|---:|---:|']
        for r in reactingComparisons:
            f=r['fields'];lines.append(f"| {r['dt']*1e6:g} | {r['mode']} | {f['T']['L1']:.7e} | {f['T']['Linf']:.7e} | {f['U']['L1']:.7e} |")
        lines+=['','These are matched algorithm contrasts, not reference errors.',
                'No source-path ranking or reacting convergence order is inferred.',
                'The screen wall times are excluded from performance claims because',
                'logical stopping-rule replays overlapped parts of this campaign.','',
                'The predeclared 1e-10 relative source-energy gate fails in three',
                'of four spatial Cv configurations. Their maximum source discrepancy',
                'is about 3e-7, despite conservative final CFD inventory. The branch',
                'audit and independent direct-source controls in',
                '[cv_source_invariant_results.md](cv_source_invariant_results.md)',
                'isolate a legacy NASA midpoint jump in the direct controls.',
                'Some baseline non-straddling failures remain; not every spatial',
                'discrepancy is assigned to that mechanism. The physical gate stays',
                'failed, and its threshold is not relaxed after observing the result.']
    else:lines+=['Not yet completed; no spatial conclusion is asserted.']
    lines+=['','## Provenance and decision','',
            'Per-case experiment.json identifies immutable source snapshots, chemistry',
            'library and executable hashes; raw inputs, source traces and failures are',
            'retained. cv_chemistry_analysis.json includes all current records and a',
            'separate superseded-case list. The finite-difference chemistry Jacobian',
            'is a verification implementation; single wall times do not establish a',
            'low-cost advantage. Established Cv physics remains IMPLEMENTATION_ONLY.','',
            '[Cantera IdealGasReactor](https://cantera.org/stable/reference/reactors/ideal-gas-reactor.html)',
            'gives the closed-volume species/internal-energy equations. This port',
            'does not pass a numerical-method novelty gate. Full reacting reference',
            'uncertainty, pressure equilibrium, general boundaries, restart and',
            'performance gates remain separate requirements.','']
    (ROOT/'docs/cv_chemistry_results.md').write_text('\n'.join(lines))
    print('Corrected chemistry records',len(rows),'superseded',len(data['superseded']),'reacting screens',len(reacting))
if __name__=='__main__':main()
