/*---------------------------------------------------------------------------*\
  =========                 |
  \\      /  F ield         | OpenFOAM: The Open Source CFD Toolbox
   \\    /   O peration     |
    \\  /    A nd           | www.openfoam.com
     \\/     M anipulation  |
-------------------------------------------------------------------------------
    Copyright (C) 2011-2016 OpenFOAM Foundation
-------------------------------------------------------------------------------
License
    This file is part of OpenFOAM.

    OpenFOAM is free software: you can redistribute it and/or modify it
    under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    OpenFOAM is distributed in the hope that it will be useful, but WITHOUT
    ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
    FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General Public License
    for more details.

    You should have received a copy of the GNU General Public License
    along with OpenFOAM.  If not, see <http://www.gnu.org/licenses/>.

Application
    rhoCentralFoam

Group
    grpCompressibleSolvers

Description
    Density-based compressible flow solver based on central-upwind
    schemes of Kurganov and Tadmor.

\*---------------------------------------------------------------------------*/

#include <limits>
#include "fvCFD.H"
#include "psiReactionThermo.H"
#include "BasicChemistryModel.H"
#include <cstdio>
#include "turbulentFluidThermoModel.H"
#include "fixedRhoFvPatchScalarField.H"
#include "directionInterpolate.H"
#include "localEulerDdtScheme.H"
#include "fvcSmooth.H"

// * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * //

