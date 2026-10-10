# Conservative compressible reacting reference — limited inviscid scope

This reference is a new research-only adaptation of the installed v2012
rhoCentralFoam, which implements established Kurganov central-upwind fluxes.
It is an independent numerical formulation for comparing pressure-based
candidate trajectories, not a proposed novel method. Original copied source
and hashes are retained alongside the adaptation. Installed OpenFOAM and the
completed baseline/actionStudy are not edited.

Advance conservative rho, rhoU, rhoYa for *every* species including the inert,
and rhoEa=rho(e_s+hc+K). The directed species flux uses the same central-upwind
wave-speed weights and density reconstruction as continuity. With linear
first-order reconstruction, summed species mass flux equals the continuity
mass flux, and balanced chemistry conserves the summed species mass. Add the
saved native integrated chemistry production rates to species equations once
per time step. They are evaluated from the old primitive state, independently
of the pressure-based prototype's residual correction.

The energy flux is the native conservative central-upwind total-enthalpy
flux with absolute internal energy e_a=e_s+hc. Chemical formation is included
in the conserved energy variable, so no Qdot is added to absolute total energy.
After mass/species/momentum updates, recover Y=rhoY/rho and solve the local
equation `Ea(T,Y)=rhoEa/rho-K`, using Cv as its derivative within a smooth
thermodynamic branch. Set the selected
primitive sensible h to `Ha(T,Y)-hc(Y)`, refresh thermodynamics and set
p=rho/psi. This retains the installed registered reacting sensible-h models;
it does not rely on unavailable const-Cp internal-energy chemistry registrations.
There is no pressure solve or post-pressure energy correction. Do not clip or
renormalize species; retain positivity/conservation failures explicitly.

Scope is periodic/symmetry/empty fixed meshes and **zero viscosity, diffusion,
external forcing and radiation**. The solver rejects a nonzero transport
coefficient. Its central numerical diffusion is a different spatial operator
from the pressure-based upwind convection. They must therefore be compared
under spatial and temporal refinement, not expected to agree cellwise on a
coarse mesh. The original F kernel also has As=0, but the one-column controls
separately fix geometry, native ODE and timestep conventions before comparisons.
No spatially resolved exact-reference claim is made for either geometry.

As a closed-domain consequence of shared conservative fluxes, absolute total
energy and mass telescope to boundary flux/linear residual tolerance; each
species retains its finite-volume source balance. This is not an entropy
stability or arbitrary-step positivity proof. Native chemistry integrates a
constant-pressure thermodynamic subproblem to estimate rates; resetting to
conserved total energy gives an Euler splitting method. Independently verify
its homogeneous constant-volume refinement against the corrected Cantera
reference before using it for reacting-flow comparisons.

Verification hierarchy: (1) analytic pure-gas entropy wave, (2) analytic
finite-rate equal-property isomerization wave, (3) closed homogeneous H2
chemistry and timestep refinement, (4) resolved one-dimensional inviscid H2
ignition/transport with both spatial and temporal refinement. Only levels
that execute and pass are reported. This is not a freely propagating flame
speed validation or a conservative solver whose correctness is assumed merely
because its total energy is conserved.

## Cancellation-aware root stopping (hRecovery3)

The retained nx512 hRecovery2 run failed its local inversion after 224.4296875
us despite admissible preceding states. A relative tolerance scaled only by
net absolute internal energy can demand below roundoff when formation,
sensible and gas-energy terms cancel. The new stopping scale is

```
S = |e_target| + sum_s |Y_s| (|Ha_s(T)| + |R_s T|),
|e(T)-e_target| < 1e-9 J/kg + 128 epsilon_machine S.
```

This is a floating-point backward-error criterion, not a relaxation based on
physical solution error. Bracketing, positive Cv, positive rho and the declared
200–5000 K range remain enforced. Failure now reports cell, temperature,
target, residual, tolerance and scale. The hypothesis is cancellation-limited
roundoff, not a proved diagnosis from the old abbreviated fatal message. A
new separately named run must falsify or support it; old failure fields/logs
are retained. Independent recovered-energy agreement remains mandatory.

The later actual-data branch audit limits any global inversion guarantee:
positive Cv within each NASA branch does not ensure continuity, surjectivity
or uniqueness across its 1000 K switch. The legacy data admits a conservative
target with no root and a pure-N2 target with two roots; see
candidates/thermoBranchInversion.md. Existing successful recovered-energy
checks remain scoped numerical evidence. The current reference implementation
is not promoted as a universally valid root solver or a new method, and its
original cases/data are retained unchanged.
