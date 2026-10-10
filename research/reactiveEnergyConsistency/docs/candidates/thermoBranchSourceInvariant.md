# Cv source invariant at the legacy NASA branch switch

2026-10-06. Hypothesis before the diagnostic: some spatial Cv source calls
fail the previously declared 1e-10 relative energy-invariant threshold although
the continuous source identity and homogeneous 1100 K case pass. Preserve this
failure; do not replace the threshold with the observed maximum.

For Ea(T,c)=sum_s c_s e_a,s(T), the Cv thermal RHS proves dEa/dt=0 only
on a differentiable thermodynamic branch. JANAF/NASA switches low/high
polynomials at Tmid. If their molar enthalpy values differ, the selected
perfect-gas internal energy has the same jump (the R*T term is continuous):

    jump(Ea) = sum_s c_s [h_high,s(Tmid)-h_low,s(Tmid)].

The smooth-branch RHS omits this distributional term. Reducing an ODE local
truncation tolerance need not remove a data-induced branch jump. This is a
falsifiable explanation, not yet the established cause of the spatial failure.

First audit unchanged legacy NASA coefficients independently. Classify each
recorded native source call by whether its initial/final temperature straddles
a thermo midpoint. Compare failure counts, maxima and crossing locations;
retain noncrossing failures and counterevidence. The source trace has no
concentration vector at the crossing, so coincidence alone cannot prove that
its full energy discrepancy equals the weighted branch jump. A native direct
source control and tolerance contrast would be needed for that stronger claim.
Do not alter the accepted thermo data, current libcvChemistry or old raw cases.

The endpoint audit finds all straddling calls fail the declared source-energy
gate: 144/184/240 calls for baseline dt2/dt1 us and G dt1 us, respectively.
G dt2 us has no crossings and maximum 9.78e-15 relative source discrepancy.
Baseline cases also retain 7/8 non-straddling failures, so the complete error
is not assigned solely to branch jumps. Legacy H2/O2/H2O enthalpy jumps are
1.25477/0.224023/0.812155 J/kg; N2 has -0.0158889 J/kg. Worst straddling
native calls change energy by about 0.04–0.05 J/m3 against 1e5 J/m3 inventory.

Before the stronger control, select a separate direct native ODESystem probe,
with no CFD transport/projection. Initial temperatures 999/1001/1100 K,
p=101325 Pa, Y_H2=.0283, Y_O2=.225, Y_H=Y_OH=.0001 and remaining N2=.7465;
all other species zero. TF=10 us. Use rtol1e-8/1e-10/1e-12, atol1e-16,
native Rosenbrock34 and the unchanged corrected Cv library. Compare one source
interval with 1000 equal diagnostic intervals. Record concentrations before/
after each accepted interval; interpolate concentrations at a detected 1000 K
crossing to estimate the weighted jump. Compare net energy change with the
signed accumulated jump and independent polynomial values. The interpolation
is a diagnostic approximation, not an event-exact proof. Preserve contradictory
results. Continuous-branch controls start above 1000 K. No repaired mechanism
or modified source integrator is introduced in this audit.

The direct native probe crosses at T0=999 K and retains approximately
1.14605e-7 relative source energy change at every tested tolerance. Above-branch
controls stay below 1.5e-13. With 1000 diagnostic intervals, the weighted
branch-jump estimate leaves at most 6.04e-13 relative unexplained energy;
at rtol1e-10/1e-12 that remainder is below 1.7e-14. Native molar jumps agree
with independent NASA coefficients within 5.72e-8 J/kmol. This isolates the
branch discontinuity in these direct controls, while retaining the spatial
non-straddling failures and their unresolved numerical contribution.

Before generalizing to other implementations, replay the identical three
initial states and TF in independent Cantera IdealGasReactor, clone=False,
unchanged legacy-matched mechanism and verified molecular weights/density,
rtol1e-8/1e-10/1e-12 with atol1e-16. Record energy drift and native endpoint
differences. A crossing discrepancy in both integrators supports a data/RHS
compatibility limitation rather than an OpenFOAM-only defect; no such result
is assumed before execution. Above-midpoint controls remain separate.

[Cantera's NasaPoly2 validation source](https://www.cantera.org/3.2/cxx/d6/de1/NasaPoly2_8cpp_source.html)
explicitly checks low/high Cp, enthalpy and entropy continuity at the midpoint.
Its warning thresholds do not enforce exact continuity. Thus detecting or
repairing polynomial discontinuities is established validation practice;
this audit cannot establish a new numerical-method claim.
