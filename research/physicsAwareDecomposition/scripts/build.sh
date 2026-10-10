#!/usr/bin/env bash
source "$(dirname "$0")/env.sh"
set -eo pipefail
git -C "$PAD_ROOT" status --short
git -C "$PAD_ROOT" branch --show-current
git -C "$PAD_ROOT" rev-parse HEAD
# Existing GCC 6.3/focal sysroot wrappers required on this minimal installation.
source "$PAD_ROOT/scripts/compilerEnv.sh"
mkdir -p "$FOAM_USER_APPBIN" "$FOAM_USER_LIBBIN" "$PAD_ROOT/data/raw/build"
cd "$PAD_ROOT/applications/reactingFoamPAD"
wmake 2>&1 | tee "$PAD_ROOT/data/raw/build/solver.log"
cd "$PAD_ROOT/src/costChemistry"
wmake libso 2>&1 | tee "$PAD_ROOT/data/raw/build/chemistry.log"

cd "$PAD_ROOT/applications/padWorkloadFoam"
wmake 2>&1 | tee "$PAD_ROOT/data/raw/build/synthetic.log"
