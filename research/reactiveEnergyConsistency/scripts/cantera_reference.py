"""Independent adiabatic constant-volume chemistry; retained Cantera 3.2 inputs."""
from pathlib import Path
import csv,hashlib,json,math,sys
ROOT=Path(__file__).resolve().parents[1]
sys.dont_write_bytecode=True
sys.path.insert(0,str(ROOT/'build/canteraPackages'))
sys.path.append(str(ROOT.parent/'physicsAwareDecomposition/scripts'))
import cantera as ct
from cantera import ck2yaml
from ruamel.yaml import YAML
from foamio import read_field
from thermo_reference import RU,ATOMIC,parse_nasa,ha
STUDY=ROOT/'candidateStudy';source=STUDY/'data/raw/B_none_dt2e-06_s1_g0_o1_p1'
pstd=float(sys.argv[1]) if len(sys.argv)>1 else 100000.
strictMatch=len(sys.argv)>2 and sys.argv[2]=='matched'
target=STUDY/f'data/raw/cantera0D_pstd{pstd:g}{"_matched" if strictMatch else ""}_legacyPhase';target.mkdir(exist_ok=True)
mechanism=target/'converted.yaml'
if not mechanism.exists():
    ck2yaml.convert(input_file=str(source/'chemkin/chem.inp'),thermo_file=str(source/'chemkin/therm.dat'),out_name=str(mechanism))
yaml=YAML();data=yaml.load(mechanism)
# Use the documented legacy molecular weights, not modern default atomic weights.
elements=data['phases'][0]['elements'];data['elements']=[{'symbol':e,'atomic-weight':ATOMIC[e.upper()]} for e in elements]
effectivePstd=pstd*ct.gas_constant/RU if strictMatch else pstd
for speciesData in data['species']:speciesData['thermo']['reference-pressure']=effectivePstd
if strictMatch:
    # v2012 chemkinLexer.L uses RRcal=1.987316 independent of thermodynamic RR.
    factor=(ct.gas_constant/4184)/1.987316
    for reactionData in data['reactions']:
        for key in ['rate-constant','low-P-rate-constant','high-P-rate-constant']:
            if key in reactionData:reactionData[key]['Ea']*=factor
matched=target/'legacyWeights.yaml'
with matched.open('w') as f:yaml.dump(data,f)
gas=ct.Solution(str(matched));species=gas.species_names
Y0={s:read_field(source/'0'/s,256)[0] for s in species};p0=read_field(source/'0/p',256)[0]
T0=read_field(source/'0/T',256)[0];gas.TPY=T0,p0,Y0
nasa=parse_nasa(source/'chemkin/therm.dat')
legacyDensity=p0/(T0*RU*math.fsum(Y0[s]/nasa[s]['w'] for s in species))
if strictMatch:gas.TDY=T0,legacyDensity,Y0
ofcp=sum(Y0[s]*(ha(nasa[s],T0+.001)-ha(nasa[s],T0-.001))/.002 for s in species)
matching=dict(legacyGasConstant=RU,canteraGasConstant=ct.gas_constant,
    thermodynamicReferencePressure=pstd,
    effectiveCanteraReferencePressure=effectivePstd,strictConstantConversion=strictMatch,
    activationEnergyConversionFactor=(ct.gas_constant/4184)/1.987316 if strictMatch else 1,
    pressureReportingFactor=RU/ct.gas_constant if strictMatch else 1,
    relativeGasConstantMismatch=ct.gas_constant/RU-1,legacyCp=ofcp,canteraCp=gas.cp_mass,
    molecularWeightMaxError=max(abs(gas.molecular_weights[gas.species_index(s)]-nasa[s]['w']) for s in species),
    caveat='Legacy molecular weights are explicit. Matched mode aligns Kc through reference-pressure/R, Arrhenius Ea/Rcal and initial density; pressure comparisons use the declared EOS R conversion. Independent pointwise rate verification remains required.')
