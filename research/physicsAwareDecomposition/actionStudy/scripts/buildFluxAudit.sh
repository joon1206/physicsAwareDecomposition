#!/usr/bin/env bash
set -eo pipefail
source "$(dirname "$0")/../../scripts/env.sh"
source "$PAD_ROOT/scripts/compilerEnv.sh"
cd "$PAD_ROOT/applications/padFluxAudit"
wclean
wmake > "$PAD_ROOT/actionStudy/data/raw/build/fluxAudit.log" 2>&1
