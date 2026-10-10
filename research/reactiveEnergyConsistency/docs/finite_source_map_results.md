# Finite source and transition-map candidate cycles

The existing source interface already uses finite species increments. The selected integrated-reaction path computes RR_i=(c_i_new-c_i_old)W_i/dt and Qdot=-sum Hc_i RR_i. Therefore dt Qdot+sum Hc_i delta(rho Yi)=0 is an algebraic identity, independent of stiff integrator tolerance. It does not imply that the endpoint chemistry state has accurate species or preserves absolute energy. The installed instantaneous calculate() method is distinct from this selected solve path.

For continuous thermodynamics, exact scalar inversion of absolute energy/enthalpy completes a conditional conservative chemistry map. At CV, delta(rho hs)=-sum Hc_i delta q_i+delta p. Omitting delta p conserves the wrong enthalpy-density quantity and produces a CV residual equal to minus the EOS pressure change. At physical CP, delta hs=-sum Hc_i delta Yi with expansion/dilution and fixed total mass; density-scaled energy is not the invariant. Variable Cp changes inversion, not the constant formation-energy contraction.

## Independent minimal model

The Python model uses actual continuous H2 NASA properties, but a prescribed mass-balanced H2+O2/2->H2O extent with exponential progress. It is an abstract algebraic falsification model, not a replacement kinetic mechanism or a physical trajectory reference. It varies initial T, time step and CV/physical CP constraint, preserves positivity/mass/elements, and uses bisection inversion.

| Constraint | T0 (K) | dt (s) | Invariant residual (J/kg) | Finite RR/Qdot residual (J/m3) | CV omitted-pressure error (J/m3) |
|---|---|---|---|---|---|
| CV | 500.0 | 1e-06 | -1.1642e-10 | -1.8190e-12 | -3.4598e+03 |
| CP | 500.0 | 1e-06 | +0.0000e+00 | -1.8190e-12 | not applicable |
| CV | 500.0 | 1e-05 | -8.7311e-11 | +0.0000e+00 | -2.7579e+04 |
| CP | 500.0 | 1e-05 | +1.7462e-10 | +0.0000e+00 | not applicable |
| CV | 500.0 | 0.0001 | -2.9104e-11 | +0.0000e+00 | -6.7930e+04 |
| CP | 500.0 | 0.0001 | -5.8208e-11 | +0.0000e+00 | not applicable |
| CV | 1100.0 | 1e-06 | +1.1642e-10 | -9.0949e-13 | -1.3907e+03 |
| CP | 1100.0 | 1e-06 | +0.0000e+00 | -9.0949e-13 | not applicable |
| CV | 1100.0 | 1e-05 | +0.0000e+00 | -7.2760e-12 | -1.1067e+04 |
| CP | 1100.0 | 1e-05 | +2.3283e-10 | -7.2760e-12 | not applicable |
| CV | 1100.0 | 0.0001 | -2.3283e-10 | +1.4552e-11 | -2.7283e+04 |
| CP | 1100.0 | 0.0001 | -2.3283e-10 | +1.4552e-11 | not applicable |
| CV | 1500.0 | 1e-06 | +2.3283e-10 | +0.0000e+00 | -9.4884e+02 |
| CP | 1500.0 | 1e-06 | +2.3283e-10 | +0.0000e+00 | not applicable |
| CV | 1500.0 | 1e-05 | +0.0000e+00 | +0.0000e+00 | -7.5582e+03 |
| CP | 1500.0 | 1e-05 | +0.0000e+00 | +0.0000e+00 | not applicable |
| CV | 1500.0 | 0.0001 | +4.6566e-10 | +0.0000e+00 | -1.8665e+04 |
| CP | 1500.0 | 0.0001 | +0.0000e+00 | +0.0000e+00 | not applicable |

The finite update cancels to roundoff; substituting an instantaneous initial source instead creates the recorded finite heat mismatch. This validates the rationale for finite increments but does not create an improvement over native RR, which is already finite.

## Post-map operator counterexample

Two unit-volume cells have exact chemistry maps and the same final composition but unequal temperatures. Opposite density changes preserve global mass and every species inventory while pressure is reset exactly by EOS. The energy then changes by -6851.46961 J. Its exact decomposition is DrhoH+DrhoC+Dpressure, with closure +4.0018e-11 J (roundoff against the energy scale). The prescribed density operation is not a solution of a flow equation; it is a counterexample to the claim that an invariant chemistry map alone guarantees conservation under arbitrary later pressure/density updates.

Full native matched runs provide the stronger CFD evidence: Dchemistry remains roundoff while the density pair persists. Thus a chemistry/CFD interface rewrite cannot cancel the measured terms without changing transport or pressure/species/energy response. PelePhysics and conservative Cantera reactor state integration already implement the essential invariant-carrying architecture.

Decisions: family 2 REJECT as a new finite-RR method; family 3 REJECT as a generic new interface or sufficient CFD cure. Retain conservative maps as baselines. This does not exclude a demonstrably different operator response or source-forcing approximation. Machine evidence: thermochemical_abstract_map.json; raw ThermochemicalAbstractMap_v1.
