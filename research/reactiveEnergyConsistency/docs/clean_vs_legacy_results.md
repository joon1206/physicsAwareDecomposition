# Clean versus legacy thermochemistry

The original pressure/density/enthalpy defect survives continuous thermochemistry. The direct breakpoint source floor is removed, while a small number of spatial source failures remain under the unchanged 1e-10 criterion. Therefore continuity repair alone is not a complete source-integration or CFD correction.

This report currently includes 18 completed matched H2 attribution records (18 planned including reused legacy controls), 18 direct native controls, and 90 independent CV/physical-CP trajectories. It reports completed runs only; pending cases are not interpreted.

The kinetic input text, low/reference thermo, transport, initial T/p/U/species, grid, Euler/upwind discretization and source settings are held fixed within each matched pair. Changing entropy/enthalpy affects equilibrium-derived reverse rates; this is an unavoidable thermochemistry-driven trajectory interaction. No original run or accepted source is edited. The original transport remains As=Ts=0.

## Endpoint and local attribution

| Source | Closure | dt (us) | Thermo | Energy drift (%) | Mean T (K) | rho hs + rho hc (J) | Source fails / calls |
|---|---|---|---|---|---|---|---|
| native | none | 2.0 | legacy | -17.388659758 | 2828.432337256 | -3.2478627044e-03 | unobserved / unobserved |
| native | none | 2.0 | HS | -17.390004673 | 2828.430400330 | -3.2481211751e-03 | unobserved / unobserved |
| native | none | 2.0 | CpHS | -17.390027162 | 2828.430770610 | -3.2481248697e-03 | unobserved / unobserved |
| native | none | 1.0 | legacy | +0.893299251 | 2846.047230623 | +1.6706819260e-04 | unobserved / unobserved |
| native | none | 1.0 | HS | +0.893251299 | 2846.046573401 | +1.6705986166e-04 | unobserved / unobserved |
| native | none | 1.0 | CpHS | +0.893236663 | 2846.046946498 | +1.6705738456e-04 | unobserved / unobserved |
| CV | none | 2.0 | legacy | -23.137932495 | 2822.851698445 | -4.3124994360e-03 | 151 / 30720 |
| CV | none | 2.0 | HS | -23.136900311 | 2822.852301648 | -4.3122911528e-03 | 10 / 30720 |
| CV | none | 2.0 | CpHS | -23.136964347 | 2822.852629234 | -4.3123029490e-03 | 9 / 30720 |
| CV | conservativeState | 2.0 | legacy | -0.000000000 | 727.822788169 | +1.2387620199e-03 | 0 / 30720 |
| CV | conservativeState | 2.0 | HS | -0.000000000 | 727.831234558 | +1.2387720972e-03 | 0 / 30720 |
| CV | conservativeState | 2.0 | CpHS | -0.000000000 | 727.830817062 | +1.2387713647e-03 | 0 / 30720 |
| CV | none | 1.0 | legacy | -1.991142504 | 2843.428619831 | -3.3177598814e-04 | 192 / 61440 |
| CV | none | 1.0 | HS | -1.990371428 | 2843.428732920 | -3.3163891295e-04 | 3 / 61440 |
| CV | none | 1.0 | CpHS | -1.990475832 | 2843.429021812 | -3.3165713344e-04 | 5 / 61440 |
| CV | conservativeState | 1.0 | legacy | +0.000000000 | 2844.741557324 | -3.1958985815e-05 | 240 / 61440 |
| CV | conservativeState | 1.0 | HS | +0.000000000 | 2844.740982885 | -3.2064239854e-05 | 0 / 61440 |
| CV | conservativeState | 1.0 | CpHS | +0.000000000 | 2844.741370752 | -3.2061503676e-05 | 0 / 61440 |

Native costOde source endpoints were not traced; its cellwise species/Qdot identity is measured. CV source entries test the actual accepted endpoint energy with J/m3 units and the original relative denominator max(|E_initial|,1 J/m3). The source diagnostic is separate from the CFD ledger and must not be added again as external heat.

## native, dt=2 us: same eight-term budget

