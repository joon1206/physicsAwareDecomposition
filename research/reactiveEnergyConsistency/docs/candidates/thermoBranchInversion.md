# Missing and multiple conservative temperature roots in discontinuous NASA data

2026-10-06. Derivation before the exact algebraic screen. IMPLEMENTATION_ONLY
as a thermodynamic data-validation diagnostic, not a numerical-method novelty.

## Hypothesis and derivation

The direct source audit verifies finite high/low enthalpy jumps in the unchanged
legacy mechanism. Positive Cv within each polynomial branch does not imply
continuous, globally invertible mixture energy. At fixed positive rho and Y,
define e_low(T,Y), e_high(T,Y), switching at m=1000 K, and

    J(Y)=e_high(m,Y)-e_low(m,Y).

If Cv>0 on both valid branches and J>0, every target strictly inside
(e_low(m,Y),e_high(m,Y)) has no temperature root in their combined range.
If J<0, every target inside (e_high(m,Y),e_low(m,Y)) has a root on each
branch when the range endpoints bracket it. Both EOS pressures rho R(Y)T
are admissible. Positive branch Cv supplies neither surjectivity nor global
uniqueness. An elemental energy reference shift adds the same constant to
both branches and target; it cannot change the gap/overlap.

## Predeclared actual-data examples

For a positive gap, start from the direct probe's H2/air/radical mixture at
999 K, rho=1. Preserve its absolute internal energy and change composition
by a balanced extent x of H2+0.5 O2 -> H2O. Mixture energy is linear in Y.
Choose x algebraically so the conserved initial energy equals the midpoint
of the target composition's low/high energy values at 1000 K. Check all
mass fractions, total/elemental mass, EOS and a strictly positive gap.
This is a possible conservative state target, not an actual integrated
reaction path or validated flame.

For an overlap, use pure N2 and the midpoint of its low/high 1000 K energies.
Find both roots with their own branch polynomial and retain their temperatures
and pressures. Do not clip or repair either thermodynamic polynomial.

Certify positive Cv on each branch over 200–1000 and 1000–5000 K with
natural interval bounds of its quartic polynomial on 10 K subintervals.
Evaluate bounds with exact rational arithmetic for the declared binary
coefficient/weight values; require a positive lower bound. Numerical endpoint
root residuals are diagnostics, not the basis of the existence proof.

This directly limits previous unqualified statements that positive Cv alone
guarantees a global monotone/unique temperature recovery. Executed inventories
and root residuals remain evidence for those specific successful cases. The
fixed rho,p,Y impossibility still holds because the perfect-gas EOS already
fixes T; it does not rely on crossing-branch enthalpy monotonicity.

## Prior work, cost and decision rule

[Cantera NasaPoly2 continuity checks](https://www.cantera.org/3.2/cxx/d6/de1/NasaPoly2_8cpp_source.html)
make polynomial continuity an explicit existing validation concern. This
screen costs a few exact scalar polynomial evaluations and no CFD solve.
It cannot count as a new conservative projection or cure the original density
pair. A continuity-adjusted data model would need newly matched physical
thermochemistry/references; it cannot silently replace accepted inputs.

## Executed counterexamples

The admissible balanced H2/air target has a positive gap of 0.07407165 J/kg,
and the conserved target lies strictly inside it. Mass change is zero;
elemental differences are below 4.3e-18. Rational natural interval bounds
give minimum Cv above 968.16/1143.84 J/kg/K on low/high branches. Hence no
valid root exists anywhere in the declared 200–5000 K range for this target.

Pure N2 has an overlap of 0.01588887 J/kg. Its two valid temperatures are
999.9999908968 and 1000.0000091032 K, with EOS pressures
296803.3152283 and 296803.3206320 Pa at rho=1. Branch Cv lower bounds exceed
725.96/869.24 J/kg/K. Both numerical energy residuals are below 6e-11 J/kg.
The rational positive-derivative certificates, gap/overlap values and branch
validity supply the existence argument; the small root residuals alone do not.

Decision: REJECT a global root/uniqueness guarantee from positive branch Cv
alone. Keep the actual-data negative examples in
candidateStudy/data/raw/ThermoBranchInversion_analytic and processed
thermo_branch_inversion.json. Their narrow gaps do not explain the original
17.3887% energy drift or the nonzero-transport Mix partition discrepancy.
