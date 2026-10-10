"""Coupling-tolerance tradeoff, derived in docs/candidates/couplingBudget.md."""
from candidate_screen import run
for tolerance in [1e-2,1e-3,1e-4]:
    for kind,dt in [('Mix',2e-6),('F',1e-6)]:
        run(kind=kind,mode='blockConservative',exe='reactingEnergyBlockCandidates',
            dt=dt,block_tolerance=tolerance,tag=f'_tol{tolerance:g}',every=0)
