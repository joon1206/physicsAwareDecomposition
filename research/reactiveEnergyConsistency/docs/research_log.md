# Research log

## 2026-10-06 — continuation and preserved baseline

Hypothesis: the density/thermochemical projection mismatch can be corrected
only with an explicit thermodynamic state response. Reviewed accepted audit,
installed species source and mixture APIs, and preserved initial Git status.
Created branch codex/reactive-energy-candidates and froze accepted audit
files in baseline_audit_freeze.json; no prior artifact was edited.

Derived local density weighting ha=hs+hc, a cellwise species/source split and
the EOS constraints on a correction. A local fixed-rho projection must change
pressure; a scalar linearized corrector uses rho Cv/Cp rather than rho as its
thermodynamic transient coefficient. No numerical candidate result is yet asserted.

Targeted primary-source search found McDermott 2014, including its discrete
enthalpy product rule and explicit discussion of enthalpy-transporting solvers.
This rules out novelty of the broad product-rule correction principle. Exact
local/scalar constructions remain unverified for novelty.

Next experiments: compile read-only cellwise instrumentation, verify local
and rank-summed closure and unchanged final fields, execute formation-scale
and elemental-gauge controls, then screen the two derived correction families.
Each run records source/executable SHA256, dictionaries and configuration in
experiment.json; failures are retained under candidateStudy/data/raw.

## 2026-10-06 — cell ledger and thermochemical ablations

Read-only cell ledger source snapshot fbdb129d, executable hash in each run.
Hypothesis: the sum of independently measured local terms equals the global
inventory change. Observed maximum cell closure below 9.5e-19 J in the full
formation/timestep controls, with exact baseline F endpoint fields.

At dt=2 us physical F, net density contributions are +0.008887525315 J sensible
and -0.01213538802 J formation. Their sum -0.003247862704 J exceeds the net
loss -0.003042426341 J because pressure/kinetic and other terms compensate.
At dt=1,0.5,0.25 us the density pair is +0.0001670682,-0.0032191727,
-0.0044200041 J. This does not establish a smooth asymptotic temporal order.
Absolute space/time sums are in ablation_analysis.json.

An H-element gauge of 1e7 J/kg_H changes F absolute loss by only 8.09e-10 J
and T Linf by 2.17e-5 K (NASA representation/trajectory sensitivity), while
the relative denominator nearly doubles. The isolated absolute local density
norm changes, illustrating reference dependence. Formation-scale 0 B/F fail
the chemistry ODE; scale 0.5 changes the physical thermochemistry and does not
validate an invariant numerical causality claim.

Nonreacting Mix fields remain equal across offsets to T Linf<2.3e-12 K.
Its energy drift persists at zero Hc. Its H and N element masses drift by
+0.192225% and -0.020579% despite conserved total mass. The small absolute
energy differences between offsets agree with the changed species inventory.
This exposes a compatible species/density transport problem beyond energy alone.
Next: screen derived nonlinear and scalar corrections, then shared-flux species.

## 2026-10-06 — first correction screens and rejection

Source snapshot d7a1d1b1; exact executable hashes and dictionaries per run.
A localInternal and C scalarDensity have distinct derivations in docs/candidates.
Both preserve the static A control and leave homogeneous B drift at roughly
-1.624e-6. A changes full F energy drift from -17.3887% to +26.6068%; at dt/2
it is +56.4175%. Its induced momentum-corrector change reaches 930 m/s on
the coarse F test. Cell ledger still closes below 9.3e-19 J. Cancelling the
density pair is insufficient: pressure/transport response causes a new defect.

C reaches a nonpositive thermochemical correction capacity after severely
distorted temperatures at t=168 us (coarse F). Its dt/2 and gauge controls
also fail, with all logs retained. A gauge control reaches an unattainable
energy target inside the declared 200–5000 K thermodynamic interval. Both
methods worsen Mix drift to -25.52% and -13.18%. Decision: REJECT the tested
energy-only formulations for the reacting/general variable-composition target.

Two/four pressure correctors yield +1.3441%/+3.0903% F drift with measured
walls 8.13/8.68 s versus 8.25 s baseline. These single trials are cost screens,
not repeated performance claims. Two outer correctors fail coarse F; at
dt=0.25 us they reproduce +60.1277% drift and take 80.19 s.

A minor EOS refresh tolerance issue is being repaired in an explicitly tagged
EOS2 rerun; it cannot erase the measured pressure-gradient/gauge failure.
Next candidate derives final-flux conservative species balances without
clipping or normalization. It is a diagnostic precursor to compatible coupling,
not a new generic conservative transport claim.

## 2026-10-06 — compatible transport and pressure block

SpeciesFlux removes Mix elemental drift to about 1e-15 and enforces EOS to
about 2e-16; reacting energy drift worsens to +58.26%/+34.30% at 2/1 us.
REJECT species-only correction as an energy solution; retain its shared-flux
balances as part of the derived next method. EOS2 fixes the energy-only
prototype's EOS refresh to roundoff while leaving its +26.61% drift and
930 m/s momentum mismatch: rejection does not depend on the earlier EOS tolerance.

