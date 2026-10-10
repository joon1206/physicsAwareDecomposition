"""Field comparisons clearly separate self-reference from independent exact errors."""
from pathlib import Path
import json,math,re,csv
from analyze import compare,fields
from foamio import read_field
ROOT=Path(__file__).resolve().parents[1];STUDY=ROOT/'candidateStudy'
records=json.loads((STUDY/'data/processed/screen_summary.json').read_text())
accepted=ROOT/'data/raw/F_dt3.125e-08_p4'
if not (accepted/'result.json').exists():
    accepted=ROOT/'data/raw/F_dt3.125e-08_p4_fine'
reference=STUDY/'data/raw/F_conservativeState_dt1.25e-07_s1_g0_o1_p1'
blockReference=STUDY/'data/raw/F_blockConservative_dt1.25e-07_s1_g0_o1_p1'
out=[]
for r in records:
    if r['kind']!='F' or r['formationAblation']['scale']!=1 or 'pilot' in r['name']:continue
    case=STUDY/'data/raw'/r['name'];ts=fields(case,r['ranks'],r['dt']*r['steps'],'T',r['nCells'])
    us=fields(case,r['ranks'],r['dt']*r['steps'],'U',r['nCells']);mass=r['massDrift']
    row=dict(name=r['name'],mode=r['mode'],dt=r['dt'],wall=r['solverWall'],energyDrift=r['signedEnergyDrift'],
       Tmin=min(ts),Tmax=max(ts),Tmean=math.fsum(ts)/len(ts),Umax=max(math.sqrt(math.fsum(x*x for x in u)) for u in us),
       pressureMomentumMismatch=r['maxMomentumDeltaU'],massDrift=mass,
       conservativeSelfReference=compare(reference,case))
    row['blockSelfReference']=compare(blockReference,case)
    if (accepted/'result.json').exists():row['preservedBaselineFineComparison']=compare(accepted,case)
    # Count solver invocations and iterations from actual logs; corrections are named separately.
    log=(case/'solver.log').read_text();counts={}
    for name,iterations in re.findall(r'Solving for (\w+),[^\n]*No Iterations (\d+)',log):
        v=counts.setdefault(name,dict(solves=0,iterations=0));v['solves']+=1;v['iterations']+=int(iterations)
    row['linearSolvers']=counts;out.append(row)
    print(r['name'],f"T {row['Tmin']:.2f}..{row['Tmax']:.2f} mean {row['Tmean']:.2f} Umax {row['Umax']:.2f} self T L1 {row['conservativeSelfReference']['T']['L1']:.2f}",flush=True)
(STUDY/'data/processed/solution_comparisons.json').write_text(json.dumps(dict(records=out,
    references=dict(conservativeSelfReference=reference.name,blockSelfReference=blockReference.name,preservedBaselineFineComparison=accepted.name),
    caution='Neither reacting reference is an independent exact solution. Conservative/self and preserved baseline comparisons diagnose trajectory and refinement differences only.'),indent=2)+'\n')
