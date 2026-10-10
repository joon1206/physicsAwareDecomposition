# Current numerical-method decision and bounded negative evidence

No candidate has passed all publication gates. Compatible species/absolute-
energy residuals close the tested inventory at modest measured G cost, but
establish neither novelty nor resolved reacting accuracy. This is a scoped
research decision, not a proof that all possible future CFD contributions are
exhausted. The unqualified research objective remains open.

The frozen baseline loses 17.3886598% total energy. Its exact discrete budget
and independent inventory isolate V delta-rho (hs+hc), with separate pressure/
kinetic contributions and full species/chemistry terms. The 499 published
actionStudy files and accepted first audit remain frozen.

At fixed final rho,p,Y the perfect-gas EOS fixes T. An energy-only change cannot
repair rhoY transport. Formation-only compensation lacks elemental-reference
covariance. These are mathematical limits on specified cheap correction
classes; rejected formulations are not generalized into all conceivable methods.

| Family / pivot | Evidence and decision |
|---|---|
| Local internal-energy remap | F energy increases 26.61%/56.42%, Mix loses 25.52%; pressure/momentum/gauge failures. Reject tested projection. |
| Local/deferred energy source without species response | Species inventory/final-flux residual unchanged by energy alone. Reject general joint-conservation claim. |
| Scalar post-pressure density corrector | Reacting capacity/ODE failure; Mix loses 13.18%. Reject tested formulation. |
| Midpoint product identity | Supplies no coupled endpoint closure; established principle. No independent method. |
| Isolated formation correction | Full gauge covariance requires elemental/species residuals. Reject isolated reference-invariant claim. |
| Species remap alone | Mix elements/EOS close; F energy worsens to 58.26%/34.30%. Retain component, reject alone. |
| G compatible species/absolute-energy residual | Conservation, first-order exact waves; median cost 1.048x baseline. Novelty and reacting accuracy open; coarse quenching remains. |
| Frozen-source pressure/species/energy block | Smaller momentum mismatch; cost 1.391x, collectives 7.35x. Known coupling; frozen predictor and accuracy/cost gates open. |
| Inexact block | Measured tolerance/momentum/cost tradeoff; coarse quenching remains. Comparator, not an accuracy controller. |
| Reordering / extra pressure or outer iteration | Selected extra-outer variant worsens drift/cost; generic procedures are prior art. Does not reject fully converged PIMPLE. |
| Mixture pressure-equilibrium/remapping | Actual NASA mixing changes pressure while conserving energy. Conditional one-state common-weight obstruction, no new equilibrium-preserving method. |
| Compatible sensible species diffusion | Known physical flux removes exact unequal-Cp temperature floor. Original density defect and strict MPI field-equivalence gate remain. |
| Cv chemistry path | Homogeneous source-path error falls inside reference contrast. Known physics; both spatial conservative paths still quench at dt2 us and burn at dt1 us. |
| Component energy stopping | Cap fallback completes cold and preserves completing fields; failed earlier policies retained. Implementation robustness, not an error bound. |
| Taylor thermal-path compensation | Smooth second-order gain; stiff negativity; positive common limiter worsens error 14.72x. Reject general admissibility/accuracy claims. |
| Element-invariant elimination | Conditional exact equivalence; variable elements/unequal diffusion fail; general reduction is prior art. No native cost novelty. |
| Energy/momentum/source-defect controller | Exact conservative contact wave has zero indicators and finite temperature error. Transport/truncation information is necessary. |
| NASA branch source/inversion | Native/Cantera crossing energy jumps; actual-data missing/multiple roots with positive branch Cv. Data-validation boundary, not a new correction. |

