"""Host/toolchain/source/binary fingerprints without exposing environment secrets."""
import datetime,hashlib,json,subprocess
from pathlib import Path
from analysis import ROOT
PAD=Path(__file__).resolve().parents[2]
def run(args):
    result=subprocess.run(args,cwd=PAD,text=True,stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
    return dict(exitCode=result.returncode,output=result.stdout)
def main():
    sources=[]
    for directory in ['src','applications','actionStudy/scripts','actionStudy/tests','tools','scripts']:
        for p in (PAD/directory).rglob('*'):
            if not p.is_file() or any(part in ['lnInclude','__pycache__'] or part.startswith('linux') for part in p.parts):continue
            if p.suffix in ['.C','.H','.c','.py','.sh'] or p.name in ['files','options','g++']:
                sources.append(dict(path=str(p.relative_to(PAD)),sha256=hashlib.sha256(p.read_bytes()).hexdigest()))
    binaries=[dict(path=str(p.relative_to(PAD)),sha256=hashlib.sha256(p.read_bytes()).hexdigest()) for folder in ['build/bin','build/lib'] for p in (PAD/folder).iterdir() if p.is_file()]
    result=dict(timestamp=datetime.datetime.now(datetime.timezone.utc).isoformat(),git=run(['git','rev-parse','HEAD']),
        hardware=run(['lscpu']),memory=run(['free','-b']),kernel=run(['uname','-a']),mpi=run(['mpirun','--version']),
        clusterAvailability={name:run(['which',name]) for name in ['sbatch','sinfo','srun']},sources=sources,binaries=binaries)
    out=ROOT/'docs';out.mkdir(parents=True,exist_ok=True)
    (out/'environment_manifest.json').write_text(json.dumps(result,indent=2))
    (out/'source_manifest.json').write_text(json.dumps(sources,indent=2))
    print('CAPTURED',len(sources),'source hashes and',len(binaries),'binary hashes')
if __name__=='__main__':main()
