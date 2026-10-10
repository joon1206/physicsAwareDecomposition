"""Create a separate known HLLC reference, leaving central evidence untouched."""
from pathlib import Path
import shutil,json,hashlib
ROOT=Path(__file__).resolve().parents[1];old=ROOT/'applications/reactingEnergyCentralReference';new=ROOT/'applications/reactingEnergyHLLCReference'
if new.exists():raise RuntimeError('HLLC application already exists; build current source, do not recreate')
new.mkdir();hashes={}
for p in old.iterdir():
    if p.suffix in ['.C','.H']:
        hashes[p.name]=hashlib.sha256(p.read_bytes()).hexdigest()
        shutil.copy2(p,new/('reactingEnergyHLLCReference.C' if p.suffix=='.C' else p.name))
(new/'Make').mkdir()
for p in [old/'Make/files',old/'Make/options']:(new/'Make'/p.name).write_text(p.read_text().replace('reactingEnergyCentralReference','reactingEnergyHLLCReference'))
shutil.copytree(old/'originalV2012',new/'originalV2012')
(new/'parentCentralManifest.json').write_text(json.dumps(hashes,indent=2)+'\n')
app=new/'reactingEnergyHLLCReference.C';src=app.read_text();needle='        volScalarField muEff("muEff", turbulence->muEff());'
assert src.count(needle)==1;src=src.replace(needle,'        #include "hllcFlux.H"\n\n'+needle)
app.write_text(src)