ConservativeState adds a nonlinear full absolute-energy residual using final
rho,phi and corrected species, rather than cancelling an isolated density term.
A/B/Mix/F screens conserve energy to roughly 1e-13 relative or better;
mass/elements/EOS pass. Wave T L1 at nx32/64/128 is 0.590951/0.297848/0.149692 K,
close to baseline 0.590397/0.297133/0.149312 K, with energy roundoff.
The coarse 2 us reacting run quenches to mean T=726.81 K, while the 1 us run
burns to 2844.69 K. The perfectly conservative coarse trajectory is unacceptable
for a blanket robustness/accuracy claim. Coarse MorePressure does not cure it.
At 0.125 us the conservative mean T is 2840.70 K; field self-differences are
nonmonotonic and are not an independent reference. Decision: restrict/pursue
convergence; no publication promotion.

BlockConservative uses a separate executable and derived frozen-source block
Gauss-Seidel pressure/species/energy loop. It passes rapid conservation/EOS gates
and reduces the final pressure/momentum mismatch to about 1e-5 m/s, but retains
coarse quenching. At 1 us wall time is 20.32 s versus 11.56 s for ConservativeState
and 10.65 s baseline (single screening trials); field mean T is 2844.85 K.
No cost advantage or new generic block-coupling principle is claimed.

Independent Cantera 3.2 conversion contains the same 10 species/27 reactions.
Explicit legacy atomic weights remove molecular-weight differences. The first
reference used Cantera's default 1 atm thermodynamic standard pressure; v2012
uses 1 bar. Matching that convention removes a false ~1.255 K endpoint floor.
Raw 1-atm and 1-bar reference data are retained in separate directories.
Further conversion matches initial density, Arrhenius Ea/Rcal (v2012 uses
RRcal=1.987316) and Kc reference-pressure/R. Eight independent instantaneous
rate fixtures agree within normalized net-rate error 1.3e-14 away from near
equilibrium and 6.3e-11 in the cancellation-dominated near-equilibrium fixture.
A remaining ~8e-4 K endpoint limit is being audited before formal order claims.
The one-column homogeneous runs duplicate full-mesh endpoints to <4e-10 K
while cheaply extending dt refinement to 0.03125 us.

Every candidate retains exact source snapshots, executable hashes, fields,
dictionaries and failed logs. Eight executed-evidence regression checks pass,
including all 499 published artifact hashes and the accepted audit freeze.
Next: reference thermodynamic-property audit, finer reacting block/G coupling,
resolved transport validation, novelty-specific comparisons and communication/cost.

## 2026-10-06 — independent phase identity, convergence and strong cost controls

Hypothesis: the homogeneous endpoint floor was a reference-convention issue,
not yet evidence against first-order solver convergence. A read-only reactor
identity audit showed that Cantera 3.2 clone=True changed the custom legacy
atomic weights (max molecular-weight difference approximately 0.002 kg/kmol).
Using the separately constructed input phase with clone=False removes that
change, with explicit initial pressure and molecular-weight assertions.
Expected result: reference-consistent refinement rather than a false floor.
Observed reference at 240 us is 2928.259905383 K; tolerance-refined reference
energy drift is approximately 1.05e-11. Baseline endpoint errors at dt
.125/.0625/.03125 us are .000302254/.000148877/.000073816 K; G gives
.000103186/.000051115/.000025386 K. Both are first order. Earlier references
and native tight-tolerance integration failures remain retained. Source/version
and kinetic/thermodynamic conventions are in independent_reference_matching.md
and each reference_summary.json. Decision: reference validation passes for 0D;
no higher-order claim. Next: transport/space reference independent of G.

Hypothesis: tighter pressure-block iteration than the Euler discretization
requires may be wasteful. Exact source snapshots 1c36d4860d10e980c74a32e02b6479cdca7541db71be50645e923dbf9ccd7efd
(candidate) and a7b60dbabdbcc6c97040514b3f75a9f414875e8809bd1b7e8964451f3e6a97c8
(block), plus complete executable SHA256, are recorded in every experiment.
Configuration: F at 1 us and Mix at 2 us, block pressure tolerance 1e-2/1e-3/1e-4,
constant final-flux conservative species/energy solves. Expected: lower cost
with increasing momentum residual. F maximum deltaU is 5.455/.745/.0671 m/s,
with roundoff energy and close burned temperature means. Single-trial walls
14.434/14.292/15.399 s cannot establish a statistical advantage. Decision:
IMPLEMENTATION_ONLY tolerance tradeoff; no guaranteed accuracy controller.

