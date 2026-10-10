from candidate_screen import run
for kind in ['A','B','Mix','F']:
    run(kind=kind,mode='conservativeState',ranks=1 if kind in ['A','B'] else 4,steps=20 if kind=='A' else None,every=4)
run(mode='conservativeState',dt=1e-6,every=8)
run(kind='Mix',mode='conservativeState',gauge=1e7,every=4)
