# Physics-aware decomposition for reactive OpenFOAM

The latest continuation is the [reactive action-oracle study](actionStudy/README.md): four balancing actions, a reproduced Stuttgart chemistry baseline, whole-condition held-out models, executed controllers, global-timestep numerical gates, profiling and 1–6-core scaling. Read its [generated report](actionStudy/docs/final_report.md), [research summary](actionStudy/docs/research_summary.md) and [figures](actionStudy/figures/README.md). The material below documents the original LTS/static-weighting study and its separate timing scope.

A numerically checked, user-space OpenCFD **v2012** prototype and retained local computational study. It asks when chemistry-derived mesh weights improve total execution time, and when they make it worse. Existing native Scotch supplies the graph partitioner.

**MEASURED:** The best accepted persistent-flame result is **1.159× faster** on four bound Ryzen 5 5600X cores: median 2.017 s versus 1.740 s, five repeats, pointwise bootstrap 95% CI **[1.030, 1.223]**. This exploratory solver-only gain excludes training/decomposition. Chemistry imbalance drops 3.112 to 1.803. A short fixed-global-timestep test is neutral within uncertainty. Stale weights with chemistry disabled make gamma=16 **48.5% slower**. Charging fresh training/setup gives an indicative 705-iteration amortization horizon. The original larger loose-tolerance speedup fails numerical validation and is excluded.

The [full report](docs/final_report.md) contains all positive and negative results, status/evidence table, hypotheses, uncertainty and next experiments. Static weighting and previous-step chemistry prediction have prior art; no general novelty or superiority to DLBFoam is claimed. See [literature review](docs/literature_review.md) and [fact checks](docs/claim_verification.md).

![Accepted gamma sweep](figures/11_gamma_speedup.png)

## What is implemented

- reactingFoamPAD: unchanged numerical equations with buffered rank-local exclusive phase timers, complete step timing, processor face/neighbor metadata and no added reactive timing collectives.
- libcostChemistry: measured cell clocks, substep counters, smoothing, restart history, trace control and passive fields. The continuation adds standard ODE instrumentation and a narrowly registered same-version Stuttgart chemistry-task baseline.
- padWorkloadFoam: controlled synthetic CPU work, native coupled halos and a synthetic-only step barrier.
- Python drivers for synthetic distributions, cost normalization/clipping, native static partitioning, parsing, norms/inventories, predictor accuracy, repeated trials, bootstrap intervals, figures and tables.

Source is GPL-3.0-or-later; attribution is in [NOTICE](NOTICE). The installed OpenFOAM source and unrelated user files are preserved. Work is committed on `codex/reactive-action-oracle`. Historical inventories describe the original study; the continuation supplies its own source hashes, provenance, compact evidence and generated artifact index.

## Tested environment and benchmark

OpenCFD OpenFOAM-v2012 build _7bdb509494-20201222, GCC 6.3 -O3, double precision/Int32, OpenMPI 4.0.3, Scotch 6.0.9. Single WSL2 guest: six physical/twelve logical Ryzen cores and about 15 GiB usable guest memory. Performance uses 1/2/4 core-bound ranks, OMP_NUM_THREADS=1. Ranks 8/12 are decomposition-only; no 24-rank, cluster or GPU benchmark. Detection and hashes: [machine.json](data/machine.json).

Public shipped counterFlowFlame2DLTS: 4000 cells, CH4/O2/CO2/H2O/N2, one reaction, EulerImplicit. LTS is iteration space, not physical elapsed seconds. Separate fixed Euler dt=1e-6 s sensitivity covers 80 steps. Full initial/BC/chemistry dictionaries and input hashes are in every retained case.

## Build and smoke test

From the repository root in WSL/Linux:

```bash
bash research/physicsAwareDecomposition/scripts/build.sh
bash research/physicsAwareDecomposition/scripts/reproduceStudy.sh --smoke
```

The smoke command rebuilds, executes 13 component tests, serial/two-rank stock/instrumented equivalence with residuals/native rho/h, native probe histories, serial/decomposed smoothing restarts and invalid-configuration rejection. Evidence goes to a **fresh** UTC-stamped directory under reproductions. Existing runs are never overwritten. The final executed smoke/probe evidence is indexed in data/project_inventory.json.

This host's extracted GCC 6.3 installation needs existing sysroot wrappers at ../../scripts/wrappers and ~/local/usr/bin; build.sh uses them read-only. For a normal configured v2012 installation, use:

