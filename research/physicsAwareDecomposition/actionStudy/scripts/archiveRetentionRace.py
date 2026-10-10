"""Preserve the stopped collection that overlapped an evidence archive."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
source_root = ROOT / 'data/raw/live'
destination_root = ROOT / 'data/raw/liveRetentionRace'
destination_root.mkdir(exist_ok=False)
moved = []
for source in source_root.iterdir():
    if not source.is_dir():
        continue
    assert source.resolve().is_relative_to(source_root.resolve())
    destination = destination_root / source.name
    assert not destination.exists()
    source.rename(destination)
    moved.append(source.name)
for name in ['live.log']:
    source = ROOT / 'data/raw/finishLogs' / name
    if source.exists():
        (destination_root / name).write_bytes(source.read_bytes())
(destination_root / 'archive.json').write_text(json.dumps(dict(
    cases=moved, excluded=True,
    reason='The stopped first completion run overlapped the one-time archival of live evidence. The case directory was moved during a solve, causing FileNotFoundError in endpoint validation. Preserve this attempt, then rerun the entire randomized collection using finalized segment retention code.'
), indent=2))
print('Preserved', len(moved), 'stopped live cases; no active collection remains.')
