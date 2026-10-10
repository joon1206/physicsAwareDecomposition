"""Resolution-aware reacting comparisons; no underresolved curve is exact."""
from pathlib import Path
import json,math
from foamio import read_field
ROOT=Path(__file__).resolve().parents[1];STUDY=ROOT/'candidateStudy';rows=[]
for meta in sorted(list((STUDY/'data/raw').glob('Central_F_*/central_result.json'))+list((STUDY/'data/raw').glob('HLLC_F_*/central_result.json'))+list((STUDY/'data/raw').glob('InvF_*/result.json'))):
    config=json.loads(meta.read_text());case=meta.parent;nx=config['nCells'];tf=config['dt']*config['steps'];end=case/format(tf,'.12g')
    T=read_field(end/'T',nx);U=read_field(end/'U',nx);rho=read_field(end/'rho',nx);H2=read_field(end/'H2',nx);H2O=read_field(end/'H2O',nx)
    initialH2=(config.get('initial',{}).get('mass') or None)
    if 'end' in config:massDrift=config['massDrift'];energyDrift=config['signedEnergyDrift'];element=config['elementDrift']
    else:
        summary=json.loads((case/'inviscid_summary.json').read_text());massDrift=summary['massDrift'];energyDrift=summary['signedEnergyDrift'];element=summary['elementDrift']
    row=dict(name=case.name,kind=config['kind'],mode=config.get('mode','hllc' if case.name.startswith('HLLC_') else 'central'),nx=nx,dt=config['dt'],TF=tf,
        Tmean=math.fsum(T)/nx,Tmin=min(T),Tmax=max(T),Umax=max(math.sqrt(math.fsum(x*x for x in u)) for u in U),
        H2MassFraction=math.fsum(r*y for r,y in zip(rho,H2))/math.fsum(rho),H2OMassFraction=math.fsum(r*y for r,y in zip(rho,H2O))/math.fsum(rho),
        energyDrift=energyDrift,massDrift=massDrift,maxElementDrift=max(abs(v) for v in element.values()),
        sourceSnapshot=config['sourceSnapshot'],executableSHA256=config['executableSHA256'])
    rows.append(row);print(case.name,'meanT',row['Tmean'],'H2O massfraction',row['H2OMassFraction'],flush=True)
(STUDY/'data/processed/inviscid_comparison.json').write_text(json.dumps(dict(records=rows,
    scope='Same inviscid PDE, chemistry, initial profile and geometry. Different spatial fluxes; grid and time refinement required. No underresolved curve is an independent exact reference.'),indent=2)+'\n')
