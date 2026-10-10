#!/usr/bin/env bash
# Safe default: a fresh, retained four-action regression, not a full campaign.
set -eo pipefail
PAD_TASK_SCRIPT_DIR=$(cd "$(dirname "$0")" && pwd)
PAD_TASK_PROFILE=${1:-smoke}
case "$PAD_TASK_PROFILE" in
  smoke) bash "$PAD_TASK_SCRIPT_DIR/test.sh" parallel ;;
  small)
    : "${PAD_ACTION_ROOT:?Set PAD_ACTION_ROOT to a fresh output directory}"
    mkdir -p "$PAD_ACTION_ROOT/data/processed"
    bash "$PAD_TASK_SCRIPT_DIR/run.sh" oracle.py pilot
    ;;
  full)
    : "${PAD_ACTION_ROOT:?Set PAD_ACTION_ROOT to a fresh output directory}"
    mkdir -p "$PAD_ACTION_ROOT/data/processed"
    python3 "$PAD_TASK_SCRIPT_DIR/executeStudy.py"
    ;;
  *) echo "Profiles: smoke (default), small (8 pilot continuations), full (complete bounded local study)"; exit 2 ;;
esac
