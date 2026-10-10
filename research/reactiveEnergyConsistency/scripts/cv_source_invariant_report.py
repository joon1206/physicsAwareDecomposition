"""Report failed source-energy gate without relaxing its declared threshold."""
from pathlib import Path
import json
ROOT=Path(__file__).resolve().parents[1];P=ROOT/'candidateStudy/data/processed'

def main():
    audit=json.loads((P/'cv_source_invariant_audit.json').read_text())
    native=json.loads((P/'cv_branch_probe.json').read_text())
    independent=json.loads((P/'cantera_branch_probe.json').read_text())
    inversion=json.loads((P/'thermo_branch_inversion.json').read_text())
    lines=['# Source energy invariance and legacy NASA branch discontinuity','',
           'The corrected Cv source satisfies its continuous energy identity on',
           'smooth thermodynamic branches. The original 1e-10 relative accepted-source',
           'energy gate nevertheless fails in three of four spatial Cv cases.',
           'Final CFD energy conservation does not make this source gate pass.',
           'The original threshold and all failed traces remain retained.','',
           '## Spatial endpoint audit','',
           '| Closure | dt (us) | Calls | Calls straddling 1000 K | Straddling failures | Other failures | Max relative source E change |',
           '|---|---:|---:|---:|---:|---:|---:|']
    for r in audit['records']:
        g={x['endpointStraddlesMidpoint']:x for x in r['categories']}
        lines.append(f"| {r['mode']} | {r['dt']*1e6:g} | {r['sourceCalls']} | {g[True]['sourceCalls']} | {g[True]['invariantFailures']} | {g[False]['invariantFailures']} | {max(x['maxRelativeEnergyChange'] for x in r['categories']):.8e} |")
    lines+=['','All 568 straddling calls exceed the unchanged gate. The 15 other',
            'baseline failures are also retained; endpoint non-straddling does not',
            'exclude an internal excursion, and no complete cause is asserted for',
            'those calls. The spatial trace lacks crossing concentrations, so its',
            'energy changes are not retrospectively identified as exact branch jumps.','',
            '## Independent thermodynamic coefficients','',
            '| Species | High-minus-low molar enthalpy at 1000 K (J/kmol) | Specific jump (J/kg) |',
            '|---|---:|---:|']
    for r in audit['thermo']:lines.append(f"| {r['species']} | {r['enthalpyJumpMolar']:+.9g} | {r['enthalpyJumpSpecific']:+.9g} |")
    lines+=['','The perfect-gas R*T term is continuous, so internal energy has the same',
            'branch jump. On each smooth branch, dE/dt=0 follows from the Cv RHS;',
            'a discontinuous polynomial energy includes an additional signed jump',
            'sum_s c_s Delta h_s. The smooth-branch RHS alone does not supply it.','',
            '## Direct native and independent source controls','',
            'p=101325 Pa; Y_H2=.0283, Y_O2=.225, Y_H=Y_OH=.0001, N2=.7465;',
            'TF=10 us; unchanged legacy mechanism, matched molecular weights and',
            'constants. Native Rosenbrock34 is compared with independent Cantera',
            'IdealGasReactor/BDF, clone=False. The native probe also subdivides',
            'the source into 1000 equal diagnostic intervals, interpolating',
            'concentrations at the detected switch. This is an approximate jump',
            'diagnostic, not an event-exact integrator or new CFD method.','',
            '| Initial T (K) | rtol | Native E change (relative) | Jump-subtracted native remainder (relative) | Cantera E drift (relative) | Native/Cantera T difference (K) |',
            '|---:|---:|---:|---:|---:|---:|']
    for case in independent:
        for ct in case['records']:
            n=next(r for r in native if r['Tinitial']==case['Tinitial'] and r['chunks']==1000 and r['odeRelativeTolerance']==ct['rtol'])
            diff=next(r for r in ct['comparisons'] if r['chunks']==1000)
            lines.append(f"| {case['Tinitial']:g} | {ct['rtol']:g} | {n['relativeEnergyChange']:.8e} | {n['relativeJumpUnexplainedEnergy']:.8e} | {ct['end']['energyDrift']:+.8e} | {diff['nativeTemperatureDifference']:.8e} |")
    lines+=['','The crossing energy change remains about 1.14605e-7 as the native ODE',
            'tolerance tightens. At rtol1e-10/1e-12 the fine diagnostic jump estimate',
            'leaves less than 1.7e-14 relative unexplained energy. Above-branch',
            'native controls stay below 1.5e-13. Independent Cantera retains the',
            'same positive crossing change; the strict native/Cantera temperature',
            'difference there is below 3.3e-9 K. Molar jumps from native properties',
            'and independently evaluated NASA coefficients agree within 5.72e-8',
            'J/kmol. This isolates the data/RHS compatibility limitation in these',
            'direct controls; it is not an OpenFOAM-only invariant failure.','',
            '![Direct source branch controls](../figures/candidates/chemistry_branch_invariant.png)','',
            '[Exported PDF figure](../figures/candidates/chemistry_branch_invariant.pdf)','',
            '## Conservative inversion counterexamples','',
            f"Actual-data balanced H2/air has an admissible conservative target inside a {inversion['gap']['gapWidth']:.8g} J/kg energy gap.",
            'Exact rational natural interval bounds certify positive branch Cv',
            'over 200–5000 K, but no valid temperature root exists for that target.',
            'This is an algebraic possible state, not an integrated reaction path.','',
            f"Pure N2 instead has a {inversion['overlap']['overlapWidth']:.8g} J/kg overlap, with valid roots",
            f"{inversion['overlap']['lowBranchRoot']['T']:.12f} and {inversion['overlap']['highBranchRoot']['T']:.12f} K.",
            'Both branch temperatures, pressures and energies are admissible.',
            'Positive branch Cv does not guarantee global invertibility. See',
            '[the derivation](candidates/thermoBranchInversion.md) and',
            'thermo_branch_inversion.json for certificates and exact inputs.','',
            '## Decision and limits','',
            'Retain the failed spatial source gate. Do not alter accepted thermo',
            'coefficients, replace the source-energy cutoff or declare a conservative',
            'reacting method validated from final inventory alone. The roughly 1e-7',
            'source jump is distinct from the original order-1e-1 CFD density-pair',
            'loss. It does not explain the original loss or remove coarse quenching.','',
            '[Cantera NasaPoly2 validation](https://www.cantera.org/3.2/cxx/d6/de1/NasaPoly2_8cpp_source.html)',
            'already checks midpoint Cp/enthalpy/entropy discontinuities. Warning',
            'thresholds do not enforce exact continuity. Polynomial validation or',
            'repair is an established practice, not a new numerical-method contribution.','',
            'Raw CvBranchProbe and cantera_Branch directories retain source snapshots,',
            'library/executable hashes, exact inputs and trajectories. Processed',
            'cv_source_invariant_audit.json, cv_branch_probe.json and',
            'cantera_branch_probe.json are the table sources. Continuous identity',
            'and homogeneous 1100 K claims remain restricted to their tested branch.','']
    (ROOT/'docs/cv_source_invariant_results.md').write_text('\n'.join(lines))
    print('Source-invariant report:',len(audit['records']),'spatial',len(native),'native direct',sum(len(r['records']) for r in independent),'independent')
if __name__=='__main__':main()
