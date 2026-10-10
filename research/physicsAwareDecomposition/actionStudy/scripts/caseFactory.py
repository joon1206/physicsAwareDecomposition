"""Closed periodic reactive-flow boxes using public OpenFOAM mechanisms.

These are controlled reacting-flow experiments, not validated burner models.
The assigned regime names are hypotheses; measured histories determine whether
the intended persistence, translation, ignition or decay actually occurred.
"""
from pathlib import Path
import hashlib, json, math, os, re, shutil, subprocess, time, threading
from foamio import read_field, proc_metrics, patches

PAD = Path(__file__).resolve().parents[2]
ROOT = Path(os.environ.get('PAD_ACTION_ROOT', PAD/'actionStudy'))
TUTORIALS = Path(os.environ['FOAM_TUTORIALS'])
SPECS = {
    'persistent': dict(velocity=0, cold=500, hot=1300, width=.0015),
    'translating': dict(velocity=60, cold=500, hot=1300, width=.0015),
    'ignition': dict(velocity=0, cold=850, hot=1050, width=.003),
    'decay': dict(velocity=0, cold=500, hot=1800, width=.0015, depleted=True),
    'uniform': dict(velocity=0, cold=1100, hot=1100, width=.0015),
    'chemistryDominated': dict(velocity=0, cold=700, hot=1400, width=.002, mechanism='gri'),
    'transportDominated': dict(velocity=60, cold=300, hot=300, width=.002),
    'heldoutMoving': dict(velocity=120, cold=600, hot=1250, width=.0025),
    'heldoutIgnition': dict(velocity=0, cold=800, hot=980, width=.004),
    'heldoutPersistent': dict(velocity=0, cold=600, hot=1200, width=.003),
}

def command(args, case, log, timeout=300, env=None):
    start=time.perf_counter()
    with Path(log).open('w') as stream:
        process_env=dict(os.environ if env is None else env);process_env['PWD']=str(case)
        p=subprocess.Popen(list(map(str,args)),cwd=case,stdout=stream,
                           stderr=subprocess.STDOUT,start_new_session=True,env=process_env)
        expired=[]
        def stop():
            import signal
            expired.append(True)
            try:os.killpg(p.pid,signal.SIGKILL)
            except ProcessLookupError:pass
        watchdog=threading.Timer(timeout,stop);watchdog.start()
        try:p.wait()
        finally:watchdog.cancel()
        if expired:raise RuntimeError(f'timeout: {log}')
    elapsed=time.perf_counter()-start
    if p.returncode:
        raise RuntimeError(f'{args[0]} failed: {log}')
    return elapsed

def header(name, cls='dictionary'):
    return f'FoamFile {{ version 2.0; format ascii; class {cls}; object {name}; }}\n'

def field(path, values, dimensions='[0 0 0 0 0 0 0]', vector=False):
    kind='vector' if vector else 'scalar'
    text=header(path.name,'vol'+kind.title()+'Field')+f'dimensions {dimensions};\n'
    if isinstance(values,(int,float)):
        text+=f'internalField uniform {values:.17g};\n'
    elif vector and isinstance(values,tuple):
        text+='internalField uniform ('+' '.join(map(str,values))+');\n'
    else:
        text+=f'internalField nonuniform List<{kind}>\n{len(values)}\n(\n'
        text+='\n'.join('('+' '.join(map(str,x))+')' if vector else f'{x:.17g}' for x in values)+'\n);\n'
    text+='boundaryField {\nleft { type cyclic; }\nright { type cyclic; }\n'
    text+='walls { type symmetry; }\nfrontAndBack { type empty; }\n}\n'
    path.write_text(text)

def set_control(case, start=0, steps=40, dt=2e-6, write_interval=None,restart_state=True):
    (case/'system/controlDict').write_text(header('controlDict')+f'''
application reactingFoamPAD;
startFrom startTime;
startTime {start:.17g};
stopAt endTime;
endTime {start+steps*dt:.17g};
deltaT {dt:.17g};
adjustTimeStep no;
writeControl timeStep;
writeInterval {write_interval or steps};
writeFormat ascii;
writePrecision 16;
timePrecision 12;
writeCompression off;
runTimeModifiable false;
padTiming true;
padWriteFinal true;
padRestartState {'true' if restart_state else 'false'};
padThermoCorrections 2;
libs ("libcostChemistry.so" "libstuttgartV2012.so");
''')

def set_chemistry(case, action='A0', trace=0, update=0):
    task=action in ['AC','AH']
    (case/'constant/chemistryProperties').write_text(header('chemistryProperties')+f'''
chemistryType {{ solver {'ode' if task else 'costOde'}; method {'LoadBalancedChemistryModel' if task else 'standard'}; }}
chemistry on;
initialChemicalTimeStep 1e-7;
maxChemicalTimeStep 1e-3;
Treact 500;
odeCoeffs {{ solver Rosenbrock34; absTol 1e-12; relTol 1e-5; }}
LoadBalancedCoeffs {{ updateIter {update}; minFractionOfCellsToSend 0.02; }}
costAlpha 1;
costTraceInterval {trace};
cellTiming true;
''')

