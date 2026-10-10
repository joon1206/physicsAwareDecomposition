# Discrete total-energy consistency in reactive OpenFOAM

Independent numerical audit of the installed OpenCFD v2012 pressure-based
reacting algorithm. The completed `../physicsAwareDecomposition/actionStudy`
is a read-only input. The first audit is preserved; candidate corrections and
independent references are implemented separately in candidateStudy.

The first acceptance gate is an equation-derived budget that closes per step,
with an independent thermodynamic inventory and instrumentation equivalence.
Stage inventory jumps alone are not interpreted as equation defects.

Run in WSL from the repository root:

```bash
python3 research/reactiveEnergyConsistency/scripts/prepare.py
bash research/reactiveEnergyConsistency/scripts/build.sh
bash research/reactiveEnergyConsistency/scripts/run.sh campaign.py
bash research/reactiveEnergyConsistency/scripts/run.sh followup.py
bash research/reactiveEnergyConsistency/scripts/run.sh exact_wave.py
bash research/reactiveEnergyConsistency/scripts/run.sh analyze.py
bash research/reactiveEnergyConsistency/scripts/run.sh log_metrics.py
bash research/reactiveEnergyConsistency/scripts/test.sh
bash research/reactiveEnergyConsistency/scripts/report.sh
bash research/reactiveEnergyConsistency/scripts/run.sh provenance.py
```

See `docs/research_question.md`, `docs/baseline_algorithm.md`,
`docs/discrete_energy_derivation.md`, and the generated `docs/audit_results.md`.
Raw runs are retained locally; processed budgets, source manifests, gates,
and plots are portable. Every run refuses to overwrite an existing case.

The executed first milestone reproduces −17.3886598% drift and closes the
baseline budget to roundoff. Density changes after the enthalpy solve dominate
the net sensible/formation-energy mismatch. See the report for nonmonotonic
refinements, negative outer-iteration controls, exact-solution verification,
tests, timing uncertainty, and the remaining novelty/validation gates.

## Continuation: candidate methods and references

See candidateStudy/README.md for current files, reproduction commands and
reference limits. Runtime-selectable local/scalar/shared-flux energy/species
corrections, a separate pressure/species/energy block, and an inviscid
conservative reference have been tested. Local/scalar energy-only screens
failed; compatible residual formulations conserve the tested closed inventory.
No tested method has established a new numerical contribution or passed every
reacting accuracy/performance gate. docs/novelty_matrix.md and
 docs/claim_strength.md state the current evidence boundary.

The current bounded decision is in docs/candidate_decision.md. The corrected
chemistry comparisons retain coarse quenching and a failed source-energy gate
at the legacy NASA branch switch, independently reproduced in Cantera. Actual
data also limits global temperature inversion guarantees. All failures are
retained; no universal exhaustion or positive publication decision is asserted.

The continuous-thermo continuation is reported in
`docs/clean_vs_legacy_results.md`, with every-species/reaction auditing in
`docs/mechanism_continuity_audit.md` and representation-independent derivation
in `docs/invariant_derivation.md`. The five candidate cycles are documented in
`docs/invariant_projection_results.md`, `docs/finite_source_map_results.md`
and `docs/thermochemical_risk_results.md`; `docs/thermo_prior_art_matrix.md`
records equation-level challenges. These controls distinguish the direct
breakpoint floor from a surviving CFD coupling defect and retain remaining
continuous-data source failures. Candidate conservation is not publication
acceptance. Historical 38 checks remain separate from the new phase checks.
