# Known species enthalpy transport: reacting and coupled-face controls

The added periodic heat flux changes local transport. It cannot algebraically
remove the original post-pressure density/thermochemical energy defect.
The initial Mix MPI run caught an uncancelled coupled-face flux; it is
retained as a failed broader conservation control, even though its local
energy accounting was correct. Derived coefficient halo evaluation was
then changed and tested in distinct coupledSync cases.

Original kernel/B/Mix: Sutherland As=0, Ts=0. Nonzero tagged controls:
shared As=1.458e-6, Ts=110.4 K, same public NASA chemistry and geometry.
These coefficients define a numerical screen, not validated H2 diffusion.
Each case runs to 240 us. Wall times are single execution records and
are excluded from comparative performance claims.

| Group | Kind | dt (us) | Ranks | Method | Flux | E drift (%) | T mean (K) | Extra net (J) | Extra absolute space/time (J) | Cell closure (J) |
|---|---|---:|---:|---|---|---:|---:|---:|---:|---:|
| zero | F | 2 | 4 | none | off | -17.38866 | 2828.43233726 | +0.00000e+00 | 0.00000e+00 | 7.18284e-19 |
| zero | F | 2 | 4 | none | on | -17.38866 | 2828.43233726 | +0.00000e+00 | 0.00000e+00 | 7.18284e-19 |
| zero | F | 2 | 4 | conservativeState | off | -2.37951e-13 | 726.81294996 | +0.00000e+00 | 0.00000e+00 | 2.04512e-19 |
| zero | F | 2 | 4 | conservativeState | on | -2.37951e-13 | 726.81294996 | +0.00000e+00 | 0.00000e+00 | 2.04512e-19 |
| zero | F | 1 | 4 | none | off | +0.89329925 | 2846.04723062 | +0.00000e+00 | 0.00000e+00 | 7.26119e-19 |
| zero | F | 1 | 4 | none | on | +0.89329925 | 2846.04723062 | +0.00000e+00 | 0.00000e+00 | 7.26119e-19 |
| zero | F | 1 | 4 | conservativeState | off | +5.55219e-12 | 2844.69122784 | +0.00000e+00 | 0.00000e+00 | 1.27275e-17 |
| zero | F | 1 | 4 | conservativeState | on | +5.55219e-12 | 2844.69122784 | +0.00000e+00 | 0.00000e+00 | 1.27275e-17 |
| zero | Mix | 2 | 4 | none | off | +0.2815143 | 800.14247910 | +0.00000e+00 | 0.00000e+00 | 1.27862e-19 |
| zero | Mix | 2 | 4 | none | on | +0.2815143 | 800.14247910 | +0.00000e+00 | 0.00000e+00 | 1.27862e-19 |
| zero | Mix | 2 | 4 | conservativeState | off | -1.9126379e-13 | 799.48366643 | +0.00000e+00 | 0.00000e+00 | 1.36599e-19 |
| zero | Mix | 2 | 4 | conservativeState | on | -1.9126379e-13 | 799.48366643 | +0.00000e+00 | 0.00000e+00 | 1.36599e-19 |
| zero | B | 1 | 1 | none | off | -8.6007873e-05 | 2928.26272330 | +0.00000e+00 | 0.00000e+00 | 5.08000e-19 |
| zero | B | 1 | 1 | none | on | -8.6007873e-05 | 2928.26272330 | +0.00000e+00 | 0.00000e+00 | 5.08000e-19 |
| zero | B | 1 | 1 | conservativeState | off | +5.1178122e-11 | 2928.26079833 | +0.00000e+00 | 0.00000e+00 | 3.11960e-17 |
| zero | B | 1 | 1 | conservativeState | on | +5.1178122e-11 | 2928.26079833 | +0.00000e+00 | 0.00000e+00 | 3.11960e-17 |
| firstNonzero | F | 1 | 4 | none | off | +0.71643164 | 2845.89806665 | +0.00000e+00 | 0.00000e+00 | 9.73558e-19 |
| firstNonzero | F | 1 | 4 | none | on | +0.7161575 | 2845.89782272 | +8.71205e-24 | 1.42079e-06 | 7.53012e-19 |
| firstNonzero | F | 1 | 4 | conservativeState | off | +3.251997e-12 | 2844.69012120 | +0.00000e+00 | 0.00000e+00 | 1.50328e-17 |
| firstNonzero | F | 1 | 4 | conservativeState | on | +2.7364365e-12 | 2844.69015285 | -1.39914e-23 | 1.49074e-06 | 1.51816e-17 |
| firstNonzero | F | 0.5 | 4 | none | off | -21.77505 | 2821.80127310 | +0.00000e+00 | 0.00000e+00 | 8.67362e-19 |
| firstNonzero | F | 0.5 | 4 | none | on | -21.77592 | 2821.80034592 | +6.14790e-24 | 1.52521e-06 | 8.97855e-19 |
| firstNonzero | F | 0.5 | 4 | conservativeState | off | +1.7053155e-12 | 2844.79352778 | +0.00000e+00 | 0.00000e+00 | 4.13739e-17 |
| firstNonzero | F | 0.5 | 4 | conservativeState | on | +8.328285e-13 | 2844.79354384 | -6.26034e-24 | 1.60099e-06 | 4.01978e-17 |
| firstNonzero | Mix | 1 | 4 | none | off | +0.14200449 | 799.82497391 | +0.00000e+00 | 0.00000e+00 | 1.43638e-19 |
| firstNonzero | Mix | 1 | 4 | none | on | +0.14213841 | 799.82977844 | +1.78170e-10 | 6.80750e-06 | 1.40038e-19 |
| firstNonzero | Mix | 1 | 4 | conservativeState | off | -1.7387618e-14 | 799.49275595 | +0.00000e+00 | 0.00000e+00 | 1.37779e-19 |
| firstNonzero | Mix | 1 | 4 | conservativeState | on | +8.9292264e-07 | 799.49712935 | +1.78170e-10 | 6.80944e-06 | 1.55236e-19 |
| coupledSync | F | 1 | 4 | none | off | +0.71643164 | 2845.89806665 | +0.00000e+00 | 0.00000e+00 | 9.73558e-19 |
| coupledSync | F | 1 | 4 | none | on | +0.7161575 | 2845.89782272 | +8.71209e-24 | 1.42079e-06 | 7.53012e-19 |
| coupledSync | F | 1 | 4 | conservativeState | off | +3.251997e-12 | 2844.69012120 | +0.00000e+00 | 0.00000e+00 | 1.50328e-17 |
| coupledSync | F | 1 | 4 | conservativeState | on | +2.7364365e-12 | 2844.69015285 | -1.39914e-23 | 1.49074e-06 | 1.51816e-17 |
| coupledSync | F | 0.5 | 4 | none | off | -21.77505 | 2821.80127310 | +0.00000e+00 | 0.00000e+00 | 8.67362e-19 |
| coupledSync | F | 0.5 | 4 | none | on | -21.77592 | 2821.80034592 | +6.14788e-24 | 1.52521e-06 | 8.97855e-19 |
| coupledSync | F | 0.5 | 4 | conservativeState | off | +1.7053155e-12 | 2844.79352778 | +0.00000e+00 | 0.00000e+00 | 4.13739e-17 |
| coupledSync | F | 0.5 | 4 | conservativeState | on | +8.328285e-13 | 2844.79354384 | -6.26037e-24 | 1.60099e-06 | 4.01978e-17 |
| coupledSync | Mix | 1 | 4 | none | off | +0.14200449 | 799.82497391 | +0.00000e+00 | 0.00000e+00 | 1.43638e-19 |
| coupledSync | Mix | 1 | 4 | none | on | +0.14213752 | 799.82977513 | -1.64144e-23 | 6.80753e-06 | 1.55570e-19 |
| coupledSync | Mix | 1 | 4 | conservativeState | off | -1.7387618e-14 | 799.49275595 | +0.00000e+00 | 0.00000e+00 | 1.37779e-19 |
| coupledSync | Mix | 1 | 4 | conservativeState | on | -1.5648856e-13 | 799.49712602 | -9.05117e-23 | 6.80947e-06 | 1.52451e-19 |
| coupledSync | Mix | 1 | 1 | none | off | +0.14162778 | 799.82408648 | +0.00000e+00 | 0.00000e+00 | 1.35115e-19 |
| coupledSync | Mix | 1 | 1 | none | on | +0.14176081 | 799.82888768 | +2.07441e-24 | 6.80772e-06 | 1.48595e-19 |
| coupledSync | Mix | 1 | 1 | conservativeState | off | -3.9991521e-13 | 799.49275621 | +0.00000e+00 | 0.00000e+00 | 1.46921e-19 |
| coupledSync | Mix | 1 | 1 | conservativeState | on | -3.9991521e-13 | 799.49712629 | +1.07146e-23 | 6.80949e-06 | 1.35415e-19 |
| thermo2 | Mix | 1 | 4 | none | off | +0.14200449 | 799.82497391 | +0.00000e+00 | 0.00000e+00 | 1.43638e-19 |
| thermo2 | Mix | 1 | 4 | none | on | +0.14213752 | 799.82977513 | -1.64144e-23 | 6.80753e-06 | 1.55570e-19 |
| thermo2 | Mix | 1 | 4 | conservativeState | off | -1.7387618e-14 | 799.49275595 | +0.00000e+00 | 0.00000e+00 | 1.37779e-19 |
| thermo2 | Mix | 1 | 4 | conservativeState | on | -1.5648856e-13 | 799.49712602 | -9.05117e-23 | 6.80947e-06 | 1.52451e-19 |
| thermo2 | Mix | 1 | 1 | none | off | +0.14162778 | 799.82408648 | +0.00000e+00 | 0.00000e+00 | 1.35115e-19 |
| thermo2 | Mix | 1 | 1 | none | on | +0.14176081 | 799.82888768 | +2.07441e-24 | 6.80772e-06 | 1.48595e-19 |
| thermo2 | Mix | 1 | 1 | conservativeState | off | -3.9991521e-13 | 799.49275621 | +0.00000e+00 | 0.00000e+00 | 1.46921e-19 |
| thermo2 | Mix | 1 | 1 | conservativeState | on | -3.9991521e-13 | 799.49712629 | +1.07146e-23 | 6.80949e-06 | 1.35415e-19 |
| thermo4 | Mix | 1 | 4 | none | off | +0.14200449 | 799.82497391 | +0.00000e+00 | 0.00000e+00 | 1.49376e-19 |
| thermo4 | Mix | 1 | 4 | none | on | +0.14213752 | 799.82977513 | -4.10488e-23 | 6.80753e-06 | 1.40647e-19 |
| thermo4 | Mix | 1 | 4 | conservativeState | off | +3.4775235e-14 | 799.49275595 | +0.00000e+00 | 0.00000e+00 | 1.35477e-19 |
| thermo4 | Mix | 1 | 4 | conservativeState | on | -2.6081426e-13 | 799.49712602 | +1.33512e-23 | 6.80947e-06 | 1.47699e-19 |
| thermo4 | Mix | 1 | 1 | none | off | +0.14162778 | 799.82408648 | +0.00000e+00 | 0.00000e+00 | 1.55328e-19 |
| thermo4 | Mix | 1 | 1 | none | on | +0.14176081 | 799.82888768 | +8.62077e-24 | 6.80772e-06 | 1.49892e-19 |
| thermo4 | Mix | 1 | 1 | conservativeState | off | -3.3036474e-13 | 799.49275621 | +0.00000e+00 | 0.00000e+00 | 1.34949e-19 |
| thermo4 | Mix | 1 | 1 | conservativeState | on | -3.1297712e-13 | 799.49712629 | -1.54773e-23 | 6.80949e-06 | 1.63798e-19 |

