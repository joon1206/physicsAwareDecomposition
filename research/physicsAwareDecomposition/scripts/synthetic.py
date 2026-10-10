#!/usr/bin/env python3
"""Full factorial workload study, cached unweighted native partitions."""
import argparse,csv,json,os,shutil,time
from pathlib import Path
from study import ROOT,run,decomp
from foamio import read_field,write_scalar,patches,proc_metrics
from models import weights,metrics,lpt
def make_mesh(nx,ny,tag):
    c=ROOT/f'data/raw/{tag}/mesh_{nx}x{ny}';c.mkdir(parents=True,exist_ok=False)
    for d in ['0','constant','system']:(c/d).mkdir()
    head=lambda obj:'FoamFile {version 2.0; format ascii; class dictionary; object '+obj+';}\n'
    (c/'system/blockMeshDict').write_text(head('blockMeshDict')+f"""
convertToMeters 1;
vertices ((0 0 0) (1 0 0) (1 1 0) (0 1 0) (0 0 .01) (1 0 .01) (1 1 .01) (0 1 .01));
blocks (hex (0 1 2 3 4 5 6 7) ({nx} {ny} 1) simpleGrading (1 1 1));
edges ();
boundary
(
walls {{type wall; faces ((0 4 7 3) (1 2 6 5) (0 1 5 4) (3 7 6 2));}}
frontAndBack {{type empty; faces ((0 3 2 1) (4 5 6 7));}}
);
mergePatchPairs ();
""")
    (c/'system/controlDict').write_text(head('controlDict')+'application icoFoam; startFrom startTime; startTime 0; stopAt endTime; endTime 1; deltaT 1; writeControl timeStep; writeInterval 1; writeFormat ascii; writePrecision 14;')
    (c/'system/fvSchemes').write_text(head('fvSchemes')+'ddtSchemes {default Euler;} gradSchemes {default Gauss linear;} divSchemes {default none;} laplacianSchemes {default Gauss linear orthogonal;} interpolationSchemes {default linear;} snGradSchemes {default orthogonal;}')
    (c/'system/fvSolution').write_text(head('fvSolution')+'solvers {}')
    run(['blockMesh'],c,c/'blockMesh.log')
    run(['postProcess','-func','writeCellCentres','-time','0'],c,c/'centres.log')
    pts=read_field(c/'0/C',nx*ny)
    expected=[((i+.5)/nx,(j+.5)/ny,.005) for j in range(ny) for i in range(nx)]
    if max(abs(a-b) for p,q in zip(pts,expected) for a,b in zip(p,q))>1e-12:raise RuntimeError('unexpected mesh ordering')
    return c,pts
def partition(base,name,p,method,w=None):
    c=base/name;c.mkdir()
    shutil.copytree(base/'constant',c/'constant',copy_function=os.link)
    shutil.copytree(base/'system',c/'system')
    (c/'0').mkdir()
    if w is not None:write_scalar(c/'0/cellWeight',w,[('walls','wall'),('frontAndBack','empty')])
    if p==1:return c,0.,[{'rank':0,'nCells':len(w) if w else 0,'processorFaces':0,'nNeighbours':0,'ids':list(range(len(w))) if w else []}]
    # decompose() uses current-time field; noFields avoids unnecessary volume output.
    (c/'system/decomposeParDict').write_text('FoamFile {version 2.0; format ascii; class dictionary; object decomposeParDict;}\n'+f'numberOfSubdomains {p}; method {method};\n'+('weightField cellWeight;\n' if w is not None else '')+f'simpleCoeffs {{ n ({p} 1 1); delta .001; }}')
    dt=run(['decomposePar','-time','0'],c,c/'decompose.log')
    return c,dt,proc_metrics(c)
def main(full=True):
    out=ROOT/'data/processed';out.mkdir(exist_ok=True,parents=True)
    tag='synthetic' if full else 'syntheticPilot'
    path=out/(tag+'.csv')
    if path.exists():raise RuntimeError('refusing to overwrite synthetic campaign')
    columns=['mesh','ranks','kind','amplitude','width','centreX','method','weighted','imbalance','cv','idealImbalance','processorFaces','maxProcessorFaces','maxNeighbours','decompositionWall','case','parts']
    with path.open('w',newline='') as f:
        writer=csv.DictWriter(f,fieldnames=columns);writer.writeheader()
        count=0
        for nx,ny in ([(32,16),(64,32)] if full else [(16,8)]):
            base,points=make_mesh(nx,ny,tag);n=nx*ny
            for p in ([1,2,4,8,12] if full else [1,2,4]):
                cache={}
                for method in ['scotch','simple']:
                    if p==1:cache[method]=(base,0.,[{'rank':0,'nCells':n,'processorFaces':0,'nNeighbours':0,'ids':list(range(n))}])
                    else:cache[method]=partition(base,f'baseline_p{p}_{method}',p,method)
                specs=[('gaussian',a,s,x) for a in ([0,1,2,5,10,20,50] if full else [0,20]) for s in ([.07,.15,.3] if full else [.15]) for x in ([.05,.25,.5] if full else [.25])]
                specs += [(kind,a,.15,.25) for kind in ['uniform','slab','half','multiple','extreme'] for a in [2,50]]
                for specid,(kind,a,s,x) in enumerate(specs):
                    w=weights(points,kind,a,s,(x,.5,.005));ideal,_=lpt(w,p)
                    for method in ['scotch','simple']:
                        for weighted in [False,True]:
                            if not weighted or p==1:c,dt,parts=cache[method]
                            else:c,dt,parts=partition(base,f'p{p}_s{specid}_{method}_weighted',p,method,w)
                            loads=[sum(w[i] for i in row['ids']) for row in parts]
                            if abs(sum(loads)-sum(w))>1e-8*sum(w):raise RuntimeError('lost cells')
                            row={'mesh':f'{nx}x{ny}','ranks':p,'kind':kind,'amplitude':a,'width':s,'centreX':x,'method':method,'weighted':int(weighted),'imbalance':metrics(loads)['imbalance'],'cv':metrics(loads)['cv'],'idealImbalance':metrics(ideal)['imbalance'],
                                'processorFaces':sum(r['processorFaces'] for r in parts)//2,'maxProcessorFaces':max(r['processorFaces'] for r in parts),'maxNeighbours':max(r['nNeighbours'] for r in parts),'decompositionWall':dt,'case':str(c.relative_to(ROOT)),
                                'parts':json.dumps([{k:v for k,v in r.items() if k!='ids'}|{'workload':load} for r,load in zip(parts,loads)])}
                            writer.writerow(row);count+=1
                    f.flush()
                print('MEASURED synthetic',nx,ny,p,'rows',count,flush=True)
    (ROOT/('data/raw/'+tag+'/manifest.json')).write_text(json.dumps({'status':'MEASURED','fullFactorial':full,'rows':count,'meshCoordinates':'native writeCellCentres independently checked against actual cell centres','timing':'process wall includes mesh decomposition and output; repeated cached baselines marked by shared case'},indent=2))
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--pilot',action='store_true');a=p.parse_args();main(not a.pilot)
