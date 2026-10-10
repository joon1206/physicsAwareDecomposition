"""Read-only native instantaneous rate fixtures for independent Cantera matching."""
from pathlib import Path
import hashlib,json
from caseFactory import make_case,field,command
ROOT=Path(__file__).resolve().parents[1];STUDY=ROOT/'candidateStudy'
ref=json.loads((STUDY/'data/processed/cantera_reference.json').read_text())
endpoint=ref['records'][-1]['end']
names=['H2','H','O2','O','OH','HO2','H2O2','H2O','AR','N2']
initial={s:(.0283 if s=='H2' else .225 if s=='O2' else .7467 if s=='N2' else 0) for s in names}
burned={s:endpoint[s] for s in names}
for label,Y in [('fresh',initial),('burned',burned)]:
    for T in [900.,1100.,1800.,2928.]:
        name=f'Rates_{label}_T{T:g}';case=STUDY/'data/raw'/name
        if (case/'instantaneous_rates.csv').exists():continue
        make_case(name,'uniform',nx=1,ny=1,dt=1e-9,steps=1)
        field(case/'0/T',T,'[0 0 0 1 0 0 0]')
        for s,v in Y.items():field(case/'0'/s,v)
        command(['nativeChemistryRates'],case,case/'native_rates.log')
        (case/'rates_experiment.json').write_text(json.dumps(dict(T=T,p=101325.,Y=Y,
            sourceSHA256=hashlib.sha256((ROOT/'applications/nativeChemistryRates/nativeChemistryRates.C').read_bytes()).hexdigest(),
            executableSHA256=hashlib.sha256((ROOT/'build/bin/nativeChemistryRates').read_bytes()).hexdigest()),indent=2)+'\n')
        print('Native rates',name,flush=True)
