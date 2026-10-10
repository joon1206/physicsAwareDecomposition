/* GPL-3.0-or-later. Cellwise Euler equation audit, no physical field mutations. */
#include <cstdio>
class cellEnergyAudit
{
    const Foam::fvMesh& mesh_;
    const Foam::Time& time_;
    Foam::label step_=0,every_;
    std::FILE *fp_=nullptr,*totals_=nullptr;
    Foam::scalarField rn_,hn_,cn_,kn_,pn_,ra_,ha_,ca_,ka_,pa_,w_,q_,bk_,history_;
    Foam::scalarField eq_,bh_,lh_,chem_,spTransport_,spResidual_,boundary_;
    Foam::List<Foam::scalarField> yn_,rates_;
public:
    bool enabled;
    cellEnergyAudit(const Foam::fvMesh& m,const Foam::Time& t,const Foam::PtrList<Foam::volScalarField>& Y)
    :mesh_(m),time_(t),every_(t.controlDict().getOrDefault<Foam::label>("cellLedgerEvery",1)),
      yn_(Y.size()),rates_(Y.size()),enabled(t.controlDict().getOrDefault<bool>("energyLedger",true) && t.controlDict().getOrDefault<bool>("cellEnergyLedger",true))
    {
        if(!enabled)return;
        Foam::fileName dir(t.path()/"postProcessing"/"cellEnergyLedger"/t.timeName());Foam::mkDir(dir);
        char n[80];std::snprintf(n,sizeof(n),"cells_rank%04d.csv",Foam::Pstream::myProcNo());
        if(every_>0){fp_=std::fopen((dir/n).c_str(),"w");if(!fp_)FatalErrorInFunction<<"Cell ledger open failed"<<Foam::exit(Foam::FatalError);}
        std::snprintf(n,sizeof(n),"totals_rank%04d.csv",Foam::Pstream::myProcNo());totals_=std::fopen((dir/n).c_str(),"w");
        if(!totals_)FatalErrorInFunction<<"Cell totals open failed"<<Foam::exit(Foam::FatalError);
        const char* columns="DE,Dpressure,Dkinetic,DrhoH,DrhoC,Dchemistry,DspeciesTransport,DspeciesResidual,Dequation,Dtransport,Dhistory,DpostH,closure,deltaRho,absDensityEnergy,continuityAbs";
        if(fp_){std::fprintf(fp_,"step,time,rank,cell,V,rhoAssembly,rhoFinal,hSensible,hFormation,pBeforeProjection,pFinal,T,energyResidual,%s",columns);
            forAll(Y,s)std::fprintf(fp_,",deltaRhoY_%s",Y[s].name().c_str());std::fputc('\n',fp_);}
        std::fprintf(totals_,"step,time,rank,nCells,maxCellClosure,maxEOSRelative,maxMomentumDeltaU,%s\n",columns);
    }
    ~cellEnergyAudit(){if(fp_)std::fclose(fp_);if(totals_)std::fclose(totals_);}
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
    void start(const Foam::volScalarField& rho,Foam::psiReactionThermo& th,const Foam::volScalarField& K)
    {
        if(!enabled)return;++step_;rn_=rho.primitiveField();hn_=th.he().primitiveField();
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
            spTransport_-=dt*hc*(bc-lc);
            spResidual_+=hc*(mesh_.V()*(rho.primitiveField()*Y[s].primitiveField()-rn_*yn_[s])-dt*rates_[s]+dt*(bc-lc));
        }
    }
    void assemble(const Foam::volScalarField& rho,Foam::psiReactionThermo& th,const Foam::volScalarField& K,
                  const Foam::volScalarField& Q,const Foam::volScalarField& dpdt,const Foam::surfaceScalarField& phi)
    {
        if(!enabled)return;ra_=rho.primitiveField();ka_=K.primitiveField();pa_=th.p().primitiveField();
        w_=dpdt.primitiveField();q_=Q.primitiveField();auto div=Foam::fvc::div(phi,K);bk_=div().primitiveField();
        history_=mesh_.V()*(rho.oldTime().primitiveField()*(th.he().oldTime().primitiveField()+K.oldTime().primitiveField())-rn_*(hn_+kn_));
    }
    void solved(const Foam::fvScalarMatrix& original,const Foam::fvScalarMatrix& conv,const Foam::fvScalarMatrix& diff,Foam::psiReactionThermo& th)
    {
        if(!enabled)return;ha_=th.he().primitiveField();auto hc=th.hc();ca_=hc().primitiveField();
        eq_=residualCells(original);bh_=residualCells(conv);lh_=residualCells(diff);
    }
    void finish(const Foam::volScalarField& rho,Foam::psiReactionThermo& th,const Foam::volScalarField& K,const Foam::surfaceScalarField& phi)
    {
        if(!enabled)return;const Foam::scalar dt=time_.deltaTValue();const auto& rf=rho.primitiveField();const auto& hf=th.he().primitiveField();
        const auto& pf=th.p().primitiveField();auto hct=th.hc();const auto& cf=hct().primitiveField();
        auto continuity=Foam::fvc::ddt(rho)+Foam::fvc::div(phi);auto eos=th.rho();
        Foam::scalar sums[16]={},maxClosure=0,maxEOS=0;
        forAll(rho,i)
        {
            const Foam::scalar v=mesh_.V()[i];Foam::scalar a[16];
            a[0]=v*(rf[i]*(hf[i]+cf[i]+K[i])-pf[i]-(rn_[i]*(hn_[i]+cn_[i]+kn_[i])-pn_[i]));
            a[1]=v*(dt*w_[i]-pf[i]+pn_[i]);a[2]=v*(rf[i]*K[i]-ra_[i]*ka_[i]);
            a[3]=v*(rf[i]-ra_[i])*ha_[i];a[4]=v*(rf[i]-ra_[i])*ca_[i];
            a[5]=dt*chem_[i];a[6]=spTransport_[i];a[7]=spResidual_[i];a[8]=dt*eq_[i];
            a[9]=-dt*(bh_[i]+v*bk_[i]-lh_[i]);a[10]=history_[i];a[11]=v*rf[i]*(hf[i]-ha_[i]);
            a[12]=a[0];for(int j=1;j<=11;++j)a[12]-=a[j];
            a[13]=v*(rf[i]-ra_[i]);a[14]=Foam::mag(a[3]+a[4]);a[15]=v*Foam::mag(continuity()[i]);
            for(int j=0;j<16;++j)sums[j]+=a[j];maxClosure=Foam::max(maxClosure,Foam::mag(a[12]));
            maxEOS=Foam::max(maxEOS,Foam::mag(rf[i]-eos()[i])/Foam::max(rf[i],Foam::SMALL));
            if(fp_ && (step_==1 || step_%every_==0))
            {std::fprintf(fp_,"%d,%.17g,%d,%d,%.17g,%.17g,%.17g,%.17g,%.17g,%.17g,%.17g,%.17g,%.17g",step_,double(time_.value()),Foam::Pstream::myProcNo(),i,double(v),double(ra_[i]),double(rf[i]),double(ha_[i]),double(ca_[i]),double(pa_[i]),double(pf[i]),double(th.T()[i]),double(eq_[i]));
             for(int j=0;j<16;++j)std::fprintf(fp_,",%.17g",double(a[j]));
             forAll(yn_,s)std::fprintf(fp_,",%.17g",double(v*(rf[i]-ra_[i])*th.composition().Y()[s][i]));std::fputc('\n',fp_);}
        }
        std::fprintf(totals_,"%d,%.17g,%d,%d,%.17g,%.17g,0",step_,double(time_.value()),Foam::Pstream::myProcNo(),mesh_.nCells(),double(maxClosure),double(maxEOS));
        for(int j=0;j<16;++j)std::fprintf(totals_,",%.17g",double(sums[j]));std::fputc('\n',totals_);
        std::fflush(totals_);if(fp_)std::fflush(fp_);
    }
};
