from candidate_screen import run
for dt in [.5e-6,.25e-6,.125e-6]:
    run(mode='blockConservative',exe='reactingEnergyBlockCandidates',dt=dt,every=round(4e-6/dt))
run(kind='Mix',mode='blockConservative',exe='reactingEnergyBlockCandidates',gauge=1e7,every=4)
run(mode='blockConservative',exe='reactingEnergyBlockCandidates',dt=1e-6,gauge=1e7,every=8)
