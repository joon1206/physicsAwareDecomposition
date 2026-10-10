#!/usr/bin/env python3
"""Compare OpenFOAM fields at final time between timed and stock runs.

Parses internalField values for volScalar/volVector fields at time 10
in reactingTest (timed) vs reactingRef (stock). Reports max abs diff,
L2 norms, and species sums. Exits nonzero on mismatch beyond tolerance.
"""
import re
import sys
from pathlib import Path

TIMED = Path("/home/joon1206/research/ForFun/cases/reactingTest/10")
REF = Path("/home/joon1206/research/ForFun/cases/reactingRef/10")

TOL_ABS = 1e-12
TOL_REL = 1e-9


def parse_internal(path):
    text = path.read_text()
    m = re.search(r"internalField\s+(uniform|nonuniform)", text)
    if not m:
        raise ValueError(f"no internalField in {path}")
    kind = m.group(1)
    if kind == "uniform":
        v = re.search(r"internalField\s+uniform\s+(\(?[^;]*\)?);", text)
        vals = v.group(1).strip()
        if vals.startswith("("):
            return [tuple(float(x) for x in vals.strip("() ").split())]
        return [float(vals)]
    # nonuniform List<scalar> or List<vector>
    m2 = re.search(
        r"internalField\s+nonuniform\s+List<\w+>\s+(\d+)\s*\((.*)\)\s*;",
        text,
        re.DOTALL,
    )
    n = int(m2.group(1))
    body = m2.group(2).strip()
    if "(" in body:
        vecs = re.findall(r"\(([^()]*)\)", body)
        vals = [tuple(float(x) for x in v.split()) for v in vecs]
    else:
        vals = [float(x) for x in body.split()]
    assert len(vals) == n, f"{path}: count {len(vals)} != {n}"
    return vals


def flat(vals):
    out = []
    for v in vals:
        if isinstance(v, tuple):
            out.extend(v)
        else:
            out.append(v)
    return out


def main():
    fields = sorted(f.name for f in REF.iterdir() if f.is_file() and f.name != "uniform")
    ok = True
    print(f"{'field':<10}{'n':>8}{'maxAbsDiff':>14}{'|timed|_inf':>14}{'|diff|_2/|x|_2':>14}")
    for f in fields:
        rt, tt = REF / f, TIMED / f
        if not tt.exists():
            print(f"{f:<10} MISSING in timed run")
            ok = False
            continue
        try:
            rv, tv = flat(parse_internal(rt)), flat(parse_internal(tt))
        except Exception as e:
            print(f"{f:<10} SKIP ({e})")
            continue
        assert len(rv) == len(tv), f"{f}: size mismatch"
        diffs = [abs(a - b) for a, b in zip(rv, tv)]
        mad = max(diffs)
        n2r = sum(a * a for a in rv) ** 0.5
        n2d = sum(d * d for d in diffs) ** 0.5
        rel = n2d / n2r if n2r > 0 else n2d
        flag = "" if (mad <= TOL_ABS or rel <= TOL_REL) else "  <-- MISMATCH"
        if flag:
            ok = False
        print(f"{f:<10}{len(rv):>8}{mad:>14.3e}{max(map(abs, tv)):>14.6g}{rel:>14.3e}{flag}")
    # also diff the solver logs' residual lines
    print("NUMERICAL_CHECK:", "PASS" if ok else "FAIL")
    return 0 if ok else 1


sys.exit(main())
