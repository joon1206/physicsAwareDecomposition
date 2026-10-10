// GPL-3.0-or-later. Controlled synthetic CPU + processor-halo experiment.
#include "fvCFD.H"
#include "processorPolyPatch.H"
#include <mpi.h>
#include <chrono>
#include <cstdio>
#include <cmath>
#include <set>
int main(int argc,char* argv[])
{
    #include "setRootCase.H"
    #include "createTime.H"
    #include "createMesh.H"
    IOdictionary props(IOobject("workloadProperties",runTime.constant(),mesh,IOobject::MUST_READ,IOobject::NO_WRITE));
    const label base=props.get<label>("baseIterations"),unit=props.get<label>("chemistryIterations"),passes=props.get<label>("haloPasses"),steps=props.get<label>("steps");
    if(base<0 || unit<0 || passes<0 || steps<1) FatalErrorInFunction << "Nonnegative work and positive steps required" << exit(FatalError);
    volScalarField w(IOobject("cellWeight",runTime.timeName(),mesh,IOobject::MUST_READ,IOobject::NO_WRITE),mesh);
    if(min(w.primitiveField())<=0) FatalErrorInFunction << "Positive weights required" << exit(FatalError);
    volScalarField halo(IOobject("halo",runTime.timeName(),mesh,IOobject::NO_READ,IOobject::NO_WRITE),mesh,dimensionedScalar(dimless,1),"zeroGradient");
    const fileName dir(runTime.path()/"postProcessing"/"performance");mkDir(dir);
    char name[32];std::snprintf(name,sizeof(name),"rank%04d.csv",Pstream::myProcNo());
    std::FILE* fp=std::fopen((dir/name).c_str(),"w");
    if(!fp) FatalErrorInFunction << "Cannot write timing" << exit(FatalError);
    std::fputs("timeIndex,rank,nCells,processorFaces,nNeighbours,stepWall,transportWall,chemistryWall,communicationWall,synchronizationWall,sink\n",fp);
    label faces=0;std::set<label> neighbours;
    forAll(mesh.boundaryMesh(),i) if(isA<processorPolyPatch>(mesh.boundaryMesh()[i]))
    {
        const auto& pp=refCast<const processorPolyPatch>(mesh.boundaryMesh()[i]);
        if(!halo.boundaryField()[i].coupled()) FatalErrorInFunction << "Halo patch is not coupled" << exit(FatalError);
        Pout << "Halo patch " << i << " type " << halo.boundaryField()[i].type() << endl;
        faces+=pp.size();neighbours.insert(pp.neighbProcNo());
    }
    typedef std::chrono::steady_clock Clock;
    const auto seconds=[](Clock::time_point a,Clock::time_point b){return std::chrono::duration<double>(b-a).count();};
    volatile double sink=0;
    // Deliberate barriers define a synchronous synthetic makespan, separate
    // from the reacting solver, which contains no added timing collectives.
    if(Pstream::parRun()) MPI_Barrier(MPI_COMM_WORLD);
    for(label step=0;step<steps;++step)
    {
        const auto t0=Clock::now();
        forAll(w,i) for(label j=0;j<base;++j) sink+=std::sin(1e-4*(i+j+1));
        const auto t1=Clock::now();
        forAll(w,i)
        {
            const label work=label(std::round(unit*w[i]));
            for(label j=0;j<work;++j) sink+=std::sin(1e-4*(i+j+1));
        }
        const auto t2=Clock::now();
        for(label j=0;j<passes;++j) halo.correctBoundaryConditions();
        const auto t3=Clock::now();
        if(Pstream::parRun()) MPI_Barrier(MPI_COMM_WORLD);
        const auto t4=Clock::now();
        std::fprintf(fp,"%d,%d,%d,%d,%d,%.12g,%.12g,%.12g,%.12g,%.12g,%.12g\n",step,Pstream::myProcNo(),mesh.nCells(),faces,label(neighbours.size()),seconds(t0,t4),seconds(t0,t1),seconds(t1,t2),seconds(t2,t3),seconds(t3,t4),double(sink));
    }
    std::fclose(fp);return 0;
}
