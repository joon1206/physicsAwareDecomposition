# Answers to the fifteen research questions

These answers are generated from the final measured dataset. The full report supplies methods, primary citations and uncertainty limits.

## Q1: When is chemistry imbalance large enough to matter?

Its importance depends jointly on chemistry fraction, available horizon and persistence. The same rank imbalance can have negligible whole-solver value in the cold inactive-chemistry control. The measured regime map and horizon sweep show this dependence; these data do not identify a universal imbalance threshold.

## Q2: When does chemistry-task redistribution win?

AC is the median winner in 17 of 25 measured states. Held-out always-AC replay gives 1.190× versus A0. Complete pointwise intervals and negative states are in tables/oracle.csv; a median winner alone does not prove statistical separation.

## Q3: When does mesh redistribution win?

AM is the median winner in 0 measured states. Its held-out aggregate speedup is 0.767×. The tested gamma and horizon sweeps are complete; no useful unobserved winning region is inferred.

## Q4: When does doing nothing win?

A0 wins 8 states: heldoutIgnition at 40 μs, H=80, heldoutPersistent at 200 μs, H=80, translating at 200 μs, H=80, transportDominated at 200 μs, H=80, transportDominated at 40 μs, H=20, transportDominated at 40 μs, H=320, uniform at 200 μs, H=80, uniform at 40 μs, H=80. These include conditions with limited savings or uncertain differences. Current workload balance alone is not sufficient.

## Q5: Does a hybrid ever win?

AH is the median winner in 0 states. No winning state was measured; the full action sweep remains available rather than suppressing this negative result.

## Q6: How persistent must workload heterogeneity be?

Past-cost autocorrelation, expensive-region overlap and center displacement are measured. The controller uses a bounded empirical lifetime. Persistence alone does not separate all useful and harmful actions: workload magnitude, transport consequences and setup also matter. No universal required lifetime is established from constructed short kernels.

## Q7: What is the break-even migration horizon?

consequence_models.json reports each measured positive-use-phase crossing as action cost divided by observed solver savings per step, and the dimensionless lifetime/crossing ratio. No positive savings yields an undefined crossing. H=20/80/320 measurements test available intervals; longer extrapolated horizons assume savings persist and are not measured evidence.

## Q8: How important are transport and pressure penalties?

They are included in phase clocks and total wall. Weighted mesh changes processor faces, neighbors and ownership; AM/AH may improve chemistry balance while losing overall. PMPI adds separate migration and solver observations. Rank-mean transport clocks contain synchronization waits; they are not an isolated network measurement.

## Q9: Can those consequences be predicted cheaply?

The past-only ridge model is cheap to evaluate, but its held-out replay is 1.027×. The explanatory post-partition transport model has held-out MAE 0.010021 s/step; the additional MPI-call-duration model has held-out MAE 0.012456 s/step on one unseen moving condition. Computing these post-partition inputs is not free, and MPI includes waits. Initial geometry is constant, so the main communication coefficient is not independently identifiable. This study does not establish a cheap accurate general consequence predictor.

## Q10: Does the controller generalize to unseen flows?

Three whole temperature/velocity/width conditions are held out. Retrospective speedup is 1.027×; actual held-out live speedup is 0.922× [0.895, 0.942] relative to uninterrupted native chemistry. Scope is one constructed periodic geometry and H2 premix, not different burners/fuels/hardware.

## Q11: Does it reduce end-to-end total runtime, including its own overhead?

The live controller ratio is 0.922× and its interval is [0.895, 0.942]. This includes preprocessing, decomposition, measured prefix, all startups/writes, feature extraction, inference and actions. Actual AC gives 1.044×; segmented A0 gives 0.887×. Reusable model-acquisition cost is separately disclosed; it is not hidden as online overhead.

## Q12: Does it preserve numerical results?

There are 375 main same-checkpoint gates, 0 failed, maximum temperature difference 1.694e-07 K. The live collection has 120 comparisons and 1 rejected mesh endpoint(s), retained and marked numerically ineligible; the controller and strong chemistry baseline pass. Fixed-partition and numerical-sensitivity controls investigate the rejection without changing thresholds or removing trials. Restart, deployment, fine-dt and scaling gates add evidence. Stored h/rho, all species and positivity are checked. Physical conservation and grid/time refinement are separate: maximum main mass/energy budget drift is 0.2315% / 22.55%. Passing equivalence does not validate a resolved flame. The face audit identifies eight zero cyclic flux copies; restoring them from their existing periodic partners in independent copies gives maximum T difference 8.231e-11 K with all gates passing. The original failed trial remains rejected. A separate initialization-only executable preserves mass through two complete 240 μs histories (maximum relative drift 1.074e-14); its finest combined time/pressure control still has -1.369% signed energy drift. Neither correction replaces frozen performance data.

## Q13: How does it compare with the strongest reproducible prior baseline?

The directly executed competitor is pinned Stuttgart standard chemistry task balancing, ported to the same v2012, mechanism, Rosenbrock34 and tolerances. AC gives 1.190× held-out replay versus 1.027× for the selector. Uninterrupted Stuttgart live execution gives 1.209× versus the controller's 0.922×. Hindsight oracle gives 1.195×, only 0.430% extra headroom above AC. QUICKLB is also compiled and field-tested on its standalone public-library kernel, not used as a cross-physics leaderboard.

## Q14: What is genuinely novel relative to the literature?

The bounded primary-source search did not establish an identical four-action same-version gated checkpoint oracle. The defensible artifact contribution is that dataset, measured whole-cost tradeoffs, held-out external-controller comparison and documented negative result. Adaptive triggers, migration penalties, prediction, persistence, weighted partitions and chemistry task scheduling have prior art. First-invention and controller-superiority claims are unsupported.

## Q15: What are the limits of the conclusion given the available cluster?

The environment supplies one Ryzen 5600X host and six physical cores, no Slurm allocation or inter-node network. Tested rank range is 1/2/4/6 with bound cores and no oversubscription. Tiny 256/512-cell domains, constructed physics, upwind/Euler discretization, modest repetitions, WSL timing noise and unidentifiable communication geometry limit external validity. Multi-node scale and resolved production flames cannot be inferred.

Evidence: [report](final_report.md), [oracle tables](../tables/oracle.csv), [live tables](../tables/live.csv), [figures](../figures/README.md), [claim verification](claim_verification.md).
