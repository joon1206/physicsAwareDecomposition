/* GPL-3.0-or-later. Untimed native thermodynamic inventory for closed boxes. */
#include "fvCFD.H"
#include "psiReactionThermo.H"
#include "timeSelector.H"
#include <cstdio>
int main(int argc,char *argv[]) {
    timeSelector::addOptions();
    #include "setRootCaseLists.H"
    #include "createTime.H"
    const instantList times=timeSelector::select0(runTime,args);
    const fileName output(runTime.path()/"postProcessing"/"inventory");mkDir(output);
    char filename[64];std::snprintf(filename,sizeof(filename),"rank%04d.csv",Pstream::myProcNo());
    std::FILE* fp=std::fopen((output/filename).c_str(),"w");
    if(!fp) FatalErrorInFunction << "Cannot write inventory" << exit(FatalError);
    forAll(times,ti) {
        runTime.setTime(times[ti],ti);
        fvMesh mesh(IOobject(fvMesh::defaultRegion,runTime.timeName(),runTime,IOobject::MUST_READ));
        autoPtr<psiReactionThermo> ptr=psiReactionThermo::New(mesh);auto& thermo=ptr();
        const volVectorField U(IOobject("U",runTime.timeName(),mesh,IOobject::MUST_READ,IOobject::NO_WRITE),mesh);
        const tmp<volScalarField> rhoEOS=thermo.rho(), hc=thermo.hc();
        const volScalarField rho(IOobject("rho",runTime.timeName(),mesh,IOobject::READ_IF_PRESENT,IOobject::NO_WRITE,false),rhoEOS());
        const volScalarField h(IOobject(thermo.he().name(),runTime.timeName(),mesh,IOobject::READ_IF_PRESENT,IOobject::NO_WRITE,false),thermo.he());
        const auto& p=thermo.p();const auto& T=thermo.T();
        scalar mass=0,chemical=0,sensible=0,kinetic=0,pv=0,sumYError=0,massEOS=0,energyEOS=0;
        const auto& Y=thermo.composition().Y();
        if(ti==0) {
            std::fputs("time,rank,nCells,mass,totalEnergy,chemicalEnergy,sensibleEnthalpy,kineticEnergy,pressureVolume,minT,maxT,sumYError,massEOS,energyEOS",fp);
            forAll(Y,s) std::fprintf(fp,",speciesMass_%s",Y[s].name().c_str());
            std::fputc('\n',fp);
        }
        scalarField speciesMass(Y.size(),Zero);
        forAll(mesh.V(),i) {
            scalar volume=mesh.V()[i],dm=rho[i]*volume;
            mass+=dm;chemical+=dm*hc()[i];sensible+=dm*h[i];
            kinetic+=dm*magSqr(U[i])/2;pv+=p[i]*volume;
            massEOS+=rhoEOS()[i]*volume;
            energyEOS+=rhoEOS()[i]*volume*(thermo.he()[i]+hc()[i]+magSqr(U[i])/2)-p[i]*volume;
            scalar totalY=0;forAll(Y,s) { totalY+=Y[s][i];speciesMass[s]+=dm*Y[s][i]; }
            sumYError=max(sumYError,mag(totalY-1));
        }
        std::fprintf(fp,"%.17g,%d,%d,%.17g,%.17g,%.17g,%.17g,%.17g,%.17g,%.17g,%.17g,%.17g,%.17g,%.17g",
            double(runTime.value()),Pstream::myProcNo(),mesh.nCells(),double(mass),
            double(sensible+chemical+kinetic-pv),double(chemical),double(sensible),double(kinetic),double(pv),
            double(min(T).value()),double(max(T).value()),double(sumYError),double(massEOS),double(energyEOS));
        forAll(speciesMass,s) std::fprintf(fp,",%.17g",double(speciesMass[s]));
        std::fputc('\n',fp);
    }
    std::fclose(fp);return 0;
}
