"""Retain exact experimental source before mutations, including first ablations."""
from pathlib import Path
import hashlib,json,shutil
ROOT=Path(__file__).resolve().parents[1]
app=ROOT/'applications/reactingEnergyCandidates'
source={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in app.iterdir() if p.suffix in ['.H','.C']}
version=hashlib.sha256(json.dumps(source,sort_keys=True).encode()).hexdigest()
snapshot=ROOT/'candidateStudy/sourceSnapshots'/version
if not snapshot.exists():
    snapshot.mkdir(parents=True)
    for p in app.iterdir():
        if p.suffix in ['.H','.C']:shutil.copy2(p,snapshot/p.name)
    shutil.copytree(app/'Make',snapshot/'Make',ignore=shutil.ignore_patterns('linux*'))
for p in (ROOT/'candidateStudy/data/raw').glob('*/experiment.json'):
    v=json.loads(p.read_text())
    if v['source']==source:
        v['sourceSnapshot']=str(snapshot.relative_to(ROOT));p.write_text(json.dumps(v,indent=2)+'\n')
        for filename in ['result.json','failure.json']:
            target=p.parent/filename
            if target.exists():
                q=json.loads(target.read_text());q['sourceSnapshot']=v['sourceSnapshot'];target.write_text(json.dumps(q,indent=2)+'\n')
print(snapshot)
