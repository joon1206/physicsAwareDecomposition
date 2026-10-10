"""Sequential campaign launcher: no overlapping timed solver jobs."""
import json,os,subprocess,time
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];PAD=ROOT.parent
def active_oracle():
    for proc in Path('/proc').glob('[0-9]*/cmdline'):
        try:args=proc.read_bytes().split(b'\0')
        except OSError:continue
        if b'small' in args and any(a.endswith(b'/actionStudy/scripts/oracle.py') for a in args):return True
    return False
print('Waiting for existing oracle process before supplemental measurements.',flush=True)
while active_oracle():time.sleep(10)
phases=[
 ('inventoryBuild',['bash',str(ROOT/'scripts/buildInventory.sh')]),
 ('mpiBuild',['bash',str(ROOT/'scripts/buildMPI.sh')]),
 ('horizon',['bash',str(ROOT/'scripts/run.sh'),'supplement.py','horizons']),
 ('analysis',['bash',str(ROOT/'scripts/run.sh'),'analysis.py']),
 ('workload',['bash',str(ROOT/'scripts/run.sh'),'workload.py']),
 ('inventory',['bash',str(ROOT/'scripts/run.sh'),'verifyNumerics.py','inventories']),
 ('norms',['bash',str(ROOT/'scripts/run.sh'),'verifyNumerics.py','norms']),
 ('refinement',['bash',str(ROOT/'scripts/run.sh'),'verifyNumerics.py','refinement']),
 ('deployment',['bash',str(ROOT/'scripts/run.sh'),'controller.py','checkpoint']),
 ('live',['bash',str(ROOT/'scripts/run.sh'),'controller.py','live']),
 ('profiles',['bash',str(ROOT/'scripts/run.sh'),'supplement.py','profiles']),
 ('scaling',['bash',str(ROOT/'scripts/run.sh'),'supplement.py','scaling']),
 ('gamma',['bash',str(ROOT/'scripts/run.sh'),'supplement.py','gamma'])]
results=[];logs=ROOT/'data/raw/campaignLogs';logs.mkdir(parents=True,exist_ok=True)
for name,args in phases:
    start=time.perf_counter();print('START phase',name,flush=True)
    with (logs/(name+'.log')).open('w') as f:status=subprocess.run(args,stdout=f,stderr=subprocess.STDOUT).returncode
    row=dict(phase=name,exitCode=status,wall=time.perf_counter()-start);results.append(row)
    (ROOT/'data/processed/campaign_status.json').write_text(json.dumps(results,indent=2))
    print('FINISHED phase',row,flush=True)
    if status:print('\n'.join((logs/(name+'.log')).read_text().splitlines()[-12:]),flush=True)
print('Supplemental phases complete. Inspect and repair failed phases before reporting.',flush=True)
