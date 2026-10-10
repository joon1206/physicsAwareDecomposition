#!/usr/bin/env bash
set -eo pipefail
source "$(dirname "$0")/candidate_env.sh"
export PAD_SYSROOT=${PAD_SYSROOT:-"$HOME/local"}
export PATH="$REC_PAD/tools/wrappers:$PAD_SYSROOT/usr/bin:$PATH"
unset C_INCLUDE_PATH CPLUS_INCLUDE_PATH CPATH
cd "$REC_ROOT/applications/reactingEnergyBlockCandidates"
wmake > "$REC_ROOT/candidateStudy/data/raw/block_build.log" 2>&1
echo "Built $FOAM_USER_APPBIN/reactingEnergyBlockCandidates"
