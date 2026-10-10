#!/bin/bash
source /opt/OpenFOAM/OpenFOAM-v2012/etc/bashrc > /dev/null 2>&1
cd /home/joon1206/research/ForFun/cases/reactingTest
ls processor0/phaseTiming/ processor1/phaseTiming/
echo RANK0
cat processor0/phaseTiming/phaseTimes_rank0.csv
echo RANK1
cat processor1/phaseTiming/phaseTimes_rank1.csv
