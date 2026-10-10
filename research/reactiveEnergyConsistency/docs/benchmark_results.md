# Executed candidate benchmark matrix

No method has passed all publication gates. The reacting T/species columns below
are differences from a tight block self-refinement trajectory at dt=0.125 us,
not independent exact PDE errors. All rows use the same 256-cell F mesh with As=0 (zero physical viscosity/diffusion).
The separate inviscid mesh-reference comparison does not replace this reference.

| Configuration | Energy drift (%) | Mass drift | Max element drift | T L1 (K) | T L2 (K) | T Linf (K) | Tmax difference (K) | H2O L1 | Median seconds | Range (s) | Wall ratio | Energy solves | Pressure solves | MPI collectives |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|---:|---:|---:|---:|
| Base | +0.893299 | -1.12e-16 | 7.46e-15 | 4.6292 | 5.8802 | 11.1535 | 5.0253 | 0.0008316 | 14.577 | 12.846–14.739 | 1.000 | 240 | 240 | 201228 |
| ConservativeState | +5.55219e-12 | 1.12e-15 | 2.10e-15 | 8.4346 | 9.4588 | 16.6711 | 9.5671 | 0.0003202 | 15.277 | 13.011–15.957 | 1.048 | 759 | 240 | 364656 |
| Block | -4.878e-12 | -1.12e-15 | 4.45e-15 | 9.6228 | 10.8178 | 17.5519 | 9.3755 | 0.0005053 | 20.278 | 19.800–21.192 | 1.391 | 2568 | 1757 | 1479168 |
| MorePressure | +0.643219 | 1.23e-15 | 7.78e-15 | 9.5613 | 11.1787 | 20.1091 | 10.1834 | 0.0009892 | 13.344 | 12.676–14.394 | 0.915 | 240 | 480 | 263136 |
| Base dt/2 | -19.6161 | 1.23e-15 | 7.17e-15 | 33.5306 | 40.4222 | 71.8023 | 16.6860 | 0.001789 | 20.487 | 20.260–21.567 | 1.405 | 480 | 480 | not measured |
| Base dt/4 | -28.4734 | -1.10e-14 | 2.10e-14 | 37.8030 | 44.2390 | 69.2756 | 65.9781 | 0.001937 | 32.423 | 30.300–33.527 | 2.224 | 960 | 960 | not measured |
| MoreOuter at dt/4 | +60.1277 | -5.59e-15 | 8.34e-07 | 55.6660 | 59.5388 | 89.6172 | 30.7465 | 0.004971 | 92.025 | 84.567–99.143 | 6.313 | 1920 | 1920 | not measured |
| MoreOuter same dt | +239.118 | 2.24e-16 | 2.50e-02 | 195.1585 | 200.8697 | 260.4811 | 151.1122 | 0.02309 | 49.211 | 44.072–51.883 | 3.376 | 480 | 480 | not measured |

Original seven configurations: three sequential rotated-order four-rank trials. Same-dt MoreOuter: three appended sequential trials, not paired with the earlier baseline. Every=0 equal ledger settings; no concurrent CFD campaign during these timing trials. Ordinary host/background and brief analysis may affect noise. Small n gives no strong significance claim.

Operation counts from separately instrumented matching runs; their contended wall/latency measurements excluded from runtime comparison.

Original seven configurations used rotated blocks; the same-dt extra-outer
configuration used three later sequential trials and is not paired with the
earlier baseline. Horizontal figure ranges are observed min/max, not confidence
intervals. Energy solver counts include deltaConservativeH. Operation counts
come from separately instrumented matching runs; no missing count is inferred.

## Inexact block controls

The following state differences use a tight block at the **same** dt and mesh.
They measure coupling-iteration effects, not discretization error. Walls are
single trials; the instrumented duplicate is shown only for call counts.

| Case | Pressure tolerance | Mean T (K) | Max momentum mismatch (m/s) | T L1 from same-dt tight block (K) | Energy drift | Single wall (s) | MPI collectives |
|---|---:|---:|---:|---:|---:|---:|---:|
| F dt=1 us | 1e-04 | 2844.84679 | 0.067075 | 0.0225165 | -1.745e-14 | 15.399 | not measured |
| F dt=1 us instrumentation | 1e-04 | 2844.84679 | 0.067075 | 0.0225165 | -1.745e-14 | 14.169 | 684108 |
| F dt=1 us | 1e-03 | 2844.84353 | 0.74523 | 0.0793465 | -1.586e-15 | 14.292 | not measured |
| F dt=1 us | 1e-02 | 2844.80669 | 5.4554 | 0.628191 | 5.116e-14 | 14.434 | not measured |
| F dt=2 us | 1e-04 | 723.33043 | 0.075971 | 0.00749931 | -3.173e-15 | 3.756 | not measured |
| Mix dt=2 us | 1e-04 | 799.48363 | 0.041741 | 0.00464247 | 1.043e-15 | 1.422 | not measured |
| Mix dt=2 us | 1e-03 | 799.48363 | 0.15372 | 0.00486755 | -4.695e-15 | 1.395 | not measured |
| Mix dt=2 us | 1e-02 | 799.48363 | 0.15372 | 0.00486755 | -4.695e-15 | 1.565 | not measured |

The 2 us loose-block negative control still quenches to 723.33 K with energy
roundoff. Tightening only pressure coupling cannot certify ignition accuracy.
The 1e-4 tolerance reduces collectives from 1,479,168 to 684,108 (53.75%)
but still uses 3.40 times baseline collectives. The measured velocity mismatch
is 0.0671 m/s, and same-dt T L1 difference is 0.02252 K. This useful implementation
point has no new equation or verified solution-error controller.

## Accuracy and novelty boundary

Independent corrected Cantera matching verifies first-order homogeneous
reacting convergence. Analytic entropy waves verify first-order transport.
Detailed-chemistry inviscid spatial trajectories remain resolution sensitive;
conservative central nx32/64/128 quench while nx256/512 burn. HLLC burns
at coarse meshes but still has substantial mesh and cross-flux profile differences.
See inviscid_reference_results.md and inviscid_cross_reference.json for the
current mesh/time/cross-flux values. These comparisons cannot yet establish
reacting spatial order or a resolved error floor.

Conservative primitive thermodynamic updates, compatible scalar/EOS pressure
correction, block iteration and deferred thermochemical coupling all have
equation-level prior art. See targeted_prior_art_comparison.md and novelty_matrix.md.
No positive numerical-method contribution is asserted from these tables.

Source records: candidateStudy/data/processed/benchmark_matrix.json,
coupling_tolerance.json, cantera_reference.json, candidate_reacting_wave.json
and inviscid_cross_reference.json. Exact dictionaries, fields, ledgers, logs,
C/H snapshots and executable hashes are retained per experiment.
