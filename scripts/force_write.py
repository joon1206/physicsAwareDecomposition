#!/usr/bin/env python3
"""Force field write at final step for numerical comparison."""
from pathlib import Path
for case in ("reactingTest", "reactingRef"):
    p = Path(f"/home/joon1206/research/ForFun/cases/{case}/system/controlDict")
    t = p.read_text()
    t = t.replace("writeControl    runTime;", "writeControl    timeStep;")
    t = t.replace("writeInterval   20;", "writeInterval   10;")
    p.write_text(t)
    print(f"{case} updated")
