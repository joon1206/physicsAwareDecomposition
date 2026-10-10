/* GPL-3.0-or-later. Known fixed-volume source-path verification control.
   Native reaction rates and ODE interface; modified RHS/Jacobian are scoped in
   docs/candidates/isochoricChemistry.md. No accepted solver is replaced. */
#ifndef cvOde_H
#define cvOde_H
#include "chemistrySolver.H"
#include "ODESolver.H"
#include "OSspecific.H"
#include <cstdio>
#include <cmath>
#include <limits>
namespace Foam
{
template<class ChemistryModel>
class cvOde : public chemistrySolver<ChemistryModel>
{
    dictionary coefficients_;
    bool constantVolume_;
    mutable autoPtr<ODESolver> integrator_;
    mutable scalarField state_;
    mutable label calls_=0;
    std::FILE* trace_=nullptr;
    scalar gasConstant() const
    {return this->specieThermo()[0].R()*this->specieThermo()[0].W();}
    void invariants(const scalarField& q,scalar& rho,scalar& energy,scalar& pressure) const
    {
        const label n=this->nSpecie();rho=0;energy=0;scalar total=0;
        for(label i=0;i<n;++i){rho+=q[i]*this->specieThermo()[i].W();total+=q[i];}
        pressure=gasConstant()*q[n]*total;
        for(label i=0;i<n;++i)energy+=q[i]*this->specieThermo()[i].ea(pressure,q[n]);
    }
public:
    TypeName("cvOde");
    explicit cvOde(typename ChemistryModel::reactionThermo& thermo)
    :chemistrySolver<ChemistryModel>(thermo),coefficients_(this->subDict("odeCoeffs")),
     constantVolume_(this->template getOrDefault<word>("odeThermalPath","constantVolume")=="constantVolume"),
     integrator_(ODESolver::New(*this,coefficients_)),state_(this->nEqns())
    {
        const word path=this->template getOrDefault<word>("odeThermalPath","constantVolume");
        if(path!="constantVolume" && path!="constantPressure")
            FatalErrorInFunction<<"odeThermalPath must be constantVolume or constantPressure"<<exit(FatalError);
        fileName dir(this->mesh().time().path()/"postProcessing"/"cvChemistry");mkDir(dir);
        char name[40];std::snprintf(name,sizeof(name),"rank%04d.csv",Pstream::myProcNo());
        trace_=std::fopen((dir/name).c_str(),"w");
        if(!trace_)FatalErrorInFunction<<"Cannot open cvOde diagnostics"<<exit(FatalError);
        std::fputs("time,call,deltaT,Tinitial,Tfinal,rhoInitial,rhoFinal,energyInitial,energyFinal,pInitial,pIntegrated,pEOS,minConcentration\n",trace_);
    }
    virtual ~cvOde(){if(trace_)std::fclose(trace_);}
    virtual void derivatives(const scalar time,const scalarField& q,scalarField& f) const override
    {
        const label n=this->nSpecie();const scalar temperature=q[n];
        if(!std::isfinite(temperature) || temperature<=0)
            FatalErrorInFunction<<"Invalid cvOde stage temperature "<<temperature<<exit(FatalError);
        scalarField concentrations(n);scalar total=0;
        // Inherited native rate safeguard is retained for internal ODE stages.
        for(label i=0;i<n;++i){concentrations[i]=max(q[i],scalar(0));total+=concentrations[i];}
        const scalar pressure=constantVolume_ ? gasConstant()*temperature*total : q[n+1];
        this->omega(concentrations,temperature,pressure,f);
        scalar capacity=0,numerator=0,totalRate=0;
        for(label i=0;i<n;++i)
        {
            capacity+=concentrations[i]*(constantVolume_ ? this->specieThermo()[i].cv(pressure,temperature) : this->specieThermo()[i].cp(pressure,temperature));
            numerator+=(constantVolume_ ? this->specieThermo()[i].ea(pressure,temperature) : this->specieThermo()[i].ha(pressure,temperature))*f[i];
            totalRate+=f[i];
        }
        if(!std::isfinite(capacity) || capacity<=0)
            FatalErrorInFunction<<"Nonpositive cvOde heat capacity "<<capacity<<exit(FatalError);
        f[n]=-numerator/capacity;
        f[n+1]=constantVolume_ ? gasConstant()*(temperature*totalRate+total*f[n]) : 0;
    }
    virtual void jacobian(const scalar time,const scalarField& q,scalarField& f,scalarSquareMatrix& jac) const override
    {
        derivatives(time,q,f);jac=Zero;const label n=this->nSpecie();scalar total=0;
        for(label i=0;i<n;++i)total+=mag(q[i]);
        const scalar epsilon=std::sqrt(std::numeric_limits<scalar>::epsilon());
        scalarField plus(q),minus(q),fp(q.size()),fm(q.size());
        for(label j=0;j<q.size();++j)
        {
            const scalar scale=j<n ? max(mag(q[j]),max(total*1e-3,scalar(1e-20))) : max(mag(q[j]),scalar(1));
            const scalar step=epsilon*scale;
            plus=q;plus[j]+=step;derivatives(time,plus,fp);
            if(j>=n || q[j]>step)
            {
                minus=q;minus[j]-=step;derivatives(time,minus,fm);
                for(label i=0;i<q.size();++i)jac(i,j)=(fp[i]-fm[i])/(2*step);
            }
            else for(label i=0;i<q.size();++i)jac(i,j)=(fp[i]-f[i])/step;
        }
    }
    virtual void solve(scalarField& c,scalar& temperature,scalar& pressure,scalar& deltaT,scalar& subDeltaT) const override
    {
        const label n=this->nSpecie();
        for(label i=0;i<n;++i)state_[i]=c[i];
        state_[n]=temperature;state_[n+1]=pressure;
        const scalar initialT=temperature,initialP=pressure;
        scalar rho0,energy0,p0;invariants(state_,rho0,energy0,p0);
        integrator_->solve(0,deltaT,state_,subDeltaT);
        scalar rho1,energy1,p1;invariants(state_,rho1,energy1,p1);scalar total=0,minC=GREAT;
        for(label i=0;i<n;++i){total+=mag(state_[i]);minC=min(minC,state_[i]);}
        if(minC < -max(total*1e-12,scalar(1e-20)))
            FatalErrorInFunction<<"Significant negative accepted cvOde concentration "<<minC<<exit(FatalError);
        for(label i=0;i<n;++i)c[i]=state_[i]; // Accepted output is not clipped.
        temperature=state_[n];const scalar integratedP=state_[n+1];pressure=constantVolume_ ? p1 : integratedP;
        ++calls_;
        std::fprintf(trace_,"%.17g,%d,%.17g,%.17g,%.17g,%.17g,%.17g,%.17g,%.17g,%.17g,%.17g,%.17g,%.17g\n",
            double(this->mesh().time().value()),calls_,double(deltaT),double(initialT),double(temperature),
            double(rho0),double(rho1),double(energy0),double(energy1),double(initialP),double(integratedP),double(p1),double(minC));
        std::fflush(trace_);
    }
};
}
#endif
