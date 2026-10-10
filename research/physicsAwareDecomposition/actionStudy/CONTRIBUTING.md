# Contributing

Run the unit and MPI smoke tests before changing numerical or restart behavior. Preserve canonical cell IDs through redistribution, assert physical endpoints, charge real action costs, and retain failed runs. Numerical gates and split definitions must be fixed before new performance data are examined.

Use new output directories for experiments. Record seed, mechanism/tolerances, grid, timestep, compiler, MPI placement, hardware and timing scope. Keep transient fields/build products outside Git; commit compact evidence and data-generated plots. Do not remove noisy trials or tune on held-out conditions.

Report numerical equivalence separately from conservation and refinement. Use primary sources for literature claims and retain explicit access limitations. A pull request should explain the scientific or software issue, the resulting behavior and meaningful validation.
