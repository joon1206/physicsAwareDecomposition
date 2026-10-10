"""Independent NASA7 inventory, no OpenFOAM thermodynamics calls.

Uses the case CHEMKIN coefficients and the installed reader's atomic weights.
The homogeneous mesh volume is specified by caseFactory's geometry.
"""
from pathlib import Path
import math,re
from foamio import read_field,read_labels
# Exact installed v2012 default: NA from fundamentalConstants.C and k from
# etc/controlDict. Matching these is necessary for an independent same-EOS test.
RU=6.0221417930e23*1.38065e-23*1000
ATOMIC={'H':1.00797,'O':15.99940,'N':14.00670,'AR':39.948,'C':12.01115}
def parse_nasa(path):
    lines=path.read_text().splitlines();data={}
    for i,line in enumerate(lines):
        if len(line)<80 or line[79]!='1':continue
        name=line[:18].strip().split()[0]
        elements={}
        for j in range(24,44,5):
            elem=line[j:j+2].strip().upper();count=line[j+2:j+5].strip()
            if elem and count:elements[elem]=int(count)
        w=sum(ATOMIC[e]*n for e,n in elements.items())
        high=[float(lines[i+1][j:j+15]) for j in range(0,75,15)]+[float(lines[i+2][j:j+15]) for j in [0,15]]
        low=[float(lines[i+2][j:j+15]) for j in [30,45,60]]+[float(lines[i+3][j:j+15]) for j in [0,15,30,45]]
        assert w>0 and len(high)==len(low)==7
        data[name]=dict(w=w,elements=elements,low=low,high=high,mid=float(line[65:75]))
    return data
def ha(spec,T):
    a=spec['low'] if T<spec['mid'] else spec['high']
    return RU/spec['w']*(sum(a[k]*T**(k+1)/(k+1) for k in range(5))+a[5])
def inventory(case,t,ranks):
    import json
    info=json.loads((case/'case.json').read_text());species=info['species'];n=info['nCells'];volume=.02*.008*.001/n
    nasa=parse_nasa(case/'chemkin/therm.dat');out=dict(mass=0,E_stored=0,E_NASA=0,C=0,H_stored=0,H_NASA=0,J=0,P=0,max_h_inversion_error=0,elements={})
    bases=[case/f'processor{r}' for r in range(ranks)] if ranks>1 else [case]
    for base in bases:
        nc=len(read_labels(base/'constant/polyMesh/cellProcAddressing')) if ranks>1 else n
        path=base/format(t,'.12g');T=read_field(path/'T',nc);p=read_field(path/'p',nc);U=read_field(path/'U',nc)
        ys={s:read_field(path/s,nc) for s in species}
        rho=read_field(path/'rho',nc) if (path/'rho').exists() else [p[c]/(T[c]*RU*sum(ys[s][c]/nasa[s]['w'] for s in species)) for c in range(nc)]
        hs=read_field(path/'h',nc) if (path/'h').exists() else None
        for c in range(nc):
            dm=rho[c]*volume;hc=sum(ys[s][c]*ha(nasa[s],298.15) for s in species)
            hab=sum(ys[s][c]*ha(nasa[s],T[c]) for s in species);hst=hab-hc if hs is None else hs[c]
            k=sum(v*v for v in U[c])/2
            out['mass']+=dm;out['C']+=dm*hc;out['H_stored']+=dm*hst;out['H_NASA']+=dm*(hab-hc);out['J']+=dm*k;out['P']+=volume*p[c]
            out['max_h_inversion_error']=max(out['max_h_inversion_error'],abs(hst-(hab-hc)))
            for s in species:
                for e,num in nasa[s]['elements'].items():
                    out['elements'][e]=out['elements'].get(e,0)+dm*ys[s][c]*num*ATOMIC[e]/nasa[s]['w']
    out['E_stored']=out['H_stored']+out['C']+out['J']-out['P'];out['E_NASA']=out['H_NASA']+out['C']+out['J']-out['P']
    return out