| Quantity (J) | legacy | HS | CpHS |
|---|---|---|---|
| Dpressure | -7.892729675088e-07 | -7.891883141462e-07 | -7.891863420434e-07 |
| Dkinetic | +2.062272817862e-04 | +2.062504345681e-04 | +2.062503829639e-04 |
| DrhoH | +8.887525315043e-03 | +8.887762518257e-03 | +8.887749126549e-03 |
| DrhoC | -1.213538801949e-02 | -1.213588369337e-02 | -1.213587399629e-02 |
| DspeciesChemistry | -2.496397388904e-13 | -2.493675874669e-13 | -2.496133506372e-13 |
| Dequation | -3.952695948328e-16 | -1.464952603669e-16 | -1.244160330316e-17 |
| Dtransport | -1.644747904225e-09 | -1.644747820930e-09 | -1.644748096502e-09 |
| Dhistory | +6.223235766772e-17 | -3.229524869644e-18 | +2.903734822306e-17 |
| Endpoint change | -3.042426340625e-03 | -3.042661573855e-03 | -3.042665318114e-03 |
| Max step closure | 1.4468e-16 | 1.4976e-16 | 1.3770e-16 |
| Max cell closure | 7.1828e-19 | 7.4634e-19 | 7.2532e-19 |

## native, dt=1 us: same eight-term budget

| Quantity (J) | legacy | HS | CpHS |
|---|---|---|---|
| Dpressure | -3.474218888752e-07 | -3.474318253733e-07 | -3.474274332769e-07 |
| Dkinetic | -1.042284371700e-05 | -1.042289691409e-05 | -1.042299483234e-05 |
| DrhoH | +6.445248798680e-03 | +6.445287297603e-03 | +6.445292191401e-03 |
| DrhoC | -6.278180606077e-03 | -6.278227435946e-03 | -6.278234806842e-03 |
| DspeciesChemistry | -1.251614022746e-13 | -1.250225777902e-13 | -1.252275402782e-13 |
| Dequation | +1.672791460905e-15 | +1.690557582812e-15 | +1.580272579460e-15 |
| Dtransport | -8.223748232556e-10 | -8.223748964077e-10 | -8.223747656435e-10 |
| Dhistory | +9.185489977822e-18 | -1.567164477142e-17 | -4.909911182054e-17 |
| Endpoint change | +1.562971044984e-04 | +1.562887104183e-04 | +1.562861397941e-04 |
| Max step closure | 1.2251e-16 | 1.6324e-16 | 1.3267e-16 |
| Max cell closure | 7.2612e-19 | 7.3522e-19 | 7.1087e-19 |

## CV, dt=2 us: same eight-term budget

| Quantity (J) | legacy | HS | CpHS |
|---|---|---|---|
| Dpressure | -7.801094153967e-07 | -7.798959931891e-07 | -7.798958554847e-07 |
| Dkinetic | +2.649269027262e-04 | +2.648991114765e-04 | +2.648999568486e-04 |
| DrhoH | +7.174498527215e-03 | +7.175618942595e-03 | +7.175589125209e-03 |
| DrhoC | -1.148699796323e-02 | -1.148791009538e-02 | -1.148789207419e-02 |
| DspeciesChemistry | -2.506923162495e-13 | -2.506304325634e-13 | -2.508523540273e-13 |
| Dequation | -1.271651894896e-15 | +5.016038695516e-16 | +1.068639843282e-15 |
| Dtransport | -1.644745816753e-09 | -1.644747940565e-09 | -1.644748139615e-09 |
| Dhistory | +5.669625620358e-17 | -2.772561182512e-17 | +4.762283927260e-17 |
| Endpoint change | -4.048354287698e-03 | -4.048173582296e-03 | -4.048184532981e-03 |
| Max step closure | 1.0725e-16 | 1.2882e-16 | 1.2821e-16 |
| Max cell closure | 8.0722e-19 | 7.2506e-19 | 7.2845e-19 |

## CV, dt=1 us: same eight-term budget

| Quantity (J) | legacy | HS | CpHS |
|---|---|---|---|
| Dpressure | -1.079279552286e-07 | -1.079300977540e-07 | -1.079246797213e-07 |
| Dkinetic | -1.649774087078e-05 | -1.649989256313e-05 | -1.649992269874e-05 |
| DrhoH | +6.594900533119e-03 | +6.594867743876e-03 | +6.594866296947e-03 |
| DrhoC | -6.926676521261e-03 | -6.926506656831e-03 | -6.926523430384e-03 |
| DspeciesChemistry | -1.247560815899e-13 | -1.254738756047e-13 | -1.249223288531e-13 |
| Dequation | -2.369141549607e-16 | +1.942936339594e-15 | +1.722410353233e-15 |
| Dtransport | -8.223728076828e-10 | -8.223744836109e-10 | -8.223744187618e-10 |
| Dhistory | +1.557270073527e-17 | +4.320656830429e-17 | -2.382142521299e-17 |
| Endpoint change | -3.483824794664e-04 | -3.482475581134e-04 | -3.482658033142e-04 |
| Max step closure | 1.1059e-16 | 1.2840e-16 | 1.2785e-16 |
| Max cell closure | 7.0849e-19 | 7.5471e-19 | 7.0283e-19 |

