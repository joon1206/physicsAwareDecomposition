# Conservation, momentum and source defects do not bound transport error

2026-10-06. Derivation before the exact counterexample. No new method claim.
The energy-only estimator is already falsified. This check resolves a narrower
remaining hypothesis: adding pressure/momentum mismatch and local chemistry
step error suffices to turn it into a general accuracy controller.

Consider periodic pure-gas Euler advection with u=40 m/s, p=101325 Pa,
R=300, Cv=700 J/kg/K. Let rho=rho0(1+.15 cos(kx-ku t)), rho0=p/(800 R),
L=.02 m, k=2 pi/L and T=p/(R rho). This is an exact smooth contact wave.
Chemistry is absent. Its conservative momentum and energy are

    m=u rho, E=(Cv/R)p + (u^2/2)rho.

Use implicit Euler/common upwind on a uniform grid. For theta=k dx and
C=u dt/dx, the density Fourier amplification is exactly

    g=[1+C(1-exp(-i theta))]^-1.

Momentum residual is u times continuity residual; energy residual is
(u^2/2) times continuity residual, since constant pressure terms have zero
periodic divergence. Set T from the EOS. Mass, energy, momentum, species and
EOS are compatible; the final pressure change and chemistry step error are
zero. Nevertheless g^N differs from exp(-i k u TF). Thus temperature/density
errors are finite while all three proposed indicators vanish in exact
arithmetic. A bound vanishing with those indicators is impossible in this
class. Floating-point residual checks do not replace the algebraic proof.

Predeclare nx32/64/128, dt20 ns, TF100 us. Evaluate the exact discrete
amplification, independent translated wave, all conservative residuals and
temperature errors. Require positive rho/T and relative residuals <1e-12;
retain finite field errors. This is an exactly solved FV counterexample,
not an executed native CFD method, reacting flame or performance experiment.

Decision scope: reject conservation/momentum/source-defect-only guaranteed
accuracy control. It does not reject indicators containing spatial/temporal
truncation information, adjoints, resolved reference error or rigorous operator
estimates. Such a larger controller is a separate unresolved research task;
its principle and novelty would require another precise derivation and audit.

The predeclared exact discrete experiment completes. T L1 errors on
nx32/64/128 are 9.23324/4.78121/2.43678 K, while scaled mass/momentum/energy
equation residuals are below 2.58e-16, inventories telescope and pressure/
source indicators are exactly zero. All states are positive. Observed T
orders are 0.94946/0.97240; refinement reduces error without making the
defect indicators informative. Raw CombinedDefect_analytic and processed
combined_defect_counterexample.json retain every exact/numerical field and
the script hash. This extends the energy-only counterexample without claiming
that all possible combined operator-aware estimators fail.
