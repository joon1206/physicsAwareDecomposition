# Invariant projection on continuous thermochemistry

48 controls: 40 scalar recoveries eligible, 38 pass all declared endpoint gates, 25 eligible recoveries worsen temperature error. Eight GRI states have tiny negative provisional mass fractions (largest magnitude 2.465e-23); strict nonnegativity makes scalar-only recovery ineligible. These are small floating/ODE violations, not evidence of chemically substantial negative concentrations. Two other states retain mass/element residuals above 1e-12. No clipping or normalization masks these outcomes.

Of the observed increases, 22 exceed twice the stricter-reference temperature contrast. This contrast is an empirical uncertainty check, not a rigorous error bound; comparisons close to it are not resolved accuracy rankings. The scalar recovery restores the appropriate CV absolute internal energy or physical-CP absolute enthalpy, holding every species unchanged. It cannot remove mass/element/species trajectory errors. Both loose and strict trajectory integrations use Cantera 3.2 BDF; strict 1e-12 versus 1e-13 contrasts are reported as reference uncertainty. The root/property evaluation is independent Python NASA algebra checked against Cantera, not an independent trajectory integrator. Native Rosenbrock comparisons supply the separate source implementation evidence.

At H2 CV, T0=1100 K, rtol=1e-8, temperature error increases from 8.0013e-9 to 8.4105e-6 K after recovery. The provisional cancellation of composition and temperature errors is removed when energy is restored. This is an accuracy counterexample even though both errors are small. At H2 CV, 1500 K, rtol=1e-4, error increases from 0.00624 to 0.01780 K. Tightening the ODE can reduce species error, which the scalar operation leaves exactly unchanged.

## All controls

