"""Exact unequal-thermodynamic contact transport; retained independent checks."""
from pathlib import Path
import csv, hashlib, json, math, re, shutil, sys
from caseFactory import make_case, field, command, solve
from campaign import change
from candidate_screen import sha
from thermo_reference import parse_nasa, ha, RU, inventory
from foamio import read_field
from hllc_reference_run import central_schemes

ROOT=Path(__file__).resolve().parents[1]; STUDY=ROOT/'candidateStudy'; RAW=STUDY/'data/raw'
L=.02; P=101325.; U=40.; TF=20e-6
EXES={'none':'reactingEnergyCandidates','conservativeState':'reactingEnergyCandidates',
      'blockConservative':'reactingEnergyBlockCandidates','central':'reactingEnergyCentralReference',
      'hllc':'reactingEnergyHLLCReference'}

def analytic(n,t,nasa,species):
    z=[2*math.pi*((i+.5)/n-U*t/L) for i in range(n)]
    temp=[800+200*math.sin(x) for x in z]; hydrogen=[.08+.05*math.cos(x) for x in z]
    ys={s:hydrogen if s=='H2' else [1-y for y in hydrogen] if s=='N2' else [0.]*n for s in species}
    rho=[P/(RU*temp[i]*math.fsum(ys[s][i]/nasa[s]['w'] for s in species)) for i in range(n)]
    return dict(T=temp,p=[P]*n,Ux=[U]*n,rho=rho,**ys)

def recovery(q,energy,nasa):
    density=math.fsum(q.values()); rvol=math.fsum(q[s]*RU/nasa[s]['w'] for s in q)
    def e(t):return math.fsum(q[s]*ha(nasa[s],t) for s in q)-rvol*t
    low,high=200.,5000.
    if not e(low)<=energy<=e(high):raise RuntimeError('Inadmissible mixed state')
    for _ in range(80):
        mid=(low+high)/2
        if e(mid)>energy:high=mid
        else:low=mid
    temp=(low+high)/2
    return dict(T=temp,p=rvol*temp,rho=density,rootResidual=e(temp)-energy)

def mixing_identity(nasa):
    # Physical distinct-temperature/composition donors, both at the same p,u.
    donors=[]
    for temp,y in [(500.,.02),(1500.,.2)]:
        rmix=RU*(y/nasa['H2']['w']+(1-y)/nasa['N2']['w']);rho=P/(rmix*temp)
        q={'H2':rho*y,'N2':rho*(1-y)}
        energy=math.fsum(q[s]*(ha(nasa[s],temp)-RU/nasa[s]['w']*temp) for s in q)
        donors.append(dict(T=temp,q=q,internalEnergyDensity=energy))
    records=[]
    for weight in [.1,.25,.5,.75,.9]:
        q={s:(1-weight)*donors[0]['q'][s]+weight*donors[1]['q'][s] for s in donors[0]['q']}
        target=(1-weight)*donors[0]['internalEnergyDensity']+weight*donors[1]['internalEnergyDensity']
        answer=recovery(q,target,nasa);tp=P/math.fsum(q[s]*RU/nasa[s]['w'] for s in q)
        ep=math.fsum(q[s]*(ha(nasa[s],tp)-RU/nasa[s]['w']*tp) for s in q)
        # An elemental energy-reference shift is exactly linear in q.
        gauge={'H2':1e7,'N2':0.};before=target-ep
        shiftedTarget=(1-weight)*(donors[0]['internalEnergyDensity']+math.fsum(gauge[s]*donors[0]['q'][s] for s in q))+weight*(donors[1]['internalEnergyDensity']+math.fsum(gauge[s]*donors[1]['q'][s] for s in q))
        after=shiftedTarget-(ep+math.fsum(gauge[s]*q[s] for s in q))
        records.append(dict(weight=weight,conservativeRecovery=answer,pressurePreservingTemperature=tp,
                            energyDensityMismatch=before,gaugeMismatchDifference=after-before))
    return dict(donors=donors,records=records,scope='Two-donor common-weight conservative mixing; not a general flux impossibility theorem')

def version(exe):
    app=ROOT/'applications'/exe;source={p.name:sha(p) for p in app.iterdir() if p.suffix in ['.C','.H']}
    digest=hashlib.sha256(json.dumps(source,sort_keys=True).encode()).hexdigest();snapshot=STUDY/'sourceSnapshots'/digest
    if not snapshot.exists():
        snapshot.mkdir()
        for p in app.iterdir():
            if p.suffix in ['.C','.H']:shutil.copy2(p,snapshot/p.name)
        shutil.copytree(app/'Make',snapshot/'Make',ignore=shutil.ignore_patterns('linux*'))
        if (app/'originalV2012').exists():shutil.copytree(app/'originalV2012',snapshot/'originalV2012')
    return dict(source=source,sourceSnapshot=str(snapshot.relative_to(ROOT)),executable=exe,executableSHA256=sha(ROOT/'build/bin'/exe))

