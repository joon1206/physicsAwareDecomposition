# Physics-aware domain decomposition: initial audit

Audit date: 2026-10-03, updated 2026-10-04.

## Status and scope

**Phase A completed against the installed OpenFOAM v2012 source.**
The research workspace is a Git clone at `~/research/ForFun` in Ubuntu
under WSL 2. OpenFOAM v2012 is installed at `/opt/OpenFOAM/OpenFOAM-v2012`
with working Scotch, PT-Scotch, KAHIP, and OpenMPI 4.0.3 libraries.

**Milestone 2 (synthetic weighted decomposition) is validated and
expanded** to 5 analytical distributions × 4 partitioners (40 runs).
See "Validated experiments" and "Second milestone" below.

**Milestone 1 (per-rank timing instrumentation) is implemented and
numerically verified.** `solvers/reactingFoamTimed` builds, runs
serially and on 2 MPI ranks with per-rank per-step CSVs, and produces
bitwise-identical fields to stock `reactingFoam`.

## Repository evidence

The research repository contains only `.gitattributes` and the research
directory created by this project. It is not an OpenFOAM checkout. The
OpenFOAM installation is a separate extracted source distribution without
`.git`.

### Requested architecture findings

| Audit item | Observed result |
| --- | --- |
| OpenFOAM version/fork | OpenCFD OpenFOAM v2012, build `_7bdb509494-20201222`, label=32, scalar=64 |
| Build system | `wmake`; source at `/opt/OpenFOAM/OpenFOAM-v2012` |
| Solver execution path | `reactingFoam` main loop: `rhoEqn.H`, then `pimple.loop()` containing `UEqn.H`, `YEqn.H`, `EEqn.H`, then pressure corrector `pEqn.H`/`pcEqn.H` |
| Chemistry/reaction path | `YEqn.H` calls `reaction->correct()`; the default laminar combustion model (`src/combustionModels/laminar/laminar.C`, `correct()` line 85) calls `chemistryPtr_->solve(deltaT)` (line 111); that resolves to `StandardChemistryModel::solve(deltaT)` (`StandardChemistryModel.C` line 692), whose per-cell loop (line 714) skips cells with `Ti <= Treact_` and, for reacting cells, iterates `while (timeLeft > SMALL)` (line 733) calling the pure-virtual `chemistrySolver::solve(c, T, p, deltaT, subDeltaT)` (`chemistrySolver.H` line 73) at line 736 |
| Species/energy/pressure/velocity solve paths | `YEqn.H` solves each species `Yi` with `fvScalarMatrix`; `EEqn.H` solves `he`; `pEqn.H`/`pcEqn.H` solve pressure |
| Decomposition execution path | `decomposePar` → `domainDecomposition::decomposeMesh()` → `distributeCells()` → `decompositionModel::New(...).decomposer().decompose(*this, cellWeights)` |
| Vertex/cell weight support | **Native.** `domainDecompositionDistribute.C` reads `weightField` from `decomposeParDict` as a `volScalarField` and passes `cellWeights` to `decompose()` |
| Scotch/PT-Scotch/METIS/ParMETIS/simple/hierarchical | Scotch and PT-Scotch libraries compiled; `libscotchDecomp.so`, `libptscotchDecomp.so`, `libkahipDecomp.so` present. METIS/ParMETIS not installed (dummy only). `simple`, `hierarchical`, `structured`, `manual`, `random` geometric decomposers available |
| MPI and processor boundaries | OpenMPI 4.0.3 bundled; `processorPolyPatch` represents rank boundaries; `domainDecomposition` tracks `procNeighbourProcessors_`, `procProcessorPatchSize_` |
| Chemistry-only load balancing / DLBFoam | Absent from this installation |
| Timing/profiling facilities | `cpuTime` class used by `distributeCells()`; solver prints `ExecutionTime`/`ClockTime` per timestep; no per-phase or per-rank timing instrumentation exists |
| Existing tests and public cases | Standard OpenFOAM tutorials under `/opt/OpenFOAM/OpenFOAM-v2012/tutorials`; `~/cavity` exists locally |
| Exact source files to modify | Solver time loop: `applications/solvers/combustion/reactingFoam/reactingFoam.C` lines 81-131, with includes `rhoEqn.H`, `UEqn.H`, `YEqn.H`, `EEqn.H`, `pEqn.H`/`pcEqn.H`. Chemistry integration entry: `StandardChemistryModel.C` `solve()` lines 692-761 (per-cell loop line 714, inner `while` line 733, `this->solve(...)` call line 736). Per-cell chemistry cost: `chemistrySolver/ode/ode.C` and `chemistrySolver/EulerImplicit/EulerImplicit.C`. Decomposition weight input: `domainDecompositionDistribute.C` |

