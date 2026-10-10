"""Small scoped administrative reads without Windows shell quoting."""
import sys,json
from pathlib import Path
PAD=Path(__file__).resolve().parents[2];ROOT=PAD/'actionStudy'
if sys.argv[1]=='request':
    text=Path('/mnt/c/Users/joon1/.codex/attachments/a3c23ed1-34a5-4cc1-9acd-06fc04fbccca/Pasted text.txt').read_text()
    if len(sys.argv)>2:text=text.split('# '+sys.argv[2]+'.')[1].split('# '+sys.argv[3]+'.')[0]
    print(text)
elif sys.argv[1]=='fixMetadata':
    p=ROOT/'scripts/writeLiterature.py';s=p.read_text().replace("'Sukanta Mondal','Russell Whitesides'","'Sudeepta Mondal','Russell A. Whitesides'")
    s=s.replace("'Dynamic Task Scheduling to Mitigate System Interference for Parallel Applications',['Sandia research authors']","'Dynamic Task Scheduling to Mitigate System Performance Variability',['Galen Shipman','Patrick McCormick','Kevin Pedretti','Stephen Lecler Olivier','Kurt Brian Ferreira','Jacqueline H. Chen','Ramanan Sankaran','Sean Treichler','Alex Aiken','Michael Bauer']")
    s=s.replace('final publication author metadata not resolved.','title and ten authors verified against primary OSTI record 1249032.')
    p.write_text(s)
    for n in ['environment_manifest.json','source_manifest.json']:
        p=ROOT/'docs'/n
        if p.exists() and not p.with_stem(p.stem+'_v2_execution').exists():p.with_stem(p.stem+'_v2_execution').write_bytes(p.read_bytes())
    print('Corrected verified metadata and preserved v2 execution manifests.')
elif sys.argv[1]=='summary':
    for name in sys.argv[2:]:
        p=ROOT/f'data/processed/{name}.json';data=json.loads(p.read_text());print(name,json.dumps(data,indent=2)[:20000])
elif sys.argv[1]=='numbers':
    from collections import defaultdict
    for name in sys.argv[2:]:
        p=ROOT/f'data/processed/{name}.json';data=json.loads(p.read_text());print(name,'rows',len(data))
        if name in ['inventories','conservation_refinement']:
            grouped=defaultdict(list)
            for r in data:grouped[(r['regime'],r.get('dt',2e-6))].append(r)
            for key,rows in grouped.items():
                end=max(rows,key=lambda r:r['time']);print(key,'mass',end['relativeMassDrift'],'energy',end['relativeEnergyDrift'])
        elif name=='oracle_summary':
            for r in data:print(r['regime'],r['checkpoint'],r['H'],r['winner'],r['actions']['AC']['speedup'])
elif sys.argv[1]=='archiveEndpoint':
    source=ROOT/'data/raw/endpointRegression';target=ROOT/'data/raw/nativeRestartProtocolV2/endpointRegression'
    assert source.resolve().is_relative_to((ROOT/'data/raw').resolve()) and not target.exists();source.rename(target)
    p=ROOT/'data/processed/endpoint_regression.json';p.rename(ROOT/'data/raw/nativeRestartProtocolV2/processedSnapshot/endpoint_regression.json')
    print('Archived old endpoint regression; corrected smoke will regenerate it.')
elif sys.argv[1]=='bibliography':
    records=json.loads((ROOT/'docs/literature.json').read_text());metadata=json.loads((ROOT/'docs/bibliography_metadata_verification.json').read_text())
    for r in metadata:
        if (r.get('titleSimilarity',1)<.9 or r['status']=='Metadata access failed'):
            print(json.dumps(r,ensure_ascii=False));print(next(x for x in records if x['id']==r['id']))
elif sys.argv[1]=='bibliographyDates':
    records=json.loads((ROOT/'docs/literature.json').read_text());metadata=json.loads((ROOT/'docs/bibliography_metadata_verification.json').read_text())
    for r in metadata:
        if r['id'] in ['drama2000','rlchem2026','retfalvi2026','fluent_docs']:
            print(json.dumps(r,ensure_ascii=False));print(next(x for x in records if x['id']==r['id']))
elif sys.argv[1]=='syntax':
    import ast
    paths=list((ROOT/'scripts').glob('*.py'))
    for path in paths:ast.parse(path.read_text(),filename=str(path))
    print('Parsed',len(paths),'Python scripts without syntax errors.')
elif sys.argv[1]=='warnings':
    import re
    for p in (ROOT/'data/raw/build').glob('*.log'):
        lines=[line for line in p.read_text(errors='replace').splitlines() if re.search(r'\b(?:warning|error):',line,re.I)]
        if lines:print(p.name,'\n'.join(lines[:12]))
elif sys.argv[1]=='preserveV3':
    for name in ['environment_manifest.json','source_manifest.json']:
        source=ROOT/'docs'/name;target=source.with_stem(source.stem+'_v3_execution')
        if not target.exists():target.write_bytes(source.read_bytes())
    print('Preserved final-protocol execution fingerprints before final artifact capture.')
