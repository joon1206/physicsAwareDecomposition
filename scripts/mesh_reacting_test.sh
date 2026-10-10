#!/bin/bash
source /opt/OpenFOAM/OpenFOAM-v2012/etc/bashrc > /dev/null 2>&1
cd /home/joon1206/research/ForFun/cases/reactingTest
python3 /home/joon1206/research/ForFun/scripts/shorten_case.py
blockMesh > /tmp/reacting_mesh.log 2>&1
echo "BLOCKMESH_EXIT=$?" >> /tmp/reacting_mesh.log
tail -6 /tmp/reacting_mesh.log
checkMesh > /tmp/reacting_check.log 2>&1
grep -E 'cells:|faces:' /tmp/reacting_check.log | head -4
