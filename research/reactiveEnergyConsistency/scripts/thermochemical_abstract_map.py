"""Small finite-map falsification model; prescribed extent, not kinetic reference."""
from pathlib import Path
import json,math,sys
ROOT=Path(__file__).resolve().parents[1]
sys.dont_write_bytecode=True
sys.path.append(str(ROOT.parent/'physicsAwareDecomposition/scripts'))
sys.path.append(str(ROOT.parent/'physicsAwareDecomposition/actionStudy/scripts'))
from thermo_reference import parse_nasa,ha,RU,ATOMIC
from thermo_continuity import CONTROL,sha
RAW=ROOT/'candidateStudy/data/raw';P=ROOT/'candidateStudy/data/processed'
TARGET=RAW/'ThermochemicalAbstractMap_v1'
Y0={'H2':.0283,'O2':.225,'H2O':0.,'N2':.7467}
NU={'H2':-1.,'O2':-.5,'H2O':1.,'N2':0.}

def state(data,Y,T,rho=None,p=None):
    R=math.fsum(Y[s]*RU/data[s]['w'] for s in Y)
    h=math.fsum(Y[s]*ha(data[s],T) for s in Y)
    hc=math.fsum(Y[s]*ha(data[s],298.15) for s in Y)
    if rho is None:rho=p/(R*T)
    else:p=rho*R*T
    return dict(T=T,Y=Y,rho=rho,p=p,R=R,ha=h,hc=hc,hs=h-hc,ea=h-R*T)

def recover(data,Y,target,property):
    lo,hi=200.,3500.
    assert state(data,Y,lo,rho=1)[property]<=target<=state(data,Y,hi,rho=1)[property]
    for _ in range(60):
        mid=(lo+hi)/2;v=state(data,Y,mid,rho=1)[property]
        if v>target:hi=mid
        else:lo=mid
    return (lo+hi)/2

def element(data,Y,e):
    return math.fsum(Y[s]*data[s]['elements'].get(e,0)*ATOMIC[e]/data[s]['w'] for s in Y)

def main():
    result=TARGET/'map_result.json'
    if result.exists():
        (P/'thermochemical_abstract_map.json').write_bytes(result.read_bytes());print('Reused immutable abstract maps');return
    if TARGET.exists():raise RuntimeError('Retained incomplete abstract-map experiment')
    TARGET.mkdir();(TARGET/'driver_snapshot.py').write_bytes(Path(__file__).read_bytes())
    source=CONTROL/'CpHS.dat';(TARGET/'therm.dat').write_bytes(source.read_bytes());data=parse_nasa(source)
    records=[];k=50000.
    for T0 in [500.,1100.,1500.]:
     for dt in [1e-6,1e-5,1e-4]:
      for constraint in ['CV','CP']:
        old=state(data,Y0,T0,p=101325.)
        # Prescribed finite reaction H2 + O2/2 -> H2O. This is not the real
        # 27-reaction dynamics; it tests only the algebraic interface claim.
        maximum=.15*Y0['H2']/data['H2']['w']
        extent=maximum*(-math.expm1(-k*dt))
        dy={s:NU[s]*data[s]['w']*extent for s in Y0};Y={s:Y0[s]+dy[s] for s in Y0}
        prop='ea' if constraint=='CV' else 'ha';T1=recover(data,Y,old[prop],prop)
        new=state(data,Y,T1,**({'rho':old['rho']} if constraint=='CV' else {'p':old['p']}))
        formation=math.fsum(ha(data[s],298.15)*dy[s] for s in Y)
        sensible=new['hs']-old['hs'];pressure_specific=(new['p']-old['p'])/old['rho']
        rr={s:old['rho']*dy[s]/dt for s in Y}
        qdot=-math.fsum(ha(data[s],298.15)*rr[s] for s in Y)
        finite_cancel=dt*qdot+old['rho']*formation
        instantaneous=-old['rho']*math.fsum(ha(data[s],298.15)*NU[s]*data[s]['w']*k*maximum for s in Y)
        no_dp_T=recover(data,Y,old['hs']-formation,'hs')
        no_dp=state(data,Y,no_dp_T,rho=old['rho'])
        records.append(dict(constraint=constraint,Tinitial=T0,dt=dt,old=old,new=new,extent=extent,
          maxElementResidual=max(abs(element(data,Y,e)-element(data,Y0,e)) for e in ['H','O','N']),
          massResidual=math.fsum(dy.values()),minY=min(Y.values()),specificInvariantResidual=new[prop]-old[prop],
          finiteSensibleIdentityResidual=sensible+formation-(pressure_specific if constraint=='CV' else 0),
          finiteRRCancellation=finite_cancel,instantaneousHeatMismatch=dt*(instantaneous-qdot),
          formationOnlyCVResidual=old['rho']*(no_dp['ea']-old['ea']),
          formationOnlyCVPressureChange=no_dp['p']-old['p']))
    # Same composition after exact chemistry; two unequal energies. Opposite
    # density changes preserve global mass/elements/species. EOS is exact.
    # This is a post-map operator counterexample, not a simulated flow solver.
    endpoints=[]
    extent=.08*Y0['H2']/data['H2']['w'];Y={s:Y0[s]+NU[s]*data[s]['w']*extent for s in Y0}
    for T0 in [700.,1300.]:
        old=state(data,Y0,T0,rho=1.)
        endpoints.append(state(data,Y,recover(data,Y,old['ea'],'ea'),rho=1.))
    epsilon=.01;post=[state(data,Y,s['T'],rho=s['rho']+(epsilon if i==0 else -epsilon)) for i,s in enumerate(endpoints)]
    energy=lambda states:math.fsum(s['rho']*s['ea'] for s in states)
    drhoH=math.fsum((b['rho']-a['rho'])*a['hs'] for a,b in zip(endpoints,post))
    drhoC=math.fsum((b['rho']-a['rho'])*a['hc'] for a,b in zip(endpoints,post))
    dp=-math.fsum(b['p']-a['p'] for a,b in zip(endpoints,post))
    counter=dict(before=endpoints,after=post,unitCellVolume=1.,energyChange=energy(post)-energy(endpoints),DrhoH=drhoH,DrhoC=drhoC,Dpressure=dp,
      identityClosure=energy(post)-energy(endpoints)-drhoH-drhoC-dp,
      massChange=math.fsum(s['rho'] for s in post)-math.fsum(s['rho'] for s in endpoints),
      maxSpeciesInventoryChange=max(abs(math.fsum(s['rho']*s['Y'][name] for s in post)-math.fsum(s['rho']*s['Y'][name] for s in endpoints)) for name in Y))
    payload=dict(driverSHA256=sha(__file__),thermoSHA256=sha(source),records=records,postMapCounterexample=counter,
      scope='Independent Python continuous NASA evaluation. Prescribed mass-balanced extent with variable Cp and CV/physical CP inversion. Finite-source algebra and post-map density counterexample only; not a kinetic model validation, flow reference, new method or cost benchmark.')
    result.write_text(json.dumps(payload,indent=2)+'\n');(P/'thermochemical_abstract_map.json').write_bytes(result.read_bytes())
    print('Finite maps',len(records),'post-map energy change',counter['energyChange'],'closure',counter['identityClosure'])
if __name__=='__main__':main()
