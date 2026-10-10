"""Conservative sums of recorded accepted residual maxima; not error estimates."""
from pathlib import Path
import csv,json,math,re
from foamio import read_labels
ROOT=Path(__file__).resolve().parents[1];STUDY=ROOT/'candidateStudy';P=STUDY/'data/processed'

def main():
    rows=[]
    for policy,file in [('allowance-only','component_tolerance_allowance_only.json'),('exact-cycle','component_tolerance.json'),('cap-fallback','component_tolerance_cap.json')]:
        data=json.loads((P/file).read_text())
        for r in data['records']:
            if 'error' in r:continue
            case=STUDY/'data/raw'/r['name'];info=json.loads((case/'case.json').read_text())
            accepted=[];residual=[];allowance=[];seen=set()
            for path in case.glob('**/componentEnergyTolerance/*/rank*.csv'):
                rank=int(re.search(r'rank(\d+)',path.name)[1])
                nc=len(read_labels(case/f'processor{rank}/constant/polyMesh/cellProcAddressing')) if r['ranks']>1 else info['nCells']
                with path.open() as stream:trace=list(csv.DictReader(stream))
                for row in trace:
                    if not float(row['accepted']):continue
                    key=(rank,float(row['time']))
                    if key in seen:raise RuntimeError('Duplicate accepted rank/time '+str(path))
                    seen.add(key);accepted.append(key)
                    # Global residual maximum is duplicated on ranks. Weight each
                    # once by its local cell count: this bounds sum_i |r_i|.
                    residual.append(nc*float(row['globalMaxResidual']))
                    allowance.append(nc*float(row['maxLocalAllowance']))
            expected=r['steps']*r['ranks']
            if len(accepted)!=expected:raise RuntimeError(f"Accepted trace count {len(accepted)} != {expected}: {case.name}")
            difference=abs(r['end']['E_stored']-r['initial']['E_stored'])
            rows.append(dict(policy=policy,name=r['name'],acceptedRankSteps=len(accepted),
                             absoluteInventoryChange=difference,
                             accumulatedResidualMagnitudeUpperSum=math.fsum(residual),
                             accumulatedComponentAllowanceUpperSum=math.fsum(allowance),
                             sourceSnapshot=r['sourceSnapshot'],executableSHA256=r['executableSHA256']))
    result=dict(records=rows,scope='Sum over accepted steps/ranks of nLocal times recorded residual maximum or local allowance maximum. The former bounds the sum of absolute assembled residuals, not accumulated solution/truncation error. Independent inventory includes representation/other residual effects; no certified thermodynamic error bound is asserted.')
    (P/'component_tolerance_bounds.json').write_text(json.dumps(result,indent=2)+'\n')
    for r in rows:
        if 'coldHighPressure' in r['name']:print(r)
    print('Recorded accepted-residual sums',len(rows))
if __name__=='__main__':main()