Three sequential rotated-order, four-rank F timing trials use every=0 equal
cell-ledger settings, without another CFD campaign. Median seconds: baseline
1 us 14.577, G 15.277, tight block 20.278, MorePressure 13.344, baseline
.5 us 20.487, baseline .25 us 32.423, MoreOuter .25 us 92.025. Small n and
ordinary host noise limit claims. Against the block .125 us self reference,
T L1 differences are 4.629/8.435/9.623 K for baseline/G/block; those are
numerical-trajectory differences, not exact solution errors. Separate
instrumented initial runs overlapped the homogeneous tolerance campaign, so
only their operation counts are used: G collectives approximately 1.81x and
block approximately 7.35x baseline. The CSV energy-solves aggregation was
corrected to include the actual deltaConservativeH field; original detailed
log counts were already retained. Decision: no established favorable
accuracy/cost frontier. Next: same-dt MoreOuter comparator and loose-block counts.

Hypothesis: energy residual cannot by itself bound reacting transport error.
Derived equal-property nitrogen-isomer A->B reacting entropy wave, k=5e4/s,
zero diffusion and heat, common Hf=2e6 J/kg. Exact T/rho/U and exponential
species profiles specify a rigorous control without choosing a hydrogen
trajectory. Eighteen executed mesh/time screens at 32/64/128 cells and three
timesteps show approximately first-order T and species errors for baseline/G/
block. G and block energy is roundoff despite finite analytic error. Decision:
energy-only accuracy-controller hypothesis falsified; analytic reacting
transport convergence verified. Synthetic isomers are not a detailed flame.
Next: independently conservative detailed-chemistry spatial refinement.

## 2026-10-06 — independent conservative reference and retained failure

Hypothesis: an independent rho/rhoU/rhoY/rhoEa central flux provides a reacting
reference after adequate mesh/time refinement. Derivation precedes code in
central_reference_derivation.md. Native v2012 central flux sources are copied
with hashes, all species share continuity flux weights, chemistry is native
ODE, and absolute energy has no duplicate chemical heat. Transport As=0;
periodic one-dimensional counterparts therefore use the same inviscid PDE.

Initial sensibleInternalEnergy registration failures were retained. A local
Cv inversion into registered sensible h made the reference executable. Seeding
native temperature inversion with that verified root removed an approximately
1e-10 relative primitive-versus-conserved energy mismatch. hRecovery2 source
snapshot 90dd669a6b6baaf8000d6b9c95a7e00ae7b57e714b3dc14e9ccdabd4d25d665a,
executable 02a124c6d94151580076351c4d9253b39702942a2ff46f37e8eaf6f0fb9fc86a.

Observed: coarse central nx32/64/128 quench, including a halved-dt nx128
control. nx256 ignites to mean T=2844.4297 K. hRecovery2 nx256 maximum local
energy balance is 7.05e-20 J and primitive/conserved inventory mismatch
6.07e-16 J; mass/element/energy accumulated relative errors approximately
4e-13. This establishes a spatial ignition threshold, not a resolved curve.
The nx512 hRecovery2 run fails local inversion at approximately 224.43 us;
its abbreviated old fatal message cannot distinguish root roundoff from a
physical target problem. Failure is retained. A cancellation-aware backward
error scale and expanded fatal diagnostics are derived before hRecovery3.
Expected: roundoff-limited root convergence with independently verified
primitive energy. Decision: reference unresolved; build/retest, not promotion.

Inviscid pressure counterparts nx32 dt .125 us burn with G/block mean
2840.70/2845.01 K while conserving energy. Their first walls overlap reference
work and are not uncontended cost data. Independent fields must be compared
through conservative aligned-cell restriction, retaining initial-profile
sampling and central-reference uncertainty. Next: nx64/128 pressure
refinement and hRecovery3 nx512, followed by conservative field comparison.

## 2026-10-06 — same-dt baseline, coarse negative and repaired fine reference

Expected: the missing same-dt MoreOuter baseline determines whether the
conservative block merely mimics an existing cheap outer iteration. Observed
three sequential appended F 1 us trials: 49.211/51.883/44.072 s, median
49.211 s (3.376x the earlier baseline median; not a paired rotated-block
estimate). State mean T=3040.17 K, energy drift +239.118%, H elemental drift
+2.50196%. Local ledger still closes. The altered algorithm now has dominant
pressure term +0.0329564 J and species residual +0.0089990 J; its density pair
is only -9.7784e-6 J. Baseline dominance is not asserted for this changed
algorithm. Source/executable match the existing candidate snapshot; exact
case names and dictionaries are in benchmark_matrix.json. Decision: REJECT
this prescribed two-outer variant as a conservation/accuracy remedy, while
retaining it as an executed cost comparator. This does not prove that every
possible fully converged PIMPLE configuration fails.

