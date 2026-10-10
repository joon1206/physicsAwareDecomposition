# Novelty search, 2026-10-06

No method novelty is accepted by this search. The baseline audit is allowed;
implementing a correction and presenting it as a new conservation principle
is not. Search absence is not proof of originality.

## Query record

The web search used broad synonymous formulations and exact phrases, with
follow-up primary-source retrieval. Exact overly narrow formulations often
returned no directly relevant result. The following subjects were searched:

| Search formulation | Relevant primary leads |
|---|---|
| reactingFoam energy conservation; OpenFOAM reacting flow energy conservation | Yang et al. 2019; native energy source; recent rhoCentralRfFoam integral conservation assessment |
| pressure-based reacting solver energy consistency; PIMPLE total energy conservation | Grapsas et al. 2020; pressure-correction conservation literature |
| pressure correction enthalpy consistency; total enthalpy pressure work OpenFOAM | Grapsas et al.; OpenFOAM pressure-work history; v2606 energy sources |
| discrete kinetic energy pressure correction OpenFOAM | Hassanaly et al. 2017; low-dissipative compressible OpenFOAM work |
| reactingFoam operator splitting accuracy; steady-state preserving chemistry splitting | reactingFoam-SCI; Speth et al.; Wu et al.; Zhou et al. |
| conservative pressure-based compressible solver | van der Heul et al. 2003; Denner et al. 2020; Amino et al. 2022 |
| species diffusion enthalpy consistency; reaction heat release enthalpy consistency | native Qdot/Hc sources; detailed transport implementations; Foundation multicomponent transport |
| discrete continuity correction energy equation | pressure-correction/internal-energy consistency literature; Hassanaly continuity formulation |
| reactingFoam-SCI github; OpenFOAM Cantera source | no verified SCI source repository located; paper abstract retrieved, full text unavailable |
| current OpenFOAM releases and EEqn source | official v2606 tar archive and Foundation 14 GitHub sources retrieved |

Additional challenge searches located pressure-evolution energy corrections
for multicomponent DG (Ching et al. 2025) and conservative segregated reactive
enthalpy methods on staggered meshes (Grapsas et al.). These materially
narrow any possible contribution. Sources are linked in related_work.md.

## Gate decision

Conservative pressure correction is ESTABLISHED. Energy-compatible reactive
sensible-enthalpy corrections are also ESTABLISHED in other discretizations.
Robust/steady-state-preserving chemistry splitting and detailed transport in
OpenFOAM are ESTABLISHED. None may be repackaged as a new broad principle.

The exact finite-iteration, collocated v2012 equation audit and a subsequent
cost-effective correction for its measured density/enthalpy/composition
coupling are NOT ESTABLISHED IN SEARCH. This is a candidate extension, not a
novelty verdict. A new method must compare its modified equations with
Grapsas, Hassanaly, pressure-temperature coupling methods, SCI and CTreactingFoam.

Full SCI method text/source could not be verified through
the accessible endpoints. Publisher responses were 403/429; repository
queries did not establish an authoritative SCI source location. CTreactingFoam
was subsequently found at the authors' UMN-CRFEL/OpenFOAM-Cantera repository;
source commit 0754a9cea2482fff0f6fa6630778f65042f47536 is retained with hashes.
Its EEqn adds species sensible-enthalpy diffusion but retains the same
explicit kinetic and hs -dpdt structure; its main sequence still solves
energy before pressure. It does not contain the final-state density/energy
correction investigated as a potential future extension here. The gate
therefore remains open for the *exact correction claim*. Do not implement
or headline a correction until this gap is resolved or the scope is narrowed
to an independently useful audit/negative result.

The project is currently narrowed to: **a reproducible, equation-closed audit
that tests whether final kinetic or pressure-work corrections are justified
in the documented high-drift case**. This remains useful if H1 is rejected.

## Access and scope

Full primary PDFs were inspected for Hassanaly, Wu and Grapsas, and full HTML
for Ching. SCI's publisher abstract, Zhou's publisher-indexed text and
author institutional record, Speth's publisher abstract, and pressure-based
paper abstracts were available. Abstract-only comparisons are marked
partial. CTreactingFoam's energy/species/pressure/main source was also inspected
and retained. Installed code and current official release source snapshots were
read directly. No review/forum answer is used to establish a novelty claim.

## 2026-10-07 — thermochemistry and invariant-method challenge

Primary method inspection now rejects the generic continuity/projection/source
map headlines. Exact equation/implementation comparisons are maintained in
thermo_prior_art_matrix.md. Source bytes and hashes are retained in
sourceAudit/thermoInvariants_v1/manifest.json.

The search covered NASA polynomial continuity repair and constrained fitting,
CHEMKIN thermodynamic consistency, h/s/Cp and equilibrium discontinuities,
thermochemical validation/linting, invariant-preserving ODE projection,
constrained chemical integration, finite species/energy transfer and
invariant-carrying reactor/CFD interfaces. Full inspected methods include:

- NASA Glenn 2002 p.3 reference/common-point constrained fitting;
- RMG Wilhoit-to-NASA conversion and constrained least-squares assembly;
- Cantera 3.2 NasaPoly2 validation thresholds and CV/physical-CP equations;
- Boettcher Appendix H equations H.1–H.9;
- Killingsworth et al.2020 Mech Checker sec2.1–2.3, including solver and
  pressure-coupled multizone consequences;
- CVODE eq3.11–3.12 weighted nonlinear constraint projection, accepted-step
  error test/history correction, and its separate inequality-constraint option;
- PelePhysics CV/CVH species/energy integration with transport forcing;
- actual installed StandardChemistryModel finite RR and formation contraction.

Mech Checker is a particularly strong challenge: detecting discontinuities,
repairing reference/common-point properties and showing numerical integration
benefits are already combined in that work. Likewise CVODE's projection is
integrated into time-step acceptance/history; our endpoint scalar baseline
must not be mislabeled as a new version of that established method.

SCI full-method access remains incomplete. That limitation does not support
novelty of the generic maps, which are independently covered by other primary
sources. New broad method claims are rejected; a precise future operator
response/accuracy estimator still needs its own literature and reference tests.