elif sys.argv[1]=='redistributionFlux':
    import re
    for p in (PAD/'applications/redistributeParPAD').glob('*'):
        if p.suffix not in ['.C','.H']:continue
        lines=p.read_text().splitlines()
        for i,line in enumerate(lines):
            if re.search(r'isFlux|oriented|flipFlux|correctFlux|phi',line,re.I):
                print(p.name,i+1,'\n'.join(lines[max(0,i-2):min(len(lines),i+3)]))
elif sys.argv[1]=='failedGates':
    for name in sys.argv[2:]:
        data=json.loads((ROOT/f'data/processed/{name}.json').read_text())
        for row in data:
            gate=row.get('gate',row)
            if 'pass_' in gate and not gate['pass_']:
                print('FAILED',name,{k:row.get(k) for k in ['regime','policy','repeat','path','action','checkpoint']})
                print(json.dumps({k:v for k,v in gate.items() if k!='fields'},indent=2))
                for k,v in gate.get('fields',{}).items():
                    if not v.get('pass_',True):print(k,v)
elif sys.argv[1]=='liveNumbers':
    import statistics
    data=json.loads((ROOT/'data/processed/live.json').read_text())
    print('live trials',len(data),'gates',sum('gate' in r for r in data),'failed',sum(not r['gate']['pass_'] for r in data if 'gate' in r))
    conditions=['heldoutMoving','heldoutIgnition','heldoutPersistent']
    policies=sorted({r['policy'] for r in data})
    totals={p:sum(statistics.median(r['totalWall'] for r in data if r['regime']==c and r['policy']==p) for c in conditions) for p in policies}
    for p,t in totals.items():print(p,'sum of held-out medians',t,'native/policy',totals['nativeContinuous']/t)
elif sys.argv[1]=='finishStatus':
    p=ROOT/'data/processed/finish_status.json'
    print('Finished phases:',p.read_text() if p.exists() else 'none')
    for name in ['live','confirmation','confirmationNegative','controllerProfiles','mpiConsequencesOn','mpiConsequencesOff','conservationDiagnosis']:
        folder=ROOT/'data/raw'/name
        print(name,'complete manifests',sum(1 for _ in folder.glob('**/manifest.json')) if folder.exists() else 0)
    logs=ROOT/'data/raw/finishLogs'
    if logs.exists():
        latest=max(logs.glob('*.log'),key=lambda p:p.stat().st_mtime)
        print('Current log:',latest.name,'\n'+'\n'.join(latest.read_text(errors='replace').splitlines()[-5:]))
elif sys.argv[1]=='results':
    from collections import Counter
    for name in ['oracle_summary','oracle_validation','policy_summary','live_aggregate','confirmation','confirmation_negative','fine_oracle_summary','conservation_diagnosis','live_mesh_followup','quality_control']:
        p=ROOT/f'data/processed/{name}.json'
        if not p.exists():continue
        data=json.loads(p.read_text())
        if name=='oracle_summary':print(name,'states',len(data),'winners',dict(Counter(r['winner'] for r in data)))
        elif name=='oracle_validation':print(name,'gates',len(data),'failed',sum(not g['pass_'] for g in data),'max T Linf',max(g['fields']['T']['Linf'] for g in data))
        elif name=='policy_summary':
            for key,row in data['test'].items():print('heldout replay',key,'speedup',row['aggregateSpeedup'],'mean regret',row['meanRegret'])
        elif name=='live_aggregate':
            for key,row in data.items():print('heldout live',key,row['speedup'],row['CI'])
        elif name.startswith('confirmation'):
            print(name,'speedup',data['speedup'],'CI',data['CI'],'medians',data['baseline']['median'],data['method']['median'])
        elif name=='live_mesh_followup':
            for row in data['controls']:print('live mesh control',row['label'],'T Linf',row['gate']['fields']['T']['Linf'],'passed',row['gate']['pass_'])
        elif name=='fine_oracle_summary':
            for row in data:print('fine action',row['regime'],row['action'],row['speedup'],row['valid'])
        elif name=='conservation_diagnosis':
            for row in data:print('accuracy diagnosis',row['nx'],row['dt'],row['nCorrectors'],row.get('nOuterCorrectors',1),'mass',row['relativeMassDrift'],'energy',row['relativeEnergyDrift'],'Tmax',row['Tmax'])
        else:print('final QA',data['passed'],'checks',len(data['checks']))
elif sys.argv[1]=='budgetTerms':
    from collections import defaultdict
    for name in sys.argv[2:]:
        path=ROOT/f'data/processed/{name}.json'
        if not path.exists():continue
        rows=json.loads(path.read_text());groups=defaultdict(list)
        for row in rows:groups[(row.get('regime','heldoutMoving'),row.get('dt',2e-6),row.get('nx',32),row.get('nCorrectors',1))].append(row)
        for key,group in groups.items():
            if name=='conservation_diagnosis':initial,end=group[0]['initial'],group[0]['end']
            else:initial,end=min(group,key=lambda r:r['time']),max(group,key=lambda r:r['time'])
            fields=['mass','massEOS','totalEnergy','energyEOS','chemicalEnergy','sensibleEnthalpy','kineticEnergy','pressureVolume']
            print(key,'INITIAL',{k:initial.get(k) for k in fields},'END',{k:end.get(k) for k in fields})