## Execution environment

| Component | Observation |
| --- | --- |
| Linux environment | Ubuntu 26.04.1 LTS under WSL 2 |
| CPU | AMD Ryzen 5 5600X, 6 physical cores, 12 logical processors |
| Memory | 31.92 GiB physical RAM |
| GPU | NVIDIA GeForce RTX 2080 Ti, 11264 MiB, driver 591.86 |
| OpenFOAM | v2012 at `/opt/OpenFOAM/OpenFOAM-v2012` |
| Compiler | Bundled GCC 6.3.0 |
| MPI | Bundled Open MPI 4.0.3; `mpirun -np 2 hostname` verified |
| Python | 3.14.0 (WSL), 3.14.0 (Windows) |
| Git | Research clone at `~/research/ForFun`, remote `https://github.com/joon1206/ForFun.git` |

## Validated experiments

### Native weighted decomposition (Milestone 2)

**Configuration:** 400-cell 20×20×1 cavity mesh, 3 ranks, Scotch,
localized hotspot with 40 cells (x < 0.1) at weight 1000, remaining
cells at weight 1.

**Unweighted decomposition:**
- Rank cells: 133/133/134
- Rank workload: 14119/26107/134
- Imbalance (max/mean): **1.9406**
- CV: **0.7889**

**Weighted decomposition (`weightField cellWeight`):**
- Rank cells: 373/14/13
- Rank workload: 13360/14000/13000
- Imbalance (max/mean): **1.0406**
- CV: **0.0307**

**Conclusion:** Native Scotch vertex weighting reduced workload imbalance
from 94% to 4% for a spatially concentrated workload. This validates the
core hypothesis that physics-aware weighting improves load balance.

**Communication tradeoff:** Processor faces increased from 35 (unweighted)
to 18 (weighted) in this case, but max faces between processors increased
from 25 to 16. The weighted decomposition reduced total processor faces
while dramatically improving compute balance. This is case-dependent and
must be measured across configurations.

### Parallel execution

`icoFoam -parallel` ran successfully on the 2-rank cavity decomposition,
completing 100 timesteps with residual reduction and continuity error
reporting. This confirms the MPI environment is functional.

### Instrumented solver (Milestone 1)

**Build:** `solvers/reactingFoamTimed` compiled with `wmake`
(`WMAKE_EXIT=0`) to
`~/OpenFOAM/joon1206-v2012/platforms/linux64Gcc63DPInt32Opt/bin/reactingFoamTimed`;
`-help` runs. Only measurement was added; all equation files preserve
the original numerics except surrounding `phaseTimer.start/stop` calls.

**Test case:** `cases/reactingTest`, copied from the public tutorial
`combustion/reactingFoam/laminar/counterFlowFlame2DLTS`
(4000-cell 100×40×1 mesh), shortened to 10 steps (`endTime 10`).

**Serial result:** 10 steps complete; per-step CSV
(`phaseTiming/phaseTimes_rank0.csv`) with columns
`step,timestep,rho,momentum,chemistry,species,energy,pressure,turbulence,io`.
Totals: timestep 0.030 s, of which chemistry 0.020 s (~67%), pressure
0.0033 s, energy 0.0024 s, species 0.0020 s, momentum 0.0010 s.

**Numerical equivalence (PASS):** identical 10-step run with stock
`reactingFoam` (`cases/reactingRef`) produced **bitwise-identical**
field files at time 10 (`diff -r` empty for all of
U/T/p/species/Qdot/phi/rDeltaT) and identical solver-iteration log
lines (80 `Solving for` lines each; logs differ only in
Exec/PID/Case header paths and timing output).

**Parallel result (2 ranks, scotch):** `mpirun -np 2 reactingFoamTimed
-parallel` completed 10 steps (`PAR_EXIT=0`); both
`processor0/phaseTiming/phaseTimes_rank0.csv` and
`processor1/phaseTiming/phaseTimes_rank1.csv` written with 10 rows
each. Measured chemistry imbalance is real and time-varying, e.g.
step 7: rank0 2.09 ms vs rank1 17.33 ms (~8x); step 2: 1.20 ms vs
1.30 ms (~1.1x). This is the first direct evidence that per-rank
reactive cost diverges during flame development on a uniform mesh.

## Minimum external prerequisite

No external prerequisite remains. The build toolchain (local `make` 4.4.1,
focal glibc 2.31 sysroot, sysroot compiler wrappers) is documented below
and committed in `scripts/`. Rebuild with `scripts/build_timed.sh`.

## Build toolchain (no sudo, committed)

The WSL Ubuntu image has no `make` and no glibc dev headers, while the
bundled gcc-6.3.0 needs era-matching (focal, glibc 2.31) headers because
its C++ `#include_next` does not honor `C_INCLUDE_PATH`. Resolved with:

