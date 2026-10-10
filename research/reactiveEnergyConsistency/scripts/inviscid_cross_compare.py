"""Both independent flux families with conservative restriction and uncertainty."""
from pathlib import Path
import json,math
from inviscid_field_compare import state,restrict,norms,ROOT,STUDY,RAW

def main():
    central=[state(p.parent) for p in RAW.glob('Central_F_*/central_result.json') if '_hRecovery2' in p.parent.name or '_hRecovery3' in p.parent.name]
    hllc=[state(p.parent) for p in RAW.glob('HLLC_F_*/central_result.json')]
    pressure=[state(p.parent) for p in RAW.glob('InvF_*/result.json')]
    records=[];references=[]
    for family,cases in [('central',central),('hllc',hllc)]:
        if not cases:continue
        ref=sorted(cases,key=lambda s:(s['config']['nx'],-s['config']['dt']))[-1];refn=ref['config']['nx']
        references.append(dict(family=family,name=ref['name'],nx=refn,dt=ref['config']['dt'],sourceSnapshot=ref['config']['sourceSnapshot'],
            status='Finest executed mesh in this flux family; uncertainty quantified by refinement differences, not assumed negligible'))
        for st in sorted(central+hllc+pressure,key=lambda s:s['name']):
            if st['name']==ref['name']:continue
            n=min(st['config']['nCells'],refn);expected,refRestriction=restrict(ref,n)
            actual,caseRestriction=restrict(st,n) if st['config']['nCells']>n else (st['primitive'],None)
            records.append(dict(referenceFamily=family,reference=ref['name'],name=st['name'],nx=st['config']['nCells'],comparisonNx=n,
                mode=st['config'].get('mode','hllc' if st['name'].startswith('HLLC_') else 'central'),dt=st['config']['dt'],
                differences=norms(actual,expected),referenceRestriction=refRestriction,caseRestriction=caseRestriction,
                initialEnergyRelativeDifference=(st['initial']['E_NASA']-ref['initial']['E_NASA'])/abs(ref['initial']['E_NASA']),
                sourceSnapshot=st['config']['sourceSnapshot'],executableSHA256=st['config']['executableSHA256']))
    out=dict(references=references,records=records,scope='Same inviscid detailed-chemistry PDE and physical domain. Independent central/HLLC fluxes; field differences are not exact errors. Aligned volume restriction conserves rho,rhoU,rhoY,rhoEa and recovers EOS primitives.')
    (STUDY/'data/processed/inviscid_cross_reference.json').write_text(json.dumps(out,indent=2)+'\n')
    for r in records:print(r['referenceFamily'],r['name'],'T L1',r['differences']['T']['L1'],'U L1',r['differences']['U']['L1'])
if __name__=='__main__':main()
