# Conditional scalar invariant recovery on continuous data

The mandatory clean-versus-legacy report has been written before this prototype.
It establishes that the CFD density defect remains and that continuous data do
not guarantee the unchanged spatial source gate. This is an established
projection baseline, not a claimed novel method.

Given an accepted species vector Y* whose mass/elements and nonnegativity pass,
solve sum_i Y*_i e_i(T)=e_initial for CV, or sum_i Y*_i h_i(T)=h_initial for
physical CP. Temperature recovery changes no species. At CV hold rho and set p
from EOS; at CP hold p and recover rho. Positive mixture capacity and an
admissible target ensure a unique root in the continuous valid interval. A
safeguarded Newton iteration uses the corresponding mixture Cv or Cp. A
projection cannot repair an inadmissible species update without an additional
constrained solve. No negative clipping or species normalization is introduced.

Predeclared controls: H2 and GRI, each with Cp/h/s continuous data, physical
CV/CP, initial T=999/1100/1500 K, TF=10 us for the branch state and 240 us
otherwise. Compare provisional BDF at rtol=1e-4/1e-6/1e-8/1e-10,
atol=1e-16, post-step scalar recovery, and strict reference at 1e-12/1e-13.
Use an independent Python NASA evaluation for recovery; compare its properties
and restored invariant with Cantera. The reference integration uses the same
Cantera BDF implementation as the provisional integration; this is a tolerance
baseline, not independent verification of that integrator. Earlier native
Rosenbrock source comparisons provide the separate implementation controls.

Record dimensioned and normalized invariant residual, elemental/mass residuals,
EOS, positivity, T and every species error, and root evaluations. Recovery
passes if relative invariant residual <=1e-10, EOS <=1e-10 relative,
elemental <=1e-12 kg_element/kg, no negative species and a positive valid T.
These gates do not certify trajectory accuracy. Compare all species errors;
the scalar operation leaves them exactly unchanged. A strict reference
tolerance contrast remains an uncertainty estimate, not proof of exactness.

Falsification target: a blanket accuracy/cost superiority over tighter ODE
tolerances fails if tighter integration substantially improves any resolved
species error that scalar recovery leaves untouched, or if scalar recovery
worsens temperature error. This rejects universal endpoint dominance, not all
adaptive constrained integration. Rotation of three uncontended timing trials
must be separate from the concurrent CFD campaign before cost claims.

Novelty: the constrained problem is a specialization of CVODE eq3.11–3.12;
conservative CV/CP energy state/recovery is also established in reactor/CFD
codes. Even successful invariant restoration cannot pass broad method novelty.
