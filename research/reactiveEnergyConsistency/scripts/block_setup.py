"""Separate executable for pressure/species/energy block experiments."""
from pathlib import Path
import shutil
ROOT=Path(__file__).resolve().parents[1]
original=ROOT/'applications/reactingEnergyCandidates';out=ROOT/'applications/reactingEnergyBlockCandidates'
if out.exists():raise RuntimeError('Block source already retained; edit explicitly')
out.mkdir();(out/'Make').mkdir()
for p in original.iterdir():
    if p.suffix in ['.C','.H']:shutil.copy2(p,out/p.name)
shutil.copy2(original/'Make/options',out/'Make/options')
(out/'Make/files').write_text('reactingFoamPAD.C\n\nEXE = $(FOAM_USER_APPBIN)/reactingEnergyBlockCandidates\n')
p=out/'cellEnergyAudit.H';s=p.read_text().replace('    const Foam::scalarField& rhoAssembly()', '    const Foam::scalarField& rhoStart() const{return rn_;}\n    const Foam::scalarField& rhoAssembly()');p.write_text(s)
p=out/'pEqn.H';s=p.read_text().replace('volVectorField HbyA(constrainHbyA(rAU*UEqn.H(), U, p));','volVectorField HbyA(constrainHbyA(rAU*UEqn.H(), U, p));\ndensityCorrector.momentumState(rAU,HbyA);');p.write_text(s)
p=out/'reactingFoamPAD.C';s=p.read_text().replace('cellAudit,turbulence->muEff(),K);','cellAudit,turbulence->muEff(),K,U);');p.write_text(s)
p=out/'thermoDensityCorrector.H';s=p.read_text()
s=s.replace('    std::FILE* fp_=nullptr;','    std::FILE* fp_=nullptr;\n    Foam::autoPtr<Foam::volScalarField> rAUCoeff_;\n    Foam::autoPtr<Foam::volVectorField> HbyACoeff_;')
s=s.replace(' && mode_!="conservativeState")',' && mode_!="conservativeState" && mode_!="blockConservative")')
marker='    Foam::scalar property('
helper=r'''    void momentumState(const Foam::volScalarField& rAU,const Foam::volVectorField& HbyA)
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
'''
s=s.replace(marker,helper+marker)
s=s.replace('Foam::psiReactionThermo& th,const Foam::surfaceScalarField& phi,','Foam::psiReactionThermo& th,Foam::surfaceScalarField& phi,')
s=s.replace('const Foam::tmp<Foam::volScalarField>& mu,const Foam::volScalarField& K)','const Foam::tmp<Foam::volScalarField>& mu,Foam::volScalarField& K,Foam::volVectorField& U)')
s=s.replace('momentumMismatch=0;pressureChange=0;cancellationError=0;if(!active())return;',
  'momentumMismatch=0;pressureChange=0;cancellationError=0;if(!active())return;\n        if(mode_=="blockConservative"){applyBlock(rho,th,phi,alpha,dpdt,audit,mu,K,U);return;}')
p.write_text(s)
print('Separate block prototype source prepared.')
