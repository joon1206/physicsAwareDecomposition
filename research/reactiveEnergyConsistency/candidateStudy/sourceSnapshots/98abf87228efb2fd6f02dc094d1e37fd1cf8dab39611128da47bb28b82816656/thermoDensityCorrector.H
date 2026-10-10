/* GPL-3.0-or-later. Experimental density-defect corrections; see candidate derivations. */
#include <chrono>
class thermoDensityCorrector
{
    const Foam::fvMesh& mesh_;
    const Foam::Time& time_;
    Foam::word mode_;
    Foam::scalarField rAU_;
    std::FILE* fp_=nullptr;
public:
    Foam::scalar momentumMismatch=0,pressureChange=0,cancellationError=0;
    thermoDensityCorrector(const Foam::fvMesh& mesh,const Foam::Time& time)
    :mesh_(mesh),time_(time),mode_(time.controlDict().getOrDefault<Foam::word>("energyCorrection","none"))
    {
        if(mode_!="none" && mode_!="localInternal" && mode_!="scalarDensity" && mode_!="speciesFlux")
            FatalErrorInFunction<<"Unknown energyCorrection "<<mode_<<Foam::exit(Foam::FatalError);
        Foam::fileName dir(time.path()/"postProcessing"/"thermoCorrection"/time.timeName());Foam::mkDir(dir);
        char n[64];std::snprintf(n,sizeof(n),"rank%04d.csv",Foam::Pstream::myProcNo());fp_=std::fopen((dir/n).c_str(),"w");
        if(!fp_)FatalErrorInFunction<<"Cannot open correction diagnostics"<<Foam::exit(Foam::FatalError);
        std::fputs("time,rank,wall,maxIterations,maxDeltaP,maxMomentumDeltaU,maxCancellationError\n",fp_);
    }
    ~thermoDensityCorrector(){if(fp_)std::fclose(fp_);}
    bool active() const{return mode_!="none";}
    void momentumCoefficient(const Foam::volScalarField& rAU){if(active())rAU_=rAU.primitiveField();}
    Foam::scalar property(Foam::psiReactionThermo& th,Foam::label i,Foam::scalar T,bool heatCapacity) const
    {
        auto& mixture=th.composition();Foam::scalar value=0;
        forAll(mixture.Y(),s)value+=mixture.Y()[s][i]*(heatCapacity ? mixture.Cp(s,th.p()[i],T):mixture.Ha(s,th.p()[i],T));
        return value;
    }
    void apply(Foam::volScalarField& rho,Foam::psiReactionThermo& th,const Foam::surfaceScalarField& phi,
        const Foam::tmp<Foam::volScalarField>& alpha,Foam::volScalarField& dpdt,
        const Foam::scalarField& ra,const Foam::scalarField& hb,const Foam::scalarField& cb,
        cellEnergyAudit& audit,const Foam::tmp<Foam::volScalarField>& mu)
    {
        momentumMismatch=0;pressureChange=0;cancellationError=0;if(!active())return;
        const auto start=std::chrono::steady_clock::now();Foam::label maxIterations=0;
        if(rAU_.size()!=rho.size())FatalErrorInFunction<<"Missing momentum coefficient"<<Foam::exit(Foam::FatalError);
        auto& h=th.he();auto& p=th.p();
        Foam::volScalarField pBefore(Foam::IOobject("pBeforeCorrection",time_.timeName(),mesh_,Foam::IOobject::NO_READ,Foam::IOobject::NO_WRITE,false),p);
        if(mode_=="speciesFlux")maxIterations=audit.remapSpecies(rho,th,phi,mu);
        Foam::scalarField R(1/(th.psi().primitiveField()*th.T().primitiveField()));
        if(mode_=="localInternal")
        {
            const Foam::scalar Tmin=time_.controlDict().getOrDefault<Foam::scalar>("correctionTmin",200);
            const Foam::scalar Tmax=time_.controlDict().getOrDefault<Foam::scalar>("correctionTmax",5000);
            forAll(rho,i)
            {
                if(rho[i]<=0)FatalErrorInFunction<<"Nonpositive density"<<Foam::exit(Foam::FatalError);
                const Foam::scalar target=(ra[i]*(hb[i]+cb[i])-p[i])/rho[i];
                Foam::scalar lo=Tmin,hi=Tmax,T=Foam::min(hi,Foam::max(lo,th.T()[i]));
                const Foam::scalar elo=property(th,i,lo,false)-R[i]*lo;
                const Foam::scalar ehi=property(th,i,hi,false)-R[i]*hi;
                if(target<elo || target>ehi)
                    FatalErrorInFunction<<"Unattainable local energy target at cell "<<i<<": "<<target<<" outside "<<elo<<","<<ehi<<Foam::exit(Foam::FatalError);
                bool converged=false;
                for(Foam::label it=0;it<80;++it)
                {
                    const Foam::scalar residual=property(th,i,T,false)-R[i]*T-target;
                    maxIterations=Foam::max(maxIterations,it+1);
                    if(Foam::mag(residual)<1e-8+1e-13*Foam::mag(target)){converged=true;break;}
                    if(residual>0)hi=T;else lo=T;
                    const Foam::scalar cv=property(th,i,T,true)-R[i];
                    if(cv<=0)FatalErrorInFunction<<"Nonpositive Cv"<<Foam::exit(Foam::FatalError);
                    const Foam::scalar trial=T-residual/cv;
                    T=(trial>lo && trial<hi)?trial:0.5*(lo+hi);
                }
                if(!converged)FatalErrorInFunction<<"Local projection did not converge"<<Foam::exit(Foam::FatalError);
                h[i]=property(th,i,T,false)-cb[i];
            }
        }
        else if(mode_=="scalarDensity")
        {
            Foam::volScalarField deltaH(Foam::IOobject("deltaH",time_.timeName(),mesh_,Foam::IOobject::NO_READ,Foam::IOobject::NO_WRITE,false),h);
            deltaH=Foam::dimensionedScalar("zero",h.dimensions(),0);
            Foam::volScalarField capacity(Foam::IOobject("energyCapacity",time_.timeName(),mesh_,Foam::IOobject::NO_READ,Foam::IOobject::NO_WRITE,false),rho);
            forAll(rho,i)capacity[i]=rho[i]*(1-R[i]/property(th,i,th.T()[i],true));
            if(Foam::min(capacity.primitiveField())<=0)FatalErrorInFunction<<"Nonpositive correction capacity"<<Foam::exit(Foam::FatalError);
            capacity.correctBoundaryConditions();
            Foam::volScalarField source(Foam::IOobject("densityEnergySource",time_.timeName(),mesh_,Foam::IOobject::NO_READ,Foam::IOobject::NO_WRITE,false),mesh_,Foam::dimensionedScalar("zero",rho.dimensions()*h.dimensions()/Foam::dimTime,0));
            source.primitiveFieldRef()=-(rho.primitiveField()-ra)*(hb+cb)/time_.deltaTValue();
            Foam::fvScalarMatrix correction(Foam::fvm::Sp(capacity/time_.deltaT(),deltaH)
                +Foam::fvm::div(phi,deltaH,"div(phi,deltaH)")-Foam::fvm::laplacian(alpha(),deltaH)==source);
            auto performance=correction.solve(mesh_.solver(h.name()));maxIterations=performance.nIterations();
            h+=deltaH;
        }
        h.correctBoundaryConditions();th.correct();th.correct();p=rho/th.psi();p.correctBoundaryConditions();
        if(th.dpdt())dpdt=Foam::fvc::ddt(p);
        Foam::volScalarField deltaP(Foam::IOobject("deltaPcorrection",time_.timeName(),mesh_,Foam::IOobject::NO_READ,Foam::IOobject::NO_WRITE,false),p-pBefore);
        auto grad=Foam::fvc::grad(deltaP);
        forAll(rho,i)
        {
            pressureChange=Foam::max(pressureChange,Foam::mag(deltaP[i]));
            momentumMismatch=Foam::max(momentumMismatch,rAU_[i]*Foam::mag(grad()[i]));
            const Foam::scalar defect=(rho[i]-ra[i])*(hb[i]+cb[i])+rho[i]*(h[i]-hb[i])-deltaP[i];
            cancellationError=Foam::max(cancellationError,Foam::mag(mesh_.V()[i]*defect));
        }
        const double wall=std::chrono::duration<double>(std::chrono::steady_clock::now()-start).count();
        std::fprintf(fp_,"%.17g,%d,%.17g,%d,%.17g,%.17g,%.17g\n",double(time_.value()),Foam::Pstream::myProcNo(),wall,maxIterations,double(pressureChange),double(momentumMismatch),double(cancellationError));std::fflush(fp_);
    }
};
