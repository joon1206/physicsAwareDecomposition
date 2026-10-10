"""Generate tables, scientific report and executive package from measured data."""
import collections,csv,json,math,random,statistics
from pathlib import Path
from analysis import ROOT,TRAIN,VALID,TEST,ACTIONS,summary,interval

def read(name):return json.loads((ROOT/f'data/processed/{name}.json').read_text())
def fmt(v):return f'{v:.3f}'
def table(headers,rows):return '\n'.join(['| '+' | '.join(headers)+' |','|'+'|'.join(['---']*len(headers))+'|']+['| '+' | '.join(map(str,r))+' |' for r in rows])
def aggregate(rows,policies,baseline='A0',only=TEST):
    regimes=[r for r in only if any(x['regime']==r for x in rows)]
    groups={(c,p):[r['totalWall'] for r in rows if r['regime']==c and r['policy']==p] for c in regimes for p in policies}
    result={};rng=random.Random(403194)
    for p in policies:
        speed=sum(statistics.median(groups[c,baseline]) for c in regimes)/sum(statistics.median(groups[c,p]) for c in regimes)
        ratios=[]
        for _ in range(4000):
            numerator=denominator=0.
            for c in regimes:
                x,y=groups[c,baseline],groups[c,p]
                numerator+=statistics.median(rng.choices(x,k=len(x)));denominator+=statistics.median(rng.choices(y,k=len(y)))
            ratios.append(numerator/denominator)
        eligible=all(r.get('gate',{'pass_':True})['pass_'] for r in rows if r['regime'] in regimes and r['policy']==p)
        ratios.sort();result[p]=dict(speedup=speed,CI=[1.,1.] if p==baseline else [ratios[100],ratios[3900]],conditions=regimes,valid=eligible,
            ratioInterpretation='claim-eligible within the disclosed physical limits' if eligible else 'descriptive timing ratio only; a predefined numerical gate failed; every original timing retained',
            timingScope='sum of condition median end-to-end wall; uncertainty resamples runs within each fixed condition, not a population of flows')
    return result

