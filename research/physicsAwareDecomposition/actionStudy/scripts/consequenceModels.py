"""Explanatory transport model and measured migration break-even diagnostics.

Post-partition geometry is available retrospectively, not a free online feature.
MPI-call time is not treated as independently identifiable network time.
"""
import collections,json,math,statistics
from analysis import ROOT,TRAIN,TEST,ridge,predict
from mapping import metrics as partition_metrics

def main():
    raw=json.loads((ROOT/'data/processed/oracle_raw.json').read_text());groups=collections.defaultdict(list)
    for row in raw:groups[(row['regime'],row['checkpoint'],row['horizonSteps'],row['action'])].append(row)
    def phase(row):
        return statistics.mean(sum(rank[k] for k in ['speciesWall','momentumWall','energyWall','pressureWall']) for rank in row['phaseRankSums'].values())/row['horizonSteps']
    points=[]
    for key,rows in groups.items():
        if key[-1] not in ['AM','AH']:continue
        baseline=groups[key[:-1]+('A0',)];f=rows[0]['currentFeatures'];H=key[2]
        cells=[p['nCells'] for r in rows for p in r['parts']]
        x=[statistics.median(r['processorFaces'] for r in rows)/f['processorFaces'],
           statistics.pstdev(cells)/statistics.mean(cells),f['chemistryFraction'],f['nSpecies']]
        transport=statistics.median(phase(r) for r in rows)-statistics.median(phase(r) for r in baseline)
        solver_saved=statistics.median(r['solverWall'] for r in baseline)-statistics.median(r['solverWall'] for r in rows)
        setup=statistics.median(r['migrationWall']+r['decisionWall'] for r in rows)
        points.append(dict(regime=key[0],checkpoint=key[1],H=H,action=key[-1],x=x,
            transportDeltaPerStep=transport,solverSavedPerStep=solver_saved/H,setup=setup,
            estimatedBreakEvenSteps=setup/(solver_saved/H) if solver_saved>0 else None,
            lifetimeSteps=f['lifetimeSteps'],Pi=f['lifetimeSteps']/(setup/(solver_saved/H)) if solver_saved>0 and setup>0 else None))
    train=[r for r in points if r['regime'] in TRAIN];model=ridge([r['x'] for r in train],[r['transportDeltaPerStep'] for r in train])
    for row in points:row['predictedTransportDeltaPerStep']=predict(model,row['x'])
    metrics={}
    for split,cases in [('train',TRAIN),('test',TEST)]:
        group=[r for r in points if r['regime'] in cases];errors=[r['predictedTransportDeltaPerStep']-r['transportDeltaPerStep'] for r in group]
        metrics[split]=dict(n=len(errors),MAE=statistics.mean(abs(v) for v in errors),RMSE=math.sqrt(statistics.mean(v*v for v in errors)))
    # Independently profiled durations allow an explanatory MPI-call model,
    # while retaining the distinction between time in MPI and wire transfer.
    profiles=json.loads((ROOT/'data/processed/profiles.json').read_text())+json.loads((ROOT/'data/processed/mpi_consequence_profiles.json').read_text())
    for row in profiles:
        if 'parts' not in row:
            path=ROOT/row['path'] if 'path' in row else ROOT/f"data/raw/{'profilesOn' if row['profile'] else 'profilesOff'}/{row['regime']}/cp4e-05_H80_{row['action']}_r{row['repeat']}"
            parts=partition_metrics(path);row['parts']=[{k:v for k,v in p.items() if k!='ids'} for p in parts]
            row['processorFaces']=sum(p['processorFaces'] for p in parts)/2
    profiled={(r['regime'],r['action'],r['repeat']):r for r in profiles if r['profile']}
    mpi_points=[]
    def mpi_seconds(row):return statistics.mean(float(r['callSeconds']) for r in row['MPI'])/row['horizonSteps']
    for (condition,action,repeat),row in profiled.items():
        if action not in ['AM','AH']:continue
        reference=profiled[condition,'A0',repeat];f=row['currentFeatures'];counts=[p['nCells'] for p in row['parts']]
        x=[row['processorFaces']/reference['processorFaces'],statistics.pstdev(counts)/statistics.mean(counts),
           max(p['nNeighbours'] for p in row['parts']),float(action=='AH'),f['chemistryFraction']]
        mpi_points.append(dict(regime=condition,action=action,repeat=repeat,x=x,
            MPICallDeltaPerStep=mpi_seconds(row)-mpi_seconds(reference)))
    mpi_train=[r for r in mpi_points if r['regime'] in TRAIN]
    mpi_model=ridge([r['x'] for r in mpi_train],[r['MPICallDeltaPerStep'] for r in mpi_train])
    mpi_metrics={}
    for row in mpi_points:row['predictedMPICallDeltaPerStep']=predict(mpi_model,row['x'])
    for split,cases in [('train',TRAIN),('test',TEST)]:
        group=[r for r in mpi_points if r['regime'] in cases];errors=[r['predictedMPICallDeltaPerStep']-r['MPICallDeltaPerStep'] for r in group]
        mpi_metrics[split]=dict(n=len(errors),conditions=sorted({r['regime'] for r in group}),
            MAE=statistics.mean(abs(v) for v in errors),RMSE=math.sqrt(statistics.mean(v*v for v in errors)))
    result=dict(model=model,points=points,metrics=metrics,MPIModel=dict(model=mpi_model,points=mpi_points,metrics=mpi_metrics,
        features=['postpartitionFaceRatio','postpartitionCellCV','maximumNeighbours','hybridChemistryTasks','originalChemistryFraction'],
        limitation='Two training conditions and one held-out moving condition; repeated clocks do not increase the independent physical sample count. Post-partition inputs are paid observations, not free online features. MPI calls include waits, collectives and scheduling; pure network-transfer cost is not identified.'),
        scope='Explanatory rank-mean cumulative transport/pressure phase duration, including synchronization effects; not additive pure network time.',
        onlineLimitation='Post-action processor faces and cell imbalance require a candidate partition; their availability and computation are not free. This model is not deployed by the frozen controller.',
        breakEvenLimitation='C/setup divided by observed average solver savings per step assumes the observed average persists; None means no positive savings, not infinite-horizon empirical proof.')
    (ROOT/'data/processed/consequence_models.json').write_text(json.dumps(result,indent=2))
    print('ANALYZED consequence model',metrics)

if __name__=='__main__':main()
