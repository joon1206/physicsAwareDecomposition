#!/bin/bash
grep -vE 'ExecutionTime|ClockTime|Phase timing|phaseTimes|Starting time loop|Phase timing output|Exec   :|PID    :|Case   :|elements not defined|^$|Host   :|Date   :|Time   :|Build  :|Arch   :' /tmp/log_diff.log | head -30
echo RESIDUAL_CHECK_DONE
grep -c 'Solving for' /tmp/ref_run2.log
grep -c 'Solving for' /tmp/timed_run2.log
