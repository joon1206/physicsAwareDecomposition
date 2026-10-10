#!/usr/bin/env bash
# Sequential local study. --smoke is the default; --full retains all cases.
source "$(dirname "$0")/env.sh"
set -eo pipefail
mode="${1:---smoke}"
case "$mode" in --smoke|--full) ;; *) echo "Usage: $0 [--smoke|--full]"; exit 2;; esac
export PAD_OUTPUT_ROOT="${PAD_OUTPUT_ROOT:-$PAD_ROOT/reproductions/full_$(date -u +%Y%m%dT%H%M%SZ)}"
bash "$PAD_ROOT/scripts/smokeTest.sh"
if [ "$mode" = --smoke ]; then exit 0; fi
python3 "$PAD_ROOT/scripts/study.py" train
python3 "$PAD_ROOT/scripts/sensitivity.py"
python3 "$PAD_ROOT/scripts/synthetic.py" --pilot
python3 "$PAD_ROOT/scripts/synthetic.py"
python3 "$PAD_ROOT/scripts/syntheticRuntime.py" --pilot
python3 "$PAD_ROOT/scripts/syntheticRuntime.py"
python3 "$PAD_ROOT/scripts/syntheticRuntime.py" --pilot --communication
python3 "$PAD_ROOT/scripts/syntheticRuntime.py" --communication
python3 "$PAD_ROOT/scripts/study.py" reactive
python3 "$PAD_ROOT/scripts/tightStudy.py" --pilot
python3 "$PAD_ROOT/scripts/tightStudy.py"
python3 "$PAD_ROOT/scripts/tightStudy.py" --no-chemistry
python3 "$PAD_ROOT/scripts/overhead.py"
python3 "$PAD_ROOT/scripts/transientStudy.py"
python3 "$PAD_ROOT/scripts/postprocessThermo.py"
python3 "$PAD_ROOT/scripts/analyzeTiming.py"
python3 "$PAD_ROOT/scripts/analyzeTiming.py" --campaign reactiveTight --output-dir data/processed/tight
python3 "$PAD_ROOT/scripts/analyzeTiming.py" --campaign reactiveNoChem --output-dir data/processed/noChem
python3 "$PAD_ROOT/scripts/analyzeAdditional.py"
python3 "$PAD_ROOT/scripts/summarizeEvidence.py"
python3 "$PAD_ROOT/scripts/generateTables.py"
python3 "$PAD_ROOT/scripts/writeReport.py"
if python3 -c 'import matplotlib' >/dev/null 2>&1; then
    python3 "$PAD_ROOT/scripts/generatePlots.py"
else
    echo "Install scripts/requirements-plot.txt or use scripts/reproduceFigures.ps1 to generate figures."
fi
python3 "$PAD_ROOT/scripts/verifyDeliverables.py"
python3 "$PAD_ROOT/scripts/indexArtifacts.py"
echo "MEASURED full reproduction evidence: $PAD_OUTPUT_ROOT"
