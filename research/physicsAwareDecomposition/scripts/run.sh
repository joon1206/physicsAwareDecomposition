#!/usr/bin/env bash
source "$(dirname "$0")/env.sh"
set -eo pipefail
python3 "$PAD_ROOT/scripts/study.py" "$@"
