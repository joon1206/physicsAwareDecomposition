#!/usr/bin/env bash
# Diagnostic executable; leaves every performance-study binary untouched.
set -eo pipefail
source "$(dirname "$0")/../../scripts/env.sh"
source "$PAD_ROOT/scripts/compilerEnv.sh"
export PAD_INITIAL_DIAGNOSTIC_ROOT="$PAD_ROOT"
python3 - <<'PY'
import difflib,hashlib,json,os,shutil
from pathlib import Path
r=Path(os.environ['PAD_INITIAL_DIAGNOSTIC_ROOT']);source=r/'applications/reactingFoamPAD';out=r/'build/initialStateSolver'
out.mkdir(parents=True,exist_ok=True);(out/'Make').mkdir(exist_ok=True)
for p in source.iterdir():
    if p.suffix in ['.C','.H']:shutil.copy2(p,out/p.name)
shutil.copy2(source/'Make/options',out/'Make/options')
(out/'Make/files').write_text((source/'Make/files').read_text().replace('/reactingFoamPAD','/reactingFoamPADInitialState'))
path=out/'createFields.H';before=path.read_text();needle='thermo.validate(args.executable(), "h", "e");'
assert before.count(needle)==1
after=before.replace(needle,needle+'\n// Initialization diagnostic: preserve the initial Euler coefficient before thermo changes it.\nif (runTime.value() <= SMALL) thermo.psi().oldTime();')
path.write_text(after)
docs=r/'actionStudy/docs'
(docs/'initial_psi.patch').write_text(''.join(difflib.unified_diff(before.splitlines(True),after.splitlines(True),fromfile='native-compatible/createFields.H',tofile='diagnostic/createFields.H')))
(docs/'initial_state_port.json').write_text(json.dumps(dict(originalHeaderSHA256=hashlib.sha256(before.encode()).hexdigest(),diagnosticHeaderSHA256=hashlib.sha256(after.encode()).hexdigest(),scope='Separate initialization-only diagnostic; final performance dataset and its original solver binaries remain unchanged.'),indent=2))
PY
cd "$PAD_ROOT/build/initialStateSolver"
wclean
wmake > "$PAD_ROOT/actionStudy/data/raw/build/initialStateSolver.log" 2>&1
