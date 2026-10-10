"""Exact source-map pre-screen: local order and stiff positivity counterexample."""
from pathlib import Path
import hashlib,json,math
ROOT=Path(__file__).resolve().parents[1];STUDY=ROOT/'candidateStudy'
CP=1000.;CV=700.;Q=2e6;T0=1000.;Y0=.5
def exact_source(y,k,b,dt):
    total=k+b*y;z=math.exp(-total*dt)
    return total*y*z/(k+b*y*z)
def run(k0,a,dt,tf,compensate):
    y=Y0;temperature=T0;minY=y;records=[];initialEnergy=CV*T0+Q*Y0
    for i in range(round(tf/dt)):
        k=k0+a*(temperature-T0)
        if k<=0:raise RuntimeError('Outside positive affine-rate model')
        cp_end=exact_source(y,k,a*Q/CP,dt)
        correction=-.5*dt*dt*a*Q*k*y*y*(1/CV-1/CP) if compensate else 0.
        y=cp_end+correction;temperature=T0+Q*(Y0-y)/CV;minY=min(minY,y,1-y)
        records.append(dict(time=(i+1)*dt,Y_A=y,Y_B=1-y,T=temperature,p=(CP-CV)*temperature,
                            cpEndpoint=cp_end,taylorCorrection=correction,
                            energyResidual=CV*temperature+Q*y-initialEnergy))
        if y<0 or y>1:break # Keep the non-admissible state; no clipping/repair.
    target=exact_source(Y0,k0,a*Q/CV,tf);targetT=T0+Q*(Y0-target)/CV
    return dict(k0=k0,a=a,dt=dt,TF=tf,compensated=compensate,admissible=minY>=0,
                endpoint=records[-1],reference=dict(Y_A=target,T=targetT),
                temperatureError=abs(temperature-targetT),speciesError=abs(y-target),minY=minY,
                maxEnergyResidual=max(abs(r['energyResidual']) for r in records),trajectory=records)
def main():
    raw=STUDY/'data/raw/ThermalTaylor_analytic';raw.mkdir(exist_ok=True)
    config=dict(Cp=CP,Cv=CV,Q=Q,Tinitial=T0,Yinitial=Y0,rho=1.,
                scriptSHA256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
                scope='Exact autonomous equal-property synthetic source maps. No native CFD/detailed flame or new-method novelty claim.')
    (raw/'taylor_experiment.json').write_text(json.dumps(config,indent=2)+'\n')
    rows=[]
    for dt in [2e-6,1e-6,.5e-6,.25e-6]:
        for flag in [False,True]:rows.append(dict(regime='smooth',**run(1e5,100.,dt,10e-6,flag)))
    for flag in [False,True]:rows.append(dict(regime='stiff',**run(1e7,1000.,2e-6,2e-6,flag)))
    orders=[]
    for flag in [False,True]:
        seq=[r for r in rows if r['regime']=='smooth' and r['compensated']==flag]
        for coarse,fine in zip(seq,seq[1:]):orders.append(dict(compensated=flag,coarseDt=coarse['dt'],fineDt=fine['dt'],order=math.log(coarse['temperatureError']/fine['temperatureError'],2)))
    result=dict(configuration=config,records=rows,orders=orders,
                decision='REJECT naked macro Taylor source compensation as a generally admissible stiff source update. Formal local order gain in the smooth limit does not satisfy the reacting positivity/stability gate.')
    (raw/'taylor_result.json').write_text(json.dumps(result,indent=2)+'\n')
    (STUDY/'data/processed/thermal_path_taylor.json').write_text(json.dumps(result,indent=2)+'\n')
    for r in rows:print(r['regime'],r['compensated'],r['dt'],'Terror',r['temperatureError'],'minY',r['minY'])
    print('orders',orders)
if __name__=='__main__':main()
