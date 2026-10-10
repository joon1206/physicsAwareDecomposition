"""Compare real segmented continuation with uninterrupted native chemistry."""
import json
from caseFactory import ROOT,make_case,decompose,solve,set_control,latest_time
from mapping import canonical_directory
from validation import numerical_gate

def main():
    gates=[]
    for regime in ['persistent','heldoutMoving']:
        cases=[]
        for mode in ['native','continuous','segmented']:
            segmented=mode=='segmented'
            name='restartRegressionPsi/'+regime+'_'+mode
            c=make_case(name,regime,nx=32,ny=8,steps=20 if segmented else 140)
            if mode=='native':
                p=c/'constant/chemistryProperties';p.write_text(p.read_text().replace('solver costOde;','solver ode;'))
            set_control(c,steps=20 if segmented else 140,restart_state=True);decompose(c,4)
            solve(c,4,exe='reactingFoamPADRestart')
            if segmented:
                for index in [20,60,100]:
                    cp=latest_time(c,True);assert abs(float(cp)-index*2e-6)<1e-12
                    set_control(c,start=float(cp),steps=40,restart_state=True);solve(c,4,exe='reactingFoamPADRestart')
            cases.append(c)
        info=json.loads((cases[0]/'case.json').read_text());fields=['T','h','rho','p','U','Qdot']+info['species'];end=latest_time(cases[0],True)
        for candidate in cases[1:]:
            gate=numerical_gate(*[canonical_directory(c,end,fields,info['nCells']) for c in [cases[0],candidate]],info)
            gate.update(regime=regime,candidate=candidate.name,protocol='restore he, psi oldTime and dpdt v4');gates.append(gate)
            print('REGRESSION versus uninterrupted native',candidate.name,gate['pass_'],{f:v['Linf'] for f,v in gate['fields'].items()},flush=True)
    (ROOT/'data/processed/restart_regression.json').write_text(json.dumps(gates,indent=2))
    if not all(g['pass_'] for g in gates):raise RuntimeError('live restart equivalence rejected; do not benchmark rollouts yet')

if __name__=='__main__':main()
