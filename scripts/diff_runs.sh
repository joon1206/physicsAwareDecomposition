#!/bin/bash
diff -r -x uniform /home/joon1206/research/ForFun/cases/reactingRef/10 /home/joon1206/research/ForFun/cases/reactingTest/10 > /tmp/field_diff.log 2>&1
echo "DIFF_EXIT=$?"
wc -l /tmp/field_diff.log
head -20 /tmp/field_diff.log
echo LOG_DIFF
diff /tmp/ref_run2.log /tmp/timed_run2.log > /tmp/log_diff.log 2>&1
echo "LOGDIFF_EXIT=$?"
grep -vE 'ExecutionTime|ClockTime|Phase timing|phaseTimes|^$|Starting time loop|Phase timing output' /tmp/log_diff.log | head -20
