// OpenFOAM v2012 createDpdt.H, with an opt-in static-mesh restart state.
// The default matches the original NO_READ/NO_WRITE behavior exactly.
IOobject dpdtHeader
(
    "dpdt", runTime.timeName(), mesh,
    IOobject::NO_READ, IOobject::NO_WRITE
);
if
(
    mesh.dynamic()
 || runTime.controlDict().getOrDefault<bool>("padRestartState", false)
)
{
    dpdtHeader.readOpt() = IOobject::READ_IF_PRESENT;
    dpdtHeader.writeOpt() = IOobject::AUTO_WRITE;
}
volScalarField dpdt(dpdtHeader, fvc::ddt(p));
if (!thermo.dpdt())
{
    dpdt == dimensionedScalar(dpdt.dimensions(), Zero);
    dpdt.writeOpt() = IOobject::NO_WRITE;
}