Expected: loosening pressure convergence cannot remove the coarse chemical/
transport error. F block at 2 us, tolerance 1e-4, still quenches to 723.330 K
and conserves energy. At 1 us the same tolerance differs from the tight block
by only 0.02252 K T L1, max momentum mismatch 0.06708 m/s. Separate sequential
instrumentation gives 684,108 collectives versus tight 1,479,168 and baseline
201,228; operation counts are used, wall excluded from paired comparison.
Decision: useful inexact-iteration implementation point, not a new method or
accuracy-controller proof. Next: independent resolved accuracy.

The cancellation-aware hRecovery3 nx512 reference completed at 240 us.
Source snapshot 450d0bad20c365f7d7311b8c004c7cde48002f2025e26f650e05decefd012dbb,
executable 2bbc6330600d54aa2d8c4f05e816065673a011798a695113c16025978d612ff6.
Mean T=2842.7212 K, independent energy drift -3.58e-13 relative, max local
balance 3.79e-20 J, max reconstructed/conserved discrepancy 6.63e-16 J.
199,575 accepted local roots did not meet the old net-energy-scaled criterion
at their stopping point; the new max residual is 1.90e-7 J/kg against component
scale tolerance up to 1.93e-7 J/kg. Successful physical inventory agreement is
consistent with cancellation-limited inversion. It is not direct replay of
the exact failed old root because that older fatal log did not save the state.

Conservative restriction nx512->256 gives 26.246 K T L1 and 4.854 m/s U L1.
The reference therefore remains spatially uncertain, despite close global
means. InvF block nx32/64/128 T differences from nx512 are
43.306/27.131/19.365 K; G 70.928/27.046/35.646 K; baseline
59.752/37.841/31.567 K. These are numerical-trajectory differences, not exact
errors or established orders. Next: known HLLC contact-resolving flux to
isolate the central reference's acoustic diffusion before larger brute-force
refinement. Derivation in hllc_reference_derivation.md precedes code.
# 2026-10-06 continuation: HLLC and unequal-thermodynamic compatibility

The contact-resolving reference was derived before implementation in
hllc_reference_derivation.md. It uses the known HLLC star-state flux and the
central reference's verified cancellation-aware Cv recovery. This is a
separate validation implementation, not a novel method. Source/executable
hashes and exact input dictionaries are retained per HLLC case. Wave and
synthetic reacting-wave nx32/64/128 tests preserve p/U near roundoff and
converge approximately first order in T/species. Homogeneous B agrees with
the corrected independent chemistry reference within the recorded time errors.

Hypothesis: removing central acoustic contact diffusion would resolve its
coarse-grid quenching uncertainty. HLLC nx32/64/128/256/512 all burn, supporting
the diffusion sensitivity, but not a resolved accuracy reference. The nx512
run completed: mean T 2772.882935 K; relative energy drift -1.76679e-13 and
max local energy residual 5.47962e-20 J. Its T L1 difference from nx256 is
68.16213 K, and from central nx512 is 111.03735 K. Spatial uncertainty grew
over this interval rather than demonstrating asymptotic convergence. No
reacting-order or exact-field-error claim follows. Both conserved reference
families and all pressure trajectories remain in inviscid_cross_reference.json.

Next control, selected before execution: halve dt at HLLC nx256 to separate
time/source splitting sensitivity from the mesh difference; the existing
nx128 time control is insufficient to assume time independence at finer meshes.

A further compatible transport/state-transfer pivot was derived in
candidates/mixturePressureCompatibility.md before its implementation. Fixed
common-weight conservative remapping generally changes the one-state NASA EOS
pressure because the fixed-pressure internal-energy map is nonlinear. An
elemental formation-reference shift is linear in partial densities and cancels
from this mismatch. The independent two-donor NASA check gives +1433.33 Pa
in the 50/50 example with energy conserved; enforcing p0 instead changes
internal energy by 3826.387 J/m3. This conditional obstruction does not exclude
all equilibrium-preserving fluxes or enriched representations.

The nx32 exact unequal-thermodynamic contact-wave pilot completed for all five
existing algorithms. T L1 / pressure Linf: baseline 3.2084 K / 293.55 Pa;
G 3.2112 K / 291.66 Pa; block 3.1929 K / 295.60 Pa; central 50.8142 K /
156.66 Pa; HLLC 3.2968 K / 12.07 Pa. Conservative variants have energy within
recorded roundoff/tolerance while finite pressure error remains. Interpretation:
equal-property contact preservation cannot be generalized to real mixtures;
conservation alone has not supplied a pressure-equilibrium method. Refinement
at nx64/128 is executing under the same predeclared analytic test.

The post-result novelty audit additionally verified van der Heul et al. 2002
energy-derived pressure correction, Frias et al. 2025 integral reacting-flow
auditing and Ching et al. 2025 thermodynamic pressure compatibility/residual
correction. Their exact scopes and equation-level comparisons are recorded in
targeted_prior_art_comparison.md. Generic energy-pressure, integral-audit and
equilibrium-correction claims are not promoted as novel.

# 2026-10-06 continuation: compatibility, transport and chemistry pivots

