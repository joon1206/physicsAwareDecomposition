"""Pointwise kinetic matching validates declared convention conversions."""
from pathlib import Path
import csv,json,math,sys
ROOT=Path(__file__).resolve().parents[1];sys.dont_write_bytecode=True
sys.path.insert(0,str(ROOT/'build/canteraPackages'))
import cantera as ct
RU=8314.47006650545
STUDY=ROOT/'candidateStudy';mechanism=STUDY/'data/raw/cantera0D_pstd100000_matched/legacyWeights.yaml'
rows=[]
for meta in sorted((STUDY/'data/raw').glob('Rates_*/rates_experiment.json')):
    config=json.loads(meta.read_text())
    with (meta.parent/'instantaneous_rates.csv').open() as f:native=next(csv.DictReader(f))
    native={k:float(v) for k,v in native.items()}
    gas=ct.Solution(str(mechanism));gas.TDY=config['T'],native['rho'],config['Y']
    rates={s:float(gas.net_production_rates[i]*gas.molecular_weights[i]) for i,s in enumerate(gas.species_names)}
    scale=max(abs(v) for v in rates.values())
    diffs={s:rates[s]-native['RR_'+s] for s in rates}
    row=dict(name=meta.parent.name,T=config['T'],native=native,canteraRates=rates,
        rateDifferences=diffs,normalizedMaxRateDifference=max(abs(v) for v in diffs.values())/max(scale,1e-100))
    thermoFile=meta.parent/'instantaneous_thermo_rates.csv'
    if thermoFile.exists():
        with thermoFile.open() as f:nt={k:float(v) for k,v in next(csv.DictReader(f)).items()}
        row['thermoDifferences']=dict(Cp=gas.cp_mass*RU/ct.gas_constant-nt['Cp'],Cv=gas.cv_mass*RU/ct.gas_constant-nt['Cv'],
            Ha=gas.enthalpy_mass*RU/ct.gas_constant-nt['Ha'],Ea=gas.int_energy_mass*RU/ct.gas_constant-nt['Ea'],
            nativeHsPlusHcMinusHa=nt['Hs']+nt['Hc']-nt['Ha'])
    rows.append(row);print(row['name'],'relative rate difference',row['normalizedMaxRateDifference'],'thermo',row.get('thermoDifferences'))
(STUDY/'data/processed/instantaneous_rate_comparison.json').write_text(json.dumps(dict(records=rows,
    canteraVersion=ct.__version__,maxNormalizedRateDifference=max(r['normalizedMaxRateDifference'] for r in rows)),indent=2)+'\n')