| Mechanism | Constraint | T0 | rtol | T error before (K) | T error after (K) | Max Y error | Endpoint gates |
|---|---|---|---|---|---|---|---|
| H2 | CV | 999.0 | 0.0001 | 2.03345568e-04 | 2.09431562e-04 | 4.05561077e-08 | PASS |
| H2 | CV | 999.0 | 1e-06 | 3.57790691e-06 | 3.68342694e-06 | 1.17929780e-09 | PASS |
| H2 | CV | 999.0 | 1e-08 | 3.07580899e-06 | 3.14820841e-06 | 8.39788881e-10 | PASS |
| H2 | CV | 999.0 | 1e-10 | 2.96574854e-08 | 3.03530214e-08 | 8.08914741e-12 | PASS |
| H2 | CV | 1100.0 | 0.0001 | 5.72029342e-03 | 1.87281715e-03 | 1.35857935e-07 | PASS |
| H2 | CV | 1100.0 | 1e-06 | 2.26305540e-04 | 2.00062557e-04 | 1.34413860e-08 | PASS |
| H2 | CV | 1100.0 | 1e-08 | 8.00127964e-09 | 8.41054589e-06 | 5.19861515e-10 | PASS |
| H2 | CV | 1100.0 | 1e-10 | 1.81157702e-08 | 1.51826953e-07 | 9.55363566e-12 | PASS |
| H2 | CV | 1500.0 | 0.0001 | 6.23958018e-03 | 1.77970866e-02 | 1.02777597e-06 | PASS |
| H2 | CV | 1500.0 | 1e-06 | 5.08761625e-04 | 2.19309458e-04 | 1.50191996e-08 | PASS |
| H2 | CV | 1500.0 | 1e-08 | 1.95947632e-06 | 6.39978907e-06 | 3.48926332e-10 | PASS |
| H2 | CV | 1500.0 | 1e-10 | 5.62354217e-08 | 3.07726623e-07 | 1.76070825e-11 | PASS |
| H2 | CP | 999.0 | 0.0001 | 5.57709185e-03 | 5.62503652e-03 | 1.65557305e-06 | PASS |
| H2 | CP | 999.0 | 1e-06 | 1.39976366e-05 | 1.42775793e-05 | 5.76697024e-09 | PASS |
| H2 | CP | 999.0 | 1e-08 | 3.67830808e-07 | 3.72945806e-07 | 1.35679685e-10 | PASS |
| H2 | CP | 999.0 | 1e-10 | 1.76316917e-08 | 1.79377366e-08 | 7.12345634e-12 | PASS |
| H2 | CP | 1100.0 | 0.0001 | 6.98757776e-02 | 6.45350798e-02 | 4.12696824e-06 | PASS |
| H2 | CP | 1100.0 | 1e-06 | 8.92122941e-04 | 8.95420804e-04 | 6.25053401e-08 | PASS |
| H2 | CP | 1100.0 | 1e-08 | 1.38185897e-05 | 1.05129475e-05 | 6.99721531e-10 | PASS |
| H2 | CP | 1100.0 | 1e-10 | 6.13226803e-09 | 2.32967068e-09 | 9.36195566e-14 | PASS |
| H2 | CP | 1500.0 | 0.0001 | 1.96102582e-02 | 8.12613990e-03 | 6.01623101e-07 | FAIL |
| H2 | CP | 1500.0 | 1e-06 | 7.64583955e-04 | 6.17856354e-04 | 3.85892679e-08 | PASS |
| H2 | CP | 1500.0 | 1e-08 | 6.89696753e-06 | 5.80920323e-06 | 3.63215569e-10 | PASS |
| H2 | CP | 1500.0 | 1e-10 | 4.15934210e-07 | 3.36283392e-07 | 2.14315232e-11 | PASS |
| GRI | CV | 999.0 | 0.0001 | 1.19267820e-03 | 1.21297387e-03 | 2.18503499e-07 | PASS |
| GRI | CV | 999.0 | 1e-06 | 3.90890852e-05 | 4.00760803e-05 | 7.56282625e-09 | PASS |
| GRI | CV | 999.0 | 1e-08 | 2.53262101e-06 | 2.59275566e-06 | 5.12445971e-10 | PASS |
| GRI | CV | 999.0 | 1e-10 | 1.33385356e-07 | 1.31772367e-07 | 2.64517661e-11 | PASS |
| GRI | CV | 1100.0 | 0.0001 | 2.21412156e-03 | ineligible | 3.10364705e-07 | FAIL |
| GRI | CV | 1100.0 | 1e-06 | 1.36880764e-04 | ineligible | 1.54327080e-08 | FAIL |
| GRI | CV | 1100.0 | 1e-08 | 3.58327998e-06 | ineligible | 4.12887141e-10 | FAIL |
| GRI | CV | 1100.0 | 1e-10 | 4.66752681e-09 | 7.49109859e-08 | 4.48319160e-12 | PASS |
| GRI | CV | 1500.0 | 0.0001 | 7.39988595e-03 | 2.49663970e-02 | 2.21200681e-06 | FAIL |
| GRI | CV | 1500.0 | 1e-06 | 9.11793095e-05 | 4.27881434e-04 | 2.41422142e-08 | PASS |
| GRI | CV | 1500.0 | 1e-08 | 2.67007772e-06 | ineligible | 4.15239315e-10 | FAIL |
| GRI | CV | 1500.0 | 1e-10 | 4.93582775e-08 | ineligible | 6.68487488e-12 | FAIL |
| GRI | CP | 999.0 | 0.0001 | 3.49910824e-05 | 3.72322515e-05 | 4.93760435e-08 | PASS |
| GRI | CP | 999.0 | 1e-06 | 6.79836967e-06 | 6.92997514e-06 | 2.08582399e-09 | PASS |
| GRI | CP | 999.0 | 1e-08 | 1.01572618e-06 | 1.02349736e-06 | 2.84210245e-10 | PASS |
| GRI | CP | 999.0 | 1e-10 | 4.25461621e-08 | 4.38194547e-08 | 1.26125325e-11 | PASS |
| GRI | CP | 1100.0 | 0.0001 | 1.20354533e-02 | 9.70026830e-03 | 5.15434534e-07 | PASS |
| GRI | CP | 1100.0 | 1e-06 | 1.26996020e-03 | 9.29137213e-04 | 6.52390486e-08 | PASS |
| GRI | CP | 1100.0 | 1e-08 | 2.65526910e-05 | 2.30973160e-05 | 1.62980368e-09 | PASS |
| GRI | CP | 1100.0 | 1e-10 | 5.56034593e-07 | ineligible | 3.08589820e-11 | FAIL |
| GRI | CP | 1500.0 | 0.0001 | 6.52232047e-02 | ineligible | 2.88444044e-06 | FAIL |
| GRI | CP | 1500.0 | 1e-06 | 2.93209765e-04 | ineligible | 8.53293883e-09 | FAIL |
| GRI | CP | 1500.0 | 1e-08 | 1.13476813e-05 | 5.15213378e-06 | 3.09888781e-10 | PASS |
| GRI | CP | 1500.0 | 1e-10 | 7.91260391e-09 | 7.11265784e-08 | 4.74456585e-12 | PASS |

These are final endpoint projections, not projections at every accepted BDF step with history/error-test correction. The rejection does not rule out the latter known approach or a full positivity-constrained species solve. CVODE eq3.11–3.12 already gives the weighted constrained manifold formulation; generic novelty fails independently of these numerical counterexamples.

## Accuracy and cost boundary

RHS/Jacobian/step counts are retained for all tolerances. Concurrent wall measurements are excluded from cost comparisons. No lower runtime/memory frontier is claimed; a candidate that already fails novelty and unconditional trajectory accuracy is not promoted on endpoint conservation. Prior native extra-pressure, dt and frozen-block baselines remain available with their original uncontended timings.

Machine evidence: invariant_projection_valid_data.json and raw InvariantProjectionValidData_v1. Root and data snapshots remain immutable.
