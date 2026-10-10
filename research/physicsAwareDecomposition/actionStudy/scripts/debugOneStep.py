import json
from caseFactory import *
from oracle import copy_checkpoint,action_setup,local_weights
from features import rank_costs,normalize
from mapping import canonical_directory
from validation import numerical_gate
source=ROOT/'data/raw/pilot_histories_limitedLinear/persistent';info=json.loads((source/'case.json').read_text());cp='4e-05'
cost,_=rank_costs(source,cp,256)
cases={}
for action in ['A0','nativeMesh']:
 c=ROOT/'data/raw/debugThermoCorrections'/action
 copy_checkpoint(source,c,cp);set_chemistry(c,'A0',0)
 if action=='nativeMesh':action_setup(c,'AM',cp,cost,4)
 if action=='serialMesh':
  command(['reconstructPar','-time',cp],c,c/'reconstructCp.log')
  weights=normalize(cost)
  t=header('cellWeight','volScalarField')+'dimensions [0 0 0 0 0 0 0];\ninternalField nonuniform List<scalar>\n256\n(\n'
  t+='\n'.join(str(x) for x in weights)+'\n);\n'+(c/cp/'chemCost').read_text().split('boundaryField',1)[1].join(['boundaryField',''])
  (c/cp/'cellWeight').write_text(t)
  decompose(c,4,True,float(cp),True)
 set_control(c,start=float(cp),steps=80)
 solve(c,4);end=latest_time(c,True)
 fields=['T','p','U','Qdot']+info['species']
 cases[action]=canonical_directory(c,end,fields,256)
for action in ['nativeMesh']:
 gate=numerical_gate(cases['A0'],cases[action],info)
 print(action,gate['pass_'],{k:v['Linf'] for k,v in gate['fields'].items()},flush=True)
