"""Conservative mesh restriction and field differences; no exact-reference claim."""
from pathlib import Path
import hashlib,json,math
from foamio import read_field
from thermo_reference import parse_nasa,ha,RU,inventory
ROOT=Path(__file__).resolve().parents[1];STUDY=ROOT/'candidateStudy';RAW=STUDY/'data/raw'
VOLUME=.02*.008*.001

def state(case):
    meta=case/('central_result.json' if (case/'central_result.json').exists() else 'result.json')
    cfg=json.loads(meta.read_text());n=cfg['nCells'];tf=cfg['dt']*cfg['steps'];end=case/format(tf,'.12g')
    species=json.loads((case/'case.json').read_text())['species'];nasa=parse_nasa(case/'chemkin/therm.dat')
    primitive={f:read_field(end/f,n) for f in ['rho','T','p','U']+species}
    cons={'rho':primitive['rho'],'rhoU':[[r*v for v in u] for r,u in zip(primitive['rho'],primitive['U'])]}
    cons.update({s:[r*y for r,y in zip(primitive['rho'],primitive[s])] for s in species})
    cons['rhoEa']=[r*(math.fsum(primitive[s][i]*ha(nasa[s],primitive['T'][i]) for s in species)+math.fsum(v*v for v in primitive['U'][i])/2)-primitive['p'][i] for i,r in enumerate(primitive['rho'])]
    return dict(name=case.name,config=cfg,species=species,nasa=nasa,primitive=primitive,conserved=cons,initial=inventory(case,0,1))

def restrict(st,n):
    nf=len(st['primitive']['rho']);assert nf%n==0 and nf>=n
    block=nf//n;avg=lambda v:[math.fsum(v[i:i+block])/block for i in range(0,nf,block)]
    cons={k:avg(v) for k,v in st['conserved'].items() if k!='rhoU'}
    cons['rhoU']=[[math.fsum(v[j] for v in st['conserved']['rhoU'][i:i+block])/block for j in range(3)] for i in range(0,nf,block)]
    rho=cons['rho'];u=[[x/r for x in m] for r,m in zip(rho,cons['rhoU'])];ys={s:[x/r for x,r in zip(cons[s],rho)] for s in st['species']}
    temp=[];pressure=[];maxRootResidual=0.
    for i,r in enumerate(rho):
        Rmix=RU*math.fsum(ys[s][i]/st['nasa'][s]['w'] for s in st['species'])
        target=cons['rhoEa'][i]/r-math.fsum(x*x for x in u[i])/2
        def residual(t):return math.fsum(ys[s][i]*ha(st['nasa'][s],t) for s in st['species'])-Rmix*t-target
        low,high=200.,5000.
        if residual(low)>0 or residual(high)<0:raise RuntimeError('Inadmissible restricted energy')
        for _ in range(80):
            mid=(low+high)/2
            if residual(mid)>0:high=mid
            else:low=mid
        t=(low+high)/2;temp.append(t);pressure.append(r*Rmix*t);maxRootResidual=max(maxRootResidual,abs(residual(t)))
    out=dict(rho=rho,U=u,T=temp,p=pressure,**ys)
    errors={}
    for field in ['rho','rhoEa']+st['species']:
        before=VOLUME/nf*math.fsum(st['conserved'][field]);after=VOLUME/n*math.fsum(cons[field])
        errors[field]=abs(after-before)
    return out,dict(conservationMismatch=errors,maxThermodynamicRootResidual=maxRootResidual)

def norms(a,b):
    def scalar(x,y):
        d=[abs(i-j) for i,j in zip(x,y)];return dict(L1=math.fsum(d)/len(d),L2=math.sqrt(math.fsum(i*i for i in d)/len(d)),Linf=max(d))
    out={f:scalar(a[f],b[f]) for f in a if f!='U'}
    out['U']={}
    du=[math.sqrt(math.fsum((x-y)**2 for x,y in zip(u,v))) for u,v in zip(a['U'],b['U'])]
    out['U']=dict(L1=math.fsum(du)/len(du),L2=math.sqrt(math.fsum(x*x for x in du)/len(du)),Linf=max(du))
    return out

def main():
    candidates=[state(p.parent) for p in sorted(RAW.glob('Central_F_*/central_result.json')) if '_hRecovery2' in p.parent.name or '_hRecovery3' in p.parent.name]
    if not candidates:raise RuntimeError('No primitive-recovery-verified central F run')
    candidates.sort(key=lambda s:s['config']['nx']);ref=candidates[-1];rows=[]
    for st in candidates[:-1]+[state(p.parent) for p in sorted(RAW.glob('InvF_*/result.json'))]:
        n=st['config']['nCells'];expected,restriction=restrict(ref,n)
        rows.append(dict(name=st['name'],nx=n,mode=st['config'].get('mode','central'),dt=st['config']['dt'],
            fieldDifferences=norms(st['primitive'],expected),restriction=restriction,
            initialMassRelativeDifference=(st['initial']['mass']-ref['initial']['mass'])/ref['initial']['mass'],
            initialEnergyRelativeDifference=(st['initial']['E_NASA']-ref['initial']['E_NASA'])/abs(ref['initial']['E_NASA']),
            sourceSnapshot=st['config']['sourceSnapshot'],executableSHA256=st['config']['executableSHA256']))
    out=dict(reference=ref['name'],referenceNx=ref['config']['nx'],referenceSourceSnapshot=ref['config']['sourceSnapshot'],
        referenceStatus='Independent conservative discretization at the finest executed current-source mesh; spatial/temporal uncertainty not assumed negligible.',
        restriction='Uniform aligned cell-volume averaging of rho,rhoU,rhoY,rhoEa; recover U,Y and absolute internal-energy T via independent NASA7/Cv monotone root, then EOS p. Primitive averaging would not preserve the energy target.',
        interpretation='Differences are against a restricted numerical trajectory, not exact PDE errors. Central 256-versus-512 differences measure reference uncertainty; initial profile sampling differences are recorded.',records=rows)
    (STUDY/'data/processed/inviscid_field_comparison.json').write_text(json.dumps(out,indent=2)+'\n')
    print('REFERENCE',ref['name'])
    for r in rows:print(r['name'],'T L1',r['fieldDifferences']['T']['L1'],'U L1',r['fieldDifferences']['U']['L1'],'H2O L1',r['fieldDifferences']['H2O']['L1'])
if __name__=='__main__':main()
