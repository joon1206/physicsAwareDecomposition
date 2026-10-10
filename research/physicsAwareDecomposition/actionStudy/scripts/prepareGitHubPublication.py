"""Capture the committed project subtree for an authenticated Git-data upload."""
import json
import subprocess
from pathlib import Path
from analysis import ROOT

def main():
    repo = Path(__file__).resolve().parents[4]
    prefix = 'research/physicsAwareDecomposition'
    def git(*args):
        return subprocess.check_output(['git', '-C', str(repo), *args])
    files = []
    for entry in git('ls-tree', '-r', '-l', '-z', 'HEAD', '--', prefix).split(b'\0'):
        if not entry:
            continue
        metadata, path = entry.split(b'\t', 1)
        mode, kind, sha, size = metadata.split()
        assert kind == b'blob' and path.decode().startswith(prefix + '/')
        files.append(dict(path=path.decode(), mode=mode.decode(), sha=sha.decode(), bytes=int(size)))
    result = dict(localCommit=git('rev-parse', 'HEAD').decode().strip(),
                  projectTreeSHA=git('rev-parse', 'HEAD:' + prefix).decode().strip(),
                  prefix=prefix, files=files,
                  scope='Only this project subtree overlays the current remote main tree; other remote paths are preserved.')
    destination = ROOT / 'data/raw/github_publication_manifest.json'
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(json.dumps(result, indent=2) + '\n')
    print('READY', len(files), 'files;', result['projectTreeSHA'])

if __name__ == '__main__':
    main()
