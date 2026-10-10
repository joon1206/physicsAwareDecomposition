# Local internal-energy projection (A)

Hypothesis: the density-coefficient defect can be cancelled pointwise with a
nonlinear temperature update, preserving final density and species masses.

At the pressure-loop exit let rho_f,Y_b,p_star,U_f be fixed inputs. Set
`e_target=(rho_a ha_b-p_star)/rho_f`, solve
`ha(T_new,Y_b)-R(Y_b)T_new=e_target`, then set sensible enthalpy and
`p_new=rho_f R T_new`. This gives exactly
`rho_f delta hs-delta p=-(rho_f-rho_a)ha_b`. Pressure and kinetic terms
already present in the ledger are not counted twice. The complete post-update
ledger includes `rho_f delta hs` and the actual final pressure.

This cancels one measured term, not the complete timestep energy balance.
Mass and rhoY are unchanged by the projection; EOS is enforced. Momentum and
phi remain based on p_star. We measure `-rAU grad(delta p)` as the induced
momentum-corrector mismatch. A nonuniform pressure response can therefore
falsify the claim that a local projection replaces coupled pressure correction.

For smooth delta rho=O(dt), delta T and delta p are generically O(dt), not
automatically O(dt^2). No higher temporal order is claimed. Existence requires
positive Cv and an attainable target on a continuous thermodynamic branch;
being between the 200–5000 K endpoint energies alone is insufficient when
NASA energy jumps occur inside the interval. Safeguarded
Newton/bisection solves the scalar inversion; out-of-range targets are retained
failures, not clipped energy fixes. Cost is local species-property evaluations
and EOS refresh, with no new matrix solve. Additional boundary communication
comes from the field/thermo updates and must be measured before performance claims.

Closest inspected formulations: McDermott (2014) low-Mach enthalpy/divergence
compatibility, Grapsas et al. (2020) reactive pressure correction, and the
primitive conservative thermodynamic updates of Sirianni et al. (2024).
Local thermodynamic inversion is established practice. Novelty is not established.

Screen: identical A/B/F cases and dt/2; retain local closure, absolute energy,
mass/elements, EOS, positivity and momentum mismatch. Promote only if independent
solution errors and coupling consistency improve. Algebraic cancellation alone
does not pass the mathematical or numerical publication gates.

The later actual-data gap/overlap proof in thermoBranchInversion.md corrects
the original unqualified inversion assumption. Positive branch Cv alone
does not guarantee a global root or uniqueness. This is another scoped
limitation of a local projection, in addition to its already retained CFD,
momentum and energy-reference failures. No original implementation or failed
case is removed to disguise this limitation.
