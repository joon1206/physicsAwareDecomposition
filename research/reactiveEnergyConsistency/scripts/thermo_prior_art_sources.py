"""Retain primary method/source bytes and hashes without changing dependencies."""
from pathlib import Path
import datetime,json,urllib.request
from thermo_continuity import sha
ROOT=Path(__file__).resolve().parents[1];TARGET=ROOT/'sourceAudit/thermoInvariants_v1'
URLS={
 'MechChecker2020.pdf':'https://combustiontools.llnl.gov/static/MechCheck_CandF_2020_08_02.pdf',
 'NASA_Glenn2002.pdf':'https://ntrs.nasa.gov/api/citations/20020085330/downloads/20020085330.pdf',
 'BoettcherAppendixH.pdf':'https://thesis.caltech.edu/7037/6/Boettcher_P_A_App_A_to_H.pdf',
 'RMG_wilhoit.pyx':'https://raw.githubusercontent.com/ReactionMechanismGenerator/RMG-Py/main/rmgpy/thermo/wilhoit.pyx',
 'CVODE_mathematics.html':'https://sundials.readthedocs.io/en/latest/cvode/Mathematics_link.html',
 'Pele_CvodeInPP.html':'https://pelephysics.readthedocs.io/en/latest/CvodeInPP.html',
 'StandardChemistryModel.C':'file:///opt/OpenFOAM/OpenFOAM-v2012/src/thermophysicalModels/chemistryModel/chemistryModel/StandardChemistryModel/StandardChemistryModel.C'}
def main():
    manifest=TARGET/'manifest.json'
    if manifest.exists():print('Reused primary-source manifest');return
    TARGET.mkdir(parents=True,exist_ok=True);records=[]
    for name,url in URLS.items():
        dest=TARGET/name
        try:
            if not dest.exists():
                req=urllib.request.Request(url,headers={'User-Agent':'Computational-research-provenance/1.0'})
                with urllib.request.urlopen(req,timeout=30) as response:dest.write_bytes(response.read())
            records.append(dict(name=name,url=url,sha256=sha(dest),size=dest.stat().st_size))
        except Exception as e:records.append(dict(name=name,url=url,error=str(e)))
    manifest.write_text(json.dumps(dict(retrievedUTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),records=records,scope='Retrieved primary bytes are pinned by SHA256; branch/latest URLs identify retrieval endpoint, not a fixed upstream commit.'),indent=2)+'\n')
    print(json.dumps(records,indent=2))
if __name__=='__main__':main()
