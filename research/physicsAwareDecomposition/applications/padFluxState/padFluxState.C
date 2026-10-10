/* GPL-3.0-or-later. Optional stationary, axis-aligned mesh flux snapshot.
 * Preserve flux by physical face identity outside the native field mapper.
 * This reference utility uses O(global faces) storage per rank and is not a
 * scalable general-purpose mapper. Rotated/moving meshes are unsupported.
 */
#include "fvCFD.H"
#include "timeSelector.H"
#include <fstream>
#include <iomanip>
#include <map>
#include <tuple>
#include <cmath>

typedef std::tuple<long long,long long,long long,int> FaceKey;
int axisOf(const vector& area)
{
    int axis=0;
    for (int d=1;d<3;++d) if (mag(area[d])>mag(area[axis])) axis=d;
    if (mag(area[axis])<=VSMALL) FatalErrorInFunction<<"Zero face area"<<exit(FatalError);
    for (int d=0;d<3;++d)
        if (d!=axis && mag(area[d])>1e-10*mag(area[axis]))
            FatalErrorInFunction<<"Flux snapshot requires axis-aligned faces"<<exit(FatalError);
    return axis;
}
FaceKey keyOf(vector centre,const int axis,const scalar period)
{
    if (mag(centre.x()-period)<1e-11) centre.x()=0;
    return FaceKey(std::llround(centre.x()/1e-11),std::llround(centre.y()/1e-11),
                   std::llround(centre.z()/1e-11),axis);
}

int main(int argc,char *argv[])
{
    timeSelector::addOptions();
    argList::addBoolOption("restore","restore phi from a pre-migration face snapshot");
    argList::addBoolOption("repairZeroCoupled","diagnostic: fill an exactly zero coupled copy from its nonzero partner");
    argList::addOption("xPeriod","scalar","translational x-period, default 0.02 m; origin x=0");
    #include "setRootCaseLists.H"
    #include "createTime.H"
    const scalar period=args.getOrDefault<scalar>("xPeriod",0.02);
    const instantList times=timeSelector::select0(runTime,args);
    forAll(times,ti)
    {
        runTime.setTime(times[ti],ti);
        fvMesh mesh(IOobject(fvMesh::defaultRegion,runTime.timeName(),runTime,IOobject::MUST_READ));
        surfaceScalarField phi(IOobject("phi",runTime.timeName(),mesh,IOobject::MUST_READ,IOobject::NO_WRITE),mesh);
        const fileName directory=runTime.globalPath()/"fluxState"/runTime.timeName();
        const bool restoring=args.found("restore");
        std::map<FaceKey,scalar> snapshot;
        if (restoring)
        {
            for (int rank=0;rank<Pstream::nProcs();++rank)
            {
                std::ifstream input((directory/("rank"+Foam::name(rank)+".csv")).c_str());
                if (!input.good()) FatalErrorInFunction<<"Missing flux snapshot"<<exit(FatalError);
                long long x,y,z;int axis;scalar value;
                while (input>>x>>y>>z>>axis>>value)
                {
                    const FaceKey key(x,y,z,axis);
                    auto previous=snapshot.find(key);
                    if (previous!=snapshot.end() && mag(previous->second-value)>1e-10)
                    {
                        if (args.found("repairZeroCoupled") && (previous->second==0 || value==0))
                        {
                            if (value==0) value=previous->second;
                        }
                        else FatalErrorInFunction<<"Inconsistent periodic/processor face snapshot"<<exit(FatalError);
                    }
                    snapshot[key]=value;
                }
                if (!input.eof()) FatalErrorInFunction<<"Malformed flux snapshot"<<exit(FatalError);
            }
        }
        mkDir(directory);
        std::ofstream output;
        if (!restoring) output.open((directory/("rank"+Foam::name(Pstream::myProcNo())+".csv")).c_str());
        output<<std::setprecision(17);
        auto process=[&](const vector& centre,const vector& area,scalar& value)
        {
            const int axis=axisOf(area);
            const scalar sign=area[axis]>0 ? 1 : -1;
            const FaceKey key=keyOf(centre,axis,period);
            if (restoring)
            {
                auto found=snapshot.find(key);
                if (found==snapshot.end()) FatalErrorInFunction<<"Unmatched physical face"<<exit(FatalError);
                value=found->second*sign;
            }
            else output<<std::get<0>(key)<<' '<<std::get<1>(key)<<' '<<std::get<2>(key)<<' '<<axis<<' '<<value*sign<<'\n';
        };
        forAll(phi,fi) process(mesh.Cf()[fi],mesh.Sf()[fi],phi[fi]);
        forAll(phi.boundaryField(),pi)
            forAll(phi.boundaryField()[pi],fi)
                process(mesh.Cf().boundaryField()[pi][fi],mesh.Sf().boundaryField()[pi][fi],phi.boundaryFieldRef()[pi][fi]);
        if (restoring) { phi.oriented().setOriented(true);phi.write(); }
        else if (!output.good()) FatalErrorInFunction<<"Failed flux snapshot write"<<exit(FatalError);
    }
    return 0;
}
