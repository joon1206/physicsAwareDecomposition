# Research summary package

We compare unchanged ownership (A0), chemistry-task redistribution (AC), cost-weighted mesh redistribution (AM), and their hybrid (AH) using identical reacting-flow checkpoints, a compatible upstream chemistry baseline, and total future process cost. The corrected study contains 25 states and 500 randomized continuations, five trials per action. Median oracle winners are {'AC': 17, 'A0': 8}. The largest observed action speedup is 1.393×, pointwise 95% bootstrap interval [1.364, 1.437], at heldoutMoving, checkpoint 40 μs, H=80; this is an exploratory maximum, not a universal or confirmatory claim. The held-out retrospective whole-cost selector achieves 1.027× versus 1.190× for the executed chemistry algorithm's always-enabled action. Actual held-out live controller speedup relative to uninterrupted native standard chemistry is 0.922× [0.895, 0.942]. Algorithmic field equivalence and physical accuracy are assessed separately. Coarse transient budgets and refinement results restrict physical interpretation. The contribution is a reproducible local action-oracle and negative/conditional tradeoff evidence; it does not establish a new partitioner, a new adaptive-balancing principle, or a generally superior controller.

| Executed policy | Held-out end-to-end runtime ratio | 95% within-condition bootstrap interval | Numerically eligible |
|---|---|---|---|
| nativeContinuous | 1.000 | [1.000, 1.000] | True |
| continuous | 0.996 | [0.962, 1.015] | True |
| ACContinuous | 1.209 | [1.178, 1.243] | True |
| A0 | 0.887 | [0.861, 0.924] | True |
| AC | 1.044 | [1.004, 1.067] | True |
| AM | 0.697 | [0.682, 0.717] | False |
| imbalanceThreshold | 1.054 | [1.019, 1.079] | True |
| persistenceBreakEven | 1.037 | [0.992, 1.066] | True |
| controller | 0.922 | [0.895, 0.942] | True |

See [highlight figures](../figures/highlights/), [architecture](../figures/33_architecture.png), [workflow](../figures/34_methodology.png), [complete results](final_report.md) and [summary tables](../tables/summary.md).
