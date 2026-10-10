tmp<fv::convectionScheme<scalar>> mvConvection
(
    fv::convectionScheme<scalar>::New
    (
        mesh,
        fields,
        phi,
        mesh.divScheme("div(phi,Yi_h)")
    )
);

{
    phaseTimer.start(phaseTimers::chemistry);
    reaction->correct();
    Qdot = reaction->Qdot();
    ledger.snapshot("chemistry_sources",rho,thermo,K,Qdot,dpdt);
    phaseTimer.stop(phaseTimers::chemistry);

    volScalarField Yt(0.0*Y[0]);

    phaseTimer.start(phaseTimers::species);
    forAll(Y, i)
    {
        if (i != inertIndex && composition.active(i))
        {
            volScalarField& Yi = Y[i];

            fvScalarMatrix YiEqn
            (
                fvm::ddt(rho, Yi)
              + mvConvection->fvmDiv(phi, Yi)
              - fvm::laplacian(turbulence->muEff(), Yi)
             ==
                reaction->R(Yi)
              + fvOptions(rho, Yi)
            );

            YiEqn.relax();

            fvOptions.constrain(YiEqn);

            YiEqn.solve(mesh.solver("Yi"));

            fvOptions.correct(Yi);

            Yi.max(0.0);
            Yt += Yi;
        }
    }

    Y[inertIndex] = scalar(1) - Yt;
    Y[inertIndex].max(0.0);
    phaseTimer.stop(phaseTimers::species);
    ledger.snapshot("species_solved",rho,thermo,K,Qdot,dpdt);
}
