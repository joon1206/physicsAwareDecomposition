"""Preselected independent AC/A0 replication; not used to refit the model."""
import json,random
from caseFactory import ROOT,latest_time
from oracle import run_branch
from mapping import canonical_directory
from validation import numerical_gate
from analysis import summary,interval
def condition(regime):
    source=ROOT/'data/raw/histories'/regime;info=json.loads((source/'case.json').read_text())
    jobs=[(a,r) for a in ['A0','AC'] for r in range(20)];random.Random(189341).shuffle(jobs);rows=[]
    for a,r in jobs:
        p=ROOT/f'data/raw/confirmation/{regime}/cp4e-05_H80_{a}_r{r}'
        if not (p/'manifest.json').exists():run_branch(source,'4e-05',a,80,r,'confirmation')
        rows.append(json.loads((p/'manifest.json').read_text()))
    gates=[]
    for r in range(20):
        pair=[ROOT/f'data/raw/confirmation/{regime}/cp4e-05_H80_{a}_r{r}' for a in ['A0','AC']]
        end=latest_time(pair[0],True);fields=['T','h','rho','p','U','Qdot']+info['species']
        gates.append(numerical_gate(*[canonical_directory(p,end,fields,info['nCells']) for p in pair],info))
    baseline=[r['totalWall'] for r in rows if r['action']=='A0'];method=[r['totalWall'] for r in rows if r['action']=='AC']
    result=dict(regime=regime,checkpoint='4e-05',H=80,baseline=summary(baseline),method=summary(method),speedup=summary(baseline)['median']/summary(method)['median'],CI=interval(baseline,method),gates=gates,rows=rows,
        selection='Moving positive and uniform negative conditions preselected from the prior excluded protocol; independent 20-trial-per-action replication. Not used for model fitting, margin tuning or selecting a new best state.')
    name='confirmation' if regime=='heldoutMoving' else 'confirmation_negative'
    (ROOT/f'data/processed/{name}.json').write_text(json.dumps(result,indent=2))
    if not all(g['pass_'] for g in gates):raise RuntimeError('confirmation field gates failed')
    print('CONFIRMED chemistry action',result['speedup'],result['CI'])
def main():
    for regime in ['heldoutMoving','uniform']:condition(regime)
if __name__=='__main__':main()
