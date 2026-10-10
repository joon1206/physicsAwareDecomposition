# Linearized scalar density-defect corrector (C)

Hypothesis: one scalar correction matrix can remove the density coefficient
defect while exchanging the correction through conservative face fluxes.

At fixed rho_f,Y,U the thermochemical volumetric inventory is rho_f ea(T,Y).
Since d hs/dT=Cp and d ea/dT=Cv, its Jacobian with respect to hs is
`c=rho_f Cv/Cp`. Derive a correction delta hs from

```
[c/dt + div(phi,.) - laplacian(alphaEff,.)] delta hs
   = -(rho_f-rho_a) ha_b/dt.
```

The source is the exact measured coefficient replacement divided by dt.
This is a linearized defect equation, not another original sensible-enthalpy
solve. Apply hs+=delta hs, invert thermodynamics, and enforce
p=rho_f/psi(T,Y). The actual energy increment is
`rho_f delta hs-delta p`; it differs from `c delta hs` by thermodynamic
nonlinearity. Summed face exchanges cancel on periodic boundaries; physical
boundary correction fluxes must be recorded for other domains.

For smooth delta rho=O(dt), the local nonlinear remainder is O(dt^2) per
application if derivatives are bounded. This is conditional and does not
establish convergence of the full segregated algorithm. Positive Cv/Cp gives
positive capacity; bounded convection and positive diffusion can make the
linear matrix admissible, but the nonlinear target may still become unphysical.
The pressure response is unaccompanied by a momentum/phi update, as in A.
Both methods may be reference dependent when only the density term is corrected.

Cost: one additional scalar matrix assembly/solve, thermodynamic refresh,
boundary exchanges and linear solver reductions. Compare with more pressure
corrections, another full outer loop, dt/2 and dt/4. Prior art includes
conservative pressure-based coupled methods and low-Mach enthalpy defect
corrections; no novel generic defect-correction principle is claimed.

Screen identically to A. Accept only a closed ledger with independently
improved solution error, conserved mass/elements, positivity, EOS consistency,
bounded pressure/momentum mismatch and useful cost. Reduced global drift
without local or solution accuracy is a rejection.
