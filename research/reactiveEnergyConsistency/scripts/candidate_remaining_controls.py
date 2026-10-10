"""Missing same-dt outer baseline and loose-block negative/count controls."""
from pathlib import Path
import json
from candidate_screen import run
for trial in [1,2,3]:
    case=run(kind='F',mode='none',dt=1e-6,outer=2,every=0,tag=f'_timing{trial}')
    if (case/'failure.json').exists():break
run(kind='F',mode='blockConservative',dt=2e-6,exe='reactingEnergyBlockCandidates',
    block_tolerance=1e-4,every=0,tag='_tol0.0001_negative')
run(kind='F',mode='blockConservative',dt=1e-6,exe='reactingEnergyBlockCandidates',
    block_tolerance=1e-4,every=0,profile=True,tag='_tol0.0001_mpi')
