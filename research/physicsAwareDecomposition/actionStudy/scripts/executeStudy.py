"""Sequential corrected checkpoint, deployment, profiling and accuracy study."""
import json,subprocess,time,os
from pathlib import Path
ROOT=Path(os.environ.get('PAD_ACTION_ROOT',Path(__file__).resolve().parents[1]))
SCRIPTS=Path(__file__).resolve().parent
subprocess.run(['bash',str(SCRIPTS/'run.sh'),'captureProvenance.py'],check=True)
for filename in ['environment_manifest.json','source_manifest.json']:
 source=ROOT/'docs'/filename
 target=source.with_stem(source.stem+'_v3_execution')
 if not target.exists():target.write_bytes(source.read_bytes())
phases=[('baseline',['validation.py']),('oracle',['oracle.py','small']),('horizon',['supplement.py','horizons']),('analysis',['analysis.py']),('deployment',['controller.py','checkpoint']),('live',['controller.py','live']),('profiles',['supplement.py','profiles']),('scaling',['supplement.py','scaling']),('gamma',['supplement.py','gamma']),('accuracy',['accuracyFollowup.py']),('workload',['workload.py']),('inventories',['verifyNumerics.py','inventories']),('norms',['verifyNumerics.py','norms']),('refinement',['verifyNumerics.py','refinement'])]
logs=ROOT/'data/raw/campaignLogs';logs.mkdir(parents=True,exist_ok=True);rows=[]
for name,args in phases:
 start=time.perf_counter();print('START state-preserving study',name,flush=True)
 with (logs/(name+'.log')).open('w') as f:
  code=subprocess.run(['bash',str(SCRIPTS/'run.sh')]+args,stdout=f,stderr=subprocess.STDOUT).returncode
 row=dict(phase=name,exitCode=code,wall=time.perf_counter()-start);rows.append(row)
 (ROOT/'data/processed/campaign_status.json').write_text(json.dumps(rows,indent=2))
 print('FINISHED state-preserving study',row,flush=True)
 if code:
  print('\n'.join((logs/(name+'.log')).read_text().splitlines()[-12:]),flush=True)
  if name in ['baseline','oracle','horizon','analysis']:raise SystemExit(code)
