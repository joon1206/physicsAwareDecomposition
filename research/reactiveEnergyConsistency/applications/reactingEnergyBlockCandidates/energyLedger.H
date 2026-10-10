/* GPL-3.0-or-later. Read-only equation and stage diagnostics, OpenCFD v2012. */
#include <cstdio>
class energyLedger
{
    const Foam::fvMesh& mesh_;
    const Foam::Time& time_;
    std::FILE *stages_=nullptr, *budget_=nullptr;
    Foam::label step_=0, outer_=0, pressure_=0;
    Foam::scalar Hn_=0,Jn_=0,Cn_=0,Pn_=0,Ha_=0,Ja_=0,Ca_=0;
    Foam::scalar W_=0,Q_=0,Bk_=0,R_=0,Bh_=0,Lh_=0,history_=0;
    Foam::scalarField rhoa_,ha_,hca_;
public:
    bool enabled;
    energyLedger(const Foam::fvMesh& mesh,const Foam::Time& time,
                 const Foam::PtrList<Foam::volScalarField>& Y)
    : mesh_(mesh),time_(time),enabled(time.controlDict().getOrDefault<bool>("energyLedger",true))
    {
        if(!enabled) return;
        Foam::fileName dir(time.path()/"postProcessing"/"energyLedger"/time.timeName());
        Foam::mkDir(dir);
        char name[80];std::snprintf(name,sizeof(name),"stages_rank%04d.csv",Foam::Pstream::myProcNo());
        stages_=std::fopen((dir/name).c_str(),"w");
        std::snprintf(name,sizeof(name),"budget_rank%04d.csv",Foam::Pstream::myProcNo());
        budget_=std::fopen((dir/name).c_str(),"w");
        if(!stages_ || !budget_) FatalErrorInFunction << "Cannot open energy ledger" << Foam::exit(Foam::FatalError);
        std::fputs("step,time,dt,rank,outer,pressure,stage,mass,H,C,J,P,E,massEOS,Q,W,minT,minP,minY,sumYError",stages_);
        forAll(Y,s) std::fprintf(stages_,",speciesMass_%s",Y[s].name().c_str());
        std::fputc('\n',stages_);
        std::fputs("step,time,dt,rank,outer,DE,Dpressure,Dkinetic,DrhoH,DrhoC,DspeciesChemistry,Dequation,Dtransport,Dhistory,closure,Q,W,Bh,Bk,Lh,continuityL1,DpostH,DpostC\n",budget_);
    }
    ~energyLedger(){if(stages_)std::fclose(stages_);if(budget_)std::fclose(budget_);}
    Foam::scalar integrate(const Foam::scalarField& f) const
    {return Foam::sum(mesh_.V()*f);}
    // Evaluate the actual scalar matrix once per boundary contribution.
    // v2012 fvScalarMatrix::residual adds coupled neighbour sources after
    // lduMatrix::residual has already included the coupled interfaces.
    Foam::scalar lhsMinusRhs(const Foam::fvScalarMatrix& m) const
    {
        const auto& h=m.psi().primitiveField();
        Foam::scalar r=Foam::sum(m.diag()*h-m.source());
        if(m.hasUpper())
        {
            const auto& owner=m.lduAddr().lowerAddr();
            const auto& neighbour=m.lduAddr().upperAddr();
            forAll(owner,f)r+=m.upper()[f]*h[neighbour[f]]+m.lower()[f]*h[owner[f]];
        }
        forAll(m.psi().boundaryField(),p)
        {
            const auto& patch=m.psi().boundaryField()[p];
            const auto& cells=mesh_.boundary()[p].faceCells();
            forAll(cells,f)r+=m.internalCoeffs()[p][f]*h[cells[f]];
            if(patch.coupled())
            {
                auto neighbour=patch.patchNeighbourField();
                r-=Foam::sum(m.boundaryCoeffs()[p]*neighbour());
            }
            else r-=Foam::sum(m.boundaryCoeffs()[p]);
        }
        return r;
    }
    void snapshot(const char* stage,const Foam::volScalarField& rho,
        Foam::psiReactionThermo& thermo,const Foam::volScalarField& K,
        const Foam::volScalarField& Qdot,const Foam::volScalarField& dpdt)
    {
        if(!enabled)return;
        const auto& Y=thermo.composition().Y();auto hc=thermo.hc();auto eos=thermo.rho();
        Foam::scalar H=integrate(rho.primitiveField()*thermo.he().primitiveField());
        Foam::scalar C=integrate(rho.primitiveField()*hc().primitiveField());
        Foam::scalar J=integrate(rho.primitiveField()*K.primitiveField());
        Foam::scalar P=integrate(thermo.p().primitiveField());
        Foam::scalar minY=Foam::GREAT,sumYError=0;
        forAll(rho,c){Foam::scalar sy=0;forAll(Y,s){sy+=Y[s][c];minY=Foam::min(minY,Y[s][c]);}sumYError=Foam::max(sumYError,Foam::mag(sy-1));}
        std::fprintf(stages_,"%d,%.17g,%.17g,%d,%d,%d,%s,%.17g,%.17g,%.17g,%.17g,%.17g,%.17g,%.17g,%.17g,%.17g,%.17g,%.17g,%.17g,%.17g",
            step_,double(time_.value()),double(time_.deltaTValue()),Foam::Pstream::myProcNo(),outer_,pressure_,stage,
            double(integrate(rho.primitiveField())),double(H),double(C),double(J),double(P),double(H+C+J-P),
            double(integrate(eos().primitiveField())),double(integrate(Qdot.primitiveField())),double(integrate(dpdt.primitiveField())),
            double(Foam::min(thermo.T().primitiveField())),double(Foam::min(thermo.p().primitiveField())),double(minY),double(sumYError));
        forAll(Y,s)std::fprintf(stages_,",%.17g",double(integrate(rho.primitiveField()*Y[s].primitiveField())));
        std::fputc('\n',stages_);
    }
    void start(const Foam::volScalarField& rho,Foam::psiReactionThermo& thermo,
        const Foam::volScalarField& K,const Foam::volScalarField& Qdot,const Foam::volScalarField& dpdt)
    {
        if(!enabled)return;
        ++step_;outer_=0;pressure_=0;
        auto hc=thermo.hc();Hn_=integrate(rho.primitiveField()*thermo.he().primitiveField());
        Cn_=integrate(rho.primitiveField()*hc().primitiveField());Jn_=integrate(rho.primitiveField()*K.primitiveField());Pn_=integrate(thermo.p().primitiveField());
        snapshot("timestep_start",rho,thermo,K,Qdot,dpdt);
    }
    void outer(){if(enabled){++outer_;pressure_=0;}}
    void pressure(){if(enabled)++pressure_;}
    void assemble(const Foam::volScalarField& rho,Foam::psiReactionThermo& thermo,
        const Foam::volScalarField& K,const Foam::volScalarField& Qdot,const Foam::volScalarField& dpdt,
        const Foam::surfaceScalarField& phi)
    {
        if(!enabled)return;
        rhoa_=rho.primitiveField();Ja_=integrate(rhoa_*K.primitiveField());
        W_=integrate(dpdt.primitiveField());Q_=integrate(Qdot.primitiveField());
        auto divK=Foam::fvc::div(phi,K);Bk_=integrate(divK().primitiveField());
        history_=integrate(rho.oldTime().primitiveField()*thermo.he().oldTime().primitiveField())
                +integrate(rho.oldTime().primitiveField()*K.oldTime().primitiveField())-Hn_-Jn_;
    }
    void solved(const Foam::fvScalarMatrix& original,const Foam::fvScalarMatrix& convection,
        const Foam::fvScalarMatrix& diffusion,Foam::psiReactionThermo& thermo)
    {
        if(!enabled)return;
        ha_=thermo.he().primitiveField();auto hc=thermo.hc();hca_=hc().primitiveField();
        Ha_=integrate(rhoa_*ha_);Ca_=integrate(rhoa_*hca_);
        R_=lhsMinusRhs(original);Bh_=lhsMinusRhs(convection);Lh_=lhsMinusRhs(diffusion);
    }
    void finish(const Foam::volScalarField& rho,Foam::psiReactionThermo& thermo,
        const Foam::volScalarField& K,const Foam::volScalarField& Qdot,const Foam::volScalarField& dpdt,
        const Foam::surfaceScalarField& phi)
    {
        if(!enabled)return;
        const Foam::scalar dt=time_.deltaTValue();auto hc=thermo.hc();
        Foam::scalar Hf=integrate(rho.primitiveField()*thermo.he().primitiveField());
        Foam::scalar Cf=integrate(rho.primitiveField()*hc().primitiveField());
        Foam::scalar Jf=integrate(rho.primitiveField()*K.primitiveField());Foam::scalar Pf=integrate(thermo.p().primitiveField());
        Foam::scalar DE=Hf+Cf+Jf-Pf-(Hn_+Cn_+Jn_-Pn_);
        Foam::scalar Dp=dt*W_-(Pf-Pn_),Dk=Jf-Ja_;
        Foam::scalar Dh=integrate((rho.primitiveField()-rhoa_)*ha_);
        Foam::scalar Dc=integrate((rho.primitiveField()-rhoa_)*hca_);
        Foam::scalar DpostH=integrate(rho.primitiveField()*(thermo.he().primitiveField()-ha_));
        Foam::scalar DpostC=integrate(rho.primitiveField()*(hc().primitiveField()-hca_));
        Foam::scalar Ds=Ca_-Cn_+dt*Q_,Dr=dt*R_,Db=-dt*(Bh_+Bk_-Lh_);
        auto cr=Foam::fvc::ddt(rho)+Foam::fvc::div(phi);Foam::scalar cont=integrate(Foam::mag(cr().primitiveField()));
        std::fprintf(budget_,"%d,%.17g,%.17g,%d,%d,%.17g,%.17g,%.17g,%.17g,%.17g,%.17g,%.17g,%.17g,%.17g,%.17g,%.17g,%.17g,%.17g,%.17g,%.17g,%.17g,%.17g,%.17g\n",
            step_,double(time_.value()),double(dt),Foam::Pstream::myProcNo(),outer_,double(DE),double(Dp),double(Dk),double(Dh),double(Dc),double(Ds),double(Dr),double(Db),double(history_),
            double(DE-Dp-Dk-Dh-Dc-Ds-Dr-Db-history_-DpostH-DpostC),double(Q_),double(W_),double(Bh_),double(Bk_),double(Lh_),double(cont),double(DpostH),double(DpostC));
        snapshot("timestep_end",rho,thermo,K,Qdot,dpdt);
        std::fflush(stages_);std::fflush(budget_);
    }
};
