#!/bin/bash
# Build reactingFoamTimed with local make + sysroot compiler wrappers.
# No sudo required. Does not modify /opt/OpenFOAM.
source /opt/OpenFOAM/OpenFOAM-v2012/etc/bashrc > /dev/null 2>&1
chmod +x /home/joon1206/research/ForFun/scripts/wrappers/g++ /home/joon1206/research/ForFun/scripts/wrappers/gcc /home/joon1206/research/ForFun/scripts/wrappers/cc
export PATH=/home/joon1206/research/ForFun/scripts/wrappers:/home/joon1206/local/usr/bin:$PATH
unset C_INCLUDE_PATH
unset CPLUS_INCLUDE_PATH
unset CPATH
cd /home/joon1206/research/ForFun/solvers/reactingFoamTimed
wmake > /tmp/wmake2.log 2>&1
echo "WMAKE_EXIT=$?" >> /tmp/wmake2.log