records=[];endpoints=[]
for tolerance in [1e-10,1e-12]:
    gas=ct.Solution(str(matched));gas.TPY=T0,p0,Y0
    if strictMatch:gas.TDY=T0,legacyDensity,Y0
    # Cantera 3.2 clone=True reconstitutes this custom-element phase with
    # default atomic weights. Keep the independently created input phase.
    reactor=ct.IdealGasReactor(gas,clone=False,energy='on')
    reactorWeightError=max(abs(reactor.phase.molecular_weights[reactor.phase.species_index(s)]-nasa[s]['w']) for s in species)
    if reactorWeightError>1e-12:raise RuntimeError('Reactor phase changed declared molecular weights')
    network=ct.ReactorNet([reactor]);network.rtol=tolerance;network.atol=tolerance*1e-6
    e0=reactor.mass*reactor.phase.int_energy_mass;initialDensity=reactor.density
    rows=[]
    for step in range(121):
        t=step*2e-6
        if step:network.advance(t)
        g=reactor.phase
        r=dict(time=t,T=reactor.T,p=g.P*(RU/ct.gas_constant if strictMatch else 1),rho=reactor.density,E=reactor.mass*g.int_energy_mass,
          energyDrift=(reactor.mass*g.int_energy_mass-e0)/max(abs(e0),1e-30))
        r.update({s:float(g.Y[g.species_index(s)]) for s in species});rows.append(r)
    with (target/f'trajectory_rtol{tolerance:g}.csv').open('w',newline='') as f:
        writer=csv.DictWriter(f,fieldnames=rows[0]);writer.writeheader();writer.writerows(rows)
    endpoints.append(rows[-1]);records.append(dict(rtol=tolerance,atol=network.atol,
       initialDensity=initialDensity,initialPressure=rows[0]['p'],reactorClone=False,
       reactorMolecularWeightMaxError=reactorWeightError,
       end=rows[-1],maxEnergyDrift=max(abs(x['energyDrift']) for x in rows)))
comparisons=[]
for meta in sorted(list((STUDY/'data/raw').glob('B_*/result.json'))+list((STUDY/'data/raw').glob('Central_B_*/central_result.json'))+list((STUDY/'data/raw').glob('HLLC_B_*/central_result.json'))):
    config=json.loads(meta.read_text())
    if config.get('formationAblation',{}).get('scale',1)!=1:continue
    case=meta.parent;end=case/format(config['dt']*config['steps'],'.12g');n=config['nCells'];ref=endpoints[-1]
    fieldErrors={}
    for s in ['T','p','rho']+species:
        vals=read_field(end/s,n)
        ds=[abs(v-ref[s]) for v in vals]
        fieldErrors[s]=dict(L1=math.fsum(ds)/n,L2=math.sqrt(math.fsum(x*x for x in ds)/n),Linf=max(ds))
    comparisons.append(dict(name=case.name,dt=config['dt'],mode=config.get('mode','hllc' if case.name.startswith('HLLC_') else 'central'),errors=fieldErrors))
result=dict(canteraVersion=ct.__version__,mechanismSHA256=hashlib.sha256(matched.read_bytes()).hexdigest(),
  matching=matching,records=records,toleranceEndpointDifference={k:abs(endpoints[0][k]-endpoints[1][k]) for k in endpoints[0]},
  comparisons=comparisons,scope='Independent 0D implementation comparison with declared EOS/kinetic constant conversion and verified reactor-phase molecular weights; instantaneous rate/property matching retained separately.')
(target/'reference_summary.json').write_text(json.dumps(result,indent=2)+'\n')
(STUDY/'data/processed/cantera_reference.json').write_text(json.dumps(result,indent=2)+'\n')
print('Cantera',ct.__version__,'reference T',endpoints[-1]['T'],'drift',records[-1]['maxEnergyDrift'])
for r in comparisons:print(r['name'],'T error',r['errors']['T']['Linf'])
