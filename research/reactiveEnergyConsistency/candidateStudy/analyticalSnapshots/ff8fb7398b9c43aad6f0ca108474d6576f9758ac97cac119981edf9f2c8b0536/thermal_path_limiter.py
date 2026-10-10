"""Exact, predeclared positivity-limiter counterexample; preserve bare evidence."""
from pathlib import Path
import hashlib,json
from thermal_path_taylor import CP,CV,Q,T0,Y0,run
ROOT=Path(__file__).resolve().parents[1];STUDY=ROOT/'candidateStudy'

def main():
    k0,a,dt=1e6,50.,4e-6
    baseline=run(k0,a,dt,dt,False)
    bare=run(k0,a,dt,dt,True)
    cp=bare['endpoint']['cpEndpoint'];delta=bare['endpoint']['taylorCorrection']
    # One common multiplier preserves the linear A+B invariant. A tiny
    # predeclared interior margin avoids reporting a rounded negative endpoint.
    theta=min(1.,(1.-1e-12)*cp/(-delta)) if delta<0 else 1.
    y=cp+theta*delta;t=T0+Q*(Y0-y)/CV;p=(CP-CV)*t
    target=baseline['reference'];initialEnergy=CV*T0+Q*Y0
    limited=dict(theta=theta,Y_A=y,Y_B=1-y,T=t,p=p,
                 admissible=0<=y<=1 and t>0 and p>0,
                 temperatureError=abs(t-target['T']),speciesError=abs(y-target['Y_A']),
                 massResidual=y+(1-y)-1.,
                 energyResidual=CV*t+Q*y-initialEnergy,
                 eosResidual=p-(CP-CV)*t)
    config=dict(Cp=CP,Cv=CV,Q=Q,Tinitial=T0,Yinitial=Y0,rho=1.,k0=k0,a=a,dt=dt,TF=dt,
                interiorMargin=1e-12,
                scriptSHA256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
                sourceMapSHA256=hashlib.sha256((ROOT/'scripts/thermal_path_taylor.py').read_bytes()).hexdigest(),
                scope='Exact synthetic source maps. One predeclared weak-feedback/stiff-step counterexample, not detailed chemistry or a universal result for other limiters.')
    result=dict(configuration=config,baseline=baseline,bare=bare,limited=limited,
                limitedToBaselineTemperatureErrorRatio=limited['temperatureError']/baseline['temperatureError'],
                decision='REJECT guaranteed accuracy-improvement claim for common positivity scaling of this macro Taylor correction. Positivity and conservative closure do not ensure a more accurate source trajectory.')
    raw=STUDY/'data/raw/ThermalTaylor_limiterWeakFeedback';raw.mkdir(exist_ok=True)
    (raw/'taylor_experiment.json').write_text(json.dumps(config,indent=2)+'\n')
    (raw/'taylor_result.json').write_text(json.dumps(result,indent=2)+'\n')
    (STUDY/'data/processed/thermal_path_limiter.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result,indent=2))
if __name__=='__main__':main()
