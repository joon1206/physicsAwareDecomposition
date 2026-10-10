"""Retain partial live evidence before the full segment-preserving run."""
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def main():
    live=ROOT/'data/raw/live';archive=ROOT/'data/raw/liveBeforeSegmentRetention';archive.mkdir(exist_ok=True);moved=[]
    for source in live.iterdir():
        if not source.is_dir():continue
        destination=archive/source.name
        if destination.exists():raise RuntimeError('archive already exists; refusing replacement')
        if not source.resolve().is_relative_to(live.resolve()):raise RuntimeError('owned directory boundary')
        source.rename(destination);moved.append(source.name)
    (archive/'archive.json').write_text(json.dumps(dict(cases=moved,
        reason='Complete live collection rerun with all prefix/segment clocks and logs retained, and the repeated-cyclic utility fix. Numerical settings, frozen model, jobs, repetitions and randomization seed unchanged. These partial runs remain available and are excluded from final summaries.'),indent=2))
    print('PRESERVED',len(moved),'partial live cases; final collection starts fresh with segment evidence')
if __name__=='__main__':main()
