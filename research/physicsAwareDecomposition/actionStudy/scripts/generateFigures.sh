#!/usr/bin/env bash
set -eo pipefail
PAD_TASK_ROOT=$(cd "$(dirname "$0")/../.." && pwd)
PAD_TASK_PYTHON=${PAD_PLOT_PYTHON:-"$PAD_TASK_ROOT/build/quicklbEnv/bin/python"}
export MPLBACKEND=Agg OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1
"$PAD_TASK_PYTHON" "$PAD_TASK_ROOT/actionStudy/scripts/generateFigures.py"
