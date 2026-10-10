"""Persistence metrics and current-state features, with no future inputs."""
import csv, math, statistics
from pathlib import Path
from foamio import read_field
from mapping import ids,metrics

def correlation(a,b):
    if len(a)!=len(b) or not a:raise ValueError('matching nonempty vectors required')
    ma=statistics.mean(a);mb=statistics.mean(b)
    va=sum((x-ma)**2 for x in a);vb=sum((x-mb)**2 for x in b)
    if va==0 or vb==0:return 1. if a==b else 0.
    return max(-1.,min(1.,sum((x-ma)*(y-mb) for x,y in zip(a,b))/math.sqrt(va*vb)))

def top_overlap(a,b,q=.1):
    if len(a)!=len(b) or not 0<q<=1:raise ValueError('invalid overlap inputs')
    k=max(1,math.ceil(len(a)*q))
    x=set(sorted(range(len(a)),key=lambda i:(-a[i],i))[:k])
    y=set(sorted(range(len(b)),key=lambda i:(-b[i],i))[:k])
    return len(x&y)/len(x|y)

def normalize(cost,gamma=1.,lower=.1,upper=10.):
    if not cost or any(not math.isfinite(x) or x<0 for x in cost):raise ValueError('invalid cost')
    if gamma<0 or not 0<lower<=upper:raise ValueError('invalid normalization')
    mean=statistics.mean(cost)
    return [min(upper,max(lower,(1+gamma*x/max(mean,1e-30))/(1+gamma))) for x in cost]

def center(cost,nx,ny):
    # Circular x centroid respects the periodic box; ordinary y centroid.
    total=sum(cost)
    if total<=0:return (.01,.004)
    co=sum(v*math.cos(2*math.pi*(i%nx+.5)/nx) for i,v in enumerate(cost))
    si=sum(v*math.sin(2*math.pi*(i%nx+.5)/nx) for i,v in enumerate(cost))
    x=(math.atan2(si,co)%(2*math.pi))/(2*math.pi)*.02
    y=sum(v*(i//nx+.5)/ny*.008 for i,v in enumerate(cost))/total
    return x,y

def rank_costs(case,time_name,n):
    cost=[0.]*n;substeps=[0.]*n
    for p in case.glob('processor[0-9]*'):
        identity=ids(case,p)
        c=read_field(p/time_name/'chemCost',len(identity))
        for i,v in zip(identity,c):cost[i]=v
        f=p/time_name/'chemSubsteps'
        if f.exists():
            for i,v in zip(identity,read_field(f,len(identity))):substeps[i]=v
    return cost,substeps

def trace_cost(case,index,n):
    cost=[0.]*n;seen=set()
    for p in case.glob('processor[0-9]*'):
        identity=ids(case,p)
        for f in (p/'postProcessing/performance').glob('cellCost.csv'):
            with f.open() as stream:
                for row in csv.DictReader(stream):
                    if int(row['timeIndex'])==index:
                        cell=identity[int(row['cell'])]
                        cost[cell]=float(row['wall']);seen.add(cell)
    return cost if len(seen)==n else None

def extract(case,time_name,info,previous=None,lag_steps=None):
    n=info['nCells'];cost,substeps=rank_costs(case,time_name,n)
    parts=metrics(case)
    loads=[sum(cost[i] for i in p['ids']) for p in parts]
    imbalance=max(loads)/max(statistics.mean(loads),1e-30)
    phase_rows=[]
    for p in case.glob('processor[0-9]*'):
        for f in (p/'postProcessing/performance').glob('rank*.csv'):
            with f.open() as stream:
                phase_rows.extend(r for r in csv.DictReader(stream) if float(r['time'])<=float(time_name)+1e-12)
    rows=sorted(phase_rows,key=lambda r:float(r['time']))[-5*len(parts):]
    def phase(name):
        return statistics.mean(float(r[name]) for r in rows) if rows else 0.
    # Timer names are checked at runtime instead of silently assuming schema.
    names=list(rows[0]) if rows else []
    chem_name=next((x for x in ['chemistryWall','chemistry','chem'] if x in names),'chemistryWall')
    step_name=next((x for x in ['stepWall','timestep','step'] if x in names),'stepWall')
    chem=phase(chem_name);step=phase(step_name)
    index=round(float(time_name)/info['dt'])
    interval=lag_steps or min(20,max(1,index//2))
    if previous is None:previous=trace_cost(case,index-interval,n)
    rho=correlation(previous,cost) if previous is not None else 0.
    overlap=top_overlap(previous,cost) if previous is not None else 1.
    # A bounded empirical decay-time estimate, not a physical persistence law.
    lifetime=min(1000.,max(1.,-interval/math.log(max(.001,min(.999999,rho))))) if rho<.999 else 1000.
    cnow=center(cost,info['nx'],info['ny'])[0]
    cprev=center(previous,info['nx'],info['ny'])[0] if previous is not None else cnow
    observed_velocity=((cnow-cprev+.01)%.02-.01)/(interval*info['dt'])
    def load_imbalance(values):
        load=[sum(values[i] for i in p['ids']) for p in parts]
        return max(load)/max(statistics.mean(load),1e-30)
    ema=[.5*x+.5*y for x,y in zip(cost,previous or cost)]
    result=dict(chemistryImbalance=imbalance,chemistryFraction=chem/max(step,1e-30),
                chemistrySeconds=chem,timestepSeconds=step,totalCellCost=sum(cost),
                cellCostCV=statistics.pstdev(cost)/max(statistics.mean(cost),1e-30),
                correlation=rho,topOverlap=overlap,lifetimeSteps=lifetime,
                processorFaces=sum(p['processorFaces'] for p in parts)/2,
                maxNeighbours=max(p['nNeighbours'] for p in parts),
                cellImbalance=max(p['nCells'] for p in parts)/(n/len(parts)),
                centerX=cnow,observedCostVelocity=observed_velocity,
                persistenceLagSteps=interval,persistenceAvailable=previous is not None,
                previousImbalance=load_imbalance(previous or cost),
                twoSnapshotEMAImbalance=load_imbalance(ema),
                pressureSeconds=phase('pressureWall'),
                transportSeconds=sum(phase(k) for k in ['momentumWall','speciesWall','energyWall']),
                velocity=info['specification']['velocity'],nCells=n,ranks=len(parts),
                nSpecies=len(info['species']),substepsMean=statistics.mean(substeps))
    return result,cost
