"""Same homogeneous physics in one mesh column reduces duplicated chemistry cost."""
from candidate_screen import run
for dt in [2e-6,1e-6,.5e-6,.25e-6,.125e-6,.0625e-6,.03125e-6]:
    for mode in ['none','conservativeState']:
        run(kind='B',mode=mode,dt=dt,ranks=1,cells=1,tag='_oneColumn',every=0)
