/* GPL-3.0-or-later. Known sensible species-diffusion compatibility control.
   Lagged p,T with post-species Y; declared in speciesSensibleDiffusion.md. */
surfaceScalarField extraSensibleEnergyFlux
(
    IOobject("extraSensibleEnergyFlux",runTime.timeName(),mesh,IOobject::NO_READ,IOobject::NO_WRITE,false),
    mesh,dimensionedScalar("zero",dimEnergy/dimTime,0)
);
if(runTime.controlDict().getOrDefault<bool>("compatibleSpeciesHeatFlux",false))
{
    // Initial control scope excludes open or imposed thermal/species boundaries.
    // The inherited global ledger assumes the added net boundary flux is zero.
    forAll(mesh.boundaryMesh(),patchi)
    {
        const word patchType=mesh.boundaryMesh()[patchi].type();
        if(!mesh.boundary()[patchi].coupled() && patchType!="empty"
            && patchType!="symmetryPlane" && patchType!="symmetry")
            FatalErrorInFunction<<"Compatible species heat-flux control requires periodic/processor, symmetry or empty boundaries"<<exit(FatalError);
    }
    volScalarField difference
    (
        IOobject("heatSpeciesDiffusivityDifference",runTime.timeName(),mesh,IOobject::NO_READ,IOobject::NO_WRITE,false),
        turbulence->alphaEff()-turbulence->muEff()
    );
    // Interpolation on processor patches must use the current remote internal
    // coefficients, not a manually populated or stale derived patch value.
    difference.correctBoundaryConditions();
    forAll(Y,s)
    {
        volScalarField hsSpecies
        (
            IOobject("sensibleSpeciesHeatFlux",runTime.timeName(),mesh,IOobject::NO_READ,IOobject::NO_WRITE,false),
            mesh,dimensionedScalar("zero",he.dimensions(),0)
        );
        forAll(he,i)hsSpecies[i]=composition.Ha(s,p[i],T[i])-composition.Hc(s);
        forAll(hsSpecies.boundaryField(),patchi)
            forAll(hsSpecies.boundaryField()[patchi],facei)
                hsSpecies.boundaryFieldRef()[patchi][facei]=composition.Ha(s,p.boundaryField()[patchi][facei],T.boundaryField()[patchi][facei])-composition.Hc(s);
        hsSpecies.correctBoundaryConditions();
        extraSensibleEnergyFlux+=fvc::interpolate(difference)*fvc::interpolate(hsSpecies)*fvc::snGrad(Y[s])*mesh.magSf();
    }
}
