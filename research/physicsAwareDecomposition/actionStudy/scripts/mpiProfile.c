/* GPL-3.0-or-later. Rank-local PMPI counters; no added collectives or barriers.
 * Payload bytes are application buffer bytes, not bytes observed on a network.
 * MPI call duration includes synchronization/load imbalance and is not network
 * transfer time. Thread-safety assumes the study's single-threaded MPI ranks.
 */
#include <mpi.h>
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <time.h>
static uint64_t sends, receives, send_bytes, receive_bytes, collectives, waits;
static double call_seconds, wait_seconds;
static double tick(void) { struct timespec t; clock_gettime(CLOCK_MONOTONIC,&t); return t.tv_sec+t.tv_nsec*1e-9; }
static uint64_t bytes(int count,MPI_Datatype datatype) { int n=0; PMPI_Type_size(datatype,&n);return (uint64_t)count*n; }
#define BEGIN double begin=tick()
#define END call_seconds+=tick()-begin
int MPI_Send(const void*b,int n,MPI_Datatype d,int dest,int tag,MPI_Comm c) {
 BEGIN;int r=PMPI_Send(b,n,d,dest,tag,c);END;sends++;send_bytes+=bytes(n,d);return r;
}
int MPI_Isend(const void*b,int n,MPI_Datatype d,int dest,int tag,MPI_Comm c,MPI_Request*q) {
 BEGIN;int r=PMPI_Isend(b,n,d,dest,tag,c,q);END;sends++;send_bytes+=bytes(n,d);return r;
}
int MPI_Recv(void*b,int n,MPI_Datatype d,int src,int tag,MPI_Comm c,MPI_Status*s) {
 BEGIN;int r=PMPI_Recv(b,n,d,src,tag,c,s);END;receives++;receive_bytes+=bytes(n,d);return r;
}
int MPI_Irecv(void*b,int n,MPI_Datatype d,int src,int tag,MPI_Comm c,MPI_Request*q) {
 BEGIN;int r=PMPI_Irecv(b,n,d,src,tag,c,q);END;receives++;receive_bytes+=bytes(n,d);return r;
}
int MPI_Allreduce(const void*s,void*r,int n,MPI_Datatype d,MPI_Op o,MPI_Comm c) {
 BEGIN;int ret=PMPI_Allreduce(s,r,n,d,o,c);END;collectives++;return ret;
}
int MPI_Alltoall(const void*s,int sn,MPI_Datatype sd,void*r,int rn,MPI_Datatype rd,MPI_Comm c) {
 BEGIN;int ret=PMPI_Alltoall(s,sn,sd,r,rn,rd,c);END;collectives++;return ret;
}
int MPI_Alltoallv(const void*s,const int*sn,const int*so,MPI_Datatype sd,void*r,const int*rn,const int*ro,MPI_Datatype rd,MPI_Comm c) {
 BEGIN;int ret=PMPI_Alltoallv(s,sn,so,sd,r,rn,ro,rd,c);END;collectives++;return ret;
}
int MPI_Waitall(int n,MPI_Request*q,MPI_Status*s) {
 BEGIN;int r=PMPI_Waitall(n,q,s);double dt=tick()-begin;call_seconds+=dt;wait_seconds+=dt;waits++;return r;
}
int MPI_Wait(MPI_Request*q,MPI_Status*s) {
 BEGIN;int r=PMPI_Wait(q,s);double dt=tick()-begin;call_seconds+=dt;wait_seconds+=dt;waits++;return r;
}
int MPI_Finalize(void) {
 const char*dir=getenv("PAD_MPI_PROFILE_DIR");
 if(dir) { int rank;PMPI_Comm_rank(MPI_COMM_WORLD,&rank);char path[4096];
  snprintf(path,sizeof(path),"%s/mpi_rank%04d.csv",dir,rank);FILE*f=fopen(path,"w");
  if(f) { fprintf(f,"rank,sends,receives,sendPayloadBytes,receiveBufferBytes,collectives,waits,callSeconds,waitSeconds\n");
   fprintf(f,"%d,%llu,%llu,%llu,%llu,%llu,%llu,%.17g,%.17g\n",rank,
    (unsigned long long)sends,(unsigned long long)receives,(unsigned long long)send_bytes,
    (unsigned long long)receive_bytes,(unsigned long long)collectives,(unsigned long long)waits,call_seconds,wait_seconds);fclose(f);
  }
 }
 return PMPI_Finalize();
}
