"""Independent NASA branch diagnostic for retained spatial source failures."""
from pathlib import Path
import csv,hashlib,json,math
from thermo_reference import parse_nasa,RU
ROOT=Path(__file__).resolve().parents[1];STUDY=ROOT/'candidateStudy';P=STUDY/'data/processed'

def molar_h(coefficients,t):
    return RU*(math.fsum(coefficients[k]*t**(k+1)/(k+1) for k in range(5))+coefficients[5])

def main():
    cases=json.loads((P/'cv_reacting_screen.json').read_text());records=[];thermo=[]
    for cfg in cases:
        if cfg['odeThermalPath']!='constantVolume':continue
        case=STUDY/'data/raw'/cfg['name'];nasa=parse_nasa(case/'chemkin/therm.dat')
        species=json.loads((case/'case.json').read_text())['species']
        jumps={s:dict(mid=nasa[s]['mid'],enthalpyJumpMolar=molar_h(nasa[s]['high'],nasa[s]['mid'])-molar_h(nasa[s]['low'],nasa[s]['mid']),
                      molecularWeight=nasa[s]['w']) for s in species}
        if not thermo:thermo=[dict(species=s,**r,enthalpyJumpSpecific=r['enthalpyJumpMolar']/r['molecularWeight']) for s,r in jumps.items()]
        midpoints=sorted({r['mid'] for r in jumps.values()});rows=[]
        for path in case.glob('**/cvChemistry/rank*.csv'):
            with path.open() as stream:trace=list(csv.DictReader(stream))
            for row in trace:
                r={k:float(v) for k,v in row.items()};r['rankFile']=str(path.relative_to(case))
                r['energyChange']=r['energyFinal']-r['energyInitial']
                r['relativeEnergyChange']=abs(r['energyChange'])/max(abs(r['energyInitial']),1.)
                r['crossedMidpoints']=[mid for mid in midpoints if min(r['Tinitial'],r['Tfinal'])<mid<=max(r['Tinitial'],r['Tfinal'])]
                rows.append(r)
        failing=[r for r in rows if r['relativeEnergyChange']>=1e-10]
        categories=[]
        for crossing in [False,True]:
            selected=[r for r in rows if bool(r['crossedMidpoints'])==crossing]
            categories.append(dict(endpointStraddlesMidpoint=crossing,sourceCalls=len(selected),
                                   invariantFailures=sum(r['relativeEnergyChange']>=1e-10 for r in selected),
                                   maxRelativeEnergyChange=max((r['relativeEnergyChange'] for r in selected),default=0.)))
        records.append(dict(name=cfg['name'],mode=cfg['mode'],dt=cfg['dt'],sourceCalls=len(rows),
                            failingSourceCalls=len(failing),categories=categories,
                            worstCalls=sorted(rows,key=lambda r:r['relativeEnergyChange'],reverse=True)[:8],
                            chemistrySourceSnapshot=cfg['chemistrySourceSnapshot'],chemistryLibrarySHA256=cfg['chemistryLibrarySHA256']))
    result=dict(thermo=thermo,records=records,
                diagnosticScriptSHA256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
                scope='Native accepted-source endpoint straddling versus legacy NASA energy jumps. No crossing concentration trace or exact jump attribution; non-straddling endpoints do not exclude internal excursions across the midpoint.')
    (P/'cv_source_invariant_audit.json').write_text(json.dumps(result,indent=2)+'\n')
    for r in thermo:print(r)
    for r in records:print(r['name'],r['categories'],'worst',r['worstCalls'][0])
if __name__=='__main__':main()
