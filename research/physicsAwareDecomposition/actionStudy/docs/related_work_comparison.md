# Conceptual comparison

| Work | Framework / chemistry | Dynamic? | Mesh migration? | Chemistry tasks? | Prediction? | Migration cost? | Whole-solver objective? | Published/tested scale |
|---|---|---|---|---|---|---|---|---|
| Gärtner 2024 | OpenFOAM; standard/TDAC | Yes | No | Yes | Previous cell clocks | Lightweight transfers | Published plots primarily chemistry time | Up to 8192 cores |
| DLBFoam 2021 | OpenFOAM; gas kinetics | Yes | No | Yes | Previous work | Communication overhead | Solver acceleration; filtering separate | Spray A example 256 ranks |
| Cuoci 2025 workshop | OpenFOAM; detailed kinetics | Adaptive | No | Yes | Current cost/trigger | Explicit penalty | Multi-objective chemistry scheduling | Examples 32/128 processes |
| van den Oord 2025 | INCA; EoS and chemistry | Yes | Base mesh retained | Yes, two stages | Persistence / previous cost | Transfers compared | Full application phases analyzed | Million-cell Spray A |
| PeleLMeX / SUNDIALS | AMReX; detailed chemistry | Periodic | Separate ODE grid | ODE boxes | RHS workload | Efficiency trigger | Application cost | Exascale CPU/GPU software |
| ParMETIS / Zoltan | General weighted graphs | Yes | Yes | User-defined | User cost weights | Explicit adaptive tradeoff | Partition services, user objective | General HPC libraries |
| OpenFOAM Foundation 10 | CFD, initially chemistry weights | Yes | Yes | Mesh cells | CPU cell costs | Runtime redistribution | General CPU load balance | Capability, not reproduced here |
| DRAMA | Finite elements | Yes | Yes | No chemistry-specific tasks | Measured phase costs | Partition migration considered | Sum of phase maxima | Different application, not reproduced |
| Ansys Fluent 2025 R2 | Reactive CFD and other models | Yes | Yes | Mesh-based weighting | Timers / model weights | Runtime cell migration | Multiple model constraints | Documented capability, not reproduced |
| This study | OpenCFD v2012; H2 and GRI | External segments | Native redistributePar | Stuttgart compatibility port | Past-only whole-cost ridge | Measured process wall | Four-action J(a,H), plus actual deployments | 256/512 cells, 1–6 ranks, one host |

Only the same-version Stuttgart standard implementation is a directly timed reactive-flow competitor. QUICKLB is additionally compiled and tested on its own public-library kernel; neither paper speedups nor cross-framework results are treated as a performance leaderboard.