- `make` 4.4.1: `apt-get download make`, extracted to `~/local`
  (outside the repo; binary tooling, not research output).
- focal `libc6-dev`, `libc-dev-bin`, `linux-libc-dev`, `libc6` debs
  downloaded from `archive.ubuntu.com/ubuntu/pool/` and extracted to
  `~/local` as a sysroot (`~/local/usr/include`, `~/local/lib/...`).
- `scripts/wrappers/g++|gcc|cc`: use `--sysroot=$HOME/local` for
  compilation (`-c`); for linking, `-B/-L` the local dev dirs plus
  `-Wl,--rpath-link` to the focal runtime, with corrected `ld` scripts
  in `scripts/wrappers/lib/` (`libc.so`, `libm.so`, `libdl.so`,
  `libpthread.so`, `librt.so`) that replace absolute
  `/usr/lib/...` paths missing on this image.
- `scripts/build_timed.sh`: sources the OpenFOAM bashrc, prepends the
  wrappers and local make to `PATH`, unsets `C_INCLUDE_PATH`-style
  overrides, and runs `wmake`.

`/opt/OpenFOAM/OpenFOAM-v2012` itself was not modified.

## Proposed minimal architecture (implemented for timing)

1. `solvers/reactingFoamTimed/`: exact copy of the v2012 `reactingFoam`
   sources plus `phaseTimers.H` (`std::chrono::steady_clock`,
   sub-microsecond wall time; `Foam::clock` is 1 s resolution and
   unsuitable) and `start/stop` scopes in `YEqn.H` (chemistry =
   `reaction->correct()` + `Qdot`, species = `Yi` loop), `EEqn.H`
   (energy), `UEqn.H` (momentum), `pEqn.H`/`pcEqn.H` (pressure),
   plus `rho`/`turbulence`/`io`/`timestep` scopes in the main loop.
2. One CSV row per timestep per MPI rank
   (`phaseTiming/phaseTimes_rank<N>.csv` under the case dir serially,
   or under each `processor<N>/` in parallel).
3. Offline analysis with Python; synthetic workloads with
   `scripts/synth_bench.py`; workload analysis with
   `scripts/workload_balance.py`.

## Concrete Phase-B plan and acceptance gate

### B1: establish a reproducible numerical baseline

Build and run an unmodified public reacting case at 1 and 2 MPI ranks.
Use the same mesh, initialization, integration settings, end time, and
output schedule.

### B2: instrument exclusive scopes

Accumulate wall time over all invocations within a timestep for:
- chemistry/reaction;
- species transport;
- energy solve;
- pressure/velocity;
- other work and output where separable;
- entire timestep.

Avoid double-counting chemistry inside species or combustion wrappers.

### B3: offline metrics and verification

For each timestep and component, check that all ranks are present and
times are finite and nonnegative, then calculate:

```text
I_max = max(T_r) / mean(T_r)
CV = sqrt(mean((T_r - mean(T_r))^2)) / mean(T_r)
idle_proxy_s = sum_r(max(T_r) - T_r)
```

Compare instrumentation-off/on field L1/L2/Linf norms, timestep/residual
histories, species bounds and sums, and integrated reaction rates.

Accept milestone 1 only after a real parallel run produces per-rank CSV
and passes numerical verification.

## Second milestone: synthetic static weighting (validated and expanded)

The synthetic weighted decomposition milestone passed on 2026-10-04 and
was expanded the same day to analytical distributions × partitioners.

**Benchmark:** `scripts/synth_bench.py` on the 400-cell cavity mesh at
3 ranks, weight ratio 100:1. Five distributions with analytically known
totals, all verified (`uniform` 400, `step` 20200, `hotspot` 10300,
`linear` 20200, `gaussian` 5289): exact match for uniform/step/hotspot/
linear, per-cell formula match for gaussian. Four methods
(`scotch`, `simple`, `hierarchical`, `kahip` — all functional, none
dummy), weighted (`weightField`) and unweighted: 40 `decomposePar`
runs, results in `cases/cavityTest/synth_bench_results.csv`.

**Findings:**

| dist | best unweighted imb | best weighted imb | note |
| --- | --- | --- | --- |
| uniform | 1.005 | 1.005 | weighted ≡ unweighted for every method (control passes) |
| step | 1.931 | 1.010 | all 4 methods reach ~1.01 |
| hotspot | 1.913 | 1.008 | scotch 34/296/70 cells; imb 1.009 |
| linear | 1.505 | 1.005 | |
| gaussian | 2.026 | 1.009 | hierarchical 88/44/268 cells; imb 1.009 |

