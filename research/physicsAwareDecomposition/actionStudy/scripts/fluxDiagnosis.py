"""Compare mapped face-flux divergence and canonical mesh coordinates."""
import json
from caseFactory import ROOT,PAD,command
from oracle import copy_checkpoint
from mapping import assemble


def main():
    command(['bash',PAD/'actionStudy/scripts/buildFluxAudit.sh'],PAD,
            ROOT/'data/raw/build/fluxBuildDriver.log',timeout=300)
    records=[]
    fields=['padDivPhi','padDivReconstructedPhi','padCellX','padCellY']
    for repeat in range(3):
        arrays=[]
        for action in ['A0','AM']:
            source=ROOT/f'data/raw/live/heldoutMoving_{action}_r{repeat}'
            target=ROOT/f'data/raw/fluxDiagnosis/{action}_r{repeat}'
            if not (target/'manifest.json').exists():
                copy_checkpoint(source,target,'0.0002')
                command(['mpirun','--bind-to','core','--map-by','core','--nooversubscribe','-np','4','padFluxAudit','-parallel','-time','0.0002'],target,target/'fluxAudit.log')
                (target/'manifest.json').write_text(json.dumps(dict(source=str(source.relative_to(ROOT)),checkpoint=.0002,scope='Untimed copied-state flux and geometry diagnosis; original cases unchanged.')))
            arrays.append({field:assemble(target,'0.0002',field,256) for field in fields})
        norms={field:max(abs(a-b) for a,b in zip(arrays[0][field],arrays[1][field])) for field in fields}
        records.append(dict(repeat=repeat,Linf=norms));print('FLUX DIAGNOSIS',repeat,norms,flush=True)
    (ROOT/'data/processed/flux_diagnosis.json').write_text(json.dumps(dict(records=records,
        scope='Stored mass-flux divergence versus divergence reconstructed from equivalent cell rho/U, plus canonical cell coordinates. A mismatch in the stored flux with matching reconstructed flux/geometry localizes a mapped surface-state error; it does not by itself supply a corrected migration algorithm.'),indent=2))


if __name__=='__main__':main()
