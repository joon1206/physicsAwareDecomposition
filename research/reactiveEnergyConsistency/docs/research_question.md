# Research question and gates

Can a discrete equation budget separate the final-state density, kinetic,
pressure-work and species/chemistry mismatches of segregated reactingFoam,
and does that evidence support a cheaper conservative coupling method?

This study targets OpenCFD v2012, Euler time discretization, fixed meshes,
sensible enthalpy, perfect-gas JANAF mixtures, laminar integrated chemistry,
and closed cyclic/symmetry/empty boundaries first. It is not an assertion
about every OpenFOAM fork or thermodynamic model.

1. Freeze the completed action artifact by tracked-file SHA256; never rebuild
   its binaries or rewrite its documentation, processed data or raw cases.
2. Audit primary literature and local source before proposing a correction.
3. Reproduce the initialization-only high-drift moving hydrogen history and
   compare an independent inventory against the online ledger.
4. Close the implemented discrete equations per timestep and validate the
   ledger in homogeneous nonreacting and reacting systems.
5. Isolate changes in dt, pressure corrections, outer corrections and linear
   tolerance. Test instrumentation, restart, MPI and chemistry ownership.
6. Only then derive any method in `method_derivation.md`, including formal
   accuracy and stability assumptions. No global energy rescaling is allowed.

H1: lagged pressure work and final density/kinetic changes dominate.
H2: equation-derived terms predict the measured defect independently of a
stage telescoping sum. H3: a derived local correction improves asymptotic
energy order. H4: it beats extra outer coupling on accuracy/cost. H5: its
result is independent of chemistry task ownership. H3–H5 require a method;
they are not accepted from baseline audit results.

Negative results and unavailable reference physics remain explicit. Local
timings cannot support large-cluster conclusions or a publication claim.
