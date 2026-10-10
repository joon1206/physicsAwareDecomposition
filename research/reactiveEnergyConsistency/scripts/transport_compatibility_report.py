"""Known transport control: global cancellation, field controls and limitations."""
from pathlib import Path
import json
from analyze import compare
ROOT=Path(__file__).resolve().parents[1];STUDY=ROOT/'candidateStudy';RAW=STUDY/'data/raw'

def main():
    sets={}
    for label,file in [('zero','transport_screen.json'),('firstNonzero','transport_nonzero_screen.json'),('coupledSync','transport_nonzero_sync_screen.json'),('thermo2','transport_nonzero_sync_thermo_screen.json'),('thermo4','transport_nonzero_sync_thermo4_screen.json')]:
        path=STUDY/'data/processed'/file
        if path.exists():sets[label]=json.loads(path.read_text())
    differences=[]
    for label,rows in sets.items():
        for r in rows:
            if not r.get('compatibleSpeciesHeatFlux'):continue
            off=next(q for q in rows if not q.get('compatibleSpeciesHeatFlux') and (q['kind'],q['mode'],q['dt'],q['ranks'])==(r['kind'],r['mode'],r['dt'],r['ranks']))
            differences.append(dict(kind='fluxOnVersusOff',group=label,a=off['name'],b=r['name'],fields=compare(RAW/off['name'],RAW/r['name'])))
    for label in ['coupledSync','thermo2','thermo4']:
        rows=sets.get(label,[])
        for r in rows:
            if r['ranks']!=1:continue
            parallel=next(q for q in rows if q['ranks']==4 and (q['kind'],q['mode'],q['dt'],q['compatibleSpeciesHeatFlux'])==(r['kind'],r['mode'],r['dt'],r['compatibleSpeciesHeatFlux']))
            differences.append(dict(kind='serialParallel',group=label,a=r['name'],b=parallel['name'],fields=compare(RAW/r['name'],RAW/parallel['name'])))
    thermo_comparisons=[r for r in differences if r['kind']=='serialParallel' and r['group']=='thermo4' and '_conservativeState_' in r['b']]
    hypothesis=dict(thresholdTemperatureLinf=1e-6,executed=len(thermo_comparisons)==2,
                    supported=bool(thermo_comparisons) and all(r['fields']['T']['Linf']<1e-6 for r in thermo_comparisons),
                    interpretation='Two additional passes beyond the inherited two do not reduce the G partition difference; the proposed thermodynamic-inversion explanation is rejected at this contrast. The cause is not established.')
    data=dict(sets=sets,comparisons=differences,extraThermoPartitionHypothesis=hypothesis,scope='Common-species shared-Sutherland transport ablation of public kernel/Mix. Zero original As is an exact negative control. First broader nonzero run has retained coupled-flux cancellation failure. No independent resolved flame accuracy or statistical runtime estimate.')
    (STUDY/'data/processed/transport_compatibility.json').write_text(json.dumps(data,indent=2)+'\n')
    lines=['# Known species enthalpy transport: reacting and coupled-face controls','',
           'The added periodic heat flux changes local transport. It cannot algebraically',
           'remove the original post-pressure density/thermochemical energy defect.',
           'The initial Mix MPI run caught an uncancelled coupled-face flux; it is',
           'retained as a failed broader conservation control, even though its local',
           'energy accounting was correct. Derived coefficient halo evaluation was',
           'then changed and tested in distinct coupledSync cases.','',
           'Original kernel/B/Mix: Sutherland As=0, Ts=0. Nonzero tagged controls:',
           'shared As=1.458e-6, Ts=110.4 K, same public NASA chemistry and geometry.',
           'These coefficients define a numerical screen, not validated H2 diffusion.',
           'Each case runs to 240 us. Wall times are single execution records and',
           'are excluded from comparative performance claims.','',
           '| Group | Kind | dt (us) | Ranks | Method | Flux | E drift (%) | T mean (K) | Extra net (J) | Extra absolute space/time (J) | Cell closure (J) |',
           '|---|---|---:|---:|---|---|---:|---:|---:|---:|---:|']
    for label,rows in sets.items():
        for r in rows:
            lines.append(f"| {label} | {r['kind']} | {r['dt']*1e6:g} | {r['ranks']} | {r['mode']} | {'on' if r['compatibleSpeciesHeatFlux'] else 'off'} | {100*r['signedEnergyDrift']:+.8g} | {r['meanTemperature']:.8f} | {r['cumulativeExtraFluxNetEnergy']:+.5e} | {r['extraFluxSpaceTimeAbsoluteEnergy']:.5e} | {r['maxCellClosure']:.5e} |")
    lines+=['','## Field differences and reproducibility','',
            '| Comparison | Group | Case | T Linf (K) | p Linf (Pa) | rho Linf | U Linf (m/s) |',
            '|---|---|---|---:|---:|---:|---:|']
    for r in differences:
        f=r['fields'];lines.append(f"| {r['kind']} | {r['group']} | {r['b']} | {f['T']['Linf']:.6g} | {f['p']['Linf']:.6g} | {f['rho']['Linf']:.6g} | {f['U']['Linf']:.6g} |")
    lines+=['','The G serial/four-rank T Linf discrepancy is about 1.675e-5 K, with',
            'or without the added flux. Four thermo passes instead of the inherited',
            'two do not reduce it below the predeclared 1e-6 K threshold. The first',
            'thermo2 tag duplicates the factory setting and is not extra-inversion',
            'evidence. The inversion hypothesis is rejected for this contrast; the',
            'remaining partition discrepancy is reported, not attributed to a cause',
            'or claimed to be roundoff. A strict field-equivalence gate remains open.']
    lines+=['','Exact inputs, native source snapshots, executable hashes, independent NASA',
            'and native inventories, and full ledgers are stored per case. The new',
            'flux is fixed at post-species composition and predictor p/T through the',
            'energy inversion. This control adds no matrix equation but does add',
            'derived-coefficient halo exchanges; no zero-cost claim follows.','',
            'The original two-outer benchmark, finer dt benchmarks and independent',
            'central/HLLC uncertainty comparisons remain separate evidence. A successful',
            'known heat-flux control does not change their novelty or reacting accuracy',
            'gate decisions.','']
    (ROOT/'docs/transport_compatibility_results.md').write_text('\n'.join(lines))
    print('Transport control sets:',{k:len(v) for k,v in sets.items()},'field comparisons',len(differences))
if __name__=='__main__':main()
