"""Archive project-owned v2 native-restart observations before corrected study."""
import hashlib,json,time
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];raw=ROOT/'data/raw';processed=ROOT/'data/processed'
def main():
    target=raw/'nativeRestartProtocolV2';assert not target.exists();target.mkdir()
    names=['histories','oracle','deployment','live','profilesOff','profilesOn','scaling','scalingSources','gamma','fineHistories','fineOracle','conservationRefinement','validation','campaignLogs','finishLogs','refine','endpointRegression']
    moved=[]
    for name in names:
        source=raw/name
        if source.exists():
            assert source.resolve().is_relative_to(raw.resolve());source.rename(target/name);moved.append(name)
    snapshot=target/'processedSnapshot';snapshot.mkdir()
    retained={'previous_claim_audit.json','endpoint_regression.json','restart_regression.json','restart_regression_dpdt_only_rejected.json','restart_regression_restore_solved_he_and_dpdt_v3_rejected.json'}
    for source in processed.glob('*.json'):
        if source.name not in retained:source.rename(snapshot/source.name)
    portable=processed/'nativeRestartProtocolV2';portable.mkdir(exist_ok=True)
    for name in ['model.json','oracle_summary.json','policy_summary.json']:
        p=snapshot/name
        if p.exists():(portable/name).write_bytes(p.read_bytes())
    note=dict(protocol='native restart v2, superseded',directories=moved,
        reason='Forced physical endpoints fixed stale output, but static dpdt and psi oldTime were not preserved. Same-action gates passed; segmented/native regression failed. v3 preserves the actual continuous state.',
        retainedRaw=str(target),newProtocol='physical endpoint + stored h/dpdt + psi oldTime initialization',
        modelsRefittedOnlyOnWholeTrainingConditions=True,hyperparametersUnchanged=True)
    (processed/'protocol_epochs.json').write_text(json.dumps(note,indent=2));(target/'README.json').write_text(json.dumps(note,indent=2))
    print('Archived native-restart epoch without deleting any observations:',moved)
if __name__=='__main__':main()
