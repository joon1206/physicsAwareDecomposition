"""Minimal known endpoint projection; tests valid thermo and trajectory limits."""
from pathlib import Path
import json,math,sys,time
ROOT=Path(__file__).resolve().parents[1];sys.dont_write_bytecode=True
sys.path.insert(0,str(ROOT/'build/canteraPackages'))
sys.path.append(str(ROOT.parent/'physicsAwareDecomposition/scripts'))
sys.path.append(str(ROOT.parent/'physicsAwareDecomposition/actionStudy/scripts'))
import cantera as ct
import numpy as np
from ruamel.yaml import YAML
from thermo_continuity import properties,repair,sha
from thermo_reference import RU
STUDY=ROOT/'candidateStudy';RAW=STUDY/'data/raw';P=STUDY/'data/processed';TARGET=RAW/'InvariantProjectionValidData_v1'
def coefficients(gas):
    return [dict(mid=float(s.thermo.coeffs[0]),high=list(map(float,s.thermo.coeffs[1:8])),low=list(map(float,s.thermo.coeffs[8:15])),w=s.molecular_weight) for s in gas.species()]
def absolute(data,Y,T,constraint):
    value=capacity=0.
    for d,y in zip(data,Y):
        a=d['low'] if T<d['mid'] else d['high'];v=properties(a,T)
        value+=y*(v['h']/RU*ct.gas_constant-(ct.gas_constant*T if constraint=='CV' else 0))/d['w']
        capacity+=y*(v['Cp']/RU*ct.gas_constant-(ct.gas_constant if constraint=='CV' else 0))/d['w']
    return value,capacity
def project(data,Y,T,target,constraint,low=200.,high=3500.):
    if min(Y)<0:return dict(failed=True,reason='Negative provisional species; scalar recovery is ineligible')
    left=absolute(data,Y,low,constraint)[0];right=absolute(data,Y,high,constraint)[0]
    if not left<=target<=right:return dict(failed=True,reason='Target outside valid invariant range')
    T=max(low,min(T,high))
    for n in range(30):
        value,cap=absolute(data,Y,T,constraint);error=value-target
        if cap<=0:return dict(failed=True,reason='Nonpositive mixture capacity')
        if abs(error)<=1e-13*max(abs(target),1):return dict(failed=False,T=T,relativeResidual=abs(error)/max(abs(target),1),evaluations=n+3)
        if error>0:high=T
        else:low=T
        new=T-error/cap
        T=new if low<new<high else (low+high)/2
    return dict(failed=True,reason='Recovery iteration cap')
def integrate(path,constraint,T0,rtol):
    gas=ct.Solution(str(path));Y0=dict(H2=.0283,O2=.225,H=.0001,OH=.0001,N2=.7465)
    gas.TPY=T0,101325,Y0;rho=gas.density;target=gas.int_energy_mass if constraint=='CV' else gas.enthalpy_mass;initialY=gas.Y.copy()
    ctor=ct.IdealGasReactor if constraint=='CV' else ct.IdealGasConstPressureReactor
    reactor=ctor(gas,clone=False,energy='on');net=ct.ReactorNet([reactor]);net.rtol=rtol;net.atol=1e-16
    start=time.perf_counter();net.advance(1e-5 if T0==999 else 240e-6);wall=time.perf_counter()-start
    g=reactor.phase;data=coefficients(g);Y=g.Y.copy();T=g.T;p=g.P;rho1=g.density
    value=g.int_energy_mass if constraint=='CV' else g.enthalpy_mass
    A=np.array([[g.n_atoms(s,e)*g.atomic_weight(e)/g.molecular_weights[i] for i,s in enumerate(g.species_names)] for e in g.element_names])
    record=dict(T=T,Y=list(map(float,Y)),p=p,rho=rho1,initialRho=rho,target=target,energyResidual=value-target,relativeInvariant=abs(value-target)/max(abs(target),1),elementResidual=float(np.max(np.abs(A@(Y-initialY)))),massResidual=float(sum(Y)-sum(initialY)),minY=float(min(Y)),solverStats=dict(net.solver_stats),uncontendedWallNotEstablished=wall)
    projected=project(data,Y,T,target,constraint)
    if not projected['failed']:
        # Preserve the exact provisional vector; no TPY/TDY renormalization.
        gas.set_unnormalized_mass_fractions(Y)
        if constraint=='CV':gas.TD=projected['T'],rho
        else:gas.TP=projected['T'],101325
        value=gas.int_energy_mass if constraint=='CV' else gas.enthalpy_mass
        projected.update(p=gas.P,rho=gas.density,independentCanteraInvariantResidual=value-target,relativeCanteraInvariantResidual=abs(value-target)/max(abs(target),1),EOSResidual=gas.P-gas.density*ct.gas_constant*gas.T/gas.mean_molecular_weight,speciesChangeMax=float(np.max(np.abs(gas.Y-Y))))
    record['projected']=projected;return record
