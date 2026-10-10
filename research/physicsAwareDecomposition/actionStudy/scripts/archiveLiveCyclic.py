"""Preserve owned AM live runs before rebuilding with the utility fix."""
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def main():
    live=ROOT/'data/raw/live';archive=ROOT/'data/raw/liveCyclicUtilityRejected';archive.mkdir(exist_ok=True)
    moved=[]
    for source in live.iterdir():
        if not source.is_dir():continue
        manifest=source/'manifest.json';row=json.loads(manifest.read_text()) if manifest.exists() else {}
        uses_mesh='_AM_r' in source.name or any(e['action'] in ['AM','AH'] for e in row.get('events',[]))
        if not uses_mesh:continue
        target=archive/source.name
        if target.exists():raise RuntimeError('prior archive exists; preserve it separately before retry')
        if not source.resolve().is_relative_to(live.resolve()):raise RuntimeError('owned-path boundary')
        source.rename(target);moved.append(source.name)
    (archive/'archive.json').write_text(json.dumps(dict(cases=moved,
        reason='Native v2012 loadOrCreateMesh treats processorCyclic as a physical patch during repeated redistribution. Retained AM runs are excluded and rerun with the private validation-only fix.'),indent=2))
    print('PRESERVED',len(moved),'AM/mesh-policy live cases; rerun uses private cyclic-patch fix')
if __name__=='__main__':main()
