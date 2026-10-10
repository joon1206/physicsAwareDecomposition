"""Use the host Git credential helper when WSL has no GitHub credentials."""
import os,re,subprocess
from pathlib import Path
PAD=Path(__file__).resolve().parents[2]
if os.name!='nt':raise SystemExit('Run with host Windows Python; no credential values are printed.')
git='C:/Program Files/Git/cmd/git.exe'
env=dict(os.environ,GIT_TERMINAL_PROMPT='0',GCM_INTERACTIVE='Never',GIT_OPTIONAL_LOCKS='0')
process=subprocess.Popen([git,'-c','safe.directory='+PAD.parents[1].as_posix(),'-C',str(PAD),'push','-u','origin','HEAD'],env=env,
    text=True,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,creationflags=subprocess.CREATE_NO_WINDOW)
try:output,_=process.communicate(timeout=90)
except subprocess.TimeoutExpired:
    subprocess.run(['taskkill','/PID',str(process.pid),'/T','/F'],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
    output,_=process.communicate(timeout=10);output+='\nHost push timed out; local commits retained.\n'
output=re.sub(r'(?<=://)[^/\s@]+:[^/\s@]+@','[redacted]@',output)
output=re.sub(r'(ghp_|github_pat_)[A-Za-z0-9_]+','[redacted]',output)
(PAD/'actionStudy/docs/native_push_status.txt').write_text(f'exitCode={process.returncode}\n'+output)
print(output)
raise SystemExit(process.returncode)
