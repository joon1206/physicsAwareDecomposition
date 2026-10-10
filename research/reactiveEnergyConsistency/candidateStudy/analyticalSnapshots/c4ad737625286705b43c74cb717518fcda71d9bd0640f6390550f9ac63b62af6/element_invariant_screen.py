"""Exact linear FV compatibility screen; known invariant reduction, no native claim."""
from pathlib import Path
import hashlib,json,math
from thermo_reference import parse_nasa,ATOMIC
ROOT=Path(__file__).resolve().parents[1];STUDY=ROOT/'candidateStudy';N=8;DT=1e-3
SPECIES=['H2','H','O2','O','OH','HO2','H2O2','H2O','AR','N2']
DEPENDENT=dict(H='H2',O='O2',N='N2',AR='AR')

def solve(matrix,rhs):
    a=[row[:]+[b] for row,b in zip(matrix,rhs)]
    for j in range(N):
        pivot=max(range(j,N),key=lambda i:abs(a[i][j]));a[j],a[pivot]=a[pivot],a[j]
        if abs(a[j][j])<1e-30:raise RuntimeError('Singular algebraic test')
        for i in range(j+1,N):
            f=a[i][j]/a[j][j]
            for k in range(j,N+1):a[i][k]-=f*a[j][k]
    x=[0.]*N
    for j in range(N-1,-1,-1):x[j]=(a[j][N]-math.fsum(a[j][k]*x[k] for k in range(j+1,N)))/a[j][j]
    return x

def multiply(matrix,x):return [math.fsum(a*b for a,b in zip(row,x)) for row in matrix]

def operator(rhof,flux,mu):
    matrix=[[0.]*N for i in range(N)]
    for i in range(N):matrix[i][i]=rhof[i]/DT
    for i,phi in enumerate(flux):
        j=(i+1)%N;donor=i if phi>=0 else j
        matrix[i][donor]+=phi;matrix[j][donor]-=phi
        matrix[i][i]+=mu;matrix[i][j]-=mu;matrix[j][j]+=mu;matrix[j][i]-=mu
    return matrix

def experiment(nasa,variable_elements=False,unequal_diffusion=False):
    coefficients={e:{s:nasa[s]['elements'].get(e,0)*ATOMIC[e]/nasa[s]['w'] for s in SPECIES} for e in DEPENDENT}
    rn=[1.2+.1*math.cos(2*math.pi*(i+.5)/N) for i in range(N)]
    flux=[.04*math.sin(2*math.pi*(i+1)/N) for i in range(N)]
    rf=[rn[i]-DT*(flux[i]-flux[(i-1)%N]) for i in range(N)]
    initial={s:[0.]*N for s in SPECIES};sources={s:[0.]*N for s in SPECIES}
    for i in range(N):
        extent=.002*(1+.5*math.sin(2*math.pi*(i+.5)/N))
        perturb=.003*math.sin(2*math.pi*(i+.5)/N) if variable_elements else 0.
        initial['H2'][i]=.0283+perturb-nasa['H2']['w']*extent
        initial['O2'][i]=.225-.5*nasa['O2']['w']*extent
        initial['H2O'][i]=nasa['H2O']['w']*extent;initial['N2'][i]=.7467-perturb
        rate=.3*(1+.2*math.cos(2*math.pi*(i+.5)/N))
        sources['H2'][i]=-nasa['H2']['w']*rate
        sources['O2'][i]=-.5*nasa['O2']['w']*rate
        sources['H2O'][i]=nasa['H2O']['w']*rate
    z={e:[math.fsum(coefficients[e][s]*initial[s][i] for s in SPECIES) for i in range(N)] for e in DEPENDENT}
    constant={e:math.fsum(values)/N for e,values in z.items()}
    matrices={s:operator(rf,flux,{'H2':.001,'O2':.002,'H2O':.003}.get(s,.001) if unequal_diffusion else .001) for s in SPECIES}
    rhs={s:[rn[i]*initial[s][i]/DT+sources[s][i] for i in range(N)] for s in SPECIES}
    full={s:solve(matrices[s],rhs[s]) for s in SPECIES}
    independent=[s for s in SPECIES if s not in DEPENDENT.values()]
    reduced={s:solve(matrices[s],rhs[s]) for s in independent}
    for e,s in DEPENDENT.items():
        reduced[s]=[(constant[e]-math.fsum(coefficients[e][other]*reduced[other][i] for other in independent))/coefficients[e][s] for i in range(N)]
    def residual(state):
        return max(abs(a-b)/max(1.,abs(b)) for s in SPECIES for a,b in zip(multiply(matrices[s],state[s]),rhs[s]))
    deviation=max(abs(v-constant[e]) for e,values in z.items() for v in values)
    eligible=deviation<1e-12 and not unequal_diffusion
    return dict(variableElements=variable_elements,unequalDiffusion=unequal_diffusion,eligible=eligible,
                originalSolveCount=len(SPECIES),independentSolveCount=len(independent),
                maxInitialElementDeviation=deviation,
                maxSourceElementResidual=max(abs(math.fsum(coefficients[e][s]*sources[s][i] for s in SPECIES)) for e in DEPENDENT for i in range(N)),
                maxContinuityResidual=max(abs(rf[i]/DT+flux[i]-flux[(i-1)%N]-rn[i]/DT) for i in range(N)),
                fullEquationResidualRelative=residual(full),reconstructedEquationResidualRelative=residual(reduced),
                maxFieldDifference=max(abs(full[s][i]-reduced[s][i]) for s in SPECIES for i in range(N)),
                maxReconstructedSumYError=max(abs(math.fsum(reduced[s][i] for s in SPECIES)-1) for i in range(N)),
                maxElementFieldDifference=max(abs(math.fsum(coefficients[e][s]*(full[s][i]-reduced[s][i]) for s in SPECIES)) for e in DEPENDENT for i in range(N)),
                minReconstructedY=min(v for values in reduced.values() for v in values),full=full,reconstructed=reduced,
                decision='Equivalent inside declared common-operator/uniform-element class; known principle only.' if eligible else 'Reject constant-invariant reconstruction: precondition fails; full species transport is retained.')

def main():
    mechanism=STUDY/'data/raw/B_none_dt2e-06_s1_g0_o1_p1/chemkin/therm.dat'
    nasa=parse_nasa(mechanism)
    rows=[experiment(nasa),experiment(nasa,variable_elements=True),experiment(nasa,unequal_diffusion=True)]
    config=dict(scriptSHA256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
                thermoSHA256=hashlib.sha256(mechanism.read_bytes()).hexdigest(),thermoSource=str(mechanism.relative_to(ROOT)),
                nCells=N,dt=DT,volume=1.,uniformElementsThreshold=1e-12,
                scope='Frozen exact linear periodic FV system; no chemistry approximation, energy method, native run, timing or novelty claim.')
    result=dict(configuration=config,records=rows,noveltyStatus='REJECTED_AS_PRIOR_ART')
    raw=STUDY/'data/raw/ElementInvariant_analytic';raw.mkdir(exist_ok=True)
    (raw/'invariant_experiment.json').write_text(json.dumps(config,indent=2)+'\n')
    (raw/'invariant_result.json').write_text(json.dumps(result,indent=2)+'\n')
    (STUDY/'data/processed/element_invariant_screen.json').write_text(json.dumps(result,indent=2)+'\n')
    for r in rows:print({k:v for k,v in r.items() if k not in ['full','reconstructed']})
if __name__=='__main__':main()
