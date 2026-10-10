# Independent inviscid reference comparison

No reacting spatial order or exact field-error ranking is established.
These cases solve the same periodic inviscid H2 kernel with native detailed
chemistry, As=0 and Euler time integration. They are separate from the
256-cell timing benchmark (which also has As=0). The one-column geometry and native ode controls differ. Wall times here are execution records, not a
controlled performance comparison.

## Executed reference and pressure-method differences

Each reference is its flux family's finest executed mesh. Comparing meshes
uses aligned volume averages of rho, rhoU, rhoY and rhoEa followed by
independent NASA thermodynamic inversion. Field differences are not exact
PDE errors. Initial inventory sampling differences and source hashes are
retained in the source JSON.

| Family | Reference | Cells | dt (ns) |
|---|---|---:|---:|
| central | Central_F_nx512_dt7.8125e-09_TF0.00024_hRecovery3 | 512 | 7.8125 |
| hllc | HLLC_F_nx512_dt7.8125e-09_TF0.00024_hRecovery3 | 512 | 7.8125 |

| Reference family | Comparison | Cells | T L1 (K) | T Linf (K) | U L1 (m/s) | H2O L1 | Initial E relative difference |
|---|---|---:|---:|---:|---:|---:|---:|
| central | Central_F_nx256_dt1.5625e-08_TF0.00024_hRecovery2 | 256 | 26.24599 | 49.65772 | 4.85360 | 0.002596 | +7.375e-10 |
| central | HLLC_F_nx128_dt1.5625e-08_TF0.00024_hRecovery3 | 128 | 15.25105 | 49.42147 | 9.63268 | 0.00207208 | +2.163e-09 |
| central | HLLC_F_nx128_dt3.125e-08_TF0.00024_hRecovery3 | 128 | 16.34820 | 52.58061 | 9.88253 | 0.00210549 | +2.163e-09 |
| central | HLLC_F_nx256_dt1.5625e-08_TF0.00024_hRecovery3 | 256 | 46.14056 | 125.89532 | 15.33707 | 0.00347245 | +7.375e-10 |
| central | HLLC_F_nx256_dt7.8125e-09_TF0.00024_hRecovery3 | 256 | 44.72521 | 122.47595 | 18.29844 | 0.00347163 | +7.375e-10 |
| central | HLLC_F_nx32_dt1.25e-07_TF0.00024_hRecovery3 | 32 | 31.07857 | 56.14078 | 4.92170 | 0.00241747 | +2.806e-06 |
| central | HLLC_F_nx512_dt7.8125e-09_TF0.00024_hRecovery3 | 512 | 111.03735 | 427.08394 | 26.98701 | 0.00795781 | +0.000e+00 |
| central | HLLC_F_nx64_dt6.25e-08_TF0.00024_hRecovery3 | 64 | 10.54298 | 17.42883 | 8.33966 | 0.000348074 | +3.047e-08 |
| central | InvF_blockConservative_nx128_dt3.125e-08_TF0.00024 | 128 | 19.36513 | 42.47427 | 19.95561 | 0.00199652 | +2.163e-09 |
| central | InvF_blockConservative_nx32_dt1.25e-07_TF0.00024 | 32 | 43.30563 | 76.58991 | 13.78648 | 0.00265419 | +2.806e-06 |
| central | InvF_blockConservative_nx64_dt6.25e-08_TF0.00024 | 64 | 27.13065 | 43.95919 | 11.10757 | 0.000462696 | +3.047e-08 |
| central | InvF_conservativeState_nx128_dt3.125e-08_TF0.00024 | 128 | 35.64598 | 99.63784 | 38.17176 | 0.00193637 | +2.163e-09 |
| central | InvF_conservativeState_nx32_dt1.25e-07_TF0.00024 | 32 | 70.92762 | 120.19200 | 55.73506 | 0.00330632 | +2.806e-06 |
| central | InvF_conservativeState_nx64_dt6.25e-08_TF0.00024 | 64 | 27.04578 | 83.93391 | 37.26132 | 0.000671086 | +3.047e-08 |
| central | InvF_none_nx128_dt3.125e-08_TF0.00024 | 128 | 31.56728 | 64.61628 | 32.18609 | 0.00234386 | +2.163e-09 |
| central | InvF_none_nx32_dt1.25e-07_TF0.00024 | 32 | 59.75201 | 126.33028 | 62.34754 | 0.00312676 | +2.806e-06 |
| central | InvF_none_nx64_dt6.25e-08_TF0.00024 | 64 | 37.84076 | 73.75939 | 43.34972 | 0.00109376 | +3.047e-08 |
| hllc | Central_F_nx256_dt1.5625e-08_TF0.00024_hRecovery2 | 256 | 133.80162 | 456.06701 | 22.68392 | 0.00824405 | +7.375e-10 |
| hllc | Central_F_nx512_dt7.8125e-09_TF0.00024_hRecovery3 | 512 | 111.03735 | 427.08394 | 26.98701 | 0.00795781 | +0.000e+00 |
| hllc | HLLC_F_nx128_dt1.5625e-08_TF0.00024_hRecovery3 | 128 | 96.37042 | 422.20248 | 32.46201 | 0.00707618 | +2.163e-09 |
| hllc | HLLC_F_nx128_dt3.125e-08_TF0.00024_hRecovery3 | 128 | 95.13502 | 420.79476 | 31.06772 | 0.00704536 | +2.163e-09 |
| hllc | HLLC_F_nx256_dt1.5625e-08_TF0.00024_hRecovery3 | 256 | 68.16213 | 360.07978 | 35.44323 | 0.00566587 | +7.375e-10 |
| hllc | HLLC_F_nx256_dt7.8125e-09_TF0.00024_hRecovery3 | 256 | 69.51862 | 363.12956 | 41.15093 | 0.00570514 | +7.375e-10 |
| hllc | HLLC_F_nx32_dt1.25e-07_TF0.00024_hRecovery3 | 32 | 137.61513 | 441.22648 | 23.40524 | 0.00818962 | +2.806e-06 |
| hllc | HLLC_F_nx64_dt6.25e-08_TF0.00024_hRecovery3 | 64 | 118.51958 | 438.53747 | 19.65605 | 0.00794451 | +3.047e-08 |
| hllc | InvF_blockConservative_nx128_dt3.125e-08_TF0.00024 | 128 | 97.59728 | 436.02291 | 46.12279 | 0.00716695 | +2.163e-09 |
| hllc | InvF_blockConservative_nx32_dt1.25e-07_TF0.00024 | 32 | 148.83703 | 461.82532 | 38.95318 | 0.00821079 | +2.806e-06 |
| hllc | InvF_blockConservative_nx64_dt6.25e-08_TF0.00024 | 64 | 133.93735 | 454.10832 | 20.27407 | 0.00811239 | +3.047e-08 |
| hllc | InvF_conservativeState_nx128_dt3.125e-08_TF0.00024 | 128 | 98.00499 | 414.69708 | 40.32620 | 0.00711994 | +2.163e-09 |
| hllc | InvF_conservativeState_nx32_dt1.25e-07_TF0.00024 | 32 | 171.07184 | 514.62065 | 70.01753 | 0.0083015 | +2.806e-06 |
| hllc | InvF_conservativeState_nx64_dt6.25e-08_TF0.00024 | 64 | 130.34151 | 415.99410 | 43.60659 | 0.00815152 | +3.047e-08 |
| hllc | InvF_none_nx128_dt3.125e-08_TF0.00024 | 128 | 103.38058 | 402.44530 | 45.02650 | 0.00754801 | +2.163e-09 |
| hllc | InvF_none_nx32_dt1.25e-07_TF0.00024 | 32 | 157.06202 | 413.53631 | 46.74435 | 0.00863477 | +2.806e-06 |
| hllc | InvF_none_nx64_dt6.25e-08_TF0.00024 | 64 | 131.31967 | 420.16494 | 39.79295 | 0.00842927 | +3.047e-08 |

