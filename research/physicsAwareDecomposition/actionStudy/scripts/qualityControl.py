"""Fail final QA on missing evidence, stale plots, mixed protocols or gates."""
import hashlib,json,math,re,statistics,tarfile
from analysis import ROOT,TRAIN,VALID,TEST,ACTIONS
from caseFactory import assert_endpoint,latest_time
from pathlib import Path
def read(name):return json.loads((ROOT/f'data/processed/{name}.json').read_text())
def main():
    checks=[]
    def check(name,condition):
        checks.append(dict(check=name,passed=bool(condition)))
        if not condition:raise AssertionError(name)
    raw=read('oracle_raw');states=read('oracle_summary');gates=read('oracle_validation');model=read('model')
    check('complete four-action oracle: 25 states, 500 trials',len(raw)==500 and len(states)==25)
    check('main gates include every nonbaseline repeat at actual endpoints',len(gates)==375 and all(g['pass_'] and not g['omittedOptionalFields'] for g in gates))
    for row in raw:
        check('state-preserving protocol '+row['relativeDirectory'],row['writeProtocol'].startswith('state-preserving physical endpoint v3'))
        expected=row['solverWall']+row['decisionWall']+row['migrationWall']
        check('complete cost accounting '+row['relativeDirectory'],abs(expected-row['totalWall'])<1e-8)
        if row['action'] in ['AM','AH']:check('required weight acquisition charged '+row['relativeDirectory'],row.get('weightAcquisitionCharged',False))
        assert_endpoint(ROOT/row['relativeDirectory'],row['ranks'])
    check('whole-condition disjoint split',not(set(TRAIN)&set(VALID) or set(TRAIN)&set(TEST) or set(VALID)&set(TEST)))
    check('model training cases exclude test',model['trainingCases']==TRAIN and model['testCases']==TEST)
    model_sha=hashlib.sha256((ROOT/'data/processed/model.json').read_bytes()).hexdigest()
    accounting=read('replay_accounting');check('replay correction preserves frozen coefficients',accounting['modelRefit'] is False and accounting['modelSHA256']==model_sha)
    state_lookup={(s['regime'],s['checkpoint'],s['H']):s for s in states}
    for row in read('policy_decisions'):
        state=state_lookup[row['regime'],row['checkpoint'],row['H']]
        expected=state['actions'][row['chosen']]['total']['median']+row['featureWall']+row['inferenceWall']
        check('replay action and incremental decision costs agree '+row['policy'],abs(expected-row['cost'])<1e-10)
        if row['sharedWeightAcquisition']:check('mesh acquisition reused exactly once '+row['policy'],row['chosen'] in ['AM','AH'] and row['featureWall']==0)
    for name,n in [('deployment_raw',120),('live',135)]:
        rows=read(name);check(name+' complete trial count',len(rows)==n)
        check(name+' frozen model fingerprint',all(r['modelSHA256']==model_sha for r in rows))
        if name=='deployment_raw':check(name+' numerical gates',all(r.get('gate',{'pass_':True})['pass_'] for r in rows))
        else:
            rejected=[r for r in rows if not r.get('gate',{'pass_':True})['pass_']]
            check('live non-mesh algorithms preserve predefined field gates',all(r['policy']=='AM' for r in rejected))
            followup=read('live_mesh_followup')
            check('rejected mesh endpoints investigated without trial or threshold changes',len(followup['controls'])==3*len(rejected) and set(followup['rejectedTrials'])=={r['path'] for r in rejected} and followup['originalTrialsChanged'] is False and followup['gateThresholdChanged'] is False)
    for row in read('live'):
        check('live physical endpoint '+row['path'],abs(float(latest_time(ROOT/row['path'],True))-.00028)<1e-12)
        check('actual live wall includes orchestration '+row['path'],row['totalWall']>=row['componentWall']-1e-8 and row['orchestratorOtherWall']>=-1e-8)
        if any(e['action'] in ['AM','AH'] for e in row['events']):check('live repeated mesh uses fixed native validation '+row['path'],row.get('migrationUtility')=='redistributeParPAD')
    check('baseline and restart regressions',all(r['pass_'] for r in read('baseline_validation').values()) and all(g['pass_'] for g in read('restart_regression')))
    repeated=read('repeated_migration_validation');check('native/private repeated cyclic migration regression',len(repeated)==5 and all(g['pass_'] for g in repeated))
    physical=read('physical_field_audit');check('finite fields and admissible endpoint thermodynamic state',physical['passed'] and len(physical['cases'])>=1000)
    for name,n in [('profiles',48),('scaling',60),('gamma',30),('fine_oracle_raw',40)]:check(name+' counts',len(read(name))==n)
    for name in ['scaling_validation','fine_oracle_validation']:check(name+' gates',all(r['pass_'] for r in read(name)))
    cross_rank=read('scaling_crossrank_validation');check('strong-scaling trajectories agree across rank counts',len(cross_rank)==3 and all(g['pass_'] for g in cross_rank))
    for name in ['profiles','gamma']:check(name+' gates',all(r.get('gate',{'pass_':True})['pass_'] for r in read(name)))
    controller_profiles=read('controller_profiles');check('representative controller profiles',len(controller_profiles)==12 and all(r['gate']['pass_'] for r in controller_profiles))
    mpi_profiles=read('mpi_consequence_profiles');check('held-out communication consequence profiles',len(mpi_profiles)==24 and all(r.get('gate',{'pass_':True})['pass_'] for r in mpi_profiles))
    mpi_model=read('consequence_models')['MPIModel'];check('MPI model retains genuinely held-out condition',mpi_model['metrics']['test']['conditions']==['heldoutMoving'] and mpi_model['metrics']['test']['n']==6)
    check('follow-up physical accuracy diagnosis',len(read('conservation_diagnosis'))==7)
    check('matched time and pressure conservation controls',len(read('conservation_coupling_followup'))==2)
    initialization=read('initial_state_diagnosis')
    check('initial Euler coefficient diagnosis without altering performance data',len(initialization['records'])==4 and initialization['initialMassConservationPassed'] and initialization['originalInitializationShowsOffset'] and initialization['performanceDataChanged'] is False)
    long_initialization=read('initial_state_long')
    check('initial mass fix survives the complete physical history',len(long_initialization['records'])==2 and all(abs(r['relativeMassDrift'])<1e-9 for r in long_initialization['records']) and long_initialization['performanceDataChanged'] is False)
    check('stored flux and reconstructed flux independently audited',len(read('flux_diagnosis')['records'])==3)
    flux_repair=read('flux_repair')
    check('fixed observed partitions and preserved face flux',len(flux_repair['records'])==6 and all(r['exactObservedOwnership'] and r['gate']['pass_'] and r['fluxDivergenceLinf']<1e-6 for r in flux_repair['records']))
    check('original zero-flux endpoint repaired in independent controls',len(flux_repair['observedZeroRepairs'])==3 and all(r['gate']['pass_'] and r['fluxDivergenceLinf']<1e-6 for r in flux_repair['observedZeroRepairs']) and flux_repair['originalTrialsChanged'] is False and flux_repair['gateThresholdChanged'] is False)
    check('mapped error localized to eight zero cyclic copies',flux_repair['originalFaceAudit'][0]['mismatches']==8 and flux_repair['originalFaceAudit'][0]['reversed']==0 and all(r['candidate']==0 and r['type']=='processorCyclic' for r in flux_repair['originalFaceAudit'][0]['examples']))
    continuous_gates=read('continuous_oracle_validation');check('oracle versus actual uninterrupted trajectories',len(continuous_gates)==12 and all(g['pass_'] for g in continuous_gates))
    for name in ['confirmation','confirmation_negative']:check(name+' independent replication',len(read(name)['rows'])==40 and all(r['pass_'] for r in read(name)['gates']))
    q=read('quicklb');check('third-party library four modes, pilots and three repeats',len(q)==16 and {r['algorithm'] for r in q}=={'NONE','GREEDY','SORT','SORT2'})
    check('QUICKLB field equivalence',read('quicklb_validation')['passed'])
    reproduction=json.loads((ROOT/'docs/reproduction_test.json').read_text())
    check('documented small profile exercised in a fresh output tree',reproduction['passed'] and reproduction['trials']==8 and reproduction['gates']==6)
    warnings=json.loads((ROOT/'docs/build_warnings.json').read_text())
    check('clean project builds and classified upstream warnings',warnings['projectWarningsPassed'] and all(r.get('explanation') for r in warnings['upstreamQuicklbWarnings']))
    figures=json.loads((ROOT/'figures/index.json').read_text());check('at least 25 scientific figures',len(figures)>=25)
    for figure in figures:
        for ext in ['png','pdf','svg','source.json']:check('figure export '+figure['name']+'.'+ext,(ROOT/'figures'/(figure['name']+'.'+ext)).stat().st_size>100)
        json.loads((ROOT/'figures'/figure['source']).read_text())
    figure_reproduction=json.loads((ROOT/'docs/figure_reproduction.json').read_text())
    check('all scientific exports regenerate byte-identically on the pinned host',figure_reproduction['passed'] and len(figure_reproduction['files'])==len(figures)*4)
    for path,sha in figure_reproduction['files'].items():
        check('regenerated figure fingerprint '+path,hashlib.sha256((ROOT/'figures'/path).read_bytes()).hexdigest()==sha)
    head=read('headline');best=head['best'];state=next(s for s in states if s['regime']==best['regime'] and s['checkpoint']==best['checkpoint'] and s['H']==best['H'])
    check('headline regenerated from measured medians',abs(best['speedup']-state['actions'][best['action']]['speedup'])<1e-12)
    live_rows=read('live')
    for row in read('live_summary'):
        relevant=[r for r in live_rows if r['regime']==row['regime'] and r['policy']==row['policy']]
        check('live claim eligibility matches every original field gate '+row['regime']+' '+row['policy'],row['valid']==all(r.get('gate',{'pass_':True})['pass_'] for r in relevant))
    aggregate=read('live_aggregate')
    rejected_test=[r for r in live_rows if r['regime'] in TEST and r['policy']=='AM' and not r['gate']['pass_']]
    check('mesh aggregate eligibility follows every original field gate',aggregate['AM']['valid']==(not rejected_test) and (not rejected_test or 'descriptive' in aggregate['AM']['ratioInterpretation']))
    check('controller and strong baseline are numerically eligible',aggregate['controller']['valid'] and aggregate['ACContinuous']['valid'])
    report=(ROOT/'docs/final_report.md').read_text()
    for section in ['Abstract','Related work','Oracle action experiment','Runtime controller','Numerical verification','Scaling results','Generalization','Ablation studies','Novelty assessment','Threats to validity','Reproducibility','Publication assessment']:
        check('report includes '+section,section.lower() in report.lower())
    check('physical budgets are reported separately from algorithmic equivalence','physical accuracy' in report.lower() and 'energy' in report.lower())
    documents=[ROOT/'README.md',ROOT/'figures/README.md',ROOT/'tables/summary.md']+list((ROOT/'docs').glob('*.md'))
    for document in documents:
        for target in re.findall(r'\]\(([^)]+)\)',document.read_text()):
            if re.match(r'^[a-z]+:',target,re.I) or target.startswith('#'):continue
            path=target.split('#',1)[0].strip('<>')
            check('local documentation target '+str(document.relative_to(ROOT))+' '+path,(document.parent/path).exists())
    evidence=json.loads((ROOT/'data/evidence/manifest.json').read_text())
    from assembleTimingEvidence import assemble
    archive=assemble()
    volumes=json.loads((ROOT/'data/evidence/parts.json').read_text())
    check('transport archive fingerprint matches scientific manifest',volumes['archiveSHA256']==evidence['archiveSHA256'])
    for part in volumes['parts']:
        content=(ROOT/'data/evidence'/part['path']).read_bytes()
        check('transport volume '+part['path'],len(content)==part['bytes'] and hashlib.sha256(content).hexdigest()==part['SHA256'])
    check('compact timing archive SHA256',hashlib.sha256(archive.read_bytes()).hexdigest()==evidence['archiveSHA256'])
    members={r['path']:r for r in evidence['files']};seen=set()
    with tarfile.open(archive,'r|gz') as stream:
        for member in stream:
            check('evidence member listed '+member.name,member.isfile() and member.name in members)
            record=members[member.name];content=stream.extractfile(member).read()
            check('evidence member bytes and fingerprint '+member.name,len(content)==record['bytes'] and hashlib.sha256(content).hexdigest()==record['SHA256'])
            seen.add(member.name)
    check('compact evidence inventory complete',seen==set(members))
    result=dict(passed=True,checks=checks,figureCount=len(figures),oracleTrials=len(raw),scope='Artifacts and numerical equivalence; this QA does not claim physically converged flames or population-level statistical validity.')
    (ROOT/'data/processed/quality_control.json').write_text(json.dumps(result,indent=2))
    print('PASSED final artifact QA',len(checks),'checks;',len(figures),'figures;',len(raw),'oracle trials')
if __name__=='__main__':main()