def main():
    states=read('oracle_summary');raw=read('oracle_raw');policies=read('policy_summary');model=read('model')
    live=read('live');deployed=read('deployment_summary');gates=read('oracle_validation');fine=read('fine_oracle_summary')
    inventories=read('inventories');consequences=read('consequence_models');hist=read('histories')
    diagnosis=read('conservation_diagnosis')+read('conservation_coupling_followup');continuous_gates=read('continuous_oracle_validation')
    literature_count=len(json.loads((ROOT/'docs/literature.json').read_text()))
    physical=read('physical_field_audit')
    flux_repair=read('flux_repair')
    corrected=flux_repair['observedZeroRepairs']
    preservation=flux_repair['records']
    flux_note=f"The surface audit finds eight exactly zero processorCyclic flux copies in the rejected third migration, while the paired periodic copies are nonzero. No sign reversal is observed. A separate axis-aligned, stationary-mesh utility snapshots physical face identity outside the native mapper. All three fixed observed ownership maps pass preservation and endpoint gates; ordinary manual mapping also passes, so ownership alone does not reproduce the original failure. Independently, filling the exact-zero coupled copies from their existing nonzero partners in copies of the original post-migration states reduces the worst endpoint temperature difference to {max(r['gate']['fields']['T']['Linf'] for r in corrected):.6g} K; all three corrected controls pass. These controls isolate the surface-state loss without using reference fields to repair it. Preparation and restoration each launch MPI and are charged in their manifests (median combined preservation cost {statistics.median(r['prepareWall']+r['restoreWall'] for r in preservation if r['preserveFlux']):.3f} s). The helper uses O(global faces) storage per rank and supports axis-aligned stationary geometry with translational x-periodicity only. It is a correctness reference, not a scalable generic mapper. The first rejected unoriented-field approach is preserved locally; the delivered implementation bypasses that mapper. Original live timings, their failed gate, and mesh-policy ineligibility remain unchanged.\n\n![Flux preservation and repair controls](../figures/49_flux_preservation_controls.png)"
    initial_note=''
    long_initialization=read('initial_state_long')['records']
    long_note='The same initialization-only executable is tested over the full 240 μs moving history. '+ '; '.join(f"dt={r['dt']*1e6:g} μs with {r['nCorrectors']} pressure corrector(s): mass drift {r['relativeMassDrift']*100:.6g}%, signed energy drift {r['relativeEnergyDrift']*100:.4f}%" for r in long_initialization)+'. The mass correction persists; residual energy error is a separate coupled-discretization limitation. No original timing or field-gate eligibility is replaced.\n\n![Full-history initialization controls](../figures/51_full_history_initialization.png)'
    if (ROOT/'data/processed/initial_state_diagnosis.json').exists():
        initialization=read('initial_state_diagnosis')
        native_offset=max(abs(s['relativeMassDrift']) for r in initialization['records'] if r['variant']=='nativeInitialization' for s in r['inventories'])
        fixed_offset=max(abs(s['relativeMassDrift']) for r in initialization['records'] if r['variant']=='initialPsiPreserved' for s in r['inventories'])
        initial_note=f"A separate two-step diagnostic identifies an initial-coefficient mass offset: original initialization reaches {100*native_offset:.6g}% drift, while preallocating initial psi.oldTime before the first thermo update gives at most {100*fixed_offset:.6g}%. The diagnostic executable changes this initialization condition only and is excluded from the frozen performance dataset. Long-time energy and spatial convergence remain separate.\n\n![Initial-coefficient mass diagnosis](../figures/48_initial_coefficient_mass.png)"
    confirmation=read('confirmation');negative_confirmation=read('confirmation_negative')
    lp=['nativeContinuous','continuous','ACContinuous','A0','AC','AM','imbalanceThreshold','persistenceBreakEven','controller']
    live_summary=[]
    for c in sorted(set(r['regime'] for r in live)):
        for p in lp:
            rr=[r for r in live if r['regime']==c and r['policy']==p];base=[r['totalWall'] for r in live if r['regime']==c and r['policy']=='nativeContinuous']
            tt=[r['totalWall'] for r in rr]
            live_summary.append(dict(regime=c,policy=p,stats=summary(tt),speedup=statistics.median(base)/statistics.median(tt),
                CI=[1,1] if p=='nativeContinuous' else interval(base,tt),valid=all(r.get('gate',{'pass_':True})['pass_'] for r in rr)))
    live_agg=aggregate(live,lp,baseline='nativeContinuous')
    (ROOT/'data/processed/live_summary.json').write_text(json.dumps(live_summary,indent=2))
    (ROOT/'data/processed/live_aggregate.json').write_text(json.dumps(live_agg,indent=2))
    candidates=[(s,a) for s in states for a in ACTIONS[1:] if s['actions'][a]['valid']]
    best,a=max(candidates,key=lambda p:p[0]['actions'][p[1]]['speedup']);b=best['actions'][a]
    mass=max(abs(r['relativeMassDrift']) for r in inventories);energy=max(abs(r['relativeEnergyDrift']) for r in inventories)
    maximumT=max(g['fields']['T']['Linf'] for g in gates);failed=sum(not g['pass_'] for g in gates)
    failed_live=[r for r in live if not r.get('gate',{'pass_':True})['pass_']]
    live_failure_note=(f"The rejected live trial(s) are {', '.join(r['path'] for r in failed_live)}. They remain in their timing distributions; affected policy aggregates are numerically ineligible and cannot support speedup claims. Historical ownership-map diagnostics and fixed-partition replay, finer-global-step and tighter-ODE controls are retained in live_mesh_diagnosis.json and live_mesh_followup.json. The predefined tolerances and original trials are unchanged." if failed_live else 'All original live endpoint comparisons pass; fixed field thresholds remain unchanged.')
    winner_counts=dict(collections.Counter(s['winner'] for s in states))
    acquisition=sum(r['totalWall'] for r in raw if r['regime'] in TRAIN+VALID)
    headroom=policies['test']['oracle']['aggregateSpeedup']/policies['test']['periodicChemistry']['aggregateSpeedup']
    headline=dict(best=dict(regime=best['regime'],checkpoint=best['checkpoint'],H=best['H'],action=a,speedup=b['speedup'],CI=b['speedupCI'],
        baselineMedian=best['actions']['A0']['total']['median'],actionMedian=b['total']['median'],context='one six-core Ryzen 5600X WSL2 host; four bound MPI ranks; 256 cells; OpenCFD v2012; global dt 2e-6 s; five trials; complete forced-endpoint restart continuation costs; exploratory selection'),
        oracleStates=len(states),oracleTrials=len(raw),winners=winner_counts,heldoutReplay=policies['test'],liveHeldout=live_agg,
        oracleHeadroomAboveAlwaysChemistry=headroom,numerics=dict(gates=len(gates),failed=failed,maxTemperatureDifference=maximumT,
            maximumMassBudgetDrift=mass,maximumEnergyBudgetDrift=energy,liveGates=sum('gate' in r for r in live),failedLiveGates=len(failed_live),failedLiveTrials=[r['path'] for r in failed_live]),trainingValidationAcquisitionLowerBound=acquisition,modelFitWall=model['trainingWall'])
    headline['independentConfirmation']={k:confirmation[k] for k in ['regime','checkpoint','H','baseline','method','speedup','CI','selection']}
    headline['negativeConfirmation']={k:negative_confirmation[k] for k in ['regime','speedup','CI']}
    (ROOT/'data/processed/headline.json').write_text(json.dumps(headline,indent=2))
    tables=ROOT/'tables';tables.mkdir(exist_ok=True)
    oracle_rows=[]
    for s in states:
        for act in ACTIONS:
            q=s['actions'][act];stats=q['total']
            oracle_rows.append(dict(regime=s['regime'],checkpoint=s['checkpoint'],H=s['H'],split=s['split'],action=act,winner=s['winner'],
                **stats,speedup=q['speedup'],usePhaseSolverSpeedup=s['actions']['A0']['solver']['median']/q['solver']['median'],CI_low=q['speedupCI'][0],CI_high=q['speedupCI'][1],valid=q['valid'],setup=q['setup'],faces=q['processorFaces']))
    for name,rows in [('oracle',oracle_rows),('live',live_summary),('deployment',deployed),('fine_oracle',fine)]:
        with (tables/(name+'.csv')).open('w',newline='') as f:
            writer=csv.DictWriter(f,fieldnames=list(rows[0]),lineterminator='\n');writer.writeheader()
            for row in rows:writer.writerow({k:json.dumps(v) if isinstance(v,(dict,list)) else v for k,v in row.items()})
    oracle_table=table(['Condition','Checkpoint (μs)','H','Winner','AC speedup [95% CI]','AM speedup','AH speedup'],
        [[s['regime'],f"{float(s['checkpoint'])*1e6:g}",s['H'],s['winner'],f"{s['actions']['AC']['speedup']:.3f} [{s['actions']['AC']['speedupCI'][0]:.3f}, {s['actions']['AC']['speedupCI'][1]:.3f}]",fmt(s['actions']['AM']['speedup']),fmt(s['actions']['AH']['speedup'])] for s in states])
    policy_table=table(['Held-out replay policy','Aggregate speedup [conditional 95% CI]','Mean regret (s)','Worst regret (s)','Oracle-optimal fraction'],
        [[p,f"{policies['test'][p]['aggregateSpeedup']:.3f} [{policies['test'][p]['aggregateSpeedupCI'][0]:.3f}, {policies['test'][p]['aggregateSpeedupCI'][1]:.3f}]",fmt(policies['test'][p]['meanRegret']),fmt(policies['test'][p]['worstRegret']),fmt(policies['test'][p]['oracleOptimalFraction'])] for p in ['never','imbalanceThreshold','periodicChemistry','periodicMesh','stuttgartEveryStep','persistenceBreakEven','wholeSolver','oracle']])
    live_table=table(['Executed policy','Held-out end-to-end runtime ratio','95% within-condition bootstrap interval','Numerically eligible'],
        [[p,fmt(live_agg[p]['speedup']),f"[{live_agg[p]['CI'][0]:.3f}, {live_agg[p]['CI'][1]:.3f}]",live_agg[p]['valid']] for p in lp])
    abl=table(['Ablation','Held-out speedup','Mean regret (s)'],[[p.removeprefix('ablation_'),fmt(v['aggregateSpeedup']),fmt(v['meanRegret'])] for p,v in policies['test'].items() if p.startswith('ablation_')])
    scaling=read('scaling');scale_table=[]
    for p in [1,2,4,6]:
        for act in ['A0','AC','controller']:
            group=[r['totalWall'] for r in scaling if r['ranks']==p and r['action']==act];one=[r['totalWall'] for r in scaling if r['ranks']==1 and r['action']==act]
            med=statistics.median(group);speed=statistics.median(one)/med
            scale_table.append([p,act,fmt(med),fmt(speed),fmt(speed/p)])
    scale_table=table(['Ranks','Policy','Median action + solver wall (s)','Strong-scaling speedup','Efficiency'],scale_table)
    fine_table=table(['Condition','Action','Median total wall (s)','A0/action','95% CI','Field gate'],
        [[r['regime'],r['action'],fmt(r['stats']['median']),fmt(r['speedup']),f"[{r['speedupCI'][0]:.3f}, {r['speedupCI'][1]:.3f}]",r['valid']] for r in fine])
    diagnosis_table=table(['Grid','dt (μs)','Pressure correctors','Outer correctors','Mass drift (%)','Initial E (J)','Final E (J)','ΔE (J)','ΔE / |E₀| (%)','Maximum T (K)'],
        [[f"{r['nx']}×{r['ny']}",f"{r['dt']*1e6:g}",r['nCorrectors'],r['nOuterCorrectors'],f"{r['relativeMassDrift']*100:.5f}",
          f"{r['initial']['totalEnergy']:.6g}",f"{r['end']['totalEnergy']:.6g}",
          f"{r['end']['totalEnergy']-r['initial']['totalEnergy']:.6g}",f"{r['relativeEnergyDrift']*100:.4f}",f"{r['Tmax']:.2f}"] for r in diagnosis])
    prior=read('previous_claim_audit');confirmation=read('confirmation');negative_confirmation=read('confirmation_negative')
    report=f'''# Choosing load-balancing actions for reactive OpenFOAM: a measured oracle and a constrained controller

## Abstract

We compare unchanged ownership (A0), chemistry-task redistribution (AC), cost-weighted mesh redistribution (AM), and their hybrid (AH) using identical reacting-flow checkpoints, a compatible upstream chemistry baseline, and total future process cost. The corrected study contains {len(states)} states and {len(raw)} randomized continuations, five trials per action. Median oracle winners are {winner_counts}. The largest observed action speedup is {b['speedup']:.3f}×, pointwise 95% bootstrap interval [{b['speedupCI'][0]:.3f}, {b['speedupCI'][1]:.3f}], at {best['regime']}, checkpoint {float(best['checkpoint'])*1e6:g} μs, H={best['H']}; this is an exploratory maximum, not a universal or confirmatory claim. The held-out retrospective whole-cost selector achieves {policies['test']['wholeSolver']['aggregateSpeedup']:.3f}× versus {policies['test']['periodicChemistry']['aggregateSpeedup']:.3f}× for the executed chemistry algorithm's always-enabled action. Actual held-out live controller speedup relative to uninterrupted native standard chemistry is {live_agg['controller']['speedup']:.3f}× [{live_agg['controller']['CI'][0]:.3f}, {live_agg['controller']['CI'][1]:.3f}]. Algorithmic field equivalence and physical accuracy are assessed separately. Coarse transient budgets and refinement results restrict physical interpretation. The contribution is a reproducible local action-oracle and negative/conditional tradeoff evidence; it does not establish a new partitioner, a new adaptive-balancing principle, or a generally superior controller.

## Introduction and motivation

Detailed chemistry has heterogeneous cell integration cost, while mesh ownership also determines transport, pressure, halos and locality. A more balanced chemistry phase can therefore yield a slower full simulation. Task offloading changes where independent ODEs execute while retaining finite-volume ownership; mesh redistribution changes every mesh-associated phase. Measuring these alternatives together is necessary before investing in a sophisticated selector.

## Research questions

The study asks which action minimizes J(a,H)=Cdecision+Cmigration+future solver wall, when an apparent gain survives setup costs and numerical gates, whether past-only workload features predict that action on unseen operating conditions, and whether actual controller overhead leaves usable oracle headroom. It also asks what the available single-node hardware can and cannot establish about scaling and novelty. The fifteen requested questions are answered explicitly in [answers.md](answers.md).

## Related work

The literature ledger contains {literature_count} entries across chemistry scheduling, graph repartitioning, runtime systems, GPU chemistry and solver selection. [Gärtner et al.](https://doi.org/10.1016/j.cpc.2024.109322) supplies the directly executed standard chemistry baseline; its paper's chemistry-phase speedups exclude PDE/auxiliary cost. [DLBFoam](https://doi.org/10.1016/j.cpc.2021.108073) separates task balancing from reference-cell filtering. [Cuoci's workshop material](https://zenodo.org/records/18670150) already describes adaptive migration-aware chemistry scheduling. [van den Oord et al.](https://doi.org/10.1177/10943420251329199) discusses persistence and independent chemistry/EoS redistribution. [DRAMA](https://chriswalshaw.co.uk/papers/fulltext/BasermannApMM00.pdf) already models costs across application phases. Proactive prediction, separate ODE maps, and weighted native mesh balancing also have established implementations. See [claim_verification.md](claim_verification.md), [related_work_comparison.md](related_work_comparison.md), and [novelty_search.md](novelty_search.md) for primary evidence, scope and unresolved access failures.

## OpenFOAM architecture

reactingFoamPAD retains the v2012 finite-volume equations and adds rank-local phase clocks. costOde follows the standard ODE cell loop and records cell integration clocks and substeps. Additional h-to-T corrections are opt-in and set to two for every action in these detailed-chemistry cases; this is a common numerical setting, not an unnoticed baseline change. The controller is an external Python process orchestrator. AC executes inside the chemistry library. AM runs native redistributePar between solver processes, so its wall includes process startup, field I/O and redistribution. It is not an in-solver adaptive mesh implementation.

![Architecture](../figures/33_architecture.png)

## Baseline implementations

Stuttgart source is pinned to c67d87052ec29375c5d3580888aa65a64917024b. The private standard-only v2012 port retains rank pairing, previous-cell-cost ordering, the 2% cell-transfer threshold, microsecond upstream clocks, nonblocking exchanges, and every-step update. It registers psiReactionThermo/gasHThermoPhysics with EulerImplicit and ode; TDAC is excluded. API adaptations, passive chemCost/chemDeltaT fields and license are retained in [stuttgart_v2012.patch](stuttgart_v2012.patch). Native standard ode, costOde and the compatible task algorithm pass their initial field regression. This comparison uses the same OpenFOAM, integrator, tolerances, mesh and compiler rather than conflating versions or Jacobian/filtering acceleration.

The public QUICKLB 0.02 library is additionally compiled with GNU Fortran in an isolated MPI/Python environment and run on a small Gray–Scott kernel. This is third-party library reproduction, not reproduction of the INCA Spray-A paper or a direct CFD speedup comparison. The full public INCA dataset is about 20.1 GB and the matching INCA executable is unavailable.

## Existing and synthetic experiments

The earlier project remains in the parent directory with its original synthetic workload study, weighted Scotch implementation, thirty figures and report. Its persistent LTS result was reconstructed from raw five-trial manifests: 2.01698/1.74009=1.15912× solver-only, excluding training/decomposition. The exploratory interval is [1.03009,1.22309]. The short global-step experiment did not establish a gain. These are reference evidence, not the headline for the new transient study. Synthetic imbalances isolate scheduling behavior but do not substitute for reactive physics or validate flame propagation.

## Reactive-flow test cases

The main oracle uses a closed periodic 20×8×1 mm domain, 32×8×1 cells, laminar flow, globally fixed Euler dt=2 μs, first-order upwind convection, strict linear tolerance 1e-14 and zero relTol. Chemistry uses Rosenbrock34, absTol=1e-12, relTol=1e-5, initial chemical step 1e-7 s and Treact=500 K. H2 chemistry has ten species and 27 reactions. GRI has 53 species and 325 reactions but is also driven by H2 premix; carbon chemistry is inactive. It is a mechanism-size experiment, not an unseen-mechanism generalization test.

Persistent, translating, ignition, decay, uniform, chemistryDominated and transportDominated are hypotheses describing initial conditions. Three additional held-out conditions change velocity, temperature or width. Measured temperature, heat-release and cell-clock histories determine which intended behavior actually develops. These coarse kernels solve reactive-flow equations but are not resolved flames or validated burner models. TransportDominated is a cold inactive-chemistry control; its importance is limited headroom and overhead, not an established expensive turbulent transport regime.

## Workload characterization and persistence

We measure chemistry fraction, current and previous rank imbalance, cell-cost CV, circular center of cost and observed displacement, expensive-region Jaccard overlap, and past-cost correlation. The bounded lifetime estimate −lag/log(ρ), capped at 1000 steps, is an empirical feature rather than a fitted physical lifetime law. EMA means a two-snapshot 0.5 blend. Future trace values are used only in diagnostic correlation-versus-lag figures; they are excluded from model inputs and from live controller memory.

![Persistence](../figures/16_persistence_correlation.png)

## Oracle action experiment

Each candidate copies the same mesh/field checkpoint and chemistry timestep history; duplication for an experiment is excluded, while weight acquisition/construction, configuration, native migration and solver process wall are charged. The mesh weight reader currently performs the whole extraction pass, including additional diagnostic features; this is actual measured implementation overhead, not a minimal in-solver weight-reader estimate. Early manifests' independently measured acquisition clocks are charged exactly once by the collector. No estimated duration or trial removal is used.

An inherited global timeIndex formerly caused periodic writes before the actual end; affected runs remain under interiorWriteProtocol and are excluded. A second epoch used native restart initialization and passed same-action gates, but did not preserve static dpdt and the previous psi coefficient: segmented/native comparisons differed by up to 68.4 K. That epoch remains under nativeRestartProtocolV2 and is also excluded from final claims. The final protocol forces physical endpoints, stores solved h/rho/dpdt and initializes psi.oldTime before its first thermodynamic update at a restart. Continuous and segmented standard chemistry now match to approximately 1e-9 K in the restart regression. The full oracle and dependent experiments are regenerated under that protocol. Every rank's exact step count, unique times and endpoint are asserted; a seven-step continuation from inherited index twenty directly exercises output semantics.

{oracle_table}

The oracle label is the minimum of repeated action medians subject to field validity. Small best–second margins can be noise. The complete four-action sweep and all trials are retained; no outliers are removed. The held-out hindsight oracle offers only {100*(headroom-1):.2f}% additional aggregate speedup over always enabling AC in this dataset. This is optimistic headroom, because it chooses among noisy observed medians.

An independent preselected replication uses twenty trials per action for the moving positive condition and uniform negative condition, without refitting the model. Moving AC/A0 speedup is {confirmation['speedup']:.3f}× [{confirmation['CI'][0]:.3f}, {confirmation['CI'][1]:.3f}], medians {confirmation['baseline']['median']:.4f}/{confirmation['method']['median']:.4f} s. Uniform AC/A0 is {negative_confirmation['speedup']:.3f}× [{negative_confirmation['CI'][0]:.3f}, {negative_confirmation['CI'][1]:.3f}]. Both use four ranks, 256 cells, checkpoint 40 μs and H=80 global 2 μs steps, including action and whole continuation process cost. These confirm the chosen conditions, not the exploratory maximum or all possible flows.

## Predictive model and performance objective

The interpretable ridge model predicts each action's solver delta using chemistry work over H, imbalance-derived excess, persistence-adjusted excess, transport/pressure duration, and processor faces per cell. It adds training-set median action costs, a conservative 90th-percentile absolute residual margin from training plus whole validation cases, and a minimum gain margin max(0.02 s, 2.5% of estimated future timestep work). The residual margin is not a probabilistically calibrated confidence interval. A0 has zero incremental score. Ownership/scheduler changes have a forty-step cooldown.

A separate explanatory transport model uses observed post-partition face ratio, cell-count CV, chemistry fraction and mechanism size to predict rank-mean cumulative transport/pressure change. Held-out MAE is {consequences['metrics']['test']['MAE']:.5f} s per step. This quantity includes waits and is not pure network cost. Post-partition features require candidate partition work; the model is not deployed as a free online prediction. The initial face feature in the main controller is constant in same-grid states, so communication consequences are not independently identified by that coefficient.

An additional explanatory MPI-call-duration model uses the two profiled training conditions and twenty-four new on/off trials in heldoutMoving. Six held-out AM/AH profiled runs give MAE {consequences['MPIModel']['metrics']['test']['MAE']:.5f} s per step. This model uses observed partition geometry, neighbor count, chemistry fraction and the hybrid-task indicator. It predicts time inside MPI, including synchronization and scheduling, rather than an isolated network-transfer penalty. Two training conditions and one test condition do not establish broad predictive generalization.

## Runtime controller and cost accounting

Independent checkpoint deployment runs A0, AC, AM and the frozen controller, five repeats at two checkpoints in each held-out condition. Feature extraction is charged to prediction/threshold policies and to mesh weights; inference is charged where used. Live runs use a genuinely measured twenty-step prefix followed by three forty-step segments. The state-preserving executable restores solved h and dpdt and preallocates psi.oldTime before its first restart update. All live policies reach 280 μs and include preprocessing, decomposition, prefix, every startup, write, decision and migration. Nine executed arms include uninterrupted native, instrumented standard and Stuttgart chemistry; segmented A0/AC/AM; and the three adaptive policies. Build costs are offline. Model acquisition is separate from per-case use, rather than hidden as free training.

Native v2012 repeated redistribution exposed a physical-patch synchronization check that failed to exclude processorCyclic patches. A private redistributeParPAD utility changes that check and its executable target only; the installed utility and partition/redistribution algorithm are preserved. Live mesh arms use the private utility and pay its measured process cost. First-migration fields match the native utility, three successive migrations preserve their instantaneous state, and the final trajectory matches uninterrupted native chemistry. The source patch and failed AM live runs are retained. Single-migration oracle, profile and scaling experiments use the installed utility.

Every completed live segment retains its rank clocks and solver log before the next process starts; migration checkpoints retain ownership maps. One completion attempt overlapped the one-time evidence archive and lost its case path during endpoint validation. That stopped attempt is preserved under liveRetentionRace. The complete randomized live collection was rerun with finalized retention code, with the same jobs, seed, repetitions, frozen model and numerical settings. Partial/rejected attempts never supply final performance summaries.

The measured train/validation oracle acquisition alone costs at least {acquisition:.1f} s; it also excludes common source-history generation, experiment duplication and analysis. Ridge fitting takes {model['trainingWall']*1000:.3f} ms. A reusable offline model may amortize those costs over many runs, but this small held-out set does not establish such reuse in production.

## Numerical verification

The main oracle has {len(gates)} candidate-versus-A0 endpoint gates, of which {failed} fail. Maximum temperature difference is {maximumT:.6g} K. Fields include T, p, U, Qdot, h, rho and every species; positivity and |ΣY−1|<1e-10 are also required. L1, L2 and L∞ norms, logged linear residuals/iteration counts, integrated observables, and native mass/species/element/energy budgets are retained. The gate uses absolute plus field-scale relative tolerances rather than division by trace-species values. Rejected schemes and pilot failures are not erased.

All {len(continuous_gates)} additional restarted-A0 versus uninterrupted trajectory gates pass, including all ten operating conditions and two independent longer native trajectories. This verifies the physical checkpoint state used by the oracle independently of comparisons between candidate actions. Live, deployment, profile, scaling and fine-timestep action gates are retained separately.

The live collection has {sum('gate' in r for r in live)} endpoint comparisons and {len(failed_live)} failed gate. {live_failure_note} The deployed controller and chemistry baseline retain passing gates.

![Rejected mesh-partition numerical controls](../figures/46_live_mesh_numerical_controls.png)

{flux_note}

A separate final-epoch audit checks {len(physical['cases'])} endpoints for finite values in every primary field and species, positive T/p/rho, species positivity and normalization. This guards against NaNs being hidden by comparisons and provides basic thermodynamic admissibility; it does not replace conservation or convergence tests.

Algorithmic equivalence is distinct from physical accuracy. Maximum closed-history mass drift is {100*mass:.4f}% and maximum relative total-energy drift is {100*energy:.3f}%. The energy reference can be small relative to reaction chemical energy; both absolute inventory terms and reference normalization are retained. Refinement changes temperatures by tens of kelvin and heat release also changes with grid size. The dt=0.25 μs action study repeats the same 160 μs future interval with 640 global steps. This is an accuracy sensitivity check, not a claim of spatially resolved or converged flame physics.

{fine_table}

Nine additional bounded accuracy pilots investigate the moving condition's energy-budget failure over the same 240 μs history. Seven independent controls decrease dt to 0.125 and 0.0625 μs, increase pressure correctors, refine the grid at the finest dt, and separately increase PIMPLE outer correctors to test coupling of species, energy and pressure. Two further controls combine four pressure corrections with 0.0625 and 0.03125 μs timesteps, following the observed independent effects. These diagnostics do not refit the frozen controller or replace the performance dataset. Absolute energy values accompany the normalized drift, preventing a small reference denominator from being mistaken for a field error estimate.

{diagnosis_table}

![Energy-budget diagnosis](../figures/44_conservation_diagnosis.png)

The signed energy drift is a discretization/thermodynamic-coupling diagnostic; it is not an action-versus-reference norm. Passing action gates therefore supports an algorithmic comparison on this discretized problem, while these budgets set the limit on its physical validity.

The moving condition's energy drift is not monotonic under the initial timestep refinement (about −21% at 0.5 μs and −28% at 0.25 μs). Four pressure correctors at 0.25 μs reduce the magnitude to about 5%; combining them with 0.0625 and 0.03125 μs gives about −2.08% and −1.37%. More outer correctors instead give positive drifts of about 59% and 30% in the separate 0.25 μs pilots. These results motivate a coupled convergence study, and do not establish a resolved flame or energy convergence.

{initial_note}

{long_note}

## Experimental and statistical methodology

One AMD Ryzen 5 5600X host supplies six physical cores and twelve hardware threads under WSL2. OpenCFD v2012 uses GCC 6.3, -O3, double precision, 32-bit labels, OpenMPI 4.0.3 and Scotch 6.0.9. MPI processes are bound to physical cores with no oversubscription; OMP is one. Existing pilots/source histories and the explicit MPI regression supply warmup. Timed campaigns execute sequentially. Randomized trial order is seeded and retained. Whole process wall uses blocking wait with an independent timeout watchdog, avoiding quantized polling clocks. Rank phase clocks add no collectives. Hardware frequency/thermal variation is not controlled by a hardware counter and remains a threat.

Tables retain n, median, arithmetic mean, sample standard deviation, min, max and CV. Independent median ratios use 4000 bootstrap resamples with fixed seeds. Five trials are modest; three live trials yield particularly coarse uncertainty. Intervals are pointwise and exploratory, not simultaneous, population-level or corrected for selecting a best state. Aggregate held-out ratios sum condition medians; their within-condition intervals resample runs while retaining the same three test conditions.

Replay aggregate intervals additionally resample measured trial costs within the six fixed test checkpoint states, retaining the fitted policy choices, observed oracle labels and decision-overhead estimates. An A0 choice shares its baseline draw. These conditional intervals exclude model-fitting and physical-case population uncertainty; an interval around the hindsight oracle does not remove its selection optimism.

## Scaling results

The 512-cell scaling campaign compares A0, AC and the frozen controller at 1, 2, 4 and 6 bound physical cores, five trials each. Each rank count has a measured prefix; all policies at that rank count start from identical fields. Additional cross-rank native trajectory gates compare the complete prefix and continuation against the one-rank physical endpoint. The four-rank/256-cell model is extrapolated to new rank counts and cell counts; rank one has a no-action guard. Strong scaling includes continuation and action overhead, while the common prefix is separately recorded. There is one host, no Slurm installation/allocation and no inter-node network. Startup and small-domain costs can dominate, so this is not evidence of large-scale HPC scalability.

{scale_table}

## Controller results and decision regret

The requested eight policies are compared retrospectively; AC already contains the upstream adaptive rank-pair task behavior. Actual live runs additionally execute the threshold and persistence policies. The hindsight oracle cannot be executed online without counterfactual future trials. Regret is selected total cost minus minimum observed action median. Feature-driven AM/AH reuse the acquisition pass already charged in the action cost, adding only the policy's own inference clock. A0/AC selections instead add their required feature acquisition. Replay accounting is refreshed without refitting the frozen model, and its fingerprint is asserted. HarmfulFraction uses a positive median cost difference, not a statistical claim of harm. Unnecessary and missed decisions are explicitly counted.

{policy_table}

The live results below use uninterrupted native standard chemistry as the reference, so they expose the actual external-orchestration price. A segmented-A0 reference is also retained to distinguish model action utility from the cost of segmenting a simulation. A ratio with false numerical eligibility is descriptive cost evidence, not a valid performance gain. The failed trial is retained rather than removed from its distribution.

{live_table}

![Executed held-out costs](../figures/50_live_heldout_costs.png)

## Generalization

Training uses entire persistent, translating, ignition, cold-control and GRI-size conditions. Validation uses whole uniform and decay conditions. Test uses heldoutMoving, heldoutIgnition and heldoutPersistent. No random timestep split is used. Temperature/velocity/width changes within one periodic geometry are the tested generalization scope; they do not establish transfer to different burners, fuels, solvers, mechanisms or hardware. Live controller state comes only from its own completed prefix. Frozen model hashes accompany deployments, and test results are not used to refit coefficients or margins.

## Ablation studies

{abl}

Removing uncertainty increases held-out replay speedup from {policies['test']['ablation_full']['aggregateSpeedup']:.3f}× to {policies['test']['ablation_noUncertainty']['aggregateSpeedup']:.3f}×: the conservative margin misses useful AC opportunities here. It still falls below always-AC. Removing persistence reduces it to {policies['test']['ablation_noPersistence']['aggregateSpeedup']:.3f}×. Omitting migration, communication or transport changes no measured chosen-action utility in this design; small timing differences in inference are not feature evidence. The communication input was constant, so its ablation cannot establish physical irrelevance. The transport omission replaces the fitted input by its training mean at inference. Previous-only and EMA variants are explicitly defined.

## Communication tradeoff and migration overhead

Rank-local phase maxima are not additive across overlapping MPI ranks. PMPI observes send payload bytes, receive buffer capacity, collective counts and MPI-call/wait durations without adding barriers. Those bytes are application buffers, not observed wire traffic; collectives are counted but their payload volume is not included. Wait time reflects synchronization and imbalance as well as transfer. Main timings use profiling off; a randomized three-repeat on/off calibration measures perturbation. Mesh redistribution PMPI is recorded separately. Face counts, neighbors, cell-count imbalance and linear iterations explain geometric/solver changes; cache misses and memory locality are not directly measured.

![MPI-call consequence model](../figures/45_mpi_consequence_model.png)

An approximate break-even H*=Caction/(observed mean solver savings per step) is reported only for positive savings and assumes those savings persist. A missing value means no positive measured use-phase saving. Measured H=20/80/320 sweeps are distinguished from any extrapolated crossing. The dimensionless lifetime/break-even ratio is a diagnostic and does not establish a universal threshold.

## Regime map

The map plots measured chemistry fraction and imbalance, sizes markers by past-cost lifetime and colors median oracle winners. A0 and intervals crossing unity are outlined to show weak separation. No clean decision boundary or unobserved winning region is imposed. Large imbalance matters only when the chemistry fraction and usable horizon leave enough savings after action and solver consequences.

![Regime map](../figures/25_regime_map.png)

## Discussion and negative results

The oracle is the first test of whether a more sophisticated selector is justified. A strong chemistry-only scheduler can consume most available headroom while retaining transport locality. A model can fit whole-cost deltas yet still select poorly after extraction, uncertainty and restart costs. Balanced current cell clocks need not predict future chemistry, and synchronous transport clocks can contain chemistry wait propagation. Weak action separation in uniform or late states is evidence against confident classification, not permission to report a small difference as a discovery.

The tested weighted-mesh and hybrid actions must be judged by their actual state medians and intervals in the complete table; no winning region is assumed. Native restart semantics and the stale-write failure show why field matching at a convenient output is insufficient. Physical budgets and refinement also prevent converting an algorithmic performance comparison into a validated combustion claim.

## Related-work comparison and novelty assessment

Weighted graphs, chemistry tasks, adaptive triggers, migration penalties, persistence, prediction and distinct physics decompositions are prior art. The search did not establish an identical earlier four-action same-version checkpoint dataset, but a bounded search cannot prove first invention. The narrow contribution is the local oracle/replay/deployment artifact, state-preserving live methodology, and measured limitations of this consequence model against an executed strong baseline. A controller superiority claim requires the actual held-out end-to-end table, not the existence of source code or a favorable chemistry timer.

## Limitations and threats to validity

One small WSL2 CPU host provides no inter-node evidence. OpenFOAM branch/version, GCC, MPI, Scotch and rank placement limit portability of numbers. Fixed mesh/geometry, H2 premix, carbon-inactive GRI, strict tolerances, upwind transport and opt-in thermo corrections define a narrow workload. Coarse reaction zones, temporal/spatial error and physical energy budgets limit physical inference. Thermal/frequency variation, filesystem cache, background host work and small sample counts limit statistics. Case selection covers negative controls but remains constructed. Whole-case splitting reduces leakage without creating broad physical diversity. Source clock noise changes labels, oracle selection is optimistic, and the model has more terms than independent training conditions. The communication feature is unidentifiable in its initial design. LTS and transient results are kept separate. PMPI cannot separate wire transfer, waits and collective topology.

## Reproducibility

From research/physicsAwareDecomposition run:

```bash
bash actionStudy/scripts/setup.sh
bash actionStudy/scripts/build.sh
bash actionStudy/scripts/buildRestart.sh
bash actionStudy/scripts/buildInventory.sh
bash actionStudy/scripts/buildMPI.sh
bash actionStudy/scripts/buildRedistributor.sh
bash actionStudy/scripts/buildFluxAudit.sh
bash actionStudy/scripts/buildFluxState.sh
bash actionStudy/scripts/reproduce.sh smoke
# Bounded pilot, in a fresh retained directory:
PAD_ACTION_ROOT=/tmp/pad-action-small bash actionStudy/scripts/reproduce.sh small
# Complete local study and artifact; output directory must be fresh:
export PAD_ACTION_ROOT=/tmp/pad-action-full
bash actionStudy/scripts/reproduce.sh full
python3 actionStudy/scripts/finish.py
```

The default is a smoke regression, not a cluster allocation. Compiler adaptation uses the documented user-space sysroot without changing the installed OpenFOAM. Raw transient fields/vendor/build products are ignored by Git and retained on this host; processed rows, compact timing evidence, source hashes, scripts, tables and figure source slices form the portable artifact. Every figure is regenerated from data. The fresh small-profile execution is recorded in reproduction_test.json. Rejected interiorWriteProtocol/nativeRestartProtocolV2 epochs and incomplete live attempts remain retained and excluded. License and citation metadata preserve upstream credit.

## Conclusions and future work

The available hardware establishes an audited local answer about action cost, predictive overhead and numerical equivalence, with explicit physical-accuracy limits. It does not establish universal thresholds, large-cluster scaling or a superior general controller. The useful next research boundary requires resolved/conserved physical cases, independently varying communication geometry, broader whole-case generalization and multi-node execution; unavailable network/HPC hardware cannot be replaced by oversubscribed local ranks. These are limitations of this artifact's external validity rather than unimplemented local benchmark steps.

## Publication assessment

The strongest present framing is an OpenFOAM technical/benchmark contribution or a workshop negative-result study. A conference/journal method paper would need demonstrated advantages over the strong task baseline on diverse resolved cases and meaningful multi-node scale. A software paper would need sustained public reuse and independent installation evidence. [JOSS's current submission requirements](https://joss.readthedocs.io/en/latest/submitting.html) require sustained public development and research impact, so a new burst of commits does not by itself make this artifact ready for that venue. No acceptance likelihood is asserted. A relevant technical audience is the [OpenFOAM Workshop](https://www.openfoamworkshop.org/).

## References and evidence

The complete [literature catalogue](literature.json), [BibTeX](references.bib), [primary-source ledger](claim_verification.md), [DOI registration metadata audit](bibliography_metadata_verification.json), [comparison table](related_work_comparison.md) and [novelty challenge](novelty_search.md) provide checked access levels. Local claims are generated from headline.json, oracle_summary.json, live_aggregate.json and the full CSV tables; qualityControl.py checks their raw provenance and gates. The research log records meaningful engineering failures and scientific decisions.
'''
    (ROOT/'docs/final_report.md').write_text(report)
    (tables/'summary.md').write_text('# Summary results\n\n'+policy_table+'\n\n'+live_table+'\n\n'+scale_table)
    (ROOT/'docs/research_summary.md').write_text('# Research summary package\n\n'+report.split('## Abstract\n\n')[1].split('\n\n## Introduction')[0]+'\n\n'+live_table+'\n\nSee [highlight figures](../figures/highlights/), [architecture](../figures/33_architecture.png), [workflow](../figures/34_methodology.png), [complete results](final_report.md) and [summary tables](../tables/summary.md).\n')
    import re
    readme=ROOT/'README.md'
    if not readme.exists():readme.write_bytes((Path(__file__).resolve().parents[1]/'README.md').read_bytes())
    measured=f'''<!-- measured-results-start -->
## Measured results

Held-out replay: always-AC {policies['test']['periodicChemistry']['aggregateSpeedup']:.3f}×, mesh-only {policies['test']['periodicMesh']['aggregateSpeedup']:.3f}×, frozen whole-cost selector {policies['test']['wholeSolver']['aggregateSpeedup']:.3f}×, hindsight oracle {policies['test']['oracle']['aggregateSpeedup']:.3f}×. The oracle offers only {100*(headroom-1):.2f}% extra headroom above the strong chemistry action.

Independent moving-condition AC confirmation: {confirmation['speedup']:.3f}×, 95% within-condition bootstrap interval [{confirmation['CI'][0]:.3f}, {confirmation['CI'][1]:.3f}], twenty trials per action, four bound ranks, 256 cells, 160 μs future interval, global dt=2 μs, complete action and continuation process costs.

Actual held-out live controller: {live_agg['controller']['speedup']:.3f}× [{live_agg['controller']['CI'][0]:.3f}, {live_agg['controller']['CI'][1]:.3f}] relative to uninterrupted native chemistry, including preprocessing, decomposition and every controller startup/action. Uninterrupted Stuttgart baseline: {live_agg['ACContinuous']['speedup']:.3f}×. The report distinguishes field equivalence from physical conservation/refinement limitations.

![Strong baseline consumes almost all observed oracle headroom](figures/23_oracle_controller_comparison.png)
<!-- measured-results-end -->
'''
    current=readme.read_text()
    if '<!-- measured-results-start -->' in current:current=re.sub(r'<!-- measured-results-start -->.*?<!-- measured-results-end -->',measured.strip(),current,flags=re.S)
    else:current=current.replace('## What is implemented',measured+'\n## What is implemented')
    readme.write_text(current)
    print('WROTE generated report, tables and research-summary package; best',headline['best'],'live held-out',live_agg)

if __name__=='__main__':main()
