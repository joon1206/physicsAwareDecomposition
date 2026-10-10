"""Close the equation budget, independently reconstruct energy and publish gates."""
from pathlib import Path
import csv,json,math,sys,gzip
from collections import defaultdict
from thermo_reference import inventory
from foamio import read_field,read_labels
ROOT=Path(__file__).resolve().parents[1]
TERMS=['Dpressure','Dkinetic','DrhoH','DrhoC','DspeciesChemistry','Dequation','Dtransport','Dhistory']
def rows(path):
    with path.open() as f:return [{k:(v if k=='stage' else float(v)) for k,v in row.items()} for row in csv.DictReader(f)]
def totals(case,pattern,key):
    grouped=defaultdict(list)
    # Identical stage labels can occur twice within one pressure correction.
    # Preserve file execution order rather than combining those physical states.
    stage_rows='stage' in key
    if stage_rows:key=['time','step','checkpoint','outer','pressure','stage']
    for p in case.glob(pattern):
        checkpoint=defaultdict(int)
        for r in rows(p):
            if stage_rows:
                r['checkpoint']=checkpoint[r['step']];checkpoint[r['step']]+=1
            grouped[tuple(r[k] for k in key)].append(r)
    out=[]
    for g,rs in sorted(grouped.items()):
        row=dict(zip(key,g));row['ranks']=len(rs)
        for k in rs[0]:
            if k in row or k in ['rank','stage','outer','pressure','dt','time','step','checkpoint']:continue
            row[k]=(min if k.startswith('min') else max if k=='sumYError' else math.fsum)(r[k] for r in rs)
        for k in ['time','dt','step','outer','pressure']:row.setdefault(k,rs[0][k]) if k in rs[0] else None
        out.append(row)
    return out
def fields(case,ranks,t,name,n):
    if ranks==1:return read_field(case/format(t,'.12g')/name,n)
    out=[None]*n
    for r in range(ranks):
        b=case/f'processor{r}';ids=read_labels(b/'constant/polyMesh/cellProcAddressing');vals=read_field(b/format(t,'.12g')/name,len(ids))
        for i,v in zip(ids,vals):out[i]=v
    assert all(v is not None for v in out);return out
def compare(ca,cb):
    a=json.loads((ca/'result.json').read_text());b=json.loads((cb/'result.json').read_text());info=json.loads((ca/'case.json').read_text());n=info['nCells'];t=a['dt']*a['steps'];out={}
    for name in ['T','p','rho','h','U']+info['species']:
        va=fields(ca,a['ranks'],t,name,n);vb=fields(cb,b['ranks'],t,name,n)
        ds=[math.sqrt(sum((x-y)**2 for x,y in zip(u,v))) if isinstance(u,tuple) else abs(u-v) for u,v in zip(va,vb)]
        out[name]={'L1':math.fsum(ds)/n,'L2':math.sqrt(math.fsum(d*d for d in ds)/n),'Linf':max(ds)}
    return out
def summarize(case):
    meta=json.loads((case/'result.json').read_text());t=meta['dt']*meta['steps'];initial=inventory(case,0,meta['ranks']);end=inventory(case,t,meta['ranks'])
    stages=totals(case,'**/energyLedger/*/stages_rank*.csv',['time','step','outer','pressure','stage'])
    budgets=totals(case,'**/energyLedger/*/budget_rank*.csv',['time'])
    native=totals(case,'**/inventory/rank*.csv',['time'])
    # inventory utility has no step/outer columns; totals handles this schema.
    E0=initial['E_stored'];assert abs(E0)>1e-6,'unsafe energy normalization'
    row={**meta,'initial':initial,'end':end,'signedEnergyDrift':(end['E_stored']-E0)/abs(E0),
         'absoluteEnergyDrift':abs(end['E_stored']-E0)/abs(E0),'massDrift':(end['mass']-initial['mass'])/initial['mass'],
         'elementDrift':{e:(end['elements'][e]-m)/m for e,m in initial['elements'].items() if m>1e-20},
         'independentNativeEnergyDifference':end['E_stored']-native[-1]['totalEnergy'],
         'thermoInventoryDifference':end['E_NASA']-end['E_stored']}
    if budgets:
        row.update(cumulativeTerms={k:math.fsum(r[k] for r in budgets) for k in TERMS},
                   maxStepClosure=max(abs(r['closure']) for r in budgets),cumulativeClosure=math.fsum(r['closure'] for r in budgets),
                   ledgerInventoryDifference=math.fsum(r['DE'] for r in budgets)-(end['E_stored']-E0),
                   minT=min(r['minT'] for r in stages),minP=min(r['minP'] for r in stages),minY=min(r['minY'] for r in stages),
                   sumYError=max(r['sumYError'] for r in stages),maxContinuityL1=max(r['continuityL1'] for r in budgets))
    return row,budgets,stages
