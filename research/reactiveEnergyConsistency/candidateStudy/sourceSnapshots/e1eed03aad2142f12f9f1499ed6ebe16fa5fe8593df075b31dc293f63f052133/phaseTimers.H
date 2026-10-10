// Rank-local exclusive phase timers; no collective operations.
#ifndef phaseTimers_H
#define phaseTimers_H
#include <chrono>
#include <cstdio>
namespace Foam
{
class phaseTimers
{
    typedef std::chrono::steady_clock Clock;
public:
    enum Phase { timestep, rhoPhase, momentum, chemistry, species, energy, pressure, turbulencePhase, io, count };
private:
    bool enabled_;
    double sums_[count] = {};
    Clock::time_point starts_[count];
    bool active_[count] = {};
public:
    explicit phaseTimers(bool enabled=true) : enabled_(enabled) {}
    void reset() { for(int i=0;i<count;++i) { sums_[i]=0; active_[i]=false; } }
    void start(Phase p) { if(enabled_) { starts_[p]=Clock::now(); active_[p]=true; } }
    void stop(Phase p)
    {
        if(enabled_ && active_[p])
        { sums_[p]+=std::chrono::duration<double>(Clock::now()-starts_[p]).count(); active_[p]=false; }
    }
    static void writeHeader(FILE* fp)
    {
        std::fputs("time,timeIndex,rank,nCells,processorFaces,nNeighbours,stepWall,rhoWall,momentumWall,chemistryWall,speciesWall,energyWall,pressureWall,turbulenceWall,ioWall\n",fp);
    }
    void writeRow(FILE* fp, scalar time, label index, label rank, label cells, label faces, label neighbours) const
    {
        std::fprintf(fp,"%.17g,%d,%d,%d,%d,%d",double(time),index,rank,cells,faces,neighbours);
        for(int i=0;i<count;++i) std::fprintf(fp,",%.12g",sums_[i]);
        std::fputc('\n',fp);
    }
};
}
#endif
