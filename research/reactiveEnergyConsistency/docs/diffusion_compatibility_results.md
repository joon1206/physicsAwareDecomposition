# Sensible species-diffusion compatibility: executed control

The known species enthalpy face flux removes the local temperature error
in the declared equal-W/unequal-Cp diffusion test. It does not repair the
original zero-transport kernel density defect or establish method novelty.
Derivation and pre-test predictions: candidates/speciesSensibleDiffusion.md.

All cases: L=20 mm, T=800 K, p=101325 Pa, u=40 m/s, D=.01 m2/s,
TF=100 us, dt=.2 us; Cp_A=1000, Cp_B=2000 J/(kg K), equal W=28.0134.
Exact species solution is translating exponential diffusion of a cosine.
The physical species enthalpy flux keeps T/p/rho/u constant.

| Pr | nx | Method | Compatible flux | T L1 (K) | p Linf (Pa) | YA L1 | Relative energy drift | Cell closure (J) |
|---:|---:|---|---|---:|---:|---:|---:|---:|
| 0.7 | 32 | blockConservative | parent | 1.402404 | 34.44019 | 0.01350294 | +1.18142e-15 | 1.3498e-18 |
| 0.7 | 32 | conservativeState | off | 1.404526 | 35.12076 | 0.01350294 | -3.93805e-16 | 1.5086e-18 |
| 0.7 | 32 | conservativeState | parent | 1.404526 | 35.12076 | 0.01350294 | -3.93805e-16 | 1.5086e-18 |
| 0.7 | 32 | conservativeState | on | 5.513812e-12 | 6.984919e-10 | 0.0135052 | -6.89159e-15 | 1.2265e-18 |
| 0.7 | 32 | none | off | 1.400464 | 36.40658 | 0.01350295 | +1.95425e-07 | 1.4410e-18 |
| 0.7 | 32 | none | parent | 1.400464 | 36.40658 | 0.01350295 | +1.95425e-07 | 1.4410e-18 |
| 0.7 | 32 | none | on | 7.581491e-12 | 1.193257e-09 | 0.0135052 | -7.48230e-15 | 1.2088e-18 |
| 0.7 | 64 | blockConservative | parent | 1.500536 | 35.57462 | 0.007061782 | +3.93805e-16 | 7.3889e-19 |
| 0.7 | 64 | conservativeState | off | 1.501175 | 36.65549 | 0.007061752 | +5.90708e-16 | 6.7218e-19 |
| 0.7 | 64 | conservativeState | parent | 1.501175 | 36.65549 | 0.007061752 | +5.90708e-16 | 6.7218e-19 |
| 0.7 | 64 | conservativeState | on | 4.970246e-12 | 9.022187e-10 | 0.007061515 | +1.04358e-14 | 5.6021e-19 |
| 0.7 | 64 | none | off | 1.497593 | 37.87216 | 0.007061818 | +3.01935e-07 | 7.0653e-19 |
| 0.7 | 64 | none | parent | 1.497593 | 37.87216 | 0.007061818 | +3.01935e-07 | 7.0653e-19 |
| 0.7 | 64 | none | on | 4.996892e-12 | 6.984919e-10 | 0.007061515 | +2.75664e-15 | 6.3305e-19 |
| 0.7 | 128 | blockConservative | parent | 1.567087 | 25.91824 | 0.003685031 | +4.92256e-15 | 4.2051e-19 |
| 0.7 | 128 | conservativeState | off | 1.567497 | 27.08025 | 0.003684973 | +6.10398e-15 | 3.7003e-19 |
| 0.7 | 128 | conservativeState | parent | 1.567497 | 27.08025 | 0.003684973 | +6.10398e-15 | 3.7003e-19 |
| 0.7 | 128 | conservativeState | on | 3.631762e-12 | 8.003553e-10 | 0.003676624 | -8.46681e-15 | 3.2781e-19 |
| 0.7 | 128 | none | off | 1.566088 | 27.42648 | 0.003684855 | +4.57547e-07 | 3.8767e-19 |
| 0.7 | 128 | none | parent | 1.566088 | 27.42648 | 0.003684855 | +4.57547e-07 | 3.8767e-19 |
| 0.7 | 128 | none | on | 4.636291e-12 | 9.022187e-10 | 0.003676624 | -8.46681e-15 | 3.4437e-19 |
| 1 | 32 | blockConservative | parent | 1.33511e-11 | 2.299203e-09 | 0.0135052 | -2.99292e-14 | 1.2477e-18 |
| 1 | 32 | conservativeState | off | 1.200817e-11 | 1.993612e-09 | 0.0135052 | -2.77633e-14 | 1.1031e-18 |
| 1 | 32 | conservativeState | parent | 1.200817e-11 | 1.993612e-09 | 0.0135052 | -2.77633e-14 | 1.1031e-18 |
| 1 | 32 | conservativeState | on | 1.200817e-11 | 1.993612e-09 | 0.0135052 | -2.77633e-14 | 1.1031e-18 |
| 1 | 32 | none | off | 1.231371e-11 | 1.29512e-09 | 0.0135052 | -1.77212e-14 | 1.2780e-18 |
| 1 | 32 | none | parent | 1.231371e-11 | 1.29512e-09 | 0.0135052 | -1.77212e-14 | 1.2780e-18 |
| 1 | 32 | none | on | 1.231371e-11 | 1.29512e-09 | 0.0135052 | -1.77212e-14 | 1.2780e-18 |
| 1 | 64 | blockConservative | parent | 3.211653e-12 | 6.984919e-10 | 0.007061515 | +6.49778e-15 | 6.0550e-19 |
| 1 | 64 | conservativeState | off | 3.398171e-12 | 4.947651e-10 | 0.007061515 | +7.87610e-15 | 5.5470e-19 |
| 1 | 64 | conservativeState | parent | 3.398171e-12 | 4.947651e-10 | 0.007061515 | +7.87610e-15 | 5.5470e-19 |
| 1 | 64 | conservativeState | on | 3.398171e-12 | 4.947651e-10 | 0.007061515 | +7.87610e-15 | 5.5470e-19 |
| 1 | 64 | none | off | 4.495959e-12 | 8.003553e-10 | 0.007061515 | +4.92256e-15 | 5.6521e-19 |
| 1 | 64 | none | parent | 4.495959e-12 | 8.003553e-10 | 0.007061515 | +4.92256e-15 | 5.6521e-19 |
| 1 | 64 | none | on | 4.495959e-12 | 8.003553e-10 | 0.007061515 | +4.92256e-15 | 5.6521e-19 |
| 1 | 128 | blockConservative | parent | 6.028067e-12 | 1.396984e-09 | 0.003676624 | -1.35863e-14 | 2.9661e-19 |
| 1 | 128 | conservativeState | off | 6.195933e-12 | 1.29512e-09 | 0.003676624 | -1.41770e-14 | 3.1571e-19 |
| 1 | 128 | conservativeState | parent | 6.195933e-12 | 1.29512e-09 | 0.003676624 | -1.41770e-14 | 3.1571e-19 |
| 1 | 128 | conservativeState | on | 6.195933e-12 | 1.29512e-09 | 0.003676624 | -1.41770e-14 | 3.1571e-19 |
| 1 | 128 | none | off | 6.919798e-12 | 1.193257e-09 | 0.003676624 | -1.33894e-14 | 3.2056e-19 |
| 1 | 128 | none | parent | 6.919798e-12 | 1.193257e-09 | 0.003676624 | -1.33894e-14 | 3.2056e-19 |
| 1 | 128 | none | on | 6.919798e-12 | 1.193257e-09 | 0.003676624 | -1.33894e-14 | 3.2056e-19 |

