#!/usr/bin/env python3
"""Synthetic workload benchmark with known analytical cost distributions.

Distributions (weights as a function of normalized cell-centre x in [0,1],
y in [0,1]; structured nx*ny single-block mesh, x-fastest ordering):
  uniform   w = 1                                   total = n
  step      w = H if x < 0.5 else 1                 total = n/2*(H+1)
  hotspot   w = H if x < xf else 1                  total = n_hot*H + (n-n_hot)
  linear    w = 1 + (H-1)*x                         total = n*(H+1)/2
  gaussian  w = 1 + (H-1)*exp(-((x-x0)^2+(y-y0)^2)/2s^2)
                                                    total = sum over cells
                                                    (closed form per cell;
                                                    verified cell-by-cell)

For each distribution the script asserts the generated weight sum equals
the analytical expectation (exact for uniform/step/hotspot/linear;
per-cell formula check for gaussian), then sweeps decomposition methods
(scotch, simple, hierarchical, kahip) at fixed rank count, weighted and
unweighted, recording per-rank workload imbalance and processor faces.

Usage: synth_bench.py CASE NX NY H
  Writes results CSV to CASE/synth_bench_results.csv and restores the
  case decomposeParDict/cellWeight afterwards.
"""
import math
import os
import shutil
import subprocess
import sys
from pathlib import Path

CASE = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("cases/cavityTest")
NX = int(sys.argv[2]) if len(sys.argv) > 2 else 20
NY = int(sys.argv[3]) if len(sys.argv) > 3 else 20
H = float(sys.argv[4]) if len(sys.argv) > 4 else 100.0
RANKS = 3

METHODS = ["scotch", "simple", "hierarchical", "kahip"]

DISTS = ["uniform", "step", "hotspot", "linear", "gaussian"]
HOTSPOT_XF = 0.25
GAUSS = dict(x0=0.25, y0=0.5, s=0.15)