## Unchanged spatial source gate

| Thermo | Failed CV calls | Total CV calls | Largest relative energy change |
|---|---|---|---|
| legacy | 583 | 184320 | 3.28292948e-07 |
| HS | 13 | 184320 | 8.00856654e-10 |
| CpHS | 14 | 184320 | 5.51149526e-10 |

Each completed thermo row combines the same four CV configurations (two timesteps and two coupling modes). All use the unchanged 1e-10 relative source-energy gate. Native costOde endpoint source energy is not traced and is not included in these totals. The successful removal of the direct breakpoint floor does not turn the remaining failures into passes.

## Finite chemistry transfer and conservative-state ledger

| Source | Mode | dt (us) | Thermo | Dchemistry (J) | Max source relative error |
|---|---|---|---|---|---|
| native | none | 2.0 | legacy | +1.14284661e-18 | not traced |
| native | none | 2.0 | HS | -2.71157093e-19 | not traced |
| native | none | 2.0 | CpHS | +2.96079112e-18 | not traced |
| native | none | 1.0 | legacy | -7.14445601e-19 | not traced |
| native | none | 1.0 | HS | +1.50394801e-18 | not traced |
| native | none | 1.0 | CpHS | -1.86497715e-18 | not traced |
| CV | none | 2.0 | legacy | +9.28239543e-19 | 2.76094831e-07 |
| CV | none | 2.0 | HS | -5.11853608e-19 | 8.00856654e-10 |
| CV | none | 2.0 | CpHS | -1.54601727e-18 | 5.51149526e-10 |
| CV | conservativeState | 2.0 | legacy | -5.57061241e-21 | 9.77861216e-15 |
| CV | conservativeState | 2.0 | HS | -6.85179883e-22 | 9.29330971e-15 |
| CV | conservativeState | 2.0 | CpHS | +7.65573937e-21 | 7.85644158e-15 |
| CV | none | 1.0 | legacy | +1.16238797e-19 | 2.95255564e-07 |
| CV | none | 1.0 | HS | +1.35910629e-18 | 5.95339865e-10 |
| CV | none | 1.0 | CpHS | -4.58207678e-19 | 4.40237532e-10 |
| CV | conservativeState | 1.0 | legacy | -2.50065163e-19 | 3.28292948e-07 |
| CV | conservativeState | 1.0 | HS | +1.52213102e-18 | 9.67161757e-11 |
| CV | conservativeState | 1.0 | CpHS | +8.61142277e-19 | 3.45696508e-11 |

Dchemistry is the finite formation-transfer cancellation in the CFD equations. It is distinct from the absolute-energy residual of a standalone chemistry state. An algebraically consistent RR/Qdot pair can coexist with an inaccurate thermodynamic state or later coupling defect.

### Corrected CV ledger, dt=2 us

| Quantity (J) | legacy | HS | CpHS |
|---|---|---|---|
| Dpressure | -2.7730759743e-07 | -2.7746953754e-07 | -2.7746161104e-07 |
| Dkinetic | -1.1764044974e-05 | -1.1763628793e-05 | -1.1763649759e-05 |
| DrhoH | +1.3334639420e-03 | +1.3334979991e-03 | +1.3334961517e-03 |
| DrhoC | -9.4701922175e-05 | -9.4725901903e-05 | -9.4724787013e-05 |
| Dchemistry | -5.5706124085e-21 | -6.8517988325e-22 | +7.6557393650e-21 |
| DspeciesTransport | -2.5239944330e-13 | -2.5239952518e-13 | -2.5239949631e-13 |
| DspeciesResidual | +3.8013875510e-17 | +3.7469046390e-17 | +3.7569750588e-17 |
| Dequation | -5.3389947493e-17 | -4.6440219574e-17 | -6.2540094187e-17 |
| Dtransport | -1.6447451498e-09 | -1.6447451527e-09 | -1.6447451586e-09 |
| Dhistory | +0.0000000000e+00 | +0.0000000000e+00 | +0.0000000000e+00 |
| DpostH | -1.3214209447e-03 | -1.3214552560e-03 | -1.3214533956e-03 |
| DpostC | +9.4701922428e-05 | +9.4725902155e-05 | +9.4724787265e-05 |
| Endpoint change | -6.9388939039e-18 | -3.4694469520e-18 | -4.1633363423e-17 |
| Max cell closure | 2.0599e-19 | 2.4722e-19 | 2.6554e-19 |

