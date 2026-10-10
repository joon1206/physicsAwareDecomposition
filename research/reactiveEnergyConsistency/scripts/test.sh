#!/usr/bin/env bash
set -eo pipefail
source "$(dirname "$0")/env.sh"
python3 -m unittest discover -s "$REC_ROOT/tests" -v 2>&1 | tee "$REC_ROOT/data/processed/test_results.txt"
