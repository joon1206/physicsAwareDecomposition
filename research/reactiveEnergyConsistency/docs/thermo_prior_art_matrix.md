# Thermochemistry and invariant-method prior art

No broad novelty claim survives the comparisons below. Sources were inspected
at the indicated methods/equations; abstract-only SCI access remains an open
limitation. Continuity controls are sensitivity baselines, not physically
validated replacement databases.

| Primary source | Inspected equations or implementation | Comparison and decision |
|---|---|---|
| [NASA Glenn, McBride et al. 2002](https://ntrs.nasa.gov/api/citations/20020085330/downloads/20020085330.pdf), p.3 | Cp polynomial integration gives H/S; PAC fits impose reference and common-point functional constraints. | Constrained thermodynamic fitting and preserving reference states are established. Reject generic fitting novelty. |
| [RMG Wilhoit conversion source](https://raw.githubusercontent.com/ReactionMechanismGenerator/RMG-Py/main/rmgpy/thermo/wilhoit.pyx), to_nasa lines485–585 and KKT assembly | Weighted least squares with selectable Cp derivative matching; high enthalpy/entropy integration constants match low at Tint; low matches reference. | Our a6+=−Delta h/R and a7+=−Delta s/R are the same algebraic continuity operation. HS control is prior art. |
| [Cantera 3.2 NasaPoly2 validation](https://www.cantera.org/3.2/cxx/d6/de1/NasaPoly2_8cpp_source.html), validate | Evaluates left/right Cp/R,h/RT,s/R and warns at declared relative thresholds. | Validation does not enforce exact continuity; jumps below warning thresholds can exceed a stricter source invariant criterion. A linter alone is not new science. |
| [Boettcher Caltech thesis, Appendix H](https://thesis.caltech.edu/7037/6/Boettcher_P_A_App_A_to_H.pdf), H.1–H.9, pp.201–205 | Linear constrained fit to existing coefficient-generated Cp,h,s samples, fixed reference enthalpy/entropy, endpoint constraints, Cp/Cp' and h/s matching. | Covers continuity reconstruction from old fits. This does not supply experimental source accuracy when original data are absent. Reject generic constrained-refit novelty. |
| [Killingsworth et al. 2020, Mech Checker](https://combustiontools.llnl.gov/static/MechCheck_CandF_2020_08_02.pdf), sec2.1–2.3 | Eqs1–3 NASA functions; constrained lower Cp refit matches Cp at reference and high Cp/Cp' at switch; a6/a7 restore reference and common-point h/s. | Already automates repair and demonstrates solver cost/convergence consequences in reactors and pressure-coupled multiple zones. Reject generic repair, mechanism certification and predicting numerical consequences as a new headline. |
| [SUNDIALS CVODE mathematical considerations](https://sundials.readthedocs.io/en/latest/cvode/Mathematics_link.html), eq3.11–3.12 | min WRMS distance subject to g(y)=0; Newton least-norm increments with G delta y=−g; projection enters error test/history. | The proposed full weighted elemental/mass/energy manifold projection is a direct instance. A final scalar T recovery is a constrained specialization, not a new conservation principle. |
| [Cantera CV reactor](https://cantera.org/3.2/reference/reactors/ideal-gas-reactor.html), eq3–4; [CP reactor](https://cantera.org/3.2/reference/reactors/ideal-gas-constant-pressure-reactor.html), eq2–3 | m Cv T'=−sum u_i production for closed fixed volume; m Cp T'=−sum h_i production at constant pressure. | Source-invariant absolute E/H state integration is established. Physical CP expansion differs from installed fixed-p concentration abstraction. |
| [PelePhysics reactor coupling](https://pelephysics.readthedocs.io/en/latest/CvodeInPP.html), CV/CVH sections | Integrates rhoY and absolute energy/enthalpy with transport forcing; thermal RHS contains the corresponding species absolute-energy contraction. | Chemistry/CFD consistency layer and invariant-carrying source maps predate an OpenFOAM interface rewrite. Generic architecture is not novel. |
| Installed v2012 StandardChemistryModel.C lines547–581,692–761 | solve returns RR_i=(c_i^new−c_i^old)W_i/dt; Qdot=−sum Hc_i RR_i. | Finite-update formation transfer is already exact algebraically. Transport/density replacement after consuming it remains a distinct defect. Reject merely substituting finite RR as a new method. |
| reactingFoam-SCI, Yang et al.2019; pinned author CTreactingFoam source in related_work.md | SCI full method remains inaccessible; CT source explicitly includes species sensible diffusion and conventional energy-before-pressure sequence. | Do not use this incomplete access to infer novelty; generic source maps already fail against the independent sources above. |

For a risk estimate, the exact signed event contribution is
sum_crossings sum_i c_i(Tc) Delta H_i [J/m3]. A positive bound can sum
absolute contributions. Replacing crossing concentrations by guessed activity
is an approximation whose predictive error needs separate validation.
Neither an observed correlation nor the elementary jump identity establishes
a new numerical method. The new controls test invariant drift rather than
claiming the runtime benefits already demonstrated by Mech Checker.

The HS and CpHS algebraic controls preserve low coefficients, reference H/S and
kinetic input text. CpHS changes high Cp by a small constant; it is not a
constrained fit to original molecular/tabulated data. No accuracy superiority
of either replacement data set is claimed. NASA7 representation, Cp positivity,
EOS compatibility and chemical kinetics correctness are different gates.
