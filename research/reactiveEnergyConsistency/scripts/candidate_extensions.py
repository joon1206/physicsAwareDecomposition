"""Gauge/variable-composition falsification and stronger simple competitors."""
from candidate_screen import run
for mode in ['none','localInternal','scalarDensity']:
    run(kind='Mix',mode=mode,every=4)
    if mode!='none':run(mode=mode,gauge=1e7,every=4)
for pc in [2,4]:run(pc=pc,every=4)
run(outer=2,every=4)
run(outer=2,dt=.25e-6,every=8)