def make_case(name, regime='persistent', nx=48, ny=12, dt=2e-6,
              steps=40, action='A0', trace=0):
    preprocessing_start=time.perf_counter()
    case=ROOT/'data/raw'/name
    if case.exists():
        raise RuntimeError(f'refusing to overwrite {case}')
    for sub in ['0','constant','system','chemkin']:(case/sub).mkdir(parents=True,exist_ok=True)
    spec=SPECS[regime].copy(); mech=spec.get('mechanism','h2')
    source=TUTORIALS/'combustion/chemFoam'/mech/'chemkin'
    for p in source.iterdir():
        if p.is_file() and p.name in ['chem.inp','therm.dat','transportProperties']:
            shutil.copy2(p,case/'chemkin'/p.name)
    (case/'constant/thermophysicalProperties').write_text(header('thermophysicalProperties')+'''
thermoType { type hePsiThermo; mixture reactingMixture; transport sutherland;
thermo janaf; energy sensibleEnthalpy; equationOfState perfectGas; specie specie; }
inertSpecie N2;
CHEMKINFile "<case>/chemkin/chem.inp";
CHEMKINThermoFile "<case>/chemkin/therm.dat";
CHEMKINTransportFile "<case>/chemkin/transportProperties";
''')
    (case/'constant/turbulenceProperties').write_text(header('turbulenceProperties')+'simulationType laminar;\n')
    (case/'constant/combustionProperties').write_text(header('combustionProperties')+'combustionModel laminar;\nlaminarCoeffs { integrateReactionRate true; }\n')
    (case/'system/blockMeshDict').write_text(header('blockMeshDict')+f'''
scale 1;
vertices ((0 0 0) (.02 0 0) (.02 .008 0) (0 .008 0)
          (0 0 .001) (.02 0 .001) (.02 .008 .001) (0 .008 .001));
blocks (hex (0 1 2 3 4 5 6 7) ({nx} {ny} 1) simpleGrading (1 1 1));
edges ();
boundary (
 left {{ type cyclic; neighbourPatch right; faces ((0 4 7 3)); }}
 right {{ type cyclic; neighbourPatch left; faces ((1 2 6 5)); }}
 walls {{ type symmetry; faces ((0 1 5 4) (3 7 6 2)); }}
 frontAndBack {{ type empty; faces ((0 3 2 1) (4 5 6 7)); }}
);
mergePatchPairs ();
''')
    original=TUTORIALS/'combustion/reactingFoam/laminar/counterFlowFlame2DLTS/system'
    schemes=(original/'fvSchemes').read_text().replace('localEuler','Euler')
    # The detailed premixed-kernel pilot exposed large partition sensitivity
    # with limitedLinear. First-order upwind passed the predeclared gate.
    # This choice is common to every action and is a disclosed accuracy limit.
    schemes=re.sub(r'limitedLinearV? 1','upwind',schemes)
    (case/'system/fvSchemes').write_text(schemes)
    solution=(original/'fvSolution').read_text()
    solution=re.sub(r'(tolerance\s+)[^;]+;',r'\g<1>1e-14;',solution)
    solution=re.sub(r'(relTol\s+)[^;]+;',r'\g<1>0;',solution)
    (case/'system/fvSolution').write_text(solution)
    set_control(case,steps=steps,dt=dt);set_chemistry(case,action,trace)
    # CHEMKIN species declarations contain no reaction-line parsing assumptions.
    mechanism=(case/'chemkin/chem.inp').read_text()
    block=re.search(r'(?is)\bSPECIES\b(.*?)\bEND\b',mechanism)[1]
    species=re.sub(r'![^\n]*','',block).split()
    n=nx*ny
    temperatures=[spec['cold']+(spec['hot']-spec['cold'])*math.exp(-((.02*(i%nx+.5)/nx-.005)/spec['width'])**4) for i in range(n)]
    field(case/'0/T',temperatures,'[0 0 0 1 0 0 0]')
    field(case/'0/p',101325.,'[1 -1 -2 0 0 0 0]')
    field(case/'0/U',(spec['velocity'],0,0),'[0 1 -1 0 0 0 0]',True)
    composition={'H2':.0283,'O2':.225,'N2':.7467}
    if spec.get('depleted'):composition={'H2':.0003,'O2':.0024,'H2O':.25,'N2':.7473}
    for s in species:field(case/'0'/s,composition.get(s,0.))
    field(case/'0/Ydefault',0.)
    field(case/'0/alphat',0.,'[1 -1 -1 0 0 0 0]')
    command(['blockMesh'],case,case/'blockMesh.log')
    info=dict(regime=regime,nx=nx,ny=ny,nCells=n,dt=dt,species=species,
              specification=spec,source=str(source),mechanism=mech,
              mechanismSHA256=hashlib.sha256((case/'chemkin/chem.inp').read_bytes()).hexdigest())
    info['preprocessingWall']=time.perf_counter()-preprocessing_start
    (case/'case.json').write_text(json.dumps(info,indent=2))
    return case

