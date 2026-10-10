#!/usr/bin/env bash
source "$(dirname "$0")/env.sh"
set -eo pipefail
export PAD_OUTPUT_ROOT="${PAD_OUTPUT_ROOT:-$PAD_ROOT/reproductions/smoke_$(date -u +%Y%m%dT%H%M%SZ)}"
test ! -e "$PAD_OUTPUT_ROOT" || { echo "Use a fresh PAD_OUTPUT_ROOT"; exit 2; }
mkdir -p "$PAD_OUTPUT_ROOT/data/raw"
bash "$PAD_ROOT/scripts/build.sh"
python3 "$PAD_ROOT/scripts/collectMachineInfo.py"
python3 -m unittest discover -s "$PAD_ROOT/tests" -v 2>&1 | tee "$PAD_OUTPUT_ROOT/data/raw/component_tests.log"
python3 "$PAD_ROOT/scripts/study.py" smoke
python3 "$PAD_ROOT/scripts/postprocessThermo.py"
python3 "$PAD_ROOT/scripts/integrationChecks.py"
python3 "$PAD_ROOT/scripts/probeValidation.py"
echo "TESTED smoke evidence: $PAD_OUTPUT_ROOT"
