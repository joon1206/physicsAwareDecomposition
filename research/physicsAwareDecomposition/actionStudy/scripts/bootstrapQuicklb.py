"""Fetch pinned small public prerequisites into project-owned directories."""
import hashlib,io,json,os,tarfile,urllib.request,zipfile
from pathlib import Path
PAD=Path(__file__).resolve().parents[2];ROOT=Path(os.environ.get('PAD_ACTION_ROOT',PAD/'actionStudy'))
def get(url):
    with urllib.request.urlopen(urllib.request.Request(url,headers={'User-Agent':'reactive-action-oracle-reproduction/1.0'}),timeout=45) as response:return response.read()
def main():
    metadata=[];tools=PAD/'build/tools';tools.mkdir(parents=True,exist_ok=True)
    binary=tools/'micromamba'
    if not binary.exists():
        url='https://micro.mamba.pm/api/micromamba/linux-64/2.9.0';payload=get(url)
        with tarfile.open(fileobj=io.BytesIO(payload)) as archive:
            member=archive.getmember('bin/micromamba');assert member.isfile()
            binary.write_bytes(archive.extractfile(member).read());binary.chmod(0o755)
        metadata.append(dict(component='micromamba 2.9.0 linux-64',URL=url,SHA256=hashlib.sha256(payload).hexdigest()))
    vendor=PAD/'vendor/quicklb';vendor.mkdir(parents=True,exist_ok=True)
    if not any(p.is_dir() and (p/'setup.py').exists() for p in vendor.iterdir()):
        url='https://zenodo.org/api/records/6598303'
        try:
            record=json.loads(get(url));file=next(f for f in record['files'] if f['key'].endswith('.zip'))
            url=file['links']['self'];payload=get(url)
            if file['checksum'].startswith('md5:'):assert hashlib.md5(payload).hexdigest()==file['checksum'].split(':')[1]
        except (OSError,ValueError,KeyError,StopIteration) as error:
            metadata.append(dict(zenodoMetadataAccessFailure=str(error)))
            url='https://codeload.github.com/NLESC-JCER/QUICKLB/zip/refs/tags/v0.02';payload=get(url)
        with zipfile.ZipFile(io.BytesIO(payload)) as archive:
            assert sum(f.file_size for f in archive.infolist())<10_000_000
            for member in archive.infolist():
                path=(vendor/member.filename).resolve();assert path.is_relative_to(vendor.resolve()),member.filename
                assert (member.external_attr>>16)&0o170000 != 0o120000,'Refuse archive symlink'
            archive.extractall(vendor)
        metadata.append(dict(component='QUICKLB v0.02 / Zenodo 6598303',URL=url,SHA256=hashlib.sha256(payload).hexdigest()))
    else:metadata.append(dict(component='QUICKLB v0.02',source='existing project-local pinned archive; individual source hashes recorded separately'))
    (ROOT/'docs').mkdir(parents=True,exist_ok=True);(ROOT/'docs/quicklb_bootstrap.json').write_text(json.dumps(metadata,indent=2))
    print('Pinned public-library prerequisites ready.')
if __name__=='__main__':main()
