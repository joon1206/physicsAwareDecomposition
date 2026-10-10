"""Separate retained known-physics transport control; parent is never edited."""
from pathlib import Path
import hashlib,json,shutil
ROOT=Path(__file__).resolve().parents[1]
def replace(path,old,new):
    text=path.read_text()
    if text.count(old)!=1:raise RuntimeError('Ambiguous edit '+str(path))
    path.write_text(text.replace(old,new))
def main():
    parent=ROOT/'applications/reactingEnergyCandidates';app=ROOT/'applications/reactingEnergyTransportCandidates'
    if app.exists():raise RuntimeError('Refusing existing transport control '+str(app))
    app.mkdir();records={}
    for p in parent.iterdir():
        if p.suffix in ['.H','.C']:
            shutil.copy2(p,app/p.name);records[p.name]=hashlib.sha256(p.read_bytes()).hexdigest()
    shutil.copytree(parent/'Make',app/'Make',ignore=shutil.ignore_patterns('linux*'))
    replace(app/'Make/files','/reactingEnergyCandidates','/reactingEnergyTransportCandidates')
    eq=app/'EEqn.H'
    replace(eq,'    fvScalarMatrix EEqn','    #include "speciesSensibleHeatFlux.H"\n\n    fvScalarMatrix EEqn')
    replace(eq,'      - fvm::laplacian(turbulence->alphaEff(), he)','      - fvm::laplacian(turbulence->alphaEff(), he)\n      + fvc::div(extraSensibleEnergyFlux)')
    replace(eq,'        cellAudit.assemble(rho,thermo,K,Qdot,dpdt,phi);','        cellAudit.assemble(rho,thermo,K,Qdot,dpdt,phi);\n        cellAudit.extraFaceEnergyFlux(extraSensibleEnergyFlux);')
    audit=app/'cellEnergyAudit.H'
    replace(audit,'    const Foam::scalarField& rhoAssembly()', '    Foam::scalarField extraEnergyDiv_;\n    void extraFaceEnergyFlux(const Foam::surfaceScalarField& flux)\n    {\n        if(!enabled)return;\n        auto div=Foam::fvc::div(flux);extraEnergyDiv_=mesh_.V()*div().primitiveField();\n        forAll(flux.boundaryField(),patchi)if(!flux.boundaryField()[patchi].coupled())\n            physicalBoundaryEnergy_-=time_.deltaTValue()*Foam::sum(flux.boundaryField()[patchi]);\n    }\n    const Foam::scalarField& rhoAssembly()')
    replace(audit,'-residualCells(diffusion())-formationDiffusion;','-residualCells(diffusion())-formationDiffusion+extraEnergyDiv_;')
    replace(audit,'a[9]=-dt*(bh_[i]+v*bk_[i]-lh_[i]);','a[9]=-dt*(bh_[i]+v*bk_[i]-lh_[i]+extraEnergyDiv_[i]);')
    (app/'parent_source_manifest.json').write_text(json.dumps(records,indent=2)+'\n')
    (app/'speciesSensibleHeatFlux.H').write_text('''/* GPL-3.0-or-later. Known sensible species-diffusion compatibility control.
   Lagged p,T with post-species Y; declared in speciesSensibleDiffusion.md. */
surfaceScalarField extraSensibleEnergyFlux
(
    IOobject("extraSensibleEnergyFlux",runTime.timeName(),mesh,IOobject::NO_READ,IOobject::NO_WRITE,false),
    mesh,dimensionedScalar("zero",dimEnergy/dimTime,0)
);
if(runTime.controlDict().getOrDefault<bool>("compatibleSpeciesHeatFlux",false))
{
    volScalarField difference
    (
        IOobject("heatSpeciesDiffusivityDifference",runTime.timeName(),mesh,IOobject::NO_READ,IOobject::NO_WRITE,false),
        turbulence->alphaEff()-turbulence->muEff()
    );
    forAll(Y,s)
    {
        volScalarField hsSpecies
        (
            IOobject("sensibleSpeciesHeatFlux",runTime.timeName(),mesh,IOobject::NO_READ,IOobject::NO_WRITE,false),
            mesh,dimensionedScalar("zero",he.dimensions(),0)
        );
        forAll(he,i)hsSpecies[i]=composition.Ha(s,p[i],T[i])-composition.Hc(s);
        forAll(hsSpecies.boundaryField(),patchi)
            forAll(hsSpecies.boundaryField()[patchi],facei)
                hsSpecies.boundaryFieldRef()[patchi][facei]=composition.Ha(s,p.boundaryField()[patchi][facei],T.boundaryField()[patchi][facei])-composition.Hc(s);
        extraSensibleEnergyFlux+=fvc::interpolate(difference)*fvc::interpolate(hsSpecies)*fvc::snGrad(Y[s])*mesh.magSf();
    }
}
''')
    print('Created',app)
if __name__=='__main__':main()
