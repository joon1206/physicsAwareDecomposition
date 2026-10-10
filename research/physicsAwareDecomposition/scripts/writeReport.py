#!/usr/bin/env python3
"""Regenerate the evidence-linked report from its template and summary CSV."""
import csv
from study import ROOT
from pathlib import Path
source=Path(__file__).resolve().parents[1]
text=(source/'docs/report_template.md').read_text()
rows=list(csv.DictReader((ROOT/'data/processed/tight/reactive_summary.csv').open()))
table='| Ranks | Method | gamma | Median wall (s) | Speedup | Pointwise 95% CI | Numerical gate |\n|---:|---|---:|---:|---:|---|---|\n'
for r in rows:
    table+=f"| {r['ranks']} | {r['method']} | {r['gamma'] or 'unweighted'} | {float(r['wallMedian']):.5f} | {float(r['wallSpeedup']):.3f} | [{float(r['wallSpeedupCI_low']):.3f}, {float(r['wallSpeedupCI_high']):.3f}] | {r['partitionValidationPass']} |\n"
sr=list(csv.DictReader((ROOT/'data/processed/synthetic_runtime_summary.csv').open()))
comm='| Distribution | Halo passes/step | Weighted step speedup | Pointwise 95% CI | Weighted interface faces |\n|---|---:|---:|---|---:|\n'
for r in sr:
    if r['nx']=='64' and r['ranks']=='4' and r['kind'] in ['gaussian','uniform'] and r['weighted']=='1':
        comm+=f"| {r['kind']} | {r['haloPasses']} | {float(r['stepSpeedup']):.3f} | [{float(r['stepCI_low']):.3f}, {float(r['stepCI_high']):.3f}] | {r['processorFaces']} |\n"
status='| Component | Status | Evidence |\n|---|---|---|\n'
for component,state,evidence in [
('Repository/source audit','VERIFIED','phaseA_repository_audit.md, machine.json'),
('Rank timers and cost model','IMPLEMENTED / TESTED','source, build logs, final smoke'),
('Synthetic fields / weighted partition','TESTED / MEASURED','13 tests, synthetic.csv, native addressing'),
('Numerical equivalence','VERIFIED within reported scope','field/residual/probe/restart JSON; no temporal flux proof'),
('Reactive benchmark and strong scaling','MEASURED','75 strict trials, scaling.csv, plots 5/6/11'),
('Communication tradeoff','PARTIALLY TESTED','340 CPU/halo runs, native counts/profile; no general crossover'),
('Chemistry predictor','MEASURED / INFERRED','predictor.csv, smoothing.csv, clipping_sensitivity.csv'),
('Live dynamic repartition','FUTURE WORK','decision and unsupported migration claim documented'),
('Literature review and fact checking','VERIFIED to stated access levels','26 source records; claim_verification.md'),
('Reproduction','TESTED smoke; stages executed','fresh smoke/probe data; bounded full wrapper'),
('Publication readiness','PARTIALLY TESTED','local foundation; detailed/multinode/task baseline needed')]:
    status+=f'| {component} | {state} | {evidence} |\n'
text=text.replace('{TABLE_REACTIVE}',table).replace('{SYNTHETIC_COMMS}',comm).replace('{STATUS_TABLE}',status)
if ROOT.resolve()!=source.resolve():
    text='# Fresh reproduction results\n\nMEASURED from this fresh dataset. Historical report/claims stay in the source project; these trial medians will differ.\n\n'+table+'\n\nControlled communication sensitivity:\n\n'+comm+'\n\n'+status
out=ROOT/'docs/final_report.md';out.parent.mkdir(exist_ok=True,parents=True);out.write_text(text)
print(out)
