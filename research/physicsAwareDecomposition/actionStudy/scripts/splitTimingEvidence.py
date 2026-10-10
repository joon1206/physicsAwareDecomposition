"""Lossless small Git objects for the existing checksummed timing archive."""
import hashlib
import json
from analysis import ROOT

def main():
    folder = ROOT / 'data/evidence'
    archive = folder / 'timing_evidence.tar.gz'
    evidence = json.loads((folder / 'manifest.json').read_text())
    assert hashlib.sha256(archive.read_bytes()).hexdigest() == evidence['archiveSHA256']
    parts = []
    with archive.open('rb') as stream:
        while content := stream.read(4 * 1024 * 1024):
            name = f'timing_evidence.tar.gz.part{len(parts):03d}'
            path = folder / name
            if not path.exists() or path.read_bytes() != content:
                path.write_bytes(content)
            parts.append(dict(path=name, bytes=len(content), SHA256=hashlib.sha256(content).hexdigest()))
    result = dict(archive=archive.name, archiveBytes=archive.stat().st_size,
                  archiveSHA256=evidence['archiveSHA256'], parts=parts,
                  scope='Lossless transport volumes; archive contents and scientific data unchanged.')
    (folder / 'parts.json').write_text(json.dumps(result, indent=2) + '\n')
    print('SPLIT', len(parts), 'volumes;', result['archiveBytes'], 'bytes')

if __name__ == '__main__':
    main()
