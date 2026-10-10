# Figure captions and evidence

## 03_chemistry_imbalance

Measured strict-tolerance LTS run medians. Step wall includes MPI waiting; near-unity step imbalance does not establish balanced compute.

## 04_step_imbalance

Measured strict-tolerance LTS run medians. Step wall includes MPI waiting; near-unity step imbalance does not establish balanced compute.

## 05_strong_scaling

Measured 1/2/4-core WSL strong scaling, including MPI launch and final output. No extrapolation beyond tested ranks.

## 06_parallel_efficiency

Measured 1/2/4-core WSL strong scaling, including MPI launch and final output. No extrapolation beyond tested ranks.

## 07_workload_by_rank

Native partition metrics; predicted cost is summed from the independent serial training trace, not measured parallel chemistry time.

## 08_cells_by_rank

Native partition metrics; predicted cost is summed from the independent serial training trace, not measured parallel chemistry time.

## 09_faces_by_rank

Native partition metrics; predicted cost is summed from the independent serial training trace, not measured parallel chemistry time.

## 10_synthetic_amplitude

Derived workload imbalance from measured native assignments, using actual cell centres. These are predicted work sums, not CFD runtime.

## 11_gamma_speedup

Measured strict LTS medians. Speedup error bars are pointwise 95% bootstrap intervals from five whole-run trials; exploratory gamma selection is not corrected.

## 12_gamma_faces

Measured strict LTS medians. Speedup error bars are pointwise 95% bootstrap intervals from five whole-run trials; exploratory gamma selection is not corrected.

## 13_gamma_neighbours

Measured strict LTS medians. Speedup error bars are pointwise 95% bootstrap intervals from five whole-run trials; exploratory gamma selection is not corrected.

## 19_decomposition_overhead

Measured strict LTS medians. Speedup error bars are pointwise 95% bootstrap intervals from five whole-run trials; exploratory gamma selection is not corrected.

## 14_chemistry_fraction

Measured samples only. Chemistry fraction depends on partition and MPI waits in other phases; it is not an independently controlled explanatory variable.

## 15_prediction_vs_timing

Predicted serial-clock workload versus measured parallel chemistry phase imbalance. Neither is total timestep makespan.

## 16_reactive_runtime

Five strict-tolerance trials; bars are medians and whiskers are sample standard deviations. Includes launch/output, excludes training/decomposition.

## 17_cost_persistence

Measured per-cell wall-clock correlations from serial training. Temporal persistence is in LTS iteration space, not physical time.

## 18_instrumentation_overhead

Seven randomized repetitions, 80 LTS iterations. Small differences overlap run variability; full per-cell tracing is materially more costly. Disabled negative estimates are noise, not an optimization claim.

## 20_measured_regimes

Measured regime samples, including stale weights after chemistry is disabled. Sparse samples do not establish a universal crossover surface.

## 01_rank_chemistry

Measured local wall durations from strict repeat 0. Step includes waits and final output; the maximum is an offline per-iteration proxy, not an added barrier.

## 02_timestep_makespan

Measured local wall durations from strict repeat 0. Step includes waits and final output; the maximum is an offline per-iteration proxy, not an added barrier.

## 21_spatial_relationship

Native training cost and reconstructed strict-solver temperature; processor maps come from cellProcAddressing. Identical camera and ownership color range.

## 22_heat_release_species

Native strict-run reconstructed fields. These images establish localized reaction structure; they are not experimental validation of this one-step chemistry mechanism.

## 23_negative_control

Five strict-tolerance trials. Static weights predict a chemistry workload that is absent, producing a clear transport imbalance regression.

## 24_numerical_failure_repair

Log axis explicitly used to display orders of magnitude. Original loose LTS performance result fails the numerical gate and is excluded from accepted speedup conclusions.

## 25_smoothing_sensitivity

Derived smoothing sensitivity from the same measured serial trace; it is predictor accuracy, not a measured solver-runtime optimization.

## 26_substeps_proxy

Measured relationship between chemistry-loop substeps and elapsed cell cost. It is not an ODE RHS/Jacobian evaluation count.

## 27_phase_profile

Lightweight measured phase profile. Pressure/species/energy times include solver communication and idle time; no MPI-only attribution is made.

## 28_synthetic_compute_communication

Measured trigonometric CPU work with verified coupled processor halos and intentional step barriers. This controlled workload is separate from reactive CFD.

## 29_communication_pressure

Measured 64x32 four-rank Gaussian CPU/halo workload, five trials per sample. Benefit diminishes at high communication pressure; the high-halo interval includes unity. Low/high campaigns were separate, so this is not a causal universal crossover threshold.

## 30_moving_hotspot

Derived work sums on measured native 64x32 four-rank static partitions. Hotspot translation is analytic, not moving chemistry or a dynamic migration experiment.
