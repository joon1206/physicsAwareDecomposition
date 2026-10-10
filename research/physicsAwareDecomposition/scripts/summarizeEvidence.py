#!/usr/bin/env python3
"""Derived evidence summary and rank work/throughput, from retained data."""
import csv,json,math,statistics
from study import ROOT
from analyzeTiming import timing,csvout
from foamio import read_field,proc_metrics
P=ROOT/'data/processed'
rows=list(csv.DictReader((P/'tight/reactive_summary.csv').open()))
base=next(r for r in rows if r['ranks']=='4' and r['method']=='scotch' and not r['gamma'])
best=json.loads((P/'tight/key_results.json').read_text())['best']
training=json.loads((ROOT/'data/raw/training/manifest.json').read_text())
saving=(float(base['steadyMaxRankMedian'])-best['steadyMaxRankMedian'])/69
construct=list(csv.DictReader((P/'clipping_sensitivity.csv').open()))[0]
inventory={}
d=json.loads((P/'tight/partition_validation_p4_scotch_g1.json').read_text())
for key in ['totalMassKg','sensiblePlusKineticEnergyJ','QdotIntegralW']:
    a=d['referenceDiagnostics'][key];b=d['testDiagnostics'][key]
    inventory[key]={'reference':a,'test':b,'absoluteDifference':abs(a-b),'relativeDifference':abs(a-b)/abs(a)}
out={'status':'DERIVED from measured data','best':best,'steadySavingPerIteration':saving,
 'coldCostAccounting':{'trainingWall':training['solverWall'],'weightedDecompositionWall':best['decompositionMedian'],'weightConstructionMedian':float(construct['constructionMedian']),
    'coldSetupBreakEvenIterations':math.ceil((training['solverWall']+best['decompositionMedian']+float(construct['constructionMedian']))/saving),
    'incrementalDecompositionOnlyBreakEvenIterations':math.ceil((best['decompositionMedian']-float(base['decompositionMedian'])+float(construct['constructionMedian']))/saving),
    'limitations':'Indicative static restart arithmetic; training was an earlier unbound serial trace; no live migration or physical-time horizon measured.'},
 'nativeInventoryComparison':inventory}
(P/'evidence_summary.json').write_text(json.dumps(out,indent=2)+'\n')
rankRows=[];through=[]
for g in ['None','1']:
    case=ROOT/f'data/raw/reactiveTight/p4_scotch_g{g}_r0'
    qdot=read_field(case/'160/Qdot',4000);threshold=.01*max(qdot)
    t=timing(case,4,10)
    for part in proc_metrics(case):
        rankRows.append({'gamma':g,'rank':part['rank'],'nCells':part['nCells'],'processorFaces':part['processorFaces'],'nNeighbours':part['nNeighbours'],
            'reactingCells':sum(qdot[i]>threshold for i in part['ids']),'criterion':'Qdot > 1 percent global maximum, diagnostic only',
            'chemistryWallSum':t['phaseTotals']['chemistryWall'][part['rank']],'stepWallSum':t['phaseTotals']['stepWall'][part['rank']]})
    through.append({'gamma':g,'steadySteps':t['steadySteps'],'iterationThroughputMaxRankProxy':69/t['steadyMaxRankSum'],
      'chemistryCellVisitThroughputMaxRankProxy':4000*69/max(t['phaseTotals']['chemistryWall']),
      'meaning':'Offline exclusive timer throughput; cell visits, not ODE RHS evaluations; no global barrier.'})
csvout(P/'reacting_cells_by_rank.csv',rankRows);csvout(P/'throughput.csv',through)
print(json.dumps(out,indent=2))
