from candidate_screen import run
for mode in ['none','conservativeState','blockConservative']:
    run(mode=mode,dt=1e-6,profile=True,tag='_mpi',every=8,
        exe='reactingEnergyBlockCandidates' if mode=='blockConservative' else 'reactingEnergyCandidates')
run(dt=1e-6,pc=2,profile=True,tag='_mpi',every=8)
