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
    reactingFoamTimed

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

    if (!LTS)
    {
        #include "compressibleCourantNo.H"
        #include "setInitialDeltaT.H"
    }

    // Research phase timing: register phases and open the per-rank CSV
    Foam::phaseTimers phaseTimer;
    phaseTimer.registerPhase("timestep");
    phaseTimer.registerPhase("rho");
    phaseTimer.registerPhase("momentum");
    phaseTimer.registerPhase("chemistry");
    phaseTimer.registerPhase("species");
    phaseTimer.registerPhase("energy");
    phaseTimer.registerPhase("pressure");
    phaseTimer.registerPhase("turbulence");
    phaseTimer.registerPhase("io");

    const Foam::fileName timingDir(runTime.path()/"phaseTiming");
    Foam::mkDir(timingDir);

    const Foam::fileName timingFile
    (
        timingDir
       /Foam::fileName
        (
            "phaseTimes_rank"
          + std::to_string(Foam::Pstream::myProcNo())
          + ".csv"
        )
    );

    std::FILE* timingFp = std::fopen(timingFile.c_str(), "w");
    if (timingFp)
    {
        phaseTimer.writeHeader(timingFp);
    }

    Info<< nl
        << "Phase timing output: " << timingFile << nl
        << "Starting time loop" << endl;

    // * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * //

    while (runTime.run())
    {
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

        phaseTimer.reset();
        phaseTimer.start("timestep");

        phaseTimer.start("rho");
        #include "rhoEqn.H"
        phaseTimer.stop("rho");

        while (pimple.loop())
        {
            #include "UEqn.H"
            #include "YEqn.H"
            #include "EEqn.H"

            // --- Pressure corrector loop
            while (pimple.correct())
            {
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
                phaseTimer.start("turbulence");
                turbulence->correct();
                phaseTimer.stop("turbulence");
            }
        }

        rho = thermo.rho();

        phaseTimer.stop("timestep");

        phaseTimer.start("io");
        runTime.write();
        phaseTimer.stop("io");

        if (timingFp)
        {
            phaseTimer.writeRow(timingFp, runTime.timeIndex());
            std::fflush(timingFp);
        }

        runTime.printExecutionTime(Info);
    }

    if (timingFp)
    {
        Info<< nl
            << "Phase timing totals (rank "
            << Foam::Pstream::myProcNo() << ")" << nl;
        for (const std::string& name : phaseTimer.phases())
        {
            Info<< "    " << name << " = "
                << phaseTimer.get(name.c_str()) << " s" << nl;
        }

        std::fclose(timingFp);
    }

    Info<< "End\n" << endl;

    return 0;
}


// ************************************************************************* //
