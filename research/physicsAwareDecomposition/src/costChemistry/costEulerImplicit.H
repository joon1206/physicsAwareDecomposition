// GPL-3.0-or-later. Integration loop adapted from OpenCFD v2012
// StandardChemistryModel.C (OpenFOAM Foundation 2011-2017).
#ifndef costEulerImplicit_H
#define costEulerImplicit_H
#include "StandardChemistryModel.H"
#include "fvMesh.H"
#include "EulerImplicit.H"
#include "UniformField.H"
#include <chrono>
#include <cstdio>
#include <cmath>
#include "OSspecific.H"
namespace Foam
{
template<class ChemistryModel>
class costEulerImplicit : public EulerImplicit<ChemistryModel>
{
    typedef EulerImplicit<ChemistryModel> Base;
    typedef std::chrono::steady_clock Clock;
    volScalarField cost_, substeps_;
    scalar alpha_;
    bool cellTiming_;
    label traceInterval_;
    bool initialized_;
    std::FILE* trace_;
    template<class DeltaTType>
    scalar solveCost(const DeltaTType& deltaT)
    {
        // Preserve upstream numerical operations and their order.
        BasicChemistryModel<typename ChemistryModel::reactionThermo>::correct();
        scalar deltaTMin=GREAT;
        if(!this->chemistry_) { cost_=dimensionedScalar(dimTime,Zero); substeps_=dimensionedScalar(dimless,Zero); return deltaTMin; }
        tmp<volScalarField> trho(this->thermo().rho());
        const scalarField& rho=trho();
        const scalarField& T=this->thermo().T();
        const scalarField& p=this->thermo().p();
        scalarField c0(this->nSpecie_);
        forAll(rho,celli)
        {
            const auto begin=cellTiming_ ? Clock::now() : Clock::time_point();
            label n=0;
            scalar Ti=T[celli];
            if(Ti>this->Treact_)
            {
                const scalar rhoi=rho[celli];
                scalar pi=p[celli];
                for(label i=0;i<this->nSpecie_;++i)
                { this->c_[i]=rhoi*this->Y_[i][celli]/this->specieThermo_[i].W(); c0[i]=this->c_[i]; }
                scalar timeLeft=deltaT[celli];
                while(timeLeft>SMALL)
                {
                    scalar dt=timeLeft;
                    Base::solve(this->c_,Ti,pi,dt,this->deltaTChem_[celli]);
                    timeLeft-=dt; ++n;
                }
                deltaTMin=min(this->deltaTChem_[celli],deltaTMin);
                this->deltaTChem_[celli]=min(this->deltaTChem_[celli],this->deltaTChemMax_);
                for(label i=0;i<this->nSpecie_;++i)
                    this->RR_[i][celli]=(this->c_[i]-c0[i])*this->specieThermo_[i].W()/deltaT[celli];
            }
            else { for(label i=0;i<this->nSpecie_;++i) this->RR_[i][celli]=0; }
            const scalar wall=cellTiming_ ? std::chrono::duration<double>(Clock::now()-begin).count() : 0;
            cost_[celli]=initialized_ ? alpha_*wall+(1-alpha_)*cost_[celli] : wall;
            substeps_[celli]=n;
            if(trace_ && this->mesh().time().timeIndex()%traceInterval_==0)
                std::fprintf(trace_,"%d,%d,%.12g,%d\n",this->mesh().time().timeIndex(),celli,double(wall),n);
        }
        initialized_=true;
        return deltaTMin;
    }
public:
    TypeName("costEulerImplicit");
    explicit costEulerImplicit(typename ChemistryModel::reactionThermo& thermo)
    :
        Base(thermo),
        cost_(IOobject("chemCost",this->mesh().time().timeName(),this->mesh(),IOobject::READ_IF_PRESENT,IOobject::AUTO_WRITE),
            this->mesh(),dimensionedScalar(dimTime,Zero),"zeroGradient"),
        substeps_(IOobject("chemSubsteps",this->mesh().time().timeName(),this->mesh(),IOobject::NO_READ,IOobject::AUTO_WRITE),
            this->mesh(),dimensionedScalar(dimless,Zero),"zeroGradient"),
        alpha_(this->template getOrDefault<scalar>("costAlpha",1)),
        cellTiming_(this->template getOrDefault<bool>("cellTiming",true)),
        traceInterval_(this->template getOrDefault<label>("costTraceInterval",0)),
        initialized_(isFile(this->mesh().time().path()/this->mesh().time().timeName()/"chemCost")),trace_(nullptr)
    {
        if(!std::isfinite(alpha_) || alpha_<0 || alpha_>1 || traceInterval_<0)
            FatalErrorInFunction << "costAlpha must be in [0,1]; costTraceInterval >= 0" << exit(FatalError);
        forAll(cost_,i)
            if(!std::isfinite(cost_[i]) || cost_[i]<0)
                FatalErrorInFunction << "chemCost history must be finite and nonnegative" << exit(FatalError);
        if(traceInterval_>0)
        {
            fileName dir(this->mesh().time().path()/"postProcessing"/"performance");
            mkDir(dir); trace_=std::fopen((dir/"cellCost.csv").c_str(),"w");
            if(!trace_) FatalErrorInFunction << "Cannot create chemistry trace" << exit(FatalError);
            std::fputs("timeIndex,cell,wall,substeps\n",trace_);
        }
    }
    virtual ~costEulerImplicit() { if(trace_) std::fclose(trace_); }
    virtual scalar solve(const scalar dt)
    { return min(solveCost(UniformField<scalar>(dt)),2*dt); }
    virtual scalar solve(const scalarField& dt) { return solveCost(dt); }
};
}
#endif
