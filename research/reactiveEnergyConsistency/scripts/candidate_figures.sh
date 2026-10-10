#!/usr/bin/env bash
set -eo pipefail
source "$(dirname "$0")/candidate_env.sh"
export MPLCONFIGDIR="$REC_ROOT/build/mplCandidates"
"$REC_PAD/build/quicklbEnv/bin/python" "$REC_ROOT/scripts/candidate_figures.py"
