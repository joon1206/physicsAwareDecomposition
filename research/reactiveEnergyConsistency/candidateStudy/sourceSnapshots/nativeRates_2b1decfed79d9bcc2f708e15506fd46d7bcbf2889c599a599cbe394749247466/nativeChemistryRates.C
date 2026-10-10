/* GPL-3.0-or-later. Independent instantaneous chemistry/EOS reference inventory. */
#include "fvCFD.H"
#include "psiReactionThermo.H"
#include "BasicChemistryModel.H"
#include <cstdio>
int main(int argc,char* argv[])
{
    Foam::argList::noParallel();
    #include "setRootCaseLists.H"
    #include "createTime.H"
    #include "createMesh.H"
    auto th=Foam::psiReactionThermo::New(mesh);
    auto chem=Foam::BasicChemistryModel<Foam::psiReactionThermo>::New(th());
    chem->calculate();auto& Y=th->composition().Y();
    std::FILE* f=std::fopen((runTime.path()/"instantaneous_rates.csv").c_str(),"w");
    if(!f)FatalErrorInFunction<<"Cannot open rates output"<<Foam::exit(Foam::FatalError);
    std::fputs("T,p,rho,Cp,Cv",f);forAll(Y,s)std::fprintf(f,",RR_%s",Y[s].name().c_str());std::fputc('\n',f);
    auto rho=th->rho();auto cp=th->Cp();auto cv=th->Cv();
    forAll(Y[0],i)
    {
        std::fprintf(f,"%.17g,%.17g,%.17g,%.17g,%.17g",double(th->T()[i]),double(th->p()[i]),double(rho()[i]),double(cp()[i]),double(cv()[i]));
        forAll(Y,s)std::fprintf(f,",%.17g",double(chem->RR(s)[i]));std::fputc('\n',f);
    }
    std::fclose(f);return 0;
}
