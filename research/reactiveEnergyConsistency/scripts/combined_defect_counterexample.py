"""Exactly solved conservative FV contact wave with blind defect indicators."""
from pathlib import Path
import cmath,hashlib,json,math
ROOT=Path(__file__).resolve().parents[1];STUDY=ROOT/'candidateStudy'
L=.02;U=40.;P=101325.;R=300.;CV=700.;DT=20e-9;TF=100e-6;AMP=.15

def experiment(n):
    dx=L/n;theta=2*math.pi/n;steps=round(TF/DT);rho0=P/(800*R)
    g=1/(1+U*DT/dx*(1-cmath.exp(-1j*theta)))
    phases=[theta*(i+.5) for i in range(n)]
    state=lambda amp:[rho0*(1+AMP*(cmath.exp(1j*x)*amp).real) for x in phases]
    rho=state(g**steps);old=state(g**(steps-1));initial=state(1.)
    exact=state(cmath.exp(-1j*2*math.pi*U*TF/L))
    energy=lambda values:[CV/R*P+.5*U*U*x for x in values]
    ea=energy(rho);ea_old=energy(old)
    massResidual=[(rho[i]-old[i])/DT+U/dx*(rho[i]-rho[(i-1)%n]) for i in range(n)]
    momentumResidual=[U*r for r in massResidual]
    energyResidual=[(ea[i]-ea_old[i])/DT+U/dx*(ea[i]-ea[(i-1)%n]) for i in range(n)]
    temp=[P/(R*x) for x in rho];texact=[P/(R*x) for x in exact];errors=[abs(a-b) for a,b in zip(temp,texact)]
    return dict(nx=n,dt=DT,TF=TF,steps=steps,densityAmplificationMagnitude=abs(g**steps),
                temperatureError=dict(L1=math.fsum(errors)/n,L2=math.sqrt(math.fsum(x*x for x in errors)/n),Linf=max(errors)),
                relativeMassResidual=max(abs(x) for x in massResidual)/(max(rho)/DT),
                relativeMomentumResidual=max(abs(x) for x in momentumResidual)/(U*max(rho)/DT),
                relativeEnergyResidual=max(abs(x) for x in energyResidual)/(max(ea)/DT),
                relativeMassInventoryChange=(math.fsum(rho)-math.fsum(initial))/math.fsum(initial),
                relativeEnergyInventoryChange=(math.fsum(ea)-math.fsum(energy(initial)))/math.fsum(energy(initial)),
                finalPressureCorrection=0.,sourceStepError=0.,minDensity=min(rho),minT=min(temp),
                rhoNumerical=rho,rhoExact=exact,temperatureNumerical=temp,temperatureExact=texact)

def main():
    rows=[experiment(n) for n in [32,64,128]]
    orders=[math.log(a['temperatureError']['L1']/b['temperatureError']['L1'],2) for a,b in zip(rows,rows[1:])]
    cfg=dict(scriptSHA256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),L=L,u=U,p=P,R=R,Cv=CV,amplitude=AMP,dt=DT,TF=TF,
             scope='Exact discrete Fourier solution of a common conservative Euler/upwind contact wave. Not a native CFD run, new method or detailed reacting validation.')
    result=dict(configuration=cfg,records=rows,observedTemperatureOrders=orders,
                decision='REJECT guaranteed accuracy control based only on energy conservation defect, final pressure/momentum mismatch and chemistry step error. Resolved truncation information is separately necessary.')
    raw=STUDY/'data/raw/CombinedDefect_analytic';raw.mkdir(exist_ok=True)
    (raw/'controller_experiment.json').write_text(json.dumps(cfg,indent=2)+'\n')
    (raw/'controller_result.json').write_text(json.dumps(result,indent=2)+'\n')
    (STUDY/'data/processed/combined_defect_counterexample.json').write_text(json.dumps(result,indent=2)+'\n')
    for r in rows:print(r['nx'],'Terror',r['temperatureError'],'mass/momentum/energy residuals',[r[k] for k in ['relativeMassResidual','relativeMomentumResidual','relativeEnergyResidual']])
    print('T orders',orders)
if __name__=='__main__':main()