HLLC nx256 dt15.625->7.8125 ns completes. T L1 difference is 1.99894 K,
U L1 5.71120 m/s; mean T at the finer dt is 2832.640179 K, relative energy
drift -8.2966e-13. It remains much smaller than the measured mesh/cross-flux
differences but is not an upper bound on every temporal error. Decision:
retain the numerical reference with quantified uncertainty, no resolved-field
accuracy claim. Source/executable remain the HLLC snapshot recorded above.

All 15 unequal-NASA mixture wave runs finish. Baseline/G/block/HLLC T and H2
errors converge approximately first order over nx32/64/128; central T orders
are about .82/.91. At nx128 G/block pressure Linf remain about 75 Pa despite
roundoff conserved energy; HLLC gives about 3.10 Pa. The common-weight mixing
obstruction and exact wave are complementary evidence. Decision: reject
general pressure-equilibrium claims for these formulations. These are
verification/compatibility diagnostics, not a new pressure-preserving method.

The original F/B/Mix factory is discovered to use Sutherland As=0, Ts=0:
the original benchmark has zero physical transport. Editable candidate reports
and reference scope are corrected; accepted historical audit files are frozen.
Separate tagged shared-Sutherland As=1.458e-6/Ts=110.4 K screens explicitly
change the numerical transport model and are not physical H2 validation.

Hypothesis derived before code in candidates/speciesSensibleDiffusion.md:
v2012 species diffusion uses mu, whereas sensible-enthalpy conduction uses
alpha=mu/Pr. The known physical sensible species heat flux supplies the
missing (alpha-mu) sum Hs gradY term. A separate transport executable copies
the G residual and includes this lagged flux in both EEqn and local ledger.
No original candidate/accepted source is changed.

Exact unequal-Cp diffusion waves at Pr=.7/1, nx32/64/128 produce 66 retained
raw runs (18 parent, 24 initial transport, 24 halo-synced transport). The
current report selects 42 parent/synced records. Pr=.7 parent/G/block T L1
has a nonvanishing 1.4–1.57 K floor despite conserved energy. Compatible
heat-flux T Linf is below 2e-11 K; species convergence remains approximately
first order. All 18 parent/flag-off or Pr1 on/off endpoint comparisons are
exactly identical. Decision: verified known-physics control, IMPLEMENTATION_ONLY.
Pr1 maximum tiny absolute flux contribution 7.9e-22 J is coefficient roundoff,
below the declared 1e-20 J vanishing-term floor; flag-off is exactly zero.

Broader controls: 16 original-zero-transport on/off cases have identical
endpoint fields. The first 12 nonzero-Sutherland screens catch a Mix G MPI
energy leak +1.7816976e-10 J, matching the added flux's domain contribution
+1.7816983e-10 J, although local closure is below 1.6e-19 J. Source snapshot
e1eed03aad2142f12f9f1499ed6ebe16fa5fe8593df075b31dc293f63f052133,
executable 3c574a656df6f8f85a2bc3e38f36594c68af45b94b03e46ab40fc7e578cae06b.
This technical completion is retained as a scientific conservation failure.

Repair derived before code: refresh derived coefficient/enthalpy coupled
boundary values before interpolation, so paired faces evaluate the same
coefficient. Sixteen tagged synced F/Mix controls complete with extra net
flux at roundoff; G energy/EOS/element conservation passes. Synced source
8b900d78dd1eab35a4bf24d81839b36f42cb961edcea926c73bd44c75587367e,
executable 2f335a5f8c318449ca2d8ff99cd4c98841ab0864a407a9030573b4503b759c42.
Original density-pair loss is not algebraically cancelled by a periodic
heat flux. No efficiency or resolved reacting-accuracy claim is promoted.

Serial/four-rank Mix G T Linf difference is 1.67524e-5 K with heat flux and
1.67149e-5 K without it. The initial thermo2 tag duplicates the factory's
existing two passes; it supplies no additional-inversion evidence. Actual
thermo4 adds two passes in eight further cases and leaves those differences
essentially unchanged. Hypothesis rejected against the predeclared 1e-6 K
threshold; cause is not established. All duplicate/failing comparisons are
retained. Strict partition field equivalence remains an open gate.

Next evidence-driven pivot: homogeneous reacting G has first-order error
against matched Cantera despite roundoff final energy. Native installed
StandardChemistryModel uses a Cp/Ha constant-pressure thermal path. Derivation
in candidates/isochoricChemistry.md selects the known Cv/Ea closed-volume
limit, unchanged native reaction mechanism, separate cvOde runtime library
and full finite-difference Jacobian. Constant-pressure RHS is added to the
same adapter to isolate the path at identical Jacobian/ODE tolerances.

An ODE interface audit catches an implementation error before interpreting
the spatial screen: ODESystem/Rosenbrock34 requires the explicit partial
time derivative in jacobian's vector argument; the initial new adapter
returned the RHS. Ten homogeneous pilot/pathControl runs are retained as
superseded, and the first F run is intentionally interrupted with a retained
failure explanation. Small endpoint errors alone did not catch this bug.

