"""Modern-mechanism native energy audit, distinct from H2 thermo attribution."""
from pathlib import Path
import json,shutil,math
from caseFactory import make_case,field,decompose,solve,command
from campaign import change
from candidate_mixture_wave import version
from thermo_continuity import sha
from thermo_reference import ATOMIC
from analyze import summarize,fields
from candidate_analyze import totals,CELL_TERMS
ROOT=Path(__file__).resolve().parents[1];STUDY=ROOT/'candidateStudy';RAW=STUDY/'data/raw';INPUT=STUDY/'thermoControls/AlzuetaExport_v5'
def main():
    ATOMIC['HE']=4.00260;records=[]
    # Four matched full-flow runs, native source settings, same F fields/grid/transport.
    for dt in [2e-6,1e-6]:
     for thermo in ['legacy','CpHS']:
        name=f'CleanReference_Alzueta_{thermo}_dt{dt:g}_syntax5';case=RAW/name
        if not (case/'result.json').exists() and not (case/'failure.json').exists():
            if case.exists():raise RuntimeError('Retained incomplete '+str(case))
            make_case(name,'heldoutMoving',nx=32,ny=8,dt=dt,steps=round(240e-6/dt))
            shutil.copy2(INPUT/'chem.inp',case/'chemkin/chem.inp');shutil.copy2(INPUT/f'{thermo}.dat',case/'chemkin/therm.dat')
            from thermo_reference import parse_nasa
            species=list(parse_nasa(case/'chemkin/therm.dat'))
            for s in species:field(case/'0'/s,dict(H2=.0283,O2=.225,N2=.7467).get(s,0))
            info=json.loads((case/'case.json').read_text());info.update(species=species,mechanism='Alzueta2023_baseline',mechanismSHA256=sha(case/'chemkin/chem.inp'));(case/'case.json').write_text(json.dumps(info,indent=2)+'\n')
            change(case/'system/fvSolution','nCorrectors',1);change(case/'system/fvSolution','nOuterCorrectors',1)
            (case/'system/controlDict').open('a').write('\nenergyLedger true; cellEnergyLedger true; cellLedgerEvery 1; energyCorrection none;\n')
            cfg=dict(name=name,kind='F',mode='none',dt=dt,steps=round(240e-6/dt),ranks=4,nCells=256,nCorrectors=1,nOuterCorrectors=1,**version('reactingEnergyCandidates'),thermoControl=thermo,mechanism='Alzueta2023_baseline',driverSHA256=sha(__file__),kineticsSHA256=sha(case/'chemkin/chem.inp'),thermoSHA256=sha(case/'chemkin/therm.dat'),exportManifestSHA256=sha(INPUT/'manifest.json'),scope='Modern distinct mechanism. Same CFD discretization/initial T,p,U,H2/O2/N2/transport. Compare own thermo-only pair; no kinetics-independent causal contrast against legacy H2.')
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
        (STUDY/'data/processed/clean_reference_campaign.json').write_text(json.dumps(records,indent=2)+'\n')
        if 'error' in r:return # Diagnose a shared input failure before launching equivalent cases.
if __name__=='__main__':main()
