#!/usr/bin/env python3
"""Compute per-processor workload from OpenFOAM decomposition.

Reads processor*/constant/polyMesh/cellProcAddressing and the
cellWeight field to compute sum(weight) per rank.

Usage: workload_balance.py CASE
"""

import sys
from pathlib import Path

case = Path(sys.argv[1])

# Read cellWeight from 0/cellWeight
weight_path = case / "0" / "cellWeight"
with weight_path.open() as f:
    text = f.read()

idx = text.find("internalField")
start = text.find("(", idx)
end = text.find(")", start)
weight_tokens = text[start + 1 : end].split()
weights = [float(t) for t in weight_tokens]
n_cells = len(weights)

print(f"Mesh cells: {n_cells}")
print(f"Total weight: {sum(weights)}")
print(f"Mean weight: {sum(weights) / n_cells}")

# Read per-processor cell addressing
import re

procs = sorted(
    [d for d in case.iterdir() if d.is_dir() and d.name.startswith("processor")],
    key=lambda d: int(d.name.replace("processor", "")),
)

print(f"\n{'Rank':<6}{'Cells':<8}{'Weight':<12}{'Mean':<10}")
print("-" * 40)

rank_weights = []
for proc in procs:
    addr_path = proc / "constant" / "polyMesh" / "cellProcAddressing"
    with addr_path.open() as f:
        atext = f.read()
    aidx = atext.find("(")
    aend = atext.find(")", aidx)
    addr_tokens = atext[aidx + 1 : aend].split()
    cell_ids = [int(t) for t in addr_tokens]

    rank_weight = sum(weights[c] for c in cell_ids)
    rank_weights.append(rank_weight)
    print(
        f"{proc.name:<6}{len(cell_ids):<8}{rank_weight:<12.1f}"
        f"{rank_weight / len(cell_ids):<10.2f}"
    )

mean = sum(rank_weights) / len(rank_weights)
max_w = max(rank_weights)
imbalance = max_w / mean
cv = (sum((w - mean) ** 2 for w in rank_weights) / len(rank_weights)) ** 0.5 / mean

print(f"\nMean rank weight: {mean:.1f}")
print(f"Max rank weight:  {max_w:.1f}")
print(f"Imbalance (max/mean): {imbalance:.4f}")
print(f"CV (std/mean):        {cv:.4f}")
