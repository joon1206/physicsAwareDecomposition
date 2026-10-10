#!/usr/bin/env python3
"""Fail closed, compare all required fields; JSON norms and physical diagnostics."""
import argparse,json,math,re,statistics
from pathlib import Path
from foamio import read_field
FIELDS=['T','p','U','CH4','O2','CO2','H2O','N2','Qdot','rDeltaT']
MOLECULAR={'CH4':16.043,'O2':31.998,'CO2':44.009,'H2O':18.015,'N2':28.014}
ELEMENTS={'C':{'CH4':1,'CO2':1},'H':{'CH4':4,'H2O':2},'O':{'O2':2,'CO2':2,'H2O':1},'N':{'N2':2}}
def flatten(v):return [x for a in v for x in (a if isinstance(a,tuple) else (a,))]
def diagnostics(directory,n):
    y={s:read_field(Path(directory)/s,n) for s in MOLECULAR}
    T=read_field(Path(directory)/'T',n);p=read_field(Path(directory)/'p',n)
    # Ideal gas density, consistent with benchmark equationOfState.
    rho=[p[i]/(8314.46261815324*T[i]*sum(y[s][i]/MOLECULAR[s] for s in y)) for i in range(n)]
    if (Path(directory)/'rho').exists():rho=read_field(Path(directory)/'rho',n)
    energy=None
    if (Path(directory)/'h').exists():
        h=read_field(Path(directory)/'h',n);u=read_field(Path(directory)/'U',n)
        energy=8e-6*statistics.fmean(rho[i]*(h[i]+sum(v*v for v in u[i])/2) for i in range(n))
    # Uniform public mesh volume: 0.02 * 0.02 * 0.02 m^3.
    return {'densitySource':'native thermo.rho' if (Path(directory)/'rho').exists() else 'ideal-gas estimate',
      'totalMassKg':8e-6*statistics.fmean(rho),'sensiblePlusKineticEnergyJ':energy,'QdotIntegralW':8e-6*statistics.fmean(read_field(Path(directory)/'Qdot',n)),'densityMean':statistics.fmean(rho),
      'speciesMassPerVolume':{s:statistics.fmean([rho[i]*y[s][i] for i in range(n)]) for s in y},
      'elementKmolPerVolume':{e:statistics.fmean([rho[i]*sum(y[s][i]*a/MOLECULAR[s] for s,a in d.items()) for i in range(n)]) for e,d in ELEMENTS.items()},
      'sumYMaxError':max(abs(sum(y[s][i] for s in y)-1) for i in range(n)),
      'speciesMin':min(min(v) for v in y.values()),'speciesMax':max(max(v) for v in y.values()),
      'QdotMean':statistics.fmean(read_field(Path(directory)/'Qdot',n)),
      'probes':{f:{str(i):read_field(Path(directory)/f,n)[i] for i in [n//4,n//2,3*n//4]} for f in ['T','p','CH4']}}
def compare(ref,test,n,atol=1e-12,rtol=1e-10,fields=None):
    result={'reference':str(ref),'test':str(test),'nCells':n,'atol':atol,'rtol':rtol,'criterion':'Linf <= atol + rtol * reference Linf; pointwise criterion retained separately','fields':{},'pass':True}
    selected=list(fields or FIELDS)
    for extra in ['rho','h']:
        if (Path(ref)/extra).exists() or (Path(test)/extra).exists():selected.append(extra)
    for f in selected:
        try:
            a=flatten(read_field(Path(ref)/f,n));b=flatten(read_field(Path(test)/f,n))
            if len(a)!=len(b):raise ValueError('size mismatch')
            diff=[abs(x-y) for x,y in zip(a,b)]
            pointwise=all(d<=atol+rtol*abs(x) for d,x in zip(diff,a))
            scale=max(abs(x) for x in a)
            passed=max(diff)<=atol+rtol*scale
            result['fields'][f]={'L1':statistics.fmean(diff),'L2':math.sqrt(statistics.fmean([d*d for d in diff])),
                'Linf':max(diff),'referenceLinf':scale,'relativeLinf':max(diff)/scale if scale else None,'pointwisePass':pointwise,'relativeL2':math.sqrt(sum(d*d for d in diff)/sum(x*x for x in a)) if any(a) else None,'pass':passed}
            result['pass'] &= passed
        except (ValueError,OSError) as e:
            result['fields'][f]={'error':str(e),'pass':False};result['pass']=False
    result['referenceDiagnostics']=diagnostics(ref,n);result['testDiagnostics']=diagnostics(test,n)
    return result
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('ref');p.add_argument('test');p.add_argument('--cells',type=int,default=4000)
    p.add_argument('--atol',type=float,default=1e-12);p.add_argument('--rtol',type=float,default=1e-10);p.add_argument('--output',required=True);a=p.parse_args()
    r=compare(a.ref,a.test,a.cells,a.atol,a.rtol);Path(a.output).write_text(json.dumps(r,indent=2)+'\n')
    print('PASS' if r['pass'] else 'FAIL');raise SystemExit(0 if r['pass'] else 1)
