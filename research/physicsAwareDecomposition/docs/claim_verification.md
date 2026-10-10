# Claim verification

Primary access is stated precisely. Local findings use retained raw evidence. “Rejected” records a tempting claim that the evidence does not support.

| Claim | Source | Primary source checked? | Evidence | Confidence | Notes |
|---|---|---|---|---|---|
| v2012 already supports cell weights | Installed domainDecompositionDistribute.C, machine hashes | Exact installed source | weightField read at current time | High | No newer API assumption |
| Chemistry-aware mesh weighting is new | Fluent guide; Scotch/METIS | Official documentation | Stiff chemistry, ISAT and model weights documented | Rejected | No general novelty |
| DLBFoam balancing alone gives about 10x | Tekgül 2021 Fig. 11 | Full paper | 2.57x balancing; 9.87x with filtering | Rejected | Conditions in literature record |
| DLBFoam baseline was run here | Official repository/local audit | Repository checked | No local install/v2012 branch; no execution | Rejected | Port is not ruled out |
| Previous-step costs are novel | Micale 2024; Lu 2009 | Full papers | Predictive chemistry balancing prior art | Rejected | Integration remains useful |
| Multi-level EoS/chemistry balancing exists | van den Oord 2025 | Abstract/author page | Method/benchmark verified | Medium | No numerical gain cited |
| Reactive partition studies existed in 2019 | Wartha institutional record | Metadata | Title/authors/venue verified | Medium | Exact weights/results unavailable |
| Migration-aware repartition is established | Schloegel 2000; Zoltan guide | Abstract/API checked | Communication/migration tradeoff | High for API | Not measured locally |
| GPU gains transfer to CPU weighting | Shi/Moure sources | Metadata/abstract | Different resources/integrators | Unsupported | No GPU experiment |
| Best local speedup is 1.159x | tight/reactive_summary.csv and raw CSV/manifests | Measured | Five repeats, p4 gamma1; CI 1.030–1.223 | High for sample | Exploratory selection, no multiplicity adjustment |
| Loose LTS 1.265x is acceptable | Loose partition validation JSON | Measured fields | T difference 12.14 K | Rejected | Excluded from accepted conclusion |
| Fixed-dt sensitivity establishes speedup | transient_summary.csv | Measured | 0.965x, CI 0.863–1.240 | Rejected | Numerical gate passes, performance neutral |
| No-chemistry stale weights regress | noChem/reactive_summary.csv | Measured | gamma16 0.673x; 48.5% higher wall | High for control | Deliberately stale predictor |
| Faces measure MPI-only time | Native counts/timers | Source/data checked | Proxy; phases include waits | Rejected | Halo time also contains peer waiting |
| All conservation laws are proved | Comparison inventories | Local fields checked | Equivalent inventories | Unsupported as temporal proof | Open boundaries/LTS, no closed flux budget |
| Live dynamic repartition benefits this case | Static study | No migration experiment | No live state migration implemented | Future work | Static restart is not dynamic evidence |
| Convergence-aware OpenFOAM partitioning has prior art | Wang 2017 / Xu 2019 | Full HTML / publisher abstract | Matrix/face edge weights and convergence objectives | High for method | No local comparison or transferred speedup |
| Physics-informed GPU batching exists | Retfalvi 2026 preprint | Primary indexed abstract; fetch 403 | Scalar-dissipation-based batching | Medium | No gain or peer-review claim |
