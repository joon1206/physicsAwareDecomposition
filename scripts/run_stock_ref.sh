#!/bin/bash
source /opt/OpenFOAM/OpenFOAM-v2012/etc/bashrc > /dev/null 2>&1
SRC=/home/joon1206/research/ForFun/cases/reactingTest
REF=/home/joon1206/research/ForFun/cases/reactingRef
rm -rf $REF
mkdir -p $REF
cp -r $SRC/0 $SRC/constant $SRC/system $REF/
cd $REF
reactingFoam > /tmp/ref_run.log 2>&1
echo "REF_EXIT=$?" >> /tmp/ref_run.log
tail -4 /tmp/ref_run.log
ls -d [0-9]* 2>/dev/null
