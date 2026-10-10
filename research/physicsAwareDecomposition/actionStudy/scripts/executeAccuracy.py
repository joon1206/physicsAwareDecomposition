"""Wait for the sequential main suite, then audit accuracy without job overlap."""
from pathlib import Path
import json,shutil,subprocess,time
ROOT=Path(__file__).resolve().parents[1]
def suite_running():
    for f in Path('/proc').glob('[0-9]*/cmdline'):
        try:args=f.read_bytes().split(b'\0')
        except OSError:continue
        if any(a.endswith(b'/scripts/executeRemaining.py') for a in args):return True
    return False
print('Accuracy follow-up queued after timed supplemental suite.',flush=True)
while suite_running():time.sleep(10)
old=ROOT/'data/processed/inventories.json'
if old.exists():shutil.copy2(old,ROOT/'data/processed/inventories_initialEOS.json')
archive=ROOT/'data/raw/inventoryInitialEOS';archive.mkdir(exist_ok=True)
for case in (ROOT/'data/raw/histories').iterdir():
    for f in case.glob('processor*/postProcessing/inventory/rank*.csv'):
        shutil.copy2(f,archive/(case.name+'_'+f.name))
phases=[('storedInventoryBuild',['bash',str(ROOT/'scripts/buildInventory.sh')]),
 ('storedInventory',['bash',str(ROOT/'scripts/run.sh'),'verifyNumerics.py','inventories']),
 ('accuracy',['bash',str(ROOT/'scripts/run.sh'),'accuracyFollowup.py']),
 ('extendedGates',['bash',str(ROOT/'scripts/run.sh'),'oracle.py','collect']),
 ('extendedNorms',['bash',str(ROOT/'scripts/run.sh'),'verifyNumerics.py','norms'])]
rows=[]
for name,args in phases:
    print('START follow-up',name,flush=True);start=time.perf_counter();log=ROOT/f'data/raw/campaignLogs/{name}.log'
    with log.open('w') as stream:status=subprocess.run(args,stdout=stream,stderr=subprocess.STDOUT).returncode
    rows.append(dict(phase=name,exitCode=status,wall=time.perf_counter()-start))
    (ROOT/'data/processed/accuracy_status.json').write_text(json.dumps(rows,indent=2))
    print('FINISHED follow-up',rows[-1],flush=True)
    if status:print('\n'.join(log.read_text().splitlines()[-14:]),flush=True)
