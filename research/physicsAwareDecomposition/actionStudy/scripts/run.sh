#!/usr/bin/env bash
set -eo pipefail
source "$(dirname "$0")/../../scripts/env.sh"
export PYTHONPATH="$PAD_ROOT/scripts:$PAD_ROOT/actionStudy/scripts:${PYTHONPATH:-}"
exec python3 "$PAD_ROOT/actionStudy/scripts/$1" "${@:2}"
