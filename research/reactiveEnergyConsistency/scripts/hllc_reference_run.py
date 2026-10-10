"""Verify the independent central reference before any reacting-flow claim."""
from pathlib import Path
import csv,hashlib,json,math,re,shutil,sys
from caseFactory import make_case,header,command,field
from candidate_screen import sha
from exact_wave import analytic,CP,W,R,P,U0,TF as WAVE_TF
from candidate_reacting_wave import composition,HF
from foamio import read_field
from thermo_reference import inventory
ROOT=Path(__file__).resolve().parents[1];STUDY=ROOT/'candidateStudy';EXE='reactingEnergyHLLCReference'
def version():
    app=ROOT/'applications'/EXE
    source={p.name:sha(p) for p in app.iterdir() if p.suffix in ['.H','.C']}
    digest=hashlib.sha256(json.dumps(source,sort_keys=True).encode()).hexdigest();snapshot=STUDY/'sourceSnapshots'/digest
    if not snapshot.exists():
        snapshot.mkdir()
        for p in app.iterdir():
            if p.suffix in ['.H','.C']:shutil.copy2(p,snapshot/p.name)
        shutil.copytree(app/'Make',snapshot/'Make',ignore=shutil.ignore_patterns('linux*'))
        shutil.copytree(app/'originalV2012',snapshot/'originalV2012')
    return dict(source=source,sourceSnapshot=str(snapshot.relative_to(ROOT)),executable=EXE,executableSHA256=sha(ROOT/'build/bin'/EXE))
def central_schemes(case):
    (case/'system/fvSchemes').write_text(header('fvSchemes')+'''fluxScheme Kurganov;
ddtSchemes { default Euler; }
gradSchemes { default Gauss linear; }
divSchemes { default Gauss linear; }
laplacianSchemes { default Gauss linear corrected; }
interpolationSchemes { default linear; reconstruct(rho) upwind; reconstruct(U) upwind; reconstruct(T) upwind; }
snGradSchemes { default corrected; }
fluxRequired { default no; }
''')
    (case/'system/fvSolution').write_text(header('fvSolution')+'solvers { "(rho|rhoU|rhoE|rhoY_.*)" { solver diagonal; } }\n')
