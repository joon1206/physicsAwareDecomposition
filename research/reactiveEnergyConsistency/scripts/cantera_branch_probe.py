"""Independent fixed-volume source controls across unchanged NASA branch data."""
from pathlib import Path
import csv,hashlib,json,math,sys
ROOT=Path(__file__).resolve().parents[1];sys.dont_write_bytecode=True
sys.path.insert(0,str(ROOT/'build/canteraPackages'))
sys.path.append(str(ROOT.parent/'physicsAwareDecomposition/scripts'))
import cantera as ct
from thermo_reference import RU,parse_nasa
STUDY=ROOT/'candidateStudy';RAW=STUDY/'data/raw';P=STUDY/'data/processed'
MATCHED=RAW/'cantera0D_pstd100000_matched_legacyPhase/legacyWeights.yaml'
SOURCE=RAW/'B_none_dt2e-06_s1_g0_o1_p1'
Y0=dict(H2=.0283,O2=.225,H=.0001,OH=.0001,N2=.7465)

def main():
    results=[];nasa=parse_nasa(SOURCE/'chemkin/therm.dat')
    native=json.loads((P/'cv_branch_probe.json').read_text())
    for t0 in [999.,1001.,1100.]:
        name=f'cantera_Branch_T{t0:g}';target=RAW/name;summary=target/'reference_summary.json'
        if summary.exists():results.append(json.loads(summary.read_text()));continue
        if target.exists():raise RuntimeError('Retained incomplete reference '+str(target))
        target.mkdir();trials=[];rho0=101325./(t0*RU*math.fsum(y/nasa[s]['w'] for s,y in Y0.items()))
        for rtol in [1e-8,1e-10,1e-12]:
            gas=ct.Solution(str(MATCHED));gas.TDY=t0,rho0,Y0
            reactor=ct.IdealGasReactor(gas,clone=False,energy='on')
            weightError=max(abs(reactor.phase.molecular_weights[reactor.phase.species_index(s)]-nasa[s]['w']) for s in gas.species_names)
            if weightError>1e-12 or abs(reactor.density-rho0)/rho0>1e-14:raise RuntimeError('Reference phase changed')
            net=ct.ReactorNet([reactor]);net.rtol=rtol;net.atol=1e-16
            e0=reactor.density*reactor.phase.int_energy_mass;rows=[]
            for i in range(1001):
                time=i*1e-8
                if i:net.advance(time)
                g=reactor.phase;e=reactor.density*g.int_energy_mass
                row=dict(time=time,T=reactor.T,p=g.P*RU/ct.gas_constant,rho=reactor.density,
                         energyDensityLegacy=e*RU/ct.gas_constant,energyDrift=(e-e0)/abs(e0))
                row.update({s:float(g.Y[g.species_index(s)]) for s in gas.species_names});rows.append(row)
            with (target/f'trajectory_rtol{rtol:g}.csv').open('w',newline='') as stream:
                writer=csv.DictWriter(stream,fieldnames=rows[0]);writer.writeheader();writer.writerows(rows)
            comparisons=[dict(name=r['name'],chunks=r['chunks'],nativeTemperatureDifference=abs(r['Tfinal']-rows[-1]['T']),
                              nativeEnergyDriftDifference=abs(r['relativeEnergyChange']-abs(rows[-1]['energyDrift'])))
                         for r in native if r['Tinitial']==t0 and r['odeRelativeTolerance']==rtol]
            trials.append(dict(rtol=rtol,atol=net.atol,initial=rows[0],end=rows[-1],maxEnergyDrift=max(abs(r['energyDrift']) for r in rows),
                               reactorClone=False,reactorMolecularWeightMaxError=weightError,comparisons=comparisons))
            print(name,rtol,'T',rows[-1]['T'],'Edrift',rows[-1]['energyDrift'],'native',comparisons,flush=True)
        result=dict(name=name,Tinitial=t0,pInitial=101325.,TF=1e-5,Yinitial=Y0,records=trials,
                    matchedMechanismSHA256=hashlib.sha256(MATCHED.read_bytes()).hexdigest(),
                    driverSHA256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),canteraVersion=ct.__version__,
                    scope='Independent known Cv reactor at identical branch-probe states with unchanged matched NASA/mechanism. Energy drift is retained, not interpreted as an energy-conserving reference across discontinuities.')
        summary.write_text(json.dumps(result,indent=2)+'\n');results.append(result)
    (P/'cantera_branch_probe.json').write_text(json.dumps(results,indent=2)+'\n')
if __name__=='__main__':main()
