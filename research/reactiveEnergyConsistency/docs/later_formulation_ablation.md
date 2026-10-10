# Later OpenFOAM equation comparison and controlled-port scope

The frozen sourceAudit contains current OpenCFD v2606 EEqn/pEqn/YEqn/main
and Foundation 14 multicomponentFluid::thermophysicalPredictor. Exact source
hashes and URLs are in the accepted source manifest. Installed core files were
not changed. Comparison is by mathematical term, not a whole-version run.

OpenCFD v2606 EEqn has the same rho*hs Euler/convection, explicit K time/flux,
-dpdt sensible-enthalpy work, thermal laplacian, Qdot and thermo.correct as the
selected v2012 case. Its added `div(MRF.phi(),p)` is guarded by active MRF.
The present fixed cyclic domain has no MRF, so this term is identically zero;
there is no nonzero pressure-work change to port into this particular control.
The current pEqn likewise retains EOS density replacement before/after pressure,
continuity, HbyA/rAU velocity correction and dpdt update. The solver lookup API
differs; that is not a new discrete term. These source comparisons do not imply
all later versions/forks are equivalent.

Foundation 14 separates transport through divj/divq and species normalization,
and routes pressure work through a helper. For the h path, that helper receives
-dpdt. A transport-port experiment must specify the chosen divj/divq model;
blindly copying an API cannot isolate a numerical improvement. The present
speciesFlux/conservativeState variants isolate final-density/final-flux species
and absolute-energy compatibility while retaining the installed transport model.
They are not labelled a port of the entire Foundation formulation.

Changing to internal energy would select a different pressure-flux equation;
the documented baseline is sensible enthalpy. No result from that path is
inferred for the h control. Current evidence therefore rules out attributing
the observed fix to a later OpenCFD MRF pressure-work patch in this nonrotating
case. Species normalization alone cannot conserve missing rhoY: a local rescale
has sum Yi=rho_a/rho_f and normalization restores the original state.

Related primary source example:
[Foundation 10 EEqn](https://raw.githubusercontent.com/OpenFOAM/OpenFOAM-10/master/applications/solvers/combustion/reactingFoam/EEqn.H)
also preserves -dpdt for h, while revising transport and the e pressure flux.
Unimplemented open-boundary, rotating and differential-diffusion variants remain
outside the present controlled comparison.
