# Literature review

**VERIFIED to the access levels stated; PARTIALLY TESTED external comparisons.** Search/fact checking: 2026-10-04. Broad scoped review, not proof that every relevant publication was found. Full-text limits remain explicit. Machine-readable requested metadata: [literature.json](literature.json).

Search families: reactive CFD and stiff ODE imbalance; OpenFOAM/DLBFoam; chemistry mesh weights versus task/core redistribution; weighted Scotch/METIS/ParMETIS; adaptive repartitioning/migration; ISAT; AMPI/Zoltan; CPU/GPU chemistry. Primary papers/preprints, institutional records, repositories, manuals and installed source were preferred. Inaccessible theses/posters are recorded without quantitative claims.

## Positioning

Static weighted graph partitioning and chemistry-aware mesh weights are established. The exact installed v2012 utility already reads weightField. Fluent's official guide documents stiff-chemistry/ISAT mesh weights and model-weighted METIS partitioning. Static physics-aware weighting is **not general novelty**. [Fluent manual](https://ansyshelp.ansys.com/public/Views/Secured/corp/v252/en/flu_ug/flu_ug_GridPartition.html)

Task redistribution retains mesh/transport ownership; our static weighting changes cell counts and interfaces for every PDE phase. Core lending, virtual ranks and adaptive repartitioning use different scheduling units. Unmatched published speedups cannot rank these choices.