Flag-off/parent and Pr=1 on/off endpoint field comparisons are recorded
for T/p/rho/h/U/A/B in diffusion_compatibility.json. Maximum comparison
Linf over all recorded fields: 0.
Pr=.7 parent temperature errors increase toward a nonzero model-error
floor while the compatible flux leaves only recorded roundoff/solve error.
That is a local transport-model result; global energy alone misses it.

| Method | Flux | Mesh pair | Observed YA L1 order |
|---|---|---|---:|
| none | parent | 32→64 | 0.93516 |
| none | parent | 64→128 | 0.93843 |
| conservativeState | parent | 32→64 | 0.93518 |
| conservativeState | parent | 64→128 | 0.93837 |
| blockConservative | parent | 32→64 | 0.93517 |
| blockConservative | parent | 64→128 | 0.93836 |
| none | on | 32→64 | 0.93547 |
| none | on | 64→128 | 0.94160 |
| conservativeState | on | 32→64 | 0.93547 |
| conservativeState | on | 64→128 | 0.94160 |

The correction uses post-species composition and predictor p/T, frozen
through the conservative energy inversion. Its divergence is included
in both the actual residual and local transport ledger. A separate
DextraSensibleTransport column reports its signed local contribution;
absExtraSensibleTransport distinguishes nonzero local redistribution
from its zero periodic-domain sum. Positivity and EOS are recorded
for every case. This special constant-temperature control does not
prove a general nonlinear face chain rule, time order or entropy stability.
The shared Sutherland reacting controls are interpreted separately.
