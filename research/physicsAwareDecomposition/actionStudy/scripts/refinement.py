import json,re
from caseFactory import *
from oracle import copy_checkpoint,action_setup
from features import rank_costs
from mapping import canonical_directory
from validation import numerical_gate
source=ROOT/'data/raw/pilot_histories_limitedLinear/persistent';info=json.loads((source/'case.json').read_text());cp='4e-05'
cost,_=rank_costs(source,cp,256)
results={}
for setting,dt,linear,absolute,relative in [
 ('tightLinear',2e-6,'1e-14','1e-12','1e-5'),
 ('tightODE',2e-6,'1e-14','1e-16','1e-8'),
 ('smallDt',.5e-6,'1e-14','1e-16','1e-8')]:
 dirs={}
 for action in ['A0','AM']:
  c=ROOT/'data/raw/refinement'/setting/action
  copy_checkpoint(source,c,cp)
  action_setup(c,action,cp,cost,4)
  set_control(c,start=float(cp),steps=round(.00016/dt),dt=dt)
  f=c/'system/fvSolution';s=f.read_text();s=re.sub(r'(tolerance\s+)[^;]+;',lambda m:m[1]+linear+';',s);f.write_text(s)
  f=c/'constant/chemistryProperties';s=f.read_text().replace('solver Rosenbrock34','solver seulex').replace('absTol 1e-12','absTol '+absolute).replace('relTol 1e-5','relTol '+relative);f.write_text(s)
  elapsed=solve(c,4,timeout=240)
  end=latest_time(c,True);fields=['T','p','U','Qdot']+info['species']
  dirs[action]=canonical_directory(c,end,fields,256)
  print('MEASURED refinement',setting,action,elapsed,flush=True)
 gate=numerical_gate(dirs['A0'],dirs['AM'],info)
 results[setting]=gate
 (ROOT/'data/processed/refinement.json').write_text(json.dumps(results,indent=2))
 print('REFINEMENT GATE',setting,gate['pass_'],{k:v['Linf'] for k,v in gate['fields'].items()},flush=True)
