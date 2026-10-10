# Density projection and thermochemical energy: local discrete derivation

This derivation concerns the installed v2012 fixed-mesh, global Euler,
sensible-enthalpy, perfect-gas reacting formulation. No added sources, moving
mesh, MRF, transonic pressure or differential-diffusion model is included.
The accepted baseline audit is preserved; candidate work uses a separate
executable and case directory.

## States and actual equation sequence

One outer loop advances continuity, momentum, chemical source construction,
species, sensible enthalpy, thermo inversion, pressure/flux/velocity and density.
Let n denote the stored beginning of a step, a the density coefficient in the
species/energy solve, b the solved species/enthalpy and predictor kinetic state,
and f the final pressure-corrected state. The final density is
rho_f = rho_a + delta rho. Composition does not change after species in this
baseline; the pressure loop leaves solved hs unchanged.

For a cell of volume V, the absolute total-energy inventory is

```
E_i = V [rho_i (hs_i + hc(Y_i) + K_i) - p_i],
hc(Y) = sum_s Y_s Hc_s,    ha = hs + hc.
```

The energy coefficient replacement, with pressure and kinetic terms written
separately, therefore has the **exact** contribution

```
dE_density = V (rho_f-rho_a) [hs_b + hc(Y_b)].
dE_kinetic = V [rho_f K_f - rho_a K_b].
dE_pressure = V [dt dpdt_used - (p_f-p_n)].
```

The thermochemical weighting is absolute enthalpy, not hs alone, hc alone or
internal energy. The pressure inventory has already been subtracted separately.
Replacing ha by e would omit V delta rho p/rho without a matching pressure
term. The kinetic term already includes its density change and must not be
included again in the thermochemical density term. Pressure cancellation is
measured through dE_pressure, not presumed from a continuum product rule.

## Cellwise identity from independently evaluated operators

Let B_h and L_h be each cell's assembled convection and positive laplacian
matrix operators in watts; B_K is V div(phi,K). Let R_h be the original,
unrelaxed energy matrix LHS-minus-RHS, with each coupled boundary source
counted once. Define formation convection/diffusion by Hc-weighted species
operators B_c and L_c. Chemistry produces integrated species sources R_s
in kg/s. All use the actual species and energy assemblies, not a fitted total.

```
dE_chemistry = dt [V Qdot + sum_s Hc_s R_s]
dE_speciesTransport = -dt (B_c-L_c)
dE_speciesResidual = V [rho_a hc_b-rho_n hc_n]
                       - dt sum_s Hc_s R_s + dt (B_c-L_c)
dE_equation = dt R_h
dE_transport = -dt (B_h+B_K-L_h)
dE_history = V [rho_old(hs_old+K_old)-rho_n(hs_n+K_n)]
```

The species residual evaluates the actual conservative species balance,
including the algebraic inert closure and clipping. It is not chemistry ODE
trajectory error. These terms combine to the earlier species/chemistry
aggregate exactly. The Euler energy matrix yields

```
E_f-E_n = dE_pressure + dE_kinetic + dE_density
        + dE_chemistry + dE_speciesTransport + dE_speciesResidual
        + dE_equation + dE_transport + dE_history.
```

After an explicit candidate enthalpy modification, add
`dE_postH = V rho_f (hs_final-hs_b)`; use the actual final pressure in
dE_pressure. Summing cells and ranks gives the global identity, including
measured net boundary transport. Physical boundary contributions are parts
of the transport terms; coupled processor/cyclic contributions are paired
internal transfers, not external sources. No uniform global redistribution
is introduced.

## Temporal scaling and gauge qualification

For a smooth, consistently initialized trajectory, delta rho=O(dt), so the
single-step coefficient mismatch is O(dt) before cancellations with transport,
species and pressure. A generic global O(dt^2) defect cannot be asserted merely
from that local product. The observed reacting sweep is nonmonotonic. Cellwise
signed sums and absolute norms must be measured at multiple dt and fixed endpoint.

Formation enthalpy is reference dependent. Shift species absolute enthalpy
by g_s and keep hs unchanged by applying the same shift to Hc_s. The energy
inventory changes by sum_s g_s M_s. For an elemental gauge
g_s=sum_e a_e Z_es, this equals sum_e a_e M_e; if elemental masses are
conserved, the global energy **defect** is unchanged. However,
dE_density changes by V delta rho sum_s g_s Y_s, compensated elsewhere in the
species budget. Its isolated formation contribution is therefore not a
reference-invariant causal indicator. Setting every Hc to zero is generally
not an elemental gauge: it changes reaction heat, equilibrium thermodynamics
and the reacting physical problem. Nonreacting constant-offset ablations can
retain exactly the same fields; reacting ablations must be labelled changed
thermochemistry. Both are required controls, not interchangeable evidence.

## Candidate cancellation and unavoidable state response

To cancel the density pair at fixed final rho,Y,U, define

```
rho_f ea(T_new,Y_b) = rho_a ha(T_b,Y_b) - p_f,
ea(T,Y)=ha(T,Y)-R(Y)T,
p_new=rho_f R(Y)T_new.
```

Then, algebraically,

```
rho_f [hs_new-hs_b] - [p_new-p_f]
 = -(rho_f-rho_a) ha_b.
```

Cv=d ea/dT must be positive and the target must lie in the admissible
thermodynamic range. This local nonlinear projection preserves rho and all
rhoY, enforces EOS and cancels the density pair exactly. It changes pressure:
the existing momentum and flux correction is no longer based on final p.
Consequently it is a *testable candidate*, not a complete legitimate final
coupling algorithm. At fixed rho,p,Y simultaneously, no nonzero correction
is possible since the EOS fixes T and hs. Any accepted modification must
also bound or correct the changed momentum/pressure state, local energy flux,
species consistency and solution error.

A distinct scalar correction linearizes this relation and includes transport:
`[rho_f Cv/Cp / dt + div(phi,.) - laplacian(alpha,.)] delta hs
 = -(rho_f-rho_a) ha_b/dt`. It cancels the density term to linearized order
plus conservative correction-flux exchanges. Its pressure response and
thermodynamic nonlinear remainder must be measured; this is not a claimed
new product-rule principle or simply a repeat of the original energy equation.

## Closest inspected primary formulations

[McDermott 2014](https://tsapps.nist.gov/publication/get_pdf.cfm?pub_id=914205),
sections 3.2 and 5, constructs discrete enthalpy/product-rule corrections for
low-Mach divergence constraints, including numerical mixing. Its pressure
decomposition differs from this fully compressible p/hs update, but the broad
compatible-product-rule principle is established.
[Grapsas et al.](https://arxiv.org/abs/2010.07577), section 6, proves a reactive
staggered pressure-correction total-energy identity using kinetic dissipation
correction and specific density histories. [Denner et al.](https://arxiv.org/abs/2002.10482)
uses a collocated coupled p,U,T system. None of these comparisons establishes
novelty for either proposed local or scalar correction; targeted searches and
equation-level validation remain required.