### Corrected CV ledger, dt=1 us

| Quantity (J) | legacy | HS | CpHS |
|---|---|---|---|
| Dpressure | -6.4834821900e-07 | -6.4829927986e-07 | -6.4829629752e-07 |
| Dkinetic | -1.5621321288e-05 | -1.5623849453e-05 | -1.5623755379e-05 |
| DrhoH | +6.1155201180e-03 | +6.1156322663e-03 | +6.1156312512e-03 |
| DrhoC | -6.1474791038e-03 | -6.1476965061e-03 | -6.1476927549e-03 |
| Dchemistry | -2.5006516348e-19 | +1.5221310216e-18 | +8.6114227721e-19 |
| DspeciesTransport | -1.2616622633e-13 | -1.2617197828e-13 | -1.2619124679e-13 |
| DspeciesResidual | +2.0670972088e-15 | +2.0665852626e-15 | +2.0875034295e-15 |
| Dequation | -8.7996627212e-17 | -1.3528113826e-16 | -1.1214525804e-16 |
| Dtransport | -8.2237262491e-10 | -8.2237261743e-10 | -8.2237259445e-10 |
| Dhistory | +0.0000000000e+00 | +0.0000000000e+00 | +0.0000000000e+00 |
| DpostH | -6.0992496262e-03 | -6.0993592951e-03 | -6.0993583772e-03 |
| DpostC | +6.1474791040e-03 | +6.1476965062e-03 | +6.1476927550e-03 |
| Endpoint change | +2.9143354396e-16 | +8.5348395018e-16 | +8.1185058676e-16 |
| Max cell closure | 1.5639e-17 | 1.5303e-17 | 1.6704e-17 |

## GRI: independently matched full-flow controls

The identical GRI kinetics and initial fields are retained within each legacy/CpHS pair. This tests generalization of the coupling attribution; its different kinetics and constants prevent using H2-versus-GRI drift as a thermo-only difference.

| dt (us) | Thermo | Energy drift (%) | rho hs (J) | rho hc (J) | Mean T (K) | Max step closure (J) |
|---|---|---|---|---|---|---|
| 2.0 | legacy | +7.250802258 | +1.29125236e-03 | -9.21924060e-06 | 720.815134 | 2.1128e-17 |
| 2.0 | CpHS | +7.250802348 | +1.29125238e-03 | -9.21921258e-06 | 720.815134 | 1.8243e-17 |
| 1.0 | legacy | +3.954543924 | +7.21503852e-04 | -1.26388563e-05 | 716.088896 | 1.7565e-17 |
| 1.0 | CpHS | +3.954543871 | +7.21503819e-04 | -1.26388130e-05 | 716.088883 | 2.0902e-17 |

### GRI dt=2 us: eight-term budget

| Quantity (J) | legacy | CpHS |
|---|---|---|
| Dpressure | -7.360439311881e-07 | -7.360441169821e-07 |
| Dkinetic | -1.221471326815e-05 | -1.221471339274e-05 |
| DrhoH | +1.291252359226e-03 | +1.291252380478e-03 |
| DrhoC | -9.219240599459e-06 | -9.219212584380e-06 |
| DspeciesChemistry | -1.446912069742e-13 | -1.446919803641e-13 |
| Dequation | +8.618812330496e-16 | +8.540865792384e-16 |
| Dtransport | -1.645300934564e-09 | -1.645300940331e-09 |
| Dhistory | -1.519238294195e-17 | -1.436567878543e-18 |
| Endpoint change | +1.269080715982e-03 | +1.269080764939e-03 |

### GRI dt=1 us: eight-term budget

| Quantity (J) | legacy | CpHS |
|---|---|---|
| Dpressure | -3.520173473026e-07 | -3.520169389413e-07 |
| Dkinetic | -1.636316941150e-05 | -1.636317066483e-05 |
| DrhoH | +7.215038522948e-04 | +7.215038187066e-04 |
| DrhoC | -1.263885626690e-05 | -1.263881300660e-05 |
| DspeciesChemistry | -7.234601481962e-14 | -7.234730671730e-14 |
| Dequation | +6.099121208081e-16 | +6.454001777456e-16 |
| Dtransport | -8.226507181669e-10 | -8.226507357642e-10 |
| Dhistory | -7.169286865560e-18 | -9.486769009248e-18 |
| Endpoint change | +6.921489865464e-04 | +6.921489953736e-04 |

