"""Stop only this project's finishing driver and its current descendants."""
import os,signal,subprocess,time
from pathlib import Path
target=str(Path(__file__).with_name('finish.py'))
rows=[]
for line in subprocess.check_output(['ps','-eo','pid,ppid,args'],text=True).splitlines()[1:]:
    parts=line.strip().split(None,2)
    if len(parts)==3:rows.append((int(parts[0]),int(parts[1]),parts[2]))
roots=[pid for pid,ppid,cmd in rows if cmd in ['python3 '+target,'python3 '+target+' --no-wait']]
owned=set(roots)
while True:
    new={pid for pid,ppid,cmd in rows if ppid in owned}-owned
    if not new:break
    owned|=new
for pid in sorted(owned-set(roots),reverse=True):
    try:os.kill(pid,signal.SIGTERM)
    except ProcessLookupError:pass
for pid in roots:
    try:os.kill(pid,signal.SIGTERM)
    except ProcessLookupError:pass
print('Stopped only owned finish tree:',sorted(owned))
