"""Native closed-domain inventory, field norms, temporal and mesh diagnostics."""
import argparse,csv,json,math,re,statistics
from caseFactory import ROOT,make_case,decompose,solve,command,latest_time
from mapping import assemble,canonical_directory
from foamio import read_field

def norms():
    raw=json.loads((ROOT/'data/processed/oracle_raw.json').read_text());rows=[]
    for r in raw:
        if r['repeat']!=0 or r['action']=='A0':continue
        c=ROOT/r['relativeDirectory'];ref=c.with_name(c.name.replace('_'+r['action']+'_','_A0_'))
        if not (ref/'manifest.json').exists():continue
        end=latest_time(c,True);n=r['case']['nCells']
        optional=[f for f in ['h','rho'] if all((p/end/f).exists() for x in [ref,c] for p in x.glob('processor[0-9]*'))]
        for f in ['T','p','U','Qdot']+optional+r['case']['species']:
            a=assemble(ref,end,f,n);b=assemble(c,end,f,n)
            aa=[v for x in a for v in (x if isinstance(x,tuple) else [x])]
            bb=[v for x in b for v in (x if isinstance(x,tuple) else [x])]
            e=[abs(x-y) for x,y in zip(aa,bb)]
            rows.append(dict(regime=r['regime'],checkpoint=r['checkpoint'],H=r['horizonSteps'],action=r['action'],field=f,
                L1=statistics.mean(e),L2=math.sqrt(statistics.mean(x*x for x in e)),Linf=max(e),
                referenceIntegral=sum(aa),candidateIntegral=sum(bb)))
    (ROOT/'data/processed/numerical_norms.json').write_text(json.dumps(rows,indent=2))

def inventories():
    rows=[];species_composition={}
    # Exact weights in this OpenFOAM version's atomicWeights.C; generic rounded
    # periodic tables introduced a spurious ~2e-5 hydrogen budget discrepancy.
    atomic={'H':1.00797,'O':15.9994,'N':14.0067,'AR':39.948,'C':12.01115}
    for case in sorted((ROOT/'data/raw/histories').iterdir()):
        if not (case/'history.json').exists():continue
        info=json.loads((case/'case.json').read_text())
        for line in (case/'chemkin/therm.dat').read_text().splitlines():
            name=line[:18].split()[0] if line[:18].split() else ''
            if name not in info['species'] or not line.rstrip().endswith('1'):continue
            comp={}
            for i in range(24,44,5):
                element=line[i:i+2].strip().upper();count=line[i+2:i+5].strip()
                if element and count:
                    try:comp[element]=int(float(count))
                    except ValueError:pass
            if comp:species_composition[name]=comp
        command(['mpirun','--bind-to','core','--map-by','core','--nooversubscribe','-np','4','padNativeInventory','-parallel','-time','0:'],case,case/'inventory.log')
        rank=[]
        for f in case.glob('processor*/postProcessing/inventory/rank*.csv'):
            rank.extend({k:float(v) for k,v in r.items()} for r in csv.DictReader(f.open()))
        times=sorted(set(r['time'] for r in rank));initial=None
        for t in times:
            group=[r for r in rank if r['time']==t];total={k:sum(r[k] for r in group) for k in group[0] if k not in ['time','rank','nCells','minT','maxT','sumYError']}
            total.update(time=t,regime=case.name,minT=min(r['minT'] for r in group),maxT=max(r['maxT'] for r in group),sumYError=max(r['sumYError'] for r in group))
            elements={e:0. for e in atomic}
            for s in info['species']:
                comp=species_composition.get(s,{})
                W=sum(atomic.get(e,0)*v for e,v in comp.items())
                if W<=0:raise RuntimeError('unparsed species elemental composition: '+s)
                for e,v in comp.items():elements[e]+=total['speciesMass_'+s]*v*atomic[e]/W
            total['elements']=elements
            if initial is None:initial=total
            total['relativeMassDrift']=(total['mass']-initial['mass'])/initial['mass']
            total['relativeEnergyDrift']=(total['totalEnergy']-initial['totalEnergy'])/max(abs(initial['totalEnergy']),1e-30)
            total['elementRelativeDrift']={e:(v-initial['elements'][e])/max(initial['elements'][e],1e-30) for e,v in elements.items()}
            rows.append(total)
    (ROOT/'data/processed/inventories.json').write_text(json.dumps(rows,indent=2))
    (ROOT/'data/processed/species_atoms.json').write_text(json.dumps(species_composition,indent=2))
    print('VERIFIED inventory snapshots',len(rows),'maximum mass drift',max(abs(r['relativeMassDrift']) for r in rows),flush=True)

def refinement():
    rows=[]
    # Same physical end time, identical grid, increasingly small physical dt.
    for nx,ny in [(32,8),(64,16)]:
        for dt in [2e-6,1e-6,.5e-6]:
            steps=round(4e-05/dt);name=f'refine/nx{nx}_dt{dt}'
            c=ROOT/'data/raw'/name
            if not (c/'manifest.json').exists():
                make_case(name,'persistent',nx=nx,ny=ny,dt=dt,steps=steps)
                decompose(c,4);wall=solve(c,4)
                (c/'manifest.json').write_text(json.dumps(dict(wall=wall,nx=nx,ny=ny,dt=dt)))
            T=assemble(c,latest_time(c,True),'T',nx*ny);q=assemble(c,latest_time(c,True),'Qdot',nx*ny)
            rows.append(dict(nx=nx,ny=ny,dt=dt,Tmean=statistics.mean(T),Tmax=max(T),QdotIntegral=sum(q)*.02*.008*.001/(nx*ny),T=T))
    for r in rows:
        reference=next(s for s in rows if s['nx']==r['nx'] and s['dt']==.5e-6)
        e=[abs(a-b) for a,b in zip(r['T'],reference['T'])]
        r['temporalT_Linf']=max(e);r['temporalT_L2']=math.sqrt(statistics.mean(x*x for x in e))
    (ROOT/'data/processed/refinement.json').write_text(json.dumps(rows,indent=2))

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('mode',choices=['norms','inventories','refinement']);globals()[p.parse_args().mode]()
