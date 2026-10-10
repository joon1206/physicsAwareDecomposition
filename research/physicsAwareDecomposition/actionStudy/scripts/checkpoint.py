"""Commit only this project's authorized changes; optionally push its branch."""
import argparse,re,subprocess,os,signal
from pathlib import Path
PAD=Path(__file__).resolve().parents[2]
p=argparse.ArgumentParser();p.add_argument('--push',action='store_true');p.add_argument('--message',default='Checkpoint reactive-action study and reproducible evidence');args=p.parse_args()
subprocess.run(['git','add',str(PAD)],cwd=PAD,check=True)
changed=subprocess.check_output(['git','diff','--cached','--name-only','--',str(PAD)],cwd=PAD,text=True).strip()
if changed:
    subprocess.run(['git','commit','--quiet','--only',str(PAD),'-m',args.message],cwd=PAD,check=True)
    print('COMMITTED',subprocess.check_output(['git','rev-parse','HEAD'],cwd=PAD,text=True).strip(),flush=True)
if args.push:
    env=dict(os.environ,GIT_TERMINAL_PROMPT='0',GCM_INTERACTIVE='never',GIT_SSH_COMMAND='ssh -o BatchMode=yes -o ConnectTimeout=15')
    process=subprocess.Popen(['git','push','-u','origin','HEAD'],cwd=PAD,env=env,text=True,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,start_new_session=True)
    try:output,_=process.communicate(timeout=90)
    except subprocess.TimeoutExpired:
        os.killpg(process.pid,signal.SIGTERM);output,_=process.communicate(timeout=10)
        output+='\nPush timed out after 90 seconds; local commits retained.\n'
    safe=re.sub(r'(?<=://)[^/\s@]+:[^/\s@]+@','[redacted]@',output)
    safe=re.sub(r'(ghp_|github_pat_)[A-Za-z0-9_]+','[redacted]',safe)
    print(safe,flush=True)
    (PAD/'actionStudy/docs/push_status.txt').write_text(f'exitCode={process.returncode}\n'+safe)
    if process.returncode:raise SystemExit(process.returncode)
