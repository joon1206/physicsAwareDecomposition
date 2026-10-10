"""Direct native source trajectory/thermo-branch controls, independently audited."""
from pathlib import Path
import csv,json,math
from caseFactory import make_case,field,command
from campaign import change
from candidate_cv_chemistry import chemistry_version
from candidate_mixture_wave import version
from cv_source_invariant_audit import molar_h
from thermo_reference import parse_nasa
ROOT=Path(__file__).resolve().parents[1];STUDY=ROOT/'candidateStudy';RAW=STUDY/'data/raw'

def main():
    records=[]
    for chunks in [1,1000]:
        for rtol in [1e-8,1e-10,1e-12]:
            name=f'CvBranchProbe_chunks{chunks}_rtol{rtol:g}';case=RAW/name
            if (case/'probe_result.json').exists():records+=json.loads((case/'probe_result.json').read_text());continue
            if case.exists():raise RuntimeError('Retained incomplete '+str(case))
            make_case(name,'uniform',nx=8,ny=1,dt=1e-5,steps=1)
            field(case/'0/T',[999.,1001.,1100.,999.,1001.,1100.,999.,1001.],'[0 0 0 1 0 0 0]')
            field(case/'0/U',(0,0,0),'[0 1 -1 0 0 0 0]',True)
            species=json.loads((case/'case.json').read_text())['species']
            composition=dict(H2=.0283,O2=.225,H=.0001,OH=.0001,N2=.7465)
            for s in species:field(case/'0'/s,composition.get(s,0.),'[0 0 0 0 0 0 0]')
            chemistry=case/'constant/chemistryProperties';chemistry.write_text(chemistry.read_text().replace('solver costOde','solver cvOde'))
            chemistry.open('a').write('odeThermalPath constantVolume;\n');change(chemistry,'relTol',rtol);change(chemistry,'absTol',1e-16)
            control=case/'system/controlDict';control.write_text(control.read_text().replace('libs (','libs ("libcvChemistry.so" '))
            control.open('a').write(f'branchProbeChunks {chunks}; branchProbeEndTime 1e-5;\n')
            cfg=dict(name=name,kind='CvBranchProbe',ranks=1,nCells=8,odeThermalPath='constantVolume',odeRelativeTolerance=rtol,odeAbsoluteTolerance=1e-16,
                     chunks=chunks,TF=1e-5,**version('cvChemistryBranchProbe'),**chemistry_version(),
                     scope='Direct autonomous native ODE trajectory with unchanged NASA/rates. Diagnostic interval subdivision is not a CFD algorithm, exact event tracker or cost benchmark.')
            (case/'experiment.json').write_text(json.dumps(cfg,indent=2)+'\n')
            try:command(['cvChemistryBranchProbe'],case,case/'probe.log')
            except RuntimeError as e:
                (case/'failure.json').write_text(json.dumps(dict(cfg,error=str(e)),indent=2)+'\n');raise
            nasa=parse_nasa(case/'chemkin/therm.dat')
            with (case/'branch_properties.csv').open() as stream:properties=list(csv.DictReader(stream))
            mismatch=max(abs(float(r['molarEnthalpyJump'])-(molar_h(nasa[r['species']]['high'],1000.)-molar_h(nasa[r['species']]['low'],1000.))) for r in properties)
            with (case/'branch_probe.csv').open() as stream:rows=[{k:float(v) for k,v in row.items()} for row in csv.DictReader(stream)]
            for r in rows:
                r.update(name=name,odeRelativeTolerance=rtol,nativeIndependentJumpDifferenceMax=mismatch,
                         energyChange=r['energyFinal']-r['energyInitial'],**{k:cfg[k] for k in ['sourceSnapshot','executableSHA256','chemistrySourceSnapshot','chemistryLibrarySHA256']})
                r['relativeEnergyChange']=abs(r['energyChange'])/max(abs(r['energyInitial']),1.)
                r['relativeJumpUnexplainedEnergy']=abs(r['energyChange']-r['estimatedBranchJump'])/max(abs(r['energyInitial']),1.)
                print(name,'T0',r['Tinitial'],'Tf',r['Tfinal'],'DE',r['energyChange'],'jump',r['estimatedBranchJump'],'remainder',r['relativeJumpUnexplainedEnergy'],flush=True)
            (case/'probe_result.json').write_text(json.dumps(rows,indent=2)+'\n');records+=rows
    (STUDY/'data/processed/cv_branch_probe.json').write_text(json.dumps(records,indent=2)+'\n')
    print('Direct source branch controls',len(records),flush=True)
if __name__=='__main__':main()
