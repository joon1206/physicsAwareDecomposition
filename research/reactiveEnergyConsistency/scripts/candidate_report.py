"""Generate candidate benchmark tables from executed data, preserving first audit."""
from pathlib import Path
import json,math
ROOT=Path(__file__).resolve().parents[1];STUDY=ROOT/'candidateStudy'
bench=json.loads((STUDY/'data/processed/benchmark_matrix.json').read_text());coupling=json.loads((STUDY/'data/processed/coupling_tolerance.json').read_text())
text=['# Executed candidate benchmark matrix','',
'No method has passed all publication gates. The reacting T/species columns below',
'are differences from a tight block self-refinement trajectory at dt=0.125 us,',
'not independent exact PDE errors. All rows use the same 256-cell F mesh with As=0 (zero physical viscosity/diffusion).',
'The separate inviscid mesh-reference comparison does not replace this reference.','',
'| Configuration | Energy drift (%) | Mass drift | Max element drift | T L1 (K) | T L2 (K) | T Linf (K) | Tmax difference (K) | H2O L1 | Median seconds | Range (s) | Wall ratio | Energy solves | Pressure solves | MPI collectives |',
'|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|---:|---:|---:|---:|']
for r in bench['records']:
    energy=sum(v['solves'] for k,v in r['linearSolvers'].items() if k in ['h','deltaConservativeH','deltaHs','deltaH']);p=r['linearSolvers'].get('p',{}).get('solves',0)
    mpi=str(int(r['MPI']['collectives'])) if 'MPI' in r else 'not measured'
    text.append(f"| {r['label']} | {r['energyDrift']*100:+.6g} | {r['massDrift']:.2e} | {r['maxElementDrift']:.2e} | {r['T_L1']:.4f} | {r['T_L2']:.4f} | {r['T_Linf']:.4f} | {r['TmaxDifference']:.4f} | {r['H2O_L1']:.4g} | {r['wallMedian']:.3f} | {r['wallMin']:.3f}–{r['wallMax']:.3f} | {r['medianWallRatio']:.3f} | {energy} | {p} | {mpi} |")
text+=['',bench['timingScope'],'',bench['MPIScope'],'',
'Original seven configurations used rotated blocks; the same-dt extra-outer',
'configuration used three later sequential trials and is not paired with the',
'earlier baseline. Horizontal figure ranges are observed min/max, not confidence',
'intervals. Energy solver counts include deltaConservativeH. Operation counts',
'come from separately instrumented matching runs; no missing count is inferred.','',
'## Inexact block controls','',
'The following state differences use a tight block at the **same** dt and mesh.',
'They measure coupling-iteration effects, not discretization error. Walls are',
'single trials; the instrumented duplicate is shown only for call counts.','',
'| Case | Pressure tolerance | Mean T (K) | Max momentum mismatch (m/s) | T L1 from same-dt tight block (K) | Energy drift | Single wall (s) | MPI collectives |',
'|---|---:|---:|---:|---:|---:|---:|---:|']
for r in coupling['records']:
    mpi=str(int(r['MPI']['sumRankCounters']['collectives'])) if 'MPI' in r else 'not measured'
    text.append(f"| {r['kind']} dt={r['dt']*1e6:g} us{' instrumentation' if 'MPI' in r else ''} | {r['pressureTolerance']:.0e} | {r['Tmean']:.5f} | {r['momentumMismatch']:.5g} | {r['fieldDifferences']['T']['L1']:.6g} | {r['energyDrift']:.3e} | {r['wallSingleTrial']:.3f} | {mpi} |")
text+=['',
'The 2 us loose-block negative control still quenches to 723.33 K with energy',
'roundoff. Tightening only pressure coupling cannot certify ignition accuracy.',
'The 1e-4 tolerance reduces collectives from 1,479,168 to 684,108 (53.75%)',
'but still uses 3.40 times baseline collectives. The measured velocity mismatch',
'is 0.0671 m/s, and same-dt T L1 difference is 0.02252 K. This useful implementation',
'point has no new equation or verified solution-error controller.','',
'## Accuracy and novelty boundary','',
'Independent corrected Cantera matching verifies first-order homogeneous',
'reacting convergence. Analytic entropy waves verify first-order transport.',
'Detailed-chemistry inviscid spatial trajectories remain resolution sensitive;',
'conservative central nx32/64/128 quench while nx256/512 burn. HLLC burns',
'at coarse meshes but still has substantial mesh and cross-flux profile differences.',
'See inviscid_reference_results.md and inviscid_cross_reference.json for the',
'current mesh/time/cross-flux values. These comparisons cannot yet establish',
'reacting spatial order or a resolved error floor.','',
'Conservative primitive thermodynamic updates, compatible scalar/EOS pressure',
'correction, block iteration and deferred thermochemical coupling all have',
'equation-level prior art. See targeted_prior_art_comparison.md and novelty_matrix.md.',
'No positive numerical-method contribution is asserted from these tables.','',
'Source records: candidateStudy/data/processed/benchmark_matrix.json,',
'coupling_tolerance.json, cantera_reference.json, candidate_reacting_wave.json',
'and inviscid_cross_reference.json. Exact dictionaries, fields, ledgers, logs,',
'C/H snapshots and executable hashes are retained per experiment.']
(ROOT/'docs/benchmark_results.md').write_text('\n'.join(text)+'\n');print(ROOT/'docs/benchmark_results.md')
