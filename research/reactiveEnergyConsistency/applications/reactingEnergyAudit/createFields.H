#include "createRDeltaT.H"

Info<< "Reading thermophysical properties\n" << endl;
autoPtr<psiReactionThermo> pThermo(psiReactionThermo::New(mesh));
psiReactionThermo& thermo = pThermo();
thermo.validate(args.executable(), "h", "e");
// Initialization diagnostic: preserve the initial Euler coefficient before thermo changes it.
if (runTime.value() <= SMALL) thermo.psi().oldTime();
// heThermo initializes he from T/Y instead of reading the solved enthalpy.
if (runTime.controlDict().getOrDefault<bool>("padRestartState", false))
{
    IOobject storedHe
    (
        thermo.he().name(), runTime.timeName(), mesh,
        IOobject::READ_IF_PRESENT, IOobject::NO_WRITE, false
    );
    if (storedHe.typeHeaderOk<volScalarField>(true))
    {
        volScalarField checkpointHe(storedHe, mesh);
        thermo.he() == checkpointHe;
        thermo.correct();
        thermo.correct();
        // psi is first used by ddt(psi,p) after thermo.correct(). Without
        // preallocating oldTime at a restart, its first old value is the
        // already-updated psi, whereas a continuous trajectory retains the
        // checkpoint value. Preserve Euler's previous coefficient explicitly.
        if (runTime.value() > SMALL) thermo.psi().oldTime();
    }
}
if (runTime.controlDict().getOrDefault<bool>("padWriteFinal", false))
{
    thermo.he().writeOpt() = IOobject::AUTO_WRITE;
}

basicSpecieMixture& composition = thermo.composition();
PtrList<volScalarField>& Y = composition.Y();

const word inertSpecie(thermo.get<word>("inertSpecie"));
if (!composition.species().found(inertSpecie))
{
    FatalIOErrorIn(args.executable().c_str(), thermo)
        << "Inert specie " << inertSpecie << " not found in available species "
        << composition.species() << exit(FatalIOError);
}

volScalarField rho
(
    IOobject
    (
        "rho",
        runTime.timeName(),
        mesh
    ),
    thermo.rho()
);

Info<< "Reading field U\n" << endl;
volVectorField U
(
    IOobject
    (
        "U",
        runTime.timeName(),
        mesh,
        IOobject::MUST_READ,
        IOobject::AUTO_WRITE
    ),
    mesh
);

volScalarField& p = thermo.p();

#include "compressibleCreatePhi.H"

pressureControl pressureControl(p, rho, pimple.dict(), false);

mesh.setFluxRequired(p.name());

Info << "Creating turbulence model.\n" << nl;
autoPtr<compressible::turbulenceModel> turbulence
(
    compressible::turbulenceModel::New
    (
        rho,
        U,
        phi,
        thermo
    )
);

Info<< "Creating reaction model\n" << endl;
autoPtr<CombustionModel<psiReactionThermo>> reaction
(
    CombustionModel<psiReactionThermo>::New(thermo, turbulence())
);

multivariateSurfaceInterpolationScheme<scalar>::fieldTable fields;

forAll(Y, i)
{
    fields.add(Y[i]);
}
fields.add(thermo.he());

volScalarField Qdot
(
    IOobject
    (
        "Qdot",
        runTime.timeName(),
        mesh,
        IOobject::READ_IF_PRESENT,
        IOobject::AUTO_WRITE
    ),
    mesh,
    dimensionedScalar(dimEnergy/dimVolume/dimTime, Zero)
);

#include "padCreateDpdt.H"

#include "createK.H"

#include "createMRF.H"
#include "createFvOptions.H"
