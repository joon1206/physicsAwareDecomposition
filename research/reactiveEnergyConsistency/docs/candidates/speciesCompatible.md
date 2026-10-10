# Conservative density/species/energy pairing: evidence-driven pivot

The nonreacting variable H2/N2 control preserves total mass and its fields across
formation offsets, but after 240 us its H mass rises by 0.192225% and N mass
falls by 0.020579%. Thus an arbitrary species enthalpy shift changes the absolute
global defect by `sum_s g_s Delta M_s`. An elemental gauge does so when element
masses are not conserved. This is a measured species-density defect, not a
thermodynamic text-rounding effect: T differences are below 2.3e-12 K.

The energy density defect and the species density defect are the same
coefficient replacement in different conserved variables:
`delta(rho Yi)=delta rho Yi_b` and `delta(rho ha)=delta rho ha_b`.
An energy-only correction at fixed final Y cannot restore the missing elemental
balance. At fixed rho,p,Y the EOS also prevents any nonzero energy correction.
Therefore the proposed strong fixed-final-state hypothesis is false under the
perfect-gas assumptions unless a compatible update changes more of the state.

A purely local repair `Yi_new=rho_a Yi_b/rho_f` preserves the assembly species
inventories but gives `sum Yi_new=rho_a/rho_f`, generally not one. Normalizing
returns Yi_b and restores the original defect. A viable correction must include
the matching conservative mass redistribution through shared face fluxes.

Next derived test: advance the same rhoY and absolute total-energy inventory
with final mass flux, then jointly recover Y,T,p and recompute compatible
pressure/momentum corrections. The pressure-energy block alone cannot certify
elemental conservation if its density/flux changes leave species untouched.
This broader compatible transport principle has substantial prior art; any
novel claim must concern a specific low-cost algorithm or error control, not
the generic requirement of conserving all state components.

Expected cost and order depend on the chosen coupled update and are unresolved.
Acceptance requires the variable-composition control, reference-invariant
trajectory, mass/elements, EOS, local energy closure, independent field errors
and runtime against additional PIMPLE iterations. This is an unresolved
candidate, not proof that the research direction is exhausted.
