"""Unforced exact Euler entropy wave plus a matched density-based reference.

This verifies a nonreacting subset, not a general forced reacting MMS.
Constant Cp/EOS and zero transport eliminate model mismatch with rhoCentralFoam.
"""
from pathlib import Path
import json,math,re,shutil
from caseFactory import make_case,header,field,command
from thermo_reference import RU
from foamio import read_field
ROOT=Path(__file__).resolve().parents[1]
CP=1000.;W=28.0134;R=RU/W;P=101325.;U0=40.;TBAR=800.;RHOBAR=P/(R*TBAR);TF=20e-6
def analytic(nx,t):
    rho=[RHOBAR*(1+.05*math.sin(2*math.pi*((i+.5)/nx-U0*t/.02))) for i in range(nx)]
    return rho,[P/(R*r) for r in rho]
def run(nx,dt,density=False):
    name=f'exact2_{"density" if density else "pressure"}_nx{nx}_dt{dt:g}';case=ROOT/'data/raw'/name
    if (case/'mms_result.json').exists():return json.loads((case/'mms_result.json').read_text())
    if case.exists():raise RuntimeError('retained incomplete exact case: '+str(case))
    make_case(name,'uniform',nx=nx,ny=1,dt=dt,steps=round(TF/dt))
    rho,T=analytic(nx,0);field(case/'0/T',T,'[0 0 0 1 0 0 0]');field(case/'0/U',(U0,0,0),'[0 1 -1 0 0 0 0]',True)
    field(case/'0/N2',1.)
    const=f'specie {{ molWeight {W}; }} thermodynamics {{ Cp {CP}; Hf 0; }} transport {{ mu 0; Pr 1; }}'
    constE=f'specie {{ molWeight {W}; }} thermodynamics {{ Cv {CP-R:.17g}; Hf 0; Eref {-R*298.15:.17g}; }} transport {{ mu 0; Pr 1; }}'
    (case/'constant/thermophysicalProperties').write_text(header('thermophysicalProperties')+(
      f'thermoType {{ type hePsiThermo; mixture pureMixture; transport const; thermo eConst; energy sensibleInternalEnergy; equationOfState perfectGas; specie specie; }}\nmixture {{ {constE} }}\n'
      if density else f'thermoType {{ type hePsiThermo; mixture reactingMixture; transport const; thermo hConst; energy sensibleEnthalpy; equationOfState perfectGas; specie specie; }}\ninertSpecie N2; chemistryReader foamChemistryReader; foamChemistryFile "<case>/constant/reactions"; foamChemistryThermoFile "<case>/constant/thermo";\n'))
    (case/'constant/reactions').write_text(header('reactions')+'species (N2); reactions {}\n')
    (case/'constant/thermo').write_text(header('thermo')+'N2 { '+const+' }\n')
    cp=case/'constant/chemistryProperties';cp.write_text(re.sub(r'\bchemistry\s+on;', 'chemistry off;',cp.read_text()).replace('solver costOde','solver ode'))
    control=case/'system/controlDict';control.write_text(control.read_text().replace('padTiming true;','padTiming false;')+'\nenergyLedger '+('false' if density else 'true')+';\n')
    if density:
        tutorial=Path('/opt/OpenFOAM/OpenFOAM-v2012/tutorials/compressible/rhoCentralFoam/shockTube/system')
        for f in ['fvSchemes','fvSolution']:shutil.copy2(tutorial/f,case/'system'/f)
        s=case/'system/fvSchemes';s.write_text(re.sub(r'vanLeerV?','upwind',s.read_text()))
    exe='rhoCentralFoam' if density else 'reactingEnergyAudit'
    wall=command(['mpirun','--bind-to','core','--map-by','core','--nooversubscribe','-np','1',exe],case,case/'solver.log',timeout=180)
    end=case/format(TF,'.12g');rr=read_field(end/'rho',nx) if (end/'rho').exists() else None
    tt=read_field(end/'T',nx);pp=read_field(end/'p',nx);uu=read_field(end/'U',nx)
    if rr is None:rr=[p/(R*t) for p,t in zip(pp,tt)]
    exactR,exactT=analytic(nx,TF);errors={}
    for name,values,exact in [('rho',rr,exactR),('T',tt,exactT),('p',pp,[P]*nx),('Ux',[u[0] for u in uu],[U0]*nx)]:
        ds=[abs(v-e) for v,e in zip(values,exact)];errors[name]=dict(L1=math.fsum(ds)/nx,L2=math.sqrt(math.fsum(d*d for d in ds)/nx),Linf=max(ds))
    volume=.02*.008*.001/nx
    def energy(r,t,p,u):return math.fsum(volume*(ri*(CP*(ti-298.15)+sum(x*x for x in ui)/2)-pi) for ri,ti,pi,ui in zip(r,t,p,u))
    E0=energy(rho,T,[P]*nx,[(U0,0,0)]*nx);Ef=energy(rr,tt,pp,uu)
    result=dict(name=case.name,nx=nx,dt=dt,solver=exe,wall=wall,errors=errors,E0=E0,Ef=Ef,signedEnergyDrift=(Ef-E0)/abs(E0),
      massDrift=(math.fsum(rr)-math.fsum(rho))/math.fsum(rho),scope='same constant-Cp perfect gas, zero viscosity/conduction/chemistry, mesh and dt; upwind reconstruction but different pressure and Kurganov convective fluxes')
    (case/'mms_result.json').write_text(json.dumps(result,indent=2)+'\n');print('EXACT',case.name,'T_L1',errors['T']['L1'],'E drift',result['signedEnergyDrift'],flush=True)
    return result
