/* GPL-3.0-or-later. Experimental density-defect corrections; see candidate derivations. */
#include <chrono>
class thermoDensityCorrector
{
    const Foam::fvMesh& mesh_;
    const Foam::Time& time_;
    Foam::word mode_;
    Foam::scalarField rAU_;
    std::FILE* fp_=nullptr;
    Foam::autoPtr<Foam::volScalarField> rAUCoeff_;
    Foam::autoPtr<Foam::volVectorField> HbyACoeff_;
public:
    Foam::scalar momentumMismatch=0,pressureChange=0,cancellationError=0;
    thermoDensityCorrector(const Foam::fvMesh& mesh,const Foam::Time& time)
    :mesh_(mesh),time_(time),mode_(time.controlDict().getOrDefault<Foam::word>("energyCorrection","none"))
    {
        if(mode_!="none" && mode_!="localInternal" && mode_!="scalarDensity" && mode_!="speciesFlux" && mode_!="conservativeState" && mode_!="blockConservative")
            FatalErrorInFunction<<"Unknown energyCorrection "<<mode_<<Foam::exit(Foam::FatalError);
        Foam::fileName dir(time.path()/"postProcessing"/"thermoCorrection"/time.timeName());Foam::mkDir(dir);
        char n[64];std::snprintf(n,sizeof(n),"rank%04d.csv",Foam::Pstream::myProcNo());fp_=std::fopen((dir/n).c_str(),"w");
        if(!fp_)FatalErrorInFunction<<"Cannot open correction diagnostics"<<Foam::exit(Foam::FatalError);
        std::fputs("time,rank,wall,maxIterations,maxDeltaP,maxMomentumDeltaU,maxCancellationError,maxConservativeEnergyResidual\n",fp_);
    }
    ~thermoDensityCorrector(){if(fp_)std::fclose(fp_);}
    bool active() const{return mode_!="none";}
    void momentumCoefficient(const Foam::volScalarField& rAU){if(active())rAU_=rAU.primitiveField();}
    void momentumState(const Foam::volScalarField& rAU,const Foam::volVectorField& HbyA)
    {
        if(mode_!="blockConservative")return;
        rAUCoeff_.reset(new Foam::volScalarField(Foam::IOobject("frozenRAU",time_.timeName(),mesh_,Foam::IOobject::NO_READ,Foam::IOobject::NO_WRITE,false),rAU));
        HbyACoeff_.reset(new Foam::volVectorField(Foam::IOobject("frozenHbyA",time_.timeName(),mesh_,Foam::IOobject::NO_READ,Foam::IOobject::NO_WRITE,false),HbyA));
    }
    void applyBlock(Foam::volScalarField& rho,Foam::psiReactionThermo& th,Foam::surfaceScalarField& phi,
        const Foam::tmp<Foam::volScalarField>& alpha,Foam::volScalarField& dpdt,
        cellEnergyAudit& audit,const Foam::tmp<Foam::volScalarField>& mu,Foam::volScalarField& K,Foam::volVectorField& U)
    {
        const auto start=std::chrono::steady_clock::now();
        if(!rAUCoeff_.valid() || !HbyACoeff_.valid())FatalErrorInFunction<<"Missing frozen momentum state"<<Foam::exit(Foam::FatalError);
        auto& p=th.p();
        forAll(p.boundaryField(),patch)
            if(!p.boundaryField()[patch].coupled() && mesh_.boundary()[patch].type()!="symmetry" && mesh_.boundary()[patch].type()!="empty")
                FatalErrorInFunction<<"Block prototype restricted to cyclic/symmetry/empty boundaries"<<Foam::exit(Foam::FatalError);
        const Foam::label maximum=time_.controlDict().getOrDefault<Foam::label>("blockMaxIterations",12);
        const Foam::scalar tolerance=time_.controlDict().getOrDefault<Foam::scalar>("blockPressureTolerance",1e-8);
        Foam::scalar energyResidual=0;Foam::label totalIterations=0;
        for(Foam::label iteration=0;iteration<maximum;++iteration)
        {
            Foam::surfaceScalarField rhorAUf("blockRhorAUf",Foam::fvc::interpolate(rho*rAUCoeff_()));
            Foam::surfaceScalarField phiH("blockPhiHbyA",Foam::fvc::flux(rho*HbyACoeff_())+rhorAUf*Foam::fvc::ddtCorr(rho,U,phi));
            Foam::volScalarField massSource(Foam::IOobject("blockMassSource",time_.timeName(),mesh_,Foam::IOobject::NO_READ,Foam::IOobject::NO_WRITE,false),rho/time_.deltaT());
            massSource.primitiveFieldRef()=audit.rhoStart()/time_.deltaTValue();
            Foam::fvScalarMatrix pressureEquation(Foam::fvm::Sp(th.psi()/time_.deltaT(),p)+Foam::fvc::div(phiH)-Foam::fvm::laplacian(rhorAUf,p)==massSource);
            auto performance=pressureEquation.solve(mesh_.solver(p.name()));totalIterations+=performance.nIterations();
            phi=phiH+pressureEquation.flux();U=HbyACoeff_()-rAUCoeff_()*Foam::fvc::grad(p);U.correctBoundaryConditions();K=0.5*Foam::magSqr(U);
            rho=th.rho();
            Foam::volScalarField pMomentum(Foam::IOobject("pBlockMomentum",time_.timeName(),mesh_,Foam::IOobject::NO_READ,Foam::IOobject::NO_WRITE,false),p);
            totalIterations+=audit.remapSpecies(rho,th,phi,mu);
            th.correct();th.correct();p=rho/th.psi();p.correctBoundaryConditions();
            totalIterations+=audit.conservativeEnergy(rho,th,K,phi,alpha,mu,energyResidual);
            Foam::volScalarField deltaP(Foam::IOobject("deltaBlockP",time_.timeName(),mesh_,Foam::IOobject::NO_READ,Foam::IOobject::NO_WRITE,false),p-pMomentum);
            auto grad=Foam::fvc::grad(deltaP);Foam::scalar relativeChange=0;
            momentumMismatch=0;pressureChange=0;
            forAll(rho,i)
            {
                pressureChange=Foam::max(pressureChange,Foam::mag(deltaP[i]));
                relativeChange=Foam::max(relativeChange,Foam::mag(deltaP[i])/Foam::max(Foam::mag(p[i]),Foam::SMALL));
                momentumMismatch=Foam::max(momentumMismatch,rAU_[i]*Foam::mag(grad()[i]));
            }
            relativeChange=Foam::returnReduce(relativeChange,Foam::maxOp<Foam::scalar>());
            if(relativeChange<tolerance)
            {
                if(th.dpdt())dpdt=Foam::fvc::ddt(p);
                const double wall=std::chrono::duration<double>(std::chrono::steady_clock::now()-start).count();
                std::fprintf(fp_,"%.17g,%d,%.17g,%d,%.17g,%.17g,0,%.17g\n",double(time_.value()),Foam::Pstream::myProcNo(),wall,totalIterations,double(pressureChange),double(momentumMismatch),double(energyResidual));std::fflush(fp_);
                return;
            }
        }
        FatalErrorInFunction<<"Frozen-source block did not converge in "<<maximum<<" iterations"<<Foam::exit(Foam::FatalError);
    }
    Foam::scalar property(Foam::psiReactionThermo& th,Foam::label i,Foam::scalar T,bool heatCapacity) const
    {
        auto& mixture=th.composition();Foam::scalar value=0;
        forAll(mixture.Y(),s)value+=mixture.Y()[s][i]*(heatCapacity ? mixture.Cp(s,th.p()[i],T):mixture.Ha(s,th.p()[i],T));
        return value;
    }
    void apply(Foam::volScalarField& rho,Foam::psiReactionThermo& th,Foam::surfaceScalarField& phi,
        const Foam::tmp<Foam::volScalarField>& alpha,Foam::volScalarField& dpdt,
        const Foam::scalarField& ra,const Foam::scalarField& hb,const Foam::scalarField& cb,
        cellEnergyAudit& audit,const Foam::tmp<Foam::volScalarField>& mu,Foam::volScalarField& K,Foam::volVectorField& U)
    {
        momentumMismatch=0;pressureChange=0;cancellationError=0;if(!active())return;
        if(mode_=="blockConservative"){applyBlock(rho,th,phi,alpha,dpdt,audit,mu,K,U);return;}
        const auto start=std::chrono::steady_clock::now();Foam::label maxIterations=0;
        if(rAU_.size()!=rho.size())FatalErrorInFunction<<"Missing momentum coefficient"<<Foam::exit(Foam::FatalError);
        auto& h=th.he();auto& p=th.p();
        Foam::volScalarField pBefore(Foam::IOobject("pBeforeCorrection",time_.timeName(),mesh_,Foam::IOobject::NO_READ,Foam::IOobject::NO_WRITE,false),p);
        Foam::scalar conservativeResidual=0;
        if(mode_=="speciesFlux" || mode_=="conservativeState")
        {
            maxIterations=audit.remapSpecies(rho,th,phi,mu);
            h.correctBoundaryConditions();th.correct();th.correct();p=rho/th.psi();p.correctBoundaryConditions();
        }
        if(mode_=="conservativeState")
            maxIterations+=audit.conservativeEnergy(rho,th,K,phi,alpha,mu,conservativeResidual);
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
        std::fprintf(fp_,"%.17g,%d,%.17g,%d,%.17g,%.17g,%.17g,%.17g\n",double(time_.value()),Foam::Pstream::myProcNo(),wall,maxIterations,double(pressureChange),double(momentumMismatch),double(cancellationError),double(conservativeResidual));std::fflush(fp_);
    }
};
