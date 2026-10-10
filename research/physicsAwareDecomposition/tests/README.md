# Test scope

Run the final smoke suite using scripts/reproduceStudy.sh --smoke. Component tests check distributions, nonnegative/finite costs, normalization/clipping/EMA, load metrics, correlation/zero variance, break-even arithmetic and strict OpenFOAM field/label parsing.

Integration checks compare stock/instrumented/cost solvers with identical serial/two-rank partitions, native thermo fields and residual histories. Native probe histories provide iteration-by-iteration T/p/U/species checks at three points. Serial and two-rank decomposed restarts hold loaded chemCost exactly with alpha=0. Invalid alpha and negative trace intervals fail with native diagnostics.

Full-study checks retain weight survival, cellProcAddressing, reconstruction, strict partition field norms and a fixed-dt sensitivity. Inventory agreement is checked across solutions; a closed conservation flux budget is not performed. tests do not establish arbitrary thermo registration, dynamic migration or detailed-mechanism accuracy.
