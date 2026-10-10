import json,shutil,time
from caseFactory import ROOT,make_case,decompose,solve,set_control,latest_time
from oracle import copy_checkpoint,run_branch
from mapping import canonical_directory
from validation import numerical_gate
c=make_case('endpointRegression/source','persistent',nx=32,ny=8,steps=20,trace=1)
decompose(c,4);solve(c,4)
results=[]
for action in ['A0','AC','AM','AH']:
 target=run_branch(c,'4e-05',action,7,0,'endpointRegression/branches')
 assert abs(float(latest_time(target,True))-54e-6)<1e-13
 results.append(str(target.relative_to(ROOT)))
info=json.loads((c/'case.json').read_text());fields=['T','p','U','Qdot','h','rho']+info['species']
reference=ROOT/results[0];end=latest_time(reference,True);gates=[]
for path in results[1:]:
 gates.append(numerical_gate(*[canonical_directory(x,end,fields,info['nCells']) for x in [reference,ROOT/path]],info))
assert all(g['pass_'] for g in gates)
(ROOT/'data/processed/endpoint_regression.json').write_text(json.dumps(dict(paths=results,gates=gates,endTime=float(end)),indent=2))
print('PASSED physical endpoint and four-action MPI regression',end,flush=True)
