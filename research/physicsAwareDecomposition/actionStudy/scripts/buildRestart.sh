#!/usr/bin/env bash
# Separate executable: never replaces a binary during an active campaign.
set -eo pipefail
source "$(dirname "$0")/../../scripts/env.sh"
source "$PAD_ROOT/scripts/compilerEnv.sh"
export PAD_TASK_BUILD_ROOT="$PAD_ROOT"
python3 - <<'PY'
import os,shutil
from pathlib import Path
r=Path(os.environ['PAD_TASK_BUILD_ROOT']);source=r/'applications/reactingFoamPAD';out=r/'build/restartSolver'
out.mkdir(parents=True,exist_ok=True);(out/'Make').mkdir(exist_ok=True)
for p in source.iterdir():
    if p.suffix in ['.C','.H']:shutil.copy2(p,out/p.name)
shutil.copy2(source/'Make/options',out/'Make/options')
(out/'Make/files').write_text((source/'Make/files').read_text().replace('/reactingFoamPAD','/reactingFoamPADRestart'))
PY
cd "$PAD_ROOT/build/restartSolver"
wmake > "$PAD_ROOT/actionStudy/data/raw/build/restartSolver.log" 2>&1
