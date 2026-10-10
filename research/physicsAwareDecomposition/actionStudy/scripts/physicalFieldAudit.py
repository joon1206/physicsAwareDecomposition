"""Audit every retained final-epoch endpoint for finite, admissible fields."""
import json,math
from caseFactory import ROOT,latest_time
from mapping import assemble
from foamio import read_field
FOLDERS=['histories','oracle','deployment','live','profilesOn','profilesOff','controllerProfiles',
    'mpiConsequencesOn','mpiConsequencesOff','scaling','gamma','fineOracle','fineHistories',
    'confirmation','confirmationNegative','continuousOracle','repeatedMigration','restartRegressionPsi',
    'conservationDiagnosis','conservationRefinement','refine','liveMeshFollowup','conservationCoupling','initialState','initialStateLong','fluxDiagnosis','fluxRepair']
def main():
    records=[];cases=set()
    for name in FOLDERS:
        base=ROOT/'data/raw'/name
        for pattern in ['*/case.json','*/*/case.json']:
            cases.update(p.parent for p in base.glob(pattern))
    for case in sorted(cases):
        info=json.loads((case/'case.json').read_text());parallel=any(case.glob('processor[0-9]*'));end=latest_time(case,parallel)
        arrays={};bad=[]
        for field in ['T','p','U','Qdot','h','rho']+info['species']:
            values=assemble(case,end,field,info['nCells']) if parallel else read_field(case/end/field,info['nCells'])
            flat=[v for x in values for v in (x if isinstance(x,tuple) else [x])]
            if not all(math.isfinite(v) for v in flat):bad.append(field)
            arrays[field]=values
        minimum={field:min(arrays[field]) for field in ['T','p','rho']}
        min_y=min(min(arrays[field]) for field in info['species'])
        normalization=max(abs(sum(arrays[field][i] for field in info['species'])-1) for i in range(info['nCells']))
        passed=not bad and all(v>0 for v in minimum.values()) and min_y>=-1e-12 and normalization<1e-10
        records.append(dict(path=str(case.relative_to(ROOT)),time=float(end),nonfiniteFields=bad,minimum=minimum,
            maximumTemperature=max(arrays['T']),minY=min_y,sumYError=normalization,passed=passed))
    result=dict(passed=bool(records) and all(r['passed'] for r in records),cases=records,
        scope='Final-epoch endpoints only; rejected protocols excluded explicitly. Basic field admissibility supplements action equivalence and does not assert physical conservation or convergence.')
    (ROOT/'data/processed/physical_field_audit.json').write_text(json.dumps(result,indent=2))
    if not result['passed']:raise RuntimeError('field admissibility audit failed; evidence retained')
    print('PASSED finite-field, positive T/p/rho and species audit for',len(records),'endpoints')
if __name__=='__main__':main()
