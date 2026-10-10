"""Refinement and history controls following the closed first-stage audit."""
from pathlib import Path
import json,re
from campaign import run,ROOT
from caseFactory import set_control,solve,command
def restart():
    c=ROOT/'data/raw/F_restart'
    if (c/'result.json').exists():return
    c=run('F_restart_prefix',steps=60)
    # Preserve the completed prefix; copy only this project's case into a
    # new explicitly named run. All published cases remain read only.
    import shutil
    out=ROOT/'data/raw/F_restart';assert not out.exists();shutil.copytree(c,out)
    (out/'result.json').unlink()
    set_control(out,start=120e-6,steps=60)
    (out/'system/controlDict').open('a').write('\nenergyLedger true;\n')
    wall=solve(out,4,exe='reactingEnergyAudit',timeout=900)
    command(['mpirun','--bind-to','core','--map-by','core','--nooversubscribe','-np','4','padNativeInventory','-parallel','-time','0:'],out,out/'inventory.log')
    info=json.loads((c/'result.json').read_text());info.update(name='F_restart',steps=120,solverWall=info['solverWall']+wall,segmented=True)
    (out/'result.json').write_text(json.dumps(info,indent=2)+'\n');print('EXECUTED segmented restart',flush=True)
def main():
    restart()
    run('F_outer2_dt2.5e-7',dt=.25e-6,outer=2)
    for dt in [.125e-6,.0625e-6,.03125e-6]:run(f'F_dt{dt:g}_p4',dt=dt,correctors=4)
    # Homogeneous reaction convergence separates pressure lag from spatial effects.
    for dt in [1e-6,.5e-6]:run(f'B_dt{dt:g}',kind='B',ranks=1,dt=dt)
if __name__=='__main__':main()
