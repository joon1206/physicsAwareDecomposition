# Constant-volume chemistry source-path control

2026-10-06. Derivation before implementation. Status: IMPLEMENTATION_ONLY;
constant-volume chemistry is established physics, not a novelty claim.

## Measured limitation and actual installed equations

The conservative state correction still has first-order homogeneous reacting
error against the independently matched Cantera closed-volume trajectory.
The installed v2012 StandardChemistryModel::derivatives advances molar
concentrations c, temperature T and a pressure slot p:

    dc_s/dt = omega_s(c,T,p),
    dT/dt = -sum_s Ha_molar,s omega_s / sum_s c_s Cp_molar,s,
    dp/dt = 0.

Its code explicitly selects the constant-pressure thermal path. The native
source wrapper returns RR_s=W_s(c_new-c_old)/dt; the CFD energy equation then
advances a separate state. Closing that later energy residual cannot retroactively
change the temperatures sampled inside the source integration. This distinction
is a source-path/splitting mechanism, not another net density compensation.

The source was read locally at StandardChemistryModel.C derivatives and solve,
and chemistrySolver/ode/ode.C. A constant-pressure subproblem can be appropriate
in other formulations; its use is not labelled a universal OpenFOAM bug.

## Closed-volume equations and invariant

For fixed cell volume, balanced ideal-gas chemistry gives

    rho = sum_s W_s c_s,  d(rho)/dt=0,
    E_internal = sum_s c_s Ea_molar,s(T),  dE_internal/dt=0,
    Cvol = sum_s c_s Cv_molar,s(T) > 0,
    dT/dt = -sum_s Ea_molar,s omega_s / Cvol,
    p = Ru*T*sum_s c_s,
    dp/dt = Ru*(T*sum_s omega_s + sum_s c_s*dT/dt).

This follows by differentiating absolute internal energy, including formation
energy. An elemental reference shift changes the numerator by an elemental
production rate, which is zero for balanced chemistry. Neither a formation-only
source nor a second chemical heat term is added to absolute energy.

Use the same installed reactions and JANAF thermodynamics; only the ODE thermal
path changes. Evaluate reaction pressure from the concentration/T EOS, rather
than an inconsistent redundant pressure slot. Retain that slot's derivative
for the native ODE interface and report its endpoint EOS discrepancy before
setting returned pressure to its concentration/T value. The CFD source wrapper
still returns integrated species rates once; its Qdot remains -sum Hc_s RR_s.

The invariant is exact for the continuous local ODE. A tolerance-controlled
generic integrator preserves it only approximately. The full conservative G
residual subsequently enforces the CFD physical-energy target; a successful
homogeneous result requires both the source trajectory and that target.

## Scoped implementation and Jacobian

Create a separate cvOde runtime chemistry solver library for the selected
psiReactionThermo/gasHThermoPhysics registration. It must not replace any
installed or accepted chemistry solver. Use native ODESolver/Rosenbrock34.
Compute a finite-difference Jacobian of the entire modified RHS, including
temperature and pressure responses. This deliberately avoids claiming that
the installed constant-pressure temperature Jacobian is a constant-volume
Jacobian. It is a verification implementation, not an optimized chemistry kernel.

Use the inherited rate evaluation's intermediate concentration safeguard.
Do not clip accepted concentration outputs to force positivity; retain small
negative traces with their recorded magnitude and reject significant negatives.
Log local species mass, absolute internal energy and pressure-slot discrepancies
before/after each source integration. No general positivity or entropy theorem
is asserted. Domain physical invariants and final primitive states remain
independently checked from saved fields, not merely from this log.

## Falsifiable hypothesis and acceptance

First test uniform closed H2/air at 1100 K, zero velocity, chemistry on, As=0,
TF=240 us, same legacy NASA/kinetic conventions as the verified Cantera phase.
Use thin nx8/ny1 cases, dt1/.5/.25/.125 us, baseline and conservativeState,
with the cvOde source. Preserve every input and exact library/source hash.

Hypothesis: G+cvOde removes the first-order source-path error in the homogeneous
limit, leaving the local ODE/thermo tolerance floor. Before promotion, require
T endpoint error <1e-5 K, absolute relative global energy drift <1e-9, mass and
elements <1e-9, sumY <1e-9, positive T/p and acceptable species traces. Tighten
ODE tolerance separately to identify any remaining floor. Do not infer high
CFD time order from a homogeneous source-only control.

The baseline+cvOde control must identify whether source-path accuracy alone
removes the post-pressure density/energy mismatch; it is expected not to supply
the full conservative discrete identity. If the homogeneous control passes,
screen F at dt2/1 us to assess the observed coarse quenching sensitivity. That
screen is not resolved reacting validation. Extra local Jacobian/rate work and
MPI cost must be measured before any efficiency claim.

## Primary prior-art boundary

