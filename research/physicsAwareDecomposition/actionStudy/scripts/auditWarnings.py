"""Inventory final build warnings without treating retained failures as success."""
import json,re
from caseFactory import ROOT

def main():
    build=ROOT/'data/raw/build'
    names=['costChemistry.log','reactingFoamPAD.log','restartSolver.log','stuttgartV2012.log',
           'nativeInventory.log','redistributeParPAD.log','fluxAudit.log','fluxState.log','initialStateSolver.log']
    project=[]
    for name in names:
        path=build/name
        assert path.exists(),name
        for number,line in enumerate(path.read_text(errors='replace').splitlines(),1):
            if re.search(r'\bwarning:',line,re.I):project.append(dict(log=name,line=number,text=line.strip()))
    quick=ROOT/'data/raw/finishLogs/quicklb.log'
    upstream=[]
    for number,line in enumerate(quick.read_text(errors='replace').splitlines(),1):
        if re.search(r'warning|deprecated|unable to open mca_btl_openib',line,re.I):
            if 'distutils' in line:explanation='Legacy upstream F2Py/distutils backend deprecation; pinned Python/NumPy toolchain builds successfully.'
            elif 'redefinition' in line:explanation='Upstream F2Py kind-map redefinition; fixed-width integers and pointers map to 64-bit host ABI. Executed four-mode field checks pass.'
            elif 'capi_j' in line:explanation='Unused variable in generated F2Py C wrapper; no project CFD source warning.'
            elif 'CMA support' in line:explanation='WSL ptrace policy disables CMA; OpenMPI explicitly falls back to another shared-memory mechanism. Same fallback across all modes; toy timings are specific to this host.'
            elif 'mca_btl_openib' in line:explanation='Optional OpenMPI InfiniBand plugin cannot load absent RDMA library and is ignored. This single-host run uses shared-memory communication; no network scalability claim.'
            else:raise RuntimeError('Unclassified upstream warning: '+line)
            upstream.append(dict(line=number,text=line.strip(),explanation=explanation))
    result=dict(projectWarnings=project,upstreamQuicklbWarnings=upstream,projectWarningsPassed=not project,
                interpretation='Project C++ clean final builds contain no compiler warnings. Public QUICKLB uses legacy numpy.distutils/F2Py packaging; its final successful build warnings are retained below. The unused generated capi_jset warning concerns F2Py wrapper code, not a changed CFD kernel. Successful four-mode field checks establish the executed toy scope, not absence of all upstream packaging risk.',
                rejectedBuilds='OPAL_LIBDIR contamination and upstream --inplace packaging failures are retained separately; they are not counted as successful build evidence.')
    (ROOT/'docs/build_warnings.json').write_text(json.dumps(result,indent=2))
    print('PROJECT WARNINGS',len(project),'UPSTREAM WARNINGS',len(upstream))
    if project:raise RuntimeError('Investigate final project compiler warnings')

if __name__=='__main__':main()
