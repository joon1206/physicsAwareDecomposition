/*---------------------------------------------------------------------------*\
  =========                 |
  \\      /  F ield         | OpenFOAM: The Open Source CFD Toolbox
   \\    /   O peration     |
    \\  /    A nd           | www.openfoam.com
     \\/     M anipulation  |
-------------------------------------------------------------------------------
    Research instrumentation: per-phase wall-clock timers.

    Description
        Minimal, composable wall-clock phase timer for load-balance
        research. Uses std::chrono::steady_clock (monotonic,
        sub-microsecond) because Foam::clock::elapsedClockTime() is
        time_t-based (1 s resolution, too coarse for per-phase
        timing) and Foam::cpuTime measures CPU time only.

        Timers are accumulated per named phase and reset each
        timestep. One CSV row per timestep is written per MPI rank.

    NOTE
        This adds measurement overhead only. It does not alter any
        numerical operation, field, solver call, or write schedule.

\*---------------------------------------------------------------------------*/

#ifndef phaseTimers_H
#define phaseTimers_H

#include <chrono>
#include <cstdio>
#include <map>
#include <string>
#include <vector>

// * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * //

namespace Foam
{

//- Accumulates wall-clock time (seconds) for named phases.
//  Not thread-safe; intended for the single-threaded solver loop.
class phaseTimers
{
    // Private types

        typedef std::chrono::steady_clock clock_t;

    // Private data

        //- Accumulated time per phase name
        std::map<std::string, double> sums_;

        //- Start time per currently-active phase
        std::map<std::string, clock_t::time_point> starts_;

        //- Ordered phase names for stable CSV columns
        std::vector<std::string> order_;

public:

    // Constructors

        //- Construct null
        phaseTimers() = default;

    // Member Functions

        //- Register a phase name (idempotent) so its column is stable
        void registerPhase(const std::string& name)
        {
            if (sums_.find(name) == sums_.end())
            {
                sums_[name] = 0.0;
                order_.push_back(name);
            }
        }

        //- Start timing a named phase
        inline void start(const char* name)
        {
            starts_[name] = clock_t::now();
        }

        //- Stop timing a named phase and accumulate the elapsed time
        inline void stop(const char* name)
        {
            auto it = starts_.find(name);
            if (it == starts_.end())
            {
                return;
            }

            const double dt =
                std::chrono::duration<double>(clock_t::now() - it->second)
               .count();

            sums_[name] += dt;
            starts_.erase(it);
        }

        //- Accumulated time for a phase (0 if never started)
        inline double get(const char* name) const
        {
            auto it = sums_.find(name);
            return (it == sums_.end() ? 0.0 : it->second);
        }

        //- Reset all accumulators (call at the start of each timestep)
        inline void reset()
        {
            for (auto& kv : sums_)
            {
                kv.second = 0.0;
            }
            starts_.clear();
        }

        //- Ordered phase names
        inline const std::vector<std::string>& phases() const
        {
            return order_;
        }

        //- Write a header line to an open FILE
        void writeHeader(FILE* fp) const
        {
            std::fputs("step", fp);
            for (const std::string& name : order_)
            {
                std::fputs(",", fp);
                std::fputs(name.c_str(), fp);
            }
            std::fputc('\n', fp);
        }

        //- Write one data row (timestep plus all phase times)
        void writeRow(FILE* fp, const label timestep) const
        {
            std::fprintf(fp, "%d", timestep);
            for (const std::string& name : order_)
            {
                const double t = get(name.c_str());
                std::fprintf(fp, ",%.9g", t);
            }
            std::fputc('\n', fp);
        }
};

} // End namespace Foam

// * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * //

#endif

// ************************************************************************* //
