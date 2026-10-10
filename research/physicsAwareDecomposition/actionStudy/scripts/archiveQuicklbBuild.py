"""Preserve the failed build that inherited OpenFOAM's OPAL_LIBDIR."""
import json
from pathlib import Path
PAD=Path(__file__).resolve().parents[2];ROOT=PAD/'actionStudy'
source=next(p for p in (PAD/'vendor/quicklb').iterdir() if p.is_dir() and (p/'setup.py').exists())
build=source/'build';archive=PAD/'build/quicklbFailedOPALLibDir'
assert build.resolve().is_relative_to((PAD/'vendor/quicklb').resolve())
assert not archive.exists();archive.mkdir()
build.rename(archive/'build')
log=ROOT/'data/raw/finishLogs/quicklb.log'
(ROOT/'data/raw/build/quicklbNativeEnvRejected.log').write_bytes(log.read_bytes())
(archive/'reason.json').write_text(json.dumps(dict(reason='OpenFOAM shell OPAL_LIBDIR redirected the isolated mpifort module/library paths to the older installed MPI. Clear all relevant OPAL overrides, preserve this cache, and configure afresh.'),indent=2))
print('Preserved failed QUICKLB cache; isolated retry will configure afresh.')
