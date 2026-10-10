# Native chemistry thermal-path controls

The corrected constant-volume source and conservative CFD energy closure
are tested separately. Constant-pressure and constant-volume RHS controls
use the same FD Jacobian, native Rosenbrock34 solver and ODE tolerances.
These are established chemistry equations, not a new numerical method.

The first adapter incorrectly returned the RHS in the ODESystem explicit
time-derivative vector. Its ten homogeneous runs and interrupted F screen
are retained as superseded evidence; they are excluded from current claims.
Corrected cases carry dfdt0. The native probe checks the callback itself
and continuous identities at 600–3000 K in both thermal paths.

Probe: 16 states; explicit time derivative exactly zero; maximum
directional Jacobian discrepancy 7.6974051e-08
(predeclared limit 1e-4). Continuous scaled mass/thermal/pressure residuals
are below 2.2247759e-16
(predeclared limit 1e-12). This verifies the scoped interface, not global
positivity, entropy stability or chemistry integration order.

## Homogeneous fixed-volume control

Thin 8-cell H2/air domain, 1100 K, p=101325 Pa, U=0, As=0, TF=240 us.
All rows use atol=1e-16. The reference matches legacy molecular weights,
NASA conventions and native reaction-rate conversions; reactor clone is
disabled and the initialized phase identity is asserted. Strict reference
T=2928.259905382967 K; its rtol contrast gives
a temperature difference of 2.4948804e-08 K.
Agreement below that contrast does not determine true endpoint error.

| Source path | CFD closure | dt (us) | ODE rtol | T Linf (K) | p Linf (Pa) | E drift (relative) | Source E change (relative, max) | Source calls |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| constantPressure | conservativeState | 1 | 1e-10 | 8.58425389e-04 | 5.64843885e-02 | +7.94143265e-15 | 4.73447396e-02 | 1920 |
| constantVolume | conservativeState | 1 | 1e-12 | 6.74936018e-09 | 5.34433639e-07 | +2.63453877e-14 | 3.80671803e-14 | 1920 |
| constantVolume | conservativeState | 1 | 1e-10 | 1.06574589e-08 | 7.90343620e-07 | +8.19354162e-15 | 2.69008074e-14 | 1920 |
| constantVolume | conservativeState | 0.5 | 1e-10 | 7.40828909e-09 | 5.77449100e-07 | +3.39086569e-14 | 2.57164951e-14 | 3840 |
| constantVolume | conservativeState | 0.25 | 1e-10 | 6.14318196e-09 | 4.93047992e-07 | +2.40764069e-14 | 1.70879342e-14 | 7680 |
| constantVolume | conservativeState | 0.125 | 1e-10 | 4.11728251e-09 | 3.63332219e-07 | +9.69359001e-14 | 1.25198726e-14 | 15360 |
| constantVolume | none | 1 | 1e-10 | 1.97068203e-03 | 1.21845870e-01 | -8.78540304e-07 | 3.62297503e-14 | 1920 |
| constantVolume | none | 0.5 | 1e-10 | 8.85240977e-04 | 5.43143929e-02 | -4.43003065e-07 | 2.43031983e-14 | 3840 |
| constantVolume | none | 0.25 | 1e-10 | 4.14377529e-04 | 2.52977792e-02 | -2.21971637e-07 | 1.88609030e-14 | 7680 |
| constantVolume | none | 0.125 | 1e-10 | 1.99689666e-04 | 1.21558387e-02 | -1.11038925e-07 | 1.56105017e-14 | 15360 |

Constant-pressure source internal-energy change is expected: that
RHS is not the fixed-volume invariant. CPFD denotes the installed
fixed-p, Cp/Ha thermal RHS at the same concentration/source abstraction;
it is not a physically expanding constant-pressure reactor. Its final CFD
inventory does not retroactively change temperatures sampled during
reaction integration. Constant-volume source alone still does not
supply the CFD pressure/species/energy conservation identity.

For the constant-volume source without CFD closure, observed T orders:
1.154553, 1.095124, 1.053186.
For G, ratios below the reference tolerance contrast are deliberately
not promoted as time-order evidence. Homogeneous transport vanishes;
this test supplies no higher-order reacting-flow theorem.

