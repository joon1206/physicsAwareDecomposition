"""Deterministic cost models and offline metrics; no fabricated runtime."""
import math,statistics
def weights(points,kind='uniform',amplitude=0,width=.15,centre=(.5,.5,.5)):
    if not math.isfinite(amplitude) or amplitude<0 or not math.isfinite(width) or width<=0:raise ValueError('amplitude >= 0 and width > 0 required')
    result=[]
    for x,y,z in points:
        if kind=='uniform':v=1.
        elif kind=='gaussian':v=1+amplitude*math.exp(-((x-centre[0])**2+(y-centre[1])**2)/width**2)
        elif kind=='slab':v=1+amplitude*(abs(x-centre[0])<width/2)
        elif kind=='half':v=1+amplitude*(x<.5)
        elif kind=='multiple':
            v=1+amplitude*sum(math.exp(-((x-a)**2+(y-b)**2)/width**2) for a,b in [(.2,.25),(.7,.75)])
        elif kind=='extreme':v=1+amplitude*(abs(x-centre[0])<width/2 and abs(y-centre[1])<width/2)
        else:raise ValueError('unknown distribution '+kind)
        result.append(v)
    return result
def composite(cost,gamma,lo=.05,hi=100.,alpha=1.,previous=None):
    if not cost or not all(math.isfinite(c) and c>=0 for c in cost):raise ValueError('finite nonnegative cost required')
    if not 0<=alpha<=1 or not math.isfinite(gamma) or gamma<0 or not 0<lo<=hi:raise ValueError('invalid model parameters')
    if previous is not None:
        if len(previous)!=len(cost) or not all(math.isfinite(c) and c>=0 for c in previous):raise ValueError('invalid previous costs')
        cost=[alpha*c+(1-alpha)*p for c,p in zip(cost,previous)]
    mean=statistics.fmean(cost)
    w=[1+gamma*c/mean if mean else 1. for c in cost]
    scale=statistics.fmean(w)
    # Clip AFTER normalization, so final weights honor bounds.
    return [min(hi,max(lo,x/scale)) for x in w]
def metrics(loads):
    if not loads or any(not math.isfinite(v) or v<0 for v in loads):raise ValueError('invalid loads')
    m=statistics.fmean(loads)
    return {'min':min(loads),'max':max(loads),'mean':m,'median':statistics.median(loads),
      'imbalance':max(loads)/m if m else 1.,'cv':statistics.pstdev(loads)/m if m else 0.,
      'idleProxy':sum(max(loads)-x for x in loads)}
def correlation(a,b):
    if len(a)!=len(b) or len(a)<2:raise ValueError('matched samples required')
    ma=statistics.fmean(a);mb=statistics.fmean(b)
    va=sum((x-ma)**2 for x in a);vb=sum((y-mb)**2 for y in b)
    return sum((x-ma)*(y-mb) for x,y in zip(a,b))/math.sqrt(va*vb) if va and vb else None
def break_even(partition,migration,saving):
    if min(partition,migration)<0:raise ValueError('costs must be nonnegative')
    return (partition+migration)/saving if saving>0 else None
def lpt(weights,p):
    loads=[0.]*p;assignment=[0]*len(weights)
    for i in sorted(range(len(weights)),key=lambda i:weights[i],reverse=True):
        r=min(range(p),key=lambda j:loads[j]);loads[r]+=weights[i];assignment[i]=r
    return loads,assignment
