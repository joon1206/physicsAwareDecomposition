#!/usr/bin/env bash
# Standalone compiler/MPI environment; never mixes it with OpenFOAM's MPI.
set -eo pipefail
PAD_TASK_ROOT=$(cd "$(dirname "$0")/../.." && pwd)
PAD_TASK_OUTPUT=${PAD_ACTION_ROOT:-$PAD_TASK_ROOT/actionStudy}
python3 "$(dirname "$0")/bootstrapQuicklb.py"
PAD_TASK_ENV="$PAD_TASK_ROOT/build/quicklbEnv"
PAD_TASK_MAMBA="$PAD_TASK_ROOT/build/tools/micromamba"
export MAMBA_ROOT_PREFIX="$PAD_TASK_ROOT/build/mambaHome"
export SETUPTOOLS_USE_DISTUTILS=stdlib
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MPLBACKEND=Agg
# finish.py may inherit an initialized OpenFOAM shell. Remove its dynamic
# loader and wrapper overrides before entering the independent conda MPI.
unset LD_LIBRARY_PATH LD_PRELOAD OPAL_PREFIX OPAL_LIBDIR OPAL_DATADIR OPAL_BINDIR OPAL_INCLUDEDIR OPAL_EXEC_PREFIX MPI_HOME
unset OMPI_CC OMPI_CXX OMPI_FC OMPI_F77 OMPI_F90
PAD_TASK_OPERATION=create
if [ -f "$PAD_TASK_ENV/conda-meta/history" ]; then PAD_TASK_OPERATION=install; fi
"$PAD_TASK_MAMBA" "$PAD_TASK_OPERATION" -y -p "$PAD_TASK_ENV" -c conda-forge \
  python=3.11 numpy=1.26 scipy=1.11 mpi4py=3.1 openmpi=4.1 \
  cmake=3.27 make gcc_linux-64=13 gfortran_linux-64=13 setuptools=59.8 matplotlib=3.8
PAD_TASK_SOURCE=$(find "$PAD_TASK_ROOT/vendor/quicklb" -mindepth 1 -maxdepth 1 -type d | head -n 1)
cd "$PAD_TASK_SOURCE"
# Upstream's --inplace copy concatenates two absolute paths. Its ordinary
# build_ext path stays relative and builds the same unmodified library.
"$PAD_TASK_MAMBA" run -p "$PAD_TASK_ENV" python setup.py build_ext
mkdir -p "$PAD_TASK_OUTPUT/data/raw/quicklb" "$PAD_TASK_OUTPUT/docs"
"$PAD_TASK_MAMBA" list -p "$PAD_TASK_ENV" --explicit > "$PAD_TASK_OUTPUT/docs/quicklb_environment.txt"
PAD_TASK_EXTENSION_DIR=$(find "$PAD_TASK_SOURCE/build" -mindepth 1 -maxdepth 1 -type d -name 'lib.*' | head -n 1)
test -n "$PAD_TASK_EXTENSION_DIR"
export PYTHONPATH="$PAD_TASK_SOURCE:$PAD_TASK_EXTENSION_DIR"
# Two-step pilot verifies communication and bounds cost before longer runs.
for PAD_TASK_ALGORITHM in NONE GREEDY SORT SORT2; do
  "$PAD_TASK_MAMBA" run -p "$PAD_TASK_ENV" mpirun --bind-to core --map-by core --nooversubscribe -np 4 python \
    "$PAD_TASK_ROOT/actionStudy/scripts/quicklbDemo.py" --algorithm "$PAD_TASK_ALGORITHM" --steps 2 --repeat 99 --output "$PAD_TASK_OUTPUT/data/raw/quicklb"
done
for PAD_TASK_REPEAT in 0 1 2; do
  for PAD_TASK_ALGORITHM in NONE SORT2 GREEDY SORT; do
    "$PAD_TASK_MAMBA" run -p "$PAD_TASK_ENV" mpirun --bind-to core --map-by core --nooversubscribe -np 4 python \
      "$PAD_TASK_ROOT/actionStudy/scripts/quicklbDemo.py" --algorithm "$PAD_TASK_ALGORITHM" --steps 10 --repeat "$PAD_TASK_REPEAT" --output "$PAD_TASK_OUTPUT/data/raw/quicklb"
  done
done
