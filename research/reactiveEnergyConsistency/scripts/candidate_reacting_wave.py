"""Exact finite-rate isomerization in an advecting compressible entropy wave."""
from pathlib import Path
import csv,hashlib,json,math,re,sys
from exact_wave import analytic,CP,W,R,P,U0,TF
from caseFactory import make_case,header,field,command
from foamio import read_field
from candidate_screen import sha
ROOT=Path(__file__).resolve().parents[1];STUDY=ROOT/'candidateStudy'
RATE=5e4;HF=2e6
def composition(nx,t):
    a=[(.5+.2*math.cos(2*math.pi*((i+.5)/nx-U0*t/.02)))*math.exp(-RATE*t) for i in range(nx)]
    return a,[1-x for x in a]
def run(mode,nx,dt):
    name=f'ReactingWave_{mode}_nx{nx}_dt{dt:g}_v2';case=STUDY/'data/raw'/name
    if (case/'wave_result.json').exists():return json.loads((case/'wave_result.json').read_text())
    if (case/'failure.json').exists():return json.loads((case/'failure.json').read_text())
    if case.exists():raise RuntimeError('Retained incomplete '+str(case))
    make_case(name,'uniform',nx=nx,ny=1,dt=dt,steps=round(TF/dt))
    info=json.loads((case/'case.json').read_text());info['species']=['A','B'];(case/'case.json').write_text(json.dumps(info,indent=2)+'\n')
    rho,T=analytic(nx,0);ya,yb=composition(nx,0)
    field(case/'0/T',T,'[0 0 0 1 0 0 0]');field(case/'0/U',(U0,0,0),'[0 1 -1 0 0 0 0]',True)
    field(case/'0/A',ya);field(case/'0/B',yb)
    (case/'constant/thermophysicalProperties').write_text(header('thermophysicalProperties')+
      'thermoType { type hePsiThermo; mixture reactingMixture; transport const; thermo hConst; energy sensibleEnthalpy; equationOfState perfectGas; specie specie; }\ninertSpecie B; chemistryReader foamChemistryReader; foamChemistryFile "<case>/constant/reactions"; foamChemistryThermoFile "<case>/constant/thermo";\n')
    (case/'constant/reactions').write_text(header('reactions')+f'species (A B); reactions {{ isomerization {{ type irreversibleArrheniusReaction; reaction "A = B"; A {RATE}; beta 0; Ta 0; }} }}\n')
    const=f'specie {{ molWeight {W}; }} thermodynamics {{ Cp {CP}; Hf {HF}; }} transport {{ mu 0; Pr 1; }}'
    (case/'constant/thermo').write_text(header('thermo')+'A { '+const+' }\nB { '+const+' }\n')
    cp=case/'constant/chemistryProperties';cp.write_text(cp.read_text().replace('solver costOde','solver ode'))
    control=case/'system/controlDict';control.open('a').write(f'\nenergyLedger true; cellEnergyLedger true; cellLedgerEvery 0; energyCorrection {mode};\n')
    exe='reactingEnergyBlockCandidates' if mode=='blockConservative' else 'reactingEnergyCandidates'
    sourceCase=STUDY/f'data/raw/F_{mode}_dt1e-06_s1_g0_o1_p1_timing3/result.json'
    original=json.loads(sourceCase.read_text());assert sha(ROOT/'build/bin'/exe)==original['executableSHA256']
    provenance={k:original[k] for k in ['source','sourceSnapshot','executableSHA256']}
    config=dict(name=name,mode=mode,nx=nx,dt=dt,TF=TF,rate=RATE,Hf=HF,
        executable=exe,**provenance,scope='Analytic synthetic reacting transport; equal-property nitrogen isomers, no reaction heat, not a flame benchmark')
    (case/'wave_experiment.json').write_text(json.dumps(config,indent=2)+'\n')
    try:wall=command(['mpirun','--bind-to','core','--map-by','core','--nooversubscribe','-np','1',exe],case,case/'solver.log',timeout=600)
    except RuntimeError as e:
        result={**config,'failed':True,'error':str(e)};(case/'failure.json').write_text(json.dumps(result,indent=2)+'\n');print('RETAINED FAILURE',name,flush=True);return result
    end=case/format(TF,'.12g');rr=read_field(end/'rho',nx);tt=read_field(end/'T',nx);pp=read_field(end/'p',nx);uu=read_field(end/'U',nx)
    aa=read_field(end/'A',nx);bb=read_field(end/'B',nx)
    exactR,exactT=analytic(nx,TF);exactA,exactB=composition(nx,TF);errors={}
    for key,vals,exact in [('rho',rr,exactR),('T',tt,exactT),('p',pp,[P]*nx),('Ux',[u[0] for u in uu],[U0]*nx),('A',aa,exactA),('B',bb,exactB)]:
        ds=[abs(v-e) for v,e in zip(vals,exact)];errors[key]=dict(L1=math.fsum(ds)/nx,L2=math.sqrt(math.fsum(x*x for x in ds)/nx),Linf=max(ds))
    v=.02*.008*.001/nx
    E0=math.fsum(v*(r*(CP*(t-298.15)+HF+U0*U0/2)-P) for r,t in zip(rho,T))
    Ef=math.fsum(v*(r*(CP*(t-298.15)+HF+sum(x*x for x in u)/2)-p) for r,t,p,u in zip(rr,tt,pp,uu))
    totals=[]
    for path in case.glob('**/cellEnergyLedger/*/totals_rank*.csv'):
        with path.open() as f:totals.extend({k:float(v) for k,v in row.items()} for row in csv.DictReader(f))
    result=dict(**config,wall=wall,errors=errors,E0=E0,Ef=Ef,signedEnergyDrift=(Ef-E0)/abs(E0),
        massDrift=(math.fsum(rr)-math.fsum(rho))/math.fsum(rho),
        sumYError=max(abs(a+b-1) for a,b in zip(aa,bb)),minY=min(aa+bb),
        maxCellClosure=max(r['maxCellClosure'] for r in totals),
        maxEOSRelative=max(r['maxEOSRelative'] for r in totals),
        maxMomentumDeltaU=max(r['maxMomentumDeltaU'] for r in totals))
    (case/'wave_result.json').write_text(json.dumps(result,indent=2)+'\n')
    print(name,'T L1',errors['T']['L1'],'A L1',errors['A']['L1'],'E',result['signedEnergyDrift'],flush=True);return result
def main():
    records=[]
    sizes=[32] if len(sys.argv)>1 and sys.argv[1]=='pilot' else [32,64,128]
    for nx in sizes:
        for mode in ['none','conservativeState','blockConservative']:records.append(run(mode,nx,20e-9))
    if sizes!=[32]:
        for dt in [200e-9,100e-9,50e-9]:
            for mode in ['none','conservativeState','blockConservative']:records.append(run(mode,128,dt))
    (STUDY/'data/processed/candidate_reacting_wave.json').write_text(json.dumps(records,indent=2)+'\n')
if __name__=='__main__':main()
