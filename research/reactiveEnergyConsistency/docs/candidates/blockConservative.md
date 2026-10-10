# Frozen-source pressure/species/energy block iteration (F/pivot)

Hypothesis: a small coupling loop over pressure, conservative species and
absolute energy can remove G's final pressure/momentum mismatch without a
second chemistry call or momentum matrix assembly.

Freeze the initial momentum matrix inverse diagonal rAU and constrained HbyA,
and freeze the integrated chemistry species source R_s for the timestep.
At each inner iteration, with current psi(T,Y), solve the conservative pressure
equation `V psi p/dt + div(phiHbyA)-laplacian(rho rAU,p)=V rho_n/dt`.
This uses the actual saved beginning-of-step density, not an inferred history.
Update phi from its pressure flux, U=HbyA-rAU grad p, K and EOS rho. Then solve
the final-flux species residuals and nonlinear absolute-energy residual described
in speciesFlux.md and conservativeState.md. Repeat until the energy-driven
pressure change is small; an iteration-limit failure is retained.

This is a block Gauss-Seidel approximation of a pressure/energy Schur iteration
with species operators inside the thermodynamic block. At fixed Y the EOS
linearization is `delta rho=psi delta p-rho/(Cp T) delta hs`; species-induced
composition changes supply the remaining EOS Jacobian. A strict 2x2 block that
omits that response cannot certify elemental conservation. The momentum
pressure-gradient mismatch is evaluated against the most recent pressure used
to update U, not the original timestep pressure.

At convergence each species and energy equation shares final rho and phi;
local energy and elemental balances follow to their solver tolerances, and
EOS is enforced after energy inversion. Pressure continuity holds for the
same stored initial rho. Momentum satisfies the frozen predictor's correction
to the coupling tolerance. Updating the momentum matrix is deferred to the
next timestep, as in segregated PISO. This is not proof of solving the fully
implicit momentum equation or entropy stability. Smooth first-order consistency
requires bounded frozen-coefficient variation and convergence of the loop.

Scope: fixed orthogonal cyclic/symmetry/empty meshes, ideal-gas sensible enthalpy,
no external source, MRF, pressure clipping, transonic mode or added models.
Newton and block iteration admissibility/convergence failures are explicit;
no global energy redistribution, species clipping or normalization is allowed.
Cost can exceed extra PIMPLE for inexpensive chemistry. Repeating source-frozen
species/energy matrices is only promising if saved chemistry/momentum work
outweighs those solves and field errors improve.

Closest prior: Denner et al. 2020 equations 40–52 conservative coupled p,U,T,
Sirianni primitive conservative updates, Grapsas reacting pressure correction,
McDermott enthalpy/species compatibility. Block Gauss-Seidel, Schur complements,
and frozen chemistry are established ideas. Status: NOVELTY_NOT_ESTABLISHED;
only a specific useful algorithmic/analysis extension could change that.

Screen A/B/F/Mix, dt/2, analytic wave, gauge controls and exact ledgers. Reject
nonconvergence, conservation/positivity/EOS failure, inaccurate fields or poor
cost versus pressure/outer corrections. If it survives, require reacting spatial
and temporal refinements, independent chemistry and resolved reacting validation,
serial/parallel/restart, MPI cost and a second method-specific literature search.
