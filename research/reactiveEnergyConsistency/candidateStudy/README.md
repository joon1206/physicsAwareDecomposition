# Candidate investigation and independent references

This is the continuation of the preserved first audit. No method has passed
all publication gates. The accepted audit applications/data and the 499-file
published actionStudy are checked against stored hashes. Failed candidates and
reference failures are retained alongside successful cases.

Location on this computer:

- WSL: /home/joon1206/research/ForFun/research/reactiveEnergyConsistency
- Windows Explorer: \\wsl.localhost\Ubuntu\home\joon1206\research\ForFun\research\reactiveEnergyConsistency

Current evidence is in ../docs/claim_strength.md, ../docs/novelty_matrix.md,
../docs/research_log.md and ../docs/targeted_prior_art_comparison.md. Exact
Euler/cellwise identities are in ../docs/dominant_defect_derivation.md.

## Data layout and provenance

- data/raw/<case>: input dictionaries, meshes, primitive fields, solver logs,
  inventories, local/global ledger CSVs and experiment/result/failure JSON.
- sourceSnapshots/<sha>: exact C/H and Make source used for a recorded run.
  Each experiment also records the executable SHA256.
- data/processed: regenerated analyses. benchmark_matrix.json/CSV uses repeated
  timing trials and explicitly labels its reacting self reference.
- ../figures/candidates: figures generated from those source records.
- ../applications: separate audit, runtime-selectable candidates, block
  candidates, native rate utility, conservative central and HLLC references.
- ../build/bin: compiled research executables. ../build/canteraPackages contains
  the independent Cantera runtime; it does not replace the OpenFOAM model.

## Reproduce from the repository root in WSL

The installed v2012/compiler/native chemistry wrappers are configured by
scripts/candidate_env.sh. Build only the desired candidate applications:

```bash
bash research/reactiveEnergyConsistency/scripts/candidate_build.sh
bash research/reactiveEnergyConsistency/scripts/block_build.sh
bash research/reactiveEnergyConsistency/scripts/central_build.sh
bash research/reactiveEnergyConsistency/scripts/hllc_build.sh
bash research/reactiveEnergyConsistency/scripts/transport_build.sh
bash research/reactiveEnergyConsistency/scripts/cv_build.sh
bash research/reactiveEnergyConsistency/scripts/cv_probe_build.sh
bash research/reactiveEnergyConsistency/scripts/roundoff_build.sh
```

Generate analyses and evidence checks without rerunning CFD:

```bash
bash research/reactiveEnergyConsistency/scripts/candidate_run.sh candidate_analyze.py
bash research/reactiveEnergyConsistency/scripts/candidate_run.sh candidate_ablation_report.py
bash research/reactiveEnergyConsistency/scripts/candidate_run.sh candidate_mpi_analyze.py
bash research/reactiveEnergyConsistency/scripts/candidate_run.sh candidate_benchmark_matrix.py
bash research/reactiveEnergyConsistency/scripts/candidate_run.sh inviscid_compare.py
bash research/reactiveEnergyConsistency/scripts/candidate_run.sh inviscid_field_compare.py
bash research/reactiveEnergyConsistency/scripts/candidate_run.sh inviscid_cross_compare.py
bash research/reactiveEnergyConsistency/scripts/candidate_run.sh inviscid_reference_report.py
bash research/reactiveEnergyConsistency/scripts/candidate_run.sh candidate_mixture_wave.py algebra
bash research/reactiveEnergyConsistency/scripts/candidate_run.sh candidate_verification.py
```

Experiment drivers reuse completed cases and refuse to overwrite incomplete or
failed evidence. Name a new tagged case for a changed configuration/source.
Historical prepare/setup scripts describe the original prototype creation;
current sourceSnapshots and build scripts define the reproducible application.

## Reference limitations

The independent Cantera reference uses declared legacy atomic weights,
thermodynamic gas constant/standard-pressure and Arrhenius conversion, with
clone=False and explicit reactor-phase identity assertions. Old convention
failures remain in distinct directories. The corrected reference verifies
first-order homogeneous reacting convergence.

