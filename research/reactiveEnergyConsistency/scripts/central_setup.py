"""Historical first setup: retained internal-energy-registration trial.

The current reference is built directly from applications/reactingEnergyCentralReference.
Its later h/Cv recovery adaptation is retained in source snapshots; do not rerun
this historical preparer to replace that source.
"""
from pathlib import Path
import hashlib,json,shutil
ROOT=Path(__file__).resolve().parents[1]
app=ROOT/'applications/reactingEnergyCentralReference'
if app.exists():raise RuntimeError('Existing reference preserved')
src=Path('/opt/OpenFOAM/OpenFOAM-v2012/applications/solvers/compressible/rhoCentralFoam')
app.mkdir();old=app/'originalV2012';old.mkdir()
names=['rhoCentralFoam.C','createFields.H','createFieldRefs.H','directionInterpolate.H','readFluxScheme.H','centralCourantNo.H','setRDeltaT.H']
for name in names:
    shutil.copy2(src/name,old/name);shutil.copy2(src/name,app/name)
(old/'manifest.json').write_text(json.dumps({n:hashlib.sha256((old/n).read_bytes()).hexdigest() for n in names},indent=2)+'\n')
def replace(text,a,b):
    assert text.count(a)==1,a
    return text.replace(a,b)
fields=(app/'createFields.H').read_text().replace('autoPtr<psiThermo>','autoPtr<psiReactionThermo>').replace('psiThermo::New','psiReactionThermo::New').replace('psiThermo& thermo','psiReactionThermo& thermo')
fields=replace(fields,'volScalarField& e = thermo.he();','thermo.validate(args.executable(), "e");\nvolScalarField& e = thermo.he();\nauto& Y=thermo.composition().Y();\nauto chemistry=BasicChemistryModel<psiReactionThermo>::New(thermo);')
fields=fields.replace('rho*(e + 0.5*magSqr(U))','rho*(e + thermo.hc() + 0.5*magSqr(U))')
fields+='''
PtrList<volScalarField> rhoY(Y.size());
forAll(Y,s)rhoY.set(s,new volScalarField(IOobject("rhoY_"+Y[s].name(),runTime.timeName(),mesh,IOobject::NO_READ,IOobject::NO_WRITE),rho*Y[s]));
'''
(app/'createFields.H').write_text(fields)
text=(app/'rhoCentralFoam.C').read_text().replace('#include "psiThermo.H"','#include "psiReactionThermo.H"\n#include "BasicChemistryModel.H"\n#include <cstdio>')
text=replace(text,'    turbulence->validate();','''    turbulence->validate();
    if(gMax(thermo.mu()().primitiveField())>SMALL)
        FatalErrorInFunction<<"Inviscid reference requires zero transport"<<exit(FatalError);
    const fileName referenceDir(runTime.path()/"postProcessing"/"centralReference"/runTime.timeName());mkDir(referenceDir);
    char rankName[64];std::snprintf(rankName,sizeof(rankName),"rank%04d.csv",Pstream::myProcNo());
    std::FILE* referenceFp=std::fopen((referenceDir/rankName).c_str(),"w");
    if(!referenceFp)FatalErrorInFunction<<"Cannot open reference budget"<<exit(FatalError);
    std::fputs("time,mass,absoluteEnergy,thermoEnergy,maxLocalEnergyResidual,sumYError,minY,minT,minP\\n",referenceFp);
''')
text=replace(text,'        // --- Directed interpolation of primitive fields onto faces','''        // Old-state integrated species source, once per physical Euler step.
        chemistry->solve(runTime.deltaTValue());
        const scalarField energyOld(rhoE.primitiveField());
        volScalarField ea("eaAbsolute",e+thermo.hc());
        // --- Directed interpolation of primitive fields onto faces''')
