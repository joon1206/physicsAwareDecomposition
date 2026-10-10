from candidate_screen import run
for kind in ['A','B','Mix','F']:
    run(kind=kind,mode='speciesFlux',ranks=1 if kind in ['A','B'] else 4,steps=20 if kind=='A' else None,every=4)
run(mode='speciesFlux',dt=1e-6,every=8)
# Verify EOS refresh fix independently of the rejected v1 energy-only result.
for mode in ['localInternal','scalarDensity']:
    run(mode=mode,every=4,tag='_EOS2')
run(kind='Mix',mode='speciesFlux',gauge=1e7,every=4)
