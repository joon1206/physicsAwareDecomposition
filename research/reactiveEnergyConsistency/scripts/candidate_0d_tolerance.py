from candidate_screen import run
for dt in [.5e-6,.25e-6,.125e-6,.0625e-6]:
    for mode in ['none','conservativeState']:
        run(kind='B',mode=mode,dt=dt,ranks=1,cells=1,tag='_oneColumn_tight',every=0,ode_rtol=1e-10,ode_atol=1e-16)
