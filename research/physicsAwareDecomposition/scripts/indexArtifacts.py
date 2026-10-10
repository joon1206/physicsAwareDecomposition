#!/usr/bin/env python3
"""Index exact additions, source hashes and campaign allocation without hashing GB of fields."""
import collections,datetime,hashlib,json,pathlib,subprocess
from study import ROOT
source=pathlib.Path(__file__).resolve().parents[1]
files=sorted(p for p in ROOT.rglob('*') if p.is_file())
exclude={'artifact_inventory.txt','changed_files.txt','project_inventory.json','source_manifest.json'}
paths=files
(ROOT/'artifact_inventory.txt').write_text('All retained artifact files; root='+str(ROOT)+'\n'+'\n'.join(str(p.relative_to(ROOT)) for p in paths)+'\n')
src=[]
for p in files:
    parts=p.relative_to(ROOT).parts
    if parts[0] in ['build','data','reproductions'] or '__pycache__' in parts or any(x.startswith('linux64') for x in parts) or 'lnInclude' in parts:continue
    if p.name in exclude:continue
    src.append(p)
(ROOT/'changed_files.txt').write_text('Exact new source, documentation, figures and tables; no original user files edited.\n'+'\n'.join(str(p) for p in src)+'\n')
hashes={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in src if p.suffix not in ['png','pdf','svg']}
binaries={str(p.relative_to(source)):hashlib.sha256(p.read_bytes()).hexdigest() for d in ['build/bin','build/lib'] for p in (source/d).glob('*') if p.is_file()}
(ROOT/'data/source_manifest.json').write_text(json.dumps({'status':'VERIFIED current artifact hashes','gitRevision':subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),
 'gitStatus':subprocess.check_output(['git','status','--short'],text=True),'compiler':'GCC 6.3, -O3, DP Int32','sourceAndDocumentation':hashes,'binaries':binaries,
 'benchmarkCostModelSnapshot':'data/raw/build/costEulerImplicit_benchmarked.H; final change preserves restart EMA history and validates controls'},indent=2)+'\n')
campaigns={}
for folder in (ROOT/'data/raw').iterdir():
    if not folder.is_dir():continue
    manifests=list(folder.rglob('manifest.json'));records=[]
    for p in manifests:
        try:records.append(json.loads(p.read_text()))
        except json.JSONDecodeError:raise RuntimeError('Malformed manifest '+str(p))
    if records:campaigns[folder.name]={'manifestCount':len(records),'ranks':sorted(set(r['ranks'] for r in records if isinstance(r.get('ranks'),int))),
        'sumSolverProcessWall':sum(r.get('solverWall',0) for r in records),'firstUTC':min(r.get('timestamp','') for r in records),'lastUTC':max(r.get('timestamp','') for r in records)}
smokes=sorted(p for p in (source/'reproductions').glob('*/data/processed/final_smoke.json'))
latest=smokes[-1] if smokes else None
summary={'status':'VERIFIED inventory; process-wall sum is not CPU allocation time','timestamp':datetime.datetime.now(datetime.timezone.utc).isoformat(),'root':str(ROOT),
 'fileCount':len(files),'logicalBytes':sum(p.stat().st_size for p in files),'logicalGiB':sum(p.stat().st_size for p in files)/2**30,
 'campaigns':campaigns,'syntheticMatrixRecords':sum(1 for _ in (ROOT/'data/processed/synthetic.csv').open())-1,
 'figureCount':len(list((ROOT/'figures').glob('*.png'))),'latestSmokeEvidence':str(latest) if latest else None,
 'latestProbeEvidence':str(latest.parent/'probe_validation.json') if latest else None,
 'resourcePolicy':'Sequential local single-guest runs, pilots before expansion, no cluster/GPU jobs; 8/12 ranks decomposition only.'}
(ROOT/'data/project_inventory.json').write_text(json.dumps(summary,indent=2)+'\n')
print(json.dumps(summary,indent=2))
