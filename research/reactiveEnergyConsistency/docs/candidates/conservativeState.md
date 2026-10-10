# Shared-flux species plus nonlinear absolute-energy correction (G/pivot)

Hypothesis: the final mass flux can advance all rhoY and absolute total energy
consistently without a repeated chemistry call. SpeciesFlux tests establish
elemental conservation but also show that changing species alone worsens energy.

First solve the saved-source conservative species equations at rho_f,phi_f as
derived in speciesFlux.md. At fixed rho_f,Y_f,U_f,phi_f define the actual energy
residual in each cell in watts:

```
rE = V[(rho_f(hs+hc+K_f)-p) - E_n]/dt
   + B_phi(hs)+B_phi(hc)+V div(phi,K_f)
   - L_alpha(hs)-sum_s Hc_s L_mu(Ys).
E_n = rho_n(hs_n+hc_n+K_n)-p_n.
```

All convection operators use the same final upwind mass flux; diffusion and
kinetic terms are the actual selected model operators. Chemical conversion
cancels between Qdot and saved Hc-weighted species rates to roundoff. The
formation diffusion term is required by the absolute energy obtained by adding
the species and sensible-enthalpy equations. It is not an added physical heat
source. There are no external sources in these screening domains.

Solve Newton defect equations
`[V rho_f Cv/Cp/dt+B_phi-L_alpha] delta hs=-rE`, update hs, invert T, and set
`p=rho_f R(Y_f)T`. Recompute the nonlinear residual until a specified absolute
local tolerance is met, or retain a convergence/admissibility failure. Then
`Delta E_i+dt F_E,i=0` to tolerance. Sum internal/processor/cyclic fluxes in
pairs to obtain the global identity. The species residual gives a compatible
elemental gauge: shifting Ha,Hc by elemental constants changes the energy
residual by the corresponding species/element residual, not an isolated
rho*Ha term. The exact midpoint product identity is a consequence, not a
separate numerical principle or proof of higher order.

This remains an Euler frozen-source correction. No improved temporal order is
claimed. Cv>0 and admissible temperatures are required; Newton iterations may
fail for large time steps. Cost: species matrices plus one or more scalar energy
matrices and thermo refreshes. This is distinct from repeating the original
EEqn: it enforces the full absolute energy residual, uses its internal-energy
Jacobian, final density/flux, and compatible species state.

Pressure changes remain unpaired with momentum and face-flux recalculation.
Therefore the current fixed-flux construction must be rejected or followed by
a pressure/energy/species coupling correction if reference or momentum errors
are unacceptable. A 2x2 pressure/energy correction that omits induced species
flux changes would not satisfy the established elemental gate.

Closest prior art: Sirianni et al. conservative primitive updates; Grapsas
reactive energy correction; Denner collocated conservative coupled p,U,T;
McDermott low-Mach enthalpy/species compatibility. The broad method principle
is prior art. Precise low-cost segregated extension novelty is not established.

Screen A/B/F/Mix and dt/2; then analytic entropy-wave errors, elemental gauge,
strong coupling baselines and cost. Promote only for simultaneous local energy,
elemental/EOS/admissibility, solution accuracy and useful coupling consistency.
