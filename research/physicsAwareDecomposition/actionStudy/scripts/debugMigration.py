import json
from caseFactory import *
from mapping import assemble,canonical_directory
from validation import numerical_gate
source=ROOT/'data/raw/pilot_histories_limitedLinear/persistent'
target=ROOT/'data/raw/oracle/persistent/cp4e-05_H80_AM_r0'
for field in ['T','p','U','H2','H2O','N2','chemDeltaT']:
 a=assemble(source,'4e-05',field,256);b=assemble(target,'4e-05',field,256)
 flat=lambda vs:[z for v in vs for z in (v if isinstance(v,tuple) else [v])]
 print('CHECKPOINT',field,max(abs(x-y) for x,y in zip(flat(a),flat(b))),flush=True)
for case in [source,target]:
 args=['mpirun','-np','4','postProcess','-parallel','-func','writeCellCentres','-time','4e-05']
 command(args,case,case/'centres.log')
 centers=assemble(case,'4e-05','C',256)
 expected=[(.02*(i%32+.5)/32,.008*(i//32+.5)/8,.0005) for i in range(256)]
 print('GEOMETRY',case.name,max(abs(a-b) for x,y in zip(centers,expected) for a,b in zip(x,y)),flush=True)
