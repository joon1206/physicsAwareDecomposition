#!/usr/bin/env python3
import csv,os
from pathlib import Path
ROOT=Path(os.environ.get('PAD_OUTPUT_ROOT',Path(__file__).resolve().parents[1]))
for p in (ROOT/'data/processed').rglob('*.csv'):
    if p.name not in ['reactive_summary.csv','instrumentation_overhead.csv','scaling.csv','smoothing.csv','synthetic_runtime_summary.csv','transient_summary.csv','numerical_norms.csv']:continue
    rows=list(csv.DictReader(p.open()))
    out=ROOT/'tables'/p.relative_to(ROOT/'data/processed').with_suffix('.md');out.parent.mkdir(exist_ok=True,parents=True)
    keys=list(rows[0])
    s='| '+' | '.join(keys)+' |\n| '+' | '.join('---' for _ in keys)+' |\n'
    for row in rows:
        def fmt(x):
            try:return f'{float(x):.5g}'
            except ValueError:return x
        s+='| '+' | '.join(fmt(row[k]) for k in keys)+' |\n'
    out.write_text(s)
