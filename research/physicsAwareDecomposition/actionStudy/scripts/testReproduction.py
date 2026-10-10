"""Exercise the documented small profile in a fresh, retained output tree."""
import datetime
import json
import os
import tempfile
import time
from pathlib import Path
from caseFactory import ROOT, command


def main():
    scripts = Path(__file__).resolve().parent
    destination = Path(tempfile.mkdtemp(prefix='pad-action-small-reproduction-'))
    environment = dict(os.environ, PAD_ACTION_ROOT=str(destination))
    log = ROOT / 'data/raw/build/smallReproduction.log'
    start = time.perf_counter()
    if log.exists():
        log.rename(log.with_name('smallReproductionRejected_' + str(time.time_ns()) + '.log'))
    wall = command(['bash', scripts / 'reproduce.sh', 'small'], scripts,
                   log, timeout=600, env=environment)
    processed = destination / 'data/processed'
    raw = json.loads((processed / 'oracle_raw.json').read_text())
    gates = json.loads((processed / 'oracle_validation.json').read_text())
    assert len(raw) == 8 and len(gates) == 6
    assert {r['regime'] for r in raw} == {'persistent', 'transportDominated'}
    assert {r['action'] for r in raw} == {'A0', 'AC', 'AM', 'AH'}
    assert all(g['pass_'] and not g['omittedOptionalFields'] for g in gates)
    assert all(r['normalExit'] and r['writeProtocol'].startswith(
        'state-preserving physical endpoint v3') for r in raw)
    for r in raw:
        assert abs(r['totalWall'] - r['solverWall'] - r['decisionWall']
                   - r['migrationWall']) < 1e-8
    record = dict(passed=True, timestamp=datetime.datetime.now(
        datetime.timezone.utc).isoformat(), outputDirectory=str(destination),
        command='PAD_ACTION_ROOT=<fresh directory> bash actionStudy/scripts/reproduce.sh small',
        subprocessWall=wall, totalVerificationWall=time.perf_counter() - start,
        trials=len(raw), gates=len(gates), log=str(log),
        scope='Fresh small profile, all four actions and native physical endpoint checks; full campaign evidence audited separately.')
    (ROOT / 'docs/reproduction_test.json').write_text(json.dumps(record, indent=2))
    print('PASSED documented small reproduction:', record, flush=True)


if __name__ == '__main__':
    main()
