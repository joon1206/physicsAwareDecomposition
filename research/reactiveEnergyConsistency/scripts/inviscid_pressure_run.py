"""One-column inviscid/native-ODE controls of the zero-transport F kernel."""
from pathlib import Path
import json,re,sys
from caseFactory import make_case,solve,command
from candidate_screen import sha
from analyze import summarize
ROOT=Path(__file__).resolve().parents[1];STUDY=ROOT/'candidateStudy'
def run(mode='none',nx=32,dt=.125e-6,tf=240e-6,tag=''):
    name=f'InvF_{mode}_nx{nx}_dt{dt:g}_TF{tf:g}{tag}';case=STUDY/'data/raw'/name
    if (case/'result.json').exists() or (case/'failure.json').exists():return case
    if case.exists():raise RuntimeError('Retained incomplete '+str(case))
    make_case(name,'heldoutMoving',nx=nx,ny=1,dt=dt,steps=round(tf/dt))
    transport=case/'chemkin/transportProperties';transport.write_text(re.sub(r'(\bAs\s+)[^;]+;',r'\g<1>0;',transport.read_text()))
    chem=case/'constant/chemistryProperties';chem.write_text(chem.read_text().replace('solver costOde','solver ode'))
    control=case/'system/controlDict';control.open('a').write(f'\nenergyLedger true; cellEnergyLedger true; cellLedgerEvery 0; energyCorrection {mode};\n')
    cfg=json.loads((STUDY/f'data/raw/F_{mode}_dt1e-06_s1_g0_o1_p1_timing3/result.json').read_text())
    exe=cfg['executable'];assert sha(ROOT/'build/bin'/exe)==cfg['executableSHA256']
    config=dict(cfg,name=name,kind='InvF',nx=nx,nCells=nx,dt=dt,steps=round(tf/dt),ranks=1,
        scope='Inviscid one-column counterpart; As=0 as in the original F kernel, with native standard ode replacing costOde; independent exact error is not established')
    config.pop('solverWall',None);(case/'experiment.json').write_text(json.dumps(config,indent=2)+'\n')
    try:
        wall=solve(case,1,exe=exe,timeout=900)
        command(['padNativeInventory','-time','0:'],case,case/'inventory.log')
    except RuntimeError as e:
        (case/'failure.json').write_text(json.dumps(dict(config,error=str(e)),indent=2)+'\n');print('RETAINED FAILURE',name,flush=True);return case
    (case/'result.json').write_text(json.dumps(dict(config,solverWall=wall),indent=2)+'\n')
    summary,_,_=summarize(case);(case/'inviscid_summary.json').write_text(json.dumps(summary,indent=2)+'\n')
    print(name,'wall',wall,'energy',summary['signedEnergyDrift'],flush=True);return case
def main():
    if len(sys.argv)>1 and sys.argv[1]=='refinement':
        for nx,dt in [(64,.0625e-6),(128,.03125e-6)]:
            for mode in ['none','conservativeState','blockConservative']:run(mode,nx,dt)
    else:
        for mode in ['none','conservativeState','blockConservative']:run(mode)
if __name__=='__main__':main()