Precise derivations, acceptance criteria, failures and primary literature are
in novelty_matrix.md, claim_strength.md, candidate_space_constraints.md and
candidates/*.md. Implementation size or a passed evidence check is not novelty.

Matched Cantera preserves legacy weights, standard-pressure/Arrhenius
conventions, clone=False and phase identity. Source-only agreement does not
validate transport. Exact waves establish first-order errors and expose
pressure/diffusion compatibility. Finest central/HLLC kernel fields differ by
T L1=111.04 K; mesh differences remain large. These numerical trajectories
cannot supply exact reacting accuracy rankings. Original F transport is zero;
tagged shared-Sutherland controls are not physical H2 flame validation.

The prior three-trial timing matrix is sequential/rotated. Later logical
chemistry/stopping campaigns overlap and are excluded from cost claims. The
finite-difference chemistry Jacobian is a verification port, with no verified
low-cost advantage. Raw inputs/snapshots and the reproducibility manifest
identify the executed versions and distinguish execution from scientific gates.

Three spatial Cv configurations fail the unchanged 1e-10 source-energy gate:
568 straddling and 15 other failed calls. A direct crossing retains about
1.14605e-7 energy change under tolerance tightening; independent Cantera
reproduces it with unchanged data. Fine crossing-concentration diagnostics
account for the direct change through the NASA energy jump. Other spatial
contributions remain incompletely attributed. The data also admits a target
inside a 0.07407165 J/kg gap and two pure-N2 roots across a 0.01588887 J/kg
overlap. These small effects do not explain the original 17% CFD loss.
See cv_source_invariant_results.md and candidates/thermoBranchInversion.md.

The strongest evidence-supported broader question is an operator-aware
transport/source/coupling error controller or a demonstrably different
pressure/species/energy response approximation. Its principles overlap
established coupling/error estimation/source forcing; no precise new
approximation has been identified. Generic Schur elimination, shared operator
reduction, a Cv port or polynomial repair cannot supply novelty by themselves.

Remaining requirements include an explicitly matched continuous thermodynamic
model, resolved reacting references across nonzero transport regimes,
reference-invariant local estimates, applicable boundary/restart/MPI
equivalence and uncontended accuracy/cost trials. This finite review cannot
honestly certify universal exhaustion or a positive publication decision.
The project is not marked complete.

## 2026-10-07 — clean-data continuation and bounded decision

The continuous-thermo prerequisite above is now addressed by the matched
original/HS/CpHS H2 campaign and original/CpHS GRI campaign, with unchanged
kinetic input, fields, transport and discretization within each pair. The
thermodynamic intervention can change equilibrium-derived reverse rates;
its trajectory interaction is measured rather than declared absent.

The original density/enthalpy/formation defect survives. H2 native dt2-us
drift changes from -17.3886598% to -17.3900272% under CpHS; GRI's corresponding
drift remains about +7.2508%. Direct source breakpoint floors are removed,
while some continuous-data spatial source calls still fail the original
1e-10 invariant criterion. All uncorrected eight-term budgets close, and
the conservative-state identity explicitly includes its post-state terms.
See clean_vs_legacy_results.md for source/pressure/density/species/kinetic
attribution and the measured two-factor interactions.

The immediate five-family continuation is rejected at decisive gates:

| Family | Decision | Evidence |
|---|---|---|
| Valid-data scalar invariant projection | REJECT generic novelty and unconditional trajectory dominance | 48 controls, 40 eligible, 38 endpoint gate passes, 25 observed T-error increases; 22 exceed twice the stricter-reference contrast. No species accuracy correction. |
| Finite species/formation transfer | REJECT as new native method | Native integrated RR is already the finite update; exact CV sensible-h transfer also needs delta p. |
| Chemistry/CFD transition-map layer | REJECT generic architecture novelty and CFD sufficiency | Known Cantera/Pele invariant integration; independent post-map counterexample and actual CFD density budgets. |
| Thermochemical risk certification | REJECT generic linter/predictor headline | Multi-mechanism event identity uses observed crossing weights; prospective source/CFD prediction is unvalidated. Mech Checker already establishes numerical consequences. |
| Continuous reconstruction | REJECT generic repair novelty and unverified physical-accuracy claim | Prior constrained fitting covers the operation; original source data absent; continuity controls leave CFD defect. |

The reasonable implementation-level variants of these five classes and the
previous cheap coupling formulations have now reached an evidence-backed
bounded exhaustion decision. The exact boundary and every publication gate
are recorded in continuous_thermo_pivot.md. This satisfies the continuation's
negative-decision route; it does not exhaust all future numerical analysis or
claim a publishable method. A full constrained/history-aware integrator,
prospective operating-state predictor or original-data reconstruction would
require a precise new contribution, not the generic known formulations tested
here. No invariant-only success is promoted.

The stronger pivot is a distinct pressure/species/energy operator response
or error estimate that includes transport truncation and chemistry sensitivity
to finite transport forcing, validated with resolved independent reacting
fields. Continuous thermo is now a baseline. The zero-indicator exact-wave
counterexample proves why transport information is necessary; the dt-dependent
quenching/burning contrast proves why conservation cannot replace reacting
accuracy. Generic source forcing, tangent propagation and Schur reduction
remain prior art. Only a specific justified approximation with an improved
resolved accuracy/cost frontier would advance the numerical-method objective.

The modern Alzueta source controls generalize the thermochemistry audit;
native full-flow import remains unavailable because v2012 lacks PLOG support.
The parser failures are retained and are not chemical-method failures.
Concurrent continuation walls are excluded from new cost claims. The previous
historical 38 evidence criteria remain unchanged; new phase checks and a
supplemental manifest explicitly retain continuous-data scientific failures.
