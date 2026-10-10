"""Independent source invariants, including physical CV/CP and modern data."""
from pathlib import Path
import csv,json,math,shutil,sys
ROOT=Path(__file__).resolve().parents[1];sys.dont_write_bytecode=True
sys.path.insert(0,str(ROOT/'build/canteraPackages'))
sys.path.append(str(ROOT.parent/'physicsAwareDecomposition/scripts'))
sys.path.append(str(ROOT.parent/'physicsAwareDecomposition/actionStudy/scripts'))
import cantera as ct
import numpy as np
from thermo_continuity import properties,sha
from thermo_reference import RU
STUDY=ROOT/'candidateStudy';RAW=STUDY/'data/raw';P=STUDY/'data/processed';AUDIT=RAW/'MechanismContinuity_v2'
TARGET=RAW/'CleanThermoIndependent_v1'
def main():
    summary=TARGET/'reference_summary.json'
    if summary.exists():
        (P/'clean_thermo_reference.json').write_bytes(summary.read_bytes());print('Reused immutable independent controls');return
    if TARGET.exists():raise RuntimeError('Retained incomplete reference')
    TARGET.mkdir();(TARGET/'driver_snapshot.py').write_bytes(Path(__file__).read_bytes())
    specs=[('legacy',RAW/'cantera0D_pstd100000_matched_legacyPhase/legacyWeights.yaml','gas'),('HS',AUDIT/'H2_HS.yaml','gas'),('CpHS',AUDIT/'H2_CpHS.yaml','gas'),('GRI',AUDIT/'gri.yaml','gas'),('Alzueta',AUDIT/'ammonia-CO-H2-Alzueta-2023.yaml','baseline')]
    records=[]
    for label,path,phase in specs:
      # Imported phase names differ; default first phase except modern explicit baseline.
      for constraint in ['CV','CP']:
       for t0 in [999.,1100.,1500.]:
        for rtol in [1e-8,1e-10,1e-12]:
            gas=ct.Solution(str(path),phase) if label=='Alzueta' else ct.Solution(str(path))
            y=dict(H2=.0283,O2=.225,H=.0001,OH=.0001,N2=.7465)
            scale=RU/ct.gas_constant if label in ['legacy','HS','CpHS'] else 1.
            gas.TPY=t0,101325./scale,y
            ctor=ct.IdealGasReactor if constraint=='CV' else ct.IdealGasConstPressureReactor
            reactor=ctor(gas,clone=False,energy='on');net=ct.ReactorNet([reactor]);net.rtol=rtol;net.atol=1e-16
            m0=reactor.mass;rho0=reactor.density;v0=reactor.volume;u0=gas.int_energy_mass;h0=gas.enthalpy_mass;p0=gas.P;Y0=gas.Y.copy();W=gas.molecular_weights.copy()
            A=np.array([[gas.n_atoms(s,e)*gas.atomic_weight(e)/W[i] for i,s in enumerate(gas.species_names)] for e in gas.element_names])
            jumps={s.name:(properties(list(s.thermo.coeffs)[1:8],s.thermo.coeffs[0])['h']-properties(list(s.thermo.coeffs)[8:15],s.thermo.coeffs[0])['h'])/RU*ct.gas_constant for s in gas.species()}
            rows=[];predicted=0.;oldT=t0;oldY=Y0.copy();tf=1e-5
            for j in range(1001):
                time=j*tf/1000
                if j:net.advance(time)
                g=reactor.phase;T=g.T;Y=g.Y
                for i,s in enumerate(g.species()):
                    mid=s.thermo.coeffs[0]
                    if (oldT<mid<=T) or (T<mid<=oldT):
                        fraction=(mid-oldT)/(T-oldT);yc=(1-fraction)*oldY[i]+fraction*Y[i]
                        predicted+=(1 if T>oldT else -1)*yc*jumps[s.name]/W[i]
                row=dict(time=time,T=T,p=g.P*scale,rho=reactor.density,mass=reactor.mass,volume=reactor.volume,
                         R_element=float(np.max(np.abs(A@(Y-Y0)))),R_mass=(reactor.mass-m0)/m0,
                         R_energy=(g.int_energy_mass-u0)*scale,R_enthalpy=(g.enthalpy_mass-h0)*scale,
                         R_EOS=(g.P-reactor.density*ct.gas_constant*T/g.mean_molecular_weight)*scale,
                         R_CV_energy=(g.int_energy_mass-u0)*rho0*scale,
                         R_CP_energy=(g.int_energy_mass-u0+p0*(1/reactor.density-1/rho0))*scale,
                         predictedJump=predicted*scale,minY=float(min(Y)),sumY=float(sum(Y)))
                rows.append(row);oldT=T;oldY=Y.copy()
            filename=f'{label}_{constraint}_T{t0:g}_rtol{rtol:g}.csv'
            with (TARGET/filename).open('w',newline='') as f:
                writer=csv.DictWriter(f,fieldnames=rows[0]);writer.writeheader();writer.writerows(rows)
            energy=rows[-1]['R_energy'] if constraint=='CV' else rows[-1]['R_enthalpy'];denom=max(abs((u0 if constraint=='CV' else h0)*scale),1)
            record=dict(mechanism=label,constraint=constraint,Tinitial=t0,rtol=rtol,atol=1e-16,TF=tf,initialY=y,initialRho=rho0,initialE=u0*scale,initialH=h0*scale,end=rows[-1],relativeInvariantChange=abs(energy)/denom,
                        jumpSubtractedRelativeError=abs(energy-predicted*scale)/denom,solverStats=dict(net.solver_stats),trajectory=filename,mechanismSHA256=sha(path),minY=min(r['minY'] for r in rows),maxElementResidual=max(r['R_element'] for r in rows),reactorClone=False,weights=list(map(float,W)))
            records.append(record);print(label,constraint,t0,rtol,'R',record['relativeInvariantChange'],'jump remainder',record['jumpSubtractedRelativeError'],flush=True)
    result=dict(canteraVersion=ct.__version__,driverSHA256=sha(__file__),records=records,
                units=dict(R_element='kg_element/kg',R_mass='relative total mass',R_energy='J/kg',R_enthalpy='J/kg',R_CV_energy='J/m3',R_CP_energy='J/kg',R_EOS='Pa'),
                scope='Same species mixture, pressure, TF and numerical settings within each thermo-only comparison. GRI/Alzueta have different kinetics and constants; no thermochemical-only causal inference across mechanisms. CP uses a physically expanding closed reactor. Crossing concentrations linearly interpolated in output samples, not event-exact.')
    summary.write_text(json.dumps(result,indent=2)+'\n');(P/'clean_thermo_reference.json').write_bytes(summary.read_bytes())
if __name__=='__main__':main()
