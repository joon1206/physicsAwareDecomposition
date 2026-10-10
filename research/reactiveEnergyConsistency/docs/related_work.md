# Related work and equation-level distinctions

| Primary work | Established result | Relationship and limitation |
|---|---|---|
| [Yang, Zhao, Ge (2019), reactingFoam-SCI](https://doi.org/10.1016/j.compfluid.2019.06.008) | OpenFOAM 5 platform with midpoint chemistry splitting, stiff ODE error control and improved reacting-flow treatment. | Splitting/chemistry improvements are prior art. Only primary abstract verified; exact pressure/enthalpy corrections and source availability remain unresolved. |
| [Zhou, Zhang, Yang (2022)](https://doi.org/10.3390/aerospace9020102) | OpenFOAM/Cantera reacting solver with well-balanced splitting and combustion diagnostics. | Author source CTreactingFoam was verified at commit 0754a9c: adds differential diffusion/enthalpy terms while retaining explicit K, -dpdt and energy-before-pressure. This source snapshot does not establish every method variant described in the paper. |
| [Speth et al. (2013)](https://doi.org/10.1137/120878641) | Balanced/rebalanced splitting adjusts subproblem sources to improve steady-state consistency. | Conservation at finite pressure iterations and preservation of split steady states are distinct properties. |
| [Wu, Ma, Ihme (2018)](https://arxiv.org/abs/1712.00953) | Simpler balanced splitting and Rosenbrock–Krylov integration with stability and reacting-flow tests. | A candidate reordering/splitting method must address this prior art; the present source-averaged segregated algorithm is not automatically Strang splitting. |
| [Hassanaly et al. (2017)](https://arxiv.org/abs/1705.04777) | Minimally dissipative collocated low-Mach OpenFOAM formulation; consistent continuity/pressure and kinetic-energy discretization; MMS. | Strong precedent for discrete energy-consistency research. Mechanical and thermodynamic pressures are separated in its low-Mach formulation; the present fully compressible hs/Qdot/p update differs. |
| [van der Heul, Vuik, Wesseling (2003)](https://doi.org/10.1016/S0045-7930(02)00086-5) | Conservative Mach-uniform pressure correction on staggered grids. | Pressure-based variables do not inherently forbid conservation. The present question concerns incomplete segregated coupling, not a universal pressure-based limitation. |
| [Denner et al. (2020)](https://www.sciencedirect.com/science/article/abs/pii/S0021999120301224) | Collocated conservative finite-volume framework with fully coupled pressure-based solution for all speeds. | Relevant reference for conservative fluxes and EOS coupling, although the target project seeks lower additional coupling cost. Abstract-only comparison. |
| [Amino et al. (2022)](https://doi.org/10.1002/fld.5116) | Conservative time-staggered variable-density pressure correction in code_saturne. | A limited pressure-energy correction cannot claim this general principle as new. Exact equation comparison remains to be completed. |
| [Grapsas, Herbin, Latché, Nasseri (2020)](https://arxiv.org/abs/2010.07577) | Segregated reactive pressure correction with sensible-enthalpy corrections, discrete total-energy conservation and positivity on staggered meshes. | Closest challenge to broad novelty. Section 6 cancels discrete kinetic dissipation using enthalpy corrections; phenomenological finite-rate flame chemistry and staggered kinetic energy differ from collocated v2012 detailed chemistry. |
| [Ching, Johnson, Kercher (2025)](https://arxiv.org/abs/2501.12532) | Multicomponent pressure-evolution DG scheme with semidiscrete conservative corrections and equilibrium-preserving modifications. | Direct precedent for defect correction restoring energy; equilibrium, zero species and accuracy tradeoffs must be considered. No reacting viscous validation in this work. |
| [Ching et al. conservative reacting DG (JCP 2024)](https://arxiv.org/abs/2211.16254) | Conservative reacting formulation with positivity and entropy control. | Candidate density-based reference must match thermo and chemistry, not treat incompatible model differences as error. |
| [rhoCentralRfFoam integral assessment (2025)](https://www.mdpi.com/2075-1680/14/11/782) | Integral mass/momentum/energy/species evaluation of a density-based reactive solver. | Integral diagnostics are established; a closed equation-term attribution and method cost comparison would need more evidence. |

The installed v2012 reactingFoam and rhoPimpleFoam EEqn sources use explicit
kinetic derivatives and either internal-energy pressure-flux work or hs
-dpdt. Current OpenCFD v2606 preserves this structure plus MRF work; current
Foundation 14 has revised thermophysical transport APIs. The selected source
snapshots and their hashes establish these statements, not the documentation
alone. Core sources were never patched.

The CTreactingFoam source is linked and pinned in
[the author repository](https://github.com/UMN-CRFEL/OpenFOAM-Cantera/tree/0754a9cea2482fff0f6fa6630778f65042f47536),
with energy, species, pressure and main source copies retained under sourceAudit.

No fully coupled conservative solver is claimed to be universally superior.
Low-Mach, acoustic, pressure-equilibrium and kinetic dissipation properties
must be compared for the same governing equations and physical regime.
