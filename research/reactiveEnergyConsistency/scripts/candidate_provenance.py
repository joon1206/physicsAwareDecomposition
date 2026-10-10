"""Current reproducibility manifest; native per-run hashes remain authoritative."""
from pathlib import Path
import datetime, hashlib, json, subprocess, shutil
ROOT=Path(__file__).resolve().parents[1]; REPO=ROOT.parents[1]; STUDY=ROOT/'candidateStudy'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def git(*args):return subprocess.check_output(['git',*args],cwd=REPO,text=True).strip()
def main():
    records=[]
    cv=json.loads((STUDY/'data/processed/cv_chemistry.json').read_text())
    superseded={r['name'] for r in cv['superseded']}
    superseded.add('F_none_dt2e-06_s1_g0_o1_p1_cvSource_rtol1e-10')
    audit=json.loads((STUDY/'data/processed/cv_source_invariant_audit.json').read_text())
    source_failures={r['name'] for r in audit['records'] if r['failingSourceCalls']}
    names=['experiment.json','wave_experiment.json','central_experiment.json']
    for case in sorted((STUDY/'data/raw').iterdir()):
        if not case.is_dir():continue
        metas=[case/n for n in names if (case/n).exists()]
        if not metas:continue
        if len(metas)!=1:raise RuntimeError('Ambiguous metadata '+str(case))
        cfg=json.loads(metas[0].read_text());snapshot=ROOT/cfg['sourceSnapshot']
        for filename,expected in cfg['source'].items():
            if sha(snapshot/filename)!=expected:raise RuntimeError('Changed source snapshot '+str(snapshot/filename))
        extension={}
        if 'chemistrySourceSnapshot' in cfg:
            chemistry_snapshot=ROOT/cfg['chemistrySourceSnapshot']
            for filename,expected in cfg['chemistrySource'].items():
                if sha(chemistry_snapshot/filename)!=expected:raise RuntimeError('Changed chemistry snapshot '+str(chemistry_snapshot/filename))
            extension=dict(chemistrySourceSnapshot=cfg['chemistrySourceSnapshot'],chemistryLibrarySHA256=cfg['chemistryLibrarySHA256'])
        files={}
        for folder in ['0','constant','system','chemkin']:
            for p in sorted((case/folder).rglob('*')):
                if p.is_file():files[str(p.relative_to(case))]=sha(p)
        status='failed' if (case/'failure.json').exists() else 'completed' if any((case/n).exists() for n in ['result.json','wave_result.json','central_result.json','probe_result.json']) else 'incomplete'
        records.append(dict(name=case.name,status=status,
                            scientificStatus='superseded' if case.name in superseded else 'sourceEnergyGateFailed' if case.name in source_failures else 'notDeterminedByExecutionStatus',
                            metadataSHA256=sha(metas[0]),sourceSnapshot=cfg['sourceSnapshot'],executableSHA256=cfg['executableSHA256'],inputFiles=files,**extension))
    analytical=[]
    for name,metadata,result,declared in [
        ('ThermalTaylor_analytic','taylor_experiment.json','taylor_result.json',{'thermal_path_taylor.py':'scriptSHA256'}),
        ('ThermalTaylor_limiterWeakFeedback','taylor_experiment.json','taylor_result.json',{'thermal_path_limiter.py':'scriptSHA256','thermal_path_taylor.py':'sourceMapSHA256'}),
        ('ElementInvariant_analytic','invariant_experiment.json','invariant_result.json',{'element_invariant_screen.py':'scriptSHA256'}),
        ('ThermoBranchInversion_analytic','inversion_experiment.json','inversion_result.json',{'thermo_branch_inversion.py':'scriptSHA256'}),
        ('CombinedDefect_analytic','controller_experiment.json','controller_result.json',{'combined_defect_counterexample.py':'scriptSHA256'})]:
        case=STUDY/'data/raw'/name;cfg=json.loads((case/metadata).read_text());sources={}
        for filename,key in declared.items():
            if sha(ROOT/'scripts'/filename)!=cfg[key]:raise RuntimeError('Changed declared analytic source '+filename)
            sources[filename]=cfg[key]
        digest=hashlib.sha256(json.dumps(sources,sort_keys=True).encode()).hexdigest()
        snapshot=STUDY/'analyticalSnapshots'/digest;snapshot.mkdir(parents=True,exist_ok=True)
        for filename,expected in sources.items():
            if not (snapshot/filename).exists():shutil.copy2(ROOT/'scripts'/filename,snapshot/filename)
            if sha(snapshot/filename)!=expected:raise RuntimeError('Changed analytic snapshot '+filename)
        analytical.append(dict(name=name,metadataSHA256=sha(case/metadata),resultSHA256=sha(case/result),declaredScriptSnapshot=str(snapshot.relative_to(ROOT)),source=sources,
                               scope='Snapshot matches the explicit source hashes saved at execution. Imported helper versions not declared then are not retrospectively attested.'))
    independent=[]
    for reference in sorted((STUDY/'data/raw').glob('*/reference_summary.json')):
        independent.append(dict(name=reference.parent.name,summarySHA256=sha(reference),
                                retainedFiles={str(p.relative_to(reference.parent)):sha(p) for p in reference.parent.iterdir() if p.is_file()}))
    code={str(p.relative_to(ROOT)):sha(p) for p in sorted((ROOT/'scripts').glob('*')) if p.is_file()}
    apps={}
    for app in sorted((ROOT/'applications').iterdir()):
        if not app.is_dir():continue
        for p in sorted(app.iterdir()):
            if p.is_file() and p.suffix in ['.C','.H']:apps[str(p.relative_to(ROOT))]=sha(p)
        for name in ['files','options']:
            p=app/'Make'/name
            if p.exists():apps[str(p.relative_to(ROOT))]=sha(p)
    libraries={}
    for source_dir in sorted((ROOT/'src').iterdir()) if (ROOT/'src').exists() else []:
        if not source_dir.is_dir():continue
        for p in sorted(source_dir.iterdir()):
            if p.is_file() and p.suffix in ['.C','.H']:libraries[str(p.relative_to(ROOT))]=sha(p)
        for name in ['files','options']:
            p=source_dir/'Make'/name
            if p.exists():libraries[str(p.relative_to(ROOT))]=sha(p)
    payload=dict(generatedUTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),gitHEAD=git('rev-parse','HEAD'),gitBranch=git('branch','--show-current'),
                 scope='Hashes of current input files and orchestration scripts for reproduction. These are not retrospective attestations that every helper was unchanged at execution. Immutable per-run native source snapshots and executable hashes identify the numerical implementation; raw logs and dictionaries remain retained.',
                 currentScripts=code,currentApplicationSource=apps,currentLibrarySource=libraries,experiments=records,
                 analyticalExperiments=analytical,independentReferences=independent,
                 statusCounts={s:sum(r['status']==s for r in records) for s in ['completed','failed','incomplete']})
    path=STUDY/'data/processed/reproducibility_manifest.json';path.write_text(json.dumps(payload,indent=2)+'\n')
    print('Manifest:',len(records),'experiments,',payload['statusCounts'])
if __name__=='__main__':main()
