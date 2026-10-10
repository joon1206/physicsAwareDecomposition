"""Check that A0 continuations match uninterrupted physical trajectories."""
import json
from caseFactory import ROOT,make_case,decompose,solve,latest_time
from mapping import canonical_directory
from validation import numerical_gate
def main():
    states=json.loads((ROOT/'data/processed/oracle_summary.json').read_text());gates=[]
    for state in states:
        if state['checkpoint']!='4e-05' or state['H'] not in [20,80]:continue
        if state['H']==20 and state['regime']!='chemistryDominated':continue
        regime=state['regime'];source=ROOT/'data/raw/histories'/regime;info=json.loads((source/'case.json').read_text())
        target=ROOT/f"data/raw/oracle/{regime}/cp4e-05_H{state['H']}_A0_r0";end=latest_time(target,True)
        fields=['T','h','rho','p','U','Qdot']+info['species']
        g=numerical_gate(*[canonical_directory(c,end,fields,info['nCells']) for c in [source,target]],info);g.update(regime=regime,checkpoint='4e-05',H=state['H'],reference='uninterrupted measured source trajectory');gates.append(g)
        print('CONTINUOUS ORACLE',regime,g['pass_'],g['fields']['T']['Linf'],flush=True)
    for regime in ['persistent','heldoutMoving']:
        c=ROOT/'data/raw/continuousOracle'/regime
        if not (c/'manifest.json').exists():
            make_case('continuousOracle/'+regime,regime,nx=32,ny=8,steps=180)
            p=c/'constant/chemistryProperties';p.write_text(p.read_text().replace('solver costOde;','solver ode;'))
            decompose(c,4);wall=solve(c,4);(c/'manifest.json').write_text(json.dumps(dict(wall=wall,steps=180,reference='uninterrupted native standard chemistry')))
        info=json.loads((c/'case.json').read_text());target=ROOT/f'data/raw/oracle/{regime}/cp0.0002_H80_A0_r0';end=latest_time(target,True)
        fields=['T','h','rho','p','U','Qdot']+info['species']
        g=numerical_gate(*[canonical_directory(p,end,fields,info['nCells']) for p in [c,target]],info);g.update(regime=regime,checkpoint='0.0002',H=80,reference='uninterrupted native standard chemistry through 180 steps');gates.append(g)
        print('CONTINUOUS LATE ORACLE',regime,g['pass_'],g['fields']['T']['Linf'],flush=True)
    (ROOT/'data/processed/continuous_oracle_validation.json').write_text(json.dumps(gates,indent=2))
    if len(gates)!=12 or not all(g['pass_'] for g in gates):raise RuntimeError('Oracle does not preserve continuous baseline trajectory')
if __name__=='__main__':main()