def inputs():
    yaml=YAML();audit=RAW/'MechanismContinuity_v2';out=[]
    for label,source in [('H2',audit/'H2_CpHS.yaml'),('GRI',audit/'gri.yaml')]:
        dest=TARGET/f'{label}_continuous.yaml'
        if not dest.exists():
            original=yaml.load(source)
            for s in original['species']:
                if s['thermo']['model']!='NASA7':raise RuntimeError('Non-NASA7 input')
                ranges=s['thermo']['temperature-ranges'];a=s['thermo']['data'];d=dict(mid=ranges[1] if len(ranges)==3 else 1000,low=list(a[0]),high=list(a[-1]))
                fixed=repair(d,'CpHS');s['thermo']['data']=[fixed['low'],fixed['high']];s['thermo']['temperature-ranges']=[ranges[0],fixed['mid'],ranges[-1]]
            with dest.open('w') as f:yaml.dump(original,f)
        out.append((label,dest))
    return out
def main():
    summary=TARGET/'projection_result.json'
    if summary.exists():
        (P/'invariant_projection_valid_data.json').write_bytes(summary.read_bytes());print('Reused immutable projection controls');return
    if TARGET.exists():raise RuntimeError('Retained incomplete projection experiment')
    TARGET.mkdir();(TARGET/'driver_snapshot.py').write_bytes(Path(__file__).read_bytes())
    records=[]
    for label,path in inputs():
     for constraint in ['CV','CP']:
      for T0 in [999.,1100.,1500.]:
        references=[integrate(path,constraint,T0,tol) for tol in [1e-12,1e-13]];reference=references[-1]
        contrast=dict(T=abs(references[0]['T']-reference['T']),Y=max(abs(a-b) for a,b in zip(references[0]['Y'],reference['Y'])))
        for tol in [1e-4,1e-6,1e-8,1e-10]:
            r=integrate(path,constraint,T0,tol);pr=r['projected']
            r.update(mechanism=label,constraint=constraint,Tinitial=T0,rtol=tol,referenceToleranceContrast=contrast,temperatureError=abs(r['T']-reference['T']),speciesErrorMax=max(abs(a-b) for a,b in zip(r['Y'],reference['Y'])),reference=reference,mechanismSHA256=sha(path))
            if not pr['failed']:
                pr['temperatureError']=abs(pr['T']-reference['T']);pr['speciesErrorMax']=r['speciesErrorMax']
                pr['gatesPass']=pr['relativeCanteraInvariantResidual']<=1e-10 and abs(pr['EOSResidual'])/pr['p']<=1e-10 and r['elementResidual']<=1e-12 and r['massResidual']<=1e-12 and r['minY']>=0 and pr['T']>0 and pr['speciesChangeMax']==0
            records.append(r);print(label,constraint,T0,tol,'Terrors',r['temperatureError'],pr.get('temperatureError'),'Yerror',r['speciesErrorMax'],'eligible',not pr['failed'],flush=True)
    result=dict(canteraVersion=ct.__version__,driverSHA256=sha(__file__),records=records,scope='Known scalar endpoint projection baseline on continuous data. Independent polynomial recovery checked by Cantera properties. Reference/provisional integration both use Cantera BDF; tolerance contrast is not an independent integrator verification. Concurrent wall measurements excluded from cost comparisons.')
    summary.write_text(json.dumps(result,indent=2)+'\n');(P/'invariant_projection_valid_data.json').write_bytes(summary.read_bytes())
if __name__=='__main__':main()
