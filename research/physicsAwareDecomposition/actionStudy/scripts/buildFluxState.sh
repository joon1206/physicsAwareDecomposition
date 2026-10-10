#!/usr/bin/env bash
set -eo pipefail
source "$(dirname "$0")/../../scripts/env.sh"
source "$PAD_ROOT/scripts/compilerEnv.sh"
cd "$PAD_ROOT/applications/padFluxState"
wclean
wmake > "$PAD_ROOT/actionStudy/data/raw/build/fluxState.log" 2>&1
