"""Replay fixed observed ownership and validate optional face-flux preservation.

The failed original live trial remains rejected. These are separate diagnostic
controls, with preparation/restoration process costs explicitly recorded.
"""
import csv,json,math,time
from caseFactory import ROOT,PAD,command,header,set_control,solve,latest_time,set_chemistry
from oracle import copy_checkpoint,local_weights
from mapping import ids,save_ids,assemble,canonical_directory
from validation import numerical_gate

CP='0.0002'
MPI=['mpirun','--bind-to','core','--map-by','core','--nooversubscribe','-np','4']

def audit(case):
    return command(MPI+['padFluxAudit','-parallel','-time',CP],case,case/'fluxAudit.log')

def face_map(case):
    result={}
    for path in case.glob('processor[0-9]*/'+CP+'/faceAudit.csv'):
        for row in csv.DictReader(path.open()):
            coords=[float(row[k]) for k in ['x','y','z']]
            if abs(coords[0]-.02)<1e-12:coords[0]=0.
            area=[float(row[k]) for k in ['sx','sy','sz']]
            axis=max(range(3),key=lambda a:abs(area[a]))
            key=tuple(round(x,12) for x in coords)+(axis,)
            value=float(row['phi'])*math.copysign(1.,area[axis])
            result.setdefault(key,[]).append(dict(value=value,patch=row['patch'],type=row['type']))
    return result

def face_comparison(reference,candidate):
    a,b=face_map(reference),face_map(candidate)
    assert set(a)==set(b),'physical face identities changed'
    errors=[]
    for key in a:
        av=sum(r['value'] for r in a[key])/len(a[key])
        for row in b[key]:
            error=abs(row['value']-av)
            if error>1e-10:
                errors.append(dict(face=key,reference=av,candidate=row['value'],error=error,
                                   patch=row['patch'],type=row['type'],
                                   signReversal=abs(row['value']+av)<1e-10))
    return dict(physicalFaces=len(a),mismatches=len(errors),
                maxError=max([r['error'] for r in errors],default=0.),
                reversed=sum(r['signReversal'] for r in errors),examples=sorted(errors,key=lambda r:-r['error'])[:20])

