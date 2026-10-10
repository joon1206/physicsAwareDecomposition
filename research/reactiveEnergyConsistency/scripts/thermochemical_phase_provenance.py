"""Supplemental phase manifest, separate from historical scientific criteria."""
from pathlib import Path
import datetime,json
from thermo_continuity import sha
ROOT=Path(__file__).resolve().parents[1];STUDY=ROOT/'candidateStudy';P=STUDY/'data/processed';RAW=STUDY/'data/raw'

def main():
    matched=json.loads((P/'clean_thermo_campaign.json').read_text())
    gri=json.loads((P/'clean_gri_campaign.json').read_text())
    branch=json.loads((P/'clean_thermo_branch.json').read_text())
    records=[]
    for r in matched+gri:
        case=RAW/r['name'];meta=case/'experiment.json'
        records.append(dict(name=r['name'],reusedLegacy=r['name'].startswith('F_'),status='completed' if (case/'result.json').exists() else 'failed' if (case/'failure.json').exists() else 'incomplete',
          scientificStatus='sourceEnergyGateFailed' if r.get('failedSourceEnergyCalls',0) else 'sourceGatePassed' if 'sourceCalls' in r else 'sourceEndpointNotTraced',
          failedSourceCalls=r.get('failedSourceEnergyCalls'),sourceCalls=r.get('sourceCalls'),sourceGate=r.get('sourceGate'),metadataSHA256=sha(meta),resultSHA256=sha(case/'result.json') if (case/'result.json').exists() else None))
    nativeFailures=[]
    for f in sorted(RAW.glob('CleanReference_Alzueta*/failure.json')):
        nativeFailures.append(dict(name=f.parent.name,status='failed',scientificStatus='mechanismParserFailure',failureSHA256=sha(f),metadataSHA256=sha(f.parent/'experiment.json')))
    retained=[]
    for name in ['CleanThermoIndependent_v1','MechanismContinuity_v1','MechanismContinuity_v2','InvariantProjectionValidData_v1','ThermochemicalAbstractMap_v1']:
        case=RAW/name
        retained.append(dict(name=name,files={p.name:sha(p) for p in sorted(case.iterdir()) if p.is_file()},scope='Current retained artifact hashes. Helper implementation versions not saved at original execution are not retrospectively attested.'))
    inputs={}
    for n in ['clean_thermo_campaign.json','clean_gri_campaign.json','clean_thermo_branch.json','clean_thermo_reference.json','mechanism_continuity_audit.json','invariant_projection_valid_data.json','thermochemical_abstract_map.json','thermochemical_candidate_decision.json','clean_thermo_interactions.json','clean_thermo_report_sources.json','native_thermo_control_limits.json','thermochemical_pivot.json','thermochemical_figure_data.json']:
        inputs[n]=sha(P/n)
    result=dict(generatedUTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),driverSHA256=sha(__file__),nativeMatched=records,directBranchCaseNames=sorted(set(r['name'] for r in branch)),nativeReferenceParserFailures=nativeFailures,otherRetained=retained,processedSHA256=inputs,
      scope='Supplement to historical reproducibility_manifest.json. Historical three-source-failure criterion is unchanged; new continuous-data scientific failures are explicitly classified here. Native snapshots remain in each experiment.json. No publication status is inferred from execution completion.')
    (P/'thermochemical_phase_manifest.json').write_text(json.dumps(result,indent=2)+'\n')
    print('Phase manifest matched',len(records),'native parser failures',len(nativeFailures))
if __name__=='__main__':main()
