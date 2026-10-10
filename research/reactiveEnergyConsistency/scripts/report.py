"""Generate scientific figures and a results report from executed evidence only."""
from pathlib import Path
import json,math,gzip
from collections import Counter
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from analyze import TERMS,plot
ROOT=Path(__file__).resolve().parents[1]
LABELS={'Dpressure':'Pressure mismatch','Dkinetic':'Kinetic change',
 'DrhoH':'Density × sensible h','DrhoC':'Density × formation h',
 'DspeciesChemistry':'Species + chemistry','Dequation':'Energy equation residual',
 'Dtransport':'Net assembled transport','Dhistory':'History mismatch'}
COLORS=dict(zip(TERMS,['#b08a00','#8657ae','#227bb6','#c95147','#179278','#777777','#a86217','#bd74a4']))
def load(name):return json.loads((ROOT/'data/processed'/name).read_text())
def save(fig,name):
    fig.savefig(ROOT/'figures'/f'{name}.png',dpi=180)
    fig.savefig(ROOT/'figures'/f'{name}.pdf')
    plt.close(fig)
def table(headers,rows):
    return '\n'.join(['| '+' | '.join(headers)+' |','| '+' | '.join(['---']*len(headers))+' |']+
                     ['| '+' | '.join(map(str,r))+' |' for r in rows])
