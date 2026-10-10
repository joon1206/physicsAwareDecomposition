"""Stop only a stalled push descended from this project's checkpoint helper."""
import os,signal
from pathlib import Path
marker=str(Path(__file__).with_name('checkpoint.py')).encode();parents={};roots=[]
for directory in Path('/proc').glob('[0-9]*'):
    try:
        args=(directory/'cmdline').read_bytes().split(b'\0')
        parent=int(next(line.split()[1] for line in (directory/'status').read_text().splitlines() if line.startswith('PPid:')))
    except (OSError,StopIteration,ValueError):continue
    pid=int(directory.name);parents[pid]=parent
    if marker in args and b'--push' in args and pid!=os.getpid():roots.append(pid)
for root in roots:
    descendants=[]
    for pid in parents:
        p=parents[pid];visited=set()
        while p in parents and p not in visited:
            if p==root:descendants.append(pid);break
            visited.add(p);p=parents[p]
    for pid in reversed(descendants):
        try:os.kill(pid,signal.SIGTERM)
        except ProcessLookupError:pass
    print('Stopped stalled push children:',len(descendants))