def run(mode,n,dt=20e-9,exe_override=None,component=None,tag=''):
    prefix='ThermoWave' if component is None else 'RoundoffThermoWave'
    tag=tag+('' if component is None else '_component'+('On' if component else 'Off'))
    name=f'{prefix}_{mode}_nx{n}_dt{dt:g}{tag}';case=RAW/name
    for filename in ['wave_result.json','failure.json']:
        if (case/filename).exists():return json.loads((case/filename).read_text())
    if case.exists():raise RuntimeError('Retained incomplete '+str(case))
    make_case(name,'uniform',nx=n,ny=1,dt=dt,steps=round(TF/dt))
    species=json.loads((case/'case.json').read_text())['species'];nasa=parse_nasa(case/'chemkin/therm.dat');initial=analytic(n,0,nasa,species)
    for s in species:field(case/'0'/s,initial[s])
    field(case/'0/T',initial['T'],'[0 0 0 1 0 0 0]');field(case/'0/U',(U,0,0),'[0 1 -1 0 0 0 0]',True)
    transport=case/'chemkin/transportProperties';transport.write_text(re.sub(r'(\bAs\s+)[^;]+;',r'\g<1>0;',transport.read_text()))
    change(case/'constant/chemistryProperties','chemistry','off')
    chem=case/'constant/chemistryProperties';chem.write_text(chem.read_text().replace('solver costOde','solver ode'))
    exe=exe_override or EXES[mode];reference=mode in ['central','hllc']
    if reference:central_schemes(case)
    else:(case/'system/controlDict').open('a').write(f'\nenergyLedger true; cellEnergyLedger true; cellLedgerEvery 0; energyCorrection {mode};\n')
    if component is not None:(case/'system/controlDict').open('a').write('componentEnergyTolerance '+('true' if component else 'false')+';\n')
    config=dict(name=name,mode=mode,kind='ThermoWave',nx=n,nCells=n,dt=dt,TF=TF,steps=round(TF/dt),ranks=1,
                **version(exe),componentEnergyTolerance=component,scope='Exact inviscid nonreacting unequal-NASA H2/N2 contact wave; chemistry and all transport coefficients zero')
    (case/'wave_experiment.json').write_text(json.dumps(config,indent=2)+'\n')
    try:
        wall=command(['mpirun','--bind-to','core','--map-by','core','--nooversubscribe','-np','1',exe],case,case/'solver.log',timeout=600) if reference else solve(case,1,exe=exe,timeout=600)
    except RuntimeError as error:
        result={**config,'failed':True,'error':str(error)};(case/'failure.json').write_text(json.dumps(result,indent=2)+'\n');print('RETAINED FAILURE',name,flush=True);return result
    end=case/format(TF,'.12g');actual={f:read_field(end/f,n) for f in ['rho','T','p']+species}
    actual['Ux']=[u[0] for u in read_field(end/'U',n)];exact=analytic(n,TF,nasa,species);errors={}
    for f in actual:
        d=[abs(x-y) for x,y in zip(actual[f],exact[f])];errors[f]=dict(L1=math.fsum(d)/n,L2=math.sqrt(math.fsum(x*x for x in d)/n),Linf=max(d))
    start=inventory(case,0,1);last=inventory(case,TF,1)
    with next(case.glob('**/'+('centralReference' if reference else 'cellEnergyLedger')+'/*/'+('rank0000.csv' if reference else 'totals_rank0000.csv'))).open() as stream:
        budgets=[{k:float(v) for k,v in row.items()} for row in csv.DictReader(stream)]
    eos=max(abs(actual['p'][i]/(actual['rho'][i]*actual['T'][i]*RU*math.fsum(actual[s][i]/nasa[s]['w'] for s in species))-1) for i in range(n))
    result=dict(**config,wall=wall,errors=errors,initial=start,end=last,signedEnergyDrift=(last['E_NASA']-start['E_NASA'])/abs(start['E_NASA']),
                massDrift=(last['mass']-start['mass'])/start['mass'],elementDrift={e:(last['elements'][e]-v)/v for e,v in start['elements'].items() if v>1e-20},
                sumYError=max(abs(math.fsum(actual[s][i] for s in species)-1) for i in range(n)),minY=min(min(actual[s]) for s in species),maxEOSRelative=eos,
                maxLocalEnergyResidual=max(r['maxLocalEnergyResidual' if reference else 'maxCellClosure'] for r in budgets))
    (case/'wave_result.json').write_text(json.dumps(result,indent=2)+'\n')
    print(name,'T L1',errors['T']['L1'],'p Linf',errors['p']['Linf'],'E',result['signedEnergyDrift'],flush=True);return result

def main():
    nasa=parse_nasa(next(RAW.glob('HLLC_B_*/chemkin/therm.dat')))
    (STUDY/'data/processed/mixture_mixing_identity.json').write_text(json.dumps(mixing_identity(nasa),indent=2)+'\n')
    if len(sys.argv)>1 and sys.argv[1]=='algebra':return
    sizes=[32] if len(sys.argv)>1 and sys.argv[1]=='pilot' else [32,64,128]
    for n in sizes:
        for mode in EXES:run(mode,n)
    rows=[json.loads(p.read_text()) for p in sorted(RAW.glob('ThermoWave_*/wave_result.json'))]
    (STUDY/'data/processed/mixture_wave.json').write_text(json.dumps(rows,indent=2)+'\n')
if __name__=='__main__':main()