Analytic nonreacting and synthetic reacting entropy waves provide exact
transport errors. The synthetic reaction is not a detailed flame benchmark.
The native conservative central reference solves the same inviscid kernel PDE
as InvF cases, with different numerical diffusion. Coarse central meshes quench;
nx256 ignites. Finest-grid numerical trajectories and self references are not
labelled exact until their spatial/temporal uncertainty is resolved. Aligned
mesh comparisons conserve rho/rhoU/rhoY/rhoEa during restriction, then recover
primitive T/p from the independent NASA7 thermodynamics.

The independent known-method HLLC reference reduces acoustic contact diffusion
and preserves p/U in the equal-property analytic waves. It burns on the coarse
kernel meshes, but its reacting mesh differences and differences from the
central reference still limit accuracy claims. The unequal-NASA mixture wave
and two-donor mixing calculation separately test pressure equilibrium and
conservative state transfer; no general pressure-equilibrium theorem is asserted.

The three-trial timing matrix is for the original 256-cell F case, whose
Sutherland As=0 means zero physical viscosity, thermal and species diffusion.
Logical inviscid/reference runs and separately instrumented MPI runs do not
supply uncontended runtime claims. See each analysis's recorded scope.

The separate transport control adds the known sensible enthalpy carried by
species diffusion, using v2012's actual species diffusivity. Pr=.7 unequal-Cp
diffusion waves show the old local temperature error floor while conserving
energy; the compatible flux and Pr=1 negative controls retain constant T/p.
Its lagged flux has only the declared periodic/symmetry/empty scope. Tagged
nonzero-Sutherland reacting screens change the transport model explicitly;
they are not a resolved flame validation or a novelty result.

The separate libcvChemistry runtime source implements known constant-volume
Cv/internal-energy chemistry and a matched constant-pressure RHS control.
Corrected dfdt0 cases provide native callback/Jacobian/invariant probes and
homogeneous timestep/ODE-tolerance contrasts against Cantera. Earlier adapter
runs used an incorrect explicit-time derivative and are retained as superseded.
The original installed/accepted chemistry implementation is preserved.

```bash
bash research/reactiveEnergyConsistency/scripts/candidate_run.sh cv_chemistry_probe.py
bash research/reactiveEnergyConsistency/scripts/candidate_run.sh candidate_cv_chemistry.py
bash research/reactiveEnergyConsistency/scripts/candidate_run.sh candidate_cv_chemistry.py tolerance
bash research/reactiveEnergyConsistency/scripts/candidate_run.sh candidate_cv_chemistry.py reactingScreen
bash research/reactiveEnergyConsistency/scripts/candidate_run.sh cv_chemistry_report.py
```

See ../docs/cv_chemistry_results.md and ../docs/transport_compatibility_results.md.
Known-physics controls do not establish a new algorithm or resolve the existing
kernel's spatial reference uncertainty. Immutable chemistrySnapshots and each
experiment's library SHA256 identify the source implementation used.

The eight corrected CPFD/CV spatial F controls are complete. Both conservative
paths quench at dt2 us and burn at dt1 us. Additional cold/high-pressure and
hot homogeneous regimes retain the original cold Newton failure. The separate
roundoff executable tests three stopping policies; final cap fallback completes
cold while preserving formerly completing on/off fields. These logical wall
times are excluded from cost comparisons because campaigns overlapped.

```bash
bash research/reactiveEnergyConsistency/scripts/candidate_run.sh cv_chemistry_regimes.py
bash research/reactiveEnergyConsistency/scripts/candidate_run.sh roundoff_screen.py
bash research/reactiveEnergyConsistency/scripts/candidate_run.sh component_tolerance_bounds.py
bash research/reactiveEnergyConsistency/scripts/candidate_run.sh component_tolerance_report.py
bash research/reactiveEnergyConsistency/scripts/candidate_run.sh thermal_path_limiter.py
bash research/reactiveEnergyConsistency/scripts/candidate_run.sh element_invariant_screen.py
```

The exact Taylor source-map and positivity-limiter counterexamples are scoped
synthetic proofs/screens. Element-invariant reduction is a known principle;
its linear-system equivalence and ineligible controls do not establish a new
native solver. See ../docs/candidates/thermalPathTaylor.md,
../docs/component_tolerance_results.md and
../docs/candidates/elementInvariantReduction.md for assumptions and failures.

