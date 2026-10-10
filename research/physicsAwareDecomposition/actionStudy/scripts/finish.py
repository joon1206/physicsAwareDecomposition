"""Finish all feasible local experiments after the state-preserving campaign.

A successful phase is resumable. Failures stop this driver and remain visible;
they are diagnosed before explicitly rerunning the affected phase.
"""
import argparse,json,os,subprocess,time
from pathlib import Path
SCRIPTS=Path(__file__).resolve().parent
ROOT=Path(os.environ.get('PAD_ACTION_ROOT',SCRIPTS.parent))
def main():
    parser=argparse.ArgumentParser();parser.add_argument('--from-phase');parser.add_argument('--no-wait',action='store_true');args=parser.parse_args()
    ledger=ROOT/'data/processed/finish_status.json';logs=ROOT/'data/raw/finishLogs';logs.mkdir(parents=True,exist_ok=True)
    if not args.no_wait:
        while True:
            p=ROOT/'data/processed/campaign_status.json'
            status=json.loads(p.read_text()) if p.exists() else []
            if status and status[-1]['phase']=='refinement':
                failures=[r for r in status if r['exitCode'] and r['phase']!='live']
                if failures:raise RuntimeError('Repair failed primary phases before finish: '+repr(failures))
                break
            time.sleep(15)
    phases=[('live',['run.sh','controller.py','live']),('cleanBuild',['cleanBuild.sh']),
        ('confirmation',['run.sh','confirmChemistry.py']),('continuousOracle',['run.sh','validateContinuousOracle.py']),('controllerProfiles',['run.sh','profileController.py']),('mpiConsequences',['run.sh','mpiConsequenceStudy.py']),('conservationDiagnosis',['run.sh','conservationDiagnosis.py']),('replayAccounting',['run.sh','recomputeReplay.py']),('consequences',['run.sh','consequenceModels.py']),
        ('actionInventories',['run.sh','actionInventories.py']),('physicalFields',['run.sh','physicalFieldAudit.py']),('quicklb',['reproduceQuicklb.sh']),
        ('quicklbProcess',['processQuicklb.sh']),('initialState',['run.sh','initialStateDiagnosis.py']),('initialStateLong',['run.sh','initialStateLong.py']),('fluxRepair',['run.sh','fluxRepair.py']),('physicalFieldsFinal',['run.sh','physicalFieldAudit.py']),('reproduction',['run.sh','testReproduction.py']),('literature',['run.sh','writeLiterature.py']),
        ('primaryDocuments',['run.sh','literatureFollowup.py']),('bibliography',['run.sh','verifyBibliography.py']),('literatureVerified',['run.sh','writeLiterature.py']),
        ('warnings',['run.sh','auditWarnings.py']),('provenance',['run.sh','captureProvenance.py']),('figures',['generateFigures.sh']),('figureReproduction',['run.sh','verifyFigureReproduction.py']),
        ('report',['run.sh','writeReport.py']),('answers',['run.sh','writeAnswers.py']),
        ('evidence',['run.sh','archiveEvidence.py']),('quality',['run.sh','qualityControl.py'])]
    previous=json.loads(ledger.read_text()) if ledger.exists() else []
    done={r['phase'] for r in previous if r['exitCode']==0};force=args.from_phase is not None
    if force:
        names=[p[0] for p in phases]
        if args.from_phase not in names:raise ValueError(args.from_phase)
        phases=phases[names.index(args.from_phase):]
    for name,argv in phases:
        if not force and name in done:continue
        start=time.perf_counter();print('START FINISH',name,flush=True)
        with (logs/(name+'.log')).open('w') as stream:
            result=subprocess.run(['bash',str(SCRIPTS/argv[0])]+argv[1:],stdout=stream,stderr=subprocess.STDOUT)
        row=dict(phase=name,exitCode=result.returncode,wall=time.perf_counter()-start)
        previous=[r for r in previous if r['phase']!=name]+[row];ledger.write_text(json.dumps(previous,indent=2))
        print('FINISHED',row,flush=True)
        if result.returncode:
            print('\n'.join((logs/(name+'.log')).read_text().splitlines()[-25:]),flush=True)
            raise SystemExit(result.returncode)
    print('All local completion phases passed.',flush=True)
if __name__=='__main__':main()