## Source invariants and independent checks

| Constraint / mechanism | T0 | rtol | Invariant change (relative) | Jump-subtracted remainder |
|---|---|---|---|---|
| CV / legacy | 999.0 | 1e-12 | 1.14604431e-07 | 8.17407379e-14 |
| CV / legacy | 1100.0 | 1e-12 | 9.58786500e-13 | 9.58786500e-13 |
| CV / legacy | 1500.0 | 1e-12 | 8.66575212e-14 | 8.66575212e-14 |
| CP / legacy | 999.0 | 1e-12 | 7.10122846e-08 | 1.33748139e-14 |
| CP / legacy | 1100.0 | 1e-12 | 1.11085103e-13 | 1.11085103e-13 |
| CP / legacy | 1500.0 | 1e-12 | 3.09497488e-14 | 3.09497488e-14 |
| CV / HS | 999.0 | 1e-12 | 1.59248037e-12 | 1.55719084e-12 |
| CV / HS | 1100.0 | 1e-12 | 8.64874597e-13 | 8.64874597e-13 |
| CV / HS | 1500.0 | 1e-12 | 4.63617766e-12 | 4.63617766e-12 |
| CP / HS | 999.0 | 1e-12 | 1.87432324e-12 | 1.85251707e-12 |
| CP / HS | 1100.0 | 1e-12 | 1.13799231e-13 | 1.13799231e-13 |
| CP / HS | 1500.0 | 1e-12 | 2.42544980e-14 | 2.42544980e-14 |
| CV / CpHS | 999.0 | 1e-12 | 6.96687657e-14 | 3.45328143e-14 |
| CV / CpHS | 1100.0 | 1e-12 | 9.17623965e-13 | 9.17623965e-13 |
| CV / CpHS | 1500.0 | 1e-12 | 8.25487913e-14 | 8.25487913e-14 |
| CP / CpHS | 999.0 | 1e-12 | 3.23409139e-14 | 1.06298772e-14 |
| CP / CpHS | 1100.0 | 1e-12 | 1.04687545e-13 | 1.04687545e-13 |
| CP / CpHS | 1500.0 | 1e-12 | 3.44868719e-14 | 3.44868719e-14 |
| CV / GRI | 999.0 | 1e-12 | 2.16137570e-07 | 1.64416629e-12 |
| CV / GRI | 1100.0 | 1e-12 | 2.16892287e-12 | 2.16892287e-12 |
| CV / GRI | 1500.0 | 1e-12 | 2.24138730e-13 | 2.24138730e-13 |
| CP / GRI | 999.0 | 1e-12 | 1.33908206e-07 | 9.64634520e-13 |
| CP / GRI | 1100.0 | 1e-12 | 5.16989868e-13 | 5.16989868e-13 |
| CP / GRI | 1500.0 | 1e-12 | 8.91928802e-14 | 8.91928802e-14 |
| CV / Alzueta | 999.0 | 1e-12 | 6.59221231e-11 | 6.01060577e-13 |
| CV / Alzueta | 1100.0 | 1e-12 | 1.22763581e-12 | 1.22763581e-12 |
| CV / Alzueta | 1500.0 | 1e-12 | 5.36825471e-12 | 5.36825471e-12 |
| CP / Alzueta | 999.0 | 1e-12 | 4.03446256e-11 | 2.39015235e-13 |
| CP / Alzueta | 1100.0 | 1e-12 | 4.39035263e-13 | 4.39035263e-13 |
| CP / Alzueta | 1500.0 | 1e-12 | 3.74135477e-14 | 3.74135477e-14 |

Direct native HS/CpHS controls cross 1000 K from 999 K without the persistent legacy 1.146e-7 floor. Independent Cantera confirms removal. The remaining native spatial failures for continuous data are retained, including calls wholly above 1000 K. Endpoint noncrossing still cannot exclude internal excursions; the trace does not uniquely resolve stage error. The full CpHS control removes Cp jumps to floating precision but does not make an adaptive ODE tolerance a certified nonlinear energy-invariant tolerance.

## Hierarchical attribution and measured interaction

These are distinct mechanisms with interacting trajectories. The source jump follows an event identity in 0D and disappears under matched continuity controls. The CFD density pair remains after that change. Local reactor and global CFD normalizations differ and are not directly subtracted.

