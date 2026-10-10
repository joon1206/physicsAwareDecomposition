#!/usr/bin/env python3
"""Shorten reactingTest to a quick timing smoke test (10 steps)."""
from pathlib import Path
p = Path("/home/joon1206/research/ForFun/cases/reactingTest/system/controlDict")
t = p.read_text()
t = t.replace("endTime         1000;", "endTime         10;")
p.write_text(t)
print("controlDict shortened")
