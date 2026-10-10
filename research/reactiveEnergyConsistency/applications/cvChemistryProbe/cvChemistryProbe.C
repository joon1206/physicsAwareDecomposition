/* GPL-3.0-or-later. Independent ODESystem interface/invariant verification. */
#include "fvCFD.H"
#include "psiReactionThermo.H"
#include "BasicChemistryModel.H"
#include "ODESystem.H"
#include <cstdio>
#include <cmath>
int main(int argc,char* argv[])
{
    Foam::argList::noParallel();
    #include "setRootCaseLists.H"
    #include "createTime.H"
    #include "createMesh.H"
    auto th=Foam::psiReactionThermo::New(mesh);
    auto chem=Foam::BasicChemistryModel<Foam::psiReactionThermo>::New(th());
    const auto* ode=dynamic_cast<const Foam::ODESystem*>(&chem());
    if(!ode)FatalErrorInFunction<<"Selected chemistry is not an ODESystem"<<Foam::exit(Foam::FatalError);
    const bool cv=chem->getOrDefault<Foam::word>("odeThermalPath","constantVolume")=="constantVolume";
    const auto& mix=th->composition();const auto& Y=mix.Y();const Foam::label ns=Y.size(),n=ns+2;
    if(ode->nEqns()!=n)FatalErrorInFunction<<"Unexpected ODE dimensions"<<Foam::exit(Foam::FatalError);
    const auto rho=th->rho();
    std::FILE* out=std::fopen((runTime.path()/"cv_ode_probe.csv").c_str(),"w");
    if(!out)FatalErrorInFunction<<"Cannot write probe"<<Foam::exit(Foam::FatalError);
    std::fputs("cell,T,path,timeDerivativeMax,directionalJacobianRelativeError,massResidualRelative,thermalResidualRelative,pressureResidualRelative\n",out);
    forAll(th->T(),cell)
    {
        const Foam::scalar T=th->T()[cell],p=th->p()[cell];
        const Foam::scalar ru=mix.W(0)*(mix.Cp(0,p,T)-mix.Cv(0,p,T));
        Foam::scalarField q(n),f(n),fp(n),fm(n),dfdt(n),direction(n);Foam::scalar total=0;
        forAll(Y,s){q[s]=rho()[cell]*Y[s][cell]/mix.W(s);total+=q[s];}
        // Probe a smooth, positive concentration state, including trace species.
        forAll(Y,s)q[s]=Foam::max(q[s],total*1e-4);
        q[ns]=T;q[ns+1]=p;total=0;forAll(Y,s)total+=q[s];
        Foam::scalarSquareMatrix jac(n);ode->derivatives(.3,q,f);ode->jacobian(.3,q,dfdt,jac);
        ode->derivatives(.301,q,fp);ode->derivatives(.299,q,fm);
        Foam::scalar timeError=0;
        forAll(q,i)timeError=Foam::max(timeError,Foam::max(Foam::mag(dfdt[i]),Foam::mag((fp[i]-fm[i])/.002)));
        forAll(Y,s)direction[s]=(q[s]+total*.001)*std::sin(.7*(s+1));
        direction[ns]=200;direction[ns+1]=.1*p;
        const Foam::scalar step=1e-5;Foam::scalarField plus(q),minus(q);
        forAll(q,i){plus[i]+=step*direction[i];minus[i]-=step*direction[i];}
        ode->derivatives(.3,plus,fp);ode->derivatives(.3,minus,fm);
        Foam::scalar jacError=0,jacScale=1e-30;
        forAll(q,i)
        {
            Foam::scalar action=0;forAll(q,j)action+=jac(i,j)*direction[j];
            const Foam::scalar fd=(fp[i]-fm[i])/(2*step);
            jacError=Foam::max(jacError,Foam::mag(action-fd));
            jacScale=Foam::max(jacScale,Foam::max(Foam::mag(action),Foam::mag(fd)));
        }
        Foam::scalar mass=0,massScale=1e-30,thermal=0,thermalScale=1e-30,capacity=0,totalRate=0;
        forAll(Y,s)
        {
            const Foam::scalar W=mix.W(s),massTerm=W*f[s];mass+=massTerm;massScale+=Foam::mag(massTerm);
            const Foam::scalar energy=W*mix.Ha(s,p,T)-(cv ? ru*T : 0);
            const Foam::scalar term=energy*f[s];thermal+=term;thermalScale+=Foam::mag(term);
            capacity+=q[s]*W*(cv ? mix.Cv(s,p,T) : mix.Cp(s,p,T));totalRate+=f[s];
        }
        thermal+=capacity*f[ns];thermalScale+=Foam::mag(capacity*f[ns]);
        const Foam::scalar expectedP=cv ? ru*(T*totalRate+total*f[ns]) : 0;
        const Foam::scalar pError=Foam::mag(f[ns+1]-expectedP)/Foam::max(Foam::max(Foam::mag(f[ns+1]),Foam::mag(expectedP)),Foam::scalar(1));
        const Foam::scalar jError=jacError/jacScale,mError=Foam::mag(mass)/massScale,eError=Foam::mag(thermal)/thermalScale;
        std::fprintf(out,"%d,%.17g,%s,%.17g,%.17g,%.17g,%.17g,%.17g\n",cell,double(T),cv ? "constantVolume" : "constantPressure",double(timeError),double(jError),double(mError),double(eError),double(pError));
        if(timeError!=0 || jError>1e-4 || mError>1e-12 || eError>1e-12 || pError>1e-12)
            FatalErrorInFunction<<"ODE interface/invariant probe failed in cell "<<cell<<Foam::exit(Foam::FatalError);
    }
    std::fclose(out);return 0;
}
