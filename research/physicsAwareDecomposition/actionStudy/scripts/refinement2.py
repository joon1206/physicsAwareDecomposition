import json,re
from caseFactory import *
from oracle import copy_checkpoint,action_setup
from features import rank_costs
from mapping import canonical_directory
from validation import numerical_gate
source=ROOT/'data/raw/pilot_histories_limitedLinear/persistent';info=json.loads((source/'case.json').read_text());cp='4e-05'
cost,_=rank_costs(source,cp,256);results={}
for setting,dt,integrator,upwind in [('rosenbrock',2e-6,'Rosenbrock34',False),('upwind',2e-6,'seulex',True),('upwindSmallDt',.5e-6,'Rosenbrock34',True)]:
 dirs={};failed=False
 for action in ['A0','AM']:
  c=ROOT/'data/raw/refinement2'/setting/action
  copy_checkpoint(source,c,cp);action_setup(c,action,cp,cost,4)
  set_control(c,start=float(cp),steps=round(.00016/dt),dt=dt)
  f=c/'system/fvSolution';s=re.sub(r'(tolerance\s+)[^;]+;',r'\g<1>1e-14;',f.read_text());f.write_text(s)
  f=c/'constant/chemistryProperties';f.write_text(f.read_text().replace('solver Rosenbrock34','solver '+integrator))
  if upwind:
   f=c/'system/fvSchemes';f.write_text(re.sub(r'limitedLinearV? 1','upwind',f.read_text()))
  try:elapsed=solve(c,4,timeout=180)
  except RuntimeError as error:
   results[setting]={'status':'FAILED','error':str(error)};failed=True;print('FAILED refinement',setting,action,error,flush=True);break
  end=latest_time(c,True);fields=['T','p','U','Qdot']+info['species'];dirs[action]=canonical_directory(c,end,fields,256)
  print('MEASURED refinement',setting,action,elapsed,flush=True)
 if not failed:
  gate=numerical_gate(dirs['A0'],dirs['AM'],info);results[setting]=gate
  print('REFINEMENT GATE',setting,gate['pass_'],{k:v['Linf'] for k,v in gate['fields'].items()},flush=True)
 (ROOT/'data/processed/refinement2.json').write_text(json.dumps(results,indent=2))
