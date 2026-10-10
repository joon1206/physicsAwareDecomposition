"""Independent NASA7/property/reaction audit using pinned Cantera and inputs."""
from pathlib import Path
import csv,hashlib,json,math,shutil,sys,warnings
ROOT=Path(__file__).resolve().parents[1];sys.dont_write_bytecode=True
sys.path.insert(0,str(ROOT/'build/canteraPackages'))
sys.path.append(str(ROOT.parent/'physicsAwareDecomposition/scripts'))
sys.path.append(str(ROOT.parent/'physicsAwareDecomposition/actionStudy/scripts'))
from thermo_continuity import CONTROL,BASE,properties,sha
from thermo_reference import parse_nasa,RU
import cantera as ct
from cantera import ck2yaml
import numpy as np
from ruamel.yaml import YAML
STUDY=ROOT/'candidateStudy';RAW=STUDY/'data/raw';P=STUDY/'data/processed'
TARGET=RAW/'MechanismContinuity_v2'
def gas_species(gas):
    data={}
    for s in gas.species():
        assert isinstance(s.thermo,ct.NasaPoly2),s.name
        c=list(map(float,s.thermo.coeffs))
        data[s.name]=dict(mid=c[0],high=c[1:8],low=c[8:15],elements=s.composition,w=s.molecular_weight,
                          Tmin=s.thermo.min_temp,Tmax=s.thermo.max_temp)
    return data
def audit(name,data,gas=None):
    species=[];reactions=[];mixtures=[];checks=[]
    for s,d in data.items():
        t=d['mid'];lo=properties(d['low'],t);hi=properties(d['high'],t)
        record=dict(species=s,Tcommon=t,left=lo,right=hi,jumps={k:hi[k]-lo[k] for k in lo},units=dict(Cp='J/(kmol K)',h='J/kmol',s='J/(kmol K)',g='J/kmol'),coefficients=d)
        minima={}
        for branch,low,high in [('low',d.get('Tmin',200),t),('high',t,d.get('Tmax',5000))]:
            a=d[branch];roots=np.roots([4*a[4],3*a[3],2*a[2],a[1]])
            points=[low,high]+[float(x.real) for x in roots if abs(x.imag)<1e-7 and low<x.real<high]
            minima[branch]=min(properties(a,x)['Cp'] for x in points)
        record['computedBranchCpMin']=minima;species.append(record)
        if gas is not None:
            i=gas.species_index(s)
            for ttest in [max(d.get('Tmin',200),t-1),min(d.get('Tmax',5000),t+1)]:
                gas.TP=ttest,gas.reference_pressure;a=d['low'] if ttest<t else d['high'];v=properties(a,ttest)
                check=dict(species=s,T=ttest,Cp=gas.standard_cp_R[i]*RU,h=gas.standard_enthalpies_RT[i]*RU*ttest,s=gas.standard_entropies_R[i]*RU)
                checks.append(max(abs(check[k]-v[k])/max(abs(v[k]),1) for k in ['Cp','h','s']))
    mids=sorted(set(d['mid'] for d in data.values()))
    if gas is not None:
        nu=gas.product_stoich_coeffs-gas.reactant_stoich_coeffs
        B=np.array([[gas.n_atoms(s,e) for s in gas.species_names] for e in gas.element_names])
        elemental=float(np.max(np.abs(B@nu)))
    else:elemental=None
    for t in mids:
        limits=[]
        for side in ['left','right']:
            limits.append({s:properties(d['low'] if t<d['mid'] or (t==d['mid'] and side=='left') else d['high'],t) for s,d in data.items()})
        jumps={s:{k:limits[1][s][k]-limits[0][s][k] for k in ['Cp','h','s','g']} for s in data}
        if gas is not None:
            for r in range(gas.n_reactions):
                dh=math.fsum(nu[i,r]*jumps[s]['h'] for i,s in enumerate(gas.species_names))
                dg=math.fsum(nu[i,r]*jumps[s]['g'] for i,s in enumerate(gas.species_names))
                dl=-dg/(RU*t)
                reactions.append(dict(index=r,equation=gas.reaction_equation(r) if hasattr(gas,'reaction_equation') else gas.reaction(r).equation,Tcommon=t,deltaReactionEnthalpy=dh,deltaReactionGibbs=dg,deltaLogK=dl,relativeKJump=math.expm1(dl)))
        for label,y in [('unburnedH2',dict(H2=.0283,O2=.225,N2=.7467)),('branchRadicals',dict(H2=.0283,O2=.225,H=.0001,OH=.0001,N2=.7465)),('equalMoles',{s:d['w'] for s,d in data.items()})]:
            y={s:v for s,v in y.items() if s in data};total=math.fsum(y.values());y={s:v/total for s,v in y.items()}
            dh=math.fsum(y[s]*jumps[s]['h']/data[s]['w'] for s in y)
            ds=math.fsum(y[s]*jumps[s]['s']/data[s]['w'] for s in y)
            mixtures.append(dict(composition=label,Y=y,Tcommon=t,deltaHa=dh,deltaEa=dh,deltaS=ds,deltaG=dh-t*ds,units='J/kg; entropy J/(kg K)'))
    return dict(name=name,nSpecies=len(data),nReactions=0 if gas is None else gas.n_reactions,species=species,reactions=reactions,mixtures=mixtures,
                reactionElementResidualAtoms=elemental,independentCanteraPropertyMaxRelativeDifference=max(checks,default=0),
                rankedEnthalpy=sorted([dict(species=r['species'],Tcommon=r['Tcommon'],deltaH=r['jumps']['h'],deltaHSpecific=r['jumps']['h']/r['coefficients']['w']) for r in species],key=lambda r:abs(r['deltaHSpecific']),reverse=True),
                largestReactionEnthalpyJump=max((abs(r['deltaReactionEnthalpy']) for r in reactions),default=0),largestRelativeKJump=max((abs(r['relativeKJump']) for r in reactions),default=0),
                scope='Exact one-sided polynomial evaluation in binary arithmetic. Branch Cp extrema computed with floating polynomial roots; no interval-arithmetic positivity certificate claimed. Equilibrium K jumps at fixed T have identical Kp/Kc multiplicative factors.')
