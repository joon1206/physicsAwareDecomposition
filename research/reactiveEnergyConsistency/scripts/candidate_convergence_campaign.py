from candidate_screen import run
for dt in [.5e-6,.25e-6,.125e-6]:
    run(mode='conservativeState',dt=dt,every=round(4e-6/dt))
run(mode='conservativeState',pc=2,every=4)
run(mode='conservativeState',gauge=1e7,every=4)
for dt in [1e-6,.5e-6,.25e-6]:
    run(kind='B',mode='conservativeState',ranks=1,dt=dt,every=round(4e-6/dt))
    run(kind='B',dt=dt,ranks=1,every=round(4e-6/dt))
