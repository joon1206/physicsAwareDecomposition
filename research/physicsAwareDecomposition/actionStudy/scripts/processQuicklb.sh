#!/usr/bin/env bash
set -eo pipefail
PAD_TASK_ROOT=$(cd "$(dirname "$0")/../.." && pwd)
unset LD_LIBRARY_PATH LD_PRELOAD OPAL_PREFIX OPAL_LIBDIR OPAL_DATADIR OPAL_BINDIR OPAL_INCLUDEDIR OPAL_EXEC_PREFIX MPI_HOME
"$PAD_TASK_ROOT/build/quicklbEnv/bin/python" "$(dirname "$0")/processQuicklb.py"
