from pathlib import Path
import urllib.request,json,hashlib
ROOT=Path(__file__).resolve().parents[1]
PIN='0754a9cea2482fff0f6fa6630778f65042f47536'
BASE=f'https://raw.githubusercontent.com/UMN-CRFEL/OpenFOAM-Cantera/{PIN}/'
def main():
    records=[]
    for name in ['README.md','LICENSE','CTreactingFoam/CTreactingFoam.C','CTreactingFoam/EEqn.H','CTreactingFoam/YEqn.H','CTreactingFoam/pEqn.H']:
        data=urllib.request.urlopen(BASE+name,timeout=30).read();p=ROOT/'sourceAudit/CTreactingFoam'/name;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(data)
        records.append(dict(commit=PIN,url=BASE+name,path=str(p.relative_to(ROOT)),sha256=hashlib.sha256(data).hexdigest()))
    (ROOT/'docs/prior_art_source_manifest.json').write_text(json.dumps(records,indent=2)+'\n')
if __name__=='__main__':main()
