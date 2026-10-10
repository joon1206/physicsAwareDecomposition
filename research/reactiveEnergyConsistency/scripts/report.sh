#!/usr/bin/env bash
set -eo pipefail
source "$(dirname "$0")/env.sh"
export MPLCONFIGDIR="$REC_ROOT/build/matplotlib"
"$REC_PAD/build/quicklbEnv/bin/python" "$REC_ROOT/scripts/report.py"
