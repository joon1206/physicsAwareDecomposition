#!/usr/bin/env bash
# Only project-owned wmake outputs; execute after all timed jobs finish.
set -eo pipefail
source "$(dirname "$0")/../../scripts/env.sh"
source "$PAD_ROOT/scripts/compilerEnv.sh"
for PAD_TASK_TARGET in src/costChemistry src/stuttgartV2012 applications/reactingFoamPAD applications/padNativeInventory applications/padWorkloadFoam applications/redistributeParPAD; do
  cd "$PAD_ROOT/$PAD_TASK_TARGET"
  wclean
done
bash "$PAD_ROOT/actionStudy/scripts/build.sh"
bash "$PAD_ROOT/actionStudy/scripts/buildInventory.sh"
bash "$PAD_ROOT/actionStudy/scripts/buildMPI.sh"
bash "$PAD_ROOT/actionStudy/scripts/buildRedistributor.sh"
cd "$PAD_ROOT/applications/padWorkloadFoam"
wmake > "$PAD_ROOT/actionStudy/data/raw/build/padWorkloadFoam.log" 2>&1
if [ -d "$PAD_ROOT/build/restartSolver/Make" ]; then
  cd "$PAD_ROOT/build/restartSolver"
  wclean
fi
bash "$PAD_ROOT/actionStudy/scripts/buildRestart.sh"
bash "$PAD_ROOT/actionStudy/scripts/test.sh" parallel