## Same-mesh time check

At nx128, dt=31.25 versus 15.625 ns gives T L1 1.30553 K,
T Linf 3.18060 K and U L1 2.41690 m/s.
This estimates one time-refinement difference; it is not a proof of
negligible time error at all meshes or later phases.
At nx256, dt=15.625 versus 7.8125 ns gives T L1 1.99894 K,
T Linf 4.86264 K and U L1 5.71120 m/s.
This estimates one time-refinement difference; it is not a proof of
negligible time error at all meshes or later phases.

## Interpretation

The central nx32/64/128 trajectories quenched; nx256/512 burned.
The contact-resolving HLLC trajectory burns at nx32 and on all executed
refinements. Its equal-property analytic-wave p/U errors are near roundoff,
while its T/species errors remain first order. The analytic central wave is
much more diffusive at the selected coarse meshes. This makes the central
coarse quenching a discretization-sensitive outcome, not independent
evidence of physical extinction. The known flux comparison isolates that
source of uncertainty without establishing which finest trajectory is exact.

The pressure candidates preserve energy/mass/elements within recorded
tolerances but show differing velocity and thermochemical profiles. Their
differences from both flux families must be judged alongside the references'
own mesh differences. Current evidence does not justify a precise reacting
accuracy/cost frontier, a resolved error floor, or a new-method claim.

Source: candidateStudy/data/processed/inviscid_cross_reference.json,
hllc_verification.json, central_verification.json and inviscid_summary.json.
All raw cases and failures remain retained. The figure
../figures/candidates/inviscid_reference_uncertainty.png is generated
from those data.
