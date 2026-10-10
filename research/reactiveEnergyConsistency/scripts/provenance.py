from pathlib import Path
import json,hashlib,subprocess,datetime
ROOT=Path(__file__).resolve().parents[1]
FOAM=Path('/opt/OpenFOAM/OpenFOAM-v2012')
PAD=ROOT.parent/'physicsAwareDecomposition'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    files=[FOAM/'META-INFO/api-info',FOAM/'etc/controlDict',
      FOAM/'applications/solvers/combustion/reactingFoam/reactingFoam.C',
      FOAM/'applications/solvers/combustion/reactingFoam/EEqn.H',
      FOAM/'applications/solvers/combustion/reactingFoam/pEqn.H',
      FOAM/'applications/solvers/combustion/reactingFoam/YEqn.H',
      FOAM/'applications/solvers/compressible/rhoPimpleFoam/EEqn.H',
      FOAM/'src/thermophysicalModels/basic/psiThermo/hePsiThermo.C',
      FOAM/'src/thermophysicalModels/chemistryModel/chemistryModel/StandardChemistryModel/StandardChemistryModel.C',
      FOAM/'src/finiteVolume/fvMatrices/fvScalarMatrix/fvScalarMatrix.C']
    environment=dict(timestampUTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),clientDate='2026-10-06',clientTimezone='America/New_York',
      gitHEAD=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT).decode().strip(),
      gitStatus=subprocess.check_output(['git','status','--short'],cwd=ROOT).decode(),
      api=(FOAM/'META-INFO/api-info').read_text(),platform='linux64Gcc63DPInt32Opt',
      hardware=subprocess.check_output(['lscpu']).decode(),mpi=subprocess.check_output(['mpirun','--version']).decode(),
      executableSHA256=sha(ROOT/'build/bin/reactingEnergyAudit'),installedSources={str(p):sha(p) for p in files},
      readOnlyDependencies={str(p):sha(p) for p in [PAD/'tools/wrappers/g++',
        PAD/'build/lib/libcostChemistry.so',PAD/'build/lib/libstuttgartV2012.so',
        PAD/'build/bin/reactingFoamPADInitialState',PAD/'build/bin/padNativeInventory']},
      compiler=subprocess.check_output([str(FOAM/'ThirdParty/platforms/linux64/gcc-6.3.0/bin/g++'),'--version']).decode(),
      python=subprocess.check_output(['python3','--version']).decode(),
      instrumentationScope='Euler sensible enthalpy, fixed mesh, nontransonic/nonconsistent, closed periodic, laminar; executed cases have no fvOptions/MRF.')
    (ROOT/'docs/environment_manifest.json').write_text(json.dumps(environment,indent=2)+'\n')
    portable=[p for sub in ['applications','scripts','tests','sourceAudit','figures','data/processed','docs']
              for p in (ROOT/sub).rglob('*') if p.is_file() and not any(
                q in {'linux64Gcc63DPInt32Opt','lnInclude','__pycache__'} for q in p.parts)
              and p.name!='evidence_manifest.json']+[ROOT/'README.md',ROOT/'references.bib',ROOT/'.gitignore']
    evidence=[p for p in (ROOT/'data/raw').glob('*/result.json')]+list((ROOT/'data/raw').glob('*/mms_result.json'))
    manifest={'scope':'Source, scripts, processed evidence and figures; raw metadata plus reproducible case dictionaries/initial fields. Full raw logs/fields/CSV remain local.',
      'files':{str(p.relative_to(ROOT)):{'bytes':p.stat().st_size,'sha256':sha(p)} for p in portable+evidence}}
    for meta in evidence:
        case=meta.parent
        for directory in ['0','system','constant']:
            for p in (case/directory).rglob('*'):
                if p.is_file():manifest['files'][str(p.relative_to(ROOT))]={'bytes':p.stat().st_size,'sha256':sha(p)}
    (ROOT/'docs/evidence_manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
if __name__=='__main__':main()
