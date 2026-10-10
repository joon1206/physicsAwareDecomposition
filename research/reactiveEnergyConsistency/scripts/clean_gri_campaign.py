"""Installed GRI full CFD thermo-only controls with exact ledger and inputs."""
from pathlib import Path
import json,math
from caseFactory import make_case,field,decompose,solve,command,SPECS
from campaign import change
from candidate_mixture_wave import version
from thermo_continuity import repair,properties,number,sha
from thermo_reference import parse_nasa
from analyze import summarize,fields
from candidate_analyze import totals,CELL_TERMS
ROOT=Path(__file__).resolve().parents[1];STUDY=ROOT/'candidateStudy';RAW=STUDY/'data/raw'
def main():
    SPECS['heldoutMoving']['mechanism']='gri';records=[]
    for dt in [2e-6,1e-6]:
     for thermo in ['legacy','CpHS']:
        name=f'CleanGRI_{thermo}_dt{dt:g}';case=RAW/name
        if not (case/'result.json').exists() and not (case/'failure.json').exists():
            if case.exists():raise RuntimeError('Retained incomplete '+str(case))
            make_case(name,'heldoutMoving',nx=32,ny=8,dt=dt,steps=round(240e-6/dt))
            data=case/'chemkin/therm.dat';parent=sha(data)
            if thermo=='CpHS':
                nasa=parse_nasa(data);lines=data.read_text().splitlines()
                for i,line in enumerate(lines):
                    if len(line)<80 or line[79]!='1':continue
                    name0=line[:18].strip().split()[0];spec=repair(nasa[name0],'CpHS')
                    lines[i+1]=number(spec['high'][0])+lines[i+1][15:]
                    lines[i+2]=number(spec['high'][5])+number(spec['high'][6])+lines[i+2][30:]
                data.write_text('\n'.join(lines)+'\n')
            change(case/'system/fvSolution','nCorrectors',1);change(case/'system/fvSolution','nOuterCorrectors',1)
            (case/'system/controlDict').open('a').write('\nenergyLedger true; cellEnergyLedger true; cellLedgerEvery 1; energyCorrection none;\n')
            cfg=dict(name=name,kind='F',mode='none',dt=dt,steps=round(240e-6/dt),ranks=4,nCells=256,nCorrectors=1,nOuterCorrectors=1,**version('reactingEnergyCandidates'),thermoControl=thermo,mechanism='installedGRI',driverSHA256=sha(__file__),kineticsSHA256=sha(case/'chemkin/chem.inp'),thermoSHA256=sha(data),parentThermoSHA256=parent,scope='Full F fields/transport/discretization with installed GRI rates. Thermo-only comparison within GRI pair; different kinetics from old H2. No empirical refit accuracy claim.')
            (case/'experiment.json').write_text(json.dumps(cfg,indent=2)+'\n');decompose(case,4)
            try:
                wall=solve(case,4,exe='reactingEnergyCandidates',timeout=900)
                command(['mpirun','--bind-to','core','--map-by','core','--nooversubscribe','-np','4','padNativeInventory','-parallel','-time','0:'],case,case/'inventory.log')
                (case/'result.json').write_text(json.dumps(dict(cfg,solverWall=wall),indent=2)+'\n')
            except RuntimeError as e:(case/'failure.json').write_text(json.dumps(dict(cfg,error=str(e)),indent=2)+'\n')
        if (case/'failure.json').exists():r=json.loads((case/'failure.json').read_text())
        else:
            r,_,_=summarize(case);local=totals(case);r.update(cellCumulativeTerms={k:math.fsum(x.get(k,0) for x in local) for k in CELL_TERMS},maxCellClosure=max(x['maxCellClosure'] for x in local),maxEOSRelative=max(x['maxEOSRelative'] for x in local),meanTemperature=math.fsum(fields(case,4,240e-6,'T',256))/256)
        records.append(r);print(name,r.get('signedEnergyDrift'),r.get('error'),flush=True)
        (STUDY/'data/processed/clean_gri_campaign.json').write_text(json.dumps(records,indent=2)+'\n')
        if 'error' in r:return
if __name__=='__main__':main()
