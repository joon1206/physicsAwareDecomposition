"""Reproduce the rejected mesh endpoint and test bounded numerical controls."""
import json
import re
from caseFactory import ROOT, set_control, solve, latest_time
from oracle import copy_checkpoint
from mapping import canonical_directory
from validation import numerical_gate


def controls_for(failure):
    assert failure['policy'] == 'AM', 'A non-mesh rejection requires separate investigation.'
    rejected = ROOT / failure['path']
    reference = rejected.with_name(rejected.name.replace('_AM_', '_A0_'))
    info = json.loads((reference / 'case.json').read_text())
    fields = ['T', 'p', 'U', 'Qdot'] + info['species']
    initial_gate = numerical_gate(*[canonical_directory(c, '0.0002', fields, 256)
                                    for c in [reference, rejected]], info)
    assert initial_gate['pass_'], 'The diagnostic inputs must pass the original checkpoint gate.'
    records = []
    specs = [('original', 2e-6, 40, False), ('fineGlobalStep', .25e-6, 320, False),
             ('tightODE', 2e-6, 40, True)]
    for label, dt, steps, tighten in specs:
        cases = []
        for arm, source in [('A0', reference), ('rejectedPartition', rejected)]:
            target = ROOT / f'data/raw/liveMeshFollowup/{rejected.name}_{label}_{arm}'
            if not (target / 'manifest.json').exists():
                copy_checkpoint(source, target, '0.0002')
                set_control(target, start=.0002, dt=dt, steps=steps, restart_state=True)
                if tighten:
                    path = target / 'constant/chemistryProperties'
                    text = path.read_text()
                    text = re.sub(r'absTol\s+[^;]+;', 'absTol 1e-14;', text)
                    text = re.sub(r'relTol\s+[^;]+;', 'relTol 1e-7;', text)
                    path.write_text(text)
                wall = solve(target, 4, exe='reactingFoamPADRestart', timeout=300)
                (target / 'manifest.json').write_text(json.dumps(dict(
                    label=label, arm=arm, dt=dt, steps=steps, solverWall=wall,
                    source=str(source.relative_to(ROOT)), checkpoint=.0002,
                    scope='diagnostic only; fixed observed partition, no trial replacement, model tuning or tolerance relaxation'), indent=2))
            cases.append(target)
        end = latest_time(cases[0], True)
        gate = numerical_gate(*[canonical_directory(c, end, fields, 256)
                                for c in cases], info)
        reproduction = numerical_gate(*[canonical_directory(c, end, fields, 256)
                                         for c in [rejected, cases[1]]], info) if label == 'original' else None
        record = dict(rejectedTrial=failure['path'],label=label, dt=dt, steps=steps, tightODE=tighten,inputGate=initial_gate,
                      gate=gate, originalEndpointReproduction=reproduction)
        records.append(record)
        print('LIVE MESH CONTROL', label, 'T Linf', gate['fields']['T']['Linf'],
              'gate', gate['pass_'], flush=True)
    return records


def main():
    # The independent sweeps exposed pressure/time coupling. Keep these
    # matched controls sequential with the other numerical diagnostics.
    from conservationCouplingFollowup import main as coupled_controls
    coupled_controls()
    live = json.loads((ROOT / 'data/processed/live.json').read_text())
    failures = [r for r in live if not r.get('gate', {'pass_': True})['pass_']]
    records = [control for failure in failures for control in controls_for(failure)]
    result = dict(rejectedTrials=[r['path'] for r in failures], controls=records,
                  originalTrialsChanged=False, gateThresholdChanged=False,
                  interpretation='Original partition and checkpoint replay tests reproducibility; finer physical time and tighter ODE controls test numerical sensitivity. They do not substitute for the failed original trajectory or establish an isolated surface-flux root cause.')
    (ROOT / 'data/processed/live_mesh_followup.json').write_text(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
