#!/bin/bash
source /opt/OpenFOAM/OpenFOAM-v2012/etc/bashrc > /dev/null 2>&1
cd /home/joon1206/research/ForFun
python3 scripts/force_write.py
rm -rf cases/reactingTest/phaseTiming
cd cases/reactingTest
rm -rf 10
/home/joon1206/OpenFOAM/joon1206-v2012/platforms/linux64Gcc63DPInt32Opt/bin/reactingFoamTimed > /tmp/timed_run2.log 2>&1
echo "TIMED_EXIT=$?" >> /tmp/timed_run2.log
cd ../reactingRef
rm -rf 10
reactingFoam > /tmp/ref_run2.log 2>&1
echo "REF_EXIT=$?" >> /tmp/ref_run2.log
echo TIMED_TIMES
ls -d /home/joon1206/research/ForFun/cases/reactingTest/[0-9]* 2>/dev/null
echo REF_TIMES
ls -d /home/joon1206/research/ForFun/cases/reactingRef/[0-9]* 2>/dev/null
