# Analytic reacting-transport falsification

This benchmark extends the verified nonreacting entropy wave with a genuine
finite-rate species source and an analytic reference. It tests the surviving
shared-flux species/energy constructions independently of the coarse H2 kernel.
It is a mathematical reacting-transport benchmark, not a validated flame.

Two idealized nitrogen isomers A and B have identical W=28.0134 kg/kmol,
Cp=1000 J/(kg K), and Hf=2e6 J/kg. They share the same N elemental composition.
The irreversible first-order reaction A -> B has k=5e4 s^-1, zero activation
energy and zero reaction heat. The large common formation offset is an
elemental reference choice, not a source of heat. There is no viscosity,
diffusion, external forcing or boundary flux; the domain is periodic.

For constant U=40 m/s and p=101325 Pa, let q=x-Ut and

```
rho(x,t)=rhobar[1+0.05 sin(2 pi q/L)],
T(x,t)=p/[R rho(x,t)],
YA(x,t)=[0.5+0.2 cos(2 pi q/L)] exp(-k t),
YB(x,t)=1-YA(x,t).
```

These satisfy compressible Euler continuity/momentum/absolute-energy equations
and conservative finite-rate species transport exactly. Equal molecular
weights, caloric properties and formation references make EOS/energy
independent of the isomer split; production conserves mass/elements and
chemical enthalpy. Density and composition both vary, while the analytic
pressure and velocity remain constant. A second common-Hf variant can test
reference invariance without altering the physical trajectory.

Use the same domain, density amplitude and analytic entropy-wave initialization
as the preserved reference benchmark. At TF=20 us, compare rho,T,p,U,YA,YB
L1/L2/Linf errors for nx32/64/128 at dt=20 ns, and temporal refinement at fixed
nx128. All schemes remain first-order Euler/upwind; require ~first-order
spatial convergence, conservative mass/element/energy balance, positive states,
and no chemical-scalar accuracy penalty hidden by energy conservation.

The reaction is intentionally simple so exact verification does not depend
on Cantera, fitted flame speeds or the disputed coarse ignition trajectory.
Passing does not establish detailed reacting flame accuracy or novelty. Failure
is a cheap falsification of shared conservative transport even in this limit.