def main():
    results=[];budgets={};stages={}
    for p in sorted((ROOT/'data/raw').glob('*/result.json')):
        if p.parent.name.startswith('timing_'):continue
        r,b,s=summarize(p.parent);results.append(r);budgets[r['name']]=b;stages[r['name']]=s
        print(r['name'],'drift',r['signedEnergyDrift'],'closure',r.get('maxStepClosure'),flush=True)
    (ROOT/'data/processed/audit_summary.json').write_text(json.dumps(results,indent=2)+'\n')
    (ROOT/'data/processed/step_budgets.json').write_text(json.dumps(budgets,indent=2)+'\n')
    with gzip.open(ROOT/'data/processed/stage_inventories.json.gz','wt',compresslevel=6) as f:json.dump(stages,f,separators=(',',':'))
    # Keep a compact human-readable first/last-step slice; full stages are lossless gzip.
    latest_times={name:max((r['time'] for r in rs),default=0) for name,rs in stages.items()}
    slices={name:[r for r in rs if r['step']<=2 or r['time']==latest_times[name]] for name,rs in stages.items()}
    (ROOT/'data/processed/stage_slices.json').write_text(json.dumps(slices,indent=2)+'\n')
    previous=ROOT/'data/processed/stage_inventories.json'
    if previous.exists():previous.unlink()
    gates={}
    for r in results:
        gates[r['name']]=dict(independentInventory=abs(r['independentNativeEnergyDifference'])<1e-10,
                             mass=abs(r['massDrift'])<1e-9,elements=max(abs(v) for v in r['elementDrift'].values())<1e-5)
        if 'maxStepClosure' in r:gates[r['name']].update(closure=r['maxStepClosure']<1e-12,ledgerInventory=abs(r['ledgerInventoryDifference'])<1e-10,
            positivity=r['minT']>0 and r['minP']>0 and r['minY']>=-1e-14,normalization=r['sumYError']<1e-12)
    base=ROOT/'data/raw/F_dt2e-06_p1'
    for name in ['F_ledger_off','F_original','F_serial','F_balanced','F_restart']:
        case=ROOT/'data/raw'/name
        if (base/'result.json').exists() and (case/'result.json').exists():
            norms=compare(base,case);gates[name]['fieldNorms']=norms
            gates[name]['equivalence']=norms['T']['Linf']<.02 and norms['h']['Linf']<20 and norms['p']['Linf']<1
    (ROOT/'data/processed/gates.json').write_text(json.dumps(gates,indent=2)+'\n')
    if '--plots' in sys.argv:plot(results,budgets,stages)
def plot(results,budgets,stages):
    import matplotlib;matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    lookup={r['name']:r for r in results};name='F_dt2e-06_p1'
    if name not in lookup:return
    b=budgets[name];t=[r['time']*1e6 for r in b];fig,axes=plt.subplots(2,2,figsize=(12,8),constrained_layout=True)
    cumulative=[math.fsum(r['DE'] for r in b[:i+1]) for i in range(len(b))]
    axes[0,0].plot(t,cumulative,color='black',label='Measured');axes[0,0].set_ylabel('Cumulative energy defect (J)')
    for k in TERMS[:6]:axes[0,0].plot(t,[math.fsum(r[k] for r in b[:i+1]) for i in range(len(b))],label=k)
    axes[0,0].legend(fontsize=7,ncol=2);axes[0,1].plot(t,[r['DE'] for r in b]);axes[0,1].set_ylabel('Defect per timestep (J)')
    for pc in [1,4]:
        rs=sorted((r for r in results if r['name'].startswith('F_dt') and r['nCorrectors']==pc),key=lambda r:r['dt'])
        axes[1,0].loglog([r['dt']*1e6 for r in rs],[r['absoluteEnergyDrift'] for r in rs],'o-',label=f'{pc} pressure corrections')
    axes[1,0].set_xlabel('dt (μs)');axes[1,0].set_ylabel('Absolute normalized endpoint drift');axes[1,0].legend(fontsize=8)
    bars=[lookup[name]['cumulativeTerms'][k] for k in TERMS];axes[1,1].bar(range(len(TERMS)),bars);axes[1,1].set_xticks(range(len(TERMS)));axes[1,1].set_xticklabels(TERMS,rotation=45,ha='right',fontsize=7);axes[1,1].set_ylabel('Signed cumulative contribution (J)')
    for ax in axes[0]:ax.set_xlabel('Time (μs)')
    for ax in axes.flat:ax.grid(alpha=.2)
    fig.savefig(ROOT/'figures/closed_energy_audit.png',dpi=180);fig.savefig(ROOT/'figures/closed_energy_audit.pdf');plt.close(fig)
    # Deliberately do not use an unsigned stacked plot with cancelling terms.
if __name__=='__main__':main()
