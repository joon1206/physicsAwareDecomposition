"""Stop only this project's waiting finish driver to load added phases."""
import os,signal,subprocess
from pathlib import Path
target=str(Path(__file__).with_name('finish.py'))
lines=subprocess.check_output(['ps','-eo','pid,args'],text=True).splitlines()
for line in lines:
    parts=line.strip().split(None,1)
    if len(parts)==2 and parts[1] in ['python3 '+target,'/usr/bin/python3 '+target]:
        os.kill(int(parts[0]),signal.SIGTERM);print('Stopped project finish waiter',parts[0])
