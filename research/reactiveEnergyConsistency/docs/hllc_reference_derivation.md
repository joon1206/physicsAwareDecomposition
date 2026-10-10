# Contact-resolving independent reference

Hypothesis, before implementation: the central-upwind reference's acoustic
numerical diffusion contaminates an ignition-kernel comparison at low Mach
number. A standard first-order HLLC conservative flux provides a useful
independent check with resolved contact transport. This is a known reference
method, not a proposed new numerical contribution.

The conserved variables and native chemistry/EOS remain the central reference's
rho, rhoU, all rhoYs and rhoEa. Ea includes absolute internal and kinetic energy.
For a face unit normal n, let uK=UK dot n, EK=rhoK (eaK+|UK|^2/2), and
cK=sqrt(CpK/CvK pK/rhoK). Use bounding estimates

```
SL = min(uL-cL,uR-cR), SR = max(uL+cL,uR+cR),
SM = [pR-pL+rhoL*uL*(SL-uL)-rhoR*uR*(SR-uR)]
     /[rhoL*(SL-uL)-rhoR*(SR-uR)].
rhoK* = rhoK*(SK-uK)/(SK-SM),
UK* = UK+(SM-uK)n,
EK* = rhoK* [EK/rhoK+(SM-uK)(SM+pK/(rhoK*(SK-uK)))].
```

Select FK when all waves travel toward the other cell, or
FK*=FK+SK(QK*-QK) in the appropriate star region. Multiply each flux by face
area. Species star states use rhoYs*=rhoK* YsK. Consequently their flux is
mass-flux times the selected side's Ys and sums to the continuity flux. Momentum
and energy use the same star region. The energy equation receives no reaction
heat source: chemical energy is already part of Ea.

Face-flux cancellation gives global mass/species/momentum/energy conservation
on periodic boundaries, independent of the accuracy of the wave approximation.
EOS is recovered through the cancellation-aware Cv root after each Euler step.
No general positivity or entropy theorem for the selected JANAF mixture and
wave bounds is assumed. The reference rejects negative species, nonpositive
rho/Cv/p/T, or an unattainable energy target; it does not clip or normalize.
Scope remains fixed mesh, inviscid, closed periodic/symmetry/empty conditions.

Verify constant-Cp entropy-wave contacts, analytic synthetic reacting transport
and the independently matched homogeneous detailed-chemistry reference before
using a hydrogen trajectory. Then compare mesh/time refinements and both
independent flux families. A single better-looking burned curve is insufficient.
The same first-order temporal limitations apply to frozen old-state chemistry.

Primary equation source: [Toro 2012 author lecture](https://www.prague-sum.com/download/2012/Toro_2-HLLC-RiemannSolver.pdf),
equations 26–39 for star states/flux, pages 23–25 for general EOS and chemical
species. The original method is [Toro, Spruce and Speares 1994](https://doi.org/10.1007/BF01414629).
The use of mixture sound speeds and absolute chemical energy is a reference
implementation of those jump relations; it does not establish new HLLC theory.
