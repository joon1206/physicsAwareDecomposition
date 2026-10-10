# Constraints on the direct-correction candidate space

These statements narrow the search. They are not a proof that no new reacting
CFD algorithm can exist. The active question is a cheap modification of the
identified segregated density/enthalpy pair, with the specified conservation,
EOS, accuracy and cost requirements.

1. **Fixed final rho,p,Y admits no nonzero thermochemical correction.** For
   the selected perfect-gas mixture, p=rho R(Y)T fixes T and hence the
   selected hs(T,Y) value. Thus a nonzero energy correction cannot retain all
   three quantities and EOS. This rejects the stronger fixed-state version
   of the hypothesis analytically, not merely through a failed implementation.

2. **Energy-only correction does not repair a rhoY incompatibility.** At
   unchanged rho,Y, elemental inventories and their discrete transport
   residuals cannot change. The nonreacting variable-composition Mix case
   measures this defect independently of reaction heat. A local rescaling
   rho_a Ya/rho_f conserves old cell species mass but makes sumY=rho_a/rho_f;
   normalizing it restores the old Y. A legitimate update needs compatible
   mass/species flux or density changes. This applies to local, explicit,
   predictor, midpoint and deferred energy sources that leave the species
   discrete equation unchanged; choosing a different time level cannot
   supply the missing species conservation identity.

3. **The midpoint product identity supplies no final-state closure.** The
   exact identity Delta(rho h)=rho_bar Delta h+h_bar Delta rho is an algebraic
   rewriting. It does not determine the pressure/density/species endpoint.
   Using predicted density leaves a splitting residual; using the converged
   final density requires its coupled response. A stand-alone discrete
   product-rule claim is therefore insufficient and overlaps prior work.

4. **Implicit final-flux energy balance is not cell-local in general.** Its
   upwind/diffusion operators depend on neighboring unknown thermochemical
   states. Independent local inversion can be conservative if the *whole*
   energy flux target is treated explicitly with appropriate stability
   restrictions, as in known conservative primitive/density-based schemes.
   Cancelling only V delta_rho ha is not that full conservative update.
   The tested scalar and shared-flux Newton corrections represent the global
   residual alternatives. Their modified pressure must still be paired with
   momentum/flux response for coupled consistency.

5. **A species-omitting 2x2 pressure/enthalpy block lacks a required response.**
   Pressure changes the continuity density and face flux. The species
   residual changes by Delta(rhoY)/dt+div(Delta phi Y) even if hs is corrected.
   Omitting this response cannot certify elemental conservation in general.
   The implemented frozen-source block includes those species equations;
   block/Schur/Newton principles themselves are established prior art.

6. **Formation-only indicators depend on the energy reference.** Adding
   elemental constants g_e shifts Ha/Hc but not balanced reaction heat.
   The full energy residual shifts by sum_e g_e r_element,e. Isolated
   delta_rho Hc or delta_rho Ha terms do not have that covariance by
   themselves. The ablations distinguish altered physical chemistry from
   an elemental gauge shift. A chemical-specific correction claim needs
   compatible species transport, not merely a different Hc weight.

7. **Energy residual alone cannot bound solution error.** In the unforced
   analytic reacting entropy wave the conservative schemes have near-zero
   energy residual and finite analytic temperature/species error. That is
   a verified counterexample even without selecting a hydrogen reference
   trajectory. A defect-only adaptive controller cannot be a guaranteed
   accuracy controller. Combined residual/truncation/chemistry estimators
   remain a distinct unresolved extension; ordinary inexact-coupling
   stopping tolerances are being measured without claiming such a theorem.

8. **Common-weight conservative remapping does not generally retain mixture
   pressure equilibrium.** With partial densities q_s and fixed p0, the
   one-state thermodynamic energy E_p(q) is nonlinear for unequal NASA species.
   Its value at the conservative mean generally differs from the mean donor
   energy. An admissible uniquely recovered temperature therefore determines a different pressure;
   enforcing p0 changes the conserved energy target. Linear elemental-reference
   shifts cancel from this discrepancy. The independent two-donor example and
   15 exact mixture-wave runs verify this separate compatibility issue. This
   conditional statement does not forbid different conservative fluxes or
   enriched/subcell closures; equilibrium-preserving methods have prior art.

9. **Eliminating constant elemental invariants is conditional and established.**
   With the same linear species operator, balanced rates and uniform elemental
   fractions, dependent species follow algebraically from independent species
   and continuity. Variable elements require transported invariant equations;
   unequal diffusion or nonlinear species-dependent reconstruction invalidates
   the commuting-operator argument. The exact eight-cell counterexamples and
   reduction prior-art audit are in candidates/elementInvariantReduction.md.
   This reduces coordinates only inside its known restricted class; it does
   not repair the pressure/energy/momentum or stiff-source accuracy defects.

10. **A local Taylor source-path correction is not uniformly stiff-admissible.**
    Its smooth expansion adds a negative quadratic species increment to a
    positive exponentially depleted CP endpoint in the exact synthetic model.
    Large steps therefore lose positivity. A common scalar limiter restores
    linear invariants and positivity, but has an executed case with 14.72x
    larger reference error. Neither property alone closes the accuracy gate.
    This is conditional evidence for the tested correction/limiter, not a
    no-go theorem for other stiff integrations or coupled source estimators.

11. **Positive branch Cv alone does not certify global thermodynamic inversion.**
    Actual legacy NASA coefficients have finite energy jumps at 1000 K.
    Rational positive-Cv bounds and admissible composition examples in
    candidates/thermoBranchInversion.md establish a missing target root and
    two distinct pure-N2 roots. Continuity and branch admissibility are
    additional requirements. This data limitation neither explains the
    original density-pair loss nor invalidates executed successful root
    residuals. A repaired thermodynamic model cannot silently replace the
    original benchmark and is not a novel energy-correction method.

Equation ordering and additional density/pressure/outer solves are diagnostics
or established coupling procedures. Moving energy last while retaining EOS
still changes density or pressure, unless it solves the conservative coupled
state; it cannot evade points 1-5. The later OpenFOAM ablation also identifies
no changed nonrotating enthalpy/pressure term in the selected newer OpenCFD
source that automatically removes this particular defect.

Implemented distinct constructions cover a local thermodynamic remap, scalar
density-source correction, shared final-flux species residual, full nonlinear
absolute-energy residual, frozen-source pressure/species/energy block, and its
inexact coupling tradeoff. The reference solver separately covers explicit
conservative mass/momentum/species/absolute-energy advancement. Remaining work
is to distinguish useful accurate coupling from merely conserved underresolved
trajectories, and to establish a precise novelty boundary. No universal
exhaustion statement follows from this finite candidate set. The remapping
pivot now has its own independent nonlinear-mixture diagnostic and exact
transport reference; it is not counted as a new correction merely because it
changes the original energy-residual target.
