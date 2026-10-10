from caseFactory import *
from mapping import assemble
source=ROOT/'data/raw/pilot_histories_limitedLinear/persistent'
target=ROOT/'data/raw/oracle/persistent/cp4e-05_H80_AM_r0'
for c in [source,target]:
 command(['mpirun','-np','4','postProcess','-parallel','-func','div(phi)','-time','4e-05'],c,c/'divPhi.log')
a=assemble(source,'4e-05','div(phi)',256);b=assemble(target,'4e-05','div(phi)',256)
print('DIV PHI DIFFERENCE',max(abs(x-y) for x,y in zip(a,b)), 'scale',max(abs(x) for x in a))
