"""Retained old/new conservative stopping-rule replays; no runtime ranking."""
from pathlib import Path
import csv,json,math,sys
from cv_chemistry_regimes import run
from candidate_mixture_wave import run as wave
from candidate_screen import run as screen
from candidate_analyze import totals
from analyze import summarize,fields
ROOT=Path(__file__).resolve().parents[1];STUDY=ROOT/'candidateStudy';RAW=STUDY/'data/raw';EXE='reactingEnergyRoundoffCandidates'
def compare(a,b):
    cfg=[json.loads(next((case/file for file in ['result.json','wave_result.json'] if (case/file).exists())).read_text()) for case in [a,b]]
    info=json.loads((a/'case.json').read_text());n=info['nCells'];t=cfg[0]['dt']*cfg[0]['steps'];out={}
    for name in ['T','p','rho','h','U']+info['species']:
        left=fields(a,cfg[0]['ranks'],t,name,n);right=fields(b,cfg[1]['ranks'],t,name,n)
        d=[math.sqrt(math.fsum((x-y)**2 for x,y in zip(u,v))) if isinstance(u,tuple) else abs(u-v) for u,v in zip(left,right)]
        out[name]=dict(L1=math.fsum(d)/n,L2=math.sqrt(math.fsum(x*x for x in d)/n),Linf=max(d))
    return out
def trace_summary(case):
    rows=[]
    for path in case.glob('**/componentEnergyTolerance/*/rank*.csv'):
        with path.open() as stream:rows.extend({k:float(v) for k,v in row.items()} for row in csv.DictReader(stream))
    accepted=[r for r in rows if r['accepted']]
    return dict(maxAcceptedEnergyResidual=max(r['globalMaxResidual'] for r in accepted),maxAcceptedScaledResidual=max(r['globalMaxScaledResidual'] for r in accepted),
                maxComponentAllowance=max(r['maxLocalAllowance'] for r in accepted),acceptedAboveOldCutoffRankSteps=sum(r['globalMaxResidual']>=5e-18 for r in accepted))
def main():
    initial=len(sys.argv)>1 and sys.argv[1]=='initial';tag='' if initial else '_capFallback'
    refs=json.loads((STUDY/'data/processed/cantera_cv_regimes.json').read_text())
    original=json.loads((STUDY/'data/processed/cantera_reference.json').read_text())
    refs.insert(1,dict(label='standard',Tinitial=1100.,pInitial=101325.,records=original['records'],
                      toleranceEndpointDifference=original['toleranceEndpointDifference'],matchedMechanismSHA256=refs[0]['matchedMechanismSHA256']))
    rows=[];differences=[]
    for ref in refs:
        pair=[run(ref,'conservativeState',exe=EXE,component=flag,tag=tag) for flag in [False,True]];rows+=pair
        if all('error' not in r for r in pair):differences.append(dict(kind=ref['label'],a=pair[0]['name'],b=pair[1]['name'],fields=compare(RAW/pair[0]['name'],RAW/pair[1]['name'])))
    pair=[wave('conservativeState',64,exe_override=EXE,component=flag,tag=tag) for flag in [False,True]]
    for r in pair:
        if 'error' not in r:r.update(trace_summary(RAW/r['name']))
    rows+=pair
    if all('error' not in r for r in pair):differences.append(dict(kind='unequalMixture',a=pair[0]['name'],b=pair[1]['name'],fields=compare(RAW/pair[0]['name'],RAW/pair[1]['name'])))
    if initial:
        (STUDY/'data/processed/component_tolerance_allowance_only.json').write_text(json.dumps(dict(records=rows,comparisons=differences,scope='Initial allowance-only stopping control. Eight executed cases retained; planned F not run after field-comparison schema error. Superseded by separately tagged representability-stagnation replays.'),indent=2)+'\n')
        print('Retained allowance-only records',len(rows),flush=True);return
    pair=[]
    for flag in [False,True]:
        case=screen(kind='F',mode='conservativeState',dt=1e-6,ranks=4,every=0,exe=EXE,tag=tag+'_component'+('On' if flag else 'Off'),component_energy_tolerance=flag)
        if (case/'failure.json').exists():r=json.loads((case/'failure.json').read_text())
        else:
            r,_,_=summarize(case);local=totals(case)
            r.update(maxCellClosure=max(x['maxCellClosure'] for x in local),maxEOSRelative=max(x['maxEOSRelative'] for x in local),**trace_summary(case))
        pair.append(r)
    rows+=pair
    if all('error' not in r for r in pair):differences.append(dict(kind='F',a=pair[0]['name'],b=pair[1]['name'],fields=compare(RAW/pair[0]['name'],RAW/pair[1]['name'])))
    report=dict(records=rows,comparisons=differences,scope='Known component-scaled roundoff fallback at the original iteration cap. Logical replays may overlap other logical chemistry screens; all wall times excluded from performance ranking. Original failures and rejected exact-state-stagnation controls remain retained.')
    (STUDY/'data/processed/component_tolerance_cap.json').write_text(json.dumps(report,indent=2)+'\n')
    print('Stopping-rule records',len(rows),'failures',sum('error' in r for r in rows),'comparisons',len(differences),flush=True)
if __name__=='__main__':main()
