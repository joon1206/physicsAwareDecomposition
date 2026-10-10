"""Create a separate research executable; preserve all accepted baseline evidence."""
from pathlib import Path
import json,hashlib,shutil,subprocess
ROOT=Path(__file__).resolve().parents[1]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    original=ROOT/'applications/reactingEnergyAudit';out=ROOT/'applications/reactingEnergyCandidates'
    for name in ['docs/candidates','candidateStudy/data/processed','candidateStudy/data/raw','figures/candidates']:
        (ROOT/name).mkdir(parents=True,exist_ok=True)
    frozen=ROOT/'docs/baseline_audit_freeze.json'
    if not frozen.exists():
        inputs=[p for p in original.rglob('*') if p.is_file() and not any(x in ['linux64Gcc63DPInt32Opt','lnInclude'] for x in p.parts)]
        inputs += [ROOT/'docs'/s for s in ['audit_results.md','discrete_energy_derivation.md','baseline_algorithm.md','actionStudy_freeze.json']]
        inputs += list((ROOT/'data/processed').glob('*'))
        frozen.write_text(json.dumps({'HEAD':subprocess.check_output(['git','rev-parse','HEAD']).decode().strip(),
             'files':{str(p.relative_to(ROOT)):sha(p) for p in inputs}},indent=2)+'\n')
    else:
        assert all(sha(ROOT/p)==s for p,s in json.loads(frozen.read_text())['files'].items())
    if not (out/'reactingFoamPAD.C').exists():
        out.mkdir(exist_ok=True);(out/'Make').mkdir(exist_ok=True)
        for p in original.iterdir():
            if p.suffix in ['.C','.H']:shutil.copy2(p,out/p.name)
        shutil.copy2(original/'Make/options',out/'Make/options')
        (out/'Make/files').write_text('reactingFoamPAD.C\n\nEXE = $(FOAM_USER_APPBIN)/reactingEnergyCandidates\n')
    main=out/'reactingFoamPAD.C';txt=main.read_text()
    if '#include "cellEnergyAudit.H"' not in txt:
        txt=txt.replace('#include "energyLedger.H"','#include "energyLedger.H"\n#include "cellEnergyAudit.H"')
        txt=txt.replace('    energyLedger ledger(mesh,runTime,Y);','    energyLedger ledger(mesh,runTime,Y);\n    cellEnergyAudit cellAudit(mesh,runTime,Y);')
        txt=txt.replace('        ledger.start(rho,thermo,K,Qdot,dpdt);','        ledger.start(rho,thermo,K,Qdot,dpdt);\n        cellAudit.start(rho,thermo,K);')
        txt=txt.replace('        ledger.finish(rho,thermo,K,Qdot,dpdt,phi);','        cellAudit.finish(rho,thermo,K,phi);\n        ledger.finish(rho,thermo,K,Qdot,dpdt,phi);')
        main.write_text(txt)
    y=out/'YEqn.H';txt=y.read_text()
    if 'cellAudit.chemistry' not in txt:
        txt=txt.replace('    Qdot = reaction->Qdot();','    Qdot = reaction->Qdot();\n    cellAudit.chemistry(reaction(),thermo,Qdot);')
        txt=txt.replace('    ledger.snapshot("species_solved",rho,thermo,K,Qdot,dpdt);','    cellAudit.species(rho,thermo,phi,turbulence->muEff(),mvConvection());\n    ledger.snapshot("species_solved",rho,thermo,K,Qdot,dpdt);')
        y.write_text(txt)
    e=out/'EEqn.H';txt=e.read_text()
    if 'cellAudit.assemble' not in txt:
        txt=txt.replace('        ledger.assemble(rho,thermo,K,Qdot,dpdt,phi);','        ledger.assemble(rho,thermo,K,Qdot,dpdt,phi);\n        cellAudit.assemble(rho,thermo,K,Qdot,dpdt,phi);')
        txt=txt.replace('    if (ledger.enabled) ledger.solved(original(),auditConvection(),auditDiffusion(),thermo);','    if (ledger.enabled)\n    {\n        ledger.solved(original(),auditConvection(),auditDiffusion(),thermo);\n        cellAudit.solved(original(),auditConvection(),auditDiffusion(),thermo);\n    }')
        e.write_text(txt)
    print('Candidate source prepared; baseline evidence frozen.')
if __name__=='__main__':main()
