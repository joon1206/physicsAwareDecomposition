/*---------------------------------------------------------------------------*\
  =========                 |
  \\      /  F ield         | OpenFOAM: The Open Source CFD Toolbox
   \\    /   O peration     |
    \\  /    A nd           | www.openfoam.com
     \\/     M anipulation  |
-------------------------------------------------------------------------------
    Copyright (C) 2011-2017 OpenFOAM Foundation
-------------------------------------------------------------------------------
License
    This file is part of OpenFOAM.

    OpenFOAM is free software: you can redistribute it and/or modify it
    under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    OpenFOAM is distributed in the hope that it will be useful, but
    WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
    General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with OpenFOAM.  If not, see <http://www.gnu.org/licenses/>.

Application
    reactingFoamPAD

Group
    grpCombustionSolvers

Description
    Solver for combustion with chemical reactions.

    Research instrumentation of reactingFoam: adds per-phase
    wall-clock timing (chemistry, species transport, energy,
    momentum, pressure, turbulence, I/O) and writes one CSV row
    per timestep per MPI rank. The numerical operations are
    identical to reactingFoam; only measurement is added.

\*---------------------------------------------------------------------------*/

#include "fvCFD.H"
#include "turbulentFluidThermoModel.H"
#include "psiReactionThermo.H"
#include "CombustionModel.H"
#include "multivariateScheme.H"
#include "pimpleControl.H"
#include "pressureControl.H"
#include "fvOptions.H"
#include "localEulerDdtScheme.H"
#include "fvcSmooth.H"
#include "phaseTimers.H"
#include "energyLedger.H"
#include "cellEnergyAudit.H"
#include "thermoDensityCorrector.H"
#include "processorPolyPatch.H"
#include <set>

// * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * //

int main(int argc, char *argv[])
{
    argList::addNote
    (
        "Solver for combustion with chemical reactions"
        " (instrumented: per-phase wall-clock timing)"
    );

    #include "postProcess.H"

    #include "addCheckCaseOptions.H"
    #include "setRootCaseLists.H"
    #include "createTime.H"
    #include "createMesh.H"
    #include "createControl.H"
    #include "createTimeControls.H"
    #include "initContinuityErrs.H"
    #include "createFields.H"
    #include "createFieldRefs.H"

    turbulence->validate();
    energyLedger ledger(mesh,runTime,Y);
    cellEnergyAudit cellAudit(mesh,runTime,Y);
    thermoDensityCorrector densityCorrector(mesh,runTime);
    if(densityCorrector.active() && !cellAudit.enabled)
        FatalErrorInFunction<<"Candidate correction currently requires both energy ledgers"<<exit(FatalError);
    if (ledger.enabled && (LTS || thermo.he().name() != "h" || mesh.dynamic()
        || pimple.consistent() || pimple.transonic()
        || word(mesh.ddtScheme("ddt(default)")[0].wordToken()) != "Euler"))
        FatalErrorInFunction << "Ledger requires Euler, fixed mesh, h, nontransonic/nonconsistent pressure" << exit(FatalError);


    if (!LTS)
    {
        #include "compressibleCourantNo.H"
        #include "setInitialDeltaT.H"
    }

    const bool timingEnabled=runTime.controlDict().getOrDefault<bool>("padTiming",true);
    Foam::phaseTimers phaseTimer(timingEnabled);
    label processorFaces=0; std::set<label> neighbours;
    forAll(mesh.boundaryMesh(),patchi)
    {
        const polyPatch& patch=mesh.boundaryMesh()[patchi];
        if(isA<processorPolyPatch>(patch))
        {
            const auto& pp=refCast<const processorPolyPatch>(patch);
            processorFaces+=pp.size(); neighbours.insert(pp.neighbProcNo());
        }
    }
    const fileName timingDir(runTime.path()/"postProcessing"/"performance");
    char rankName[32]; std::snprintf(rankName,sizeof(rankName),"rank%04d.csv",Pstream::myProcNo());
    const fileName timingFile(timingDir/rankName);
    std::FILE* timingFp=nullptr;
    if(timingEnabled)
    {
        mkDir(timingDir); timingFp=std::fopen(timingFile.c_str(),"w");
        if(!timingFp) FatalErrorInFunction << "Cannot open " << timingFile << exit(FatalError);
        phaseTimer.writeHeader(timingFp);
    }

    Info<< nl
        << "Phase timing output: " << timingFile << nl
        << "Starting time loop" << endl;

    // * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * //

    while (runTime.run())
    {
        ledger.start(rho,thermo,K,Qdot,dpdt);
        cellAudit.start(rho,thermo,K);
        phaseTimer.reset();
        phaseTimer.start(phaseTimers::timestep);
        #include "readTimeControls.H"

        if (LTS)
        {
            #include "setRDeltaT.H"
        }
        else
        {
            #include "compressibleCourantNo.H"
            #include "setDeltaT.H"
        }

        ++runTime;

        Info<< "Time = " << runTime.timeName() << nl << endl;


        phaseTimer.start(phaseTimers::rhoPhase);
        #include "rhoEqn.H"
        phaseTimer.stop(phaseTimers::rhoPhase);
        ledger.snapshot("rho_predictor",rho,thermo,K,Qdot,dpdt);

        while (pimple.loop())
        {
            ledger.outer();
            #include "UEqn.H"
            ledger.snapshot("momentum_predictor",rho,thermo,K,Qdot,dpdt);
            #include "YEqn.H"
            #include "EEqn.H"

            // --- Pressure corrector loop
            while (pimple.correct())
            {
                ledger.pressure();
                if (pimple.consistent())
                {
                    #include "pcEqn.H"
                }
                else
                {
                    #include "pEqn.H"
                }
            }

            if (pimple.turbCorr())
            {
                phaseTimer.start(phaseTimers::turbulencePhase);
                turbulence->correct();
                phaseTimer.stop(phaseTimers::turbulencePhase);
            }
        }

        rho = thermo.rho();
        densityCorrector.apply(rho,thermo,phi,turbulence->alphaEff(),dpdt,
            cellAudit.rhoAssembly(),cellAudit.sensibleSolved(),cellAudit.formationSolved(),cellAudit,turbulence->muEff(),K);
        cellAudit.finish(rho,thermo,K,phi,densityCorrector.momentumMismatch);
        ledger.finish(rho,thermo,K,Qdot,dpdt,phi);


        phaseTimer.start(phaseTimers::io);
        // timeStep output uses the checkpoint's inherited global timeIndex.
        // A continuation must also write its actual physical endpoint.
        const bool finalCheckpoint =
            runTime.controlDict().getOrDefault<bool>("padWriteFinal", false)
         && runTime.value() + 0.5*runTime.deltaTValue()
            >= runTime.endTime().value();
        if (finalCheckpoint)
        {
            runTime.writeNow();
            thermo.he().write();
            rho.write();
        }
        else
        {
            runTime.write();
        }
        phaseTimer.stop(phaseTimers::io);
        phaseTimer.stop(phaseTimers::timestep);

        if (timingFp)
        {
            phaseTimer.writeRow(timingFp, runTime.value(), runTime.timeIndex(), Pstream::myProcNo(), mesh.nCells(), processorFaces, neighbours.size());
        }

        runTime.printExecutionTime(Info);
    }

    if (timingFp)
    {
        std::fclose(timingFp);
    }

    Info<< "End\n" << endl;

    return 0;
}


// ************************************************************************* //
