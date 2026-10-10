#!/bin/bash
source /opt/OpenFOAM/OpenFOAM-v2012/etc/bashrc > /dev/null 2>&1
BIN=/home/joon1206/OpenFOAM/joon1206-v2012/platforms/linux64Gcc63DPInt32Opt/bin/reactingFoamTimed
ls -la $BIN
$BIN -help > /tmp/timed_help.log 2>&1
echo "HELP_EXIT=$?" >> /tmp/timed_help.log
head -12 /tmp/timed_help.log
