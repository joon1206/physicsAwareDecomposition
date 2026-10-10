"""Coupling versus full-block state, conserved/quenching controls and actual cost."""
from pathlib import Path
import json,math,re
from analyze import compare,fields
ROOT=Path(__file__).resolve().parents[1];STUDY=ROOT/'candidateStudy'
summary=json.loads((STUDY/'data/processed/screen_summary.json').read_text());records=[]
mpi=json.loads((STUDY/'data/processed/mpi_counts.json').read_text());mpiLookup={r['name']:r for r in mpi}
for r in summary:
    if r['mode']!='blockConservative' or r.get('blockPressureTolerance') is None:continue
    case=STUDY/'data/raw'/r['name'];stem=f"{r['kind']}_blockConservative_dt{r['dt']:g}_s1_g0_o1_p1";reference=STUDY/'data/raw'/stem
    ts=fields(case,r['ranks'],r['dt']*r['steps'],'T',r['nCells'])
    counts={}
    for field,iterations in re.findall(r'Solving for (\w+),[^\n]*No Iterations (\d+)',(case/'solver.log').read_text()):
        c=counts.setdefault(field,dict(solves=0,iterations=0));c['solves']+=1;c['iterations']+=int(iterations)
    row=dict(name=r['name'],kind=r['kind'],dt=r['dt'],pressureTolerance=r['blockPressureTolerance'],
        Tmean=math.fsum(ts)/len(ts),Tmin=min(ts),Tmax=max(ts),momentumMismatch=r['maxMomentumDeltaU'],
        energyDrift=r['signedEnergyDrift'],massDrift=r['massDrift'],maxElementDrift=max(abs(v) for v in r['elementDrift'].values()),
        wallSingleTrial=r['solverWall'],linearSolvers=counts,fullBlockSameDtReference=reference.name,
        fieldDifferences=compare(reference,case),sourceSnapshot=r['sourceSnapshot'],executableSHA256=r['executableSHA256'])
    if r['name'] in mpiLookup:row['MPI']=mpiLookup[r['name']]
    records.append(row)
(STUDY/'data/processed/coupling_tolerance.json').write_text(json.dumps(dict(records=records,
    scope='Difference from tight block at the same dt/mesh; no independent exact error or guaranteed PDE accuracy controller. Single-trial wall measurements and separate instrumentation are not paired performance estimates.'),indent=2)+'\n')
for r in records:print(r['name'],'Tmean',r['Tmean'],'deltaU',r['momentumMismatch'],'T L1 vs tight',r['fieldDifferences']['T']['L1'])
