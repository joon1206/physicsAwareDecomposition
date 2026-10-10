"""Portable timing evidence without committing transient CFD field trees."""
import hashlib,json,tarfile
from pathlib import Path
from analysis import ROOT
def main():
    raw=ROOT/'data/raw';out=ROOT/'data/evidence';out.mkdir(parents=True,exist_ok=True)
    folders=['histories','oracle','deployment','live','profilesOff','profilesOn','controllerProfiles','mpiConsequencesOff','mpiConsequencesOn',
        'scaling','scalingSources','gamma','fineOracle','fineHistories','conservationRefinement',
        'conservationDiagnosis','conservationCoupling','liveMeshFollowup','initialState','initialStateLong','fluxDiagnosis','fluxRepair','refine','confirmation','confirmationNegative','continuousOracle',
        'campaignLogs','finishLogs','build','restartRegressionPsi','endpointRegression','repeatedMigration']
    paths=[]
    for name in folders:
        d=raw/name
        if not d.exists():continue
        for p in d.rglob('*'):
            if p.is_file() and (p.name in ['manifest.json','case.json','globalCellIds.json','faceAudit.csv'] or p.parent.name=='partitionIds' or (p.suffix=='.csv' and (p.name.startswith('rank') or p.parent.name in ['mpiProfile','migrationMPI'])) or (p.suffix=='.log' and (name in ['campaignLogs','finishLogs','build','fluxRepair','fluxDiagnosis'] or p.name.startswith('solver')))):paths.append(p)
    paths=sorted(set(paths));records=[]
    with tarfile.open(out/'timing_evidence.tar.gz','w:gz',compresslevel=6) as archive:
        for p in paths:
            records.append(dict(path=str(p.relative_to(ROOT)),bytes=p.stat().st_size,SHA256=hashlib.sha256(p.read_bytes()).hexdigest()))
            archive.add(p,arcname=str(p.relative_to(ROOT)),recursive=False)
    result=dict(files=records,archiveSHA256=hashlib.sha256((out/'timing_evidence.tar.gz').read_bytes()).hexdigest(),archiveBytes=(out/'timing_evidence.tar.gz').stat().st_size,
        rawLocation=str(raw),excludedProtocol='interiorWriteProtocol, nativeRestartProtocolV2, liveCyclicUtilityRejected, liveBeforeSegmentRetention and liveRetentionRace; rejected epochs and incomplete attempts excluded from headline evidence',scope='Full cost manifests, rank clocks, IDs, solver logs and campaign/build logs. CFD field trees remain retained locally and regenerable from scripts.')
    (out/'manifest.json').write_text(json.dumps(result,indent=2))
    (out/'README.md').write_text('# Compact raw timing evidence\n\n`timing_evidence.tar.gz` preserves cost manifests, rank timing CSVs, canonical cell IDs, solver logs and campaign/build logs. `manifest.json` records every member hash and archive hash. Full transient fields are retained at `'+str(raw)+'` and ignored by Git. State-preserving physical-endpoint experiments are used. Rejected interior-write/native-restart epochs, the original repeated-cyclic utility failure, partial runs before segment retention, and the stopped archive-overlap attempt remain locally preserved and are excluded. The final randomized live collection uses finalized code and retains every segment. Source checksums and build environment are in `docs/`.\n')
    print('ARCHIVED',len(paths),'files;',result['archiveBytes'],'bytes')
    from splitTimingEvidence import main as split
    split()
    readme=out/'README.md'
    readme.write_text(readme.read_text()+'\nThe repository stores the archive as lossless `timing_evidence.tar.gz.partNNN` volumes with checksums in `parts.json`. From `research/physicsAwareDecomposition`, run `bash actionStudy/scripts/run.sh assembleTimingEvidence.py` to verify and reconstruct it. The assembled archive is ignored by Git.\n')
if __name__=='__main__':main()
