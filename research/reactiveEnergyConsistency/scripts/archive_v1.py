"""Retain the rejected diagnostics; never delete failed experiments."""
from pathlib import Path
import json
ROOT=Path(__file__).resolve().parents[1]
raw=ROOT/'data/raw';target=raw/'diagnosticResidualV1'
assert target.resolve().is_relative_to(raw.resolve())
target.mkdir(exist_ok=False)
for p in list(raw.iterdir()):
    if p.is_dir() and p!=target:
        assert p.resolve().is_relative_to(raw.resolve())
        p.rename(target/p.name)
(target/'REJECTED.json').write_text(json.dumps(dict(reason='Native fvScalarMatrix::residual double counts coupled-boundary sources in v2012; independent reconstruction initially used a different gas constant. These data are excluded from final equation attribution.',fieldsChangedByDiagnostic=False),indent=2)+'\n')
