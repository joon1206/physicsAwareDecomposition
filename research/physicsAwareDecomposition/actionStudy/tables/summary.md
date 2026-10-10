# Summary results

| Held-out replay policy | Aggregate speedup [conditional 95% CI] | Mean regret (s) | Worst regret (s) | Oracle-optimal fraction |
|---|---|---|---|---|
| never | 1.000 [1.000, 1.000] | 0.644 | 2.175 | 0.333 |
| imbalanceThreshold | 1.184 [1.168, 1.200] | 0.031 | 0.032 | 0.833 |
| periodicChemistry | 1.190 [1.173, 1.211] | 0.014 | 0.064 | 0.667 |
| periodicMesh | 0.767 [0.755, 0.779] | 1.845 | 4.198 | 0.000 |
| stuttgartEveryStep | 1.190 [1.174, 1.209] | 0.014 | 0.064 | 0.667 |
| persistenceBreakEven | 1.133 [1.122, 1.149] | 0.179 | 0.917 | 0.667 |
| wholeSolver | 1.027 [1.017, 1.036] | 0.541 | 2.205 | 0.500 |
| oracle | 1.195 [1.179, 1.212] | 0.000 | 0.000 | 1.000 |

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

| Ranks | Policy | Median action + solver wall (s) | Strong-scaling speedup | Efficiency |
|---|---|---|---|---|
| 1 | A0 | 10.824 | 1.000 | 1.000 |
| 1 | AC | 10.872 | 1.000 | 1.000 |
| 1 | controller | 10.845 | 1.000 | 1.000 |
| 2 | A0 | 8.052 | 1.344 | 0.672 |
| 2 | AC | 6.246 | 1.741 | 0.870 |
| 2 | controller | 6.243 | 1.737 | 0.869 |
| 4 | A0 | 5.358 | 2.020 | 0.505 |
| 4 | AC | 3.966 | 2.741 | 0.685 |
| 4 | controller | 4.036 | 2.687 | 0.672 |
| 6 | A0 | 4.318 | 2.507 | 0.418 |
| 6 | AC | 3.457 | 3.145 | 0.524 |
| 6 | controller | 4.350 | 2.493 | 0.416 |