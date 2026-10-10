#!/usr/bin/env bash
set -eo pipefail
source "$(dirname "$0")/../../scripts/env.sh"
source "$PAD_ROOT/scripts/compilerEnv.sh"
python3 "$PAD_ROOT/actionStudy/scripts/prepareRedistributor.py"
mkdir -p "$PAD_ROOT/actionStudy/data/raw/build" "$FOAM_USER_APPBIN"
cd "$PAD_ROOT/applications/redistributeParPAD"
wmake > "$PAD_ROOT/actionStudy/data/raw/build/redistributeParPAD.log" 2>&1
