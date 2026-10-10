"""Primary-source claim ledger and deliberately adversarial novelty review."""
import json
from pathlib import Path
from analysis import ROOT
PAD=Path(__file__).resolve().parents[2]

def main():
    source_docs=Path(__file__).resolve().parents[1]/'docs'
    for name in ['fulltext_access.json','stuttgart_v2012.patch']:
        source=source_docs/name;target=ROOT/'docs'/name
        if source.exists() and source.resolve()!=target.resolve() and not target.exists():target.write_bytes(source.read_bytes())
    catalog=json.loads((PAD/'docs/literature.json').read_text())
    byid={r['id']:r for r in catalog}
    byid['retfalvi2026'].update(DOI='10.2139/ssrn.6678658',
        checked='Primary SSRN abstract and author/DOI metadata checked 5 October 2026; full-paper download remains inaccessible (403).',accessDate='2026-10-05')
    byid['oord2025'].update(URL='https://pure.tudelft.nl/ws/portalfiles/portal/243087930/van-den-oord-et-al-2025-dynamic-multi-level-load-balancing-for-scalable-simulations-of-reacting-multiphase-flows.pdf',
        checked='Full author-institution copy of final CC BY paper, sections 2–4 and data statement',
        method='Independent chemistry and equation-of-state task repartitioning; GREEDY, SORT, SORT2; workload autocorrelation/persistence discussed.',
        mainResult='GREEDY can lose to overhead; SORT/SORT2 improve balancing. No percentage translated into a wall-time reduction here.',
        hardware='Snellius nodes: two 64-core AMD Rome 7H12 CPUs, 2.6 GHz, HDR100.',
        benchmark='INCA Spray A: coarse 1.8M cells / 2727 blocks / 700 steps; fine 10.6M cells / 2864 blocks / 400 steps.',
        limitations='Library kernel reproduction here does not reproduce the full INCA simulation.',status='Full primary text checked; public library executed separately.')
    additions=[
      ('gartner2024','A Chemistry Load Balancing Model for OpenFOAM',['Jan Wilhelm Gärtner','Ali Shamooni','Thorsten Zirwes','Andreas Kronenburg'],2024,'Computer Physics Communications 305, 109322','10.1016/j.cpc.2024.109322','https://www.researchgate.net/publication/379890300_A_Chemistry_Load_Balancing_Model_for_Openfoam',
       'Author-provided SSRN preprint 4798159, sections 2, 3.1.3, 3.2; official pinned source.',
       'Previous cell-clock task balancing with point-to-point communication; standard and TDAC.',
       'Published speedups refer to chemistry integration, excluding PDE and auxiliary wall time. The local comparison executes a standard-model v2012 port, not TDAC.',
       'Counterflow up to 64 cores; channel strong scaling 15M cells, 9 species, 27 reactions, up to 8192 cores on Hawk.'),
      ('cuoci2025','Adaptive and multi-objective load balancing for detailed chemistry simulations in OpenFOAM',['Alberto Cuoci'],2025,'20th OpenFOAM Workshop, Vienna; abstract pp. 37–38',None,'https://zenodo.org/records/18670150',
       'Downloaded full book of abstracts; PDF pages 41–42 (printed 37–38).',
       'Adaptive task balancing with migration penalties and algorithm selection; mesh ownership is preserved.',
       'Adaptive triggers and multi-objective migration-aware chemistry scheduling are already prior art. Workshop material, not a journal paper.',
       'Examples: 160 species/2500 reactions/100k cells/32 processes; 320 species/14000 reactions/250k cells/128 processes.'),
      ('quicklb','NLESC-JCER/QUICKLB: Version 0.02',['Victor Azizi'],2022,'Zenodo software archive','10.5281/zenodo.6598303','https://quicklb.readthedocs.io/en/latest/',
       'Public source archive 6598303 inspected; GNU Fortran and isolated MPI compilation plus four-rank kernel executions.',
       'Fortran/C/Python task load-balancing library; GREEDY, SORT, SORT2.',
       'Direct third-party library reproduction is feasible; public INCA dataset is about 20.1 GB and no matching INCA installation is available.',
       'Our separate Gray–Scott 30×30 kernel is a library QA benchmark, not a reacting-flow performance competitor.'),
      ('samfass2020','Lightweight task offloading exploiting MPI wait times for parallel adaptive mesh refinement',['Philipp Samfass','Tobias Weinzierl','Dominic E. Charrier','Michael Bader'],2020,'Concurrency and Computation: Practice and Experience','10.1002/cpe.5916','https://arxiv.org/abs/1909.06096',
       'Primary preprint and author-institution indexed full text; PDF download returned HTML and is recorded.',
       'Reactive task offloading complementary to mesh partitioning.',
       'Benefits depend on persistence and offloading costs; migration can outweigh a brief imbalance. No speedup comparison to this study.',
       'Adaptive mesh refinement framework, different physics and hardware.'),
      ('chameleon2023','From reactive to proactive load balancing for task-based parallel applications in distributed memory machines',['Minh Thanh Chung','Josef Weidendorfer','Karl Fürlinger','Dieter Kranzlmüller'],2023,'Concurrency and Computation: Practice and Experience','10.1002/cpe.7828','https://onlinelibrary.wiley.com/doi/10.1002/cpe.7828',
       'Full primary publisher HTML, sections 4–7; institutional copy also located.',
       'Characterize tasks, learn predicted load, offload proactively subject to migration delay.',
       'Prediction, runtime cost models, and proactive decisions are established concepts. Dedicated hybrid MPI/OpenMP communication threads differ from our external orchestrator.',
       'Chameleon microbenchmarks and Samoa AMR; conceptual comparison only.'),
      ('pele_odegrid','PeleLMeX implementation: parallelism',['PeleLMeX developers'],None,'Official manual 22.12',None,'https://amrex-combustion.github.io/PeleLMeX/manual/html/Implementation.html',
       'Full official implementation documentation, Parallelism section.',
       'Separate chemistry box array and distribution map, Knapsack weights from chemistry RHS calls; transport uses its own map.',
       'Independent chemistry decomposition and a threshold to avoid expensive data copies already exist. This was not executed locally.',
       'AMReX MPI+X; CPU/GPU-capable reactive flow software.'),
      ('balos2025','SUNDIALS time integrators for exascale applications with many independent systems of ordinary differential equations',['Cody J Balos','Marcus Day','Lucas Esclapez','Anne M Felden','David J Gardner','Malik Hassanaly','Daniel R Reynolds','Jon S Rood','Jean M Sexton','Nicholas T Wimer','Carol S Woodward'],2025,'International Journal of High Performance Computing Applications','10.1177/10943420241280060','https://journals.sagepub.com/doi/10.1177/10943420241280060',
       'Primary full publisher text, section 4.1.1; institutional final PDF located.',
       'Tentative chemistry ODE grid deployed when sufficiently better; typically 5% balancing improvement threshold offsets data movement.',
       'A migration-aware threshold is prior art; no transferable hardware speedup is claimed here.',
       'Pele/Nyx, exascale CPU/GPU ODE integration.'),
      ('nanda2025','Exploring Dynamic Load Balancing Algorithms for Block-Structured Mesh-and-Particle Simulations in AMReX',['Amitash Nanda','Md Kamal Hossain Chowdhury','Hannah Ross','Kevin Gott'],2025,'arXiv:2505.15122v1',None,'https://arxiv.org/html/2505.15122v1',
       'Full primary preprint HTML and reproducibility appendix.',
       'Knapsack, SFC, painter partition and topology-aware Knapsack+SFC.',
       'Weighted work, locality and migration tradeoffs are established. Algorithm-quality experiments do not establish our solver speedups.',
       'AMReX/Perlmutter generated-weight experiments; not a chemistry solver.'),
      ('rlchem2026','Autonomous adaptive solver selection for chemistry integration via reinforcement learning',['Eloghosa Ikponmwoba','Opeoluwa Owoyele'],2026,'Combustion and Flame 292, 115223; full preprint arXiv:2604.00264v1','10.1016/j.combustflame.2026.115223','https://arxiv.org/html/2604.00264v1',
       'Full primary v1 HTML; submitted 31 March 2026. Publisher metadata verified 5 October 2026: S0010218026004591, journal volume 292, article 115223; journal full text not assumed equivalent to v1.',
       'Accuracy-constrained adaptive selection between CVODE and QSS integration.',
       'Generic adaptive chemistry solver selection is prior art; it changes the integration algorithm rather than MPI mesh/task ownership.',
       '0D and 1D n-dodecane kinetics, 106 species; no direct baseline execution here.'),
      ('lapointe2020','Data-driven selection of stiff chemistry ODE solver in operator-splitting schemes',['Simon Lapointe','Sudeepta Mondal','Russell A. Whitesides'],2020,'Combustion and Flame 220, 133–143','10.1016/j.combustflame.2020.06.033','https://www.sciencedirect.com/science/article/pii/S0010218020302510',
       'Primary publisher metadata/abstract; institutional full-copy fetch failed.',
       'Data-driven chemistry ODE solver selection.',
       'Learning which chemistry algorithm to run predates this work. No unverified quantitative claim.',
       'Operator-split stiff chemistry; conceptual comparison only.'),
      ('openfoam10','OpenFOAM 10 release: parallelisation',['OpenFOAM Foundation'],2022,'Official release documentation',None,'https://openfoam.org/release/10/',
       'Full official release notes and linked source changes.',
       'General CPU-load mesh balancing, initially chemistry weights; runtime mesh distributor and Zoltan integration.',
       'A chemistry-weighted runtime mesh balancer is not a new invention here. Foundation release differs from OpenCFD v2012.',
       'Official software capability, not a local benchmark.'),
      ('legion_s3d','Dynamic Task Scheduling to Mitigate System Performance Variability',['Galen Shipman','Patrick McCormick','Kevin Pedretti','Stephen Lecler Olivier','Kurt Brian Ferreira','Jacqueline H. Chen','Ramanan Sankaran','Sean Treichler','Alex Aiken','Michael Bauer'],2015,'SAND2015-3037C',None,'https://www.osti.gov/servlets/purl/1249032',
       'Primary technical report indexed text, S3D implementation section; title and ten authors verified against primary OSTI record 1249032.',
       'Legion S3D task mapper distributes work over CPUs and GPUs and schedules dependent phases.',
       'Runtime task mapping provides a broader competing approach. No numeric or definitive publication attribution used.',
       'S3D reacting flow; different runtime and hardware.'),
      ('drama2000','Dynamic load-balancing of finite element applications with the DRAMA library',['A. Basermann','J. Clinckemaillie','T. Coupez','J. Fingberg','H. Digonnet','R. Ducloux','J.-M. Gratien','U. Hartmann','G. Lonsdale','B. Maerten','D. Roose','C. Walshaw'],2000,'Applied Mathematical Modelling 25, 83–98','10.1016/S0307-904X(00)00043-3','https://chriswalshaw.co.uk/papers/fulltext/BasermannApMM00.pdf',
       'Full author-hosted final paper, section 2.1, printed pp.84–85; year and author metadata checked against DOI registration.',
       'Measured multiphase computational costs, communication and migration-aware mesh repartitioning.',
       'The objective sums phase-wise maximum process costs; predicting partition consequences is longstanding prior art.',
       'Finite-element applications; no local DRAMA execution or transferred speedup.'),
      ('fluent_docs','Ansys Fluent User Guide: Mesh Partitioning and Load Balancing',['Ansys'],2025,'Release 2025 R2, section 44.5',None,'https://ansyshelp.ansys.com/public/Views/Secured/corp/v252/en/flu_ug/flu_ug_GridPartition.html',
       'Full official manual, weighting section 44.5.4.1, checked 5 October 2026.',
       'Timer/model-weighted partitions, chemistry and ISAT weights, multiple constraints and runtime cell migration.',
       'Balancing chemistry together with other model costs predates this study; this documentation does not establish our four-action selector.',
       'Commercial capability; license/executable unavailable locally, no timing comparison.'),
      ('openfpm_docs','OpenFPM vector examples: dynamic load balancing',['OpenFPM developers'],None,'Official examples, SPH load-balancing subsection',None,'https://ppmcore.mpi-cbg.de/vector-example/',
       'Full official examples and linked implementation, checked 5 October 2026.',
       'Domain cost model includes computation, ghost communication frequency and migration.',
       'Communication/migration-aware objectives are prior art; the example uses particle methods.',
       'Conceptual comparison; no reacting-flow performance reproduction.'),
    ]
    for id,title,authors,year,venue,doi,url,checked,method,result,benchmark in additions:
        byid[id]=dict(id=id,title=title,authors=authors,year=year,venue=venue,DOI=doi,URL=url,
            checked=checked,method=method,mainResult=result,benchmark=benchmark,accessDate='2026-10-05' if id in ['drama2000','fluent_docs','openfpm_docs','rlchem2026'] else '2026-10-04',
            limitations='Comparisons across frameworks are conceptual unless explicitly executed; access level limits confidence.',
            status='Verified to the stated access level')
    metadata=ROOT/'docs/bibliography_metadata_verification.json'
    if metadata.exists():
        for verified in json.loads(metadata.read_text()):
            if verified.get('status')=='Primary DOI registry returned metadata' and verified.get('titleSimilarity',0)>.8:
                record=byid.get(verified['id'])
                if record and record.get('DOI')==verified.get('DOI'):
                    record.update(title=verified['title'],authors=verified['authors'],metadataVerification=verified['agency']+' DOI registration checked 2026-10-05')
    catalog=list(byid.values());(ROOT/'docs/literature.json').write_text(json.dumps(catalog,indent=2,ensure_ascii=False))
    bib=[]
    for r in catalog:
        fields={'title':r['title'],'author':' and '.join(r['authors']),'url':r['URL'],'note':r['checked']}
        if r.get('DOI'):fields['doi']=r['DOI']
        if r.get('year'):fields['year']=str(r['year'])
        bib.append('@misc{'+r['id']+',\n'+',\n'.join('  '+k+' = {'+v.replace('{','').replace('}','')+'}' for k,v in fields.items())+'\n}')
    (ROOT/'docs/references.bib').write_text('\n\n'.join(bib))
    rows=['| Claim | Primary source | Exact evidence location | Checked | Confidence | Notes |','|---|---|---|---|---|---|']
    claims=[
      ('Stuttgart gains are chemistry-only','gartner2024','Section 3.1.3 excludes PDE and auxiliary cost.','High for timing scope','Do not compare its reported chemistry speedup to whole-solver speedup.'),
      ('Native Stuttgart compatibility excludes v2012','gartner2024','Official pinned README: v2212, v2306, v2312; source methods and registration.','High','Our standard-only compatibility port is disclosed and supplied as a patch.'),
      ('DLBFoam gain combines distinct optimizations','tekgul2021','Figure 11: balancing alone 2.57×; balancing plus reference-cell filtering 9.87× for the stated Spray-A experiment.','High','256 ranks, 4.5M cells, 500 steps, dt=2e-7 s; different workload.'),
      ('Adaptive migration-aware chemistry scheduling predates this project','cuoci2025','Printed pp.37–38 describe migration penalties and adaptive triggers preserving mesh ownership.','High for abstract content','Workshop evidence; no full performance paper assumed.'),
      ('Persistence and multiple physics stages are prior art','oord2025','Sections 1–3 discuss autocorrelation, distinct EoS/chemistry stages and transfer overhead.','High','No claim that our four actions or predictor were evaluated there.'),
      ('GREEDY may lose to overhead','oord2025','Results contrast GREEDY with SORT/SORT2.','High','Library executed locally on an independent kernel; INCA results not reproduced.'),
      ('Prediction plus migration-delay models are established','chameleon2023','Sections 4 and 5 describe migration bounds, task characterization and learned proactive offloading.','High','No generic predictive-load-balancing novelty claim.'),
      ('Chemistry and mesh ownership can be decoupled','pele_odegrid','Official Parallelism section lists separate grid and chemistry maps.','High','No local Pele performance comparison.'),
      ('Migration-aware threshold exists in Pele','balos2025','Section 4.1.1: tentative ODE grid and typically 5% improvement trigger.','High','Do not claim a universal threshold or compare GPU timing.'),
      ('Chemistry-weighted mesh redistribution predates this project','openfoam10','Parallelisation release notes: CPU load balancer, chemistry weighting, runtime mesh redistribution.','High','Foundation and OpenCFD APIs differ.'),
      ('Adaptive ODE algorithm selection is prior art','rlchem2026','Full v1 methods select CVODE or QSS under accuracy constraints; publisher confirms journal DOI.','High for v1 scope and metadata','Does not select MPI mesh/task ownership; journal full-text differences not inferred.'),
      ('Phase-wise whole-application cost models predate this study','drama2000','Section 2.1, pp.84–85: sum of phase maxima, measured application costs and migration-aware partitioning.','High','Different physics; this is not an identical four-action chemistry selector.'),
      ('Chemistry weights combined with other model costs are established','fluent_docs','Official section 44.5.4.1: timer weights, stiff chemistry and multi-constraint model weights.','High for documented capability','Commercial software unavailable locally; no performance claim.'),
      ('Communication frequency and migration cost appear in earlier domain models','openfpm_docs','Official SPH load-balancing example includes ghost-call frequency and migration terms.','High for documented example','Particle domain balancing, not a chemistry action oracle.'),
      ('A precise identical prior four-action selector has not been established','samfass2020','Search log and closest-source comparison, rather than a proof of absence.','Limited','Absence in a bounded search is not priority proof; unresolved thesis and SSRN full texts remain listed.'),
    ]
    for claim,id,evidence,confidence,notes in claims:
        rows.append(f"| {claim} | [{byid[id]['title']}]({byid[id]['URL']}) | {evidence} | {byid[id].get('accessDate','2026-10-04')} | {confidence} | {notes} |")
    (ROOT/'docs/claim_verification.md').write_text('# Primary-source claim verification\n\n'+ '\n'.join(rows)+'\n\nThe full access ledger is [fulltext_access.json](fulltext_access.json). Quantitative local claims are generated from processed data by writeReport.py and audited against raw manifests by qualityControl.py.\n')
    comparison=[
      '| Work | Framework / chemistry | Dynamic? | Mesh migration? | Chemistry tasks? | Prediction? | Migration cost? | Whole-solver objective? | Published/tested scale |',
      '|---|---|---|---|---|---|---|---|---|',
      '| Gärtner 2024 | OpenFOAM; standard/TDAC | Yes | No | Yes | Previous cell clocks | Lightweight transfers | Published plots primarily chemistry time | Up to 8192 cores |',
      '| DLBFoam 2021 | OpenFOAM; gas kinetics | Yes | No | Yes | Previous work | Communication overhead | Solver acceleration; filtering separate | Spray A example 256 ranks |',
      '| Cuoci 2025 workshop | OpenFOAM; detailed kinetics | Adaptive | No | Yes | Current cost/trigger | Explicit penalty | Multi-objective chemistry scheduling | Examples 32/128 processes |',
      '| van den Oord 2025 | INCA; EoS and chemistry | Yes | Base mesh retained | Yes, two stages | Persistence / previous cost | Transfers compared | Full application phases analyzed | Million-cell Spray A |',
      '| PeleLMeX / SUNDIALS | AMReX; detailed chemistry | Periodic | Separate ODE grid | ODE boxes | RHS workload | Efficiency trigger | Application cost | Exascale CPU/GPU software |',
      '| ParMETIS / Zoltan | General weighted graphs | Yes | Yes | User-defined | User cost weights | Explicit adaptive tradeoff | Partition services, user objective | General HPC libraries |',
      '| OpenFOAM Foundation 10 | CFD, initially chemistry weights | Yes | Yes | Mesh cells | CPU cell costs | Runtime redistribution | General CPU load balance | Capability, not reproduced here |',
      '| DRAMA | Finite elements | Yes | Yes | No chemistry-specific tasks | Measured phase costs | Partition migration considered | Sum of phase maxima | Different application, not reproduced |',
      '| Ansys Fluent 2025 R2 | Reactive CFD and other models | Yes | Yes | Mesh-based weighting | Timers / model weights | Runtime cell migration | Multiple model constraints | Documented capability, not reproduced |',
      '| This study | OpenCFD v2012; H2 and GRI | External segments | Native redistributePar | Stuttgart compatibility port | Past-only whole-cost ridge | Measured process wall | Four-action J(a,H), plus actual deployments | 256/512 cells, 1–6 ranks, one host |',
    ]
    (ROOT/'docs/related_work_comparison.md').write_text('# Conceptual comparison\n\n'+ '\n'.join(comparison)+'\n\nOnly the same-version Stuttgart standard implementation is a directly timed reactive-flow competitor. QUICKLB is additionally compiled and tested on its own public-library kernel; neither paper speedups nor cross-framework results are treated as a performance leaderboard.\n')
    (ROOT/'docs/novelty_search.md').write_text('''# Novelty challenge and search record

Search dates: 2026-10-04 and 2026-10-05. Primary papers, author repositories, official code and documentation were preferred. Full-text access failures are retained rather than converted into verified claims.

Queries included “chemistry mesh load balancing action prediction runtime”; “reacting load balancing persistence”; “chemistry load balancing persistence”; “reacting mesh redistribution prediction”; “predictive dynamic load balancing migration cost”; “proactive task offloading iterative applications”; “Cuoci adaptive multi-objective”; “PeleLMeX ODE load balancing”; “S3D load balancing detailed chemistry GPU”; and separate Scotch, PT-Scotch, ParMETIS, Zoltan, Charm++, AMPI, GPU chemistry and operator-split solver-selection searches.

The closest counterexamples are migration-aware adaptive chemistry scheduling (Cuoci), multistage chemistry/EoS balancing with persistence (van den Oord), learned proactive offloading (Chameleon), separate transport/ODE maps (PeleLMeX), chemistry-weighted native mesh redistribution (Foundation OpenFOAM), and general communication/migration-aware graph services. These invalidate novelty claims for those components.

The follow-up search also found a phase-wise whole-application objective in the author-hosted DRAMA paper, and timer/multimodel chemistry partition weights in official Fluent documentation. These further restrict novelty claims. The 2026 adaptive chemistry-solver preprint now has publisher-verified journal metadata; its verified v1 method still selects integrators rather than MPI ownership.

The bounded search did not establish a previous exact same-version OpenFOAM checkpoint oracle choosing among unchanged ownership, chemistry tasks, mesh ownership and hybrid actions using future total process wall. This is an observation about the search, not proof of first invention. A multiobjective reactive-flow thesis found through CiteSeer remains unresolved after full-text timeouts; the 2026 physics-informed GPU preprint full text returned 403. They are unresolved candidates, not evidence that identical prior art is absent.

The defensible contribution is a reproducible, numerically gated local action-oracle artifact and an honest comparison of consequence prediction with a strong executed baseline. New partitions, task offloading, prediction, persistence, migration penalties and adaptive triggers are not claimed. Controller superiority requires actual held-out end-to-end evidence; a functioning prototype alone does not meet that requirement. Negative results and tiny oracle headroom are useful evidence about whether extra control complexity is worthwhile.
''')
    print('WROTE',len(catalog),'literature entries and primary-source claim ledger.')

if __name__=='__main__':main()