def main():
    command(['bash',PAD/'actionStudy/scripts/buildFluxState.sh'],PAD,
            ROOT/'data/raw/build/fluxStateBuildDriver.log',timeout=300)
    records=[];face_records=[]
    for repeat in range(3):
        reference=ROOT/f'data/raw/fluxDiagnosis/A0_r{repeat}'
        observed=ROOT/f'data/raw/fluxDiagnosis/AM_r{repeat}'
        audit(reference);audit(observed)
        fc=face_comparison(reference,observed);face_records.append(dict(repeat=repeat,**fc))
        print('OBSERVED FACE AUDIT',repeat,fc['mismatches'],fc['reversed'],fc['maxError'],flush=True)
        observed_ids=json.loads((observed/'globalCellIds.json').read_text())
        owners={i:int(rank[9:]) for rank,local in observed_ids.items() for i in local}
        info=json.loads((reference/'case.json').read_text())
        fields=['T','p','U','Qdot']+info['species']
        final_reference=ROOT/f'data/raw/live/heldoutMoving_A0_r{repeat}'
        original=ROOT/f'data/raw/live/heldoutMoving_AM_r{repeat}'
        for preserve in [False,True]:
            label='preserved' if preserve else 'unprotected'
            target=ROOT/f'data/raw/fluxRepair/r{repeat}_{label}'
            manifest=target/'manifest.json'
            if manifest.exists():
                old=json.loads(manifest.read_text())
                if not preserve or old.get('utilityProtocol')=='physical face snapshot v2':
                    records.append(old);continue
            if target.exists():
                retained=ROOT/'data/raw/fluxRepairRejected'
                retained.mkdir(exist_ok=True)
                target.rename(retained/(target.name+'_'+str(time.time_ns())))
            copy_checkpoint(reference,target,CP)
            set_chemistry(target,'AM',trace=0)
            setup_start=time.perf_counter()
            local_weights(target,CP,[1.]*256)
            for p in target.glob('processor[0-9]*'):
                identity=ids(target,p)
                text=header('manualCellOwners','labelList')+str(len(identity))+'\n(\n'
                text+='\n'.join(str(owners[i]) for i in identity)+'\n)\n'
                (p/'constant/manualCellOwners').write_text(text)
            (target/'system/decomposeParDict').write_text(
                header('decomposeParDict','dictionary')+'numberOfSubdomains 4;\nmethod manual;\nmanualCoeffs { dataFile manualCellOwners; }\n')
            setup=time.perf_counter()-setup_start
            prepare=command(MPI+['padFluxState','-parallel','-time',CP],target,target/'fluxPrepare.log') if preserve else 0.
            migration=command(MPI+['redistributeParPAD','-parallel','-overwrite','-time',CP],target,target/'redistribute.log')
            save_ids(target,CP)
            actual={i:int(rank[9:]) for rank,local in json.loads((target/'globalCellIds.json').read_text()).items() for i in local}
            assert actual==owners,'manual map must match the observed ownership exactly'
            restore=command(MPI+['padFluxState','-restore','-parallel','-time',CP],target,target/'fluxRestore.log') if preserve else 0.
            audit(target)
            flux=max(abs(a-b) for a,b in zip(assemble(reference,CP,'padDivPhi',256),assemble(target,CP,'padDivPhi',256)))
            face=face_comparison(reference,target)
            input_gate=numerical_gate(*[canonical_directory(p,CP,fields,256) for p in [reference,target]],info)
            assert input_gate['pass_']
            set_control(target,start=float(CP),steps=40,dt=info['dt'],restart_state=True)
            solver=solve(target,4,exe='reactingFoamPADRestart',timeout=300)
            end=latest_time(target,True)
            gate=numerical_gate(*[canonical_directory(p,end,fields,256) for p in [final_reference,target]],info)
            reproduction=numerical_gate(*[canonical_directory(p,end,fields,256) for p in [original,target]],info)
            row=dict(repeat=repeat,preserveFlux=preserve,utilityProtocol='physical face snapshot v2',path=str(target.relative_to(ROOT)),exactObservedOwnership=True,
                     decisionWall=setup,prepareWall=prepare,migrationWall=migration,restoreWall=restore,solverWall=solver,
                     totalWall=setup+prepare+migration+restore+solver,fluxDivergenceLinf=flux,faceComparison=face,
                     inputGate=input_gate,gate=gate,originalEndpointComparison=reproduction,
                     scope='Separate fixed-partition diagnostic; preparation and restoration subprocess wall charged. Original failed live trial and eligibility unchanged; no controller retraining or performance-result replacement.')
            manifest.write_text(json.dumps(row,indent=2));records.append(row)
            print('FLUX REPAIR',repeat,label,'div',flux,'T',gate['fields']['T']['Linf'],'gate',gate['pass_'],flush=True)
    repaired=[]
    for repeat in range(3):
        target=ROOT/f'data/raw/fluxRepair/observedZeroRepair_r{repeat}'
        manifest=target/'manifest.json'
        if manifest.exists():repaired.append(json.loads(manifest.read_text()));continue
        source=ROOT/f'data/raw/fluxDiagnosis/AM_r{repeat}'
        reference=ROOT/f'data/raw/live/heldoutMoving_A0_r{repeat}'
        info=json.loads((source/'case.json').read_text())
        fields=['T','p','U','Qdot']+info['species']
        copy_checkpoint(source,target,CP)
        prepare=command(MPI+['padFluxState','-parallel','-time',CP],target,target/'fluxPrepare.log')
        restore=command(MPI+['padFluxState','-restore','-repairZeroCoupled','-parallel','-time',CP],target,target/'fluxRestore.log')
        audit(target)
        reference_flux=ROOT/f'data/raw/fluxDiagnosis/A0_r{repeat}'
        flux=max(abs(a-b) for a,b in zip(assemble(reference_flux,CP,'padDivPhi',256),assemble(target,CP,'padDivPhi',256)))
        set_control(target,start=float(CP),steps=40,dt=info['dt'],restart_state=True)
        wall=solve(target,4,exe='reactingFoamPADRestart',timeout=300)
        gate=numerical_gate(*[canonical_directory(p,latest_time(target,True),fields,256) for p in [reference,target]],info)
        row=dict(repeat=repeat,path=str(target.relative_to(ROOT)),source=str(source.relative_to(ROOT)),prepareWall=prepare,
                 restoreWall=restore,solverWall=wall,totalWall=prepare+restore+wall,fluxDivergenceLinf=flux,gate=gate,
                 scope='Copied original post-migration state; exact-zero coupled flux filled from its nonzero periodic partner without reference fields. Original evidence unchanged. Specialized diagnostic, not a generic arbitrary-corruption repair.')
        manifest.write_text(json.dumps(row,indent=2));repaired.append(row)
        print('OBSERVED ZERO REPAIR',repeat,'div',flux,'T',gate['fields']['T']['Linf'],'gate',gate['pass_'],flush=True)
    result=dict(records=records,observedZeroRepairs=repaired,originalFaceAudit=face_records,originalTrialsChanged=False,
                gateThresholdChanged=False,mainPerformanceDataChanged=False,
                scope='Optional version-specific axis-aligned stationary-mesh flux preservation, tested on the exact three observed final ownership maps. Not a general rotated-cyclic or moving-mesh implementation.')
    (ROOT/'data/processed/flux_repair.json').write_text(json.dumps(result,indent=2))
    assert all(r['gate']['pass_'] and r['fluxDivergenceLinf']<1e-6 for r in records if r['preserveFlux'])
    assert all(r['gate']['pass_'] and r['fluxDivergenceLinf']<1e-6 for r in repaired)

if __name__=='__main__':main()