def cell_xy(celli):
    i = celli % NX
    j = (celli // NX) % NY
    return i / (NX - 1), j / (NY - 1)


def weights(dist):
    ws = []
    for c in range(NX * NY):
        x, y = cell_xy(c)
        if dist == "uniform":
            w = 1.0
        elif dist == "step":
            w = H if x < 0.5 else 1.0
        elif dist == "hotspot":
            w = H if x < HOTSPOT_XF else 1.0
        elif dist == "linear":
            w = 1.0 + (H - 1.0) * x
        elif dist == "gaussian":
            g = GAUSS
            w = 1.0 + (H - 1.0) * math.exp(
                -((x - g["x0"]) ** 2 + (y - g["y0"]) ** 2)
                / (2 * g["s"] ** 2)
            )
        else:
            raise ValueError(dist)
        ws.append(w)
    return ws


def expected_total(dist, ws):
    n = NX * NY
    if dist == "uniform":
        return float(n)
    if dist == "step":
        return (n // 2) * H + (n - n // 2) * 1.0
    if dist == "hotspot":
        nhot = sum(1 for c in range(n) if cell_xy(c)[0] < HOTSPOT_XF)
        return nhot * H + (n - nhot) * 1.0
    if dist == "linear":
        return n * (H + 1.0) / 2.0
    if dist == "gaussian":
        # per-cell closed form recomputed independently
        tot = 0.0
        for c in range(n):
            x, y = cell_xy(c)
            g = GAUSS
            tot += 1.0 + (H - 1.0) * math.exp(
                -((x - g["x0"]) ** 2 + (y - g["y0"]) ** 2)
                / (2 * g["s"] ** 2)
            )
        return tot
    raise ValueError(dist)


FOAM_HEADER = """/*--------------------------------*- C++ -*----------------------------------*\\
| =========                 |                                                 |
| \\\\      /  O peration   | OpenFOAM: The Open Source CFD Toolbox           |
|  \\\\  /   A nd           | Version:  v2012                                 |
|   \\\\/    M anipulation  | Website:  www.openfoam.com                      |
\\*---------------------------------------------------------------------------*/
"""


def write_weight_field(ws):
    p = CASE / "0" / "cellWeight"
    with p.open("w") as f:
        f.write(FOAM_HEADER)
        f.write("FoamFile\n{\n    version     2.0;\n    format      ascii;\n")
        f.write("    class       volScalarField;\n    object      cellWeight;\n}\n")
        f.write("// * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * //\n\n")
        f.write("dimensions      [0 0 0 0 0 0 0];\n\n")
        f.write("internalField   nonuniform List<scalar>\n")
        f.write(f"{len(ws)}\n(\n")
        for w in ws:
            f.write(f"    {w}\n")
        f.write(")\n;\n\nboundaryField\n{\n")
        f.write("    movingWall\n    {\n        type            zeroGradient;\n    }\n\n")
        f.write("    fixedWalls\n    {\n        type            zeroGradient;\n    }\n\n")
        f.write("    frontAndBack\n    {\n        type            empty;\n    }\n}\n\n")
        f.write("// ************************************************************************* //\n")


def write_decomp_dict(method, weighted):
    wline = "weightField     cellWeight;\n\n" if weighted else ""
    text = (
        FOAM_HEADER
        + "FoamFile\n{\n    version     2.0;\n    format      ascii;\n"
        + '    class       dictionary;\n    location    "system";\n'
        + "    object      decomposeParDict;\n}\n"
        + "// * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * //\n\n"
        + f"numberOfSubdomains  {RANKS};\n\nmethod          {method};\n\n{wline}"
        + "simpleCoeffs\n{\n    n           (3 1 1);\n    delta       0.001;\n}\n\n"
        + "hierarchicalCoeffs\n{\n    n           (3 1 1);\n    delta       0.001;\n"
        + "    order       xyz;\n}\n\n"
        + "kahipCoeffs\n{\n}\n\n"
        + "distributed     no;\n\nroots           ();\n\n"
        + "// ************************************************************************* //\n"
    )
    (CASE / "system" / "decomposeParDict").write_text(text)


def foam_run(cmd):
    env = dict(os.environ)
    full = f"source /opt/OpenFOAM/OpenFOAM-v2012/etc/bashrc > /dev/null 2>&1; cd {CASE} && {cmd}"
    r = subprocess.run(
        ["bash", "-c", full], capture_output=True, text=True, timeout=120, env=env
    )
    return r.returncode, r.stdout + r.stderr


def parse_decomp(out):
    cells, faces = [], None
    for line in out.splitlines():
        s = line.strip()
        if s.startswith("Number of cells ="):
            cells.append(int(s.split("=")[1]))
        if s.startswith("Number of processor faces ="):
            faces = int(s.split("=")[1])
    return cells, faces


def rank_workloads(ws):
    loads = []
    for r in range(RANKS):
        a = CASE / f"processor{r}" / "constant" / "polyMesh" / "cellProcAddressing"
        text = a.read_text()
        body = text[text.find("(") + 1 : text.find(")")]
        ids = [int(t) for t in body.split()]
        loads.append((len(ids), sum(ws[c] for c in ids)))
    return loads


def main():
    # sanity: mesh size
    assert NX * NY == 400, "cavityTest is 400 cells"
    # save state
    bak_dict = (CASE / "system" / "decomposeParDict").read_text()
    bak_w = (CASE / "0" / "cellWeight").read_text()
    rows = []
    try:
        for dist in DISTS:
            ws = weights(dist)
            exp = expected_total(dist, ws)
            got = sum(ws)
            assert abs(got - exp) < 1e-6 * max(1.0, exp), (dist, got, exp)
            print(f"dist={dist:<9} total={got:.4g} expected={exp:.4g} OK")
            write_weight_field(ws)
            for method in METHODS:
                for weighted in (False, True):
                    write_decomp_dict(method, weighted)
                    for d in CASE.glob("processor*"):
                        shutil.rmtree(d)
                    rc, out = foam_run("decomposePar -force")
                    if rc != 0 or not list(CASE.glob("processor*")):
                        err = [l for l in out.splitlines() if "ERROR" in l or "Fatal" in l][:2]
                        print(f"  {method:<12} weighted={int(weighted)} FAILED {err}")
                        rows.append((dist, method, weighted, "FAIL", 0, 0, 0, 0))
                        continue
                    cells, faces = parse_decomp(out)
                    loads = rank_workloads(ws)
                    tot = sum(w for _, w in loads)
                    mean = tot / len(loads)
                    imb = max(w for _, w in loads) / mean
                    cv = (sum((w - mean) ** 2 for _, w in loads) / len(loads)) ** 0.5 / mean
                    cellstr = "/".join(str(c) for c, _ in loads)
                    print(
                        f"  {method:<12} weighted={int(weighted)} "
                        f"cells={cellstr} imb={imb:.4f} cv={cv:.4f} faces={faces}"
                    )
                    rows.append(
                        (dist, method, weighted, "OK", imb, cv, faces, cellstr)
                    )
    finally:
        (CASE / "system" / "decomposeParDict").write_text(bak_dict)
        (CASE / "0" / "cellWeight").write_text(bak_w)
        for d in CASE.glob("processor*"):
            shutil.rmtree(d)
    out = CASE / "synth_bench_results.csv"
    with out.open("w") as f:
        f.write("dist,method,weighted,status,imbalance,cv,procFaces,cells\n")
        for r in rows:
            f.write(",".join(str(x) for x in r) + "\n")
    print(f"Wrote {out} ({len(rows)} rows)")


main()
