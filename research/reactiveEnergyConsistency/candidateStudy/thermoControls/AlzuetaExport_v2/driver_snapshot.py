"""Nonphysical CHEMKIN serialization compatibility, prior exports retained."""
from pathlib import Path
import json
from thermo_continuity import sha
ROOT=Path(__file__).resolve().parents[1];BASE=ROOT/'candidateStudy/thermoControls/AlzuetaExport_v1';TARGET=BASE.parent/'AlzuetaExport_v2'
def main():
    if (TARGET/'manifest.json').exists():print('Reused syntax control');return
    if TARGET.exists():raise RuntimeError('Retained incomplete export')
    TARGET.mkdir();(TARGET/'driver_snapshot.py').write_bytes(Path(__file__).read_bytes())
    for name in ['chem.inp','legacy.dat','CpHS.dat']:
        original=(BASE/name).read_text();text='\n'.join(line for line in original.splitlines() if not line.lstrip().startswith('!'))+'\n'
        # Remove quoted prose comments and Windows CRLF; preserve all CHEMKIN data.
        with (TARGET/name).open('w',newline='\n') as f:f.write(text)
    manifest=dict(parentManifestSHA256=sha(BASE/'manifest.json'),driverSHA256=sha(__file__),files={p.name:sha(p) for p in TARGET.iterdir() if p.is_file()},scope='Comments stripped and LF serialization only. No species, stoichiometry, rate, thermo coefficient or initial-state modification. Four original parser failures remain retained.')
    (TARGET/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
if __name__=='__main__':main()
