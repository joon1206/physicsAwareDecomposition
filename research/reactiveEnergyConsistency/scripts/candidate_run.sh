#!/usr/bin/env bash
set -eo pipefail
source "$(dirname "$0")/candidate_env.sh"
python3 "$REC_ROOT/scripts/$1" "${@:2}"
