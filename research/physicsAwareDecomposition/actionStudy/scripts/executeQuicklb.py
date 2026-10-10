"""Queue standalone prior-library reproduction after all OpenFOAM timings."""
from pathlib import Path
import json,subprocess,time
ROOT=Path(__file__).resolve().parents[1]
def busy():
    for f in Path('/proc').glob('[0-9]*/cmdline'):
        try:args=f.read_bytes().split(b'\0')
        except OSError:continue
        if any(a.endswith((b'/scripts/executeRemaining.py',b'/scripts/executeAccuracy.py')) for a in args):return True
    return False
print('Standalone QUICKLB reproduction queued after OpenFOAM timings.',flush=True)
while busy():time.sleep(10)
start=time.perf_counter();log=ROOT/'data/raw/campaignLogs/quicklb.log'
with log.open('w') as f:status=subprocess.run(['bash',str(ROOT/'scripts/reproduceQuicklb.sh')],stdout=f,stderr=subprocess.STDOUT).returncode
(ROOT/'data/processed/quicklb_status.json').write_text(json.dumps(dict(exitCode=status,wall=time.perf_counter()-start),indent=2))
print('FINISHED QUICKLB attempt',status,flush=True)
if status:print('\n'.join(log.read_text().splitlines()[-20:]),flush=True)
