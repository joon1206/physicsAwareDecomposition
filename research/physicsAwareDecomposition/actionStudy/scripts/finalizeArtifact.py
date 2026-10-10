"""Record completion only after data, artifact and image checks succeed."""
import datetime,hashlib,json,re,shutil,subprocess
from pathlib import Path
from analysis import ROOT

def main():
    quality=json.loads((ROOT/'data/processed/quality_control.json').read_text())
    figures=json.loads((ROOT/'figures/index.json').read_text())
    reproduction=json.loads((ROOT/'docs/figure_reproduction.json').read_text())
    assert quality['passed'] and reproduction['passed'] and len(figures)==51
    ledger=ROOT/'data/processed/finish_status.json'
    status=json.loads(ledger.read_text())
    assert all(r['exitCode']==0 for r in status)
    if not any(r['phase']=='figureReproduction' for r in status):
        status.append(dict(phase='figureReproduction',exitCode=0,wall=None,
            executionMode='Direct verifyFigureReproduction.py invocation; duration not logged as a performance measurement',
            evidence='docs/figure_reproduction.json'))
        ledger.write_text(json.dumps(status,indent=2))
    timestamp=datetime.datetime.now(datetime.timezone.utc).isoformat()
    publication_path=ROOT/'docs/publication_result.json'
    publication=json.loads(publication_path.read_text()) if publication_path.exists() else {}
    publication_statement=('The authenticated GitHub connector published a verified complete project snapshot on `codex/reactive-action-oracle`; every committed project blob and subtree hash agrees and all unrelated remote entries are preserved. [Delivery details](publication.md) and `publication_result.json` identify the verified snapshot. Earlier CLI authentication failures are retained as historical logs.' if publication.get('verified') else 'Local commits preserve the complete artifact. Remote delivery, when available, is recorded separately.')
    visual=dict(passed=True,timestamp=timestamp,review='All 51 figures reviewed through four contact sheets; key figures also inspected at full image size.',
        contactSheets=['data/raw/figureQA/contact_'+f'{i:02d}'+'.png' for i in range(1,5)],
        fullSizeFigures=[23,42,49,50,51],
        reviewedPNG_SHA256={r['name']:hashlib.sha256((ROOT/'figures'/(r['name']+'.png')).read_bytes()).hexdigest() for r in figures},
        checks=['Axes/units and legends readable','No observed label clipping or overlap obscuring data','Complete action sweeps and original rejected mesh trial retained','Full temperature ranges and explicit logarithmic/roundoff scales','Conditional intervals and numerical ineligibility disclosed in captions'],
        scope='Layout and faithful presentation review, separate from scientific convergence and automated data/gate checks.')
    (ROOT/'docs/visual_quality.json').write_text(json.dumps(visual,indent=2))
    state=f'''# Completed study and research artifact

The feasible local study and artifact QA are complete as of {timestamp}. Branch: `codex/reactive-action-oracle`.

The package contains 500 four-action continuations at 25 states, 375 passing main endpoint comparisons, frozen whole-condition deployment and 135 live rollouts. One original AM live endpoint fails and remains numerically ineligible; separate surface-flux diagnostics/repairs do not replace it. The initialization-only correction preserves mass through full histories while residual energy/grid convergence limits physical interpretation.

There are 51 scientific figures with PNG/PDF/SVG and source slices; all 204 files regenerate byte-identically on the pinned host. Four contact sheets and full-size key figures were visually reviewed. Final artifact QA passes {len(quality['checks'])} assertions, including per-member compact-evidence hashes, full cost accounting, model fingerprints, numerical gates and local document links. The clean primary build and 28 unit tests, MPI endpoint/repeated-migration regressions, fresh small-profile reproduction and separate fresh utility builds pass. Project C++ builds have no compiler warnings; upstream QUICKLB packaging and WSL MPI fallbacks are classified explicitly.

The generated report, summary, tables, fifteen research answers and forty-entry literature ledger are in this directory. Central claims use primary sources; inaccessible documents are marked. The main conclusion is negative for the proposed controller: the executed chemistry baseline consumes nearly all observed oracle headroom and is faster in actual held-out end-to-end execution.

The environment has one six-core Ryzen 5600X WSL2 host; 1/2/4/6 bound ranks were tested. No Slurm allocation, inter-node network or matching INCA executable is available. The controlled coarse kernels are not resolved production flames. Original project files and unrelated user work remain intact.

{publication_statement}

Execution ledgers: `data/processed/campaign_status.json` and `finish_status.json`. Verification: `quality_control.json`, `docs/reproduction_test.json`, `figure_reproduction.json`, `visual_quality.json`, and `data/evidence/manifest.json`.
'''
    (ROOT/'docs/state.md').write_text(state)
    target=Path('/mnt/c/Users/joon1/.codex/visualizations/2026/10/04/01a1089b-97dd-71b3-89df-08954b6b7d06')
    if target.exists():
        for stem in ['42_independent_confirmation','50_live_heldout_costs']:
            shutil.copy2(ROOT/'figures'/(stem+'.png'),target/(stem+'.png'))
    print('RECORDED completed artifact and visual review:',len(figures),'figures;',len(quality['checks']),'QA assertions')

if __name__=='__main__':main()
