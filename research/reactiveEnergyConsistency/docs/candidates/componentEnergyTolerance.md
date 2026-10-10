# Component-scaled conservative Newton stopping control

2026-10-06. Derivation before code; IMPLEMENTATION_ONLY. Floating-point-aware
stopping is established numerical practice, not a new conservation algorithm.

## Observation and falsifiable explanation

The additional homogeneous 950 K, ten-atmosphere G+Cv case fails after 20
energy Newton updates. It reports nearby small residuals; the recorded
maximum step residual is 1.5199776767e-17 J/cell, above the fixed 5e-18 J cutoff.
The baseline+Cv case completes, and its independently computed temperature
differs from Cantera by 7.50e-8 K. The cold reference changes temperature by
only 5.87e-5 K over 240 us: this is an induction/nonigniting control, not a
validated cold flame. The hot 1500 K G/Cv control completes at roundoff energy.

Hypothesis: the original fixed absolute cutoff is below the attainable
floating-point floor for this larger pressure/volume/energy scale. It is not
yet established solely from the small failing residual. A new separately
selectable executable must retain an exact old-rule flag-off replay, record
component scale and accepted residual, and compare independent inventories
and reference errors. All original failures and source hashes remain intact.

## Discrete residual and scale

At fixed final rho, Y, phi, K, write the residual in J/cell, including the
same Euler time, sensible/formation convection, kinetic flux, sensible and
formation diffusion terms used by G:

    r_i = V_i [rho_f(hs_f+hc_f+K_f)-p_f
               -rho_n(hs_n+hc_n+K_n)+p_n]
          + dt [C_hs,i + C_hc,i + C_K,i - L_hs,i - L_hc,i].

Use a component scale S_i consisting of absolute time-inventory components
and the absolute magnitudes of each assembled matrix/vector contribution.
For matrix terms use the sum of |diag*x|, |source|, each internal-neighbour
coefficient product, and each boundary coefficient product. Do not take the
absolute value only after cancellations within an operator. Formation
diffusion uses sum_s |Hc_s| times its species operator magnitude.

The selectable stopping rule requires every cell to satisfy

    |r_i| <= 5e-18 J + 64 * epsilon_double * S_i.

The original rule uses its original strict fixed cutoff. The factor 64 is
declared before replay; it is a conservative component rounding allowance,
not a formally certified bound on thermo inversion or solution error. It
does not relax the independent global conservation/EOS/reference gates.
The scale changes under an elemental energy gauge, as rounding conditioning
can change; the physical residual remains gauge covariant only when the full
elemental residual is included. No gauge-independent error-estimator claim.

## Implementation and acceptance

Create reactingEnergyRoundoffCandidates from the unchanged G executable
sources and Make setup, with only this selected stopping rule and diagnostics.
Default the flag off. Record maximum residual, allowance, component scale and
number of accepted steps exceeding the old cutoff. Keep existing applications
and concurrently executing spatial-screen binaries unchanged.

First replay the failed cold source regime with the flag off and on. The
flag-off result must retain its failure; a successful flag-on replay must
meet T error <max(1e-5 K,10 times reference contrast), energy/mass/elements
<1e-9, EOS relative error <1e-10 and local ledger closure <1e-12 J.
Then repeat the old 1100 K and hot 1500 K controls, an unequal-mixture wave,
and F dt1 us. Record any changed fields and errors; do not assume equivalence
merely because both variants conserve energy. Only logical accuracy controls
may overlap the current screens; their wall times are excluded from comparative
performance claims. No publication gate is passed by repairing this cutoff.

## First replay and refinement before the next code version

The new flag-off cold replay reproduces the original failure. Allowance-only
stopping completes: T error 4.55e-12 K, energy drift -1.02e-15 relative,
accepted maximum step residual 1.95e-17 J/cell, maximum allowance 2.03e-15 J.
This supports a scale/roundoff limitation. In the 1100/1500 K controls it also
stops earlier than the old rule and raises global drift to 2.36e-12/1.58e-12
relative, versus roughly 1e-14 before. These still pass the declared coarse
gates, but needlessly relax convergence in cases that already completed.
The first source snapshot and allowance-only records remain retained.

Refine before replay: retain unconditional acceptance by the original cutoff.
Use the component allowance only after at least two updates and exact repetition
of the full internal h,T,p state from the previous iteration or from two
iterations earlier, on every rank. With frozen rho,Y,phi,K and the same
operators, a repeated state gives the same subsequent deterministic update;
further cycling cannot reach a different residual. This is a representability
stagnation test, not a solution-error bound. Require the component residual
ratio <=1 as well. Record repeated-state status explicitly and use distinct
stagnation-tagged cases. Prediction: the cold failure is avoided, while
previously completing warm/hot/wave/F controls reproduce their old fields.
Any contrary outcome is retained and reported; do not change the threshold
or repetition test after seeing it merely to force acceptance.

The exact period-one/two hypothesis fails: the cold replay remains below
0.01 of its component allowance but h,T,p do not repeat exactly in that
window. Residual traces show several nearby values, so a two-value residual
log alone did not establish a full-state cycle. Warm and hot field comparisons
remain identical with the stagnation policy; the cold failure is retained.
No exact-cycle explanation is asserted.

Next predeclared policy: preserve the original strict cutoff throughout the
20-iteration solve. If it is still unmet at the original cap, accept only when
the final per-cell residual is within the declared component allowance.
This avoids early acceptance in every formerly completing case without an
unsupported repetition assumption. It is a bounded residual fallback at the
existing iteration cap, not proof that more iterations could never help.
Retain fatal rejection above the component allowance. Record capFallback
explicitly, and use new capFallback-tagged cases. Hypothesis: cold completes
with its independent gates, and warm/hot/wave/F old-rule endpoint fields stay
identical. Absolute global drift may accumulate; independently verify it
against the declared gate and recorded cumulative accepted allowance.

The cap-fallback replay completes all nine formerly successful/on cases and
retains the old-rule cold failure. Cold flag-on T difference is 3.86535e-12 K,
relative energy drift -1.47611e-15, maximum accepted residual 2.15359e-17 J/cell
and maximum scaled residual 0.0106331. The independent mass/elements/EOS gates
pass. Warm/hot/unequal-mixture/F flag-on versus off endpoint fields coincide
exactly. This supports the scoped fallback, not an impossibility of achieving
a smaller residual through a different or longer nonlinear solve.

Accepted traces count each rank/time once. Cold's inventory change magnitude
3.60822e-16 J is below the recorded accumulated residual-magnitude upper sum
2.05665e-14 J; accumulated component-allowance upper sum is 3.88870e-12 J.
These are sums of nLocal times recorded maxima, not thermodynamic/truncation
error bounds. The original absolute criterion and other applications remain
unchanged. Source snapshot 9db32f14eb7577e7f647a37d01aecb0de7fa2a05fd61372b926a7c8cf284eeb2,
executable 5ae94e2ab5dbe1aaf0baac1c1581886cfa73762896dc71fd46d59034d87dea70.
All three policy versions and their failures are retained. Wall times are
excluded from cost comparisons because logical campaigns overlapped.
