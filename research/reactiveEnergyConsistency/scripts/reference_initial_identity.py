"""Read-only independent EOS initialization check."""
from pathlib import Path
import json,math,sys
ROOT=Path(__file__).resolve().parents[1];sys.dont_write_bytecode=True
sys.path.insert(0,str(ROOT/'build/canteraPackages'))
sys.path.append(str(ROOT.parent/'physicsAwareDecomposition/scripts'))
import cantera as ct
from foamio import read_field
from thermo_reference import RU,parse_nasa
STUDY=ROOT/'candidateStudy';case=STUDY/'data/raw/B_none_dt2e-06_s1_g0_o1_p1'
gas=ct.Solution(str(STUDY/'data/raw/cantera0D_pstd100000_matched/legacyWeights.yaml'))
nasa=parse_nasa(case/'chemkin/therm.dat')
Y={s:read_field(case/'0'/s,256)[0] for s in gas.species_names}
T=read_field(case/'0/T',256)[0];p=read_field(case/'0/p',256)[0]
rho=p/(RU*T*math.fsum(Y[s]/nasa[s]['w'] for s in Y))
gas.TPY=T,p,Y
print(json.dumps(dict(RU=RU,T=T,p=p,Y=Y,sumY=math.fsum(Y.values()),
    legacyDensity=rho,ctDensityTPY=gas.density,ctMW=gas.mean_molecular_weight,
    legacyMW=1/math.fsum(Y[s]/nasa[s]['w'] for s in Y),
    speciesMW=dict(zip(gas.species_names,gas.molecular_weights.tolist())),
    canteraMassFractions=dict(zip(gas.species_names,gas.Y.tolist()))),indent=2))
gas.TDY=T,rho,Y
print('TDY pressure',gas.P,'converted',gas.P*RU/ct.gas_constant)
reactor=ct.IdealGasReactor(gas,clone=True,energy='on')
cloned=dict(pressure=reactor.phase.P*RU/ct.gas_constant,
    molecularWeightError=max(abs(reactor.phase.molecular_weights[reactor.phase.species_index(s)]-nasa[s]['w']) for s in Y))
print('Cloned reactor',cloned)
uncloned=ct.IdealGasReactor(gas,clone=False,energy='on')
kept=dict(pressure=uncloned.phase.P*RU/ct.gas_constant,
    molecularWeightError=max(abs(uncloned.phase.molecular_weights[uncloned.phase.species_index(s)]-nasa[s]['w']) for s in Y))
print('Original-phase reactor',kept)
(STUDY/'data/processed/reference_phase_identity.json').write_text(json.dumps(dict(
    canteraVersion=ct.__version__,initialPressure=p,cloned=cloned,originalPhase=kept),indent=2)+'\n')