[Cantera IdealGasReactor equations](https://cantera.org/stable/reference/reactors/ideal-gas-reactor.html),
equations (3)–(4), explicitly give the species and Cv/internal-energy thermal
path. This control implements that established closed-volume limit with the
installed native rates. Source/transport splitting and conservative reacting
formulations also have extensive prior art. A successful port is a diagnostic
or useful implementation; it does not establish a new numerical method.

## Pilot and additional isolation before refinement

The first CV G dt1 us pilot completes: T error 1.28694e-8 K against the strict
Cantera endpoint, global energy drift 7.68932e-15, maximum source internal-energy
relative change 2.72392e-14, pressure-slot mismatch 1.07538e-14, and no negative
accepted concentration. That temperature difference is within the measured
Cantera tolerance contrast (2.49488e-8 K); it is not a resolved true-error floor.

Before broader conclusions, add the installed constant-pressure RHS to the
same new FD-Jacobian/native-ODE interface via a separate runtime path selection.
It retains Cp/Ha and a fixed pressure slot. Compare G at dt1 us and identical
rtol1e-10/atol1e-16 to isolate the source thermal path from the Jacobian change.
The returned pressure for this control remains its integrated constant slot;
the diagnostic concentration/T EOS mismatch is expected and is not projected
away. Accepted output concentrations remain unclipped in both controls. The
original Cv-only snapshot/pilot remains retained; new paths use tagged cases.

## ODE interface audit and superseded evidence

Before interpreting the spatial reacting screen, direct inspection of the
installed ODESystem.H and Rosenbrock34.C found an adapter error: jacobian's
vector argument is the explicit partial derivative of the RHS with respect
to time, not the RHS itself. The autonomous reaction equations require zero.
The first adapter copied the installed chemistry callback's convention and
returned the RHS there. All pilot/pathControl cases are retained but superseded;
their small endpoint discrepancies do not validate that incorrect interface.
The initial F screen was intentionally interrupted and its inputs/logs retained.

The corrected implementation returns zero explicit time derivative and still
forms the full state Jacobian by finite differences. Corrected cases carry
the dfdt0 tag and a new exact chemistry source/library hash. A native probe
must independently compare explicit time dependence, Jacobian-vector products
against a larger directional perturbation, and the continuous mass/thermal/EOS
identities before rerunning the homogeneous and spatial controls. Predeclared
probe tolerances: zero autonomous time dependence, scaled directional-Jacobian
discrepancy below 1e-4, scaled continuous invariant residual below 1e-12.
No change is made to installed or accepted chemistry implementations.

The corrected native probes complete for eight temperatures in each thermal
path: explicit time derivative is exactly zero, largest directional-Jacobian
discrepancy 7.69741e-8, and continuous mass/thermal/pressure identities satisfy
the predeclared thresholds. Corrected matched-path G dt1 us: CV T discrepancy
1.06575e-8 K; installed-thermal-path CPFD discrepancy 8.58425e-4 K. Both
conserve global energy to recorded roundoff. These observations support the
homogeneous source-path mechanism; refinement/tolerance and spatial controls
remain distinct tests. Spatial F screens compare both paths with the same
Jacobian/tolerances, baseline and G, at dt2/1 us. The default native source's
different Jacobian/tolerances are not used as the causal path contrast.

Additional equation-level prior art:
[PelePhysics reactor implementation](https://pelephysics.readthedocs.io/en/latest/CvodeInPP.html)
derives its Cv/internal-energy source with optional external forcing and a
separate Cp/enthalpy formulation. With forcing zero the former has the same
closed-volume limit as this control; its state representation and integrator
implementation differ. Thus selecting Cv or appending transport forcing is
already an established principle, not a surviving novelty claim here.

## Broader homogeneous regimes selected before execution

The 1100 K/one-atmosphere reactor is a single source-only limit. Check two
additional declared H2/air states: 950 K at ten atmospheres, and 1500 K at one
atmosphere, both TF=240 us. The former probes higher-density induction and
the latter hot initial kinetics. Use unchanged Y and legacy thermochemistry,
dt1 us, baseline and G, matched Cv source rtol1e-10/atol1e-16, no transport.
Generate independent Cantera references with the already matched immutable
mechanism, clone=False, initialized molecular-weight/density assertions, and
two independent tolerances. These are regime controls, not mesh verification.
Require G T endpoint difference <max(1e-5 K, 10 times the measured reference
tolerance contrast), energy/mass/elements <1e-9, source mass <1e-12 and source
energy <1e-10 relative, admissible primitives and trace species. Preserve any
failure; a successful hot/cold reactor still establishes no spatial order or
new numerical principle. Baseline controls retain their measured defects.

The corrected dt1/.5/.25/.125 us homogeneous Cv/G contrasts are all within
the 2.49e-8 K independent reference tolerance contrast. Source alone retains
first-order endpoint error and the CFD conservation defect. The hot 1500 K
control passes; cold/high-pressure original G fails its absolute Newton cutoff.
Separate stopping controls retain that failure and complete it only under the
documented cap fallback, without changing old completing fields.

All eight matched CPFD/CV F controls complete. Both conservative paths quench
near 727 K at dt2 us and burn near 2845 K at dt1 us. Their zero-transport
endpoint contrast is not a resolved reference error. Three spatial Cv
configurations fail the original accepted-source energy threshold at and
around the NASA 1000 K switch. The direct native/Cantera branch audit in
thermoBranchSourceInvariant.md isolates a data/RHS incompatibility in its
declared controls. The continuous identity is branchwise; no unconditional
source-invariance or higher-order reacting-flow claim is retained. Exact prior
inputs, failed source gates and superseded callback runs remain unchanged.
