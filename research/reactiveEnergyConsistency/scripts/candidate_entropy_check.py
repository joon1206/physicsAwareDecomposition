"""Independent endpoint ideal-mixture entropy/admissibility screen, not a theorem."""
from pathlib import Path
import json, math
from thermo_reference import parse_nasa, RU
from foamio import read_field, read_labels
ROOT=Path(__file__).resolve().parents[1]; STUDY=ROOT/'candidateStudy'; PSTD=100000.
def entropy(case,t,cfg):
    n=cfg['nCells'];species=json.loads((case/'case.json').read_text())['species'];nasa=parse_nasa(case/'chemkin/therm.dat')
    bases=[case/f'processor{i}' for i in range(cfg['ranks'])] if cfg['ranks']>1 else [case]
    volume=.02*.008*.001/n;terms=[];minT=math.inf;minP=math.inf;minY=math.inf;maxSum=0.;mass=0.
    for base in bases:
        nc=len(read_labels(base/'constant/polyMesh/cellProcAddressing')) if cfg['ranks']>1 else n
        path=base/format(t,'.12g');temp=read_field(path/'T',nc);pressure=read_field(path/'p',nc)
        ys={s:read_field(path/s,nc) for s in species}
        rho=read_field(path/'rho',nc) if (path/'rho').exists() else [pressure[i]/(temp[i]*RU*math.fsum(ys[s][i]/nasa[s]['w'] for s in species)) for i in range(nc)]
        for i,T in enumerate(temp):
            p=pressure[i];r=rho[i];minT=min(minT,T);minP=min(minP,p)
            minY=min(minY,min(ys[s][i] for s in species));maxSum=max(maxSum,abs(math.fsum(ys[s][i] for s in species)-1))
            if min(T,p,r)<=0:raise RuntimeError('Inadmissible entropy state '+str(path))
            # No state clipping: trace negative values are separately reported.
            if min(ys[s][i] for s in species)<-1e-12:raise RuntimeError('Negative species '+str(path))
            mol=math.fsum(ys[s][i]/nasa[s]['w'] for s in species);specific=0.
            for s in species:
                y=ys[s][i]
                if y<=0:continue # zero-species limiting contribution; signed trace is reported above
                spec=nasa[s];a=spec['low'] if T<spec['mid'] else spec['high'];R=RU/spec['w']
                standard=R*(a[0]*math.log(T)+math.fsum(a[k]*T**k/k for k in range(1,5))+a[6])
                x=(y/spec['w'])/mol;specific+=y*(standard-R*math.log(x*p/PSTD))
            dm=r*volume;mass+=dm;terms.append(dm*specific)
    return dict(totalEntropy=math.fsum(terms),mass=mass,minT=minT,minP=minP,minY=minY,maxYsumError=maxSum)
def main():
    rows=[]
    patterns=['F_*/result.json','InvF_*/result.json','Central_F_*/central_result.json','HLLC_F_*/central_result.json','ThermoWave_*/wave_result.json']
    for pattern in patterns:
        for meta in sorted((STUDY/'data/raw').glob(pattern)):
            cfg=json.loads(meta.read_text());case=meta.parent
            # Altered thermodynamic offsets are separate physics/reference experiments.
            ablation=cfg.get('formationAblation',{})
            if ablation.get('scale',1)!=1 or ablation.get('elementGauge',0)!=0:continue
            initial=entropy(case,0,cfg);last=entropy(case,cfg['dt']*cfg['steps'],cfg)
            rows.append(dict(name=case.name,mode=cfg.get('mode','hllc' if case.name.startswith('HLLC') else 'central'),
                             initial=initial,end=last,entropyChange=last['totalEntropy']-initial['totalEntropy'],
                             sourceSnapshot=cfg['sourceSnapshot'],executableSHA256=cfg['executableSHA256']))
    data=dict(records=rows,scope='Independent NASA7 ideal-mixture entropy using pstandard=100000 Pa. Endpoint closed-domain screen only: positive entropy change is not a local entropy inequality or a proof of entropy stability. Non-positive species traces are reported; their entropy limiting term is omitted below the stated -1e-12 rejection threshold, without changing fields.')
    (STUDY/'data/processed/entropy_admissibility.json').write_text(json.dumps(data,indent=2)+'\n')
    print('Entropy/admissibility endpoints:',len(rows),'min change',min(r['entropyChange'] for r in rows),'min T',min(r['end']['minT'] for r in rows),'min p',min(r['end']['minP'] for r in rows))
if __name__=='__main__':main()