def main():
    summary=load('audit_summary.json');lookup={r['name']:r for r in summary}
    budgets=load('step_budgets.json');stages=load('stage_slices.json');gates=load('gates.json')
    exact=load('exact_wave.json');timing=load('timing_controls.json')
    with gzip.open(ROOT/'data/processed/solver_metrics.json.gz','rt') as f:metrics=json.load(f)
    base=lookup['F_dt2e-06_p1'];b=budgets[base['name']];t=np.array([r['time'] for r in b])*1e6
    cum={k:np.cumsum([r[k] for r in b])*1e3 for k in TERMS};measured=np.cumsum([r['DE'] for r in b])*1e3
    plt.rcParams.update({'font.size':10,'axes.spines.top':False,'axes.spines.right':False})
    plot(summary,budgets,stages)
    fig,axes=plt.subplots(2,2,figsize=(13,9),constrained_layout=True)
    ax=axes[0,0];positive=np.zeros(len(b));negative=positive.copy()
    for k in TERMS:
        values=cum[k];up=np.maximum(values,0);down=np.minimum(values,0)
        ax.fill_between(t,positive,positive+up,color=COLORS[k],alpha=.75,label=LABELS[k]);positive+=up
        ax.fill_between(t,negative,negative+down,color=COLORS[k],alpha=.75);negative+=down
    ax.plot(t,measured,color='black',lw=2,label='Measured sum');ax.axhline(0,color='black',lw=.6)
    ax.set(title='Signed cumulative budget: moving hydrogen',ylabel='Energy (mJ)',xlabel='Time (µs)')
    ax.legend(fontsize=7,ncol=2,loc='upper left')
    ax=axes[0,1];ax.plot(t,[r['DE']*1e3 for r in b],color='black',label='Measured')
    ax.plot(t,[(r['DrhoH']+r['DrhoC'])*1e3 for r in b],label='Density sensible + formation')
    ax.plot(t,[r['Dkinetic']*1e3 for r in b],label='Kinetic')
    ax.set(title='Per-step accounting',xlabel='Time (µs)',ylabel='Energy per step (mJ)');ax.legend(fontsize=8)
    ax=axes[1,0]
    for k in ['Dpressure','Dkinetic']:ax.plot(t,cum[k]*1e3,label=LABELS[k],color=COLORS[k])
    ax.set(title='Terms after the energy solve',xlabel='Time (µs)',ylabel='Cumulative energy (µJ)');ax.legend(fontsize=8)
    ax=axes[1,1]
    for k in ['DspeciesChemistry','Dequation','Dtransport','Dhistory']:
        ax.plot(t,cum[k]/1e3,label=LABELS[k],color=COLORS[k])
    ax.set_yscale('symlog',linthresh=1e-15)
    ax.set(title='Small terms retained in the identity',xlabel='Time (µs)',ylabel='Signed cumulative energy (J)');ax.legend(fontsize=8)
    for ax in axes.flat:ax.grid(alpha=.2)
    save(fig,'signed_budget')
    rs=sorted([r for r in summary if r['name'].startswith('F_dt')],key=lambda r:(r['nCorrectors'],r['dt']))
    fig,axes=plt.subplots(2,2,figsize=(12,8),constrained_layout=True)
    for pc in [1,4]:
        subset=[r for r in rs if r['nCorrectors']==pc]
        axes[0,0].loglog([r['dt']*1e6 for r in subset],[r['absoluteEnergyDrift'] for r in subset],'o-',label=f'{pc} pressure corrections')
    axes[0,0].set(xlabel='dt (µs)',ylabel='Absolute normalized endpoint drift',title='Timestep sweep, fixed 240 µs endpoint');axes[0,0].legend(fontsize=8)
    coarse=[lookup['F_dt2e-06_p1'],lookup['F_dt2e-06_p4']]
    axes[0,1].plot([r['nCorrectors'] for r in coarse],[r['signedEnergyDrift'] for r in coarse],'o-')
    axes[0,1].set(xlabel='Pressure correctors',ylabel='Signed normalized drift',title='Pressure sweep at dt = 2 µs');axes[0,1].set_xticks([1,4])
    axes[1,0].plot([1,2],[lookup['F_dt2.5e-07_p1']['signedEnergyDrift'],lookup['F_outer2_dt2.5e-7']['signedEnergyDrift']],'o-')
    axes[1,0].set(xlabel='Outer correctors',ylabel='Signed normalized drift',title='Outer sweep at dt = 0.25 µs');axes[1,0].set_xticks([1,2])
    vals=[base['signedEnergyDrift'],lookup['F_tol1e-8']['signedEnergyDrift']]
    axes[1,1].bar(['Default','1e−8'],[(v-base['signedEnergyDrift'])*1e6 for v in vals])
    axes[1,1].set(xlabel='Requested linear tolerance',ylabel='Change in normalized drift × 10⁶',title='Tighter tolerance: negligible effect at 2 µs')
    for ax in axes.flat:ax.grid(alpha=.2)
    save(fig,'coupling_sweeps')
    fig,axes=plt.subplots(1,2,figsize=(12,4.5),constrained_layout=True)
    for solver,label in [('reactingEnergyAudit','Pressure baseline'),('rhoCentralFoam','Density reference')]:
        er=sorted([r for r in exact['records'] if r['solver']==solver and r['dt']==2e-8],key=lambda r:r['nx'])
        axes[0].loglog([.02/r['nx'] for r in er],[r['errors']['T']['L1'] for r in er],'o-',label=label)
        axes[1].loglog([.02/r['nx'] for r in er],[abs(r['signedEnergyDrift']) for r in er],'o-',label=label)
    axes[0].set(xlabel='Grid spacing (m)',ylabel='Temperature L1 error (K)',title='Exact entropy wave, dt = 20 ns')
    axes[1].set(xlabel='Grid spacing (m)',ylabel='Absolute normalized energy drift',title='Conservation and field error are distinct')
    for ax in axes:ax.grid(alpha=.2);ax.legend(fontsize=8)
    save(fig,'exact_wave_convergence')
    fig,axes=plt.subplots(1,2,figsize=(12,4.5),constrained_layout=True)
    first=[r for r in stages[base['name']] if r['step']==1]
    first=sorted(first,key=lambda r:r['checkpoint'])
    axes[0].plot(range(len(first)),[(r['E']-first[0]['E'])*1e6 for r in first],'o-',color='black')
    axes[0].set_xticks(range(len(first)));axes[0].set_xticklabels([r['stage'].replace('_',' ') for r in first],rotation=65,ha='right',fontsize=7)
    axes[0].set(ylabel='Inventory change from step start (µJ)',title='First-step snapshots: bookkeeping, not defect attribution')
    axes[1].plot(t,[r['continuityL1'] for r in b]);axes[1].set_yscale('symlog',linthresh=1e-19)
    axes[1].set(xlabel='Time (µs)',ylabel='∫ |ddt rho + div phi| dV (kg/s)',title='Final continuity can close despite energy drift')
    for ax in axes:ax.grid(alpha=.2)
    save(fig,'stages_and_continuity')
    fig,ax=plt.subplots(figsize=(7,4.5),constrained_layout=True)
    for pc in [1,4]:
        group=[r for r in rs if r['nCorrectors']==pc]
        ax.loglog([r['solverWall'] for r in group],[r['absoluteEnergyDrift'] for r in group],'o-',label=f'{pc} pressure corrections')
        for r in group:ax.annotate(f"{r['dt']*1e6:g}",(r['solverWall'],r['absoluteEnergyDrift']),fontsize=7,xytext=(4,4),textcoords='offset points')
    for name,mark in [('F_outer2_dt2.5e-7','s'),('F_tol1e-8','D')]:
        r=lookup[name];ax.scatter(r['solverWall'],r['absoluteEnergyDrift'],marker=mark,label=name)
    ax.set(xlabel='Single process-wall trial, bound 4-rank MPI (s)',ylabel='Absolute normalized energy drift',title='Diagnostic cost/error map; labels are dt in µs')
    ax.grid(alpha=.2);ax.legend(fontsize=8);save(fig,'diagnostic_cost_error')
    # Portable phase/iteration summary; full residual records remain compressed.
    performance=[]
    for r in rs+[lookup['F_outer2_dt2.5e-7'],lookup['F_tol1e-8']]:
        m=metrics[r['name']];ph=m['phaseRankSums'];sums=Counter()
        for row in m['linearSolves']:sums[row['field']]+=row['iterations']
        performance.append(dict(name=r['name'],processWall=r['solverWall'],steps=r['steps'],
          meanProcessWallPerStep=r['solverWall']/r['steps'],maxPhaseRankSums={k:max(v[k] for v in ph.values()) for k in next(iter(ph.values()))} if ph else {},
          iterations=dict(sums),rankTimingInterpretation='Maximum of per-rank phase sums; these maxima need not be attained on the same rank. Linear iterations are solver-reported globally, not rank-summed.'))
    (ROOT/'data/processed/performance_summary.json').write_text(json.dumps(performance,indent=2)+'\n')
    slopes=[]
    fine=sorted([r for r in rs if r['nCorrectors']==4 and r['dt']<=1.25e-7],key=lambda r:r['dt'],reverse=True)
    for a,c in zip(fine,fine[1:]):slopes.append((a['dt']*1e6,c['dt']*1e6,math.log(a['absoluteEnergyDrift']/c['absoluteEnergyDrift'])/math.log(2)))
    max_closure=max(r.get('maxStepClosure',0) for r in summary)
    max_energy_check=max(abs(r['independentNativeEnergyDifference']) for r in summary)
    baseph=metrics[base['name']]['phaseRankSums'];phase_table=table(['Recorded phase','Maximum accumulated rank time (s)'],[(k,f"{max(v[k] for v in baseph.values()):.6f}") for k in next(iter(baseph.values()))])
    sweep_table=table(['dt (µs)','Pressure corrections','Signed drift','Absolute drift','Single wall time (s)'],[(f"{r['dt']*1e6:g}",r['nCorrectors'],f"{r['signedEnergyDrift']:+.9f}",f"{r['absoluteEnergyDrift']:.9f}",f"{r['solverWall']:.3f}") for r in sorted(rs,key=lambda r:(-r['dt'],r['nCorrectors']))])
    terms_table=table(['Term','Cumulative contribution (J)'],[(LABELS[k],f"{base['cumulativeTerms'][k]:+.12e}") for k in TERMS]+[('Measured endpoint change',f"{base['end']['E_stored']-base['initial']['E_stored']:+.12e}")])
    eq_table=table(['Control against baseline','T Linf (K)','p Linf (Pa)','h Linf (J/kg)'],[(name,f"{gates[name]['fieldNorms']['T']['Linf']:.6e}",f"{gates[name]['fieldNorms']['p']['Linf']:.6e}",f"{gates[name]['fieldNorms']['h']['Linf']:.6e}") for name in ['F_ledger_off','F_original','F_balanced','F_serial','F_restart']])
    exact_table=table(['Solver','Cells','dt (ns)','T L1 (K)','Signed energy drift'],[(r['solver'],r['nx'],f"{r['dt']*1e9:g}",f"{r['errors']['T']['L1']:.6f}",f"{r['signedEnergyDrift']:+.6e}") for r in exact['records']])
    simple_table=table(['Case','Signed normalized drift','Maximum step closure (J)'],[(r['name'],f"{r['signedEnergyDrift']:+.9e}",f"{r['maxStepClosure']:.3e}") for r in summary if r['name'].startswith(('A_','B_','C_','D_'))])
    testpath=ROOT/'data/processed/test_results.txt'
    test_status='See `data/processed/test_results.txt` for the executed automated checks.'
    report=f'''# Closed discrete total-energy audit: OpenCFD v2012

The first milestone is complete: the initialization-corrected moving hydrogen
case reproduces the published **−17.3886598%** energy drift, and an independently
assembled eight-term equation budget closes each step to floating-point roundoff.
In this case, the net density replacement applied after the enthalpy solve,
weighted by sensible and formation enthalpy, dominates the loss. Kinetic and
pressure-work mismatches alone do not account for it. **No conservative correction
has been accepted or implemented, and no publication-ready method claim is made.**

## Scope and provenance

Execution date: 2026-10-06. Installed fork: OpenCFD OpenFOAM-v2012 API 2012,
double precision / Int32 / GCC 6.3, WSL Ubuntu, Ryzen 5 5600X. Mesh for the
reacting regression: 32×8×1 cells, cyclic closed domain 0.02×0.008×0.001 m,
Euler stepping, sensible enthalpy, perfect-gas JANAF mixture, laminar transport.
The regression runs to 240 µs and uses four bound MPI ranks unless noted.
Chemistry, initial fields, discretization and initialization correction are
inherited from the executed prior baseline; only read-only diagnostics were added.

All **499 tracked published actionStudy files** remain byte-identical to their
frozen SHA256 manifest. The OpenFOAM installation and earlier research solver
were left intact. Source/version/compiler/executable hashes are in
`environment_manifest.json`, `source_manifest.json`, `current_source_manifest.json`
and `prior_art_source_manifest.json`. `instrumentation.patch` shows every change
to the copied baseline. Raw case dictionaries, fields, logs and failed runs are
retained in `../data/raw/`; processed results are portable and contain no assumed
or extrapolated experiments.

## Conserved quantity and independent verification

The conserved inventory in joules is

```
Ecal = Σ V [rho (hs + Σ Yi Hc_i + |U|²/2) − p].
```

JANAF Hc_i is absolute species enthalpy at Tstd=298.15 K. Qdot is chemical
conversion between sensible and formation energy, not an external source.
The initial energy is {base['initial']['E_stored']:.15g} J and final energy is
{base['end']['E_stored']:.15g} J; the loss is
{base['end']['E_stored']-base['initial']['E_stored']:.12g} J. Both signed and absolute
relative errors use |Ecal(0)|, which is finite and checked above 10⁻⁶ J.
This gauge-dependent normalization is accompanied by absolute joules throughout.

`thermo_reference.py` independently parses the raw CHEMKIN NASA7 coefficients,
reconstructs species absolute/sensible/formation enthalpy, EOS density and element
masses, and reads stored fields without calling OpenFOAM. It uses the actual
v2012 gas constant {8314.47006650545:.14g} J/(kmol K) and atomic weights; modern
constants would produce a false initialization mismatch. The maximum independent
versus native energy difference across completed audit cases is
{max_energy_check:.3e} J. For the main baseline, NASA reconstruction and the
stored-h inventory agree to displayed precision. Small thermodynamic inversion
errors are recorded separately in `audit_summary.json`.

## Equation-derived attribution

For Euler, the last outer-loop energy equation relative to the beginning of the
step gives the identity in `discrete_energy_derivation.md`. Each operator is
evaluated independently; no remainder is assigned as a physical defect.
The maximum per-step closure residual in the reacting baseline is
{base['maxStepClosure']:.3e} J, and the largest among all completed ledger cases is
{max_closure:.3e} J. The baseline cumulative closure residual is
{base['cumulativeClosure']:.3e} J. The sum of step inventory changes agrees with
the independent endpoint change within {abs(base['ledgerInventoryDifference']):.3e} J.

{terms_table}

The two density terms sum to
{base['cumulativeTerms']['DrhoH']+base['cumulativeTerms']['DrhoC']:+.12e} J.
The positive kinetic contribution partly offsets this loss. Removing only that
term from the frozen-state identity would increase the net loss; this arithmetic
is not a self-consistent corrected-solver experiment. Formation and sensible
density terms cancel substantially, so unsigned stacked bars are misleading.

![Signed cumulative and per-step budget](../figures/signed_budget.png)

The initial diagnostic incorrectly used the installed scalar-matrix `residual()`
helper with coupled boundaries. In this diagnostic path, coupled neighbour sources
were counted twice, producing large cancelling residual/transport values. The
final ledger evaluates diagonal, internal faces and boundary contributions exactly
once. Those rejected runs and `REJECTED.json` remain under
`data/raw/diagnosticResidualV1` and are excluded from all conclusions. This audit
does not modify that OpenFOAM helper or make a general claim about solver behavior.

## Stages and continuity

Snapshots record rho, EOS rho, sensible/formation/kinetic/pressure energy,
species masses, Qdot, dpdt and positivity around chemistry, species, energy,
thermo and each pressure/flux/velocity/density operation. The energy equation
uses the assembled density; subsequent pressure corrections and final
`rho=thermo.rho()` change its enthalpy-weighted integral. A zero global density
change cannot cancel a spatially varying enthalpy-weighted density change.
For this baseline, mass drift is {base['massDrift']:+.3e}; maximum recorded final
continuity L1 residual is {base['maxContinuityL1']:.3e} kg/s. The drift survives
those small residuals. Snapshot jumps are bookkeeping, not independent defect labels.

![First timestep stages and final continuity residual](../figures/stages_and_continuity.png)

Full rank-aggregated snapshots are in `stage_inventories.json.gz`; a first/last
step extract is in `stage_slices.json`. Per-step equation terms are in
`step_budgets.json`. The postprocessor preserves an execution-order checkpoint
index because `rho_thermo` occurs before and after each pressure correction;
repeated stage labels must not be summed together. The decomposition does not uniquely separate chemistry ODE
truncation, time truncation, splitting and species clipping. It explicitly
retains those identifiability limits.

## Timestep, pressure, outer and linear-tolerance sweeps

{sweep_table}

The coarse and intermediate reacting results are **nonmonotonic**. They do not
support a clean formal temporal-order claim. At four pressure correctors, the
last three dt values (0.125, 0.0625, 0.03125 µs) have energy-defect slopes
{slopes[0][2]:.4f} and {slopes[1][2]:.4f}. These are endpoint integral-defect
slopes at one coarse mesh, not the order of the coupled reacting field solution.
No reacting spatial convergence result is claimed.

At dt=0.25 µs, changing one to two outer correctors changes signed drift from
{lookup['F_dt2.5e-07_p1']['signedEnergyDrift']:+.9f} to
{lookup['F_outer2_dt2.5e-7']['signedEnergyDrift']:+.9f}. At dt=2 µs, two outer
correctors trigger a chemistry ODE floating-point failure; logs, partial ledgers
and `failure.json` are retained in `data/raw/F_outer2`. More outer iterations
are not a reliable cure in these controls. A requested linear tolerance of 10⁻⁸
changes signed drift to {lookup['F_tol1e-8']['signedEnergyDrift']:+.9f}, a change
of {lookup['F_tol1e-8']['signedEnergyDrift']-base['signedEnergyDrift']:+.3e}; the
original energy matrix residual is already too small to explain the finite loss.

![Coupling and tolerance sweeps](../figures/coupling_sweeps.png)

## Hierarchical controls and exact-solution verification

{simple_table}

A is static N2 and closes at machine precision. B is a homogeneous 1100 K
closed reacting system; halving dt reduces its small pressure-lag energy defect
approximately linearly, while source/formation conversion cancels to roundoff.
This is not independent kinetic trajectory validation. C is the original smooth
nonreacting advection control with laminar transport. D is a no-reaction H2/N2
composition gradient with unity diffusivity; its integral closure does not
establish local diffusion accuracy or differential-diffusion consistency.

An additional nonreacting exact Euler entropy wave sets constant pressure,
constant velocity 40 m/s, rho=rhobar[1+0.05 sin(2π(x−Ut)/L)], constant Cp=1000
J/(kg K), pure N2 and zero viscosity/conduction. The density-based rhoCentralFoam
reference has matched EOS, energy gauge, mesh and dt. Its Kurganov convective
flux differs from the pressure-based flux: each is compared to the analytic
solution, and their difference is not labelled pure coupling error.

{exact_table}

Pressure-baseline spatial T L1 orders are
{exact['spatialOrders'][0]['T_L1_order']:.4f} and
{exact['spatialOrders'][1]['T_L1_order']:.4f} across 32/64/128 cells at dt=20 ns.
The fixed-grid T self-differences at dt=200/100/50 ns give an observed temporal
self-convergence order of {exact['temporalSelfOrderT_L1']:.4f}. This is an
unforced exact nonreacting subset, not a general reacting MMS. Fixed-grid total
field error has a spatial floor. The conservative reference has energy drift
near 10⁻¹⁴ but larger T error due to its flux dissipation. Integral conservation
alone does not establish local accuracy or universal solver superiority.

![Exact wave grid convergence and conservation](../figures/exact_wave_convergence.png)

E controlled reaction–diffusion and G resolved canonical reacting validation
have not been executed. Cantera is absent in the inspected environments; a
matched independent 0D kinetic reference remains required. These limitations
prevent method acceptance or a publication-standard reacting result.

## State preservation and executable tests

{eq_table}

Ledger on/off, the earlier unchanged initialization-corrected executable, and
native versus chemistry-balanced execution give exactly identical final fields
for T,p,rho,h,U and every species. Serial/MPI and split-restart differences are
within the recorded tight tolerances. These are baseline/instrumentation checks,
not correction on/off tests. Completed audit cases pass mass, elements, species
normalization and positivity gates. The raw minima and relative element errors
are recorded in `audit_summary.json`; zero initial element denominators are excluded.

{test_status} The tests require actual run evidence for the frozen artifact,
independent energy calculation, per-step closure, static precision, mass/elements/
species positivity, on/off and original-solver field equivalence, restart, serial/
MPI, chemistry ownership, documented drift, small transport/residual terms,
and the analytic/density-reference checks. Correction acceptance tests are
intentionally absent because no correction exists.

## Performance evidence and limits

The following baseline values are the maximum accumulated per-rank phase timers.
Each includes the entire named phase and may contain instrumentation and communication;
it is not an isolated matrix-solve time. Maxima can come from different ranks
and these rank maxima must not be added as a timestep critical-path estimate.

{phase_table}

`solver_metrics.json.gz` records reported linear residuals/iterations;
`performance_summary.json` contains compact iteration and maximum-rank phase
summaries. Baseline sweep process-wall times are single diagnostic trials.

![Diagnostic baseline cost versus energy error](../figures/diagnostic_cost_error.png)

Only instrumentation overhead was measured with repetition: two warmups,
randomized on/off order (seed 20261006), four MPI ranks bound to cores, three
full 120-step trials per setting, with no competing experiment during timing.
Ledger off: median {timing['statistics']['False']['median']:.4f} s,
mean {timing['statistics']['False']['mean']:.4f} s,
sample SD {timing['statistics']['False']['std']:.4f} s.
Ledger on: median {timing['statistics']['True']['median']:.4f} s,
mean {timing['statistics']['True']['mean']:.4f} s,
sample SD {timing['statistics']['True']['std']:.4f} s.
The median difference is {100*timing['medianAuditOverhead']:.2f}%, below observed
timing scatter; this does not establish a precise overhead bound. Startup and
endpoint I/O are included. No bootstrap interval is justified with n=3.
Memory overhead, MPI operation counts, isolated solve timing, corrected-method
Pareto improvement and strong scaling remain unmeasured. No no-communication
or large-cluster performance claim is made.

## Hypotheses, novelty gate and next admissible method work

| Hypothesis | Status from the executed audit |
| --- | --- |
| H1: kinetic/pressure mismatch dominates the moving regression | Rejected for the measured cumulative defect at the reproduced setting; density-weighted sensible/formation mismatch dominates. Other benchmarks can have different dominant terms. |
| H2: measurable predictor/corrected terms account for defect | Supported as an independently assembled algebraic budget, without unique attribution of all truncation mechanisms. |
| H3: a correction increases the asymptotic energy-defect order | Untested; no accepted correction equation. |
| H4: a correction beats another outer loop on cost/accuracy | Untested; extra outer loops are negative controls here, not proof of a new method. |
| H5: method conservation is chemistry-ownership independent | Baseline field equivalence verified; method-level statement untested. |

The primary literature/source audit establishes conservative pressure-based
compressible formulations and reactive sensible-enthalpy energy corrections as
prior art, notably [Grapsas et al.](https://arxiv.org/abs/2010.07577).
The authors' CTreactingFoam source was inspected at pinned commit
0754a9cea2482fff0f6fa6630778f65042f47536; it adds species diffusive enthalpy and
retains explicit K/pressure terms and energy-before-pressure coupling.
The SCI abstract establishes splitting improvements, but its exact full-text
energy modification and authoritative source could not be verified. That open
comparison prevents a new-method novelty claim. All search limits are stated
in `novelty_search.md`, `related_work.md` and `claim_ledger.md`.

`method_derivation.md` derives why changing hs alone at fixed rho,p,Y violates
the EOS, and why a heuristic hs×final-continuity-residual source does not follow
from this conservative baseline. This is a limited constraint on a frozen final
state, not a proof that all inexpensive corrections are impossible. A smallest
pressure/enthalpy/formation-energy correction must still be derived with common
species and energy fluxes, continuity, EOS, positivity and momentum consistency.
No post-hoc scalar energy normalization, solver reordering or unverified source
has been introduced. Milestones two and three remain unestablished.

## Reproduction

Run from the repository root in the existing WSL/OpenFOAM environment:

```bash
python3 research/reactiveEnergyConsistency/scripts/prepare.py
bash research/reactiveEnergyConsistency/scripts/build.sh
bash research/reactiveEnergyConsistency/scripts/run.sh campaign.py
bash research/reactiveEnergyConsistency/scripts/run.sh followup.py
bash research/reactiveEnergyConsistency/scripts/run.sh exact_wave.py
bash research/reactiveEnergyConsistency/scripts/run.sh analyze.py
bash research/reactiveEnergyConsistency/scripts/run.sh log_metrics.py
bash research/reactiveEnergyConsistency/scripts/test.sh
bash research/reactiveEnergyConsistency/scripts/report.sh
bash research/reactiveEnergyConsistency/scripts/run.sh provenance.py
```

`timing_controls.py` reruns warmups and recorded randomized timing controls only
when their run names are absent. Existing cases are never overwritten; failed
controls are retained and reported. `current_sources.py` and `prior_art_sources.py`
retrieve/pin official/author source snapshots, independently of case execution.
The local compiler adapter and existing chemistry libraries are read-only
dependencies recorded in the build/environment manifests. `evidence_manifest.json`
hashes the portable source, scripts, figures, processed data and raw case inputs.
Reporting uses the
existing plotting runtime without installing or altering dependencies.
'''
    (ROOT/'docs/audit_results.md').write_text(report)
    print('Report and six scientific figure sets generated from executed records.',flush=True)
if __name__=='__main__':main()
