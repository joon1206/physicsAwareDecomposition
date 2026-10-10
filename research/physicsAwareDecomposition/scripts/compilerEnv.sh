#!/usr/bin/env bash
# Source after env.sh. Native OpenFOAM compiler configuration is the default;
# use the self-contained adapter only when the recorded user sysroot is present.
export PAD_SYSROOT=${PAD_SYSROOT:-"$HOME/local"}
if [[ -n "${PAD_COMPILER_PATH:-}" ]]; then
  export PATH="$PAD_COMPILER_PATH:$PATH"
elif [[ -f "$PAD_SYSROOT/usr/include/stdio.h" && -x "$PAD_FOAM_ROOT/ThirdParty/platforms/linux64/gcc-6.3.0/bin/g++" ]]; then
  mkdir -p "$PAD_ROOT/build/compilerLib"
  PAD_TASK_LINKLIB="$PAD_SYSROOT/lib/x86_64-linux-gnu"
  PAD_TASK_DEVLIB="$PAD_SYSROOT/usr/lib/x86_64-linux-gnu"
  printf 'OUTPUT_FORMAT(elf64-x86-64)\nGROUP ( %s/libc.so.6 %s/libc_nonshared.a AS_NEEDED ( %s/ld-linux-x86-64.so.2 ) )\n' "$PAD_TASK_LINKLIB" "$PAD_TASK_DEVLIB" "$PAD_TASK_LINKLIB" > "$PAD_ROOT/build/compilerLib/libc.so"
  printf 'GROUP ( %s/libpthread.so.0 )\n' "$PAD_TASK_LINKLIB" > "$PAD_ROOT/build/compilerLib/libpthread.so"
  printf 'GROUP ( %s/libdl.so.2 )\n' "$PAD_TASK_LINKLIB" > "$PAD_ROOT/build/compilerLib/libdl.so"
  printf 'GROUP ( %s/libm.so.6 AS_NEEDED ( %s/libmvec.so.1 ) )\n' "$PAD_TASK_LINKLIB" "$PAD_TASK_LINKLIB" > "$PAD_ROOT/build/compilerLib/libm.so"
  printf 'GROUP ( %s/librt.so.1 %s/libpthread.so.0 )\n' "$PAD_TASK_LINKLIB" "$PAD_TASK_LINKLIB" > "$PAD_ROOT/build/compilerLib/librt.so"
  chmod +x "$PAD_ROOT/tools/wrappers/g++"
  export PATH="$PAD_ROOT/tools/wrappers:$PAD_SYSROOT/usr/bin:$PATH"
fi
unset C_INCLUDE_PATH CPLUS_INCLUDE_PATH CPATH
