"""Bounded pressure/time/grid pilots following nonconvergent energy budgets."""
import csv,json,re,statistics
from caseFactory import ROOT,make_case,decompose,solve,set_control,command,latest_time
from mapping import assemble
def main():
    records=[]
    specs=[(32,8,.125e-6,1,1),(32,8,.0625e-6,1,1),(32,8,.25e-6,2,1),(32,8,.25e-6,4,1),(64,16,.0625e-6,1,1),
           (32,8,.25e-6,1,2),(32,8,.25e-6,1,4)]
    for nx,ny,dt,ncorr,nouter in specs:
        name=f'conservationDiagnosis/moving_nx{nx}_dt{dt}_corr{ncorr}'+(f'_outer{nouter}' if nouter!=1 else '');c=ROOT/'data/raw'/name
        if not (c/'manifest.json').exists():
            make_case(name,'heldoutMoving',nx=nx,ny=ny,dt=dt,steps=round(.00024/dt))
            p=c/'system/fvSolution';s=p.read_text();s,n=re.subn(r'(\bnCorrectors\s+)\d+',lambda m:m[1]+str(ncorr),s);assert n==1
            s,n=re.subn(r'(\bnOuterCorrectors\s+)\d+',lambda m:m[1]+str(nouter),s);assert n==1;p.write_text(s)
            decompose(c,4);wall=solve(c,4,timeout=900)
            (c/'manifest.json').write_text(json.dumps(dict(nx=nx,ny=ny,dt=dt,nCorrectors=ncorr,nOuterCorrectors=nouter,solverWall=wall)))
            print('MEASURED conservation diagnosis',nx,dt,ncorr,nouter,wall,flush=True)
        command(['mpirun','--bind-to','core','--map-by','core','--nooversubscribe','-np','4','padNativeInventory','-parallel','-time','0:'],c,c/'inventory.log')
        rank=[]
        for path in c.glob('processor*/postProcessing/inventory/rank*.csv'):
            with path.open() as stream:rank.extend({k:float(v) for k,v in r.items()} for r in csv.DictReader(stream))
        totals=[]
        for t in sorted(set(r['time'] for r in rank)):
            group=[r for r in rank if r['time']==t];row={k:sum(r[k] for r in group) for k in group[0] if k not in ['time','rank','nCells','minT','maxT','sumYError']};row['time']=t;totals.append(row)
        initial,end=totals[0],totals[-1]
        T=assemble(c,latest_time(c,True),'T',nx*ny)
        row=dict(nx=nx,ny=ny,dt=dt,nCorrectors=ncorr,nOuterCorrectors=nouter,initial=initial,end=end,Tmax=max(T),Tmean=statistics.mean(T),
            relativeMassDrift=(end['mass']-initial['mass'])/initial['mass'],relativeEnergyDrift=(end['totalEnergy']-initial['totalEnergy'])/abs(initial['totalEnergy']),
            path=str(c.relative_to(ROOT)),scope='accuracy diagnostic, not controller tuning or a replacement for the frozen performance dataset')
        records.append(row);(ROOT/'data/processed/conservation_diagnosis.json').write_text(json.dumps(records,indent=2));print('DIAGNOSED budget',row['relativeMassDrift'],row['relativeEnergyDrift'],flush=True)
    # The fixed live mesh partition exposed one rejected endpoint. Numerical
    # controls run sequentially after these budget pilots, before plotting.
    from liveMeshFollowup import main as mesh_followup
    mesh_followup()
if __name__=='__main__':main()
