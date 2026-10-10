# Thermochemical invariants and finite state maps

This derivation uses absolute species properties and applies to any continuous
thermodynamic representation. A discontinuous representation adds signed event
jumps, as demonstrated in cv_source_invariant_results.md. NASA continuity
controls are baseline experiments, not candidate numerical corrections.

Let c_i be kmol/m3, W_i kg/kmol, q_i=rho Y_i=W_i c_i kg/m3, and
omega_i=dq_i/dt kg/(m3 s). Let B_ei count atoms and
A_ei=B_ei W_e/W_i. Then A omega=0 has units kg_element/(m3 s),
sum omega=0 has units kg/(m3 s). Mass is redundant when the element set is
complete and W_i=sum_e B_ei W_e. Independent constraints should be selected
by matrix rank rather than imposing duplicate rows in a KKT system.

For the installed perfect gas, species h_ai(T)=h_si(T)+Hc_i J/kg,
Hc_i=h_ai(298.15 K), R_i=Ru/W_i, e_ai=h_ai-R_i T, and
p=sum_i q_i R_i T. Mixture ha=sum Yi h_ai, hc=sum Yi Hc_i,
hs=ha-hc, ea=ha-p/rho. K=|U|2/2 is unchanged by a homogeneous
source step without momentum forcing. The CFD conserved density is
rho(hs+hc+K)-p. Qdot=-sum Hc_i omega_i W/m3 converts sensible and
formation energy; it is not external heat.

## Constant volume

For an adiabatic fixed volume, rho is constant and

```
sum_i q_i e_ai(T) = E_target [J/m3]
rho Cv dT/dt = -sum_i e_ai(T) omega_i
p = sum_i q_i R_i T.
```

For any finite species update delta q, the necessary and sufficient operation
for energy restoration is evaluation/inversion of this same absolute-energy
function at q_new. If Y_new is already nonnegative and element conserving,
holding Y_new fixed and solving ea(Y_new,T_new)=ea_old preserves those
properties. Existence requires the target lie in the admissible energy image.
Continuity and positive mixture Cv on a temperature interval imply uniqueness
there, but do not imply existence for every target. Legacy gap/overlap examples
invalidate the global continuity assumption. Setting pressure from EOS is
necessary; holding both rho and p instead fixes T and can make restoration
impossible.

Finite sensible transfer at fixed volume is

```
delta(rho hs) = -sum_i Hc_i delta q_i + delta p.
delta(rho es) = -sum_i Hc_i delta q_i,  es=hs-p/rho.
```

Thus formation-only transfer in a sensible-enthalpy update is insufficient
unless its pressure term is included. Variable Cp and temperature-dependent
absolute properties enter the inversion; Hc itself remains constant.

## Physical constant pressure versus the installed thermal abstraction

For a closed expanding adiabatic constant-pressure reactor, specific enthalpy
ha(Y,T) is invariant, rho follows p/(R(Y)T), and mass m is constant while
V=m/rho changes. dY_i/dt=omega_i/rho and
Cp dT/dt=-sum h_ai omega_i/rho. Concentrations also contain dilution
dc_i/dt=omega_i/W_i-c_i d(log V)/dt. Therefore source equations c'=rates
at fixed p with a Cp/Ha thermal RHS omit expansion/dilution and represent the
installed fixed-p thermal subproblem, not that physical reactor. Its conserved
algebraic quantity is sum c_i H_ai under its own concentration convention.

For the physical finite map, delta hs=-sum Hc_i delta Yi [J/kg],
ha_new=ha_old. Energy-density residuals are inappropriate because volume
changes. Total internal energy changes by -p delta V; total enthalpy is
constant. Do not require both CV energy and CP enthalpy invariance.

## Per-step residuals

At CV define R_element=A(q_new-q_old) [kg_element/m3],
R_mass=sum(q_new-q_old) [kg/m3],
R_energy=sum q_new e_a(T_new)-sum q_old e_a(T_old) [J/m3],
R_enthalpy=sum q_new h_a(T_new)-sum q_old h_a(T_old) [J/m3],
R_EOS=p_new-sum q_new R_i T_new [Pa]. CV requires R_enthalpy=delta p,
not zero. At physical CP use Yi: R_element=A delta Y [kg_element/kg],
R_mass=sum delta Y [dimensionless], R_enthalpy=delta ha [J/kg],
R_energy=delta ea+p delta(1/rho) [J/kg], and the same EOS residual.

Residual units, absolute values and normalization denominators must all be
reported. An elemental energy-reference shift changes an energy residual only
by its corresponding element residual. A conservation residual does not bound
species/temperature trajectory error or splitting/transport truncation.

## Finite native source interface

If RR_i=(q_i_chem-q_i_old)/dt and Qdot=-sum Hc_i RR_i, then
dt Qdot+sum Hc_i delta q_i=0 algebraically. Replacing RR_i by the same
finite update is already equivalent to this interface. Its CFD species solve
does not generally finish at q_chem after transport and density replacement.
That distinction, and pressure/kinetic changes after enthalpy assembly, remain
in the existing eight-term and cellwise identities. A generic conservative
chemistry transition map therefore cannot by itself cancel the CFD defect.

Projection is an established ODE technique. A weighted constrained full state
projection has KKT equations W delta z+J_C^T lambda=0, C(z+delta z)=0,
with positivity inequalities. Linear invariants remain fixed under a scalar
temperature recovery, but only if the provisional species already satisfy
them. Neither the projection nor its conservation property implies novelty
or a lower accuracy/cost frontier.

For an imperfect provisional species vector, the full constraint must be
A(Y*+delta Y)=A Y_old, not merely A delta Y=0. The latter preserves an
existing elemental residual. Likewise sum(Y*+delta Y)=sum(Y_old).
A scalar temperature recovery cannot remove either residual. The two
observed eligible endpoint recoveries that miss the declared mass/element
gate illustrate this distinction; recovering energy is a conditional result.