The spatial Cv source-energy gate also fails across the unchanged NASA
1000 K switch. Separate direct native and matched Cantera probes reproduce
the small branch energy jump; actual-data gap/overlap examples limit global
temperature inversion guarantees. The original source threshold and accepted
thermodynamics remain unchanged. Evidence-check success is not scientific
acceptance of these failed gates. Analytical driver hashes/snapshots are in
the manifest; use distinct raw tags for changed implementations or inputs.

```bash
bash research/reactiveEnergyConsistency/scripts/cv_branch_probe_build.sh
bash research/reactiveEnergyConsistency/scripts/candidate_run.sh cv_branch_probe.py
bash research/reactiveEnergyConsistency/scripts/candidate_run.sh cv_source_invariant_audit.py
bash research/reactiveEnergyConsistency/scripts/candidate_run.sh cv_source_invariant_report.py
bash research/reactiveEnergyConsistency/scripts/candidate_run.sh thermo_branch_inversion.py
bash research/reactiveEnergyConsistency/scripts/candidate_run.sh combined_defect_counterexample.py
bash research/reactiveEnergyConsistency/scripts/candidate_run.sh candidate_provenance.py
```

cantera_branch_probe.py uses the existing Windows Python/Cantera dependency
runtime; its exact inputs and generated trajectories remain in raw
cantera_Branch directories. See ../docs/candidate_decision.md and
../docs/cv_source_invariant_results.md for the current decision and scope.

## Continuous thermochemistry and five-family continuation

The matched controls use separate raw tags and the unchanged native candidate
applications/library. HS preserves Cp; CpHS additionally matches its value at
the branch switch. Both preserve the low/reference coefficients. The controls
are sensitivity baselines, not physical-data refits. H2 and GRI full-flow
comparisons retain the original zero transport. Alzueta's independent source
comparisons are valid; its unsupported native PLOG reader failures are retained.

```bash
bash research/reactiveEnergyConsistency/scripts/candidate_run.sh thermo_continuity.py
bash research/reactiveEnergyConsistency/scripts/candidate_run.sh clean_thermo_campaign.py
bash research/reactiveEnergyConsistency/scripts/candidate_run.sh clean_thermo_branch.py
bash research/reactiveEnergyConsistency/scripts/candidate_run.sh clean_gri_campaign.py
bash research/reactiveEnergyConsistency/scripts/candidate_run.sh thermochemical_abstract_map.py
bash research/reactiveEnergyConsistency/scripts/candidate_run.sh clean_thermo_report.py
bash research/reactiveEnergyConsistency/scripts/candidate_run.sh thermochemical_candidate_report.py
bash research/reactiveEnergyConsistency/scripts/candidate_run.sh thermochemical_pivot.py
bash research/reactiveEnergyConsistency/scripts/candidate_run.sh candidate_provenance.py
bash research/reactiveEnergyConsistency/scripts/candidate_run.sh thermochemical_phase_provenance.py
bash research/reactiveEnergyConsistency/scripts/candidate_run.sh candidate_verification.py
bash research/reactiveEnergyConsistency/scripts/candidate_run.sh thermochemical_phase_verification.py
```

mechanism_continuity_audit.py, clean_thermo_reference.py and
invariant_projection_valid_data.py use the existing isolated Windows Python
runtime and pinned Cantera 3.2 dependency directory. They reuse immutable
completed raw results and refuse an incomplete target. Run
thermochemical_figures.py in the existing quicklbEnv plotting environment
before generating the supplemental phase manifest. The report scripts rebuild
derived tables; they do not rewrite raw executions. The original 38 evidence
criteria are unchanged; new scientific failures are explicitly classified in
thermochemical_phase_manifest.json and checked by the separate 17 phase tests.

Read ../docs/clean_vs_legacy_results.md, ../docs/invariant_derivation.md,
../docs/thermo_prior_art_matrix.md and ../docs/continuous_thermo_pivot.md.
No method is promoted on invariant closure alone. New concurrent wall values
are excluded from runtime/memory superiority claims.