def decompose(case, ranks=4, weighted=False, start=0, force=False):
    if ranks==1:return 0.,[dict(rank=0,nCells=json.loads((case/'case.json').read_text())['nCells'],processorFaces=0,nNeighbours=0)]
    text=header('decomposeParDict')+f'numberOfSubdomains {ranks};\nmethod scotch;\n'
    if weighted:text+='weightField cellWeight;\n'
    (case/'system/decomposeParDict').write_text(text)
    args=['decomposePar','-time',format(start,'.12g')]
    if force:args.append('-force')
    elapsed=command(args,case,case/'decompose.log')
    return elapsed,proc_metrics(case)

def solve(case,ranks=4,exe='reactingFoamPAD',timeout=300,profile=False):
    # Retain completed segment clocks before native loggers open in write mode.
    # This is required to audit live decisions from their own past prefixes.
    control=(case/'system/controlDict').read_text()
    start_name=format(float(re.search(r'\bstartTime\s+([^;]+);',control)[1]),'.12g')
    previous_log=case/'solver.log'
    if previous_log.exists():
        destination=case/f'solver_until_{start_name}.log'
        if destination.exists():raise RuntimeError('refusing to replace retained segment log: '+str(destination))
        previous_log.rename(destination)
    bases=list(case.glob('processor[0-9]*')) if ranks>1 else [case]
    for base in bases:
        performance=base/'postProcessing/performance'
        if performance.exists():
            retained=base/'postProcessing/retainedPerformance'/f'until_{start_name}'
            retained.parent.mkdir(exist_ok=True)
            if retained.exists():raise RuntimeError('refusing to replace retained segment clocks: '+str(retained))
            performance.rename(retained)
    args=['mpirun','--bind-to','core','--map-by','core','--nooversubscribe',
          '--report-bindings','-np',str(ranks),exe]
    if ranks>1:args.append('-parallel')
    env=os.environ.copy()
    if profile:
        directory=case/'mpiProfile';directory.mkdir(exist_ok=True)
        env['PAD_MPI_PROFILE_DIR']=str(directory)
        env['LD_PRELOAD']=str(PAD/'build/lib/libpadMPIProfile.so')
    elapsed=command(args,case,case/'solver.log',timeout,env)
    assert_endpoint(case,ranks)
    return elapsed

def assert_endpoint(case,ranks):
    """Reject incomplete continuations before their clocks become evidence."""
    import csv
    text=(case/'system/controlDict').read_text()
    if not re.search(r'padWriteFinal\s+true\s*;',text):return
    get=lambda key:float(re.search(r'\b'+key+r'\s+([^;]+);',text)[1])
    start,end,dt=get('startTime'),get('endTime'),get('deltaT')
    expected_steps=round((end-start)/dt)
    bases=[case/f'processor{p}' for p in range(ranks)] if ranks>1 else [case]
    for base in bases:
        actual=float(latest_time(base))
        if abs(actual-end)>max(1e-13,dt*1e-6):
            raise RuntimeError(f'checkpoint ends at {actual}, expected {end}: {base}')
        directory=base/format(end,'.12g')
        for field_name in ['T','h','rho']:
            if not (directory/field_name).exists():raise RuntimeError(f'missing final {field_name}: {directory}')
        files=list((base/'postProcessing/performance').glob('rank*.csv'))
        if files:
            with files[0].open() as stream:rows=list(csv.DictReader(stream))
            times=[float(r['time']) for r in rows]
            if len(times)!=expected_steps or len(set(times))!=expected_steps or abs(times[-1]-end)>dt*1e-6:
                raise RuntimeError(f'wrong physical-step count/end time: {base}')

def latest_time(case, parallel=False):
    base=case/'processor0' if parallel else case
    times=[p for p in base.iterdir() if p.is_dir() and re.fullmatch(r'[0-9.eE+-]+',p.name)]
    return max(times,key=lambda p:float(p.name)).name

def reconstruct(case):
    return command(['reconstructPar','-latestTime'],case,case/'reconstruct.log')

def pilot():
    for regime in ['persistent','translating','ignition','decay','uniform','transportDominated','chemistryDominated']:
        case=make_case('pilot/'+regime,regime,nx=32,ny=8,steps=20,trace=1)
        setup,_=decompose(case,4)
        elapsed=solve(case,4,timeout=180)
        reconstruct(case);end=case/latest_time(case)
        T=read_field(end/'T',256)
        result=dict(regime=regime,solverWall=elapsed,decompositionWall=setup,
                    temperatureMin=min(T),temperatureMax=max(T),finalTime=end.name)
        (case/'pilot.json').write_text(json.dumps(result,indent=2))
        print('MEASURED pilot',result,flush=True)

if __name__=='__main__':pilot()
