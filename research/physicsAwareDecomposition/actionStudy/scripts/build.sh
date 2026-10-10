#!/usr/bin/env bash
set -eo pipefail
source "$(dirname "$0")/../../scripts/env.sh"
source "$PAD_ROOT/scripts/compilerEnv.sh"
mkdir -p "$PAD_ROOT/actionStudy/data/raw/build"
mkdir -p "$FOAM_USER_APPBIN" "$FOAM_USER_LIBBIN"
for target in costChemistry stuttgartV2012; do
  cd "$PAD_ROOT/src/$target"
  wmake libso > "$PAD_ROOT/actionStudy/data/raw/build/$target.log" 2>&1
done
cd "$PAD_ROOT/applications/reactingFoamPAD"
wmake > "$PAD_ROOT/actionStudy/data/raw/build/reactingFoamPAD.log" 2>&1
