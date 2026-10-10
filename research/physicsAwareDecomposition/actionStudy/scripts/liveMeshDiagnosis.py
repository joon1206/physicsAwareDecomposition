"""Locate observed live mesh differences without changing trial eligibility."""
import json
import math
from caseFactory import ROOT
from mapping import assemble


def main():
    rows = []
    for repeat in range(3):
        candidate = ROOT / f'data/raw/live/heldoutMoving_AM_r{repeat}'
        reference = ROOT / f'data/raw/live/heldoutMoving_A0_r{repeat}'
        for time_name in ['4e-05', '0.00012', '0.0002', '0.00028']:
            norms = {}
            for field in ['T', 'p', 'U', 'h', 'rho', 'chemDeltaT']:
                x, y = [assemble(c, time_name, field, 256)
                        for c in [reference, candidate]]
                differences = [math.sqrt(sum((a-b)**2 for a, b in zip(v, w)))
                               if isinstance(v, tuple) else abs(v-w)
                               for v, w in zip(x, y)]
                norms[field] = max(differences)
            row = dict(repeat=repeat, time=float(time_name), Linf=norms)
            rows.append(row)
            print('MESH LIVE DIAGNOSIS', row, flush=True)
    (ROOT / 'data/processed/live_mesh_diagnosis.json').write_text(json.dumps(
        dict(rows=rows, scope='Historical written-state comparison using retained migration ownership maps; all original live trials remain included and the predefined gate is unchanged.'), indent=2))


if __name__ == '__main__':
    main()
