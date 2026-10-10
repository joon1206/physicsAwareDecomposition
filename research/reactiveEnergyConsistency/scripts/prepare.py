"""Freeze read-only inputs and create a separately compiled instrumented snapshot."""
from pathlib import Path
import hashlib,json,subprocess,shutil,difflib
ROOT=Path(__file__).resolve().parents[1]
REPO=ROOT.parents[1]
PAD=REPO/'research/physicsAwareDecomposition'
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def replace(path,old,new,count=1):
    text=path.read_text();assert text.count(old)==count,(path,old,text.count(old))
    path.write_text(text.replace(old,new))
def main():
    for d in ['docs','data/processed','data/raw','figures','build/bin','build/lib']:(ROOT/d).mkdir(parents=True,exist_ok=True)
    files=subprocess.check_output(['git','ls-files','-z','research/physicsAwareDecomposition/actionStudy'],cwd=REPO).decode().split('\0')
    freeze=ROOT/'docs/actionStudy_freeze.json'
    if freeze.exists():
        manifest=json.loads(freeze.read_text());assert all(sha(REPO/p)==s for p,s in manifest['files'].items()),'frozen actionStudy changed'
    else:
        manifest={'gitHEAD':subprocess.check_output(['git','rev-parse','HEAD'],cwd=REPO).decode().strip(),
                  'gitStatus':subprocess.check_output(['git','status','--short'],cwd=REPO).decode(),
                  'files':{p:sha(REPO/p) for p in files if p},'scope':'All tracked published actionStudy files; raw inputs read only, never regenerated here.'}
        freeze.write_text(json.dumps(manifest,indent=2)+'\n')
    source=PAD/'build/initialStateSolver';out=ROOT/'applications/reactingEnergyAudit'
    for p in source.iterdir():
        if p.suffix in ['.C','.H']:shutil.copy2(p,out/p.name)
    (out/'Make').mkdir(exist_ok=True)
    shutil.copy2(source/'Make/options',out/'Make/options')
    (out/'Make/files').write_text('reactingFoamPAD.C\n\nEXE = $(FOAM_USER_APPBIN)/reactingEnergyAudit\n')
    main=out/'reactingFoamPAD.C'
    replace(main,'#include "phaseTimers.H"','#include "phaseTimers.H"\n#include "energyLedger.H"')
    replace(main,'    turbulence->validate();','''    turbulence->validate();
    energyLedger ledger(mesh,runTime,Y);
    if (ledger.enabled && (LTS || thermo.he().name() != "h" || mesh.dynamic()
        || pimple.consistent() || pimple.transonic()
        || word(mesh.ddtScheme("ddt(default)")[0].wordToken()) != "Euler"))
        FatalErrorInFunction << "Ledger requires Euler, fixed mesh, h, nontransonic/nonconsistent pressure" << exit(FatalError);
''')
    snap=lambda s:f'ledger.snapshot("{s}",rho,thermo,K,Qdot,dpdt);'
    replace(main,'        phaseTimer.reset();','        ledger.start(rho,thermo,K,Qdot,dpdt);\n        phaseTimer.reset();')
    replace(main,'        phaseTimer.stop(phaseTimers::rhoPhase);','        phaseTimer.stop(phaseTimers::rhoPhase);\n        '+snap('rho_predictor'))
    replace(main,'        while (pimple.loop())\n        {','        while (pimple.loop())\n        {\n            ledger.outer();')
    replace(main,'            #include "UEqn.H"','            #include "UEqn.H"\n            '+snap('momentum_predictor'))
    replace(main,'            while (pimple.correct())\n            {','            while (pimple.correct())\n            {\n                ledger.pressure();')
    replace(main,'        rho = thermo.rho();','        rho = thermo.rho();\n        ledger.finish(rho,thermo,K,Qdot,dpdt,phi);')
    y=out/'YEqn.H'
    replace(y,'    Qdot = reaction->Qdot();','    Qdot = reaction->Qdot();\n    '+snap('chemistry_sources'))
    replace(y,'    phaseTimer.stop(phaseTimers::species);','    phaseTimer.stop(phaseTimers::species);\n    '+snap('species_solved'))
    e=out/'EEqn.H'
    replace(e,'    EEqn.relax();','''    autoPtr<fvScalarMatrix> original, auditConvection, auditDiffusion;
    if (ledger.enabled)
    {
        ledger.assemble(rho,thermo,K,Qdot,dpdt,phi);
        original.reset(new fvScalarMatrix(EEqn));
        auditConvection.reset(mvConvection->fvmDiv(phi,he).ptr());
        auditDiffusion.reset(fvm::laplacian(turbulence->alphaEff(),he).ptr());
    }
    EEqn.relax();''')
    replace(e,'    fvOptions.correct(he);','''    fvOptions.correct(he);
    if (ledger.enabled) ledger.solved(original(),auditConvection(),auditDiffusion(),thermo);
    '''+snap('energy_solved'))
    replace(e,'    Info<< "min/max(T) = "','    '+snap('thermo_corrected')+'\n    Info<< "min/max(T) = "')
    p=out/'pEqn.H'
    replace(p,'rho = thermo.rho();','rho = thermo.rho();\n'+snap('rho_thermo'),count=2)
    replace(p,'        pEqn.solve(mesh.solver(p.select(pimple.finalInnerIter())));','''        pEqn.solve(mesh.solver(p.select(pimple.finalInnerIter())));
        '''+snap('pressure_solved'),count=2)
    replace(p,'            phi = phiHbyA + pEqn.flux();','            phi = phiHbyA + pEqn.flux();\n            '+snap('phi_corrected'))
    replace(p,'#include "rhoEqn.H"','#include "rhoEqn.H"\n'+snap('rho_continuity'))
    replace(p,'K = 0.5*magSqr(U);','K = 0.5*magSqr(U);\n'+snap('velocity_corrected'))
    replace(p,'phaseTimer.stop(phaseTimers::pressure);',snap('pressure_end')+'\nphaseTimer.stop(phaseTimers::pressure);')
    inputs={str(p.relative_to(REPO)):sha(p) for p in source.iterdir() if p.suffix in ['.C','.H']}
    (ROOT/'docs/source_manifest.json').write_text(json.dumps({'inputs':inputs,'instrumented':{p.name:sha(p) for p in out.iterdir() if p.suffix in ['.C','.H']}},indent=2)+'\n')
    patches=[]
    for p in out.iterdir():
        baseline=source/p.name
        if baseline.is_file(): patches.extend(difflib.unified_diff(baseline.read_text().splitlines(True),p.read_text().splitlines(True),fromfile='initialStateSolver/'+p.name,tofile='reactingEnergyAudit/'+p.name))
    (ROOT/'docs/instrumentation.patch').write_text(''.join(patches))
    print('Frozen',len(manifest['files']),'published files; separate baseline snapshot prepared.')
if __name__=='__main__':main()
