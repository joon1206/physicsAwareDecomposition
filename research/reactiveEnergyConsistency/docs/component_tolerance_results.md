# Conservative energy Newton: component scale and stagnation controls

The cold ten-atmosphere Cv/G control fails the fixed absolute stopping
cutoff in its original iteration budget. All old-rule failures remain
retained. A separate executable tests three stopping policies.
This is established numerical stopping practice, IMPLEMENTATION_ONLY.

The first allowance-only rule accepts |r_i| <= 5e-18 + 64 eps S_i.
S includes absolute time-inventory and individual matrix contribution
magnitudes before cancellation. It completes the cold case, but stops
earlier in warm/hot cases and increases drift. Exact period-one/two
h,T,p repetition preserves warm controls but fails to complete cold.
The final control retains the old cutoff throughout the solve and
allows a component-bounded residual only at the original iteration
cap. This is a residual fallback, not a certified accuracy bound.
See candidates/componentEnergyTolerance.md for the pre-test derivations.

## Broader Cv source regimes using the original G cutoff

| Regime | Method | Status | T difference (K) | E drift (relative) |
|---|---|---|---:|---:|
| coldHighPressure | none | completed | 7.4962941e-08 | -1.4947244e-10 |
| coldHighPressure | conservativeState | failed / retained | — | — |
| hot | none | completed | 3.1091108e-04 | -4.7234286e-08 |
| hot | conservativeState | completed | 4.8858055e-09 | +1.1242708e-14 |

The cold 950 K/10 atm independent reference remains in induction:
T changes by 5.87e-5 K over 240 us. Hot 1500 K/1 atm burns to about
3003.21277 K. Both use the unchanged legacy-matched H2 mechanism,
clone=False, verified density/molecular weights and two reference
tolerances. These source-only checks do not validate flame structure.

## Stopping-rule replays

