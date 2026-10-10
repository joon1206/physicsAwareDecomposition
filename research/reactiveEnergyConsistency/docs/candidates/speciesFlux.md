# Final-flux conservative species correction (diagnostic pivot)

Hypothesis: applying the final density and pressure-corrected mass flux to the
same saved species source removes the elemental drift seen in the variable
composition control. It tests the species half of a future compatible coupling.

For all species, including the inert species, define the final-flux residual
`r_s=V(rho_f Yi_b-rho_n Yi_n)/dt+B_f(Yi_b)-L_f(Yi_b)-R_s`.
Solve `[V rho_f/dt+B_f-L_f] delta Yi=-r_s`, with frozen chemistry rates.
This is the exact conservative Euler species balance at the final rho,phi.
The source includes density replacement, changed flux and the inert algebraic
closure residual. It is not a local rescale or normalization.

If sum R_s=0, all species use the same linear transport, and final rho,phi
satisfy continuity, the sum of corrected Yi is one to solver tolerance.
The net boundary species flux is retained. Negative Yi or normalization failure
reject the candidate; no clipping/renormalization hides the residual. The
energy ledger adds `DpostC=V rho_f(hc_final-hc_b)` to measure the changed
formation inventory. Sensible enthalpy is held, thermo is reinverted and pressure
is updated to enforce EOS with fixed density. Thus the pressure/momentum
compatibility problem remains explicitly measured; this is not yet an accepted
energy-conservative method.

For smooth coefficients this corrects the frozen-source Euler species equation
at O(dt) temporal accuracy. Reaction splitting error is unchanged. Positive
diagonal capacity and upwind convection help admissibility but do not guarantee
it for inconsistent rates. Cost: one scalar solve per species and thermo refresh,
without repeating chemistry or momentum assembly. Strong competitors are more
pressure and outer corrections. Conservative multispecies shared-flux transport
is established prior art, so this diagnostic has IMPLEMENTATION_ONLY status
unless it supports a specifically new combined method.

Screen A/B/F/Mix, altered dt, elemental gauge, local ledger, species masses,
EOS, pressure/momentum mismatch and wall time. Promotion requires simultaneous
energy/accuracy improvement and compatible pressure correction, not species
conservation alone.
