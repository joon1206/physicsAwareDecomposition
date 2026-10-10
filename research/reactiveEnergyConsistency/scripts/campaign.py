"""Bounded sequential experiments, never write the completed action artifact."""
from pathlib import Path
import json,re,sys,shutil,math,time,subprocess
from caseFactory import make_case,decompose,solve,set_control,set_chemistry,field,command,latest_time
ROOT=Path(__file__).resolve().parents[1]
def change(path,key,value):
    txt=path.read_text();txt,n=re.subn(r'(\b'+key+r'\s+)[^;]+;',lambda m:m[1]+str(value)+';',txt)
    assert n==1,(path,key,n);path.write_text(txt)
def run(name,kind='F',dt=2e-6,correctors=1,outer=1,ranks=4,steps=None,enabled=True,action='A0',exe='reactingEnergyAudit',nx=32,ny=8,tol=None):
    target=ROOT/'data/raw'/name
    if (target/'result.json').exists():return target
    if (target/'failure.json').exists():
        print('Retained previous failure:',name,flush=True);return target
    if target.exists():raise RuntimeError('Incomplete run retained; choose a new run name: '+str(target))
    steps=steps if steps is not None else round(240e-6/dt)
    regime='heldoutMoving' if kind=='F' else 'uniform'
    case=make_case(name,regime,nx=nx,ny=ny,dt=dt,steps=steps,action=action)
    sol=case/'system/fvSolution';change(sol,'nCorrectors',correctors);change(sol,'nOuterCorrectors',outer)
    if tol:sol.write_text(re.sub(r'(tolerance\s+)[^;]+;',lambda m:m[1]+str(tol)+';',sol.read_text()))
    (case/'system/controlDict').open('a').write('\nenergyLedger '+('true' if enabled else 'false')+';\n')
    if kind!='F':
        if kind=='A':
            field(case/'0/T',800.,'[0 0 0 1 0 0 0]');field(case/'0/U',(0,0,0),'[0 1 -1 0 0 0 0]',True)
        if kind=='B':
            field(case/'0/T',1100.,'[0 0 0 1 0 0 0]');field(case/'0/U',(0,0,0),'[0 1 -1 0 0 0 0]',True)
        if kind in ['A','C','D']:
            change(case/'constant/chemistryProperties','chemistry','off')
            for s in json.loads((case/'case.json').read_text())['species']:field(case/'0'/s,1. if s=='N2' else 0.)
        if kind=='C':
            # Smooth entropy wave; viscosity/conduction mean this is not an
            # exact solution of the configured Navier-Stokes transport model.
            ts=[800+40*math.sin(2*math.pi*(i%nx+.5)/nx) for i in range(nx*ny)]
            field(case/'0/T',ts,'[0 0 0 1 0 0 0]');field(case/'0/U',(40,0,0),'[0 1 -1 0 0 0 0]',True)
        if kind=='D':
            field(case/'0/T',800.,'[0 0 0 1 0 0 0]');field(case/'0/U',(0,0,0),'[0 1 -1 0 0 0 0]',True)
            ys=[.1+.03*math.sin(2*math.pi*(i%nx+.5)/nx) for i in range(nx*ny)]
            field(case/'0/H2',ys);field(case/'0/N2',[1-y for y in ys])
    decompose(case,ranks)
    try:wall=solve(case,ranks,exe=exe,timeout=900)
    except RuntimeError as error:
        (case/'failure.json').write_text(json.dumps(dict(name=name,kind=kind,dt=dt,nCorrectors=correctors,nOuterCorrectors=outer,ranks=ranks,error=str(error)),indent=2)+'\n')
        print('FAILED (retained)',name,flush=True)
        return case
    command(['mpirun','--bind-to','core','--map-by','core','--nooversubscribe','-np',str(ranks),'padNativeInventory']+(['-parallel'] if ranks>1 else [])+['-time','0:'],case,case/'inventory.log')
    result=dict(name=name,kind=kind,dt=dt,nCorrectors=correctors,nOuterCorrectors=outer,ranks=ranks,steps=steps,
                enabled=enabled,action=action,exe=exe,nx=nx,ny=ny,tolerance=tol,solverWall=wall)
    (case/'result.json').write_text(json.dumps(result,indent=2)+'\n')
    print('EXECUTED',name,'wall',round(wall,3),flush=True)
    return case
def main():
    if len(sys.argv)>1 and sys.argv[1]=='pilot':
        run('pilot_A',kind='A',ranks=1,steps=2);run('pilot_F',steps=2);return
    run('A_static',kind='A',ranks=1,steps=20)
    run('B_reaction',kind='B',ranks=1,steps=120)
    run('C_advection',kind='C',ranks=1,steps=120)
    run('D_diffusion',kind='D',ranks=1,steps=120)
    for dt in [2e-6,1e-6,.5e-6,.25e-6]:
        for p in [1,4]:run(f'F_dt{dt:g}_p{p}',dt=dt,correctors=p)
    run('F_outer2',outer=2);run('F_tol1e-8',tol=1e-8)
    run('F_ledger_off',enabled=False)
    run('F_original',enabled=False,exe='reactingFoamPADInitialState')
    run('F_serial',ranks=1)
    run('F_balanced',action='AC')
if __name__=='__main__':main()
