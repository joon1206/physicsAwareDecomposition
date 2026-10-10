"""Independent matched Cv reactor references for predeclared additional regimes."""
from pathlib import Path
import csv,hashlib,json,math,sys
ROOT=Path(__file__).resolve().parents[1];sys.dont_write_bytecode=True
sys.path.insert(0,str(ROOT/'build/canteraPackages'))
sys.path.append(str(ROOT.parent/'physicsAwareDecomposition/scripts'))
import cantera as ct
from thermo_reference import RU,parse_nasa
STUDY=ROOT/'candidateStudy';RAW=STUDY/'data/raw'
MATCHED=RAW/'cantera0D_pstd100000_matched_legacyPhase/legacyWeights.yaml'
SOURCE=RAW/'B_none_dt2e-06_s1_g0_o1_p1'
Y0={'H2':.0283,'O2':.225,'N2':.7467}
def main():
    results=[];nasa=parse_nasa(SOURCE/'chemkin/therm.dat')
    for label,T0,p0 in [('coldHighPressure',950.,1013250.),('hot',1500.,101325.)]:
        target=RAW/('cantera_CvRegime_'+label);summary=target/'reference_summary.json'
        if summary.exists():results.append(json.loads(summary.read_text()));continue
        if target.exists():raise RuntimeError('Retained incomplete reference '+str(target))
        target.mkdir();trials=[]
        rho0=p0/(T0*RU*math.fsum(y/nasa[s]['w'] for s,y in Y0.items()))
        for rtol in [1e-10,1e-12]:
            gas=ct.Solution(str(MATCHED));gas.TDY=T0,rho0,Y0
            reactor=ct.IdealGasReactor(gas,clone=False,energy='on')
            weightError=max(abs(reactor.phase.molecular_weights[reactor.phase.species_index(s)]-nasa[s]['w']) for s in gas.species_names)
            if weightError>1e-12 or abs(reactor.density-rho0)/rho0>1e-14:raise RuntimeError('Changed reference phase')
            net=ct.ReactorNet([reactor]);net.rtol=rtol;net.atol=rtol*1e-6
            e0=reactor.mass*reactor.phase.int_energy_mass;rows=[]
            for step in range(121):
                t=step*2e-6
                if step:net.advance(t)
                g=reactor.phase
                row=dict(time=t,T=reactor.T,p=g.P*RU/ct.gas_constant,rho=reactor.density,
                         energyDrift=(reactor.mass*g.int_energy_mass-e0)/max(abs(e0),1e-30))
                row.update({s:float(g.Y[g.species_index(s)]) for s in gas.species_names});rows.append(row)
            with (target/f'trajectory_rtol{rtol:g}.csv').open('w',newline='') as stream:
                writer=csv.DictWriter(stream,fieldnames=rows[0]);writer.writeheader();writer.writerows(rows)
            trials.append(dict(rtol=rtol,atol=net.atol,initial=rows[0],end=rows[-1],maxEnergyDrift=max(abs(r['energyDrift']) for r in rows),
                               reactorClone=False,reactorMolecularWeightMaxError=weightError))
        result=dict(label=label,Tinitial=T0,pInitial=p0,Yinitial=Y0,records=trials,
                    toleranceEndpointDifference={k:abs(trials[0]['end'][k]-trials[1]['end'][k]) for k in trials[0]['end']},
                    matchedMechanismSHA256=hashlib.sha256(MATCHED.read_bytes()).hexdigest(),canteraVersion=ct.__version__,
                    scope='Known closed-volume reactor, unchanged verified legacy mechanism/constants and declared additional source-only regime; no new CFD method or spatial reference.')
        summary.write_text(json.dumps(result,indent=2)+'\n');results.append(result)
        print(label,'Tendpoint',trials[-1]['end']['T'],'reference T contrast',result['toleranceEndpointDifference']['T'],flush=True)
    (STUDY/'data/processed/cantera_cv_regimes.json').write_text(json.dumps(results,indent=2)+'\n')
if __name__=='__main__':main()
