# Benchmark evidence and limits

| Level | Implemented control | What is established |
|---|---|---|
| A | Uniform N2, 800 K, zero U, chemistry off | Machine-precision closed energy and thermo/mass bookkeeping. |
| B | Uniform H2/air, 1100 K, zero U, closed volume; dt=2,1,0.5 μs | Species/Qdot formation balance and pressure-lag energy scaling without transport. NASA reconstruction independently checks energy; no independent kinetic trajectory is yet available. |
| C | Smooth periodic N2 thermal/advection field, chemistry off | Nonreacting pressure/density/kinetic attribution with actual laminar transport. This initial diagnostic is not called an inviscid exact solution. |
| C exact | Unforced smooth Euler entropy wave, constant Cp, zero viscosity/conduction; 32/64/128 cells | First-order spatial convergence of pressure baseline, finite energy defect, and an exactly conservative density-based reference with the same EOS, energy gauge, geometry and dt. |
| D | Smooth H2/N2 composition gradient, uniform T, no reaction | Integrated formation balance and closed transport; unity diffusivity only. This does not validate local enthalpy diffusion or differential diffusion. |
| E | Controlled reaction–diffusion chemistry | Not executed; no detailed-chemistry result substitutes for it. |
| F | Initialization-corrected actionStudy moving hydrogen kernel | Reproduction, dt/pressure/outer/tolerance sweeps, closed per-step budget and serial/MPI/restart/native-balanced equivalence. |
| G | Resolved literature-backed reacting flow | Not executed; the coarse kernel cannot validate a resolved flame. |

The exact entropy wave is `rho=rhobar(1+a sin(2 pi(x-Ut)/L))`,
`p=p0`, `U=U0`, `T=p0/(R rho)` and constant N2 composition, with a=0.05.
For inviscid constant-Cp perfect-gas Euler equations this is an exact smooth
solution: mass and rhoE are transported at U0, momentum has constant p,
and no species/chemical terms are active. It is an unforced exact subset,
not a general forced MMS of all reacting equations.

rhoCentralFoam evolves rho, rhoU and rhoE with Kurganov fluxes. Its constant
Cv= Cp-R and Eref=-R Tstd match the pressure solver's internal-energy gauge
`Cp(T-Tstd)-RT`. Mesh, EOS, zero transport and dt match. Both use first-order
upwind reconstruction, but their numerical fluxes differ; errors are judged
against the analytic solution individually. Conservation comparisons are
valid, whereas their field difference is not labelled pure coupling error.

For these smooth waves pressure-baseline total field error at fixed grid has
a spatial floor. The spatial order is measured at fixed sufficiently small
dt across three grids. Fixed-grid total errors are not misreported as formal
temporal order. Energy-defect slopes and field self-convergence are different
quantities; no formal reacting accuracy claim is made.

Cantera was not installed in either inspected Python runtime. An independent
0D chemistry trajectory must also match CHEMKIN kinetics, atomic weights,
gas constant and energy gauge. A mismatched off-the-shelf mechanism cannot
serve as an error reference. No dependencies were installed for this audit.
