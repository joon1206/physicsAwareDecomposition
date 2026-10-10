# Unequal-thermodynamic analytic contact-wave results

The chemistry-off, inviscid periodic H2/N2 wave has exact constant pressure
101325 Pa and velocity 40 m/s. Temperature and composition translate with
that velocity. The installed NASA7 thermodynamics are used in both the
case and independent inventory/analytic evaluation. See the pre-test
derivation in candidates/mixturePressureCompatibility.md.

| Method | nx | T L1 (K) | H2 L1 | p Linf (Pa) | Ux Linf (m/s) | Relative energy drift | Max element drift | Max EOS residual |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| blockConservative | 32 | 3.19291 | 0.000928987 | 295.604 | 1.49352 | +3.576e-15 | 3.900e-16 | 2.554e-14 |
| blockConservative | 64 | 1.60878 | 0.000470469 | 149.242 | 0.750327 | +4.648e-15 | 6.285e-16 | 2.665e-14 |
| blockConservative | 128 | 0.808684 | 0.000237103 | 75.2599 | 0.378006 | -2.682e-15 | 1.170e-15 | 2.820e-14 |
| central | 32 | 50.8142 | 0.0132296 | 156.662 | 0.111574 | -3.397e-14 | 2.231e-14 | 2.509e-14 |
| central | 64 | 28.8009 | 0.00756157 | 96.5215 | 0.0922453 | -1.698e-14 | 1.414e-14 | 2.787e-14 |
| central | 128 | 15.3658 | 0.00406088 | 54.5829 | 0.0639122 | -4.094e-14 | 2.325e-14 | 2.398e-14 |
| conservativeState | 32 | 3.21119 | 0.000930538 | 291.655 | 1.46943 | +4.146e-13 | 4.713e-16 | 2.154e-14 |
| conservativeState | 64 | 1.6169 | 0.000471289 | 148.041 | 0.738218 | +1.074e-13 | 0.000e+00 | 1.310e-14 |
| conservativeState | 128 | 0.810951 | 0.000237436 | 74.7409 | 0.372656 | +2.270e-14 | 1.365e-15 | 1.399e-14 |
| hllc | 32 | 3.2968 | 0.000902754 | 12.0733 | 0.0139856 | +5.363e-15 | 2.608e-14 | 9.215e-14 |
| hllc | 64 | 1.66048 | 0.000455222 | 6.09473 | 0.00826473 | -9.296e-15 | 1.823e-14 | 1.019e-13 |
| hllc | 128 | 0.831313 | 0.000227982 | 3.09567 | 0.00467885 | -1.806e-14 | 2.482e-14 | 9.570e-14 |
| none | 32 | 3.20842 | 0.000929291 | 293.553 | 1.46813 | +1.010e-05 | 7.624e-06 | 8.882e-16 |
| none | 64 | 1.61488 | 0.000470388 | 148.102 | 0.73865 | +1.097e-05 | 7.334e-06 | 8.882e-16 |
| none | 128 | 0.809204 | 0.000236801 | 74.3288 | 0.373425 | +1.159e-05 | 7.187e-06 | 8.882e-16 |

## Refinement and interpretation

| Method | Mesh pair | T L1 order | H2 L1 order | p Linf order |
|---|---|---:|---:|---:|
| blockConservative | 32/64 | 0.9889 | 0.9816 | 0.9860 |
| blockConservative | 64/128 | 0.9923 | 0.9886 | 0.9877 |
| central | 32/64 | 0.8191 | 0.8070 | 0.6987 |
| central | 64/128 | 0.9064 | 0.8969 | 0.8224 |
| conservativeState | 32/64 | 0.9899 | 0.9815 | 0.9783 |
| conservativeState | 64/128 | 0.9955 | 0.9891 | 0.9860 |
| hllc | 32/64 | 0.9895 | 0.9878 | 0.9862 |
| hllc | 64/128 | 0.9981 | 0.9977 | 0.9773 |
| none | 32/64 | 0.9904 | 0.9823 | 0.9870 |
| none | 64/128 | 0.9968 | 0.9902 | 0.9946 |

G and the tight pressure/species/energy block remove the recorded energy
drift but do not preserve the exact mixture pressure. Their temperature
errors closely track the baseline on this independent analytic problem.
HLLC produces smaller pressure deviations but finite thermodynamic mixing
error; its equal-property pressure-preservation result does not generalize
to the unequal-NASA mixture. The central flux has larger temperature
diffusion. These statements concern the displayed configurations, with
common fixed dt20ns, rather than all possible fluxes or coupling methods.

The two-donor common-weight remap independently conserves partial mass
and energy but changes EOS pressure. Enforcing pressure instead would
change the conserved energy target. This is a known nonlinear thermodynamic
compatibility problem, with the conditional proof and prior-art boundary
recorded in the derivation. Formation-reference shifts cancel algebraically
from the mixing mismatch and were checked numerically.

For the 50/50 example: pressure shift 1433.330788 Pa;
energy-density mismatch at enforced original pressure 3826.387242 J/m3.

No numerical-method contribution is asserted from this diagnostic.
The raw wave inputs/fields/ledgers and exact executable/source hashes
are retained. New methods would have to improve compatibility and the
accuracy/cost frontier, beyond correcting the original global defect.

Sources: candidateStudy/data/processed/mixture_wave.json and
mixture_mixing_identity.json.
