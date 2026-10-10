#!/usr/bin/env python3
"""Generate a synthetic cell-weight field with a left-half hotspot.

For a structured 20x20x1 cavity mesh, cells are ordered with x fastest,
then y. We assign weight hotspot_value to cells with x < x_fraction.

Usage: generate_hotspot_weights.py CASE [hotspot_value] [x_fraction]
"""

import sys
from pathlib import Path

case = Path(sys.argv[1])
hotspot_value = float(sys.argv[2]) if len(sys.argv) > 2 else 10.0
x_fraction = float(sys.argv[3]) if len(sys.argv) > 3 else 0.5

# Read cell count from the owner file
owner_path = case / "constant" / "polyMesh" / "owner"
with owner_path.open() as f:
    text = f.read()

# Find the owner list
idx = text.find("owner")
start = text.find("(", idx)
end = text.find(")", start)
owner_tokens = text[start + 1 : end].split()
n_cells = max(int(t) for t in owner_tokens) + 1

# Structured 20x20x1 mesh: cell index = i + 20*j
nx = 20
ny = 20

weights = []
for celli in range(n_cells):
    i = celli % nx
    x = i / (nx - 1) if nx > 1 else 0.0
    if x < x_fraction:
        weights.append(hotspot_value)
    else:
        weights.append(1.0)

total = sum(weights)
print(f"Cells: {n_cells}")
print(f"Total weight: {total}")
print(f"Hotspot cells (x < {x_fraction}): {sum(1 for w in weights if w > 1)}")
print(f"Mean weight: {total / n_cells}")

# Write OpenFOAM volScalarField
out = case / "0" / "cellWeight"
with out.open("w") as f:
    f.write("/*--------------------------------*- C++ -*----------------------------------*\\\n")
    f.write("| =========                 |                                                 |\n")
    f.write("| \\\\      /  O peration   | OpenFOAM: The Open Source CFD Toolbox           |\n")
    f.write("| \\\\  /   A nd           | Version:  v2012                                 |\n")
    f.write("|  \\\\/    M anipulation  | Website:  www.openfoam.com                      |\n")
    f.write("\\*---------------------------------------------------------------------------*/\n")
    f.write("FoamFile\n{\n")
    f.write("    version     2.0;\n")
    f.write("    format      ascii;\n")
    f.write("    class       volScalarField;\n")
    f.write("    object      cellWeight;\n")
    f.write("}\n")
    f.write("// * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * //\n\n")
    f.write("dimensions      [0 0 0 0 0 0 0];\n\n")
    f.write("internalField   nonuniform List<scalar>\n")
    f.write(f"{n_cells}\n(\n")
    for w in weights:
        f.write(f"    {w}\n")
    f.write(")\n;\n\n")
    f.write("boundaryField\n{\n")
    f.write("    movingWall\n    {\n        type            zeroGradient;\n    }\n\n")
    f.write("    fixedWalls\n    {\n        type            zeroGradient;\n    }\n\n")
    f.write("    frontAndBack\n    {\n        type            empty;\n    }\n")
    f.write("}\n\n")
    f.write("// ************************************************************************* //\n")

print(f"Wrote {out}")
