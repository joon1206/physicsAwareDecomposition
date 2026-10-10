"""Declared algebraic continuity controls; no fit to unavailable physical data."""
from pathlib import Path
import copy, hashlib, json, math, sys
ROOT=Path(__file__).resolve().parents[1]
sys.path.append(str(ROOT.parent/'physicsAwareDecomposition/scripts'))
sys.path.append(str(ROOT.parent/'physicsAwareDecomposition/actionStudy/scripts'))
from thermo_reference import parse_nasa, RU
BASE=ROOT/'candidateStudy/data/raw/B_none_dt2e-06_s1_g0_o1_p1/chemkin/therm.dat'
CONTROL=ROOT/'candidateStudy/thermoControls/v1'

def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def properties(a,t):
    cp=RU*math.fsum(a[k]*t**k for k in range(5))
    h=RU*(math.fsum(a[k]*t**(k+1)/(k+1) for k in range(5))+a[5])
    s=RU*(a[0]*math.log(t)+math.fsum(a[k]*t**k/k for k in range(1,5))+a[6])
    return dict(Cp=cp,h=h,s=s,g=h-t*s)
def repair(spec,mode):
    out=copy.deepcopy(spec);a=out['high'];t=out['mid'];lo=properties(out['low'],t)
    if mode=='CpHS':a[0]+=(lo['Cp']-properties(a,t)['Cp'])/RU
    elif mode!='HS':raise ValueError(mode)
    a[5]+=(lo['h']-properties(a,t)['h'])/RU
    a[6]+=(lo['s']-properties(a,t)['s'])/RU
    return out
def number(x):
    for digits in range(15,7,-1):
        value=f'{x:.{digits}g}'
        if len(value)<=15:return value.rjust(15)
    raise ValueError(x)
def write_control(mode,target):
    source=parse_nasa(BASE);lines=BASE.read_text().splitlines()
    for i,line in enumerate(lines):
        if len(line)<80 or line[79]!='1':continue
        name=line[:18].strip().split()[0];spec=repair(source[name],mode)
        if mode=='CpHS':lines[i+1]=number(spec['high'][0])+lines[i+1][15:]
        lines[i+2]=number(spec['high'][5])+number(spec['high'][6])+lines[i+2][30:]
    target.write_text('\n'.join(lines)+'\n')
    actual=parse_nasa(target);details=[]
    for name,spec in actual.items():
        assert spec['low']==source[name]['low']
        if mode=='HS':assert spec['high'][:5]==source[name]['high'][:5]
        low=properties(spec['low'],spec['mid']);high=properties(spec['high'],spec['mid'])
        details.append(dict(species=name,jumps={k:high[k]-low[k] for k in low},coefficients=spec,
                            highCpConstantChange=RU*(spec['high'][0]-source[name]['high'][0])))
    return details
def main():
    manifest=CONTROL/'manifest.json'
    if manifest.exists():
        data=json.loads(manifest.read_text())
        for mode,record in data['controls'].items():assert sha(CONTROL/f'{mode}.dat')==record['sha256']
        print('Reused immutable thermo controls');return
    if CONTROL.exists():raise RuntimeError('Retained incomplete thermo controls')
    CONTROL.mkdir(parents=True)
    controls={}
    for mode in ['HS','CpHS']:
        path=CONTROL/f'{mode}.dat';details=write_control(mode,path)
        controls[mode]=dict(sha256=sha(path),species=details)
    data=dict(sourcePath=str(BASE.relative_to(ROOT)),sourceSHA256=sha(BASE),driverSHA256=sha(__file__),controls=controls,
              scope='HS adjusts only high-branch integration constants. CpHS additionally shifts high-branch constant Cp coefficient. Low branch including 298.15 K references remains exact. These are algebraic continuity sensitivity controls, not independently refitted accurate thermochemistry; source tabulated data are unavailable. Printed residual jumps are measured after fixed-width serialization.')
    manifest.write_text(json.dumps(data,indent=2)+'\n')
    (CONTROL/'driver_snapshot.py').write_bytes(Path(__file__).read_bytes())
    print(json.dumps({mode:{k:max(abs(s['jumps'][k]) for s in v['species']) for k in ['Cp','h','s','g']} for mode,v in controls.items()}))
if __name__=='__main__':main()
