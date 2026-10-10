#!/usr/bin/env bash
set -eo pipefail
PAD_TASK_ROOT=$(cd "$(dirname "$0")/../.." && pwd)
exec "$PAD_TASK_ROOT/build/quicklbEnv/bin/python" "$PAD_TASK_ROOT/actionStudy/scripts/figureContactSheets.py"
