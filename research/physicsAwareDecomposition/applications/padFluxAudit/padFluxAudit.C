/* GPL-3.0-or-later. Untimed audit of a stored flux and its mesh geometry. */
#include "fvCFD.H"
#include "timeSelector.H"
#include <fstream>
#include <iomanip>
int main(int argc, char *argv[])
{
    timeSelector::addOptions();
    #include "setRootCaseLists.H"
    #include "createTime.H"
    const instantList times=timeSelector::select0(runTime,args);
    forAll(times,ti)
    {
        runTime.setTime(times[ti],ti);
        fvMesh mesh(IOobject(fvMesh::defaultRegion,runTime.timeName(),runTime,IOobject::MUST_READ));
        const surfaceScalarField phi(IOobject("phi",runTime.timeName(),mesh,IOobject::MUST_READ,IOobject::NO_WRITE),mesh);
        const volScalarField rho(IOobject("rho",runTime.timeName(),mesh,IOobject::MUST_READ,IOobject::NO_WRITE),mesh);
        const volVectorField U(IOobject("U",runTime.timeName(),mesh,IOobject::MUST_READ,IOobject::NO_WRITE),mesh);
        volScalarField stored(IOobject("padDivPhi",runTime.timeName(),mesh,IOobject::NO_READ,IOobject::NO_WRITE),fvc::div(phi));
        volScalarField reconstructed(IOobject("padDivReconstructedPhi",runTime.timeName(),mesh,IOobject::NO_READ,IOobject::NO_WRITE),fvc::div(fvc::interpolate(rho)*fvc::flux(U)));
        volScalarField x(IOobject("padCellX",runTime.timeName(),mesh,IOobject::NO_READ,IOobject::NO_WRITE),mesh.C().component(vector::X));
        volScalarField y(IOobject("padCellY",runTime.timeName(),mesh,IOobject::NO_READ,IOobject::NO_WRITE),mesh.C().component(vector::Y));
        stored.write();reconstructed.write();x.write();y.write();
        std::ofstream faces((runTime.path()/runTime.timeName()/"faceAudit.csv").c_str());
        faces << std::setprecision(17) << "x,y,z,sx,sy,sz,phi,patch,type\n";
        forAll(phi,fi)
        {
            const vector c=mesh.Cf()[fi],s=mesh.Sf()[fi];
            faces << c.x()<<','<<c.y()<<','<<c.z()<<','<<s.x()<<','<<s.y()<<','<<s.z()<<','<<phi[fi]<<",internal,internal\n";
        }
        forAll(phi.boundaryField(),pi)
        {
            forAll(phi.boundaryField()[pi],fi)
            {
                const vector c=mesh.Cf().boundaryField()[pi][fi],s=mesh.Sf().boundaryField()[pi][fi];
                faces << c.x()<<','<<c.y()<<','<<c.z()<<','<<s.x()<<','<<s.y()<<','<<s.z()<<','<<phi.boundaryField()[pi][fi]<<','<<mesh.boundary()[pi].name()<<','<<mesh.boundary()[pi].type()<<'\n';
            }
        }
    }
    return 0;
}
