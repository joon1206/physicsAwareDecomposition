# Baseline discrete energy identity

## Continuous formulation

For species production rates omega_i and diffusion fluxes j_i,
`dt(rho Yi) + div(rho U Yi + j_i) = omega_i`. Absolute species enthalpy is
`ha_i = hs_i + Hc_i`; JANAF Hc is a constant specific formation enthalpy.
Mixture `ha = hs + sum Yi Hc_i`, `ea = ha - p/rho`, and `E = ea + K`.
Thus the closed adiabatic total energy is

```
Ecal = sum_c Vc [rho_c (hs_c + sum_i Yi_c Hc_i + K_c) - p_c].
```

The sensible-energy source is `Qdot = -sum_i Hc_i omega_i`. Including both
formation energy in the inventory and Qdot as an *external* heat source
would double-count chemical conversion. Convection, heat conduction,
species enthalpy diffusion and stress work are boundary transports in the
absolute total-energy balance. The local v2012 baseline instead uses
`laplacian(alphaEff,hs)` and no separate stress-work term. That modelling
choice must not be confused with a segregated integral mismatch.

## Implemented Euler equation

Let n be the beginning-of-step stored state. Let a denote rho used when
the final outer-loop energy equation is assembled; b denotes its K, Y and
solved hs; f denotes the final pressure-corrected state. Define integrals
`H_a = sum V rho_a hs_b`, `J_a = sum V rho_a K_b`,
`C_a = sum V rho_a hc(Y_b)` and `P_f = sum V p_f`.

The original unrelaxed scalar matrix, evaluated after its solve, gives

```
(H_a - H_old + J_a - J_old)/dt + B_h + B_K - L_h - W = Q + R,
```

where W is the integrated dpdt actually used, Q the integrated Qdot,
B_h and L_h are respectively the integrated assembled convection and
positive laplacian operators, B_K is integrated explicit div(phi,K), and
R is LHS minus RHS in watts, evaluated independently from scalar matrix
coefficients, internal faces, and each boundary source exactly once. The
v2012 scalar residual helper adds coupled sources twice (ldu interfaces and
addBoundarySource); using it would produce spurious cancelling residual and
transport terms. The ledger retains the original matrix before
relaxation/constraining to include their effects in R.

With `E_f=H_f+J_f+C_f-P_f`, exact algebra yields

```
E_f - E_n = D_pressure + D_kinetic + D_rho_h + D_rho_c
          + D_species_chemistry + D_equation + D_transport + D_history

D_pressure = dt W - (P_f-P_n)
D_kinetic = J_f-J_a
D_rho_h = sum V (rho_f-rho_a) hs_b
D_rho_c = sum V (rho_f-rho_a) hc(Y_b)
D_species_chemistry = C_a-C_n + dt Q
D_equation = dt R
D_transport = -dt (B_h+B_K-L_h)
D_history = H_old+J_old-H_n-J_n.
```

The RHS uses separately assembled equation operators and an original-matrix
residual, rather than choosing a remainder to force closure. For multiple
outer iterations use the *last* energy assembly relative to the beginning
of the timestep. Adding every outer solve as a physical chemistry step
would be incorrect. For these closed cases D_transport should vanish to
roundoff; it is still measured from the assembled operators.

The pressure term includes lagged dpdt and all subsequent pressure changes;
it is not solely mechanical pressure work from the momentum equation.
The kinetic term includes density and velocity changes after energy.
D_rho_h and D_rho_c measure thermodynamic density replacement applied to
the transported quantities; their sum can be large with zero global mass
drift because the density change correlates with specific enthalpy.

## Identifiability and limitations

The species/chemistry aggregate is measurable but does not yet uniquely
separate ODE error, species matrix error, clipping, inert closure, and
boundary formation-enthalpy flux. A weighted species-equation residual is
needed for that refinement. Qdot's local source construction can be checked
against `-sum Hc_i R_i`; that tests source consistency, not ODE accuracy.

Time discretization, splitting error and thermodynamic inversion error are
not uniquely additive independent quantities in a single trajectory.
Stage changes in T/psi at fixed hs are not by themselves conserved-energy
losses. Temporal/spatial convergence and independent reference solutions
are needed to estimate truncation errors. Report an unallocated mechanism
explicitly rather than inventing D_time or D_split. Roundoff is bounded by
the observed closure with cancellation-aware absolute tolerances.

This identity is restricted to Euler sensible enthalpy; internal-energy,
moving-mesh, local-time and non-Euler cases require new history/pressure
terms. The instrumented executable must reject those configurations.
