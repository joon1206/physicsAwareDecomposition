# Phase A source audit — 2026-10-04

**VERIFIED** against local OpenCFD v2012 (`_7bdb509494-20201222`, DP, Int32).
Installation is extracted source, not Git. Source hashes and detected commands are in `data/machine.json`.
Repository HEAD: `ba7aeb51b1b6acc443c295950c8ed0aa4c426ec3`, branch main. Existing untracked cases, scripts, solvers, and research/physics-aware-decomposition are preserved. No commits.

All paths below are relative to /opt/OpenFOAM/OpenFOAM-v2012.

| Concern | Exact source and behavior | Status |
|---|---|---|
| Solver | applications/solvers/combustion/reactingFoam/reactingFoam.C: density, PIMPLE momentum/species/energy, pressure, turbulence | VERIFIED |
| Thermo | src/thermophysicalModels/reactionThermo/psiReactionThermo; hePsiThermo/reactingMixture/sutherland/janaf/perfectGas/sensibleEnthalpy selected | VERIFIED |
| Species | reactingFoam/YEqn.H: reaction->correct(), Qdot, active species matrices, inert species closure | VERIFIED |
| Equations | EEqn.H, UEqn.H, pEqn.H, pcEqn.H in solver; phase wall time includes linear solver MPI waits | VERIFIED |
| Combustion | src/combustionModels/laminar/laminar.C:85: chemistry solve, localEuler passes cell 1/rDeltaT | VERIFIED |
| Chemistry | src/thermophysicalModels/chemistryModel/chemistryModel/StandardChemistryModel/StandardChemistryModel.C:692: per-cell loop, temperature threshold, substeps, source recovery | VERIFIED |
| Chemistry solver | chemistrySolver/EulerImplicit/EulerImplicit.C; tutorial uses EulerImplicit, not unused Rosenbrock43 odeCoeffs | VERIFIED |
| ODE | chemistrySolver/ode/ode.C -> src/ODE/ODESolvers | VERIFIED |
| Weight API | applications/utilities/parallelProcessing/decomposePar/domainDecompositionDistribute.C:40: reads current-time volScalarField weightField and calls decompose(mesh,cellWeights) | VERIFIED |
| Scotch | src/parallel/decompose/scotchDecomp/scotchDecomp.C: normalized integer vertex weights, Scotch 6.0.9 | VERIFIED |
| Geometry | src/parallel/decompose/geometric, simple, hierarchical: weighted API exists, outcomes need testing | VERIFIED API |
| Processor boundaries | src/OpenFOAM/meshes/polyMesh/polyPatches/constraint/processor/processorPolyPatch | VERIFIED |
| MPI | Pstream/UPstream in OpenFOAM/db/IOstreams/Pstreams; bundled OpenMPI 4.0.3 | VERIFIED |
| Redistribution | applications/utilities/parallelProcessing/redistributePar; src/dynamicMesh/fvMeshDistribute | VERIFIED infrastructure; online integration untested |
| Task balance | No local DLBFoam; TDAC and tabulation present, not a task-redistribution baseline | VERIFIED |
| Timing | cpuTime, clockTime, profiling facilities; steady_clock selected for sub-ms wall timing | VERIFIED |
| Case | shipped combustion/reactingFoam/laminar/counterFlowFlame2DLTS: 4000 cells, 5 species, 1 methane reaction | VERIFIED |

Compiled serial Scotch and KaHIP available. PT-Scotch headers/MPI library exist separately; runtime must be tested. Scotch METIS compatibility wrappers do not establish native METIS/ParMETIS decomposers. No Slurm allocation or multinode hardware detected. WSL guest exposes Ryzen 5 5600X, 6 physical cores/12 logical CPUs and ~15 GiB memory. Earlier host-memory claims do not describe usable guest memory. Performance ranks 1/2/4, no oversubscription; 8/12 only decomposition sensitivity, 24 excluded.

**PROPOSED at audit:** independent solver copy, fixed-enum rank-local timers, buffered CSV and no timing reductions. Registered EulerImplicit-derived cost model copies exact v2012 per-cell integration loop, adds optional clocks/counters and calls unchanged native single-cell solves. Register only the benchmark thermo combination. Static partitioning uses native weightField. Defer live dynamic migration until evidence justifies complete state management.

Validation compares same-partition stock/instrumented output first, then changed-partition norms. LTS iteration index is not physical seconds. Time-accurate Euler sensitivity is separate. No novelty claimed for weighted graph partitioning.
