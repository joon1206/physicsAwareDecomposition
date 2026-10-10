"""Verify and restore the complete archived research evidence into this clone."""
from pathlib import Path
import argparse,hashlib,io,json,tarfile
ROOT=Path(__file__).resolve().parents[1]
class PartsReader:
 def __init__(self,parts):self.parts=iter(parts);self.current=None
 def read(self,n=-1):
  if n<0:raise ValueError('Streaming reads must be bounded')
  output=[];remaining=n
  while remaining:
   if self.current is None:
    try:self.current=next(self.parts).open('rb')
    except StopIteration:break
   block=self.current.read(remaining)
   if block:output.append(block);remaining-=len(block)
   else:self.current.close();self.current=None
  return b''.join(output)
 def close(self):
  if self.current:self.current.close()
def verify(record):
 whole=hashlib.sha256();paths=[]
 for part in record['parts']:
  path=ROOT/part['path'];h=hashlib.sha256();size=0
  with path.open('rb') as stream:
   for block in iter(lambda:stream.read(1024*1024),b''):h.update(block);whole.update(block);size+=len(block)
  if h.hexdigest()!=part['sha256'] or size!=part['bytes']:raise RuntimeError('Changed volume '+str(path))
  paths.append(path)
 if whole.hexdigest()!=record['archiveSHA256']:raise RuntimeError('Changed assembled archive '+record['name'])
 return paths
def main():
 parser=argparse.ArgumentParser();parser.add_argument('--verify-only',action='store_true');parser.add_argument('--archive',action='append');args=parser.parse_args()
 records=json.loads((ROOT/'evidence/archives.json').read_text())['archives']
 for record in records:
  if args.archive and record['name'] not in args.archive:continue
  paths=verify(record);print('Verified',record['name'],len(paths),'volumes',flush=True)
  if args.verify_only:continue
  stream=PartsReader(paths);count=0
  try:
   with tarfile.open(fileobj=stream,mode='r|gz') as archive:
    for member in archive:
     target=ROOT/member.name
     if not target.resolve().is_relative_to(ROOT):raise RuntimeError('Archive path escapes clone')
     if member.isfile() and target.exists():
      if target.is_symlink():raise RuntimeError('Existing symbolic file '+str(target))
      with archive.extractfile(member) as incoming,target.open('rb') as existing:
       while True:
        a=incoming.read(1024*1024);b=existing.read(1024*1024)
        if a!=b:raise RuntimeError('Refusing to overwrite different existing file '+str(target))
        if not a:break
     else:archive.extract(member,ROOT,filter='data')
     count+=1
   print('Restored',record['name'],count,'entries',flush=True)
  finally:stream.close()
if __name__=='__main__':main()