"""Create a private v2012 utility with the cyclic-patch validation fix."""
import difflib,hashlib,json,os,shutil
from pathlib import Path
PAD=Path(__file__).resolve().parents[2]
ROOT=Path(os.environ.get('PAD_ACTION_ROOT',PAD/'actionStudy'))
def main():
    native=Path(os.environ.get('PAD_FOAM_ROOT','/opt/OpenFOAM/OpenFOAM-v2012'))/'applications/utilities/parallelProcessing/redistributePar'
    target=PAD/'applications/redistributeParPAD';target.mkdir(exist_ok=True)
    for source in native.iterdir():
        if source.is_file() and source.suffix in ['.C','.H']:
            destination=target/source.name
            if not destination.exists():shutil.copy2(source,destination)
    (target/'Make').mkdir(exist_ok=True)
    for name in ['files','options']:
        if not (target/'Make'/name).exists():shutil.copy2(native/'Make'/name,target/'Make'/name)
    source=(native/'loadOrCreateMesh.C').read_text()
    old='if (type == processorPolyPatch::typeName)'
    new='if (type == processorPolyPatch::typeName || type == processorCyclicPolyPatch::typeName)'
    if source.count(old)!=1:raise RuntimeError('native v2012 patch-check location differs; inspect before porting')
    fixed=source.replace(old,new)
    destination=target/'loadOrCreateMesh.C'
    if destination.read_text() not in [source,fixed]:raise RuntimeError('private utility contains independent edits; refusing overwrite')
    destination.write_text(fixed)
    original=(native/'Make/files').read_text();adapted=original.replace('$(FOAM_APPBIN)/redistributePar','$(FOAM_USER_APPBIN)/redistributeParPAD')
    (target/'Make/files').write_text(adapted)
    docs=ROOT/'docs';docs.mkdir(parents=True,exist_ok=True)
    patch=''.join(difflib.unified_diff(source.splitlines(True),fixed.splitlines(True),fromfile='native/loadOrCreateMesh.C',tofile='private/loadOrCreateMesh.C'))
    patch+=''.join(difflib.unified_diff(original.splitlines(True),adapted.splitlines(True),fromfile='native/Make/files',tofile='private/Make/files'))
    (docs/'redistribute_v2012.patch').write_text(patch)
    (docs/'redistribute_port.json').write_text(json.dumps(dict(OpenFOAM='v2012',nativeSource=str(native),
        originalSHA256=hashlib.sha256(source.encode()).hexdigest(),patchedSHA256=hashlib.sha256(fixed.encode()).hexdigest(),
        change='Treat processorCyclic as a processor patch in the load-time physical-patch synchronization check. Redistribution algorithm is unchanged. Private executable only; installed utility is preserved.'),indent=2))
    print('PREPARED private redistributeParPAD; cyclic processor patches skip physical-patch checks')
if __name__=='__main__':main()