The tekgul2021 JSON record checks separate balancing-only and combined-filtering gains against the primary paper. Neither predicts this reduced-mechanism CPU case. [Primary article](https://acris.aalto.fi/ws/portalfiles/portal/66228302/ENG_Tekgul_et_al_DLBFoam_An_open_source_dynamic_Computer_Physics_Communications.pdf)

Previous-cell-time predictors already appear in catalyst-surface and parallel PDF chemistry balancing. Smoothing and amortization formulas are useful engineering tools, not publication novelty by themselves. Official DLBFoam source currently targets Foundation OpenFOAM; no local install or v2012 branch was found. A compatible baseline was not executed; a port is not ruled out. [Official repository](https://github.com/blttkgl/DLBFoam)

The defensible paper angle is **numerical equivalence and limits of static chemistry-weighted decomposition**: compute balance versus whole-run time, misleading loose-tolerance speedups, and persistent reaction zones. This local prototype is a foundation; publication requires multicase/multinode evidence, equivalent task-balancing baselines and a validated transport/communication-aware predictor or trigger.

Recent targeted queries included 2026 reacting-flow/GPU scheduling, chemistry mesh weighting and partitioning theses. Added convergence-aware OpenFOAM partitioning and current DeepFlame/physics-informed GPU preprint records reinforce the conservative novelty assessment. Inaccessible thesis PDFs were not used for specific claims.

## Checked source comparison

Details, requested metadata, hardware/benchmark conditions and access limitations are retained in literature.json.

| Record | Year | Framework | Method / relevance | Access | Primary source |
|---|---|---|---|---|---|
| tekgul2021 | 2021 | OpenFOAM/DLBFoam | MPI chemistry-task redistribution; separately reference-cell filtering. | full primary paper | [Source](https://acris.aalto.fi/ws/portalfiles/portal/66228302/ENG_Tekgul_et_al_DLBFoam_An_open_source_dynamic_Computer_Physics_Communications.pdf) |
| dlb_repo | versioned | Current repository states OpenFOAM-dev/latest Foundation support. | Dynamic chemistry tasks, reference-cell filtering and analytic Jacobian extensions. | official README and read-only remote branch inventory | [Source](https://github.com/blttkgl/DLBFoam) |
| morev2022 | 2022 | OpenFOAM/DLBFoam | Chemistry acceleration plus dynamic balancing. | primary preprint abstract and official repository metadata; PDF fetch unavailable | [Source](https://arxiv.org/abs/2105.12070) |
| ramirez2023 | 2023 | Alya | DLB library core lending among MPI ranks; chemistry threading. | full primary preprint | [Source](https://arxiv.org/pdf/2210.07364) |
| micale2024 | 2024 | Reactive CFD at catalyst surfaces | Previous-step cell-time prediction, MPI task distribution and OpenMP. | full primary paper | [Source](https://re.public.polimi.it/retrieve/565325b6-3cd7-4f2e-9dc9-b52ddd14a405/micale-et-al-2024-acs-eng-au.pdf) |
| oord2025 | 2025 | INCA | Multi-level independent task offload. | publisher abstract and author-project page; full PDF unavailable | [Source](https://journals.sagepub.com/doi/abs/10.1177/10943420251329199) |
| wu2019 | 2019 | Reactive-flow solver | Rosenbrock-Krylov time stepping, splitting and dynamic balancing described in journal abstract. | publisher abstract plus earlier primary preprint https://arxiv.org/pdf/1712.00953 | [Source](https://www.sciencedirect.com/science/article/pii/S001046551930133X) |
| antonelli2011 | 2011 | Engine combustion MPI simulation | Contiguity-preserving cell distribution for chemistry evaluation. | primary institutional metadata/abstract; full text unavailable | [Source](https://iris.cnr.it/handle/20.500.14243/171628) |
| wartha2019 | 2019 | Not verified from accessible primary record | Not fully verified from accessible primary record. | primary institutional publication record; poster/thesis unavailable | [Source](https://www.k1-met.com/fileadmin/user_upload/Publications/Presentations/GB_2018_19_Screen2.pdf) |
| scotch1996 | 1996 | Scotch/PT-Scotch | Graph partitioning/static mapping with weighted vertices and edges. | official author software page/bibliography | [Source](https://www.labri.fr/perso/pelegrin/scotch/) |
| metis1998 | 1998 | METIS | Multilevel coarsen, partition and refine. | full primary paper; institutional bibliographic metadata | [Source](https://people.eecs.berkeley.edu/~jordan/sail/readings/karypis-kumar.pdf) |
| schloegel2000 | 2000 | Parallel graph repartitioning | Unified adaptive repartitioning objective. | primary institutional abstract/metadata | [Source](https://experts.umn.edu/en/publications/a-unified-algorithm-for-load-balancing-adaptive-scientific-simula/) |
| zoltan2002 | 2002 | Zoltan | Partitioning/repartitioning services; ParMETIS AdaptiveRepart exposes migration sizing. | official citation and user guide | [Source](https://sandialabs.github.io/Zoltan/Zoltan_cite.html) |
| ampi_docs | versioned | AMPI/Charm++ | Virtual-rank load balancing and migration. | official documentation | [Source](https://charm.readthedocs.io/en/latest/ampi/04-extensions.html) |
| fluent_docs | versioned | Ansys Fluent | Stiff-chemistry flame-sensor weights, ISAT weights and model-weighted METIS partitioning. | official full documentation | [Source](https://ansyshelp.ansys.com/public/Views/Secured/corp/v252/en/flu_ug/flu_ug_GridPartition.html) |
| pope1997 | 1997 | Combustion chemistry integration | In situ adaptive tabulation (ISAT). | full primary paper; DOI corroborated in bibliographic references | [Source](https://tcg.mae.cornell.edu/pubs/Pope_CTM_97.pdf) |
| lu2009 | 2009 | Parallel PDF/ISAT | Adaptive PLP with task strategies including URAN/PREF. | full primary paper; DOI on article | [Source](https://tcg.mae.cornell.edu/pubs/Lu_LRP_JCP_09b.pdf) |
| shi2012 | 2012 | Multidimensional combustion | GPU and hybrid explicit/implicit ODE integration. | primary author-group metadata; DOI in primary DLBFoam bibliography; full text unavailable | [Source](https://greengroup.mit.edu/biblio/accelerating-multi-dimensional-combustion-simulations-using-gpu-and-hybrid-explicitimplicit-ode/) |
| moure2025 | 2025 | CPU–GPU combustion | ChemInt heterogeneous chemistry integration. | primary publisher indexed abstract and CRediT author list; direct fetch unavailable | [Source](https://doi.org/10.1016/j.compfluid.2025.106846) |
| openfoam_v2012 | 2020 | OpenCFD OpenFOAM v2012 | decomposePar reads current-time weightField and calls native weighted decomposition. | installed actual v2012 source, hashed in data/machine.json | [Source](https://dl.openfoam.com/source/v2012/) |
| wang2017 | 2017 | OpenFOAM/Metis | FMetis assigns face-area approximations of matrix coefficients as edge weights. | full primary HTML paper | [Source](https://journals.sagepub.com/doi/10.1177/1687814017734109) |
| xu2019 | 2019 | OpenFOAM | MDMRPar records previous-step surface matrix information; ParMetis weighted repartitioning, with coarse graphs for AMR. | primary publisher abstract/metadata | [Source](https://onlinelibrary.wiley.com/doi/abs/10.1002/cpe.5412) |
| deepflame2026 | 2026 | DeepFlame | OpenFOAM/Cantera/PyTorch integration; README credits DLBFoam chemistry balancing from v0.2 and CPU/GPU extensions. | official current README | [Source](https://github.com/deepmodeling/deepflame-dev) |
| retfalvi2026 | 2026 | ABLATE/Zero-RK | Scalar dissipation/progress-variable predictors guide batch load balancing. | primary indexed SSRN abstract; direct page fetch 403 | [Source](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=6678658) |
| carreon2025 | 2025 | AMReX-based compressible solver | Bulk-sparse chemistry integration and multi-GPU AMR load distribution. | primary preprint abstract/metadata | [Source](https://arxiv.org/abs/2510.23993) |
| yang2023 | 2023 | OpenFOAM-based customized solver | SpeedCHEM sparse Jacobian, chemistry DLB, OpenMP and LTS. | primary preprint abstract/metadata | [Source](https://arxiv.org/abs/2311.14941) |