## Spatial reacting screen

Same 256-cell original periodic F kernel, four ranks, TF=240 us,
zero transport. CPFD/CV change only the declared thermal path at
matched rtol=1e-10/atol=1e-16. Endpoint trajectories are not exact
errors. Local ledgers and independent inventories remain enabled.

| Source | Closure | dt (us) | Status | T mean (K) | E drift (%) | Source E change (relative, max) | Cell closure (J) |
|---|---|---:|---|---:|---:|---:|---:|
| constantPressure | none | 2 | completed | 2828.43587910 | -17.385187 | 1.0336529e+02 | 8.3348042e-19 |
| constantVolume | none | 2 | completed | 2822.85169844 | -23.137932 | 2.7609483e-07 | 8.0722240e-19 |
| constantPressure | conservativeState | 2 | completed | 726.76474032 | -3.96585e-14 | 2.3533341e-03 | 1.9552730e-19 |
| constantVolume | conservativeState | 2 | completed | 727.82278817 | -3.96585e-14 | 9.7786122e-15 | 2.0598782e-19 |
| constantPressure | none | 1 | completed | 2846.04687263 | +0.89289911 | 3.5535404e+01 | 8.1892204e-19 |
| constantVolume | none | 1 | completed | 2843.42861983 | -1.9911425 | 2.9525556e-07 | 7.0849012e-19 |
| constantPressure | conservativeState | 1 | completed | 2844.69108749 | +4.7193615e-12 | 6.6678448e+00 | 1.6156386e-17 |
| constantVolume | conservativeState | 1 | completed | 2844.74155732 | +1.665657e-12 | 3.2829295e-07 | 1.5639335e-17 |

Both conservative paths quench at dt2 us (mean T about 727 K)
and burn at dt1 us (about 2845 K), while conserving the recorded
inventory. Changing the source thermal path therefore does not
remove the coarse-step instability/accuracy gate. CV without G
retains substantial CFD energy loss; source conservation alone
cannot close the post-pressure thermochemical pair.

| dt (us) | Closure | CPFD/CV T L1 (K) | T Linf (K) | U L1 (m/s) |
|---:|---|---:|---:|---:|
| 1 | none | 2.6182528e+00 | 4.7073516e+00 | 1.2053574e+00 |
| 1 | conservativeState | 5.3387492e-01 | 9.9141424e-01 | 2.4985552e-01 |
| 2 | none | 8.2455629e+00 | 1.8100519e+01 | 6.7156221e+00 |
| 2 | conservativeState | 1.0580479e+00 | 2.1546306e+00 | 7.1494124e-03 |

These are matched algorithm contrasts, not reference errors.
No source-path ranking or reacting convergence order is inferred.
The screen wall times are excluded from performance claims because
logical stopping-rule replays overlapped parts of this campaign.

The predeclared 1e-10 relative source-energy gate fails in three
of four spatial Cv configurations. Their maximum source discrepancy
is about 3e-7, despite conservative final CFD inventory. The branch
audit and independent direct-source controls in
[cv_source_invariant_results.md](cv_source_invariant_results.md)
isolate a legacy NASA midpoint jump in the direct controls.
Some baseline non-straddling failures remain; not every spatial
discrepancy is assigned to that mechanism. The physical gate stays
failed, and its threshold is not relaxed after observing the result.

## Provenance and decision

Per-case experiment.json identifies immutable source snapshots, chemistry
library and executable hashes; raw inputs, source traces and failures are
retained. cv_chemistry_analysis.json includes all current records and a
separate superseded-case list. The finite-difference chemistry Jacobian
is a verification implementation; single wall times do not establish a
low-cost advantage. Established Cv physics remains IMPLEMENTATION_ONLY.

[Cantera IdealGasReactor](https://cantera.org/stable/reference/reactors/ideal-gas-reactor.html)
gives the closed-volume species/internal-energy equations. This port
does not pass a numerical-method novelty gate. Full reacting reference
uncertainty, pressure equilibrium, general boundaries, restart and
performance gates remain separate requirements.
