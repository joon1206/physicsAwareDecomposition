from pathlib import Path
import hashlib,json,shutil
from caseFactory import command
ROOT=Path(__file__).resolve().parents[1];STUDY=ROOT/'candidateStudy'
for case in sorted((STUDY/'data/raw').glob('Rates_*')):
    command(['nativeChemistryRates'],case,case/'native_thermo_rates.log')
    (case/'thermo_rates_experiment.json').write_text(json.dumps(dict(
       sourceSHA256=hashlib.sha256((ROOT/'applications/nativeChemistryRates/nativeChemistryRates.C').read_bytes()).hexdigest(),
       executableSHA256=hashlib.sha256((ROOT/'build/bin/nativeChemistryRates').read_bytes()).hexdigest()),indent=2)+'\n')