- Weighted decomposition reduces imbalance from 1.5–2.9× to
  1.005–1.043× **for every method**, including geometric
  `simple`/`hierarchical` (v2012 honors `weightField` there too).
- Communication: graph methods keep fewer processor faces
  (scotch 29–35, kahip 30–41) than geometric (simple/hierarchical 42
  in most rows); weighting does not systematically inflate faces
  (e.g. scotch/step 35 → 29).
- The earlier single-point result (hotspot H=1000, imb 1.94 → 1.04)
  is consistent with the sweep (hotspot H=100, scotch 1.913 → 1.009).

## Technical risks and research controls

- **Attribution:** chemistry, transport, and linear-solver scopes may
  overlap; elapsed phase time includes communication/wait unless
  independently measured.
- **Perturbation:** CSV I/O and timers can affect scheduling and
  wall-time-based solver behavior.
- **Physics verification:** decomposition changes ordering and
  floating-point reductions. Define tolerances and conservation budgets.
- **Communication tradeoff:** processor faces measure a proxy, not MPI
  seconds or bytes. Compute-balance gains may lose overall.
- **Static prediction:** persistent synthetic hotspots cannot establish
  usefulness for moving/stiff reactive regions.

## Research log

### Implemented

- Repository audit and environment verification.
- `cases/cavityTest` with native `weightField` decomposition.
- `scripts/generate_hotspot_weights.py` synthetic hotspot generator.
- `scripts/workload_balance.py` per-rank workload analyzer.
- Validated native weighted decomposition against unweighted baseline.
- `solvers/reactingFoamTimed`: instrumented reactingFoam copy
  (`phaseTimers.H`, phase scopes in `YEqn`/`EEqn`/`UEqn`/`pEqn`/`pcEqn`
  + main loop); builds with `scripts/build_timed.sh` via
  `scripts/wrappers/` sysroot toolchain (no `/opt` modification).
- `cases/reactingTest` (public counterFlowFlame2DLTS, 4000 cells,
  10 steps) and `cases/reactingRef` (stock-solver numerical reference).
- `scripts/synth_bench.py`: 5 analytical distributions × 4 methods
  × weighted/unweighted (40 runs) with results CSV.
- `scripts/compare_fields.py`, `scripts/diff_runs.sh`: numerical
  verification tooling.

### Validation

- `decomposePar -force` runs successfully with and without `weightField`.
- `icoFoam -parallel` completes on 2 ranks.
- `mpirun -np 2 hostname` confirms MPI.
- Workload imbalance reduced 1.94 → 1.04 for localized hotspot.
- `reactingFoamTimed` builds (`WMAKE_EXIT=0`); serial + 2-rank parallel
  runs complete with per-rank per-step CSVs.
- Stock vs instrumented: bitwise-identical time-10 fields, identical
  residuals (numerical equivalence PASS).
- Benchmark: 5/5 analytical totals verified; 40/40 decomposition runs
  completed; uniform-weighted ≡ unweighted for all methods.

### Benchmarks

- Decomposition workload balance: full sweep (5 distributions × 4
  methods × weighted/unweighted) in
  `cases/cavityTest/synth_bench_results.csv`.
- Solver phase timing: serial totals + 2-rank per-step CSVs in
  `cases/reactingTest` (`phaseTiming/`, `processor*/phaseTiming/`).
  No makespan/partition-comparison claims yet.

### Known limitations

- Chemistry-derived weights not yet generated from timing data.
- No dynamic repartitioning.
- The cavity test case is non-reacting; it validates decomposition
  mechanics only.
- `scripts/compare_fields.py` does not yet parse multi-line
  nonuniform field formats (bitwise `diff -r` used instead).
- Per-rank CSVs in parallel runs land under each `processor<N>/`
  directory rather than one consolidated location.

### Research observations

- OpenFOAM v2012 already supports native cell weights in `decomposeParDict`
  via `weightField`. No source modification is needed for static weighted
  decomposition.
- Scotch vertex weights are normalized to integer multiples of the minimum
  weight, with overflow compression. Extreme weight ratios (1000:1) work.
- For symmetric half-domain hotspots, weighted and unweighted partitions
  coincide. Localized hotspots are required to observe differences.

### Next hypotheses

- ~~Per-rank chemistry timing will show whether localized reactive hotspots
  produce measurable timestep imbalance.~~ **Confirmed**: 2-rank
  counterFlowFlame run shows chemistry cost diverging up to ~8x between
  ranks as the flame develops (step 7: 2.09 ms vs 17.33 ms).
- Chemistry-derived weights (previous-timestep per-cell cost → normalized
  `weightField` → `redistributePar`/re-`decomposePar`) are the next step;
  temporal correlation of per-cell cost is untested.
- Communication overhead may offset compute-balance gains at high rank
  counts; measure processor faces and MPI time.
