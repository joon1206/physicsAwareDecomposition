/* GPL-3.0-or-later. Direct source branch/invariant diagnostic, no CFD method. */
#include "fvCFD.H"
#include "psiReactionThermo.H"
#include "BasicChemistryModel.H"
#include "ODESystem.H"
#include "ODESolver.H"
#include <cstdio>
#include <cmath>
int main(int argc,char* argv[])
{
    Foam::argList::noParallel();
    #include "setRootCaseLists.H"
    #include "createTime.H"
    #include "createMesh.H"
    auto th=Foam::psiReactionThermo::New(mesh);
    auto chemistry=Foam::BasicChemistryModel<Foam::psiReactionThermo>::New(th());
    const auto* ode=dynamic_cast<const Foam::ODESystem*>(&chemistry());
    if(!ode)FatalErrorInFunction<<"Missing ODESystem"<<Foam::exit(Foam::FatalError);
    auto integrator=Foam::ODESolver::New(*ode,chemistry->subDict("odeCoeffs"));
    const auto& mix=th->composition();const auto& Y=mix.Y();const Foam::label ns=Y.size();
    const Foam::label chunks=runTime.controlDict().getOrDefault<Foam::label>("branchProbeChunks",1000);
    const Foam::scalar tf=runTime.controlDict().getOrDefault<Foam::scalar>("branchProbeEndTime",1e-5),mid=1000,eps=1e-6;
    if(chunks<=0 || tf<=0)FatalErrorInFunction<<"Invalid probe interval"<<Foam::exit(Foam::FatalError);
    const Foam::scalar ru=mix.W(0)*(mix.Cp(0,101325,1100)-mix.Cv(0,101325,1100));
    Foam::scalarField jumps(ns);
    std::FILE* properties=std::fopen((runTime.path()/"branch_properties.csv").c_str(),"w");
    std::FILE* out=std::fopen((runTime.path()/"branch_probe.csv").c_str(),"w");
    if(!properties || !out)FatalErrorInFunction<<"Probe output failed"<<Foam::exit(Foam::FatalError);
    std::fputs("species,molarEnthalpyJump\n",properties);
    forAll(Y,s)
    {
        jumps[s]=mix.W(s)*(mix.Ha(s,101325,mid+eps)-mix.Ha(s,101325,mid-eps)
                   -eps*(mix.Cp(s,101325,mid+eps)+mix.Cp(s,101325,mid-eps)));
        std::fprintf(properties,"%s,%.17g\n",Y[s].name().c_str(),double(jumps[s]));
    }
    auto energy=[&](const Foam::scalarField& q)
    {
        Foam::scalar total=0,value=0;forAll(Y,s)total+=q[s];
        const Foam::scalar p=ru*q[ns]*total;
        forAll(Y,s)value+=q[s]*(mix.W(s)*mix.Ha(s,p,q[ns])-ru*q[ns]);
        return value;
    };
    std::fputs("cell,Tinitial,Tfinal,chunks,energyInitial,energyFinal,estimatedBranchJump,crossings,minAcceptedConcentration,pressureSlotRelativeMismatch\n",out);
    const auto rho=th->rho();
    for(Foam::label cell=0;cell<Foam::min(Foam::label(3),mesh.nCells());++cell)
    {
        Foam::scalarField q(ns+2);forAll(Y,s)q[s]=rho()[cell]*Y[s][cell]/mix.W(s);
        q[ns]=th->T()[cell];q[ns+1]=th->p()[cell];
        const Foam::scalar ti=q[ns],ei=energy(q),dt=tf/chunks;
        Foam::scalar subdt=Foam::min(dt,Foam::scalar(1e-9)),jump=0,minC=Foam::GREAT;Foam::label crossings=0;
        for(Foam::label interval=0;interval<chunks;++interval)
        {
            const Foam::scalarField before(q);integrator->solve(interval*dt,(interval+1)*dt,q,subdt);
            forAll(Y,s)minC=Foam::min(minC,q[s]);
            if((before[ns]<mid && q[ns]>=mid) || (q[ns]<mid && before[ns]>=mid))
            {
                const Foam::scalar fraction=(mid-before[ns])/(q[ns]-before[ns]);
                Foam::scalar crossingJump=0;
                forAll(Y,s)crossingJump+=((1-fraction)*before[s]+fraction*q[s])*jumps[s];
                jump+=(q[ns]>before[ns] ? 1 : -1)*crossingJump;++crossings;
            }
        }
        Foam::scalar total=0;forAll(Y,s)total+=q[s];const Foam::scalar peos=ru*q[ns]*total;
        std::fprintf(out,"%d,%.17g,%.17g,%d,%.17g,%.17g,%.17g,%d,%.17g,%.17g\n",cell,double(ti),double(q[ns]),chunks,
            double(ei),double(energy(q)),double(jump),crossings,double(minC),double(Foam::mag(q[ns+1]-peos)/peos));
    }
    std::fclose(out);std::fclose(properties);return 0;
}
