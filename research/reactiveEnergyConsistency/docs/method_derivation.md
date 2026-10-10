# Constraints on a correction: no method accepted

The baseline equations and exact measured identity are derived in
discrete_energy_derivation.md. The first milestone identifies a dominant
net density/enthalpy/formation-energy replacement in the moving case. It does
not establish that a kinetic or pressure-work-only correction will improve
the fully recomputed solution. No correction code is implemented.

## Why the obvious frozen-state modification is inconsistent

At a final cell state for the selected perfect-gas sensible-enthalpy model,

```
p = rho R(Y) T,    hs=hs(T,Y),    d hs/dT=Cp(T,Y)>0.
```

At fixed rho, p and Y, the EOS fixes T and therefore hs. A nonzero change in
hs while retaining those three quantities violates the thermodynamic closure.
If only hs changes and thermo is corrected at fixed p and Y, to first order

```
delta T = delta hs/Cp,
delta rho = -rho delta hs/(Cp T).
```

This generally changes both local continuity and integrated species masses.
If rho is held instead, pressure must change as
`delta p=rho R delta hs/Cp`, changing pressure gradients and the already
corrected momentum/flux state. Except in special spatially uniform cases,
a local enthalpy adjustment thus requires coupled pressure/flux treatment.
This is a limited no-go result for retaining the *entire final state*, not a
proof that all inexpensive conservative corrections are impossible.

## Why final continuity residual alone is insufficient

The exact Euler finite-volume product identity is

```
D_t(rho hs) + D_phi(hs) - hs_c [D_t rho + D_phi(1)]
 = rho_old (hs_c-hs_old)/dt
   + (1/Vc) sum_faces phi_cf (hs_face-hs_c).
```

The baseline already solves the conservative LHS transport. There is no
missing `hs R_rho` source to insert merely by analogy with an advective
equation. Its measured DrhoH instead reflects changing the coefficient
*after* that conservative solve. Final continuity can be small while
`sum V delta rho hs` is large, because zero integrated delta rho does not
imply zero enthalpy-weighted delta rho. A final-residual correction would
not account for that mismatch without a new coupling derivation.

## Conditions for proceeding

Any modified local equation must conserve absolute rhoE with the *same*
species/formation-energy fluxes and sources, enforce EOS and continuity,
and quantify its momentum-pressure residual. Holding one subset of variables
requires an explicit consistency argument for the others. A full extra
energy equation followed by unexamined rho=thermo.rho is not automatically
conservative either.

Possible limited pressure-energy iterations are established prior art in
related discretizations. Full SCI comparison and a rigorous modified-equation
derivation are still required before implementation. Expected order,
positivity, stability, differential diffusion and method cost cannot be
asserted from this audit. H3/H4 and method-level H5 remain untested.
