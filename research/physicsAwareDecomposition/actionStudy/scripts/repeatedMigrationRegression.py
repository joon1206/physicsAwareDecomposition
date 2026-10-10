"""Validate cyclic redistribution repeatedly against uninterrupted chemistry."""
import json,shutil
from caseFactory import ROOT,make_case,decompose,solve,set_control,latest_time
from oracle import copy_checkpoint,action_setup
from features import rank_costs
from mapping import canonical_directory
from validation import numerical_gate
def main():
    output=ROOT/'data/processed/repeated_migration_validation.json'
    if output.exists():
        gates=json.loads(output.read_text())
        if not all(g['pass_'] for g in gates):raise RuntimeError('retained repeated migration regression failed')
        print('REUSED successful repeated-migration regression');return
    source=make_case('repeatedMigration/source','heldoutIgnition',steps=20,trace=0)
    decompose(source,4);solve(source,4,exe='reactingFoamPADRestart')
    info=json.loads((source/'case.json').read_text());cp=latest_time(source,True)
    native=ROOT/'data/raw/repeatedMigration/nativeFirst';working=ROOT/'data/raw/repeatedMigration/privateRepeated'
    copy_checkpoint(source,native,cp);copy_checkpoint(source,working,cp)
    cost,_=rank_costs(source,cp,info['nCells'])
    action_setup(native,'AM',cp,cost,4)
    fields=['T','h','rho','p','U','Qdot']+info['species'];gates=[]
    for index in [20,60,100]:
        cp=latest_time(working,True);assert abs(float(cp)-index*info['dt'])<1e-12
        before=working/'validation'/f'before{index}'
        shutil.copytree(canonical_directory(working,cp,fields,info['nCells']),before)
        cost,_=rank_costs(working,cp,info['nCells'])
        action_setup(working,'AM',cp,cost,4,redistributor='redistributeParPAD')
        after=canonical_directory(working,cp,fields,info['nCells'])
        gate=numerical_gate(before,after,info);gate.update(check='instantaneous migration state',index=index);gates.append(gate)
        if index==20:
            gate=numerical_gate(canonical_directory(native,cp,fields,info['nCells']),after,info)
            gate.update(check='private versus native first migration',index=index);gates.append(gate)
        set_control(working,start=float(cp),steps=40,dt=info['dt']);solve(working,4,exe='reactingFoamPADRestart')
    reference=make_case('repeatedMigration/nativeContinuous','heldoutIgnition',steps=140,trace=0)
    prop=reference/'constant/chemistryProperties';prop.write_text(prop.read_text().replace('solver costOde;','solver ode;'))
    decompose(reference,4);solve(reference,4,exe='reactingFoamPADRestart')
    end=latest_time(working,True);assert abs(float(end)-140*info['dt'])<1e-12
    gate=numerical_gate(*[canonical_directory(p,end,fields,info['nCells']) for p in [reference,working]],info)
    gate.update(check='three migrations versus uninterrupted native trajectory',index=140);gates.append(gate)
    output.write_text(json.dumps(gates,indent=2))
    if not all(g['pass_'] for g in gates):raise RuntimeError('repeated migration field gates failed; all evidence retained')
    print('PASSED repeated migration regression: native/private first map, three instantaneous gates, native trajectory endpoint')
if __name__=='__main__':main()
