# Physics-aware decomposition and reactive-energy consistency

Complete research snapshot from the local ForFun project, transferred on 2026-10-10. Source code, reports, figures, processed results, immutable implementation snapshots, failed experiments and compressed raw evidence are included. Existing local files and the ForFun repository remain in place.

## Research projects

- [Physics-aware decomposition](research/physicsAwareDecomposition/README.md): original chemistry-cost/decomposition work, including the [published action study](research/physicsAwareDecomposition/actionStudy/README.md).
- [Reactive energy consistency](research/reactiveEnergyConsistency/README.md): discrete reacting-flow energy audit and candidate-method continuation.
- [Clean versus legacy thermochemistry](research/reactiveEnergyConsistency/docs/clean_vs_legacy_results.md): matched H2/GRI CFD controls and independent mechanism/source evidence.
- [Current bounded decision and research pivot](research/reactiveEnergyConsistency/docs/continuous_thermo_pivot.md): no candidate passed all publication gates. Continuous thermo removes the direct breakpoint floor, but the pressure/density/enthalpy defect survives. This is not a claim of universal research exhaustion.

The snapshot retains 449 native experiments: 415 technical completions, 34 retained failures, and no incomplete cases. Technical completion is distinct from scientific acceptance. The previous 38 evidence checks and 17 new phase checks pass. The 499 published actionStudy files are copied byte-for-byte and verified against their frozen SHA256 manifest.

## Complete raw evidence

Raw campaigns contain more than a million files and roughly 13 GB of uncompressed data. To keep them portable, they are stored in `evidence/` as ordered 4 MiB compressed archive volumes. The oversized processed `cell_totals.json` is included in the same scheme. These are real evidence bytes, not external placeholders or Git LFS pointers.

After cloning, use Python 3.12 or newer:

```bash
python3 tools/restore_evidence.py --verify-only
python3 tools/restore_evidence.py
```

The script verifies every volume and whole-archive SHA256 before restoring the original relative paths. It refuses to overwrite different existing files and supports retrying an interrupted restoration. Allow sufficient disk space for the expanded evidence. `evidence/archives.json` lists every volume; `evidence/source_files.json` records the original source commit, scope and copied-file hashes.

## Reproduction

Historical build and reproduction instructions are retained inside each project. Native experiments use OpenCFD OpenFOAM v2012 on Ubuntu/WSL with the documented compiler and MPI environment. The independent chemistry references use pinned Cantera 3.2.0; plotting uses the documented Python dependencies. Installed Python/compiler environments, compiled binaries and caches are excluded and should be rebuilt from the preserved source/instructions.

After restoring evidence and initializing the documented OpenFOAM environment:

```bash
bash research/reactiveEnergyConsistency/scripts/candidate_run.sh candidate_verification.py
bash research/reactiveEnergyConsistency/scripts/candidate_run.sh thermochemical_phase_verification.py
```

The original relative project layout is preserved to keep cross-project imports and manifests valid. Source-only historical `build/initialStateSolver` and `build/restartSolver` snapshots are included where preparation scripts require them. Unrelated local research projects are excluded.

## Licensing and provenance

See [LICENSE](LICENSE), [source attribution](research/physicsAwareDecomposition/NOTICE), retained upstream headers and mechanism licenses. Scientific conclusions, negative controls, provenance limitations and reference uncertainty are documented in the project reports. This repository is a snapshot of the current work; earlier ForFun Git history is identified by commit in the export manifest.