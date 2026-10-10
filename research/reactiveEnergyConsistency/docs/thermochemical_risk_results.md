# Mechanism risk and reconstruction candidate cycles

For a CV trajectory crossing Tc, the data-jump contribution is sum_crossings sum_i c_i(Tc) Delta H_i [J/m3]. At physical CP the corresponding specific-enthalpy expression uses Yi(Tc) Delta H_i/W_i [J/kg]. Signed jumps follow crossing direction. Summing absolute contributions supplies a bound on the data jump only; it does not bound smooth ODE error, transport error or pressure coupling.

## Multi-mechanism source comparison

| Mechanism | Constraint | T0 | Max species h jump (J/kg) | Observed relative drift | Event-weighted prediction (relative) | Remainder |
|---|---|---|---|---|---|---|
| legacy | CV | 999.0 | 1.254769e+00 | 1.146044e-07 | 1.146045e-07 | 8.174074e-14 |
| legacy | CV | 1100.0 | 1.254769e+00 | 9.587865e-13 | 0.000000e+00 | 9.587865e-13 |
| legacy | CV | 1500.0 | 1.254769e+00 | 8.665752e-14 | 0.000000e+00 | 8.665752e-14 |
| legacy | CP | 999.0 | 1.254769e+00 | 7.101228e-08 | 7.101230e-08 | 1.337481e-14 |
| legacy | CP | 1100.0 | 1.254769e+00 | 1.110851e-13 | 0.000000e+00 | 1.110851e-13 |
| legacy | CP | 1500.0 | 1.254769e+00 | 3.094975e-14 | 0.000000e+00 | 3.094975e-14 |
| HS | CV | 999.0 | 1.538476e-06 | 1.592480e-12 | 3.528953e-14 | 1.557191e-12 |
| HS | CV | 1100.0 | 1.538476e-06 | 8.648746e-13 | 0.000000e+00 | 8.648746e-13 |
| HS | CV | 1500.0 | 1.538476e-06 | 4.636178e-12 | 0.000000e+00 | 4.636178e-12 |
| HS | CP | 999.0 | 1.538476e-06 | 1.874323e-12 | 2.180618e-14 | 1.852517e-12 |
| HS | CP | 1100.0 | 1.538476e-06 | 1.137992e-13 | 0.000000e+00 | 1.137992e-13 |
| HS | CP | 1500.0 | 1.538476e-06 | 2.425450e-14 | 0.000000e+00 | 2.425450e-14 |
| CpHS | CV | 999.0 | 1.538476e-06 | 6.966877e-14 | 3.513595e-14 | 3.453281e-14 |
| CpHS | CV | 1100.0 | 1.538476e-06 | 9.176240e-13 | 0.000000e+00 | 9.176240e-13 |
| CpHS | CV | 1500.0 | 1.538476e-06 | 8.254879e-14 | 0.000000e+00 | 8.254879e-14 |
| CpHS | CP | 999.0 | 1.538476e-06 | 3.234091e-14 | 2.171104e-14 | 1.062988e-14 |
| CpHS | CP | 1100.0 | 1.538476e-06 | 1.046875e-13 | 0.000000e+00 | 1.046875e-13 |
| CpHS | CP | 1500.0 | 1.538476e-06 | 3.448687e-14 | 0.000000e+00 | 3.448687e-14 |
| GRI | CV | 999.0 | 3.627359e+00 | 2.161376e-07 | 2.161359e-07 | 1.644166e-12 |
| GRI | CV | 1100.0 | 3.627359e+00 | 2.168923e-12 | 0.000000e+00 | 2.168923e-12 |
| GRI | CV | 1500.0 | 3.627359e+00 | 2.241387e-13 | 0.000000e+00 | 2.241387e-13 |
| GRI | CP | 999.0 | 3.627359e+00 | 1.339082e-07 | 1.339072e-07 | 9.646345e-13 |
| GRI | CP | 1100.0 | 3.627359e+00 | 5.169899e-13 | 0.000000e+00 | 5.169899e-13 |
| GRI | CP | 1500.0 | 3.627359e+00 | 8.919288e-14 | 0.000000e+00 | 8.919288e-14 |
| Alzueta | CV | 999.0 | 6.076542e-01 | 6.592212e-11 | 6.532106e-11 | 6.010606e-13 |
| Alzueta | CV | 1100.0 | 6.076542e-01 | 1.227636e-12 | 0.000000e+00 | 1.227636e-12 |
| Alzueta | CV | 1500.0 | 6.076542e-01 | 5.368255e-12 | 0.000000e+00 | 5.368255e-12 |
| Alzueta | CP | 999.0 | 6.076542e-01 | 4.034463e-11 | 4.058364e-11 | 2.390152e-13 |
| Alzueta | CP | 1100.0 | 6.076542e-01 | 4.390353e-13 | 0.000000e+00 | 4.390353e-13 |
| Alzueta | CP | 1500.0 | 6.076542e-01 | 3.741355e-14 | 0.000000e+00 | 3.741355e-14 |

The event-weighted quantities use observed, sample-interpolated crossing compositions. Their strong agreement for legacy H2/GRI is a verification of the jump identity, not held-out prospective prediction. Alzueta also has a smaller measured event floor. The same mechanism-wide maximum gives different invariant errors in crossing and noncrossing regimes; it cannot certify source success by itself. Continuous native spatial calls also fail in hot states despite negligible breakpoint jumps. A certificate requires both valid data and numerical/operator information.

Mech Checker (Killingsworth et al.2020, sec2.1–2.3) already combines automated constrained repair with numerical integration and pressure-coupled multizone consequences. A mechanism linter or an observed jump predictor has insufficient generic novelty. Family 4 REJECT as the primary method: no prospective, operating-condition-independent source/CFD error predictor has been validated. The event diagnostic remains useful evidence.

## Reconstruction

HS changes only upper-branch enthalpy/entropy integration constants and preserves Cp exactly. CpHS also shifts upper Cp by a small constant and then rematches h/s. Both preserve lower/reference coefficients exactly. NASA PAC fitting, RMG Wilhoit-to-NASA conversion, Boettcher Appendix H and Mech Checker already impose these types of constraints, including Cp derivatives and reference values.

The controls materially improve source breakpoint invariance, but neither supplies a validated fit to original molecular/tabulated thermochemical source data. Those source data are not available for the legacy files. Comparing a refit against samples from the old polynomial would measure approximation to that polynomial, not physical accuracy. Alternative polynomial order and reference interpolation therefore cannot be honestly ranked for physical accuracy here. No synthetic “correct” source data are substituted.

Family 5 REJECT as a generic new repair method or physical-accuracy claim. MODIFY only if independent original source data become available and a specific unresolved constrained-fit problem can be defined. This is a bounded branch decision, not a claim that all future thermochemistry reconstruction research is exhausted.

Machine evidence: thermochemical_candidate_decision.json contains all 90 tolerance/regime records and input hashes; mechanism_continuity_audit.json contains the full reaction and equilibrium rankings. The repair manifest records serialized residual jumps, not a claim of exact-real continuity.