Corrected chemistry source snapshot
2526e97b2bdeec4bdee79849fb3321a19f0fafaf7a782f1a4901f354c40cfe19,
library SHA256 1249dfe42b15ad52a3c3854dae77c70e1797a3d40aaa455d71903cae4d506aa9.
The separate native ODE probe evaluates both paths at 600–3000 K, 16 states:
explicit time derivative zero, directional Jacobian discrepancy <=7.69741e-8,
continuous mass/thermal/pressure identities pass the predeclared 1e-12 limit.
Corrected dfdt0 pilot G dt1 us: CV T difference 1.06575e-8 K (within Cantera's
2.49488e-8 K tolerance contrast), CPFD 8.58425e-4 K. Both globally conserve.
Interpretation: supports the selected homogeneous source-path mechanism,
not higher CFD order. CV source alone still leaves the baseline pressure/
energy mismatch. Refinement, ODE-tolerance contrast and matched CPFD/CV F
screen are the next tests; no pending result is presented as complete.

Post-result primary audit reads Cantera's Cv/internal-energy equations and
PelePhysics' CV/CVH equations and external-source coupling. Decision: path
selection and generic source forcing are established principles; this pivot
remains IMPLEMENTATION_ONLY. No method has passed the publication gates and
finite tested-class restrictions are not a universal exhaustion proof.

## 2026-10-06 — completed corrected source and stopping controls

Hypothesis: the verified Cv thermal path removes homogeneous source error and
may remove coarse F quenching. Exact chemistry source snapshot
2526e97b2bdeec4bdee79849fb3321a19f0fafaf7a782f1a4901f354c40cfe19,
library 1249dfe42b15ad52a3c3854dae77c70e1797a3d40aaa455d71903cae4d506aa9;
original G application/executable remain unchanged. All corrected eight Cv
homogeneous runs, one matched CPFD control and one tighter Cv tolerance run
complete. Cv/G T differences over dt1/.5/.25/.125 us are
1.06575e-8/7.40829e-9/6.14318e-9/4.11728e-9 K, inside reference contrast.
Cv without G remains first order and retains the CFD energy defect.

Eight matched four-rank full F controls complete at TF240 us, dt2/1 us,
CPFD/Cv, baseline/G, rtol1e-10/atol1e-16. Conservative dt2 us means
726.764740/727.822788 K; dt1 us means 2844.691087/2844.741557 K. Both conserve
final energy; both coarse paths quench. Baseline Cv energy drifts are
-23.1379325%/-1.9911425%. Decision: reject removal of coarse failure; known
source-path physics remains IMPLEMENTATION_ONLY. Wall times overlap separate
logical stopping replays and are excluded from comparative performance.

Broader controls: matched Cantera cold950 K/10 atm remains in induction at
950.00005869 K; hot1500 K/1 atm ends at 3003.21276986 K. Baseline/hot G
complete; original cold G fails its 20-update absolute Newton cutoff. Three
prederived separate stopping policies retain every version. Allowance-only
completes cold but unnecessarily loosens warm/hot residuals; exact full-state
period-one/two repetition fails to complete cold. Final cap fallback completes
cold with T difference 3.86535e-12 K and energy drift -1.47611e-15 relative.
All warm/hot/mixture/F formerly completing on/off fields coincide exactly.
Snapshot 9db32f14eb7577e7f647a37d01aecb0de7fa2a05fd61372b926a7c8cf284eeb2,
executable 5ae94e2ab5dbe1aaf0baac1c1581886cfa73762896dc71fd46d59034d87dea70.
Cold cumulative accepted-residual upper sum 2.05665e-14 J and component
allowance upper sum 3.88870e-12 J exceed its observed inventory change
3.60822e-16 J. Status: implementation robustness, no certified error bound.

## 2026-10-06 — low-cost pivot falsifications

Derive macro Taylor thermal-path compensation before coding an exact source
map. Smooth orders improve to 2.0976/2.0470/2.0230; the stiff positive-source
counterexample gives negative Y_A=-4.2857143. The separately predeclared common
positivity limiter gives positive output but T error 21.0463 K versus baseline
1.43018 K, a 14.7158 ratio. Mass/EOS/energy compatibility does not ensure
admissibility or accuracy. Decision: reject naked general stiff update and
common-limiter guaranteed accuracy; keep both raw proof directories unchanged.

Prior-art audit: Kräutle's common linear transport/reaction-invariant reduction,
Hiremath's element-determined species and Wang's elemental-consistent
reconstruction cover the generic reduction principle. Six independent species
plus four elemental reconstructions agree with the full ten-equation eligible
linear FV system to 2.22e-16. Variable elements and unequal diffusion instead
give residuals 0.121386/8.49e-8 relative and fail the predeclared equivalence
gate. Status: REJECTED_AS_PRIOR_ART generically; no duplicate native method or
measured cost advantage. Exact algebra and individual fields remain retained.