text=text.replace('interpolate(e, pos, T.name())','interpolate(ea, pos, T.name())').replace('interpolate(e, neg, T.name())','interpolate(ea, neg, T.name())')
text=replace(text,'        // --- Solve energy','''        // All species share the central continuity reconstruction/weights.
        forAll(Y,s)
        {
            surfaceScalarField phiY("phiY",aphiv_pos*interpolate(rhoY[s],pos,rho.name())+aphiv_neg*interpolate(rhoY[s],neg,rho.name()));
            volScalarField source(IOobject("sourceY",runTime.timeName(),mesh,IOobject::NO_READ,IOobject::NO_WRITE,false),mesh,dimensionedScalar("zero",rho.dimensions()/dimTime,0));
            source.primitiveFieldRef()=chemistry->RR(s);
            solve(fvm::ddt(rhoY[s])+fvc::div(phiY)==source);
            Y[s].primitiveFieldRef()=rhoY[s].primitiveField()/rho.primitiveField();Y[s].correctBoundaryConditions();
        }
        // --- Solve absolute total energy: no chemical heat source''')
text=replace(text,'        e = rhoE/rho - 0.5*magSqr(U);','        e = rhoE/rho - 0.5*magSqr(U) - thermo.hc();')
text=text.replace('e.boundaryField() + 0.5*magSqr(U.boundaryField())','e.boundaryField() + thermo.hc()().boundaryField() + 0.5*magSqr(U.boundaryField())')
text=replace(text,'        runTime.write();','''        scalar sumError=0,minY=GREAT;
        forAll(rho,i){scalar total=0;forAll(Y,s){total+=Y[s][i];minY=Foam::min(minY,Y[s][i]);}sumError=Foam::max(sumError,Foam::mag(total-1));}
        sumError=returnReduce(sumError,maxOp<scalar>());minY=returnReduce(minY,minOp<scalar>());
        if(sumError>1e-8 || minY<-1e-12 || gMin(thermo.T().primitiveField())<=0 || gMin(p.primitiveField())<=0)
            FatalErrorInFunction<<"Reference admissibility failure "<<sumError<<","<<minY<<exit(FatalError);
        auto energyDiv=fvc::div(phiEp);scalar localResidual=0;
        forAll(rho,i)localResidual=Foam::max(localResidual,Foam::mag(mesh.V()[i]*(rhoE[i]-energyOld[i]+runTime.deltaTValue()*energyDiv()[i])));
        const scalar mass=gSum(mesh.V()*rho.primitiveField());
        const scalar absoluteEnergy=gSum(mesh.V()*rhoE.primitiveField());
        auto thermochemical=thermo.hc();const scalar reconstructed=gSum(mesh.V()*rho.primitiveField()*(e.primitiveField()+thermochemical().primitiveField()+0.5*magSqr(U.primitiveField())));
        std::fprintf(referenceFp,"%.17g,%.17g,%.17g,%.17g,%.17g,%.17g,%.17g,%.17g,%.17g\\n",double(runTime.value()),double(mass),double(absoluteEnergy),double(reconstructed),double(returnReduce(localResidual,maxOp<scalar>())),double(sumError),double(minY),double(gMin(thermo.T().primitiveField())),double(gMin(p.primitiveField())));std::fflush(referenceFp);
        if(runTime.controlDict().getOrDefault<bool>("padWriteFinal",false) && runTime.value()+0.5*runTime.deltaTValue()>=runTime.endTime().value())runTime.writeNow();else runTime.write();
        if(runTime.writeTime())e.write();''')
text=replace(text,'    Info<< "End\\n" << endl;','    std::fclose(referenceFp);\n    Info<< "End\\n" << endl;')
(app/'reactingEnergyCentralReference.C').write_text(text)
# Keep the copied original main available only in originalV2012.
(app/'rhoCentralFoam.C').unlink()
(app/'Make').mkdir();(app/'Make/files').write_text('reactingEnergyCentralReference.C\n\nEXE = $(FOAM_USER_APPBIN)/reactingEnergyCentralReference\n')
options=(ROOT/'applications/reactingEnergyCandidates/Make/options').read_text()
options=options.replace('EXE_INC = \\\n','EXE_INC = \\\n    -I$(FOAM_SOLVERS)/compressible/rhoCentralFoam/BCs/lnInclude \\\n').replace('EXE_LIBS = \\\n','EXE_LIBS = \\\n    -lrhoCentralFoam \\\n')
(app/'Make/options').write_text(options+'\n')
print(app)
