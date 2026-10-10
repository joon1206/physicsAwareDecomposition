"""Fine physical-timestep follow-up, after the main timed campaign."""
import csv,json,random,shutil,time
from caseFactory import ROOT,make_case,set_control,decompose,solve,latest_time,command
from oracle import run_branch
from mapping import canonical_directory
from validation import numerical_gate
from analysis import summary,interval

def budget_refinement():
    records=[]
    for regime in ['persistent','translating','heldoutMoving']:
        for dt in [.5e-6,.25e-6]:
            c=ROOT/f'data/raw/conservationRefinement/{regime}_dt{dt}'
            if not (c/'history.json').exists():
                if c.exists():raise RuntimeError('incomplete refined history retained: '+str(c))
                steps=round(.00024/dt)
                make_case(str(c.relative_to(ROOT/'data/raw')),regime,nx=32,ny=8,dt=dt,steps=steps,trace=0)
                set_control(c,steps=steps,dt=dt,write_interval=round(4e-5/dt))
                setup,_=decompose(c,4);wall=solve(c,4)
                (c/'history.json').write_text(json.dumps(dict(solverWall=wall,decompositionWall=setup)))
                print('MEASURED accuracy history',regime,dt,wall,flush=True)
            command(['mpirun','--bind-to','core','--map-by','core','--nooversubscribe','-np','4','padNativeInventory','-parallel','-time','0:'],c,c/'inventory.log')
            rank=[]
            for f in c.glob('processor*/postProcessing/inventory/rank*.csv'):
                rank.extend({k:float(v) for k,v in r.items()} for r in csv.DictReader(f.open()))
            initial=None
            for t in sorted(set(r['time'] for r in rank)):
                group=[r for r in rank if r['time']==t];row={k:sum(r[k] for r in group) for k in ['mass','massEOS','totalEnergy','energyEOS']}
                row.update(time=t,dt=dt,regime=regime)
                if initial is None:initial=row
                row['relativeMassDrift']=(row['mass']-initial['mass'])/initial['mass']
                row['relativeEnergyDrift']=(row['totalEnergy']-initial['totalEnergy'])/abs(initial['totalEnergy'])
                records.append(row)
    (ROOT/'data/processed/conservation_refinement.json').write_text(json.dumps(records,indent=2))

def fine_oracle():
    # Same checkpoint physical time and future physical duration as the original
    # H80 campaign, at a timestep eight times smaller. Cases remain coarse in
    # space; this does not establish physical flame-resolution convergence.
    dt=.25e-6;H=640;cp='4e-05';rows=[];gates=[]
    for regime in ['persistent','heldoutMoving']:
        c=ROOT/'data/raw/fineHistories'/regime
        if not (c/'history.json').exists():
            make_case('fineHistories/'+regime,regime,nx=32,ny=8,dt=dt,steps=160,trace=1)
            decompose(c,4);wall=solve(c,4)
            (c/'history.json').write_text(json.dumps(dict(solverWall=wall)))
        jobs=[(a,r) for a in ['A0','AC','AM','AH'] for r in range(5)]
        random.Random(777).shuffle(jobs)
        for a,r in jobs:
            target=ROOT/'data/raw/fineOracle'/regime/f'cp{cp}_H{H}_{a}_r{r}'
            if not (target/'manifest.json').exists():run_branch(c,cp,a,H,r,campaign='fineOracle')
            row=json.loads((target/'manifest.json').read_text());row['path']=str(target.relative_to(ROOT));rows.append(row)
        info=json.loads((c/'case.json').read_text());fields=['T','p','U','Qdot','h','rho']+info['species']
        for row in [r for r in rows if r['regime']==regime and r['action']!='A0']:
            target=ROOT/row['path'];ref=target.with_name(target.name.replace('_'+row['action']+'_','_A0_'));end=latest_time(target,True)
            gate=numerical_gate(*[canonical_directory(x,end,fields,info['nCells']) for x in [ref,target]],info)
            gate.update(regime=regime,action=row['action'],repeat=row['repeat']);gates.append(gate)
    result=[]
    for regime in ['persistent','heldoutMoving']:
        base=[r['totalWall'] for r in rows if r['regime']==regime and r['action']=='A0']
        for a in ['A0','AC','AM','AH']:
            times=[r['totalWall'] for r in rows if r['regime']==regime and r['action']==a]
            result.append(dict(regime=regime,action=a,dt=dt,H=H,stats=summary(times),speedup=summary(base)['median']/summary(times)['median'],
                speedupCI=[1,1] if a=='A0' else interval(base,times),valid=all(g['pass_'] for g in gates if g['regime']==regime and g['action']==a)))
    for name,data in [('fine_oracle_raw',rows),('fine_oracle_summary',result),('fine_oracle_validation',gates)]:
        (ROOT/f'data/processed/{name}.json').write_text(json.dumps(data,indent=2))

if __name__=='__main__':
    budget_refinement();fine_oracle()
