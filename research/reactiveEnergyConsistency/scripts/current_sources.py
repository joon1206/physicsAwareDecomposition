"""Read current official source releases without changing the installation."""
from pathlib import Path
import urllib.request,tarfile,json,hashlib
ROOT=Path(__file__).resolve().parents[1]
def main():
    output=ROOT/'sourceAudit';output.mkdir(exist_ok=True);records=[]
    base='https://raw.githubusercontent.com/OpenFOAM/OpenFOAM-14/master/'
    for name in ['applications/modules/multicomponentFluid/thermophysicalPredictor.C','applications/modules/isothermalFluid/pressureCorrector.C']:
        url=base+name
        try:
            data=urllib.request.urlopen(url,timeout=30).read();p=output/'foundation14'/name;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(data)
            records.append(dict(url=url,path=str(p.relative_to(ROOT)),sha256=hashlib.sha256(data).hexdigest(),status='retrieved'))
        except Exception as e:records.append(dict(url=url,status='unavailable',error=str(e)))
    url='https://dl.openfoam.com/source/v2606/OpenFOAM-v2606.tgz'
    targets={f'applications/solvers/{directory}/{name}' for directory in ['combustion/reactingFoam','compressible/rhoPimpleFoam'] for name in ['EEqn.H','pEqn.H','YEqn.H','createFields.H']}
    try:
        with urllib.request.urlopen(url,timeout=60) as response,tarfile.open(fileobj=response,mode='r|gz') as archive:
            for member in archive:
                relative=member.name.split('/',1)[-1]
                if relative in targets:
                    data=archive.extractfile(member).read();p=output/'openCFD2606'/relative;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(data)
                    records.append(dict(url=url,member=member.name,path=str(p.relative_to(ROOT)),sha256=hashlib.sha256(data).hexdigest(),status='retrieved'))
                    targets.remove(relative);print('Read',relative,flush=True)
                # rhoPimpleFoam has no YEqn: don't wait for a nonexistent file.
                if targets=={'applications/solvers/compressible/rhoPimpleFoam/YEqn.H'}:break
        if targets:records.append(dict(url=url,status='not_found',members=sorted(targets)))
    except Exception as e:records.append(dict(url=url,status='unavailable',error=str(e)))
    (ROOT/'docs/current_source_manifest.json').write_text(json.dumps(records,indent=2)+'\n')
if __name__=='__main__':main()