## Field differences and reproducibility

| Comparison | Group | Case | T Linf (K) | p Linf (Pa) | rho Linf | U Linf (m/s) |
|---|---|---|---:|---:|---:|---:|
| fluxOnVersusOff | zero | F_none_dt2e-06_s1_g0_o1_p1_transportOn | 0 | 0 | 0 | 0 |
| fluxOnVersusOff | zero | F_conservativeState_dt2e-06_s1_g0_o1_p1_transportOn | 0 | 0 | 0 | 0 |
| fluxOnVersusOff | zero | F_none_dt1e-06_s1_g0_o1_p1_transportOn | 0 | 0 | 0 | 0 |
| fluxOnVersusOff | zero | F_conservativeState_dt1e-06_s1_g0_o1_p1_transportOn | 0 | 0 | 0 | 0 |
| fluxOnVersusOff | zero | Mix_none_dt2e-06_s1_g0_o1_p1_transportOn | 0 | 0 | 0 | 0 |
| fluxOnVersusOff | zero | Mix_conservativeState_dt2e-06_s1_g0_o1_p1_transportOn | 0 | 0 | 0 | 0 |
| fluxOnVersusOff | zero | B_none_dt1e-06_s1_g0_o1_p1_transportOn | 0 | 0 | 0 | 0 |
| fluxOnVersusOff | zero | B_conservativeState_dt1e-06_s1_g0_o1_p1_transportOn | 0 | 0 | 0 | 0 |
| fluxOnVersusOff | firstNonzero | F_none_dt1e-06_s1_g0_o1_p1_transportOn_nonzeroSutherland | 0.00133965 | 0.112181 | 1.85664e-07 | 0.000210394 |
| fluxOnVersusOff | firstNonzero | F_conservativeState_dt1e-06_s1_g0_o1_p1_transportOn_nonzeroSutherland | 0.00139274 | 0.0214159 | 2.34312e-07 | 0.000180701 |
| fluxOnVersusOff | firstNonzero | F_none_dt5e-07_s1_g0_o1_p1_transportOn_nonzeroSutherland | 0.00634106 | 2.40802 | 1.83419e-06 | 0.00665864 |
| fluxOnVersusOff | firstNonzero | F_conservativeState_dt5e-07_s1_g0_o1_p1_transportOn_nonzeroSutherland | 0.000897063 | 0.110963 | 1.8082e-07 | 0.000265566 |
| fluxOnVersusOff | firstNonzero | Mix_none_dt1e-06_s1_g0_o1_p1_transportOn_nonzeroSutherland | 0.142258 | 0.0752039 | 2.83668e-05 | 0.00145664 |
| fluxOnVersusOff | firstNonzero | Mix_conservativeState_dt1e-06_s1_g0_o1_p1_transportOn_nonzeroSutherland | 0.142599 | 0.00359197 | 2.84904e-05 | 0.00144316 |
| fluxOnVersusOff | coupledSync | F_none_dt1e-06_s1_g0_o1_p1_transportOn_nonzeroSutherland_coupledSync | 0.00133965 | 0.112181 | 1.85664e-07 | 0.000210394 |
| fluxOnVersusOff | coupledSync | F_conservativeState_dt1e-06_s1_g0_o1_p1_transportOn_nonzeroSutherland_coupledSync | 0.00139274 | 0.0214159 | 2.34312e-07 | 0.000180701 |
| fluxOnVersusOff | coupledSync | F_none_dt5e-07_s1_g0_o1_p1_transportOn_nonzeroSutherland_coupledSync | 0.00634106 | 2.40802 | 1.83419e-06 | 0.00665864 |
| fluxOnVersusOff | coupledSync | F_conservativeState_dt5e-07_s1_g0_o1_p1_transportOn_nonzeroSutherland_coupledSync | 0.000897063 | 0.110963 | 1.8082e-07 | 0.000265566 |
| fluxOnVersusOff | coupledSync | Mix_none_dt1e-06_s1_g0_o1_p1_transportOn_nonzeroSutherland_coupledSync | 0.142255 | 0.074782 | 2.83665e-05 | 0.0014566 |
| fluxOnVersusOff | coupledSync | Mix_conservativeState_dt1e-06_s1_g0_o1_p1_transportOn_nonzeroSutherland_coupledSync | 0.142596 | 0.00401296 | 2.84907e-05 | 0.00144314 |
| fluxOnVersusOff | coupledSync | Mix_none_dt1e-06_s1_g0_o1_p1_transportOn_nonzeroSutherland_coupledSync_serial | 0.142258 | 0.0747814 | 2.83657e-05 | 0.00145657 |
| fluxOnVersusOff | coupledSync | Mix_conservativeState_dt1e-06_s1_g0_o1_p1_transportOn_nonzeroSutherland_coupledSync_serial | 0.142597 | 0.00401298 | 2.84907e-05 | 0.00144314 |
| fluxOnVersusOff | thermo2 | Mix_none_dt1e-06_s1_g0_o1_p1_transportOn_nonzeroSutherland_coupledSync_thermo2 | 0.142255 | 0.074782 | 2.83665e-05 | 0.0014566 |
| fluxOnVersusOff | thermo2 | Mix_conservativeState_dt1e-06_s1_g0_o1_p1_transportOn_nonzeroSutherland_coupledSync_thermo2 | 0.142596 | 0.00401296 | 2.84907e-05 | 0.00144314 |
| fluxOnVersusOff | thermo2 | Mix_none_dt1e-06_s1_g0_o1_p1_transportOn_nonzeroSutherland_coupledSync_thermo2_serial | 0.142258 | 0.0747814 | 2.83657e-05 | 0.00145657 |
| fluxOnVersusOff | thermo2 | Mix_conservativeState_dt1e-06_s1_g0_o1_p1_transportOn_nonzeroSutherland_coupledSync_thermo2_serial | 0.142597 | 0.00401298 | 2.84907e-05 | 0.00144314 |
| fluxOnVersusOff | thermo4 | Mix_none_dt1e-06_s1_g0_o1_p1_transportOn_nonzeroSutherland_coupledSync_thermo4 | 0.142255 | 0.074782 | 2.83665e-05 | 0.0014566 |
| fluxOnVersusOff | thermo4 | Mix_conservativeState_dt1e-06_s1_g0_o1_p1_transportOn_nonzeroSutherland_coupledSync_thermo4 | 0.142596 | 0.00401296 | 2.84907e-05 | 0.00144314 |
| fluxOnVersusOff | thermo4 | Mix_none_dt1e-06_s1_g0_o1_p1_transportOn_nonzeroSutherland_coupledSync_thermo4_serial | 0.142258 | 0.0747814 | 2.83657e-05 | 0.00145657 |
| fluxOnVersusOff | thermo4 | Mix_conservativeState_dt1e-06_s1_g0_o1_p1_transportOn_nonzeroSutherland_coupledSync_thermo4_serial | 0.142597 | 0.00401298 | 2.84907e-05 | 0.00144314 |
| serialParallel | coupledSync | Mix_none_dt1e-06_s1_g0_o1_p1_transportOff_nonzeroSutherland_coupledSync | 0.00158744 | 0.257263 | 7.43828e-07 | 3.05478e-05 |
| serialParallel | coupledSync | Mix_none_dt1e-06_s1_g0_o1_p1_transportOn_nonzeroSutherland_coupledSync | 0.00159441 | 0.257264 | 7.45496e-07 | 3.0568e-05 |
| serialParallel | coupledSync | Mix_conservativeState_dt1e-06_s1_g0_o1_p1_transportOff_nonzeroSutherland_coupledSync | 1.67149e-05 | 2.45207e-05 | 8.55178e-09 | 2.16548e-06 |
| serialParallel | coupledSync | Mix_conservativeState_dt1e-06_s1_g0_o1_p1_transportOn_nonzeroSutherland_coupledSync | 1.67524e-05 | 2.4491e-05 | 8.57667e-09 | 2.15962e-06 |
| serialParallel | thermo2 | Mix_none_dt1e-06_s1_g0_o1_p1_transportOff_nonzeroSutherland_coupledSync_thermo2 | 0.00158744 | 0.257263 | 7.43828e-07 | 3.05478e-05 |
| serialParallel | thermo2 | Mix_none_dt1e-06_s1_g0_o1_p1_transportOn_nonzeroSutherland_coupledSync_thermo2 | 0.00159441 | 0.257264 | 7.45496e-07 | 3.0568e-05 |
| serialParallel | thermo2 | Mix_conservativeState_dt1e-06_s1_g0_o1_p1_transportOff_nonzeroSutherland_coupledSync_thermo2 | 1.67149e-05 | 2.45207e-05 | 8.55178e-09 | 2.16548e-06 |
| serialParallel | thermo2 | Mix_conservativeState_dt1e-06_s1_g0_o1_p1_transportOn_nonzeroSutherland_coupledSync_thermo2 | 1.67524e-05 | 2.4491e-05 | 8.57667e-09 | 2.15962e-06 |
| serialParallel | thermo4 | Mix_none_dt1e-06_s1_g0_o1_p1_transportOff_nonzeroSutherland_coupledSync_thermo4 | 0.00158744 | 0.257263 | 7.43828e-07 | 3.05478e-05 |
| serialParallel | thermo4 | Mix_none_dt1e-06_s1_g0_o1_p1_transportOn_nonzeroSutherland_coupledSync_thermo4 | 0.00159441 | 0.257264 | 7.45496e-07 | 3.0568e-05 |
| serialParallel | thermo4 | Mix_conservativeState_dt1e-06_s1_g0_o1_p1_transportOff_nonzeroSutherland_coupledSync_thermo4 | 1.67149e-05 | 2.45204e-05 | 8.55177e-09 | 2.16548e-06 |
| serialParallel | thermo4 | Mix_conservativeState_dt1e-06_s1_g0_o1_p1_transportOn_nonzeroSutherland_coupledSync_thermo4 | 1.67524e-05 | 2.44909e-05 | 8.57667e-09 | 2.15962e-06 |

The G serial/four-rank T Linf discrepancy is about 1.675e-5 K, with
or without the added flux. Four thermo passes instead of the inherited
two do not reduce it below the predeclared 1e-6 K threshold. The first
thermo2 tag duplicates the factory setting and is not extra-inversion
evidence. The inversion hypothesis is rejected for this contrast; the
remaining partition discrepancy is reported, not attributed to a cause
or claimed to be roundoff. A strict field-equivalence gate remains open.

Exact inputs, native source snapshots, executable hashes, independent NASA
and native inventories, and full ledgers are stored per case. The new
flux is fixed at post-species composition and predictor p/T through the
energy inversion. This control adds no matrix equation but does add
derived-coefficient halo exchanges; no zero-cost claim follows.

The original two-outer benchmark, finer dt benchmarks and independent
central/HLLC uncertainty comparisons remain separate evidence. A successful
known heat-flux control does not change their novelty or reacting accuracy
gate decisions.
