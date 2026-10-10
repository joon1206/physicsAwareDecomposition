#!/usr/bin/env bash
REC_ROOT=$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)
REC_REPO=$(cd "$REC_ROOT/../.." && pwd)
REC_PAD="$REC_REPO/research/physicsAwareDecomposition"
if source /opt/OpenFOAM/OpenFOAM-v2012/etc/bashrc >/dev/null 2>&1; then :; fi
export FOAM_USER_APPBIN="$REC_ROOT/build/bin"
export FOAM_USER_LIBBIN="$REC_ROOT/build/lib"
export PATH="$FOAM_USER_APPBIN:$REC_PAD/build/bin:$PATH"
export LD_LIBRARY_PATH="$FOAM_USER_LIBBIN:$REC_PAD/build/lib:$LD_LIBRARY_PATH"
export OMP_NUM_THREADS=1 PYTHONDONTWRITEBYTECODE=1
export PAD_ACTION_ROOT="$REC_ROOT"
export PYTHONPATH="$REC_PAD/scripts:$REC_PAD/actionStudy/scripts:${PYTHONPATH:-}"
