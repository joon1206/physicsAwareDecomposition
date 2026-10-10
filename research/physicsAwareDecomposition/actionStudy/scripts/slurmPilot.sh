#!/usr/bin/env bash
# Example only: validate paths/environment and a pilot before increasing scale.
#SBATCH --job-name=pad-action-pilot
#SBATCH --nodes=1
#SBATCH --ntasks=4
#SBATCH --cpus-per-task=1
#SBATCH --time=00:15:00
#SBATCH --mem=4G
set -eo pipefail
: "${PAD_PROJECT_DIR:?Set PAD_PROJECT_DIR to research/physicsAwareDecomposition}"
: "${PAD_ACTION_ROOT:?Set PAD_ACTION_ROOT to a fresh scratch output directory}"
cd "$PAD_PROJECT_DIR"
bash actionStudy/scripts/setup.sh
bash actionStudy/scripts/reproduce.sh small
# Do not turn this into a multi-node claim: the current harness pins local cores.
# A real cluster extension must use allocation-aware placement and validate it.
