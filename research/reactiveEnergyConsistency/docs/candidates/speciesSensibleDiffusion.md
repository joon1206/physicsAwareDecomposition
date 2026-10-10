# Species sensible-enthalpy diffusion compatibility control

Date: 2026-10-06. Derivation before numerical tests. This follows the measured
failure of energy closure to guarantee local thermochemical accuracy. It is
a transport-model/control pivot, not a new pressure-correction claim.

## Hypothesis and target term

The installed v2012 species equations use -laplacian(muEff,Ys), while the
sensible-enthalpy equation uses -laplacian(alphaEff,hs). In the laminar constant
transport model muEff=mu and alphaEff=mu/Pr. Those are different species and
enthalpy diffusivities unless Pr=1. Formation-inclusive energy closure adds
the formation transport from the species equations; it does not automatically
supply the sensible enthalpy carried by their diffusion fluxes.

For Fick flux Js=-mu*grad(Ys) and physical conductivity lambda=alpha*Cp,

    q_sensible=-lambda*grad(T)+sum_s Hs_s*Js,
    grad(hs)=Cp*grad(T)+sum_s Hs_s*grad(Ys),
    q_sensible=-alpha*grad(hs)+(alpha-mu)*sum_s Hs_s*grad(Ys).

Thus a conservative face-flux correction, if implemented, would be
(alpha-mu)*sum_s Hs_s*grad(Ys), not an isolated formation-density source. Its
divergence integrates to zero in the periodic domain. It changes the local
transport ledger, not the original net post-pressure density defect. For
general thermodynamics a discretely consistent face chain rule is needed;
the continuous identity alone is not a proof of the finite-volume algorithm.

## Independent exact control

Use equal molecular weights W=28.0134 kg/kmol but different constant heat
capacities Cp_A=1000 and Cp_B=2000 J/(kg K); both formation enthalpies are zero.
No chemistry. Initial T=800 K, p=101325 Pa, u=40 m/s, constant rho=p/(R*T).
On the periodic L=20 mm domain,

    Y_A=.5+.2*cos[2*pi*(x-u*t)/L]*exp[-D*(2*pi/L)^2*t],
    Y_B=1-Y_A, D=.01 m2/s, mu=rho*D.

With physical sensible-species diffusion flux, T,p,rho,u remain constant.
Species and energy equations use the same diffusing composition, while heat
conduction has zero gradient. The old alpha*grad(hs) closure instead gives a
residual (mu-alpha)*(Cp_A-Cp_B)*(800-298.15)*laplacian(Y_A). The mismatch
persists under refinement to that different continuum transport model.

Test existing baseline/G/block at Pr=.7 and the Pr=1 negative control. Use
nx32/64/128, dt200ns, TF100us. Record exact T/Y/p/U errors, local and global
budget closure, sumY, positivity and energy drift. No solver change is needed
to falsify the claim that conservative energy repair also provides physical
diffusion compatibility. Expected outcome: conservation survives for G/block,
but the Pr=.7 temperature error does not vanish to roundoff. Pr=1 should
eliminate this particular transport mismatch; other algorithm errors remain.

## Prior art, cost and decision rule

