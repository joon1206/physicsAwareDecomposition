# Claim ledger

| Claim | Classification | Evidence/condition |
|---|---|---|
| Pressure-based compressible conservation is possible. | ESTABLISHED | van der Heul; Denner; conservative time-staggered work. |
| Reactive sensible-enthalpy pressure correction can conserve a discrete total energy. | ESTABLISHED | Grapsas et al., sections 5–6. |
| Minimizing implied kinetic-energy dissipation in OpenFOAM is new. | UNSUPPORTED | Hassanaly and other low-dissipative implementations precede it. |
| Steady-state-preserving chemistry splitting is new. | UNSUPPORTED | Speth, Wu, Zhou. |
| reactingFoam-SCI implements essentially the specific correction envisioned here. | PARTIALLY ESTABLISHED | Improved splitting established; exact finite-pressure-iteration energy modification not accessible/verified. |
| The exact v2012 collocated final-state equation attribution is present in searched literature. | NOT ESTABLISHED IN SEARCH | Absence limited to documented search; no originality conclusion. |
| A density/enthalpy/composition consistency extension moves the accuracy/cost frontier. | PROPOSED NOVEL EXTENSION | Requires method derivation, full prior-art comparison, local accuracy/MMS and timing evidence. |
| A kinetic-only final-state correction is sufficient for the moving hydrogen case. | UNSUPPORTED | Must be tested against the closed baseline budget; no corrected run currently supports it. |
| Chemistry ownership is responsible for the physical energy drift. | UNSUPPORTED | Native/balanced equivalence is a test, not an assumption. |
| Global energy conservation establishes local solution accuracy. | UNSUPPORTED | Integral closure cannot replace field/reference convergence. |
| Baseline finite total-energy drift exists despite corrected initialization. | ESTABLISHED | Published actionStudy and independently executed reproduction. |
| A budget can separate time, linear, roundoff, splitting and thermo errors uniquely from snapshots. | UNSUPPORTED | Exact equation identity separates state/operator mismatches; truncation attribution requires independent refinements/reference trajectories. |

Measured results are reported in audit_results.md and machine-readable gates.
This ledger does not accept a method before the first milestone closes, or
claim a publication-standard result from a coarse local audit.

## 2026-10-07 — continuous-thermo and invariant-map continuation

The original table records initial hypotheses. The earlier “PROPOSED NOVEL
EXTENSION” label is a proposal, not established originality or demonstrated
advantage. The present tested extension families have no publication survivor.

| Current claim | Classification | Evidence and limits |
|---|---|---|
| Making h/s and Cp continuous removes the original CFD density/enthalpy defect. | FALSIFIED IN MATCHED CONTROLS | H2 and GRI retain the defect; exact eight-term budgets close. See clean_vs_legacy_results.md. |
| The legacy breakpoint data causes the persistent direct source-energy floor. | ESTABLISHED FOR DIRECT CONTROLS | HS/CpHS with identical kinetic input remove it; native Rosenbrock and independent Cantera agree. Thermo changes equilibrium-derived reverse rates. This does not attribute every spatial source error. |
| Continuous thermo guarantees the unchanged spatial source gate. | FALSIFIED | Retained hot continuous-data calls exceed 1e-10; source tolerances are not nonlinear invariant certificates. |
| Data and pressure coupling are separate mechanisms with no interaction. | PARTIALLY ESTABLISHED / OVERSTRONG AS STATED | Distinct identities and interventions identify surviving mechanisms; measured two-factor interactions exclude a universal independence claim. |
| Scalar invariant recovery preserves every species and can restore E/H conditionally. | ESTABLISHED / KNOWN METHOD | Positive capacity and target in admissible image; provisional species must already pass mass/elements/positivity. |
| Scalar endpoint recovery dominates tighter ODE tolerances in trajectory accuracy. | FALSIFIED | 25 of 40 eligible cases worsen T error; species error remains unchanged; two recoveries fail mass/element gates. |
| Finite species increments with formation-energy transfer are a new native method. | REJECTED AS EXISTING IMPLEMENTATION | Installed integrated solve already returns finite RR and Qdot from it. |
| An invariant chemistry map alone guarantees total CFD energy conservation. | FALSIFIED | Independent two-cell counterexample plus matched CFD source/density ledger. |
| Mechanism jump ranking alone certifies source or CFD accuracy. | FALSIFIED AS SUFFICIENT CERTIFICATE | Crossing dependence, remaining smooth numerical errors and CFD coupling survive; observed event weights are not prospective prediction. |
| HS/CpHS provide more physically accurate legacy thermochemistry. | UNVERIFIED | Original source data absent; controls preserve references but are sensitivity replacements, not validated database fits. |
| Generic continuity reconstruction or numerical-consequence prediction is novel. | REJECTED AS PRIOR ART | NASA PAC, RMG, Boettcher and Mech Checker exact methods inspected. |
| These tests exhaust all future reacting-flow numerical methods. | UNSUPPORTED | Exhaustion is bounded to the defined repair/projection/interface classes and previously tested cheap coupling formulations. |

The full constrained projection constraint is A(Y*+delta Y)=A Y_old.
A delta Y=0 alone cannot remove a provisional element residual. No endpoint
conservation result is substituted for local reacting accuracy or an
uncontended runtime/memory frontier.
