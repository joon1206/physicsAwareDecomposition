"""Numerical gates fixed before the action benchmark campaign."""
import json, math, re, shutil
from caseFactory import ROOT, make_case, decompose, solve, reconstruct, latest_time, set_chemistry
from foamio import read_field

def numerical_gate(reference, candidate, info):
    n=info['nCells']; rows={}; passed=True
    fields=['T','p','U','Qdot']+info['species']
    optional=[f for f in ['h','rho'] if (reference/f).exists() and (candidate/f).exists()]
    fields+=optional
    for name in fields:
        a=read_field(reference/name,n);b=read_field(candidate/name,n)
        af=[z for x in a for z in (x if isinstance(x,tuple) else [x])]
        bf=[z for x in b for z in (x if isinstance(x,tuple) else [x])]
        finite=all(math.isfinite(v) for v in af+bf)
        error=max(abs(x-y) for x,y in zip(af,bf)) if finite else None
        scale=max(abs(x) for x in af) if finite else None
        atol,rtol={'T':(2e-4,1e-7),'p':(.02,1e-7),'U':(1e-5,1e-7),
                   'Qdot':(1.,1e-5),'h':(.01,1e-7),'rho':(1e-9,1e-7)}.get(name,(1e-8,1e-6))
        admissible=finite and (min(af+bf)>0 if name in ['T','p','rho'] else True)
        ok=admissible and error<=atol+rtol*scale
        rows[name]=dict(Linf=error,referenceScale=scale,atol=atol,rtol=rtol,finite=finite,admissible=admissible,pass_=ok)
        passed &= ok
    ys=[read_field(candidate/s,n) for s in info['species']]
    sum_error=max(abs(sum(v[i] for v in ys)-1) for i in range(n))
    smallest=min(min(v) for v in ys)
    passed &= sum_error<1e-10 and smallest>=-1e-12
    return dict(pass_=passed,fields=rows,sumYError=sum_error,minY=smallest,
                omittedOptionalFields=[f for f in ['h','rho'] if f not in optional],
                criterion='Predeclared field-scale infinity norm; no pointwise division by trace-species values.')

def main():
    cases={}
    for action in ['native','A0','AC']:
        c=make_case('validation/'+action,'persistent',nx=32,ny=8,steps=20,action=action)
        if action=='native':
            f=c/'constant/chemistryProperties'
            f.write_text(f.read_text().replace('solver costOde;','solver ode;'))
        decompose(c,4);solve(c,4);reconstruct(c)
        cases[action]=c
    info=json.loads((cases['A0']/'case.json').read_text())
    end=latest_time(cases['A0'])
    results={}
    for pair in [('native','A0'),('A0','AC')]:
        result=numerical_gate(cases[pair[0]]/end,cases[pair[1]]/end,info)
        results['_vs_'.join(pair)]=result
        print('TESTED',pair,result['pass_'],{k:v['Linf'] for k,v in result['fields'].items()},flush=True)
    (ROOT/'data/processed/baseline_validation.json').write_text(json.dumps(results,indent=2))
    if not all(r['pass_'] for r in results.values()):raise RuntimeError('baseline numerical gate failed')

if __name__=='__main__':main()
