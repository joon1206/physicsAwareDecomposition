phaseTimer.start(phaseTimers::pressure);

rho = thermo.rho();
ledger.snapshot("rho_thermo",rho,thermo,K,Qdot,dpdt);

volScalarField rAU(1.0/UEqn.A());
surfaceScalarField rhorAUf("rhorAUf", fvc::interpolate(rho*rAU));
volVectorField HbyA(constrainHbyA(rAU*UEqn.H(), U, p));

if (pimple.nCorrPISO() <= 1)
{
    tUEqn.clear();
}

if (pimple.transonic())
{
    surfaceScalarField phid
    (
        "phid",
        fvc::interpolate(psi)
       *(
            fvc::flux(HbyA)
          + MRF.zeroFilter
            (
                rhorAUf*fvc::ddtCorr(rho, U, phi)/fvc::interpolate(rho)
            )
        )
    );

    MRF.makeRelative(fvc::interpolate(psi), phid);

    while (pimple.correctNonOrthogonal())
    {
        fvScalarMatrix pEqn
        (
            fvm::ddt(psi, p)
          + fvm::div(phid, p)
          - fvm::laplacian(rhorAUf, p)
         ==
            fvOptions(psi, p, rho.name())
        );

        pEqn.solve(mesh.solver(p.select(pimple.finalInnerIter())));
        ledger.snapshot("pressure_solved",rho,thermo,K,Qdot,dpdt);

        if (pimple.finalNonOrthogonalIter())
        {
            phi == pEqn.flux();
        }
    }
}
else
{
    surfaceScalarField phiHbyA
    (
        "phiHbyA",
        (
            fvc::flux(rho*HbyA)
          + MRF.zeroFilter(rhorAUf*fvc::ddtCorr(rho, U, phi))
        )
    );

    MRF.makeRelative(fvc::interpolate(rho), phiHbyA);

    // Update the pressure BCs to ensure flux consistency
    constrainPressure(p, rho, U, phiHbyA, rhorAUf, MRF);

    while (pimple.correctNonOrthogonal())
    {
        fvScalarMatrix pEqn
        (
            fvm::ddt(psi, p)
          + fvc::div(phiHbyA)
          - fvm::laplacian(rhorAUf, p)
         ==
            fvOptions(psi, p, rho.name())
        );

        pEqn.solve(mesh.solver(p.select(pimple.finalInnerIter())));
        ledger.snapshot("pressure_solved",rho,thermo,K,Qdot,dpdt);

        if (pimple.finalNonOrthogonalIter())
        {
            phi = phiHbyA + pEqn.flux();
            ledger.snapshot("phi_corrected",rho,thermo,K,Qdot,dpdt);
        }
    }
}

#include "rhoEqn.H"
ledger.snapshot("rho_continuity",rho,thermo,K,Qdot,dpdt);
#include "compressibleContinuityErrs.H"

// Explicitly relax pressure for momentum corrector
p.relax();

U = HbyA - rAU*fvc::grad(p);
U.correctBoundaryConditions();
fvOptions.correct(U);
K = 0.5*magSqr(U);
ledger.snapshot("velocity_corrected",rho,thermo,K,Qdot,dpdt);

if (pressureControl.limit(p))
{
    p.correctBoundaryConditions();
}

rho = thermo.rho();
ledger.snapshot("rho_thermo",rho,thermo,K,Qdot,dpdt);

if (thermo.dpdt())
{
    dpdt = fvc::ddt(p);
}

ledger.snapshot("pressure_end",rho,thermo,K,Qdot,dpdt);
phaseTimer.stop(phaseTimers::pressure);
