#!/usr/bin/env bash
set -eo pipefail
source "$(dirname "$0")/../../scripts/env.sh"
source "$PAD_ROOT/scripts/compilerEnv.sh"
mkdir -p "$FOAM_USER_LIBBIN"
PAD_TASK_CC_FLAGS=(); PAD_TASK_LD_FLAGS=()
if [[ -f "$PAD_SYSROOT/usr/include/stdio.h" && -d "$PAD_ROOT/build/compilerLib" ]]; then
  PAD_TASK_CC_FLAGS=(--sysroot="$PAD_SYSROOT")
  PAD_TASK_LD_FLAGS=(-B"$PAD_SYSROOT/usr/lib/x86_64-linux-gnu/" -L"$PAD_ROOT/build/compilerLib" -L"$PAD_SYSROOT/usr/lib/x86_64-linux-gnu" -Wl,--rpath-link,"$PAD_SYSROOT/lib/x86_64-linux-gnu:/lib/x86_64-linux-gnu:/usr/lib/x86_64-linux-gnu")
fi
mpicc "${PAD_TASK_CC_FLAGS[@]}" -O2 -std=c99 -D_POSIX_C_SOURCE=200809L -fPIC -c "$PAD_ROOT/actionStudy/scripts/mpiProfile.c" -o "$PAD_ROOT/build/lib/mpiProfile.o"
mpicc -shared "${PAD_TASK_LD_FLAGS[@]}" "$PAD_ROOT/build/lib/mpiProfile.o" -o "$PAD_ROOT/build/lib/libpadMPIProfile.so"