| Policy | Case | Flag | Status | T difference (K) | E drift (relative) | Max accepted residual (J) | Max scaled residual | Accepted above old cutoff |
|---|---|---|---|---:|---:|---:|---:|---:|
| allowance-only | RoundoffCvRegime_coldHighPressure_conservativeState_dt1e-06_dfdt0_componentOff | off | failed / retained | — | — | — | — | — |
| allowance-only | RoundoffCvRegime_coldHighPressure_conservativeState_dt1e-06_dfdt0_componentOn | on | completed | 4.5474735e-12 | -1.0219204e-15 | 1.9492070e-17 | 9.6239836e-03 | 239 |
| allowance-only | RoundoffCvRegime_standard_conservativeState_dt1e-06_dfdt0_componentOff | off | completed | 1.0657459e-08 | +8.1935416e-15 | 4.9398926e-18 | 2.2552644e-02 | 0 |
| allowance-only | RoundoffCvRegime_standard_conservativeState_dt1e-06_dfdt0_componentOn | on | completed | 1.1092197e-08 | +2.3611266e-12 | 9.0339810e-16 | 9.0170484e-01 | 55 |
| allowance-only | RoundoffCvRegime_hot_conservativeState_dt1e-06_dfdt0_componentOff | off | completed | 4.8858055e-09 | +1.1242708e-14 | 4.6491584e-18 | 1.4037066e-02 | 0 |
| allowance-only | RoundoffCvRegime_hot_conservativeState_dt1e-06_dfdt0_componentOn | on | completed | 5.2796167e-09 | +1.5823071e-12 | 6.8257315e-16 | 9.5149492e-01 | 50 |
| allowance-only | RoundoffThermoWave_conservativeState_nx64_dt2e-08_componentOff | off | completed | 2.4516453e+00 | +1.0744560e-13 | 4.1640696e-19 | 1.3832446e-02 | 0 |
| allowance-only | RoundoffThermoWave_conservativeState_nx64_dt2e-08_componentOn | on | completed | 2.4516453e+00 | +1.0744560e-13 | 4.1640696e-19 | 1.3832446e-02 | 0 |
| exact-cycle | RoundoffCvRegime_coldHighPressure_conservativeState_dt1e-06_dfdt0_stagnation_componentOff | off | failed / retained | — | — | — | — | — |
| exact-cycle | RoundoffCvRegime_coldHighPressure_conservativeState_dt1e-06_dfdt0_stagnation_componentOn | on | failed / retained | — | — | — | — | — |
| exact-cycle | RoundoffCvRegime_standard_conservativeState_dt1e-06_dfdt0_stagnation_componentOff | off | completed | 1.0657459e-08 | +8.1935416e-15 | 4.9398926e-18 | 2.2552644e-02 | 0 |
| exact-cycle | RoundoffCvRegime_standard_conservativeState_dt1e-06_dfdt0_stagnation_componentOn | on | completed | 1.0657459e-08 | +8.1935416e-15 | 4.9398926e-18 | 2.2552644e-02 | 0 |
| exact-cycle | RoundoffCvRegime_hot_conservativeState_dt1e-06_dfdt0_stagnation_componentOff | off | completed | 4.8858055e-09 | +1.1242708e-14 | 4.6491584e-18 | 1.4037066e-02 | 0 |
| exact-cycle | RoundoffCvRegime_hot_conservativeState_dt1e-06_dfdt0_stagnation_componentOn | on | completed | 4.8858055e-09 | +1.1242708e-14 | 4.6491584e-18 | 1.4037066e-02 | 0 |
| exact-cycle | RoundoffThermoWave_conservativeState_nx64_dt2e-08_stagnation_componentOff | off | completed | 2.4516453e+00 | +1.0744560e-13 | 4.1640696e-19 | 1.3832446e-02 | 0 |
| exact-cycle | RoundoffThermoWave_conservativeState_nx64_dt2e-08_stagnation_componentOn | on | completed | 2.4516453e+00 | +1.0744560e-13 | 4.1640696e-19 | 1.3832446e-02 | 0 |
| exact-cycle | F_conservativeState_dt1e-06_s1_g0_o1_p1_stagnation_componentOff | off | completed | — | +5.5521900e-14 | 4.9919513e-18 | 2.3103047e-01 | 0 |
| exact-cycle | F_conservativeState_dt1e-06_s1_g0_o1_p1_stagnation_componentOn | on | completed | — | +5.5521900e-14 | 4.9919513e-18 | 2.3103047e-01 | 0 |
| cap-fallback | RoundoffCvRegime_coldHighPressure_conservativeState_dt1e-06_dfdt0_capFallback_componentOff | off | failed / retained | — | — | — | — | — |
| cap-fallback | RoundoffCvRegime_coldHighPressure_conservativeState_dt1e-06_dfdt0_capFallback_componentOn | on | completed | 3.8653525e-12 | -1.4761073e-15 | 2.1535891e-17 | 1.0633097e-02 | 213 |
| cap-fallback | RoundoffCvRegime_standard_conservativeState_dt1e-06_dfdt0_capFallback_componentOff | off | completed | 1.0657459e-08 | +8.1935416e-15 | 4.9398926e-18 | 2.2552644e-02 | 0 |
| cap-fallback | RoundoffCvRegime_standard_conservativeState_dt1e-06_dfdt0_capFallback_componentOn | on | completed | 1.0657459e-08 | +8.1935416e-15 | 4.9398926e-18 | 2.2552644e-02 | 0 |
| cap-fallback | RoundoffCvRegime_hot_conservativeState_dt1e-06_dfdt0_capFallback_componentOff | off | completed | 4.8858055e-09 | +1.1242708e-14 | 4.6491584e-18 | 1.4037066e-02 | 0 |
| cap-fallback | RoundoffCvRegime_hot_conservativeState_dt1e-06_dfdt0_capFallback_componentOn | on | completed | 4.8858055e-09 | +1.1242708e-14 | 4.6491584e-18 | 1.4037066e-02 | 0 |
| cap-fallback | RoundoffThermoWave_conservativeState_nx64_dt2e-08_capFallback_componentOff | off | completed | 2.4516453e+00 | +1.0744560e-13 | 4.1640696e-19 | 1.3832446e-02 | 0 |
| cap-fallback | RoundoffThermoWave_conservativeState_nx64_dt2e-08_capFallback_componentOn | on | completed | 2.4516453e+00 | +1.0744560e-13 | 4.1640696e-19 | 1.3832446e-02 | 0 |
| cap-fallback | F_conservativeState_dt1e-06_s1_g0_o1_p1_capFallback_componentOff | off | completed | — | +5.5521900e-14 | 4.9919513e-18 | 2.3103047e-01 | 0 |
| cap-fallback | F_conservativeState_dt1e-06_s1_g0_o1_p1_capFallback_componentOn | on | completed | — | +5.5521900e-14 | 4.9919513e-18 | 2.3103047e-01 | 0 |

