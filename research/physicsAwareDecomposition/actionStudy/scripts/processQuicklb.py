"""Audit third-party-library execution and paired Gray–Scott endpoints."""
import json,os
from pathlib import Path
import numpy as np
ROOT=Path(os.environ.get('PAD_ACTION_ROOT',Path(__file__).resolve().parents[1]))
def main():
    folder=ROOT/'data/raw/quicklb';rows=[json.loads(p.read_text()) for p in sorted(folder.glob('*.json'))]
    gates=[]
    for row in rows:
        path=folder/f"{row['algorithm']}_p{row['ranks']}_r{row['repeat']}_n{row['steps']}.npz"
        reference=folder/f"NONE_p{row['ranks']}_r{row['repeat']}_n{row['steps']}.npz"
        assert path.exists() and reference.exists(), (path, reference)
        with np.load(path) as x,np.load(reference) as y:
            norms={k:float(np.max(np.abs(x[k]-y[k]))) for k in x.files if k in y.files and np.issubdtype(x[k].dtype,np.number)}
            finite=all(np.isfinite(x[k]).all() for k in x.files if np.issubdtype(x[k].dtype,np.number))
        gates.append(dict(algorithm=row['algorithm'],repeat=row['repeat'],Linf=norms,passed=finite and bool(norms) and max(norms.values())<1e-8))
    result=dict(passed=len(rows)==16 and all(g['passed'] for g in gates),gates=gates,tolerance=1e-8,scope='same-step-count paired Gray–Scott state; standalone library kernel, not INCA CFD reproduction')
    (ROOT/'data/processed/quicklb.json').write_text(json.dumps(rows,indent=2))
    (ROOT/'data/processed/quicklb_validation.json').write_text(json.dumps(result,indent=2))
    print('QUICKLB',len(rows),'runs; gate:',result['passed'])
    if not result['passed']:raise RuntimeError('Third-party library field validation failed')
if __name__=='__main__':main()
