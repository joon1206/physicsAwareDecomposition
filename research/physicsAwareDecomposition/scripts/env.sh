#!/usr/bin/env bash
PAD_ROOT=$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)
PAD_FOAM_ROOT=${PAD_FOAM_ROOT:-/opt/OpenFOAM/OpenFOAM-v2012}
# OpenFOAM's bashrc contains optional probes that are not errexit-safe on
# repeated initialization. Reuse a matching initialized environment; otherwise
# source in a conditional context and validate the required runtime explicitly.
if [[ ${WM_PROJECT_DIR:-} != "$PAD_FOAM_ROOT" ]] || ! command -v wmake >/dev/null; then
    if source "$PAD_FOAM_ROOT/etc/bashrc" >/dev/null 2>&1; then :; fi
fi
if [[ ${WM_PROJECT_DIR:-} != "$PAD_FOAM_ROOT" ]] || ! command -v wmake >/dev/null; then
    echo "Failed to initialize OpenFOAM at $PAD_FOAM_ROOT" >&2
    return 1
fi
export FOAM_USER_APPBIN="$PAD_ROOT/build/bin"
export FOAM_USER_LIBBIN="$PAD_ROOT/build/lib"
export PATH="$FOAM_USER_APPBIN:$PATH"
export LD_LIBRARY_PATH="$FOAM_USER_LIBBIN:$LD_LIBRARY_PATH"
export OMP_NUM_THREADS=1
