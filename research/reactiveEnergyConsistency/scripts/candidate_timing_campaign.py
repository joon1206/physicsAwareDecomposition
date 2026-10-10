"""Sequential paired timing trials; no other CFD campaign runs concurrently."""
from candidate_screen import run
matrix=[
    dict(mode='none',dt=1e-6),
    dict(mode='conservativeState',dt=1e-6),
    dict(mode='blockConservative',dt=1e-6,exe='reactingEnergyBlockCandidates'),
    dict(mode='none',dt=1e-6,pc=2),
    dict(mode='none',dt=.5e-6),
    dict(mode='none',dt=.25e-6),
    dict(mode='none',dt=.25e-6,outer=2),
]
for trial in range(3):
    # Rotate the order to avoid giving one construction all early trials.
    for config in matrix[trial:]+matrix[:trial]:
        run(**config,tag=f'_timing{trial+1}',every=0)
