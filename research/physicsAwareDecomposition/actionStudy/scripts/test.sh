#!/usr/bin/env bash
set -eo pipefail
source "$(dirname "$0")/../../scripts/env.sh"
export PYTHONPATH="$PAD_ROOT/scripts:$PAD_ROOT/actionStudy/scripts:${PYTHONPATH:-}"
python3 -m unittest discover -s "$PAD_ROOT/actionStudy/tests" -v
if [ "${1:-unit}" = parallel ]; then
  export PAD_ACTION_ROOT=$(mktemp -d /tmp/pad-action-regression.XXXXXX)
  mkdir -p "$PAD_ACTION_ROOT/data/processed"
  python3 "$PAD_ROOT/actionStudy/scripts/endpointRegression.py"
  if command -v redistributeParPAD >/dev/null; then python3 "$PAD_ROOT/actionStudy/scripts/repeatedMigrationRegression.py"; fi
  echo "Retained parallel smoke evidence: $PAD_ACTION_ROOT"
fi