def main():
    out=TARGET/'audit_result.json'
    if out.exists():
        (P/'mechanism_continuity_audit.json').write_bytes(out.read_bytes());print('Reused immutable mechanism audit');return
    if TARGET.exists():raise RuntimeError('Retained incomplete '+str(TARGET))
    TARGET.mkdir();(TARGET/'driver_snapshot.py').write_bytes(Path(__file__).read_bytes())
    library=ROOT/'build/canteraPackages/cantera/data'
    reference=library/'example_data/ammonia-CO-H2-Alzueta-2023.yaml'
    shutil.copy2(reference,TARGET/reference.name)
    licenseFile=ROOT/'build/canteraPackages/cantera-3.2.0.dist-info/licenses/License.txt'
    if licenseFile.exists():shutil.copy2(licenseFile,TARGET/'Cantera_License.txt')
    gri=Path(r'\\wsl.localhost\Ubuntu\opt\OpenFOAM\OpenFOAM-v2012\tutorials\combustion\chemFoam\gri\chemkin')
    for file in ['chem.inp','therm.dat']:shutil.copy2(gri/file,TARGET/('gri_'+file))
    ck2yaml.convert(input_file=str(TARGET/'gri_chem.inp'),thermo_file=str(TARGET/'gri_therm.dat'),out_name=str(TARGET/'gri.yaml'),quiet=True)
    gases=[('legacyH2',ct.Solution(str(RAW/'cantera0D_pstd100000_matched_legacyPhase/legacyWeights.yaml'))),('installedGRI',ct.Solution(str(TARGET/'gri.yaml'))),('Alzueta2023_baseline',ct.Solution(str(TARGET/reference.name),'baseline'))]
    records=[audit(name,gas_species(gas),gas) for name,gas in gases]
    legacy=gases[0][1];yaml=YAML()
    for mode in ['HS','CpHS']:
        corrected=parse_nasa(CONTROL/f'{mode}.dat');original=yaml.load(RAW/'cantera0D_pstd100000_matched_legacyPhase/legacyWeights.yaml')
        for d in original['species']:
            coeff=corrected[d['name']];ranges=d['thermo']['temperature-ranges']
            d['thermo']['temperature-ranges']=[ranges[0],coeff['mid'],ranges[-1]]
            d['thermo']['data']=[coeff['low'],coeff['high']]
        dest=TARGET/f'H2_{mode}.yaml'
        with dest.open('w') as f:yaml.dump(original,f)
        gas=ct.Solution(str(dest));records.append(audit('H2_'+mode,gas_species(gas),gas))
    unique={}
    for path in sorted(RAW.glob('*/chemkin/therm.dat')):
        digest=sha(path);entry=unique.setdefault(digest,dict(path=path,uses=[]));entry['uses'].append(path.parent.parent.name)
    implicated=[]
    for digest,entry in unique.items():
        nasa=parse_nasa(entry['path']);r=audit('retainedThermo_'+digest[:12],nasa)
        r.update(sourceSHA256=digest,sourcePath=str(entry['path'].relative_to(ROOT)),usedBy=entry['uses']);implicated.append(r)
    result=dict(canteraVersion=ct.__version__,driverSHA256=sha(__file__),mechanisms=records,retainedCoefficientSets=implicated,
                referenceProvenance=dict(file=reference.name,sha256=sha(reference),url='https://github.com/Cantera/cantera/blob/v3.2.0/data/example_data/ammonia-CO-H2-Alzueta-2023.yaml',phase='baseline',licenseScope='Cantera packaged data redistribution; retained license. Original mechanism references in file. Modern mechanism is an audit reference, not thermo-only kinetic comparator.'),
                inputs={p.name:sha(p) for p in TARGET.iterdir() if p.is_file()},controlManifestSHA256=sha(CONTROL/'manifest.json'))
    out.write_text(json.dumps(result,indent=2)+'\n');(P/'mechanism_continuity_audit.json').write_bytes(out.read_bytes())
    for r in records:print(r['name'],r['nSpecies'],r['nReactions'],'maxspecificH',r['rankedEnthalpy'][0],'Kjump',r['largestRelativeKJump'],flush=True)
    print('Unique retained coefficient sets',len(implicated),flush=True)
if __name__=='__main__':main()
