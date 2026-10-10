"""Retain licensed modern reference mechanism for distinct native audit controls."""
from pathlib import Path
import json,sys
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'build/canteraPackages'))
sys.path.append(str(ROOT.parent/'physicsAwareDecomposition/scripts'))
sys.path.append(str(ROOT.parent/'physicsAwareDecomposition/actionStudy/scripts'))
import cantera as ct
from cantera import yaml2ck
from thermo_continuity import number,repair,sha,properties
from thermo_reference import parse_nasa,ATOMIC
STUDY=ROOT/'candidateStudy';TARGET=STUDY/'thermoControls/AlzuetaExport_v1'
def main():
    if (TARGET/'manifest.json').exists():print('Reused immutable modern export');return
    if TARGET.exists():raise RuntimeError('Retained incomplete export')
    TARGET.mkdir();(TARGET/'driver_snapshot.py').write_bytes(Path(__file__).read_bytes())
    source=ROOT/'build/canteraPackages/cantera/data/example_data/ammonia-CO-H2-Alzueta-2023.yaml'
    gas=ct.Solution(str(source),'baseline')
    yaml2ck.convert(gas,mechanism_path=TARGET/'chem.inp',thermo_path=TARGET/'legacy.dat')
    # Local parser extension only; installed atomic weight was read directly.
    ATOMIC['HE']=4.00260
    nasa=parse_nasa(TARGET/'legacy.dat');lines=(TARGET/'legacy.dat').read_text().splitlines()
    for i,line in enumerate(lines):
        if len(line)<80 or line[79]!='1':continue
        name=line[:18].strip().split()[0];spec=repair(nasa[name],'CpHS')
        lines[i+1]=number(spec['high'][0])+lines[i+1][15:]
        lines[i+2]=number(spec['high'][5])+number(spec['high'][6])+lines[i+2][30:]
    (TARGET/'CpHS.dat').write_text('\n'.join(lines)+'\n');clean=parse_nasa(TARGET/'CpHS.dat')
    thermo=[]
    for name,spec in clean.items():
        low=properties(spec['low'],spec['mid']);high=properties(spec['high'],spec['mid'])
        thermo.append(dict(species=name,jumps={k:high[k]-low[k] for k in low}))
    result=dict(nSpecies=gas.n_species,nReactions=gas.n_reactions,sourceSHA256=sha(source),sourcePhase='baseline',canteraVersion=ct.__version__,driverSHA256=sha(__file__),files={p.name:sha(p) for p in TARGET.iterdir() if p.is_file()},thermo=thermo,
                scope='Independent packaged Alzueta 2023 baseline exported through Cantera yaml2ck. Native CHEMKIN uses legacy Ru/weights; this is a distinct mechanism audit, not a thermo-only comparison against the old H2 rates. Its own legacy/CpHS pair retains identical kinetic input and reference low branch.')
    (TARGET/'manifest.json').write_text(json.dumps(result,indent=2)+'\n');print('Exported',gas.n_species,gas.n_reactions,flush=True)
if __name__=='__main__':main()
