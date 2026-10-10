# Element-invariant reduction of the species correction

2026-10-06. Derivation and prior-art decision before implementation.
REJECTED_AS_PRIOR_ART for the general reduction principle. The planned exact
linear-system experiment is a compatibility diagnostic, not a new CFD method.

## Hypothesis and derivation

The shared final-flux correction solves, for each species, the same linear
Euler/upwind/common-diffusion operator at frozen rho, phi, mu and chemistry:

    L Y_s = V rho_n Y_s,n / dt + V RR_s.

Let a_es be the elemental mass fraction of element e in species s, and
Z_e=sum_s a_es Y_s. Balanced rates satisfy sum_s a_es RR_s=0. Since L is
species independent and linear,

    L Z_e = V rho_n Z_e,n / dt.

Discrete continuity gives L 1=V rho_n/dt for periodic boundaries: diffusion
annihilates a constant, and the same upwind mass flux supplies continuity.
If every Z_e,n is spatially constant z_e, the unique invariant solution is
Z_e=z_e. Partition species into independent I and dependent D, with an
invertible elemental coefficient block A_D. Then

    Y_D = A_D^-1 (z - A_I Y_I).

The dependent species equations follow from the independent equations,
balanced sources and continuity. More generally their residual obeys

    A_D R_D = z R_mass - A_I R_I - R_elementSource.

Thus continuity and independent solve tolerances propagate explicitly;
algebraic reconstruction does not make those residuals vanish by assertion.
For H/O/N/Ar and the ten-species H2 mechanism, H2/O2/N2/AR form a diagonal
dependent block. Six independent equations can replace ten corrections only
inside this restricted class. This does not change the energy residual,
momentum response, time order, chemistry path or pressure-equilibrium defect.
An elemental energy gauge remains compatible only with the full residuals.

## Conditions and counterexamples

For spatially varying Z_e, each Z_e must instead satisfy its transported
invariant equation. Solving N_s-N_e species and N_e invariants leaves N_s
equations: there is no generic equation-count saving. Reconstructing from a
single constant z erases transported elemental variation.

With unequal species diffusion or independently nonlinear convection,
sum_s a_es L_s Y_s cannot be replaced by L Z_e. Uniform initial elements
alone are then insufficient. A common linear diffusion coefficient, common
upwind operator, matched periodic boundary flux and balanced rates are all
required. Subtractive reconstruction can also lose relative accuracy for
trace dependent species; no unconditional positivity theorem follows from
the coordinate change itself.

## Predeclared diagnostic and acceptance

Use the unchanged legacy H2 NASA molecular weights and element matrix in
an eight-cell periodic variable-density, frozen-rate Euler transport system.
Create density from the discrete continuity flux. Compare all ten direct
species solutions with six solutions plus elemental reconstruction.
Require maximum field difference and scaled full equation residual below
1e-12, sumY/element errors below 1e-12 and all species >=-1e-12.

Then deliberately violate each precondition separately: sinusoidal initial
H elemental fraction; unequal H2/O2/H2O diffusion coefficients. Record the
naive reconstructed errors and flag both cases ineligible. Use no clipping.
This is an exact algebraic screen, not an OpenFOAM timing or flame benchmark.
Do not build a native reduced solver solely to repeat a known principle.

## Verified prior-art boundary

[Kräutle 2005, sections 2.1 and 4.1](https://agupubs.onlinelibrary.wiley.com/doi/full/10.1029/2004WR003624)
assumes the same linear operator for mobile species and transforms the
system into reaction coordinates and invariants. Its porous-media setting
differs from compressible pressure correction, but the commuting-operator
reduction principle is already explicit. Image-only equations require
separate inspection; textual sections alone do not attest every coefficient.

[Hiremath et al. 2010, section 3.3 and figure 6](https://tcg.mae.cornell.edu/pubs/Hiremath_RP_CTM_10.pdf)
identifies species determined by elemental conservation and terminates
selection at N_s-N_e. This is chemistry dimension reduction rather than
the present frozen FV correction, but excludes a generic species-elimination
novelty claim.

[Wang 2025, equations 1–3 and 7–14](https://arxiv.org/html/2504.04941v1)
uses consistent mass/species flux, constant elemental abundance constraints
and a stoichiometric nullspace projection for reconstruction. It is an
explicit Godunov reconstruction, rather than this implicit residual solve.
Those differences do not establish a new contribution here. Novelty, general
admissibility and a measured accuracy/cost advantage remain unestablished.

## Executed diagnostic

The eligible eight-cell system agrees with the full ten-equation solve to
2.22045e-16 in species fields; full reconstructed equation residual is
3.59462e-16 relative, sumY error zero and minimum Y zero. Six independent
solves are algebraically sufficient in this class. That equation count is
not a native runtime measurement or a correction to the energy method.

The variable-element case is ineligible: enforcing the constant invariant
changes fields by 0.00277164 and gives equation residual 0.121386 relative.
The unequal-diffusion case is also ineligible despite uniform initial
elements: field discrepancy 7.51776e-9 and equation residual 8.49268e-8.
Both violate the predeclared 1e-12 equivalence limit and remain permanent
negative controls. The latter tests operator compatibility; its unequal
uncorrected species flux is not advertised as a complete mass-conserving
differential-diffusion model. Raw/processed element_invariant_screen.json
records all direct and reconstructed fields, the legacy thermo input hash
and executable-script hash. Decision: retain as a known reduction diagnostic,
reject general applicability and generic novelty; no duplicate native method.

The Wiley equation-image requests returned unsupported GIF responses.
Those coefficients are not claimed as inspected. The verified textual
assumptions, invariants and commuting-operator statements suffice for the
limited prior-art boundary stated above.
