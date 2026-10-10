"""Untimed measured workload characterization; forecast targets stay out of inputs."""
import csv,json,math,statistics
from caseFactory import ROOT,latest_time
from features import rank_costs,trace_cost,correlation,top_overlap,center,extract
from mapping import assemble,metrics

def main():
    histories=[];spatial={};persistence=[]
    for case in sorted((ROOT/'data/raw/histories').iterdir()):
        if not (case/'history.json').exists():continue
        info=json.loads((case/'case.json').read_text());n=info['nCells'];parts=metrics(case)
        times=sorted([p.name for p in (case/'processor0').iterdir() if p.is_dir() and p.name[0].isdigit()],key=float)
        for t in times:
            fields={f:assemble(case,t,f,n) for f in ['T','H2','OH','U','p']}
            if float(t)>0:
                fields.update({f:assemble(case,t,f,n) for f in ['Qdot','chemCost']})
                features,cost=extract(case,t,info)
            else:features={};cost=[0.]*n
            owner=[0]*n
            for p in parts:
                for cell in p['ids']:owner[cell]=p['rank']
            spatial[case.name+'_'+t]=dict(info=info,fields=fields,owner=owner,time=float(t))
            histories.append(dict(regime=case.name,time=float(t),Tmax=max(fields['T']),Tmin=min(fields['T']),
                meanT=statistics.mean(fields['T']),H2mean=statistics.mean(fields['H2']),
                QdotIntegral=sum(fields.get('Qdot',[0]))*.02*.008*.001/n,
                totalCost=sum(cost),costCenter=center(cost,info['nx'],info['ny'])[0],features=features))
        # Correlation against actual future cell cost is a diagnostic, never
        # supplied to the controller or its training feature vector.
        for index in [20,60,100]:
            current=trace_cost(case,index,n)
            if current is None:continue
            for lag in [1,2,5,10,20,40]:
                future=trace_cost(case,index+lag,n)
                if future is not None:persistence.append(dict(regime=case.name,index=index,lag=lag,
                    rho=correlation(current,future),topOverlap=top_overlap(current,future),
                    currentCost=sum(current),futureCost=sum(future)))
    for name,data in [('histories',histories),('spatial',spatial),('persistence',persistence)]:
        (ROOT/f'data/processed/{name}.json').write_text(json.dumps(data,indent=2))
    # Canonical before/after ownership and measured cost for a spatial comparison.
    case=ROOT/'data/raw/oracle/persistent/cp4e-05_H80_AM_r0'
    info=json.loads((case/'case.json').read_text());owner=[0]*info['nCells']
    for p in metrics(case):
        for cell in p['ids']:owner[cell]=p['rank']
    (ROOT/'data/processed/mesh_example.json').write_text(json.dumps(dict(owner=owner,info=info),indent=2))
    print('CHARACTERIZED',len(histories),'snapshots',len(persistence),'lag measurements')

if __name__=='__main__':main()
