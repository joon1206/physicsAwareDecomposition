"""Native callback contract and continuous-identity controls, distinct inputs."""
from pathlib import Path
import csv,json
from caseFactory import make_case,field,command
from candidate_cv_chemistry import chemistry_version
from candidate_mixture_wave import version
ROOT=Path(__file__).resolve().parents[1];STUDY=ROOT/'candidateStudy';RAW=STUDY/'data/raw'
def main():
    records=[]
    for path in ['constantPressure','constantVolume']:
        name='CvProbe_'+path+'_dfdt0';case=RAW/name
        if (case/'probe_result.json').exists():records+=json.loads((case/'probe_result.json').read_text());continue
        if case.exists():raise RuntimeError('Retained incomplete '+str(case))
        make_case(name,'uniform',nx=8,ny=1,dt=1e-6,steps=1)
        field(case/'0/T',[600.,800.,1100.,1400.,1800.,2200.,2600.,3000.],'[0 0 0 1 0 0 0]')
        chemistry=case/'constant/chemistryProperties';chemistry.write_text(chemistry.read_text().replace('solver costOde','solver cvOde'))
        chemistry.open('a').write(f'odeThermalPath {path};\n')
        control=case/'system/controlDict';control.write_text(control.read_text().replace('libs (','libs ("libcvChemistry.so" '))
        cfg=dict(name=name,odeThermalPath=path,**version('cvChemistryProbe'),**chemistry_version(),scope='ODE callback contract, directional Jacobian and continuous mass/thermal/EOS identities; no trajectory/error-order claim.')
        (case/'experiment.json').write_text(json.dumps(cfg,indent=2)+'\n')
        try:command(['cvChemistryProbe'],case,case/'probe.log')
        except RuntimeError as e:
            (case/'failure.json').write_text(json.dumps(dict(cfg,error=str(e)),indent=2)+'\n');raise
        with (case/'cv_ode_probe.csv').open() as stream:
            rows=[{k:v if k=='path' else float(v) for k,v in r.items()} for r in csv.DictReader(stream)]
        (case/'probe_result.json').write_text(json.dumps(rows,indent=2)+'\n')
        records+=rows
    (STUDY/'data/processed/cv_chemistry_probe.json').write_text(json.dumps(records,indent=2)+'\n')
    print('Native ODE probes:',len(records),'max directional discrepancy',max(r['directionalJacobianRelativeError'] for r in records),'max time derivative',max(r['timeDerivativeMax'] for r in records))
if __name__=='__main__':main()
