# Coupling-tolerance pivot: bounded momentum mismatch

Hypothesis (written before these variants): requiring pressure/species/energy
block convergence to 1e-8 relative pressure may solve the splitting equations
more accurately than the Euler discretization warrants. Stopping earlier can
retain exact local energy/species balances with bounded remaining pressure
gradient mismatch and materially fewer global solves. This is a cost/accuracy
experiment, not a new conservative equation or claimed new adaptive method.

Each completed block sweep solves the final-flux species and absolute energy
residuals at the same stored rho and phi. The final energy inversion changes
p but not rho, so these conservative equations still hold after the sweep.
Continuity uses that sweep's stored rho and pressure-derived phi. The remaining
momentum inconsistency is precisely

```
delta U_i = -rAU_i grad_i(p_energy - p_momentum).
```

For an orthogonal uniform mesh and a fixed linear gradient operator G,
`max|delta U| <= max(rAU) ||G||inf max|delta p|`. Therefore a specified pressure
tolerance bounds this defect by a computable mesh-dependent quantity. Relative
pressure change alone has no mesh-independent velocity bound and does not
bound chemical ignition error. The implementation already measures the actual
gradient mismatch; report it rather than infer accuracy from the tolerance.
No claim of entropy stability or a guaranteed PDE solution-error estimator is
made. Holding a nonzero tolerance fixed under mesh/time refinement cannot
justify an improved asymptotic order; a tolerance coupled to a verified
discretization-error estimate would be needed for such a claim.

Screen F at 1 us and Mix at 2 us with pressure stopping tolerances 1e-2, 1e-3,
1e-4, against the existing 1e-8 construction. Compare actual momentum mismatch,
T/U/species fields, conservation, number of solves and runtime. Any useful
point needs the same independent and resolved reacting validation as the full
block. A faster wrong or quenched trajectory is rejected. Test the coarse
2 us ignition failure as a negative control if a point appears useful.

Closest prior: Denner et al. 2020 section 5, nonlinear residual stopping of
coupled conservative systems; Rauwoens et al. 2010 equations 23-26, Newton
iteration of the discrete conservative EOS compatibility condition. Inexact
block Gauss-Seidel/Newton and tolerance selection are established techniques.
Sadjina and Pedersen 2016 equations 14-15 already use energy residuals for
adaptive coupling time control in co-simulation; that is broader conceptual
prior art, not an identical reacting CFD scheme. Our coarse conservative F
case also gives a counterexample to treating energy residual alone as an
accuracy bound: near-zero energy residual coexists with an unignited trajectory
and a >2100 K difference from the finer burning trajectory.

Status: NOVELTY_NOT_ESTABLISHED. An implementation/cost tradeoff alone cannot
pass the novelty gate. Reject an energy-only adaptive controller as a reliable
general accuracy controller; retain combined residual/accuracy estimation as
an unresolved question if the measured tolerance tradeoff warrants it.

Primary sources:
[Rauwoens et al.](https://backoffice.biblio.ugent.be/download/1015350/1015356),
[Denner et al.](https://arxiv.org/pdf/2002.10482),
[Sadjina and Pedersen](https://arxiv.org/pdf/1606.05168).
