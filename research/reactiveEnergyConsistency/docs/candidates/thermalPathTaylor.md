# Leading thermal-path source compensation: rapid mathematical falsification

2026-10-06. Derivation before code. NOVELTY_NOT_ESTABLISHED. This is a local
Taylor/defect-compensation construction; absence of an identical implementation
in a search is not novelty. Generic augmented-source/deferred chemistry has
equation-level prior art in Nonaka 2012 and PelePhysics' forced reactors.

## Measured motivation and local expansion

Matched CPFD and Cv chemistry followed by G differ in the homogeneous limit,
while both may conserve final CFD energy. At a common initial concentration
and temperature state the species rate omega is initially the same. Thermal
and pressure derivatives differ between the two source paths. Smooth autonomous
flow expansion gives the leading concentration difference

    c_CV(dt) - c_CP(dt)
      = dt^2/2 [omega_T (Tdot_CV-Tdot_CP)
                  + omega_p (pdot_CV-pdot_CP)] + O(dt^3).

Candidate: add this computed leading term to the integrated CP source species
increment, then use the existing full conservative energy/EOS closure. Balanced
reaction derivatives have zero total mass and elemental production, so the
correction preserves those linear invariants in exact arithmetic. An elemental
energy shift leaves both balanced thermal derivatives invariant. This changes
source trajectory error, not the previously derived post-pressure density pair.

The expansion requires bounded derivatives and a resolved chemistry macro step.
It is not uniform in stiff reaction eigenvalues. No unconditional positivity,
stability, higher-order spatial accuracy or cheap detailed-chemistry claim follows.
The two thermal columns could be computed with a small number of extra rate
evaluations; that cost advantage is only a hypothesis until valid comparisons.

## Exact synthetic source pre-screen

Use two equal-molecular-weight isomers A->B, mass fraction y=Y_A, equal constant
Cp=1000 J/kg/K, Cv=700, formation-energy difference Q=2e6 J/kg, rho=1 kg/m3,
initial y0=.5, T0=1000 K. Set k(T)=k0+a(T-T0)>0. In the fixed-volume state,

    ydot=-k(T)y,  Tdot=Q k(T)y/Cv,
    E=Cv*T+Q*y = constant,
    T=T0+Q*(y0-y)/Cv.

Thus K=k0+a Q y0/Cv and b=a Q/Cv give the exact positive solution

    y(t)=K*y0*exp(-K*t)/(k0+b*y0*exp(-K*t)).

The CP source map from each macro state has the same closed form with its
local k(T_n), b_CP=aQ/Cp and initial y_n. Its temperature is projected back
to the conserved E after each macro step. The Taylor species correction is

    delta_y = -dt^2/2 * a*Q*k(T_n)*y_n^2*(1/Cv-1/Cp).

Mass, energy and EOS p=(Cp-Cv)rho T remain algebraically compatible after
projection, but delta_y is negative. As dt grows, the exact CP endpoint tends
to zero while |delta_y| grows quadratically. Therefore this naked correction
must produce negative A for sufficiently stiff/large steps, despite a positive
CP source integrator. This is an analytic counterexample to unconditional
admissibility, not merely a numerical failure.

Predeclare two numerical checks: smooth k0=1e5 s^-1, a=100 s^-1/K, TF=10 us,
dt2/1/.5/.25 us for endpoint order; stiff k0=1e7, a=1000, dt=TF=2 us for the
positivity counterexample. No native implementation is promoted if the stiff
case fails. A common scalar limiter could restore linear invariants/positivity,
but would change the local-order argument when active; it is a separate,
unverified extension with extensive limiting prior art. Preserve negative y
in the evidence rather than clipping it into an apparent success.

The exact source pre-screen completes. Uncompensated smooth endpoint T orders
are 1.0054/1.0033/1.0019; compensated orders are 2.0976/2.0470/2.0230.
At dt2 us the smooth error drops from 13.6303 K to 4.57405 K. The stiff
counterexample instead gives Y_A=-4.2857143 and T error 12244.9 K, while the
uncompensated exact CP map stays positive. Energy, mass and EOS compatibility
alone cannot rescue this state. Decision: REJECT naked macro compensation;
do not promote it into a native reacting solver under a general admissibility
claim. The raw negative state and analytic proof are permanent evidence.

Before testing a positivity limiter, select a weak thermal-feedback/stiff
regime k0=1e6 s^-1, a=50 s^-1/K, dt=TF=4 us. The linear-invariant-preserving
limiter scales the negative Taylor increment by a common theta so the output
is nonnegative. When active it drives A near zero. However, if the exact CV
endpoint remains more than half the CP endpoint, that limiting error exceeds
the original CP error. This regime is selected to falsify a general claim
that positivity plus energy restoration also improves source accuracy.
Report baseline/limited exact errors, limiter activity and invariant residuals;
do not clip the unmodified negative result or count this synthetic test as a
detailed-flame benchmark. Generic positivity limiting does not establish novelty.

The separate predeclared limiter experiment completes. The exact Cv endpoint
is Y_A=0.007366215249, T=2407.5250993 K. The uncompensated CP map gives
Y_A=0.007866779486 and T error 1.4301835 K. The naked correction gives
Y_A=-0.07784750623, retained without clipping. A common theta=0.0917790940
produces positive Y_A=7.86697e-15 and T error 21.0463293 K: 14.715824 times
the baseline error. Mass and EOS residuals are zero; the energy residual
2.33e-10 J/kg is 1.37e-16 of the initial energy. Positivity plus energy
closure therefore does not imply accuracy improvement for this limiter.
Decision: REJECT that general claim; no native solver promotion. This does
not exclude other rigorously analysed stiff-source or limiting methods.

Evidence: candidateStudy/data/raw/ThermalTaylor_analytic and the separate
ThermalTaylor_limiterWeakFeedback directory; processed thermal_path_taylor.json
and thermal_path_limiter.json. Each records the script hash and exact source
parameters. The original ten bare-map records remain unchanged.
