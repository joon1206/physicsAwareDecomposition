#!/usr/bin/env bash
set -eo pipefail
source "$(dirname "$0")/../../scripts/env.sh"
for PAD_TASK_EXEC in blockMesh decomposePar redistributePar mpirun wmake python3; do
  command -v "$PAD_TASK_EXEC" >/dev/null || { echo "Missing dependency: $PAD_TASK_EXEC"; exit 1; }
done
echo "OpenFOAM: $WM_PROJECT_VERSION ($WM_PROJECT_DIR)"
echo "Build: bash actionStudy/scripts/build.sh"
echo "Tests: bash actionStudy/scripts/test.sh parallel"
echo "Plotting needs Python, NumPy and Matplotlib; optional QUICKLB dependencies are isolated by reproduceQuicklb.sh."
