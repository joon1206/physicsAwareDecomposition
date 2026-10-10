{
    phaseTimer.start(phaseTimers::energy);

    volScalarField& he = thermo.he();

    fvScalarMatrix EEqn
    (
        fvm::ddt(rho, he) + mvConvection->fvmDiv(phi, he)
      + fvc::ddt(rho, K) + fvc::div(phi, K)
      + (
            he.name() == "e"
          ? fvc::div
            (
                fvc::absolute(phi/fvc::interpolate(rho), U),
                p,
                "div(phiv,p)"
            )
          : -dpdt
        )
      - fvm::laplacian(turbulence->alphaEff(), he)
     ==
        Qdot
      + fvOptions(rho, he)
    );

    EEqn.relax();

    fvOptions.constrain(EEqn);

    EEqn.solve();

    fvOptions.correct(he);

    thermo.correct();

    // Optional extra Newton updates for the h-to-T inversion. The original
    // v2012 default is preserved. Detailed transient partition comparisons
    // can otherwise amplify the thermodynamic inversion stopping error.
    const label padThermoCorrections =
        runTime.controlDict().getOrDefault<label>("padThermoCorrections", 0);
    if (padThermoCorrections < 0 || padThermoCorrections > 5)
        FatalErrorInFunction << "padThermoCorrections must be in [0,5]"
            << exit(FatalError);
    for (label correction=0; correction<padThermoCorrections; ++correction)
        thermo.correct();

    Info<< "min/max(T) = "
        << min(T).value() << ", " << max(T).value() << endl;

    phaseTimer.stop(phaseTimers::energy);
}
