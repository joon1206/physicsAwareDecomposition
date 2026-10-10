"""Clean rebuild and corrected state-preserving campaign, sequentially."""
import json,subprocess,time
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];S=ROOT/'scripts';logs=ROOT/'data/raw/build';logs.mkdir(parents=True,exist_ok=True)
for name,args in [('cleanBuild',['bash',str(S/'cleanBuild.sh')]),('endpoint',['bash',str(S/'run.sh'),'endpointRegression.py']),('study',['python3',str(S/'executeStudy.py')]),('finish',['python3',str(S/'finish.py')])]:
    t=time.perf_counter();print('START corrected',name,flush=True)
    with (logs/('corrected_'+name+'.log')).open('w') as stream:result=subprocess.run(args,stdout=stream,stderr=subprocess.STDOUT)
    print('FINISHED corrected',name,result.returncode,time.perf_counter()-t,flush=True)
    if result.returncode:
        print('\n'.join((logs/('corrected_'+name+'.log')).read_text().splitlines()[-25:]),flush=True);raise SystemExit(result.returncode)
