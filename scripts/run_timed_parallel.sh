#!/bin/bash
source /opt/OpenFOAM/OpenFOAM-v2012/etc/bashrc > /dev/null 2>&1
cd /home/joon1206/research/ForFun/cases/reactingTest
rm -rf processor* phaseTiming
decomposePar -force > /tmp/decomp_react.log 2>&1
grep -E 'Number of cells|Finished decomposition' /tmp/decomp_react.log
mpirun -np 2 /home/joon1206/OpenFOAM/joon1206-v2012/platforms/linux64Gcc63DPInt32Opt/bin/reactingFoamTimed -parallel > /tmp/timed_par.log 2>&1
echo "PAR_EXIT=$?" >> /tmp/timed_par.log
tail -4 /tmp/timed_par.log
echo CSVS
ls -la phaseTiming/ 2>&1 || ls -la processor0/phaseTiming/ 2>&1
