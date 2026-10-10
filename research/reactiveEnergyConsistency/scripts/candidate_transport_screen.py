"""Controlled known-physics flux ablation; no change to the parent executables."""
from pathlib import Path
import json, math, sys
from candidate_screen import run
from candidate_analyze import totals
from analyze import summarize,fields
ROOT=Path(__file__).resolve().parents[1];STUDY=ROOT/'candidateStudy'

def main():
    # Initial hypothesis: the periodic flux changes local heat transport, but
    # cannot algebraically cancel the original post-pressure net density defect.
    action=sys.argv[1] if len(sys.argv)>1 else 'zero'
    active=action.startswith('nonzero')
    sync='Sync' in action
    configs=[('F',2e-6,4,None),('F',1e-6,4,None),('Mix',2e-6,4,None),('B',1e-6,1,None)]
    if active:configs=[('F',1e-6,4,None),('F',.5e-6,4,None),('Mix',1e-6,4,None)]
    if action=='nonzeroSync':configs.append(('Mix',1e-6,1,None))
    if action=='nonzeroSyncPilot':configs=[('Mix',1e-6,4,None),('Mix',1e-6,1,None)]
    thermo_control=action in ['nonzeroSyncThermo','nonzeroSyncThermo4']
    thermo_count=4 if action=='nonzeroSyncThermo4' else 2
    if thermo_control:configs=[('Mix',1e-6,4,None),('Mix',1e-6,1,None)]
    records=[]
    for kind,dt,ranks,steps in configs:
        for mode in ['none','conservativeState']:
            for flag in [False,True]:
                case=run(kind=kind,dt=dt,ranks=ranks,steps=steps,mode=mode,every=0,
                         tag='_transport'+('On' if flag else 'Off')+('_nonzeroSutherland' if active else '')+('_coupledSync' if sync else '')+(f'_thermo{thermo_count}' if thermo_control else '')+('_serial' if ranks==1 and kind!='B' else ''),
                         exe='reactingEnergyTransportCandidates',compatible_heat_flux=flag,
                         transport_as=1.458e-6 if active else None,transport_ts=110.4 if active else None,
                         thermo_corrections=thermo_count if thermo_control else None)
                if (case/'failure.json').exists():
                    records.append(json.loads((case/'failure.json').read_text()));continue
                record,_,_=summarize(case);local=totals(case)
                temp=fields(case,ranks,dt*record['steps'],'T',record['nCells'])
                record.update(maxCellClosure=max(x['maxCellClosure'] for x in local),
                              meanTemperature=math.fsum(temp)/len(temp),
                              maxCellGlobalClosure=max(abs(x['closure']) for x in local),
                              maxEOSRelative=max(x['maxEOSRelative'] for x in local),
                              maxMomentumDeltaU=max(x['maxMomentumDeltaU'] for x in local),
                              cumulativeDensityPair=math.fsum(x['DrhoH']+x['DrhoC'] for x in local),
                              cumulativeExtraFluxNetEnergy=math.fsum(x['DextraSensibleTransport'] for x in local),
                              extraFluxSpaceTimeAbsoluteEnergy=math.fsum(x['absExtraSensibleTransport'] for x in local),
                              localInventoryDifference=math.fsum(x['DE'] for x in local)-(record['end']['E_stored']-record['initial']['E_stored']))
                records.append(record)
                print(record['name'],'E',record['signedEnergyDrift'],'Tmean',record['meanTemperature'],
                      'localClosure',record['maxCellClosure'],flush=True)
    filename=('transport_nonzero_sync_thermo4_screen.json' if thermo_count==4 else 'transport_nonzero_sync_thermo_screen.json') if thermo_control else 'transport_nonzero_sync_screen.json' if sync else 'transport_nonzero_screen.json' if active else 'transport_screen.json'
    (STUDY/'data/processed'/filename).write_text(json.dumps(records,indent=2)+'\n')
if __name__=='__main__':main()
