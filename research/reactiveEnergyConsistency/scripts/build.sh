#!/usr/bin/env bash
set -eo pipefail
source "$(dirname "$0")/env.sh"
# Reuse the established read-only compiler wrapper, while all new objects and
# executables go into this study. It links the already existing adapter libs.
export PAD_SYSROOT=${PAD_SYSROOT:-"$HOME/local"}
export PATH="$REC_PAD/tools/wrappers:$PAD_SYSROOT/usr/bin:$PATH"
unset C_INCLUDE_PATH CPLUS_INCLUDE_PATH CPATH
cd "$REC_ROOT/applications/reactingEnergyAudit"
wmake > "$REC_ROOT/data/raw/build.log" 2>&1
echo "Built $FOAM_USER_APPBIN/reactingEnergyAudit"