Species-diffusion enthalpy transport is established physics and prior art;
Nonaka 2012 explicitly includes compatible species/enthalpy diffusion. The
Foundation14 thermophysicalPredictor routes species through divj and energy
through divq, rather than porting v2012's mu/alpha operators blindly. Its
nonUnityLewisEddyDiffusivity implementation has been read at source level:
[Foundation14 source](https://cpp.openfoam.org/v14/nonUnityLewisEddyDiffusivity_8C_source.html),
q() lines 88–136 and divq() lines 190–242. It combines temperature conduction
with species sensible enthalpy transport. Its laminar species coefficient is
kappa/Cp, with a Prt/Sct turbulent term; our control retains v2012's actual mu
species coefficient. This is a transport-model distinction, not an identical
model port. FickianFourier source was unavailable and is not treated as read.
A successful compatible flux port would be an
implementation control unless a genuinely new construction/analysis resulted.

If the predicted mismatch is observed, derive and test a scoped face-flux
control before broader reacting comparisons. It must enter both the physical
energy residual and the local ledger. A correction that silently changes the
flux target while keeping the old audit formula is unacceptable. No additional
global solve is predicted for an explicit compatible face-flux term, but its
time-level/order/stability limits must be tested separately.

## First executed screen and scoped correction time level

The nx32 pilot supports the predicted failure: at Pr=.7, baseline/G/block
have T L1 1.40046/1.40453/1.40240 K. G/block energy remains roundoff. At Pr=1,
all three have T errors near 1e-11 K. This isolates the diffusion-model mismatch.

Before implementing the control: evaluate the added face flux after the species
solve using its current Ys and the thermodynamic predictor p,T. Keep that flux
fixed through the post-pressure conservative residual inversion. This is a
declared lagged first-order term; it is not a fully implicit heat-flux solve or
a general discrete chain-rule theorem. Add its divergence to the assembled
enthalpy equation, the full absolute-energy residual, and the cellwise transport
budget; include any physical boundary contribution once. No source or uniform
energy redistribution is introduced. The initial scope is the periodic
synthetic diffusion test. A flag-off run must reproduce the parent method,
Pr=1 must make the new flux vanish, and Pr=.7 must restore constant T/p to
the recorded equation/thermo tolerances before any broader claim.

## Broader control, specified before its execution

The original F/B/Mix factory cases use Sutherland As=0, Ts=0: their physical
viscosity and species/thermal diffusivities are zero. They are useful exact
zero-flux controls; their original density/energy defect cannot be removed by
a species diffusion term. Calling that kernel viscous would be incorrect.

Separately tagged nonzero-transport cases use the same public NASA chemistry,
geometry, boundary conditions and initial state, with shared Sutherland
As=1.458e-6 and Ts=110.4 K. This declared common-species transport is a
numerical compatibility screen, not validated hydrogen transport or a resolved
laminar flame. Execute F at dt1/.5 us and Mix at dt1 us, old/new flux and
baseline/G. Expected: the new periodic flux has zero net domain contribution
but changes local T/Y/p; it cannot cancel the post-pressure density mismatch
as an algebraic identity. G must retain absolute energy, mass/species and EOS
compatibility to its recorded tolerances. Record changed outcomes, failures,
flux magnitude and local closure. No flame accuracy/cost claim follows.

## Coupled-face failure and repair derivation before coding

The first shared-Sutherland Mix G run at dt1 us has relative energy drift
8.92923e-9 despite local ledger closure below 1.6e-19 J. Its accumulated extra
flux domain contribution is +1.7816983e-10 J, matching the independent energy
change +1.7816976e-10 J. F contributions happen to cancel to approximately
1e-23 J; the constant-temperature serial control alone did not expose this.
Snapshot e1eed03aad2142f12f9f1499ed6ebe16fa5fe8593df075b31dc293f63f052133
and executable 3c574a656df6f8f85a2bc3e38f36594c68af45b94b03e46ab40fc7e578cae06b
are retained with the failing broader conservation result.

For an internal or paired coupled face, the correction is conservative only
if its coefficient is the same from both adjacent cells and the normal species
gradient changes sign. v2012 surfaceInterpolationScheme::interpolate uses
patchInternalField and patchNeighbourField for coupled fields. Processor
patchNeighbourField reads evaluated halo values; manually assigning a derived
species enthalpy patch from p/T does not certify it equals the current remote
internal derived value. Refresh the derived diffusivity difference and each
species sensible enthalpy with correctBoundaryConditions before interpolation.
This is a proposed repair to coefficient halo consistency, not proof of the
cause until a tagged replay cancels the net flux and preserves independent
energy. Repeat on/off zero/Pr1 controls and compare the nonzero-transport G
solution in serial and four ranks. Do not overwrite the original evidence.

The synced Mix G flux now cancels globally and energy is at roundoff, but the
serial/four-rank endpoint T Linf difference is 1.67524e-5 K (flag off:
1.67149e-5 K). The difference exists without the new flux. Before the next
control: linear solver tolerance is already 1e-14; test two extra inherited
thermo.correct passes after the enthalpy solve, leaving equations, coefficients
and pressure coupling unchanged. Hypothesis: JANAF h-to-T stopping error is
amplified in a transient partition comparison. Acceptance for that hypothesis
requires reduction below 1e-6 K, rather than assuming the cause from a small
endpoint discrepancy. Retain the old result if it does not shrink.

The factory input already contains padThermoCorrections=2. The first thermo2
tag therefore repeats the original configuration and is retained as a duplicate
control, not evidence about additional inversion. Corrected pre-test contrast:
thermo4 changes that existing key to four passes, adding two beyond the default;
the acceptance threshold remains 1e-6 K. No duplicate input keyword is added.

At Pr=1, alpha computed through conductivity/Cp can differ from mu by floating
point roundoff. The largest recorded absolute flux step contribution is
7.9e-22 J, while all on/off endpoint fields coincide. Use the predeclared
1e-20 J roundoff floor for this vanishing-term check; a flag-off constructed
zero flux must remain exactly zero. Do not interpret that tiny algebraic
residue as physical species enthalpy diffusion.

The actual four-pass contrast completed. G serial/parallel T Linf is
1.67523989e-5 K with the flux and 1.67148618e-5 K without it, essentially
unchanged from the inherited two-pass cases. The proposed thermodynamic-pass
explanation fails its predeclared 1e-6 K test. Its cause remains unresolved;
this discrepancy is not relabelled as roundoff or accepted by changing the
threshold. Global coupled-flux cancellation and independent energy agreement
pass in the synced implementation, while strict field equivalence remains open.