def run(kind='Wave',nx=32,dt=20e-9,tf=WAVE_TF,tag=''):
    name=f'HLLC_{kind}_nx{nx}_dt{dt:g}_TF{tf:g}_hRecovery3{tag}';case=STUDY/'data/raw'/name
    if (case/'central_result.json').exists():return json.loads((case/'central_result.json').read_text())
    if (case/'failure.json').exists():return json.loads((case/'failure.json').read_text())
    if case.exists():raise RuntimeError('Retained incomplete '+str(case))
    make_case(name,'heldoutMoving' if kind=='F' else 'uniform',nx=nx,ny=1,dt=dt,steps=round(tf/dt))
    if kind in ['Wave','ReactingWave']:
        fixture=STUDY/f'data/raw/{"Wave_none" if kind=="Wave" else "ReactingWave_none"}_nx{nx}_dt2e-08{"_v2" if kind=="ReactingWave" else ""}'
        for p in (fixture/'constant').iterdir():
            if p.is_file():shutil.copy2(p,case/'constant'/p.name)
        for p in (fixture/'0').iterdir():
            if p.is_file():shutil.copy2(p,case/'0'/p.name)
        if kind=='ReactingWave':
            info=json.loads((case/'case.json').read_text());info['species']=['A','B'];(case/'case.json').write_text(json.dumps(info,indent=2)+'\n')
    else:
        transport=case/'chemkin/transportProperties';transport.write_text(re.sub(r'(\bAs\s+)[^;]+;',r'\g<1>0;',transport.read_text()))
    # Retain the registered reacting sensible-h model; recover it from Ea via Cv.
    chem=case/'constant/chemistryProperties';chem.write_text(chem.read_text().replace('solver costOde','solver ode'))
    central_schemes(case);config=dict(name=name,kind=kind,nx=nx,nCells=nx,dt=dt,TF=tf,steps=round(tf/dt),ranks=1,scope='Inviscid conservative HLLC reference; known contact-resolving flux, not a new method',**version())
    (case/'central_experiment.json').write_text(json.dumps(config,indent=2)+'\n')
    try:wall=command(['mpirun','--bind-to','core','--map-by','core','--nooversubscribe','-np','1',EXE],case,case/'solver.log',timeout=900)
    except RuntimeError as e:
        result={**config,'failed':True,'error':str(e)};(case/'failure.json').write_text(json.dumps(result,indent=2)+'\n');print('RETAINED FAILURE',name,flush=True);return result
    end=case/format(tf,'.12g');rr=read_field(end/'rho',nx);tt=read_field(end/'T',nx);pp=read_field(end/'p',nx);uu=read_field(end/'U',nx)
    with next(case.glob('**/centralReference/*/rank0000.csv')).open() as f:budget=[{k:float(v) for k,v in r.items()} for r in csv.DictReader(f)]
    result=dict(**config,wall=wall,Tmean=math.fsum(tt)/nx,Tmin=min(tt),Tmax=max(tt),
        maxLocalEnergyResidual=max(r['maxLocalEnergyResidual'] for r in budget),maxYsumError=max(r['sumYError'] for r in budget),
        minY=min(r['minY'] for r in budget),maxThermoEnergyMismatch=max(abs(r['absoluteEnergy']-r['thermoEnergy']) for r in budget),
        maxRootResidual=max(r.get('maxRootResidual',0) for r in budget),maxRootTolerance=max(r.get('maxRootTolerance',0) for r in budget),
        oldRootCriterionUnmet=math.fsum(r.get('oldRootCriterionUnmet',0) for r in budget))
    if kind in ['Wave','ReactingWave']:
        r0,t0=analytic(nx,0);rx,tx=analytic(nx,tf);hf=HF if kind=='ReactingWave' else 0
        v=.02*.008*.001/nx;E0=math.fsum(v*(r*(CP*(t-298.15)+hf+U0*U0/2)-P) for r,t in zip(r0,t0))
        errors={}
        points=[('rho',rr,rx),('T',tt,tx),('p',pp,[P]*nx),('Ux',[u[0] for u in uu],[U0]*nx)]
        if kind=='ReactingWave':
            aa,bb=composition(nx,tf);points += [('A',read_field(end/'A',nx),aa),('B',read_field(end/'B',nx),bb)]
        for key,vals,exact in points:
            ds=[abs(x-y) for x,y in zip(vals,exact)];errors[key]=dict(L1=math.fsum(ds)/nx,L2=math.sqrt(math.fsum(x*x for x in ds)/nx),Linf=max(ds))
        result.update(errors=errors,signedEnergyDrift=(budget[-1]['absoluteEnergy']-E0)/abs(E0),massDrift=(math.fsum(rr)-math.fsum(r0))/math.fsum(r0))
    else:
        start=inventory(case,0,1);last=inventory(case,tf,1)
        result.update(initial=start,end=last,signedEnergyDrift=(last['E_NASA']-start['E_NASA'])/abs(start['E_NASA']),
            massDrift=(last['mass']-start['mass'])/start['mass'],elementDrift={k:(last['elements'][k]-v)/v for k,v in start['elements'].items() if v>1e-20})
    (case/'central_result.json').write_text(json.dumps(result,indent=2)+'\n')
    print(name,'T',result['Tmean'],'energy',result['signedEnergyDrift'],'local',result['maxLocalEnergyResidual'],flush=True);return result
def main():
    if len(sys.argv)>1 and sys.argv[1]=='pilot':
        rows=[run(),run('ReactingWave'),run('B',nx=8,dt=1e-6,tf=240e-6)]
    elif len(sys.argv)>1 and sys.argv[1]=='hydrogenPilot':
        rows=[run('F',nx=32,dt=.125e-6,tf=240e-6)]
    elif len(sys.argv)>1 and sys.argv[1]=='hydrogenRefinement':
        rows=[run('F',nx=nx,dt=dt,tf=240e-6) for nx,dt in [(64,.0625e-6),(128,.03125e-6),(128,.015625e-6),(256,.015625e-6)]]
    elif len(sys.argv)>1 and sys.argv[1]=='hydrogen512':
        rows=[run('F',nx=512,dt=.0078125e-6,tf=240e-6)]
    elif len(sys.argv)>1 and sys.argv[1]=='hydrogenTime256':
        rows=[run('F',nx=256,dt=.0078125e-6,tf=240e-6)]
    elif len(sys.argv)>1 and sys.argv[1]=='hydrogenFine':
        rows=[run('F',nx=nx,dt=dt,tf=240e-6) for nx,dt in [(256,.015625e-6),(512,.0078125e-6)]]
    else:
        rows=[run(kind,nx) for kind in ['Wave','ReactingWave'] for nx in [32,64,128]]
        rows += [run('B',nx=8,dt=dt,tf=240e-6) for dt in [1e-6,.5e-6,.25e-6,.125e-6]]
    rows=[json.loads(p.read_text()) for p in sorted((STUDY/'data/raw').glob('HLLC_*/central_result.json'))]
    (STUDY/'data/processed/hllc_verification.json').write_text(json.dumps(rows,indent=2)+'\n')
if __name__=='__main__':main()
