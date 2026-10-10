# Multicomponent pressure-equilibrium diagnostic

Date: 2026-10-06. This is an evidence-driven transport/remapping pivot, not a
new correction or a novelty claim. Derivation precedes its numerical test.

## Hypothesis and exact solution

The equal-property entropy-wave tests do not exercise nonlinear composition
thermodynamics. Consider inviscid, nonreacting H2/N2 with the installed NASA7
thermodynamics, periodic length L=0.02 m, constant pressure p0=101325 Pa and
velocity u0=40 m/s. Define z=x/L-u0*t/L,

    T(z)=800+200*sin(2*pi*z) K,
    Y_H2(z)=0.08+0.05*cos(2*pi*z),  Y_N2=1-Y_H2,
    rho(z)=p0/[R(Y(z))*T(z)].

All other species are exactly absent. Chemistry, viscosity and diffusion are
disabled. Every primitive profile translates at u0. Constant p and u are exact
solutions of the momentum equation; rho, rhoY and rhoEa satisfy scalar
advection. This supplies independent field errors with realistic unequal gas
constants and heat capacities, without an uncertain detailed-flame reference.

## Conservative mixing constraint

Let q_s=rho*Y_s and m=rho*u. At fixed p0,u0,

    T_p(q)=p0/sum_s(q_s*R_s),
    E_p(q,m)=sum_s q_s*[Ha_s(T_p)-R_s*T_p] + |m|^2/(2*sum_s q_s).

A common-weight conservative remap produces q'=sum_a w_a*q_a,
m'=sum_a w_a*m_a and E'=sum_a w_a*E_a. The weights sum to one. Constant
velocity is retained since m_a=u0*sum_s q_as. Constant pressure additionally
requires E_p(q',m')=sum_a w_a*E_p(q_a,m_a). That equality generally fails because
E_p is nonlinear. With one thermodynamic state per cell, fixed conservative
targets and an admissible unique thermodynamic inversion, p is then determined; a local T change
that enforces p0 changes the energy target. Formation-reference shifts add a
linear function of q, so they cancel from this discrepancy and cannot cure it.

This statement is conditional on the specified common-weight remap. It is not
an impossibility theorem for all conservative numerical fluxes, enriched
representations, subcell closures or equilibrium-preserving methods.

## Relation to the measured defect and prior work

The original ledger remains central: G/block can remove its full density and
species/energy residual while still suffering thermodynamic mixing error.
The new diagnostic distinguishes that error from lost global energy. It also
tests whether a conservative restart/remapping pivot inherits the same issue.

[Ching, Johnson and Kercher 2025](https://arxiv.org/html/2501.12532v1),
equations 2.14-2.15 and 3.8-3.12, derive the thermodynamic pressure condition
and energy-residual corrections for DG. Their analysis discusses FV prior
work and distinguishes semidiscrete from fully discrete conservation. Our
single-state FV mixing calculation and these tests are diagnostics, not their
DG algorithm and not a new pressure-equilibrium method.

## Cost, predicted failures and acceptance criteria

No solver modification is needed: use existing baseline, G, tight block,
central and HLLC executables. First test the mixing identity independently.
Then run nx32/64/128 at dt20ns to 20us, retaining physical pressure deviations,
T/species errors, mass/elements/energy, local energy balance, positivity and
EOS residuals. Do not require p roundoff from unequal-thermodynamic mixtures;
the falsifiable question is whether each existing method actually preserves
it and how deviations refine. Expected order is at most first order for the
chosen upwind/Euler schemes. Small energy drift alone cannot pass this test.

Promotion would require an identifiable new compatibility construction and
independent accuracy/cost evidence. Known pressure/energy or flux corrections
cannot be promoted solely because they work in this implementation.
