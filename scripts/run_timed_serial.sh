#!/bin/bash
source /opt/OpenFOAM/OpenFOAM-v2012/etc/bashrc > /dev/null 2>&1
cd /home/joon1206/research/ForFun/cases/reactingTest
rm -rf phaseTiming
/home/joon1206/OpenFOAM/joon1206-v2012/platforms/linux64Gcc63DPInt32Opt/bin/reactingFoamTimed > /tmp/timed_run.log 2>&1
echo "RUN_EXIT=$?" >> /tmp/timed_run.log
tail -15 /tmp/timed_run.log
echo CSV_CHECK
ls -la phaseTiming/ 2>&1
head -3 phaseTiming/phaseTimes_rank0.csv 2>&1
