# Claim strength — active candidate investigation

The scope is the tested v2012 perfect-gas/JANAF Euler finite-volume algorithms,
closed periodic domains and documented transport models. References and source
versions are recorded per experiment. A self-refinement comparison is not an
independent exact error.

| Claim | Strength | Evidence / limit |
|---|---|---|
| Baseline eight-term global budget closes | VERIFIED_NUMERICALLY | Accepted audit: maximum step residual approximately 1.45e-16 J |
| Cellwise budget sums to the observed inventory change | VERIFIED_NUMERICALLY | Executed candidate ledgers and independent NASA inventory; frozen baseline preserved |
| Separate pressure/K terms leave the thermochemical density mismatch V delta rho (hs+hc) | PROVEN_ANALYTICALLY | Exact substitution in the selected Euler inventory and implemented equation sequence |
| A nonzero hs correction at fixed final rho,p,Y cannot retain the selected EOS | PROVEN_ANALYTICALLY | Perfect-gas EOS fixes T and its selected thermodynamic branch/value |
| An elemental energy-reference shift changes the full inventory defect only through elemental-mass defects | PROVEN_ANALYTICALLY | Linear combination of elemental inventories; requires balanced chemistry and full species terms |
| Formation-density mismatch alone is a reference-invariant causal indicator | UNSUPPORTED | Its compensation with species balance must be retained |
| A local Cv projection cancels the isolated density pair | PROVEN_ANALYTICALLY | Conditional on an admissible target; also changes pressure |
| That local projection is an acceptable reacting CFD correction | UNSUPPORTED | F +26.61%, Mix -25.52%, up to 930 m/s pressure/momentum mismatch and gauge-target failure |
| Scalar density correction improves the accuracy/cost frontier | UNSUPPORTED | Retained reacting capacity/ODE failures; worsened Mix |
| The selected baseline Mix violates elemental transport balance | VERIFIED_NUMERICALLY | +0.192225% H and -0.020579% N with conserved total mass |
| An energy-only update at fixed rho,Y repairs elemental transport | UNSUPPORTED | rhoY and its elemental inventories are unchanged by that update |
| Full compatible species/absolute-energy residual enforces tested closed-domain conservation | VERIFIED_NUMERICALLY | G and block A/B/Mix/F/Wave cases; roundoff energy, mass, elements and EOS within recorded tolerances |
| Full pressure/species/energy block reduces the final momentum inconsistency | VERIFIED_NUMERICALLY | Tight tolerance approximately 1e-5 m/s on F at 1 us; frozen predictor limits remain |
| Independent homogeneous reacting T convergence is first order | VERIFIED_NUMERICALLY | Corrected Cantera phase: dt .125/.0625/.03125 us gives baseline errors .0003023/.0001489/.00007382 K and G .0001032/.00005112/.00002539 K |
| Those algorithms are higher than first order | UNSUPPORTED | Measured homogeneous and analytic transport orders are approximately one |
| Analytic reacting entropy-wave temperature/species convergence is first order | VERIFIED_NUMERICALLY | Three meshes, same idealized chemistry/EOS; baseline, G and block all pass |
| Near-zero energy residual guarantees small solution error | UNSUPPORTED | Exact reacting entropy wave has finite T/species error under a conservative algorithm; no detailed-flame reference is needed for this counterexample |
| Conservative reacting trajectories are robust to coarse dt/mesh | UNSUPPORTED | Pressure candidates quench at coarse dt; central reference quenches at coarse meshes and ignites at nx256 |
| Correct Cantera matching requires thermodynamic, kinetic and reactor-phase conventions | VERIFIED_NUMERICALLY | Legacy W/R/standard-pressure/Ea conventions; clone=True changed custom weights; clone=False asserts exact initial identity |
| Full block is cheaper than baseline at the tested configuration | UNSUPPORTED | Three rotated-order trials: median 20.278 s versus 14.577 s, ratio 1.391; collective operation count approximately 7.35x |
| G has a large measured runtime penalty | UNSUPPORTED | Median 15.277 s versus 14.577 s, ratio 1.048; small n and noise prohibit strong significance claims |
| Looser coupling tolerance trades cost for momentum residual | EMPIRICALLY_SUPPORTED | F/Mix tolerance screens; F max deltaU 5.455/.745/.0671 m/s; single-trial wall data |
| A fixed pressure tolerance is a guaranteed accuracy controller | UNSUPPORTED | No truncation/chemistry error bound; energy residual alone fails the analytic counterexample |
| Latest central primitive recovery reproduces conserved energy | VERIFIED_NUMERICALLY | nx512 full run: recovered inventory discrepancy 6.7e-16 J; relative energy drift approximately 3.6e-13; cancellation-aware root checks recorded |
| The current reacting central curve is a spatially resolved independent reference | UNSUPPORTED | nx256 versus nx512 T L1 is 26.25 K; cross-flux uncertainty is recorded in inviscid_cross_reference.json |
| HLLC resolves the equal-property analytic contact equilibrium | VERIFIED_NUMERICALLY | Wave/ReactingWave p and U errors near roundoff; first-order T/species errors; this does not cover general unequal-thermodynamic mixtures |
| HLLC eliminates detailed-chemistry spatial uncertainty | UNSUPPORTED | nx256 versus nx512 T L1 68.16 K; central/HLLC nx512 difference 111.04 K; conservative energy is insufficient |
| Common-weight conservative remapping generally preserves single-state mixture pressure | UNSUPPORTED | Nonlinear EOS/energy compatibility condition; NASA two-donor 50/50 example changes p by 1433.33 Pa |
| Formation-reference shifts cure that mixing discrepancy | UNSUPPORTED | Such shifts add a linear partial-density function and cancel from the mismatch; independent numerical gauge check |
| G/block preserve exact pressure equilibrium in unequal-NASA mixture transport | UNSUPPORTED | Independent nx32/64/128 wave: pressure Linf converges approximately first order but remains about 75 Pa at nx128 despite roundoff energy |
| Tested successful endpoints are thermodynamically admissible | VERIFIED_NUMERICALLY | 131 physical-kernel/mixture endpoints: positive T/p, species trace threshold, positive total entropy change; entropy_admissibility.json |
| Conservation repair supplies physical species enthalpy diffusion | UNSUPPORTED | Exact unequal-Cp Pr=.7 diffusion: G/block retain 1.4–1.57 K temperature error while conserving total energy |
| The declared compatible heat-flux control retains constant T/p in the exact diffusion test | VERIFIED_NUMERICALLY | 32/64/128 cells; T errors below 2e-11 K; flag-off/parent and Pr1 on/off endpoint fields coincide |
| Coupled coefficient evaluation matters to conservative heat-flux cancellation | VERIFIED_NUMERICALLY | First Mix MPI extra net +1.7817e-10 J matches energy leak; refreshed coefficient halos reduce net contribution to roundoff |
| More thermodynamic passes explain the measured nonzero-transport G partition discrepancy | UNSUPPORTED | Four instead of inherited two passes leave T Linf approximately 1.675e-5 K; proposed cause is not established |
| The corrected native source satisfies its autonomous ODE interface | VERIFIED_NUMERICALLY | 16 native probes: zero explicit time derivative, directional Jacobian discrepancy below 7.7e-8 and continuous invariant residual below 2.3e-16; superseded wrong-callback runs retained |
| CV chemistry plus G removes the resolved homogeneous source-path error in the tested case | VERIFIED_NUMERICALLY | Matched Jacobian/ODE tolerances: CV G T difference 1.1e-8 K or smaller over dt1/.5/.25/.125 us versus CPFD G 8.584e-4 K at dt1 us; CV agreement is inside measured Cantera tolerance contrast |
| CV chemistry alone supplies the full CFD conservation identity | UNSUPPORTED | Baseline+CV energy drift -8.79e-7 to -1.11e-7 relative and first-order endpoint T trend; source invariant does not replace pressure/species/energy closure |
| The homogeneous CV/G test establishes higher-order reacting CFD accuracy | UNSUPPORTED | Transport vanishes and endpoint ratios are below the independent-reference tolerance contrast; spatial reacting/time-splitting gates are separate |
| Corrected Cv source resolves the original coarse reacting failure | UNSUPPORTED | All eight matched F controls complete; CPFD/G and Cv/G both quench near 727 K at dt2 us and burn near 2845 K at dt1 us |
| The cold/high-pressure G failure proves an unattainable floating-point floor | UNSUPPORTED | Small residual and failed exact-cycle hypothesis do not prove impossibility; only failure within the original 20-update budget is established |
| Component allowance at the original cap completes the declared cold case without changing completing controls | VERIFIED_NUMERICALLY | Cold T difference 3.87e-12 K, energy drift -1.48e-15 relative; warm/hot/mixture/F on/off fields coincide |
| Component allowance certifies solution or truncation error | UNSUPPORTED | Rounding scale estimate only; independently computed inventory/reference gates remain required |
| Smooth macro Taylor compensation has second-order endpoint error in the exact source model | VERIFIED_NUMERICALLY | Three observed orders 2.098/2.047/2.023 under its smooth resolved-step assumptions |
| That bare correction is unconditionally positive for a stiff positive source | UNSUPPORTED | Analytic large-step argument and retained exact-map negative species counterexample |
| Common positivity scaling plus conservative energy guarantees better source accuracy | UNSUPPORTED | Predeclared weak-feedback/stiff case: positive limited T error 21.0463 K versus baseline 1.43018 K |
| Uniform elemental invariants eliminate dependent equations under a common linear transport operator | PROVEN_ANALYTICALLY | Reconstruction and residual identity in candidates/elementInvariantReduction.md, conditional on continuity/balanced source/initial and boundary assumptions |
| That reduction is equivalent in the declared periodic linear system | VERIFIED_NUMERICALLY | Full/reduced field difference 2.22e-16; variable-element and unequal-diffusion counterexamples retained |
| Elemental reconstruction generally improves the CFD accuracy/cost frontier | UNSUPPORTED | Known reduction, restricted preconditions; no native timing, positivity theorem or improvement of energy/pressure/time-splitting errors |
| Continuous Cv source identity guarantees accepted energy invariance across unchanged legacy NASA switches | UNSUPPORTED | Three spatial Cv configurations fail the original 1e-10 source gate; 568 straddling and 15 other failed calls retained |
| The branch jump explains the direct-source energy change in the declared crossing controls | VERIFIED_NUMERICALLY | 18 native controls and nine independent Cantera trajectories; crossing drift about 1.14605e-7 persists under tolerance tightening; fine weighted-jump remainder below 6.04e-13 |
| Every spatial source discrepancy has been attributed to a branch jump | UNSUPPORTED | Spatial traces lack crossing concentrations; 15 non-straddling baseline failures remain unresolved |
| Positive Cv on every branch guarantees a globally unique conservative temperature root | UNSUPPORTED | Actual-data gap/overlap examples with rational branchwise Cv bounds |
| The selected discontinuous data admits missing and multiple temperature targets | PROVEN_ANALYTICALLY | Strict gap/overlap and positive derivative bounds; numerical admissible H2/air and pure-N2 examples in thermo_branch_inversion.json |
| Energy/momentum/source defects together guarantee small transport error | UNSUPPORTED | Exact conservative contact-wave counterexample: all indicators vanish with T L1 9.23/4.78/2.44 K; an operator/truncation contribution is still required |
| Positive global endpoint entropy proves local entropy stability | UNSUPPORTED | No discrete local entropy inequality or intermediate-state proof; endpoint screen only |
| A genuinely new low-cost method has survived all publication gates | UNSUPPORTED | General conservative primitive, pressure/scalar coupling and block principles have equation-level prior art; reacting accuracy remains open |
| All possible future CFD contributions are exhausted | UNSUPPORTED | Finite candidate-class constraints do not prove universal impossibility; combined truncation/coupling estimators lie outside those constraints |

The corrected reference supersedes the earlier apparent 8e-4 K convergence
floor. Original failed reference conventions, source snapshots and raw results
remain available. Energy and accuracy claims must use the corrected reference.
