"""Direct unchanged native ODE controls with continuous thermodynamic inputs."""
from pathlib import Path
import csv,json,shutil
from caseFactory import make_case,field,command
from campaign import change
from candidate_mixture_wave import version
from candidate_cv_chemistry import chemistry_version
from thermo_continuity import CONTROL,sha
ROOT=Path(__file__).resolve().parents[1];STUDY=ROOT/'candidateStudy';RAW=STUDY/'data/raw'
def main():
    rows=[]
    for thermo in ['HS','CpHS']:
     for rtol in [1e-8,1e-10,1e-12]:
        name=f'CleanBranch_{thermo}_rtol{rtol:g}';case=RAW/name
        if (case/'probe_result.json').exists():rows+=json.loads((case/'probe_result.json').read_text());continue
        if case.exists():raise RuntimeError('Retained incomplete '+str(case))
        make_case(name,'uniform',nx=8,ny=1,dt=1e-5,steps=1);shutil.copy2(CONTROL/f'{thermo}.dat',case/'chemkin/therm.dat')
        field(case/'0/T',[999,1001,1100,999,1001,1100,999,1001],'[0 0 0 1 0 0 0]')
        for s in json.loads((case/'case.json').read_text())['species']:field(case/'0'/s,dict(H2=.0283,O2=.225,H=.0001,OH=.0001,N2=.7465).get(s,0))
        cp=case/'constant/chemistryProperties';cp.write_text(cp.read_text().replace('solver costOde','solver cvOde'));cp.open('a').write('odeThermalPath constantVolume;\n');change(cp,'relTol',rtol);change(cp,'absTol',1e-16)
        control=case/'system/controlDict';control.write_text(control.read_text().replace('libs (','libs ("libcvChemistry.so" '));control.open('a').write('branchProbeChunks 1000; branchProbeEndTime 1e-5;\n')
        cfg=dict(name=name,kind='CleanBranch',ranks=1,nCells=8,thermoControl=thermo,odeRelativeTolerance=rtol,**version('cvChemistryBranchProbe'),**chemistry_version(),driverSHA256=sha(__file__),thermoSHA256=sha(case/'chemkin/therm.dat'),scope='Unchanged direct native utility, same three states and 1000 diagnostic intervals as legacy probe.')
        (case/'experiment.json').write_text(json.dumps(cfg,indent=2)+'\n')
        try:command(['cvChemistryBranchProbe'],case,case/'probe.log')
        except RuntimeError as e:
            (case/'failure.json').write_text(json.dumps(dict(cfg,error=str(e)),indent=2)+'\n');raise
        with (case/'branch_probe.csv').open() as f:records=[{k:float(v) for k,v in r.items()} for r in csv.DictReader(f)]
        for r in records:
            r.update(name=name,thermoControl=thermo,odeRelativeTolerance=rtol,relativeEnergyChange=abs(r['energyFinal']-r['energyInitial'])/max(abs(r['energyInitial']),1))
            print(name,r['Tinitial'],r['relativeEnergyChange'],flush=True)
        (case/'probe_result.json').write_text(json.dumps(records,indent=2)+'\n');rows+=records
    (STUDY/'data/processed/clean_thermo_branch.json').write_text(json.dumps(rows,indent=2)+'\n')
if __name__=='__main__':main()
