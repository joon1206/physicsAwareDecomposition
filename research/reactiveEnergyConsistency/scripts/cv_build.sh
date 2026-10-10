#!/usr/bin/env bash
set -e
source "$(dirname "${BASH_SOURCE[0]}")/candidate_env.sh"
export PAD_SYSROOT=${PAD_SYSROOT:-"$HOME/local"}
export PATH="$REC_PAD/tools/wrappers:$PAD_SYSROOT/usr/bin:$PATH"
unset CPATH CPLUS_INCLUDE_PATH C_INCLUDE_PATH
mkdir -p "$FOAM_USER_LIBBIN"
cd "$REC_ROOT/src/cvChemistry"
wmake libso > "$REC_ROOT/build/cv_build.log" 2>&1
echo "Built $FOAM_USER_LIBBIN/libcvChemistry.so"