Mixture-wave T differences are analytic transport errors; homogeneous
ones are independent Cantera endpoint differences. F has no resolved
field reference and is not assigned an exact-error number.

| Policy | Pair | T Linf (K) | p Linf (Pa) | Max of all field Linf values |
|---|---|---:|---:|---:|
| allowance-only | standard | 4.3974069e-10 | 4.9825758e-08 | 8.5029751e-07 |
| allowance-only | hot | 4.0108716e-10 | 3.4895493e-08 | 7.9162419e-07 |
| allowance-only | unequalMixture | 0.0000000e+00 | 0.0000000e+00 | 0.0000000e+00 |
| exact-cycle | standard | 0.0000000e+00 | 0.0000000e+00 | 0.0000000e+00 |
| exact-cycle | hot | 0.0000000e+00 | 0.0000000e+00 | 0.0000000e+00 |
| exact-cycle | unequalMixture | 0.0000000e+00 | 0.0000000e+00 | 0.0000000e+00 |
| exact-cycle | F | 0.0000000e+00 | 0.0000000e+00 | 0.0000000e+00 |
| cap-fallback | standard | 0.0000000e+00 | 0.0000000e+00 | 0.0000000e+00 |
| cap-fallback | hot | 0.0000000e+00 | 0.0000000e+00 | 0.0000000e+00 |
| cap-fallback | unequalMixture | 0.0000000e+00 | 0.0000000e+00 | 0.0000000e+00 |
| cap-fallback | F | 0.0000000e+00 | 0.0000000e+00 | 0.0000000e+00 |

## Accepted residual accumulation

Each accepted rank/time is counted exactly once. Weighting the recorded
global maximum by each rank cell count bounds the sum of absolute
assembled residuals over cells and steps. A second sum uses the rank
maximum component allowance. Neither sum bounds solution error.

| Cold policy | Inventory change magnitude (J) | Residual magnitude upper sum (J) | Allowance upper sum (J) |
|---|---:|---:|---:|
| allowance-only | 2.4980018e-16 | 2.2547649e-14 | 3.8886988e-12 |
| cap-fallback | 3.6082248e-16 | 2.0566477e-14 | 3.8886988e-12 |

## Interpretation and limits

The initial successful allowance-only replay does not justify relaxing
every Newton solve. The failed exact-cycle explanation remains
retained. Cap fallback preserves the old convergence checks before
the iteration limit; the independent inventories, EOS
and reference errors remain the scientific gates. A conservative
rounding allowance is not a certified thermodynamic or truncation
error bound, and may condition differently under an energy gauge.

Source snapshots/executable hashes identify each policy per case.
The installed solvers and original candidates remain unchanged.
Logical replays overlapped separate logical source screens; all their
wall times are excluded from performance comparisons. Added component
operators, state copies and MPI reductions have a cost; no low-cost
or numerical-method novelty claim follows.