```bash
export PAD_FOAM_ROOT=/path/to/OpenFOAM-v2012
export PAD_COMPILER_PATH="$PATH"
bash research/physicsAwareDecomposition/scripts/reproduceStudy.sh --smoke
```

Do not change OpenFOAM fork/version without porting and repeating numerical validation. Binaries/libs stay in build/bin and build/lib.

## Reproduce the complete local design

```bash
bash research/physicsAwareDecomposition/scripts/reproduceStudy.sh --full
```

This runs sequential small local jobs: smoke, training, clipping sensitivity, decomposition pilot/full matrix, synthetic CPU/halo pilots and repeats, loose/strict reactive sweeps, chemistry-disabled control, instrumentation overhead, fixed-dt sensitivity, native thermo output, analysis and tables. No Slurm or cluster submission is hidden in the command. Current pilots take seconds, with individual reactive runs around 1–3 seconds; the complete design takes several minutes and retains about 2 GiB of cases on this machine (logical size). Compilation and filesystem speed can dominate on another machine. Inspect data/project_inventory.json for measured dataset size. An explicit fresh PAD_OUTPUT_ROOT chooses another destination.

Repeated timing will differ. Exact-bit equality applies to the tested same-partition numerical comparisons, not to noisy runtime or arbitrary changed partitions. Every stage was executed; the finalized full wrapper is syntax checked but was not rerun as an entire duplicate campaign. The fresh smoke path was rerun after the restart correction.

## Regenerate existing analysis and figures

In WSL/Linux, from repository root:

```bash
source research/physicsAwareDecomposition/scripts/env.sh
python3 research/physicsAwareDecomposition/scripts/analyzeTiming.py
python3 research/physicsAwareDecomposition/scripts/analyzeTiming.py --campaign reactiveTight --output-dir data/processed/tight
python3 research/physicsAwareDecomposition/scripts/analyzeTiming.py --campaign reactiveNoChem --output-dir data/processed/noChem
python3 research/physicsAwareDecomposition/scripts/analyzeAdditional.py
python3 research/physicsAwareDecomposition/scripts/summarizeEvidence.py
python3 research/physicsAwareDecomposition/scripts/generateTables.py
python3 research/physicsAwareDecomposition/scripts/writeReport.py
```

With a compatible Python, install scripts/requirements-plot.txt in a virtual environment, then run generatePlots.py. On this Windows host, the bundled Python and project build/pydeps are already ready:

```powershell
& "\\wsl.localhost\Ubuntu\home\joon1206\research\ForFun\research\physicsAwareDecomposition\scripts\reproduceFigures.ps1"
```

For a fresh WSL output directory, give reproduceFigures.ps1 -OutputRoot its corresponding UNC path, or set PAD_OUTPUT_ROOT before a Linux plotting run. Every figure has PNG, PDF, SVG, source JSON and a caption. Axes distinguish whole process wall, offline max-rank proxies, synthetic work, and logarithmic comparisons.

## Data and limitations

Raw evidence: data/raw. Accepted summary: data/processed/tight. Deliberate stale-predictor regression: data/processed/noChem. Loose failed numerical comparisons and failed pilot directories remain. Final numerical norms include density, sensible enthalpy, species and native fields; inventory agreement is **not** a closed temporal conservation proof. The transient pointwise Qdot failure near zero is preserved alongside the explicitly disclosed norm-scale gate.

The design contains 2920 synthetic decomposition records, 340 repeated controlled CPU/halo runs, 75 strict and 75 loose reactive runs, 15 no-chemistry controls, 42 overhead trials and 10 transient trials, plus pilots/smoke/probes. Cached synthetic baseline timings are not independent repetitions.

Live dynamic migration, detailed chemistry, multi-node scaling, GPU scheduling, an equivalent external chemistry-task balancer, general correlation thresholds and a universal communication crossover remain untested. The full report labels these limits explicitly.

## Three next experiments

1. Longer global-timestep detailed-chemistry flame with held-out gamma and ten-plus repeats.
2. Equivalent task-only scheduler/DLBFoam baseline on the same fork, integrator and mechanism.
3. Moving reactive hotspot and small two-node migration pilot with messages/bytes and state-equivalence checks.

The strongest defensible paper framing is characterization of **numerical equivalence and total-runtime limits of static chemistry weighting**, extended with those missing comparisons.
