"""Held-out PMPI consequences with on/off calibration and endpoint gates.

The main oracle already bounds these exact cases' runtime. This small follow-up
does not refit the deployed model. MPI-call duration includes waits; it is not
pure network transfer time.
"""
import csv,json,random
from caseFactory import ROOT,latest_time
from oracle import run_branch
from mapping import canonical_directory,metrics
from validation import numerical_gate
def main():
    jobs=[(action,profile,repeat) for action in ['A0','AC','AM','AH'] for profile in [False,True] for repeat in range(3)]
    random.Random(661319).shuffle(jobs);rows=[]
    source=ROOT/'data/raw/histories/heldoutMoving';info=json.loads((source/'case.json').read_text())
    for action,profile,repeat in jobs:
        campaign='mpiConsequencesOn' if profile else 'mpiConsequencesOff'
        target=ROOT/f'data/raw/{campaign}/heldoutMoving/cp4e-05_H80_{action}_r{repeat}'
        if not (target/'manifest.json').exists():run_branch(source,'4e-05',action,80,repeat,campaign,profile)
        row=json.loads((target/'manifest.json').read_text());row['path']=str(target.relative_to(ROOT))
        parts=metrics(target);row['parts']=[{k:v for k,v in part.items() if k!='ids'} for part in parts]
        row['processorFaces']=sum(p['processorFaces'] for p in parts)/2
        row['MPI']=[]
        if profile:
            for path in (target/'mpiProfile').glob('*.csv'):
                with path.open() as stream:row['MPI'].extend(csv.DictReader(stream))
            if len(row['MPI'])!=4:raise RuntimeError('missing rank PMPI clocks')
        rows.append(row)
    fields=['T','h','rho','p','U','Qdot']+info['species']
    for row in rows:
        if not row['profile']:continue
        target=ROOT/row['path'];reference=ROOT/f"data/raw/mpiConsequencesOff/heldoutMoving/cp4e-05_H80_{row['action']}_r{row['repeat']}"
        end=latest_time(target,True)
        row['gate']=numerical_gate(*[canonical_directory(p,end,fields,info['nCells']) for p in [reference,target]],info)
    (ROOT/'data/processed/mpi_consequence_profiles.json').write_text(json.dumps(rows,indent=2))
    if not all(r.get('gate',{'pass_':True})['pass_'] for r in rows):raise RuntimeError('held-out PMPI field gates failed')
    print('PROFILED held-out MPI consequences: 24 on/off trials with field gates')
if __name__=='__main__':main()
