#!/usr/bin/env python3
import datetime, hashlib, json, os, pathlib, subprocess
ROOT = pathlib.Path(os.environ.get('PAD_OUTPUT_ROOT',pathlib.Path(__file__).resolve().parents[1]))
def command(args):
    try:
        p = subprocess.run(args,text=True,capture_output=True,timeout=30)
        return {'command':args,'returncode':p.returncode,'stdout':p.stdout,'stderr':p.stderr}
    except (OSError,subprocess.TimeoutExpired) as e:
        return {'command':args,'unavailable':str(e)}
def main():
    cmds = [['git','status','--short'],['git','branch','--show-current'],['git','rev-parse','HEAD'],
      ['uname','-a'],['hostname'],['lscpu'],['lscpu','-e'],['free','-b'],['numactl','--hardware'],
      ['g++','--version'],['mpirun','--version'],['cmake','--version'],['python3','--version'],
      ['make','--version'],['sinfo'],['scontrol','show','nodes'],['nvidia-smi'],['perf','--version']]
    foam=pathlib.Path(os.environ['WM_PROJECT_DIR'])
    rels=['applications/solvers/combustion/reactingFoam/reactingFoam.C',
      'applications/solvers/combustion/reactingFoam/YEqn.H',
      'applications/utilities/parallelProcessing/decomposePar/domainDecompositionDistribute.C',
      'src/combustionModels/laminar/laminar.C',
      'src/thermophysicalModels/chemistryModel/chemistryModel/StandardChemistryModel/StandardChemistryModel.C',
      'src/thermophysicalModels/chemistryModel/chemistrySolver/EulerImplicit/EulerImplicit.C',
      'src/parallel/decompose/scotchDecomp/scotchDecomp.C','wmake/rules/General/Gcc/c++']
    m={'timestamp':datetime.datetime.now(datetime.timezone.utc).isoformat(),'client_date':'2026-10-04',
      'platform':'single WSL2 guest; no cluster allocation detected',
      'environment':{k:v for k,v in os.environ.items() if k.startswith(('WM_','FOAM_','MPI_','OPAL_','OMP_'))},
      'commands':[command(c) for c in cmds],'source':{}}
    for rel in rels:
        p=foam/rel
        m['source'][str(p)]={'sha256':hashlib.sha256(p.read_bytes()).hexdigest()} if p.exists() else {'missing':True}
    m['decomposition_libraries']=[str(p) for p in pathlib.Path(os.environ['FOAM_LIBBIN']).glob('*Decomp*')]
    m['os_release']=pathlib.Path('/etc/os-release').read_text()
    m['cpu_governor']={str(p):p.read_text().strip() for p in pathlib.Path('/sys/devices/system/cpu').glob('cpu*/cpufreq/scaling_governor')}
    p=ROOT/'data/machine.json';p.parent.mkdir(parents=True,exist_ok=True)
    p.write_text(json.dumps(m,indent=2)+'\n');print(p)
if __name__=='__main__':main()