int main(int argc, char *argv[])
{
    argList::addNote
    (
        "Density-based compressible flow solver based on central-upwind"
        " schemes of Kurganov and Tadmor."
    );

    #define NO_CONTROL
    #include "postProcess.H"

    #include "addCheckCaseOptions.H"
    #include "setRootCaseLists.H"
    #include "createTime.H"
    #include "createMesh.H"
    #include "createFields.H"
    #include "createFieldRefs.H"
    #include "createTimeControls.H"

    turbulence->validate();
    if(gMax(thermo.mu()().primitiveField())>SMALL)
        FatalErrorInFunction<<"Inviscid reference requires zero transport"<<exit(FatalError);
    const fileName referenceDir(runTime.path()/"postProcessing"/"centralReference"/runTime.timeName());mkDir(referenceDir);
    char rankName[64];std::snprintf(rankName,sizeof(rankName),"rank%04d.csv",Pstream::myProcNo());
    std::FILE* referenceFp=std::fopen((referenceDir/rankName).c_str(),"w");
    if(!referenceFp)FatalErrorInFunction<<"Cannot open reference budget"<<exit(FatalError);
    std::fputs("time,mass,absoluteEnergy,thermoEnergy,maxLocalEnergyResidual,sumYError,minY,minT,minP,maxRootResidual,maxRootTolerance,oldRootCriterionUnmet\n",referenceFp);


    // * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * //

    #include "readFluxScheme.H"

    const dimensionedScalar v_zero(dimVolume/dimTime, Zero);

    // Courant numbers used to adjust the time-step
    scalar CoNum = 0.0;
    scalar meanCoNum = 0.0;

    Info<< "\nStarting time loop\n" << endl;

    while (runTime.run())
    {
        // Old-state integrated species source, once per physical Euler step.
        chemistry->solve(runTime.deltaTValue());
        const scalarField energyOld(rhoE.primitiveField());
        volScalarField ea("eaAbsolute",e+thermo.hc()-p/rho);
        // --- Directed interpolation of primitive fields onto faces

        surfaceScalarField rho_pos(interpolate(rho, pos));
        surfaceScalarField rho_neg(interpolate(rho, neg));

        surfaceVectorField rhoU_pos(interpolate(rhoU, pos, U.name()));
        surfaceVectorField rhoU_neg(interpolate(rhoU, neg, U.name()));

        volScalarField rPsi("rPsi", 1.0/psi);
        surfaceScalarField rPsi_pos(interpolate(rPsi, pos, T.name()));
        surfaceScalarField rPsi_neg(interpolate(rPsi, neg, T.name()));

        surfaceScalarField e_pos(interpolate(ea, pos, T.name()));
        surfaceScalarField e_neg(interpolate(ea, neg, T.name()));

        surfaceVectorField U_pos("U_pos", rhoU_pos/rho_pos);
        surfaceVectorField U_neg("U_neg", rhoU_neg/rho_neg);

        surfaceScalarField p_pos("p_pos", rho_pos*rPsi_pos);
        surfaceScalarField p_neg("p_neg", rho_neg*rPsi_neg);

        surfaceScalarField phiv_pos("phiv_pos", U_pos & mesh.Sf());
        // Note: extracted out the orientation so becomes unoriented
        phiv_pos.setOriented(false);
        surfaceScalarField phiv_neg("phiv_neg", U_neg & mesh.Sf());
        phiv_neg.setOriented(false);

        volScalarField c("c", sqrt(thermo.Cp()/thermo.Cv()*rPsi));
        surfaceScalarField cSf_pos
        (
            "cSf_pos",
            interpolate(c, pos, T.name())*mesh.magSf()
        );

        surfaceScalarField cSf_neg
        (
            "cSf_neg",
            interpolate(c, neg, T.name())*mesh.magSf()
        );

        surfaceScalarField ap
        (
            "ap",
            max(max(phiv_pos + cSf_pos, phiv_neg + cSf_neg), v_zero)
        );

        surfaceScalarField am
        (
            "am",
            min(min(phiv_pos - cSf_pos, phiv_neg - cSf_neg), v_zero)
        );

        surfaceScalarField a_pos("a_pos", ap/(ap - am));

        surfaceScalarField amaxSf("amaxSf", max(mag(am), mag(ap)));

        surfaceScalarField aSf("aSf", am*a_pos);

        if (fluxScheme == "Tadmor")
        {
            aSf = -0.5*amaxSf;
            a_pos = 0.5;
        }

        surfaceScalarField a_neg("a_neg", 1.0 - a_pos);

        phiv_pos *= a_pos;
        phiv_neg *= a_neg;

        surfaceScalarField aphiv_pos("aphiv_pos", phiv_pos - aSf);
        surfaceScalarField aphiv_neg("aphiv_neg", phiv_neg + aSf);

        // Reuse amaxSf for the maximum positive and negative fluxes
        // estimated by the central scheme
        amaxSf = max(mag(aphiv_pos), mag(aphiv_neg));

        #include "centralCourantNo.H"
        #include "readTimeControls.H"

        if (LTS)
        {
            #include "setRDeltaT.H"
        }
        else
        {
            #include "setDeltaT.H"
        }

        ++runTime;

        Info<< "Time = " << runTime.timeName() << nl << endl;

        phi = aphiv_pos*rho_pos + aphiv_neg*rho_neg;

        surfaceVectorField phiU(aphiv_pos*rhoU_pos + aphiv_neg*rhoU_neg);
        // Note: reassembled orientation from the pos and neg parts so becomes
        // oriented
        phiU.setOriented(true);

        surfaceVectorField phiUp(phiU + (a_pos*p_pos + a_neg*p_neg)*mesh.Sf());

        surfaceScalarField phiEp
        (
            "phiEp",
            aphiv_pos*(rho_pos*(e_pos + 0.5*magSqr(U_pos)) + p_pos)
          + aphiv_neg*(rho_neg*(e_neg + 0.5*magSqr(U_neg)) + p_neg)
          + aSf*p_pos - aSf*p_neg
        );

        #include "hllcFlux.H"

        volScalarField muEff("muEff", turbulence->muEff());
        volTensorField tauMC("tauMC", muEff*dev2(Foam::T(fvc::grad(U))));

        // --- Solve density
        solve(fvm::ddt(rho) + fvc::div(phi));

        // --- Solve momentum
        solve(fvm::ddt(rhoU) + fvc::div(phiUp));

        U.ref() =
            rhoU()
           /rho();
        U.correctBoundaryConditions();
        rhoU.boundaryFieldRef() == rho.boundaryField()*U.boundaryField();

        if (!inviscid)
        {
            solve
            (
                fvm::ddt(rho, U) - fvc::ddt(rho, U)
              - fvm::laplacian(muEff, U)
              - fvc::div(tauMC)
            );
            rhoU = rho*U;
        }

        // All species share the central continuity reconstruction/weights.
        forAll(Y,s)
        {
            surfaceScalarField phiY("phiY",aphiv_pos*interpolate(rhoY[s],pos,rho.name())+aphiv_neg*interpolate(rhoY[s],neg,rho.name()));
            volScalarField source(IOobject("sourceY",runTime.timeName(),mesh,IOobject::NO_READ,IOobject::NO_WRITE,false),mesh,dimensionedScalar("zero",rho.dimensions()/dimTime,0));
            source.primitiveFieldRef()=chemistry->RR(s);
            solve(fvm::ddt(rhoY[s])+fvc::div(phiY)==source);
            Y[s].primitiveFieldRef()=rhoY[s].primitiveField()/rho.primitiveField();Y[s].correctBoundaryConditions();
        }
        // --- Solve absolute total energy: no chemical heat source
        surfaceScalarField sigmaDotU
        (
            "sigmaDotU",
            (
                fvc::interpolate(muEff)*mesh.magSf()*fvc::snGrad(U)
              + fvc::dotInterpolate(mesh.Sf(), tauMC)
            )
          & (a_pos*U_pos + a_neg*U_neg)
        );

        solve
        (
            fvm::ddt(rhoE)
          + fvc::div(phiEp)
          - fvc::div(sigmaDotU)
        );

        scalar referenceRootResidual=0,referenceRootTolerance=0,referenceOldCriterionUnmet=0;
        #include "recoverAbsoluteEnergy.H"
        e.correctBoundaryConditions();
        thermo.correct();
        rhoE.boundaryFieldRef() ==
            rho.boundaryField()*
            (
                e.boundaryField() + thermo.hc()().boundaryField() + 0.5*magSqr(U.boundaryField())
            )-p.boundaryField();

        if (!inviscid)
        {
            solve
            (
                fvm::ddt(rho, e) - fvc::ddt(rho, e)
              - fvm::laplacian(turbulence->alphaEff(), e)
            );
            thermo.correct();
            rhoE = rho*(e + 0.5*magSqr(U));
        }

        p.ref() =
            rho()
           /psi();
        p.correctBoundaryConditions();
        rho.boundaryFieldRef() == psi.boundaryField()*p.boundaryField();

        turbulence->correct();

        scalar sumError=0,minY=GREAT;
        forAll(rho,i){scalar total=0;forAll(Y,s){total+=Y[s][i];minY=Foam::min(minY,Y[s][i]);}sumError=Foam::max(sumError,Foam::mag(total-1));}
        sumError=returnReduce(sumError,maxOp<scalar>());minY=returnReduce(minY,minOp<scalar>());
        if(sumError>1e-8 || minY<-1e-12 || gMin(thermo.T().primitiveField())<=0 || gMin(p.primitiveField())<=0)
            FatalErrorInFunction<<"Reference admissibility failure "<<sumError<<","<<minY<<exit(FatalError);
        auto energyDiv=fvc::div(phiEp);scalar localResidual=0;
        forAll(rho,i)localResidual=Foam::max(localResidual,Foam::mag(mesh.V()[i]*(rhoE[i]-energyOld[i]+runTime.deltaTValue()*energyDiv()[i])));
        const scalar mass=gSum(mesh.V()*rho.primitiveField());
        const scalar absoluteEnergy=gSum(mesh.V()*rhoE.primitiveField());
        auto thermochemical=thermo.hc();const scalar reconstructed=gSum(mesh.V()*(rho.primitiveField()*(e.primitiveField()+thermochemical().primitiveField()+0.5*magSqr(U.primitiveField()))-p.primitiveField()));
        std::fprintf(referenceFp,"%.17g,%.17g,%.17g,%.17g,%.17g,%.17g,%.17g,%.17g,%.17g,%.17g,%.17g,%.17g\n",double(runTime.value()),double(mass),double(absoluteEnergy),double(reconstructed),double(returnReduce(localResidual,maxOp<scalar>())),double(sumError),double(minY),double(gMin(thermo.T().primitiveField())),double(gMin(p.primitiveField())),double(returnReduce(referenceRootResidual,maxOp<scalar>())),double(returnReduce(referenceRootTolerance,maxOp<scalar>())),double(returnReduce(referenceOldCriterionUnmet,sumOp<scalar>())));std::fflush(referenceFp);
        if(runTime.controlDict().getOrDefault<bool>("padWriteFinal",false) && runTime.value()+0.5*runTime.deltaTValue()>=runTime.endTime().value())runTime.writeNow();else runTime.write();
        if(runTime.writeTime())e.write();

        runTime.printExecutionTime(Info);
    }

    std::fclose(referenceFp);
    Info<< "End\n" << endl;

    return 0;
}

// ************************************************************************* //
