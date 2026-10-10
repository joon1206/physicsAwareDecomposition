"""Canonical cell identity through native mesh redistribution."""
import json, re
from pathlib import Path
from foamio import read_labels,read_field,clean

def ids(case,processor,time_name=None):
    snapshot=case/'partitionIds'/f'{time_name}.json' if time_name is not None else None
    if snapshot is not None and snapshot.exists():return json.loads(snapshot.read_text())[processor.name]
    metadata=case/'globalCellIds.json'
    if metadata.exists():return json.loads(metadata.read_text())[processor.name]
    return read_labels(processor/'constant/polyMesh/cellProcAddressing')

def save_ids(case,time_name):
    mapping={}
    for p in case.glob('processor[0-9]*'):
        f=p/time_name/'padGlobalId'
        vals=read_field(f)
        mapping[p.name]=[int(round(x)) for x in vals]
        if any(abs(x-round(x))>1e-9 for x in vals):raise ValueError('nonintegral migrated ID')
    flat=[x for v in mapping.values() for x in v]
    if sorted(flat)!=list(range(len(flat))):raise ValueError('migration is not a bijection')
    (case/'globalCellIds.json').write_text(json.dumps(mapping))
    snapshots=case/'partitionIds';snapshots.mkdir(exist_ok=True)
    (snapshots/(time_name+'.json')).write_text(json.dumps(mapping))
    return mapping

def metrics(case):
    rows=[]
    for p in sorted(case.glob('processor[0-9]*'),key=lambda p:int(p.name[9:])):
        t=clean((p/'constant/polyMesh/boundary').read_text())
        faces=0;neighbors=set()
        for body in re.findall(r'\w+\s*\{([^{}]*)\}',t):
            if re.search(r'type\s+processor(?:Cyclic)?\s*;',body):
                faces+=int(re.search(r'nFaces\s+(\d+)',body)[1])
                neighbors.add(int(re.search(r'neighbProcNo\s+(\d+)',body)[1]))
        identity=ids(case,p)
        rows.append(dict(rank=int(p.name[9:]),nCells=len(identity),
                         processorFaces=faces,nNeighbours=len(neighbors),ids=identity))
    return rows

def assemble(case,time_name,field,n):
    values=[None]*n
    for p in case.glob('processor[0-9]*'):
        identity=ids(case,p,time_name);local=read_field(p/time_name/field,len(identity))
        for i,v in zip(identity,local):
            if values[i] is not None:raise ValueError('duplicate global cell')
            values[i]=v
    if any(v is None for v in values):raise ValueError('incomplete canonical field')
    return values

def canonical_directory(case,time_name,fields,n):
    # Text artifacts for quantitative verification; no reconstructed mesh implied.
    from caseFactory import header
    out=case/'canonical'/time_name;out.mkdir(parents=True,exist_ok=True)
    optional=[f for f in ['h','rho'] if all((p/time_name/f).exists() for p in case.glob('processor[0-9]*'))]
    fields=list(dict.fromkeys([f for f in fields if f not in ['h','rho']]+optional))
    for name in fields:
        values=assemble(case,time_name,name,n);vector=isinstance(values[0],tuple)
        kind='vector' if vector else 'scalar'
        text=header(name,'vol'+kind.title()+'Field')+f'internalField nonuniform List<{kind}>\n{n}\n(\n'
        text+='\n'.join('('+' '.join(map(str,v))+')' if vector else f'{v:.17g}' for v in values)+'\n);\n'
        (out/name).write_text(text)
    return out
