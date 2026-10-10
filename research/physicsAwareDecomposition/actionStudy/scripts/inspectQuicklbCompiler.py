"""Scoped non-secret compiler environment diagnostics."""
import os,subprocess
from pathlib import Path
pad=Path(__file__).resolve().parents[2]
env=dict(os.environ)
for key in ['LD_LIBRARY_PATH','LD_PRELOAD','OPAL_PREFIX','MPI_HOME','OMPI_CC','OMPI_CXX','OMPI_FC','OMPI_F77','OMPI_F90']:env.pop(key,None)
for key,value in sorted(env.items()):
    if key.startswith(('OMPI_','OPAL_')) or key in ['FC','FCFLAGS','FFLAGS','F90','F77','CC','CFLAGS','CPPFLAGS','CXXFLAGS','LDFLAGS']:
        print(key,value)
for option in ['--showme','--showme:compile']:
    result=subprocess.run([str(pad/'build/tools/micromamba'),'run','-p',str(pad/'build/quicklbEnv'),'mpifort',option],env=env,text=True,capture_output=True)
    print(option,result.returncode,result.stdout,result.stderr)
