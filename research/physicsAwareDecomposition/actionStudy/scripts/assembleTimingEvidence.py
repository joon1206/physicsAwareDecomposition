"""Verify and reassemble the portable archive without overwriting existing data."""
import hashlib
import json
from pathlib import Path
from analysis import ROOT

def assemble(folder=None):
    folder = Path(folder) if folder is not None else ROOT / 'data/evidence'
    manifest = json.loads((folder / 'parts.json').read_text())
    assert manifest['archive'] == 'timing_evidence.tar.gz'
    archive = folder / manifest['archive']
    if archive.exists():
        if hashlib.sha256(archive.read_bytes()).hexdigest() != manifest['archiveSHA256']:
            raise RuntimeError('Existing archive differs; refusing to overwrite it')
        return archive
    temporary = folder / 'timing_evidence.assembling'
    digest = hashlib.sha256()
    count = 0
    with temporary.open('xb') as output:
        for part in manifest['parts']:
            path = folder / part['path']
            assert path.parent == folder and path.name.startswith('timing_evidence.tar.gz.part')
            content = path.read_bytes()
            assert len(content) == part['bytes'] and hashlib.sha256(content).hexdigest() == part['SHA256']
            output.write(content)
            digest.update(content)
            count += len(content)
    assert count == manifest['archiveBytes'] and digest.hexdigest() == manifest['archiveSHA256']
    temporary.replace(archive)
    return archive

if __name__ == '__main__':
    print('VERIFIED', assemble())
