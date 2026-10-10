/* GPL-3.0-or-later. Cellwise Euler equation audit, independent of corrections. */
#include <cstdio>
#include <limits>
class cellEnergyAudit
{
    const Foam::fvMesh& mesh_;
    const Foam::Time& time_;
    Foam::label step_=0,every_;
    std::FILE *fp_=nullptr,*totals_=nullptr;
    Foam::scalarField rn_,hn_,cn_,kn_,pn_,ra_,ha_,ca_,ka_,pa_,w_,q_,bk_,history_;
    Foam::scalarField eq_,bh_,lh_,chem_,spTransport_,spResidual_,boundary_;
    Foam::List<Foam::scalarField> yn_,rates_;
    Foam::scalar physicalBoundaryEnergy_=0;
    bool componentTolerance_=false;
    std::FILE* componentTrace_=nullptr;
public:
    bool enabled;
    cellEnergyAudit(const Foam::fvMesh& m,const Foam::Time& t,const Foam::PtrList<Foam::volScalarField>& Y)
    :mesh_(m),time_(t),every_(t.controlDict().getOrDefault<Foam::label>("cellLedgerEvery",1)),
      yn_(Y.size()),rates_(Y.size()),enabled(t.controlDict().getOrDefault<bool>("energyLedger",true) && t.controlDict().getOrDefault<bool>("cellEnergyLedger",true))
    {
        if(!enabled)return;
        componentTolerance_=t.controlDict().getOrDefault<bool>("componentEnergyTolerance",false);
        Foam::fileName componentDir(t.path()/"postProcessing"/"componentEnergyTolerance"/t.timeName());Foam::mkDir(componentDir);
        char componentName[40];std::snprintf(componentName,sizeof(componentName),"rank%04d.csv",Foam::Pstream::myProcNo());
        componentTrace_=std::fopen((componentDir/componentName).c_str(),"w");
        if(!componentTrace_)FatalErrorInFunction<<"Cannot open component tolerance diagnostics"<<Foam::exit(Foam::FatalError);
        std::fputs("time,iteration,componentRule,globalMaxResidual,globalMaxScaledResidual,maxLocalAllowance,maxLocalComponentScale,repeatedState,capFallback,accepted\n",componentTrace_);
        Foam::fileName dir(t.path()/"postProcessing"/"cellEnergyLedger"/t.timeName());Foam::mkDir(dir);
        char n[80];std::snprintf(n,sizeof(n),"cells_rank%04d.csv",Foam::Pstream::myProcNo());
        if(every_>0){fp_=std::fopen((dir/n).c_str(),"w");if(!fp_)FatalErrorInFunction<<"Cell ledger open failed"<<Foam::exit(Foam::FatalError);}
        std::snprintf(n,sizeof(n),"totals_rank%04d.csv",Foam::Pstream::myProcNo());totals_=std::fopen((dir/n).c_str(),"w");
        if(!totals_)FatalErrorInFunction<<"Cell totals open failed"<<Foam::exit(Foam::FatalError);
        const char* columns="DE,Dpressure,Dkinetic,DrhoH,DrhoC,Dchemistry,DspeciesTransport,DspeciesResidual,Dequation,Dtransport,Dhistory,DpostH,closure,deltaRho,absDensityEnergy,continuityAbs";
        if(fp_){std::fprintf(fp_,"step,time,rank,cell,V,rhoAssembly,rhoFinal,hSensible,hFormation,pEnergyAssembly,pFinal,T,energyResidual,%s",columns);
            forAll(Y,s)std::fprintf(fp_,",deltaRhoY_%s",Y[s].name().c_str());std::fputs(",DpostC\n",fp_);}
        std::fprintf(totals_,"step,time,rank,nCells,maxCellClosure,maxEOSRelative,maxMomentumDeltaU,%s,physicalBoundaryEnergy,DpostC\n",columns);
    }
    ~cellEnergyAudit(){if(fp_)std::fclose(fp_);if(totals_)std::fclose(totals_);if(componentTrace_)std::fclose(componentTrace_);}
    const Foam::scalarField& rhoAssembly() const{return ra_;}
    const Foam::scalarField& sensibleSolved() const{return ha_;}
    const Foam::scalarField& formationSolved() const{return ca_;}
    Foam::label remapSpecies(const Foam::volScalarField& rho,Foam::psiReactionThermo& th,const Foam::surfaceScalarField& phi,
        const Foam::tmp<Foam::volScalarField>& mu)
    {
        auto& Y=th.composition().Y();Foam::label maxIterations=0;
        forAll(Y,s)
        {
            Foam::volScalarField dY(Foam::IOobject("deltaY",time_.timeName(),mesh_,Foam::IOobject::NO_READ,Foam::IOobject::NO_WRITE,false),Y[s]);
            dY=Foam::dimensionedScalar("zero",Foam::dimless,0);
            auto conv=Foam::fvm::div(phi,Y[s],"div(phi,Yi_h)");auto diff=Foam::fvm::laplacian(mu(),Y[s]);
            Foam::scalarField residual=mesh_.V()*(rho.primitiveField()*Y[s].primitiveField()-rn_*yn_[s])/time_.deltaTValue()
                +residualCells(conv())-residualCells(diff())-rates_[s];
            Foam::volScalarField source(Foam::IOobject("speciesCorrectionSource",time_.timeName(),mesh_,Foam::IOobject::NO_READ,Foam::IOobject::NO_WRITE,false),mesh_,Foam::dimensionedScalar("zero",rho.dimensions()/Foam::dimTime,0));
            source.primitiveFieldRef()=-residual/mesh_.V();
            Foam::fvScalarMatrix correction(Foam::fvm::Sp(rho/time_.deltaT(),dY)
                +Foam::fvm::div(phi,dY,"div(phi,Yi_h)")-Foam::fvm::laplacian(mu(),dY)==source);
            auto performance=correction.solve(mesh_.solver("Yi"));maxIterations=Foam::max(maxIterations,performance.nIterations());Y[s]+=dY;Y[s].correctBoundaryConditions();
            if(Foam::min(Y[s].primitiveField()) < -1e-12)
                FatalErrorInFunction<<"Negative species after flux correction: "<<Y[s].name()<<Foam::exit(Foam::FatalError);
        }
        Foam::scalar maxSumError=0;
        forAll(rho,i){Foam::scalar sy=0;forAll(Y,s)sy+=Y[s][i];maxSumError=Foam::max(maxSumError,Foam::mag(sy-1));}
        if(maxSumError>1e-9)FatalErrorInFunction<<"Species flux correction normalization error "<<maxSumError<<Foam::exit(Foam::FatalError);
        return maxIterations;
    }
    Foam::label conservativeEnergy(const Foam::volScalarField& rho,Foam::psiReactionThermo& th,
        const Foam::volScalarField& K,const Foam::surfaceScalarField& phi,
        const Foam::tmp<Foam::volScalarField>& alpha,const Foam::tmp<Foam::volScalarField>& mu,
        Foam::scalar& finalResidual)
    {
        auto& h=th.he();auto& p=th.p();auto& Y=th.composition().Y();
        Foam::label totalIterations=0;
        Foam::scalarField lastH(h.primitiveField()),lastT(th.T().primitiveField()),lastP(p.primitiveField());
        Foam::scalarField olderH(lastH),olderT(lastT),olderP(lastP);
        // Composition and face flux are fixed through this Newton solve.
        Foam::scalarField formationDiffusion(mesh_.nCells(),0),formationDiffusionScale(mesh_.nCells(),0);
        forAll(Y,s){auto m=Foam::fvm::laplacian(mu(),Y[s]);formationDiffusion+=th.composition().Hc(s)*residualCells(m());formationDiffusionScale+=Foam::mag(th.composition().Hc(s))*operatorMagnitudeCells(m());}
        for(Foam::label it=0;it<20;++it)
        {
            auto hc=th.hc();
            auto convection=Foam::fvm::div(phi,h,"div(phi,Yi_h)");auto diffusion=Foam::fvm::laplacian(alpha(),h);
            auto convC=Foam::fvm::div(phi,hc(),"div(phi,Yi_h)");auto divK=Foam::fvc::div(phi,K);
            Foam::scalarField residual=mesh_.V()*(rho.primitiveField()*(h.primitiveField()+hc().primitiveField()+K.primitiveField())-p.primitiveField()
                -rn_*(hn_+cn_+kn_)+pn_)/time_.deltaTValue()
                +residualCells(convection())+residualCells(convC())+mesh_.V()*divK().primitiveField()
                -residualCells(diffusion())-formationDiffusion;
            finalResidual=Foam::returnReduce(Foam::max(Foam::mag(residual))*time_.deltaTValue(),Foam::maxOp<Foam::scalar>());
            Foam::scalarField scale=mesh_.V()*(Foam::mag(rho.primitiveField()*h.primitiveField())+Foam::mag(rho.primitiveField()*hc().primitiveField())
                +Foam::mag(rho.primitiveField()*K.primitiveField())+Foam::mag(p.primitiveField())
                +Foam::mag(rn_*hn_)+Foam::mag(rn_*cn_)+Foam::mag(rn_*kn_)+Foam::mag(pn_))
                +time_.deltaTValue()*(operatorMagnitudeCells(convection())+operatorMagnitudeCells(convC())
                +Foam::mag(mesh_.V()*divK().primitiveField())+operatorMagnitudeCells(diffusion())+formationDiffusionScale);
            Foam::scalar maxRatio=0,maxAllowance=0,maxScale=0;
            forAll(residual,i)
            {
                const Foam::scalar allowance=5e-18+64*std::numeric_limits<Foam::scalar>::epsilon()*scale[i];
                maxRatio=Foam::max(maxRatio,Foam::mag(residual[i])*time_.deltaTValue()/allowance);
                maxAllowance=Foam::max(maxAllowance,allowance);maxScale=Foam::max(maxScale,scale[i]);
            }
            maxRatio=Foam::returnReduce(maxRatio,Foam::maxOp<Foam::scalar>());
            Foam::label sameLast=it>=2,sameOlder=it>=2;
            forAll(h,i)
            {
                sameLast=sameLast && h[i]==lastH[i] && th.T()[i]==lastT[i] && p[i]==lastP[i];
                sameOlder=sameOlder && h[i]==olderH[i] && th.T()[i]==olderT[i] && p[i]==olderP[i];
            }
            sameLast=Foam::returnReduce(sameLast,Foam::minOp<Foam::label>());
            sameOlder=Foam::returnReduce(sameOlder,Foam::minOp<Foam::label>());
            const bool repeated=sameLast || sameOlder;
            const bool fallback=componentTolerance_ && it==19 && finalResidual>=5e-18 && maxRatio<=1;
            const bool accepted=finalResidual<5e-18 || fallback;
            std::fprintf(componentTrace_,"%.17g,%d,%d,%.17g,%.17g,%.17g,%.17g,%d,%d,%d\n",double(time_.value()),it,int(componentTolerance_),double(finalResidual),double(maxRatio),double(maxAllowance),double(maxScale),int(repeated),int(fallback),int(accepted));std::fflush(componentTrace_);
            if(accepted)return totalIterations;
            olderH=lastH;olderT=lastT;olderP=lastP;
            lastH=h.primitiveField();lastT=th.T().primitiveField();lastP=p.primitiveField();
            Foam::volScalarField dH(Foam::IOobject("deltaConservativeH",time_.timeName(),mesh_,Foam::IOobject::NO_READ,Foam::IOobject::NO_WRITE,false),h);
            dH=Foam::dimensionedScalar("zero",h.dimensions(),0);
            Foam::volScalarField capacity(Foam::IOobject("conservativeCapacity",time_.timeName(),mesh_,Foam::IOobject::NO_READ,Foam::IOobject::NO_WRITE,false),rho*th.Cv()/th.Cp());
            if(Foam::min(capacity.primitiveField())<=0)FatalErrorInFunction<<"Nonpositive conservative capacity"<<Foam::exit(Foam::FatalError);
            Foam::volScalarField source(Foam::IOobject("conservativeEnergySource",time_.timeName(),mesh_,Foam::IOobject::NO_READ,Foam::IOobject::NO_WRITE,false),mesh_,Foam::dimensionedScalar("zero",rho.dimensions()*h.dimensions()/Foam::dimTime,0));
            source.primitiveFieldRef()=-residual/mesh_.V();
            Foam::fvScalarMatrix correction(Foam::fvm::Sp(capacity/time_.deltaT(),dH)
                +Foam::fvm::div(phi,dH,"div(phi,Yi_h)")-Foam::fvm::laplacian(alpha(),dH)==source);
            auto performance=correction.solve(mesh_.solver(h.name()));totalIterations+=performance.nIterations();
            h+=dH;h.correctBoundaryConditions();th.correct();th.correct();p=rho/th.psi();p.correctBoundaryConditions();
            if(Foam::min(th.T().primitiveField())<200 || Foam::max(th.T().primitiveField())>5000)
                FatalErrorInFunction<<"Conservative correction outside temperature interval"<<Foam::exit(Foam::FatalError);
        }
        FatalErrorInFunction<<"Conservative energy Newton failure, residual J/cell "<<finalResidual<<Foam::exit(Foam::FatalError);
        return totalIterations;
    }
    Foam::scalar physicalBoundaryOperator(const Foam::fvScalarMatrix& m) const
    {
        Foam::scalar power=0;
        forAll(m.psi().boundaryField(),p)
        {
            if(m.psi().boundaryField()[p].coupled())continue;
            const auto& c=mesh_.boundary()[p].faceCells();
            forAll(c,f)power+=m.internalCoeffs()[p][f]*m.psi()[c[f]]-m.boundaryCoeffs()[p][f];
        }
        return power;
    }
    Foam::scalarField residualCells(const Foam::fvScalarMatrix& m) const
    {
        const auto& h=m.psi().primitiveField();Foam::scalarField r(m.diag()*h-m.source());
        if(m.hasUpper())
        {const auto& o=m.lduAddr().lowerAddr();const auto& n=m.lduAddr().upperAddr();
         forAll(o,f){r[o[f]]+=m.upper()[f]*h[n[f]];r[n[f]]+=m.lower()[f]*h[o[f]];}}
        forAll(m.psi().boundaryField(),p)
        {const auto& patch=m.psi().boundaryField()[p];const auto& c=mesh_.boundary()[p].faceCells();
         if(patch.coupled())
         {auto nh=patch.patchNeighbourField();forAll(c,f)r[c[f]]+=m.internalCoeffs()[p][f]*h[c[f]]-m.boundaryCoeffs()[p][f]*nh()[f];}
         else forAll(c,f)r[c[f]]+=m.internalCoeffs()[p][f]*h[c[f]]-m.boundaryCoeffs()[p][f];}
        return r;
    }
    Foam::scalarField operatorMagnitudeCells(const Foam::fvScalarMatrix& m) const
    {
        const auto& h=m.psi().primitiveField();Foam::scalarField result(Foam::mag(m.diag()*h)+Foam::mag(m.source()));
        if(m.hasUpper())
        {
            const auto& o=m.lduAddr().lowerAddr();const auto& n=m.lduAddr().upperAddr();
            forAll(o,f){result[o[f]]+=Foam::mag(m.upper()[f]*h[n[f]]);result[n[f]]+=Foam::mag(m.lower()[f]*h[o[f]]);}
        }
        forAll(m.psi().boundaryField(),p)
        {
            const auto& patch=m.psi().boundaryField()[p];const auto& c=mesh_.boundary()[p].faceCells();
            if(patch.coupled())
            {
                auto nh=patch.patchNeighbourField();
                forAll(c,f)result[c[f]]+=Foam::mag(m.internalCoeffs()[p][f]*h[c[f]])+Foam::mag(m.boundaryCoeffs()[p][f]*nh()[f]);
            }
            else forAll(c,f)result[c[f]]+=Foam::mag(m.internalCoeffs()[p][f]*h[c[f]])+Foam::mag(m.boundaryCoeffs()[p][f]);
        }
        return result;
    }
    void start(const Foam::volScalarField& rho,Foam::psiReactionThermo& th,const Foam::volScalarField& K)
    {
        if(!enabled)return;++step_;physicalBoundaryEnergy_=0;rn_=rho.primitiveField();hn_=th.he().primitiveField();
        auto hc=th.hc();cn_=hc().primitiveField();kn_=K.primitiveField();pn_=th.p().primitiveField();
        forAll(yn_,s)yn_[s]=th.composition().Y()[s].primitiveField();
    }
    void chemistry(Foam::CombustionModel<Foam::psiReactionThermo>& reaction,Foam::psiReactionThermo& th,const Foam::volScalarField& Q)
    {
        if(!enabled)return;chem_=mesh_.V()*Q.primitiveField();auto& Y=th.composition().Y();
        forAll(Y,s){auto source=reaction.R(Y[s]);rates_[s]=-source().source();chem_+=th.composition().Hc(s)*rates_[s];}
    }
    void species(const Foam::volScalarField& rho,Foam::psiReactionThermo& th,const Foam::surfaceScalarField& phi,
                 const Foam::tmp<Foam::volScalarField>& mu,const Foam::fv::convectionScheme<Foam::scalar>& convection)
    {
        if(!enabled)return;auto& Y=th.composition().Y();const Foam::scalar dt=time_.deltaTValue();
        spTransport_=Foam::scalarField(mesh_.nCells(),0);spResidual_=spTransport_;
        forAll(Y,s)
        {
            auto conv=convection.fvmDiv(phi,Y[s]);auto diff=Foam::fvm::laplacian(mu(),Y[s]);
            Foam::scalarField bc=residualCells(conv()),lc=residualCells(diff());
            const Foam::scalar hc=th.composition().Hc(s);
            physicalBoundaryEnergy_-=dt*hc*(physicalBoundaryOperator(conv())-physicalBoundaryOperator(diff()));
            spTransport_-=dt*hc*(bc-lc);
            spResidual_+=hc*(mesh_.V()*(rho.primitiveField()*Y[s].primitiveField()-rn_*yn_[s])-dt*rates_[s]+dt*(bc-lc));
        }
    }
    void assemble(const Foam::volScalarField& rho,Foam::psiReactionThermo& th,const Foam::volScalarField& K,
                  const Foam::volScalarField& Q,const Foam::volScalarField& dpdt,const Foam::surfaceScalarField& phi)
    {
        if(!enabled)return;ra_=rho.primitiveField();ka_=K.primitiveField();pa_=th.p().primitiveField();
        w_=dpdt.primitiveField();q_=Q.primitiveField();auto div=Foam::fvc::div(phi,K);bk_=div().primitiveField();
        auto faceK=Foam::fvc::interpolate(K);
        forAll(phi.boundaryField(),p)if(!phi.boundaryField()[p].coupled())
            physicalBoundaryEnergy_-=time_.deltaTValue()*Foam::sum(phi.boundaryField()[p]*faceK().boundaryField()[p]);
        history_=mesh_.V()*(rho.oldTime().primitiveField()*(th.he().oldTime().primitiveField()+K.oldTime().primitiveField())-rn_*(hn_+kn_));
    }
    void solved(const Foam::fvScalarMatrix& original,const Foam::fvScalarMatrix& conv,const Foam::fvScalarMatrix& diff,Foam::psiReactionThermo& th)
    {
        if(!enabled)return;ha_=th.he().primitiveField();auto hc=th.hc();ca_=hc().primitiveField();
        eq_=residualCells(original);bh_=residualCells(conv);lh_=residualCells(diff);
        physicalBoundaryEnergy_-=time_.deltaTValue()*(physicalBoundaryOperator(conv)-physicalBoundaryOperator(diff));
    }
    void finish(const Foam::volScalarField& rho,Foam::psiReactionThermo& th,const Foam::volScalarField& K,const Foam::surfaceScalarField& phi,Foam::scalar momentumMismatch)
    {
        if(!enabled)return;const Foam::scalar dt=time_.deltaTValue();const auto& rf=rho.primitiveField();const auto& hf=th.he().primitiveField();
        const auto& pf=th.p().primitiveField();auto hct=th.hc();const auto& cf=hct().primitiveField();
        auto continuity=Foam::fvc::ddt(rho)+Foam::fvc::div(phi);auto eos=th.rho();
        Foam::scalar sums[16]={},maxClosure=0,maxEOS=0,totalPostC=0;
        forAll(rho,i)
        {
            const Foam::scalar v=mesh_.V()[i];Foam::scalar a[16];
            a[0]=v*(rf[i]*(hf[i]+cf[i]+K[i])-pf[i]-(rn_[i]*(hn_[i]+cn_[i]+kn_[i])-pn_[i]));
            a[1]=v*(dt*w_[i]-pf[i]+pn_[i]);a[2]=v*(rf[i]*K[i]-ra_[i]*ka_[i]);
            a[3]=v*(rf[i]-ra_[i])*ha_[i];a[4]=v*(rf[i]-ra_[i])*ca_[i];
            a[5]=dt*chem_[i];a[6]=spTransport_[i];a[7]=spResidual_[i];a[8]=dt*eq_[i];
            a[9]=-dt*(bh_[i]+v*bk_[i]-lh_[i]);a[10]=history_[i];a[11]=v*rf[i]*(hf[i]-ha_[i]);
            a[12]=a[0];for(int j=1;j<=11;++j)a[12]-=a[j];
            const Foam::scalar postC=v*rf[i]*(cf[i]-ca_[i]);a[12]-=postC;totalPostC+=postC;
            a[13]=v*(rf[i]-ra_[i]);a[14]=Foam::mag(a[3]+a[4]);a[15]=v*Foam::mag(continuity()[i]);
            for(int j=0;j<16;++j)sums[j]+=a[j];maxClosure=Foam::max(maxClosure,Foam::mag(a[12]));
            maxEOS=Foam::max(maxEOS,Foam::mag(rf[i]-eos()[i])/Foam::max(rf[i],Foam::SMALL));
            if(fp_ && (step_==1 || step_%every_==0))
            {std::fprintf(fp_,"%d,%.17g,%d,%d,%.17g,%.17g,%.17g,%.17g,%.17g,%.17g,%.17g,%.17g,%.17g",step_,double(time_.value()),Foam::Pstream::myProcNo(),i,double(v),double(ra_[i]),double(rf[i]),double(ha_[i]),double(ca_[i]),double(pa_[i]),double(pf[i]),double(th.T()[i]),double(eq_[i]));
             for(int j=0;j<16;++j)std::fprintf(fp_,",%.17g",double(a[j]));
             forAll(yn_,s)std::fprintf(fp_,",%.17g",double(v*(rf[i]-ra_[i])*th.composition().Y()[s][i]));std::fprintf(fp_,",%.17g\n",double(postC));}
        }
        std::fprintf(totals_,"%d,%.17g,%d,%d,%.17g,%.17g,%.17g",step_,double(time_.value()),Foam::Pstream::myProcNo(),mesh_.nCells(),double(maxClosure),double(maxEOS),double(momentumMismatch));
        for(int j=0;j<16;++j)std::fprintf(totals_,",%.17g",double(sums[j]));std::fprintf(totals_,",%.17g,%.17g\n",double(physicalBoundaryEnergy_),double(totalPostC));
        std::fflush(totals_);if(fp_)std::fflush(fp_);
    }
};
