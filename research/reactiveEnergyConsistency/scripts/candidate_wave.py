"""Analytic entropy-wave falsification of conservative candidate accuracy."""
from pathlib import Path
import hashlib,json,math,re,shutil
from exact_wave import analytic,CP,W,R,P,U0,TF
from caseFactory import make_case,header,field,command
from foamio import read_field
from candidate_screen import sha
ROOT=Path(__file__).resolve().parents[1];STUDY=ROOT/'candidateStudy'
def run(mode,nx,dt):
    name=f'Wave_{mode}_nx{nx}_dt{dt:g}';case=STUDY/'data/raw'/name
    if (case/'wave_result.json').exists():return json.loads((case/'wave_result.json').read_text())
    if case.exists():raise RuntimeError('Retained incomplete '+str(case))
    make_case(name,'uniform',nx=nx,ny=1,dt=dt,steps=round(TF/dt))
    rho,T=analytic(nx,0);field(case/'0/T',T,'[0 0 0 1 0 0 0]');field(case/'0/U',(U0,0,0),'[0 1 -1 0 0 0 0]',True)
    field(case/'0/N2',1.)
    (case/'constant/thermophysicalProperties').write_text(header('thermophysicalProperties')+
      'thermoType { type hePsiThermo; mixture reactingMixture; transport const; thermo hConst; energy sensibleEnthalpy; equationOfState perfectGas; specie specie; }\ninertSpecie N2; chemistryReader foamChemistryReader; foamChemistryFile "<case>/constant/reactions"; foamChemistryThermoFile "<case>/constant/thermo";\n')
    (case/'constant/reactions').write_text(header('reactions')+'species (N2); reactions {}\n')
    (case/'constant/thermo').write_text(header('thermo')+f'N2 {{ specie {{ molWeight {W}; }} thermodynamics {{ Cp {CP}; Hf 0; }} transport {{ mu 0; Pr 1; }} }}\n')
    cp=case/'constant/chemistryProperties';cp.write_text(re.sub(r'\bchemistry\s+on;','chemistry off;',cp.read_text()).replace('solver costOde','solver ode'))
    control=case/'system/controlDict';control.open('a').write(f'\nenergyLedger true; cellEnergyLedger true; cellLedgerEvery 0; energyCorrection {mode};\n')
    wall=command(['mpirun','--bind-to','core','--map-by','core','--nooversubscribe','-np','1','reactingEnergyCandidates'],case,case/'solver.log',timeout=300)
    end=case/format(TF,'.12g');rr=read_field(end/'rho',nx);tt=read_field(end/'T',nx);pp=read_field(end/'p',nx);uu=read_field(end/'U',nx)
    exactR,exactT=analytic(nx,TF);errors={}
    for key,vals,exact in [('rho',rr,exactR),('T',tt,exactT),('p',pp,[P]*nx),('Ux',[u[0] for u in uu],[U0]*nx)]:
        ds=[abs(v-e) for v,e in zip(vals,exact)];errors[key]=dict(L1=math.fsum(ds)/nx,L2=math.sqrt(math.fsum(d*d for d in ds)/nx),Linf=max(ds))
    v=.02*.008*.001/nx
    E0=math.fsum(v*(r*(CP*(t-298.15)+U0*U0/2)-P) for r,t in zip(rho,T))
    Ef=math.fsum(v*(r*(CP*(t-298.15)+sum(x*x for x in u)/2)-p) for r,t,p,u in zip(rr,tt,pp,uu))
    result=dict(name=name,mode=mode,nx=nx,dt=dt,wall=wall,errors=errors,E0=E0,Ef=Ef,signedEnergyDrift=(Ef-E0)/abs(E0),
      massDrift=(math.fsum(rr)-math.fsum(rho))/math.fsum(rho),executableSHA256=sha(ROOT/'build/bin/reactingEnergyCandidates'),
      scope='Unforced constant-Cp perfect-gas entropy wave, zero chemistry/transport; same analytic and model reference as preserved baseline')
    (case/'wave_result.json').write_text(json.dumps(result,indent=2)+'\n');print(name,'T L1',errors['T']['L1'],'U Linf',errors['Ux']['Linf'],'E',result['signedEnergyDrift'],flush=True)
    return result
records=[]
for nx in [32,64,128]:
    for mode in ['none','conservativeState']:records.append(run(mode,nx,20e-9))
for dt in [200e-9,100e-9,50e-9]:records.append(run('conservativeState',128,dt))
(STUDY/'data/processed/candidate_wave.json').write_text(json.dumps(records,indent=2)+'\n')
