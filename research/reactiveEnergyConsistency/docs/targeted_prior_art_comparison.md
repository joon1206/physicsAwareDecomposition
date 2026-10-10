# Equation-level novelty audit after candidate results

Accessed 2026-10-06. These comparisons concern mathematical ingredients. An
overlap in ingredients does not establish that every line of either prototype
is an identical published algorithm. Conversely, implementation differences
do not establish a new numerical-method contribution.

## Conservative segregated compatibility predates this study

Rauwoens, Vierendeels, Dick and Merci, *A conservative pressure-correction
scheme for transient simulations of reacting flows*, JCAM 234 (2010),
2311-2318, DOI 10.1016/j.cam.2009.08.087. The openly available author manuscript
was read through its governing and algorithmic equations, not just its abstract:
[UGent manuscript](https://backoffice.biblio.ugent.be/download/1015350/1015356).

Equations 14-15 advance density and each conservative scalar. Equations 16-18
insert the discrete subsequent-step density/scalar equations into the EOS
constraint `H(rho,rho*y1,...)=0`. For the reacting mixture-fraction example,
equations 23-24 form the nonlinear pressure-dependent compatibility equation;
equations 25-26 apply a Newton linearization with both density and scalar
pressure-response operators, `A-HC'(f*)B`. This is direct prior art for deriving
pressure coupling from the *discrete* conservative scalar/EOS constraints.
Equation 7 includes static formation plus sensible enthalpy under its low-Mach,
unity-Lewis assumptions; it is not a compressible detailed-chemistry proof for
our prototype. The worked example uses a Burke-Schumann flamesheet and a
piecewise density/mixture-fraction relation. Those scope differences remain.

Our frozen-source block instead iterates current-step pressure, all species
and absolute total energy, retains the v2012 frozen momentum diagonal, and
includes compressible kinetic/pressure inventory. It is not their particular
next-step constraint. However, claims that discrete compatible conservative
pressure/scalar/EOS coupling, or its reacting extension, are new are rejected.
No new theorem or useful efficiency advantage has been established for the
remaining specific differences in our construction.

The related 2009 JCP article is verified bibliographically at
[UGent](https://biblio.ugent.be/publication/715606), DOI
10.1016/j.jcp.2009.03.036; its deposited PDF is restricted. Do not treat its
unread detailed equations as additional verified evidence. The open 2010
manuscript supplies the equations used above.

## Conservative thermodynamic variable updates

[Sirianni, Guardone, Re and Abgrall 2024](https://arxiv.org/pdf/2404.07710),
sections 2.2.1-2.2.2, equations 7-24, derive a primitive thermodynamic update
from conservative mass/momentum/total-energy residuals and correct the
thermodynamic derivative using a secant iteration to recover the exact energy
jump. Our fixed-rho nonlinear absolute-energy inversion is a different
segregated implementation with species sources, but the broad conservation
principle and local thermodynamic inversion are established. Its species and
momentum defects cannot be resolved by citing that prior formulation.

## Coupled energy and product linearization

[Denner, Evrard and van Wachem 2020](https://arxiv.org/pdf/2002.10482), section
5 and equations 33, 40-52, solve collocated conservative equations in p,U,T
using Newton product linearizations and a momentum-weighted common advecting
velocity. Their system includes energy/pressure/velocity coupling and EOS
closure. Our frozen-source block Gauss-Seidel is an approximation with species
inside the thermodynamic block. Schur reduction, freezing coefficients and
avoiding a repeated chemistry call are implementation/solver choices until a
new analysis or verified favorable accuracy/cost regime is demonstrated.

[McDermott 2014](https://tsapps.nist.gov/publication/get_pdf.cfm?pub_id=914205),
sections 3.2 and 5, already treats discrete enthalpy product-rule/numerical
mixing compatibility in a low-Mach formulation. [Grapsas et al.]
(https://arxiv.org/pdf/2010.07577), section 6, supplies reactive pressure
correction energy identities including kinetic corrections and a modified
discrete energy. Our unmodified physical total-energy ledger must not be
equated with that modified norm without accounting for its extra terms.

## Energy-driven adaptive coupling

[Sadjina and Pedersen 2016](https://arxiv.org/pdf/1606.05168), equations 3 and
14-15, use exchanged-energy residuals to control the coupling macro step in
noniterative co-simulation. This is conceptual prior art for residual-driven
adaptive coupling, not an identical reacting FVM formulation. No analogous
guaranteed solution-error estimate follows from our closed ledger alone.
The conservative coarse reacting trajectory is a direct counterexample to
using its scalar energy error as such a bound. Formation-reference changes
also preclude a robust controller based solely on the isolated rho*Hc term.

Decision: no tested formulation has established novelty. Accurate, inexpensive
chemistry/species/pressure adaptation with a verified estimator remains a
separate unresolved extension. An ordinary residual stopping tolerance is not
promoted as that extension.

## Further coupling pivots already have specific prior art

[Nonaka et al. 2012](https://ccse.lbl.gov/Publications/nonaka/LMC_SDC.pdf),
Combustion Theory and Modelling 16(6), DOI 10.1080/13647830.2012.701019,
was read through sections 2 and 3.2. Equations 2–5 conserve species and
formation-inclusive enthalpy; section 2 corrects species diffusion fluxes so
they sum to zero. Equation 10 supplies an EOS volume-discrepancy correction.
Equations 14–22 derive iterative advection/diffusion/reaction residual
corrections; equations 18–19 use an effective reaction contribution from an
ODE integration augmented by other processes. This is specific prior art for
compatible multispecies/enthalpy transport and deferred thermochemical
coupling, beyond merely adding outer iterations. Its low-Mach constraint,
second-order time-centred transport and repeated chemistry differ from our
compressible Euler/frozen-source block. Promoting a generic deferred coupling
or formation-aware transport pivot would therefore be unsupported. A genuinely
new reduced-cost error estimator or coupling approximation still needs its
own analysis and accuracy/cost evidence.

[Zivkovic et al. 2026](https://juser.fz-juelich.de/record/1052970/files/1-s2.0-S0029549325007381-main.pdf),
Nuclear Engineering and Design 446, 114561, section 2.1 explicitly describes
containmentFOAM's additional PIMPLE density corrector and inter-species
enthalpy transport, attributing those changes to Kumar et al. 2019. This
accessible primary paper confirms the previously noted implementation family;
it does not publish the exact discrete correction in that paragraph. We do
not infer equation equivalence from it. Its gas-distribution solver and
progress-variable flame-propagation solver have different models from this
study's detailed-chemistry periodic kernel.

## Energy-derived pressure correction and conservation audits

[Van der Heul, Vuik and Wesseling 2002](https://diamhomes.ewi.tudelft.nl/~kvuik/papers/Heu02VW.pdf),
IJNMF 40, 521-529, DOI 10.1002/fld.322, section 6 was read. Equation 14
advances density, equation 15 predicts momentum, and equation 18 postulates
the pressure-dependent velocity correction. Substitution into total energy
gives equation 19; its linearization supplies a modified pressure Poisson
equation, followed by pressure/momentum updates in equations 20-21. Setting
the magnetic field to zero gives Euler. The staggered, constant-gamma method
differs from our collocated NASA mixture/frozen-source block, but establishes
energy-derived conservative segregated pressure correction well before this
study. A generic approximate-Schur or energy-based pressure-correction pivot
therefore cannot be claimed as new. The related 2003 Computers & Fluids
paper is bibliographically confirmed on the author's publication page;
unavailable full equations from that paper are not used here.

[Frias, Gutierrez Marcantoni and Elaskar 2025](https://www.mdpi.com/2075-1680/14/11/782),
Axioms 14(11), 782, DOI 10.3390/axioms14110782, sections 2 and 3 were accessible
in the publisher's indexed full text despite direct-page fetch failures.
Equations 7-8 evaluate volume, boundary and source integrals for conservation
audits, using Simpson integration. Their reactive shock-reflection study
includes mass, momentum, energy and individual species and explicitly
acknowledges postprocessing integration error. Thus integral reactive-flow
conservation auditing is prior art. Our algebraically closed cellwise matrix
ledger separates equation stages and actual discrete species/source residuals;
it must not be conflated with an independently quadrature-evaluated continuum
balance. That distinction may support a reproducible diagnostic contribution,
but alone does not satisfy the requested new-method publication gate.

## Unequal-thermodynamic pressure-equilibrium pivot

[Ching, Johnson and Kercher 2025](https://arxiv.org/html/2501.12532v1),
equations 2.14-2.15, derives a thermodynamic condition for pressure equilibrium.
Equations 3.8-3.12 restore semidiscrete energy conservation by residual
corrections; later modifications address equilibrium and zero-species
preservation. DG-specific proofs and fully discrete limitations remain distinct
from our cell-centred FV implementation. The associated mixture wave and
common-weight remapping calculation are controlled diagnostics, not a new
equilibrium-preserving algorithm. See candidates/mixturePressureCompatibility.md.

## Chemistry thermal-path pivot after measured results

[Cantera IdealGasReactor](https://cantera.org/stable/reference/reactors/ideal-gas-reactor.html)
provides the standard species/internal-energy reactor equations. A native Cv
source therefore supplies established closed-volume physics, not a new method.

[PelePhysics CVODE implementation](https://pelephysics.readthedocs.io/en/latest/CvodeInPP.html),
the different-reactors section, was read at equation level. It distinguishes
fixed-density internal-energy and fixed-density enthalpy source models, with
external source forcing available for transport coupling. Its zero-forcing Cv
limit coincides with our homogeneous control. It also documents independent
Cantera reactor validation. State variables/integrator differ from the v2012
native-source port, but the underlying thermal-path and forcing principles
already exist. Both path selection and a generic transport-augmented reaction
ODE remain IMPLEMENTATION_ONLY without a new analysis or cost/accuracy result.

The corrected adapter's small homogeneous error is empirical evidence for the
identified source-path limitation in this selected algorithm, not proof that
constant-pressure subproblems are universally inappropriate. ODESystem.H and
Rosenbrock34.C were inspected locally; their explicit-time derivative callback
was separately probed because an initial new adapter returned the wrong vector.
Superseded raw runs remain distinct and excluded from current scientific claims.