def main():
    records=[]
    for nx in [32,64,128]:
        for density in [False,True]:records.append(run(nx,.02e-6,density))
    for dt in [.2e-6,.1e-6,.05e-6]:records.append(run(128,dt))
    # Extend cached run metadata from the actual stored final fields.
    for r in records:
        end=ROOT/'data/raw'/r['name']/format(TF,'.12g')
        r.update(minT=min(read_field(end/'T',r['nx'])),minP=min(read_field(end/'p',r['nx'])),
                 minY=1.,sumYError=0.,elementDrift={'N':r['massDrift']})
        (end.parent/'mms_result.json').write_text(json.dumps(r,indent=2)+'\n')
    orders=[]
    for exe in ['reactingEnergyAudit','rhoCentralFoam']:
        rs=sorted([r for r in records if r['solver']==exe and r['dt']==.02e-6],key=lambda r:r['nx'])
        for a,b in zip(rs,rs[1:]):orders.append(dict(solver=exe,nx0=a['nx'],nx1=b['nx'],T_L1_order=math.log(a['errors']['T']['L1']/b['errors']['T']['L1'])/math.log(2)))
    temporal=sorted([r for r in records if r['solver']=='reactingEnergyAudit' and r['nx']==128 and r['dt']>=.05e-6],key=lambda r:r['dt'],reverse=True)
    differences=[]
    for a,b in zip(temporal,temporal[1:]):
        va=read_field(ROOT/'data/raw'/a['name']/format(TF,'.12g')/'T',128)
        vb=read_field(ROOT/'data/raw'/b['name']/format(TF,'.12g')/'T',128)
        ds=[abs(x-y) for x,y in zip(va,vb)]
        differences.append(dict(dt0=a['dt'],dt1=b['dt'],T_L1=math.fsum(ds)/128,
           T_L2=math.sqrt(math.fsum(d*d for d in ds)/128),T_Linf=max(ds)))
    self_order=math.log(differences[0]['T_L1']/differences[1]['T_L1'])/math.log(2)
    (ROOT/'data/processed/exact_wave.json').write_text(json.dumps(dict(records=records,spatialOrders=orders,
      temporalSelfDifferences=differences,temporalSelfOrderT_L1=self_order,
      temporalNote='Fixed-grid total field error has a spatial floor. Self-differences estimate temporal order of this smooth nonreacting discrete solution; this is not a formal coupled reacting MMS.'),indent=2)+'\n')
if __name__=='__main__':main()
