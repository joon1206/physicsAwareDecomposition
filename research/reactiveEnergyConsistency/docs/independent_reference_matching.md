# Independent 0D chemistry comparison

The current reference is Cantera 3.2.0 with the retained converted 10-species,
27-reaction CHEMKIN mechanism. The reactor is closed and adiabatic at constant
volume. Each tolerance trial owns its phase, with `clone=False` so the declared
legacy atomic weights survive reactor creation. Raw data are in
`candidateStudy/data/raw/cantera0D_pstd100000_matched_legacyPhase`; the processed
reference is `candidateStudy/data/processed/cantera_reference.json`.

The legacy v2012 EOS uses R=8314.47006650545 J/(kmol K), while Cantera uses
8314.46261815324. Explicit element weights reproduce all species molecular
weights. The declared activation-energy conversion matches v2012's independent
CHEMKIN Rcal=1.987316. The effective Cantera standard pressure is rescaled
so Kc's standard-concentration factor matches v2012's 1 bar convention.
Cantera pressure and thermodynamic property comparisons use the declared R
conversion. Eight retained instantaneous rate/property fixtures verify those
conversions independently, with normalized rate differences ~1e-14 away from
near-equilibrium cancellation and up to 6.3e-11 in that fixture. No property
conversion is inferred from agreement in the final trajectory alone.

Two false reference floors were found and retained separately. Cantera's
default 1 atm standard pressure gives a ~1.255 K difference from the intended
1 bar convention. More subtly, the `clone=True` reactor in Cantera 3.2 replaces
the custom atomic weights even when the input Solution has exactly the desired
molecular weights. The read-only identity check records a maximum molecular
weight change of 0.002 kg/kmol and an initial converted pressure of
101323.2741266 Pa instead of 101325 Pa. The un-cloned phase keeps zero weight
error and the correct initial pressure. That mismatch caused the remaining
~0.00086 K false endpoint floor. The earlier cloned reference files remain
available; they are superseded for solution-error claims.

The corrected reference endpoint at 240 us is T=2928.259905383 K. Reference
tolerances 1e-10/1e-12 (absolute tolerances 1e-16/1e-18) agree well below the
smallest native discretization error; reference energy drift is ~1.1e-11.
Native default ODE settings are relTol=1e-5, absTol=1e-12. Tight relTol=1e-10,
absTol=1e-16 runs hardly change the successful fine endpoints; two 0.5 us
runs hit the retained 10,000 integration-step limit. Neither failure is erased.

| dt (us) | Baseline endpoint T error (K) | ConservativeState error (K) |
|---:|---:|---:|
| 0.125 | 3.0225440e-4 | 1.0318595e-4 |
| 0.0625 | 1.4887744e-4 | 5.1115186e-5 |
| 0.03125 | 7.3815987e-5 | 2.5386342e-5 |

Both approaches converge at approximately first order on this homogeneous
problem. ConservativeState improves the endpoint temperature error by about
threefold and eliminates energy drift to the residual tolerance. This is not
proof of higher order, a resolved flame result, multidimensional accuracy, or
novelty. The small equilibrium endpoint error also does not establish accuracy
of the entire ignition history. Full-mesh and one-column homogeneous endpoints
agree to <4e-10 K, supporting the reduced mesh for this uniform test only.
