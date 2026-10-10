"""Real-data gap/overlap examples with rational positive-Cv branch bounds."""
from pathlib import Path
from fractions import Fraction as F
import hashlib,json,math
from thermo_reference import RU,ATOMIC,parse_nasa
ROOT=Path(__file__).resolve().parents[1];STUDY=ROOT/'candidateStudy'

def energy(nasa,ys,t,branch):
    return math.fsum(y*RU/nasa[s]['w']*(math.fsum(nasa[s][branch][k]*t**(k+1)/(k+1) for k in range(5))+nasa[s][branch][5]-t) for s,y in ys.items())

def cv_bound(nasa,ys,branch,low,high):
    coefficients=[sum((F(RU)*F(y)/F(nasa[s]['w'])*F(nasa[s][branch][k]) for s,y in ys.items()),F(0)) for k in range(5)]
    coefficients[0]-=sum((F(RU)*F(y)/F(nasa[s]['w']) for s,y in ys.items()),F(0))
    bounds=[]
    for left in range(low,high,10):
        right=min(left+10,high)
        bounds.append(sum((c*F(left if c>=0 else right)**k for k,c in enumerate(coefficients)),F(0)))
    minimum=min(bounds)
    if minimum<=0:raise RuntimeError('No positive Cv certificate from declared intervals')
    return dict(low=low,high=high,intervalWidth=10,positiveCvLowerBound=float(minimum),
                exactMinimumNumerator=str(minimum.numerator),exactMinimumDenominator=str(minimum.denominator),
                scope='Exact rational natural interval bound for polynomial evaluated with declared stored binary coefficients/weights. Not a bound on floating-point evaluation error.')

def root(nasa,ys,target,branch,lo,hi):
    if not energy(nasa,ys,lo,branch)<=target<=energy(nasa,ys,hi,branch):raise RuntimeError('Unbracketed branch root')
    for i in range(80):
        mid=(lo+hi)/2
        if energy(nasa,ys,mid,branch)>target:hi=mid
        else:lo=mid
    t=(lo+hi)/2;rmix=RU*math.fsum(y/nasa[s]['w'] for s,y in ys.items())
    return dict(T=t,p=rmix*t,energyResidual=energy(nasa,ys,t,branch)-target)

def main():
    source=STUDY/'data/raw/B_none_dt2e-06_s1_g0_o1_p1/chemkin/therm.dat';nasa=parse_nasa(source)
    initial=dict(H2=.0283,O2=.225,H=.0001,OH=.0001,N2=.7465);initialEnergy=energy(nasa,initial,999.,'low')
    direction=dict(H2=-nasa['H2']['w'],O2=-.5*nasa['O2']['w'],H2O=nasa['H2O']['w'])
    midpoint=lambda ys:(energy(nasa,ys,1000.,'low')+energy(nasa,ys,1000.,'high'))/2
    extent=(initialEnergy-midpoint(initial))/midpoint(direction)
    target=initial.copy()
    for s,value in direction.items():target[s]=target.get(s,0.)+extent*value
    lo=energy(nasa,target,1000.,'low');hi=energy(nasa,target,1000.,'high')
    if not min(target.values())>=0 or not lo<initialEnergy<hi:raise RuntimeError('Gap counterexample failed')
    elementDifference={e:math.fsum((target.get(s,0.)-initial.get(s,0.))*nasa[s]['elements'].get(e,0)*ATOMIC[e]/nasa[s]['w'] for s in set(target)|set(initial)) for e in ['H','O','N']}
    gap=dict(initialTemperature=999.,rho=1.,initialComposition=initial,targetComposition=target,reactionExtent=extent,targetEnergy=initialEnergy,
             energyLowLimit=lo,energyHighLimit=hi,gapWidth=hi-lo,
             massDifference=math.fsum(target.values())-math.fsum(initial.values()),elementDifference=elementDifference,
             branchCvBounds=[cv_bound(nasa,target,'low',200,1000),cv_bound(nasa,target,'high',1000,5000)],
             decision='No valid temperature root in 200–5000 K for this conservative target and unchanged thermochemistry.')
    ys={'N2':1.};lower=energy(nasa,ys,1000.,'low');upper=energy(nasa,ys,1000.,'high');e=(lower+upper)/2
    overlap=dict(composition=ys,rho=1.,targetEnergy=e,energyLowLimit=lower,energyHighLimit=upper,overlapWidth=lower-upper,
                 lowBranchRoot=root(nasa,ys,e,'low',200.,1000.),highBranchRoot=root(nasa,ys,e,'high',1000.,5000.),
                 branchCvBounds=[cv_bound(nasa,ys,'low',200,1000),cv_bound(nasa,ys,'high',1000,5000)],
                 decision='Two valid branch temperatures/pressures for the same rho,Y,E; global uniqueness does not follow from positive branch Cv.')
    cfg=dict(scriptSHA256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),thermoSHA256=hashlib.sha256(source.read_bytes()).hexdigest(),
             thermoSource=str(source.relative_to(ROOT)),scope='Exact branch existence argument with actual legacy data and rational derivative bounds; no actual reaction trajectory, repaired mechanism or new numerical method.')
    result=dict(configuration=cfg,gap=gap,overlap=overlap)
    raw=STUDY/'data/raw/ThermoBranchInversion_analytic';raw.mkdir(exist_ok=True)
    (raw/'inversion_experiment.json').write_text(json.dumps(cfg,indent=2)+'\n')
    (raw/'inversion_result.json').write_text(json.dumps(result,indent=2)+'\n')
    (STUDY/'data/processed/thermo_branch_inversion.json').write_text(json.dumps(result,indent=2)+'\n')
    print('Gap',gap['gapWidth'],'mass',gap['massDifference'],'elements',elementDifference,'min Cv',[r['positiveCvLowerBound'] for r in gap['branchCvBounds']])
    print('Overlap',overlap['overlapWidth'],'roots',overlap['lowBranchRoot'],overlap['highBranchRoot'],'min Cv',[r['positiveCvLowerBound'] for r in overlap['branchCvBounds']])
if __name__=='__main__':main()
