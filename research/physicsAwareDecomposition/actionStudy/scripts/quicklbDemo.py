"""Independent reproduction of QUICKLB's public Gray-Scott example.

Toy reaction-diffusion, not an OpenFOAM or INCA speedup comparison. Uses the
published Cell callbacks and diffusion stencil, with headless numerical QA.
"""
import argparse,json,time
from pathlib import Path
import numpy as np
from scipy.integrate import solve_ivp
from mpi4py import MPI
from quicklb import Loadbalancer

p=argparse.ArgumentParser();p.add_argument('--algorithm',choices=['NONE','GREEDY','SORT','SORT2'],default='SORT');p.add_argument('--steps',type=int,default=10);p.add_argument('--repeat',type=int,default=0);p.add_argument('--output',type=Path,required=True);args=p.parse_args()
comm=MPI.COMM_WORLD;rank=comm.rank;size=30
def shared(shape):
    win=MPI.Win.Allocate_shared(np.prod(shape)*8 if rank==0 else 0,8,comm=comm)
    buf,_=win.Shared_query(0);return np.ndarray(shape,dtype=np.float64,buffer=buf),win
A,wa=shared((size,size));B,wb=shared((size,size))
start=size//comm.size*rank+min(rank,size%comm.size);end=size//comm.size*(rank+1)+min(rank+1,size%comm.size)
if rank==0:
    A[:]=1;B[:]=0;A[12:18,5:25]=.5;B[12:18,5:25]=.25
comm.Barrier()
class Cell:
    def __init__(self,AA=None,BB=None):
        self.A=np.array([np.nan]) if AA is None else AA;self.B=np.array([np.nan]) if BB is None else BB
    @staticmethod
    def deriv(t,y):
        a,b=y;abb=a*b*b;return [-abb+.0545*(1-a),abb-(.0545+.062)*b]
    def compute(self):
        s=solve_ivp(self.deriv,(0,1),(self.A[0],self.B[0]),method='BDF',rtol=.0001)
        self.A[0],self.B[0]=s.y[:,-1]
    def serialize(self):return np.concatenate((self.A.view(np.byte),self.B.view(np.byte)))
    def deserialize(self,buffer):self.A[0]=buffer[:8].view(np.float64)[0];self.B[0]=buffer[8:16].view(np.float64)[0]
cells=[Cell(A[i,j:j+1],B[i,j:j+1]) for j in range(size) for i in range(start,end)]
lb=Loadbalancer(cells,args.algorithm,.01,.01,3) if args.algorithm!='NONE' else None
def lap(x):
    return np.roll(x,1,axis=0)[start:end]+np.roll(x,-1,axis=0)[start:end]+np.roll(x,1,axis=1)[start:end]+np.roll(x,-1,axis=1)[start:end]-4*x[start:end]
comm.Barrier();tick=time.perf_counter();partition=0.
for index in range(args.steps):
    wa.Sync();wb.Sync();comm.Barrier();LA=lap(A).copy();LB=lap(B).copy();comm.Barrier()
    if lb:
        stamp=time.perf_counter();lb.partition();partition+=time.perf_counter()-stamp;lb.iterate()
    else:
        for c in cells:c.compute()
    A[start:end]+= .1*LA;B[start:end]+=.05*LB
comm.Barrier();wall=comm.allreduce(time.perf_counter()-tick,op=MPI.MAX);partition=comm.allreduce(partition,op=MPI.MAX)
if rank==0:
    args.output.mkdir(parents=True,exist_ok=True)
    name=f'{args.algorithm}_p{comm.size}_r{args.repeat}_n{args.steps}'
    np.savez(args.output/(name+'.npz'),A=A.copy(),B=B.copy())
    (args.output/(name+'.json')).write_text(json.dumps(dict(algorithm=args.algorithm,ranks=comm.size,repeat=args.repeat,steps=args.steps,wall=wall,partitionWall=partition,
        benchmark='QUICKLB public Gray-Scott reaction diffusion, 30x30, headless',MPI=MPI.Get_library_version().strip()),indent=2))
    print('REPRODUCED QUICKLB',args.algorithm,comm.size,args.steps,wall,flush=True)
wa.Free();wb.Free()
