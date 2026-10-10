#!/usr/bin/env bash
set -euo pipefail
cd /home/joon1206/research/ForFun/research/physicsAwareDecomposition
bash actionStudy/scripts/run.sh splitTimingEvidence.py
bash actionStudy/scripts/run.sh assembleTimingEvidence.py
bash actionStudy/scripts/run.sh captureProvenance.py
bash actionStudy/scripts/run.sh qualityControl.py
git -C ../.. rm --cached -- research/physicsAwareDecomposition/actionStudy/data/evidence/timing_evidence.tar.gz
git -C ../.. add -- research/physicsAwareDecomposition
git -C ../.. commit -m "Package complete timing evidence as verified portable volumes"
bash actionStudy/scripts/run.sh prepareGitHubPublication.py