The combined energy/momentum/source-defect accuracy-controller hypothesis is
also derived and falsified. Exact conservative Euler/upwind Fourier contact
transport has zero pressure/source indicators and equation residuals below
2.58e-16, but T L1 errors 9.23324/4.78121/2.43678 K on nx32/64/128. A
transport/truncation indicator is separately necessary. This rejects that
specific guaranteed bound, not every possible operator-aware estimator.

## 2026-10-06 — failed source invariant gate and actual-data inversion limits

A new evidence check catches a scientific failure in technically completed
spatial Cv runs: the original 1e-10 relative accepted-source energy criterion
fails in three configurations, with maxima around 3e-7. It is not relaxed to
make the check pass. Audit finds 568 failed straddling calls at 1000 K and 15
other baseline failures. Independent legacy NASA coefficients have finite
enthalpy jumps; spatial endpoints alone cannot fully attribute each error.

Predeclare and build a separate direct native ODE branch utility, preserving
libcvChemistry and all accepted/current CFD applications. Its executable SHA
is 0f398b9e8508bd878d6f293f5b8cd3f00ae52f5317258b7dee42ae44f538e0a5;
exact source snapshot/Make inputs are in each CvBranchProbe experiment.json.
Eighteen controls: T0=999/1001/1100 K, TF10 us, rtol1e-8/1e-10/1e-12,
one interval or 1000 diagnostic intervals, declared radical mixture. Crossing
source energy changes approximately 1.14605e-7 relative at all tolerances.
Fine interpolated crossing concentrations account for it through the branch
jump, leaving <6.04e-13 relative remainder (<1.7e-14 at tight tolerances).
Native molar jumps match independent coefficients within 5.72e-8 J/kmol.

Nine independent Cantera branch trajectories, same verified legacy mechanism,
clone=False/weights/density, reproduce the crossing change. Strict native/
Cantera crossing T differences are below 3.3e-9 K. Above-branch controls do
not show the persistent jump. Interpretation: establishes the data/RHS branch
compatibility limitation in these direct controls, while other spatial errors
remain incompletely attributed. Cantera already validates NASA continuity;
status IMPLEMENTATION_ONLY, no new numerical-method claim or explanation of
the original 17% CFD loss. PNG/PDF figure generated from source JSON and
visually checked; no data repair is silently applied.

The next prederived actual-data scalar proof constructs a balanced admissible
H2/air conservative target inside a 0.07407165 J/kg energy gap, and a pure-N2
target with two roots across a 0.01588887 J/kg overlap. Exact rational interval
derivative bounds certify positive Cv on each branch. Thus positive branch
Cv alone does not guarantee global recovery existence/uniqueness. Earlier
unqualified monotonicity statements are corrected in editable candidate
derivations; executed successful residuals and accepted historical files stay
preserved. Proof raw files and explicit script hashes are retained.

Current decision: candidate_decision.md records bounded negative evidence and
specific open gates. No publishable method or universal exhaustion is claimed.
The remaining broader pivot needs transport/truncation information and a
precise new response approximation, resolved reacting references and actual
accuracy/cost benefit. Tests classify retained scientific failures separately
from technical completion. Reproducibility includes immutable analytical
script snapshots and explicit superseded/failed-source-gate classifications.

Final verification for this continuation: all 38 evidence checks pass,
including retained scientific failures, exact source snapshots, all 499 frozen
actionStudy files and the accepted audit freeze. Native reproducibility
manifest records 413 experiments: 393 technical completions, 20 retained
failures and zero incomplete cases, plus five versioned analytical experiments
and separate independent references. Eleven native records are explicitly
superseded; three completed F records are explicitly marked sourceEnergyGateFailed.
Current G and block parent C/H sources match their immutable experiment hashes.
The verification output is saved in processed/verification_results.txt. No
commit/push, publication decision or goal-complete status is asserted.

## 2026-10-07 — clean thermochemistry, invariant maps and bounded pivot

Read the requested eight historical derivation/result/log files before the
continuation; reran all 38 existing evidence checks successfully. Preserved
every original raw run, accepted audit and current native application/library.
The 499 published actionStudy files remain byte-identical.

Predeclared separate HS and CpHS sensitivity controls with immutable driver
and coefficient manifests. HS adjusts only upper h/s integration constants;
CpHS additionally matches upper Cp at the switch. Low/reference coefficients
and kinetic input text are exact. Thermo changes equilibrium-derived reverse
rates and hence trajectories; this interaction is part of the intervention.
No physical source-data accuracy or exact-real continuity is claimed.

