#!/usr/bin/env bash
set -eo pipefail
source "$(dirname "$0")/../../scripts/env.sh"
source "$PAD_ROOT/scripts/compilerEnv.sh"
mkdir -p "$PAD_ROOT/actionStudy/data/raw/build" "$FOAM_USER_APPBIN"
cd "$PAD_ROOT/applications/padNativeInventory"
wmake > "$PAD_ROOT/actionStudy/data/raw/build/nativeInventory.log" 2>&1