The exact eight-term identity is additive within a particular executed CFD trajectory. A thermo-only difference is an intervention that changes temperature, density, rates and all subsequent operators. It cannot be universally assigned as an independent additive E_data term on the original trajectory. For a two-factor comparison, define I=[D(clean,G)−D(legacy,G)]−[D(clean,none)−D(legacy,none)] with all four D measured in joules. Nonzero I records the data/coupling interaction; it is not an unmeasured residual category. The conservative closure also has DpostH/DpostC in its corrected-state identity, reported above rather than silently forced into the unmodified eight terms.

| dt (us) | Clean control | Quantity | Measured interaction (J) |
|---|---|---|---|
| 2.0 | HS | Endpoint change | -1.807054015e-07 |
| 2.0 | HS | Dpressure | -3.753623188e-10 |
| 2.0 | HS | Dkinetic | +2.820743079e-08 |
| 2.0 | HS | DrhoH | -1.086358344e-06 |
| 2.0 | HS | DrhoC | +8.881524236e-07 |
| 2.0 | HS | DpostH | -3.431127721e-08 |
| 2.0 | HS | DpostC | +2.397972725e-08 |
| 2.0 | CpHS | Endpoint change | -1.697547162e-07 |
| 2.0 | CpHS | Dpressure | -3.675735366e-10 |
| 2.0 | CpHS | Dkinetic | +2.734109283e-08 |
| 2.0 | CpHS | DrhoH | -1.058388345e-06 |
| 2.0 | CpHS | DrhoC | +8.712461222e-07 |
| 2.0 | CpHS | DpostH | -3.245085025e-08 |
| 2.0 | CpHS | DpostC | +2.286483746e-08 |
| 1.0 | HS | Endpoint change | -1.349213524e-07 |
| 1.0 | HS | Dpressure | +5.108167107e-11 |
| 1.0 | HS | Dkinetic | -3.764723453e-10 |
| 1.0 | HS | DrhoH | +1.449374637e-07 |
| 1.0 | HS | DrhoC | -3.872666906e-07 |
| 1.0 | HS | DpostH | -1.096689952e-07 |
| 1.0 | HS | DpostC | +2.174022510e-07 |
| 1.0 | CpHS | Endpoint change | -1.166761516e-07 |
| 1.0 | CpHS | Dpressure | +4.864596630e-11 |
| 1.0 | CpHS | Dkinetic | -2.522633401e-10 |
| 1.0 | CpHS | DrhoH | +1.453693404e-07 |
| 1.0 | CpHS | DrhoC | -3.667419057e-07 |
| 1.0 | CpHS | DpostH | -1.087509985e-07 |
| 1.0 | CpHS | DpostC | +2.136510293e-07 |

The hierarchy is data-event identity in 0D, chemistry integration residual under fixed data, algebraic finite source cancellation, then executed CFD operator budget. Only measured interventions supply cross-effect estimates. This establishes a surviving coupling mechanism, not statistical independence or a universal additive taxonomy.

## Candidate cycles after the mandatory deliverable

The initial completed-control report preceded the valid-data projection prototype. The subsequent 48-case scalar baseline and five-family decisions are reported in invariant_projection_results.md, finite_source_map_results.md and thermochemical_risk_results.md. Generic projection novelty, unconditional accuracy dominance, finite-RR novelty, interface sufficiency, mechanism-only certification and physical-accuracy repair claims fail their stated gates. No new correction is promoted. Pressure/transport coupling with resolved accuracy remains the relevant research pivot.

## Trusted mechanism scope

Installed GRI has both full-flow matched controls and independent Cantera replay. The independently distributed Alzueta 2023 baseline is audited and its CV/physical-CP trajectories are retained. Fourteen native export attempts preserve every parser failure: quoted comments/CRLF, global thermo header/width, element case, then the substantive unsupported PLOG reaction form. Dropping PLOG would change kinetics and is not done. Native modern full-flow validation is therefore unavailable in this v2012 reader; the independent mechanism is used in the source hierarchy.

## Provenance and decision

Machine-readable tables: clean_thermo_campaign.json, clean_gri_campaign.json, clean_thermo_branch.json, clean_thermo_reference.json, clean_thermo_interactions.json and mechanism_continuity_audit.json. Inputs, native source/library/executable snapshots and raw rank traces are retained. Historical 38 evidence criteria and 499 frozen actionStudy files remain protected. Source failures and parser failures are not relabeled as publication successes. No claim of physical source-data accuracy, universal independence, solved local reacting accuracy or publication-gate survival follows.
