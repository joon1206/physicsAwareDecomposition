"""Strict ASCII OpenFOAM field/list IO. Unsupported/binary formats fail."""
import math,re
from pathlib import Path
def clean(text):
    return re.sub(r'//[^\n]*|/\*.*?\*/','',text,flags=re.S)
def group(text,pos):
    if text[pos]!='(':raise ValueError('expected opening parenthesis')
    level=0
    for i in range(pos,len(text)):
        if text[i]=='(':level+=1
        elif text[i]==')':
            level-=1
            if level==0:return text[pos+1:i],i+1
    raise ValueError('unclosed list')
def read_field(path,n=None):
    t=clean(Path(path).read_text())
    if re.search(r'format\s+binary',t):raise ValueError('binary format unsupported')
    m=re.search(r'internalField\s+(uniform|nonuniform)\s+',t)
    if not m:raise ValueError('no internalField: '+str(path))
    if m[1]=='uniform':
        value=t[m.end():t.index(';',m.end())].strip()
        v=tuple(map(float,value.strip('()').split())) if value.startswith('(') else float(value)
        return [v]*(n or 1)
    h=re.match(r'(?:List<\w+>|\w+Field)\s+(\d+)\s*',t[m.end():])
    if not h:raise ValueError('invalid nonuniform list header')
    size=int(h[1]);pos=m.end()+h.end();body,_=group(t,pos)
    if '(' in body:
        vals=[tuple(map(float,v.split())) for v in re.findall(r'\(([^()]*)\)',body)]
    else:vals=list(map(float,body.split()))
    if len(vals)!=size or (n is not None and size!=n):raise ValueError('field size mismatch: '+str(path))
    flat=[x for v in vals for x in (v if isinstance(v,tuple) else (v,))]
    if not all(math.isfinite(x) for x in flat):raise ValueError('nonfinite field')
    return vals
def read_labels(path):
    t=clean(Path(path).read_text());end=t.index('}')+1
    m=re.search(r'(\d+)\s*\(',t[end:])
    if not m:raise ValueError('missing counted list')
    body,_=group(t,end+m.end()-1);v=list(map(int,body.split()))
    if len(v)!=int(m[1]):raise ValueError('label count mismatch')
    return v
def write_scalar(path,values,patches):
    t='FoamFile { version 2.0; format ascii; class volScalarField; object '+Path(path).name+'; }\n'
    t+='dimensions [0 0 0 0 0 0 0];\ninternalField nonuniform List<scalar>\n'+str(len(values))+'\n(\n'
    t+='\n'.join(format(v,'.17g') for v in values)+'\n);\nboundaryField\n{\n'
    for name,kind in patches:
        t+=name+' { type '+('empty' if kind=='empty' else 'zeroGradient')+'; }\n'
    Path(path).write_text(t+'}\n')
def patches(path):
    t=clean(Path(path).read_text())
    return [(m[1],m[2]) for m in re.finditer(r'(\w+)\s*\{\s*type\s+(\w+)\s*;',t)]
def proc_metrics(case):
    rows=[]
    for p in sorted(Path(case).glob('processor[0-9]*'),key=lambda x:int(x.name[9:])):
        t=clean((p/'constant/polyMesh/boundary').read_text())
        faces=0;neighbours=set()
        for _,body in re.findall(r'(\w+)\s*\{([^{}]*)\}',t):
            if re.search(r'type\s+processor\s*;',body):
                faces+=int(re.search(r'nFaces\s+(\d+)',body)[1])
                neighbours.add(int(re.search(r'neighbProcNo\s+(\d+)',body)[1]))
        ids=read_labels(p/'constant/polyMesh/cellProcAddressing')
        rows.append({'rank':int(p.name[9:]),'nCells':len(ids),'processorFaces':faces,'nNeighbours':len(neighbours),'ids':ids})
    return rows
