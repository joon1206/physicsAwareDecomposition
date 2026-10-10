#!/bin/bash
source /opt/OpenFOAM/OpenFOAM-v2012/etc/bashrc > /dev/null 2>&1
TUT=/opt/OpenFOAM/OpenFOAM-v2012/tutorials/combustion/reactingFoam/laminar/counterFlowFlame2DLTS
DST=/home/joon1206/research/ForFun/cases/reactingTest
rm -rf $DST
mkdir -p $DST
cp -r $TUT/0 $TUT/constant $TUT/system $DST/
grep -E 'endTime|deltaT|writeControl|writeInterval' $DST/system/controlDict
echo BLOCKMESH_SIZE
grep -A3 'blocks' $DST/system/blockMeshDict | head -8