Completed the mandatory matched full-F campaign: 18 H2 attribution records
(six reused legacy and twelve new runs), same 256 cells, four MPI ranks,
dt2/dt1 us and TF240 us. Native and CV source paths, and none/G closures where
declared, retain original fields, zero transport and discretization. Added
four installed-GRI full-flow thermo-only controls. Original eight-term
uncorrected budgets close with max step error below 1.64e-16 J; corrected-state
cell identities include DpostH/DpostC explicitly. The continuous CpHS H2
native dt2-us drift is -17.3900272%, versus -17.3886598% legacy. GRI likewise
retains about +7.2508%. The density/enthalpy/formation defect survives.

Six new direct native probe executions supply 18 T/tolerance observations.
All continuous-data direct source residuals pass the unchanged 1e-10 gate,
removing the legacy crossing floor near 1.146e-7. Full-flow source tracing
does not universally pass: at equal 184320 CV calls per thermo control,
legacy has 583 failures, HS 13 and CpHS 14. The 27 continuous-data failures
remain classified as scientific failures; some occur wholly above 1000 K.
Source endpoint traces do not uniquely identify the remaining stage error.
Native costOde endpoint energy is not traced; its finite RR/Qdot algebraic
cancellation is separately measured.

Pinned Cantera 3.2 supplies a mechanism-wide Cp/h/s/g, reaction enthalpy and
equilibrium audit of H2, GRI and the distributed Alzueta2023 baseline, plus
H2 controls. Audited six preexisting unique coefficient sets with original
use lists. A supplement measures the actual serialized new GRI CpHS file.
Floating Cp extrema are not promoted as interval positivity certificates.
Ninety independent CV/physical-CP trajectories vary mechanisms, initial
temperatures and ODE tolerances; observed crossing weights account for direct
legacy source floors. Physical CP expansion and units remain distinct from
the installed fixed-p concentration thermal abstraction. Modern native import
has fourteen retained parser failures; final obstacle is unsupported PLOG.
No reaction is dropped to fabricate a “matched” successful mechanism.

Wrote clean_vs_legacy_results.md before the next projection prototype; final
report includes the completed matrix, GRI budgets and measured two-factor
interactions. The exact within-trajectory identity is additive; a universal
additive data/integration/transport/coupling error partition is not inferred.
The hierarchical attribution and interaction differences retain their units
and declared intervention scope.

Primary method/source bytes are retained under sourceAudit/thermoInvariants_v1.
Full equation/implementation inspection of NASA PAC, RMG, Cantera validation,
Boettcher Appendix H, Mech Checker, CVODE projection, PelePhysics coupling and
installed finite RR rejects generic repair/projection/interface novelty.
Mech Checker already links automated continuity repair to integration and
pressure-coupled multizone numerical consequences. SCI full-method access
remains incomplete; other primary sources independently reject the broad
claims. thermo_prior_art_matrix.md records the exact comparisons.

After the mandatory attribution, executed 48 scalar projection controls on
continuous H2/GRI data over CV/physical CP, three temperatures and four loose
tolerances, with two stricter-reference tolerances. Forty recoveries are
eligible; 38 pass all endpoint gates. Eight GRI states have negligible but
strictly negative provisional Y, and two recoveries retain mass/element
residuals above 1e-12. No clipping or normalization hides them. Twenty-five
observed temperature errors increase after projection; 22 increases exceed
twice the stricter-reference contrast. Scalar recovery cannot reduce species
error. References/provisional trajectories both use Cantera BDF; independent
Python property inversion is not mislabeled as independent ODE verification.

The independent small abstract model executes 18 prescribed mass-balanced
finite maps with actual variable-Cp continuous properties and CV/physical CP
inversion. It verifies native finite RR equivalence and the necessary CV
pressure increment, and provides a two-cell post-map counterexample preserving
global species/mass and EOS while changing energy. It is an algebraic model,
not a new kinetic mechanism or a flow reference. Five candidate-family
decisions reject generic projection dominance, finite-RR novelty, interface
sufficiency, mechanism-only certification and unvalidated physical refitting.
Every decisive failure and limited successful property remains documented.

continuous_thermo_pivot.md records bounded exhaustion of these reasonable
implementation-level branches plus earlier cheap corrections, not universal
exhaustion or a publication survivor. The stronger pivot is an operator
response/error estimator containing transport truncation and chemistry
sensitivity to transported states, tested against resolved independent
reacting fields on continuous data. Generic forcing/tangent/Schur machinery
is established; a distinct approximation and accuracy/cost benefit remain
necessary. No concurrent new wall value is used for runtime/memory dominance.

Final verification: all unchanged 38 historical checks and 17 separate phase
checks pass. New source failures are classified in the supplemental phase
manifest; the historical three-source-failure criterion is preserved. Current
native provenance contains 449 experiments: 415 technical completions,
34 retained failures and zero incomplete cases. The PNG/PDF scientific figure
has machine-readable source points/input hashes and was visually inspected.
Verification outputs are retained in processed/thermochemical_phase_*verification*.txt.
No commit, push or publication/goal-complete status is asserted.

