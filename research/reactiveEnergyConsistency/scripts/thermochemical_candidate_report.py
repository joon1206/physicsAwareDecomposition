"""Derived candidate decisions from retained results; no raw evidence mutation."""
from pathlib import Path
import json,math
from thermo_continuity import sha
from clean_thermo_report import table
ROOT=Path(__file__).resolve().parents[1];P=ROOT/'candidateStudy/data/processed';D=ROOT/'docs'

def main():
    projection=json.loads((P/'invariant_projection_valid_data.json').read_text());rows=projection['records']
    eligible=[r for r in rows if not r['projected']['failed']]
    worse=[r for r in eligible if r['projected']['temperatureError']>r['temperatureError']]
    separated=[r for r in eligible if r['projected']['temperatureError']-r['temperatureError']>2*r['referenceToleranceContrast']['T']]
    passrows=[r for r in eligible if r['projected']['gatesPass']]
    ref=json.loads((P/'clean_thermo_reference.json').read_text())
    audit=json.loads((P/'mechanism_continuity_audit.json').read_text())
    abstract=json.loads((P/'thermochemical_abstract_map.json').read_text())
    mechmap={'legacy':'legacyH2','HS':'H2_HS','CpHS':'H2_CpHS','GRI':'installedGRI','Alzueta':'Alzueta2023_baseline'}
    metrics={r['name']:max(abs(s['deltaHSpecific']) for s in r['rankedEnthalpy']) for r in audit['mechanisms']}
    risk=[]
    for r in ref['records']:
        observed=r['end']['R_energy' if r['constraint']=='CV' else 'R_enthalpy']
        denom=max(abs(r['initialE' if r['constraint']=='CV' else 'initialH']),1)
        risk.append(dict(mechanism=r['mechanism'],constraint=r['constraint'],Tinitial=r['Tinitial'],rtol=r['rtol'],
          mechanismMaxSpecificHJump=metrics[mechmap[r['mechanism']]],observedInvariantChange=observed,
          observedEventWeightedPrediction=r['end']['predictedJump'],normalizedPrediction=abs(r['end']['predictedJump'])/denom,
          observedRelativeError=r['relativeInvariantChange'],normalizedUnexplainedRemainder=r['jumpSubtractedRelativeError'],
          units='J/kg; mechanism maximum also J/kg. Concentrations/compositions are observed at interpolated crossings, not forecast.'))
    summary=dict(projectionCases=len(rows),eligible=len(eligible),gatePass=len(passrows),temperatureWorsens=len(worse),
      ineligible=len(rows)-len(eligible),worseningExceedsTwiceReferenceContrast=len(separated),maxEligibleEnergyResidual=max(r['projected']['relativeCanteraInvariantResidual'] for r in eligible),
      maxElementResidual=max(r['elementResidual'] for r in rows),referenceToleranceContrasts=[r['referenceToleranceContrast'] for r in rows],
      costScope='Concurrent endpoint wall values excluded. RHS/Jacobian evaluations retained. No runtime/memory dominance or publication cost pass asserted.',
      decisions={
       '1':'Reject generic scalar projection novelty and blanket trajectory-accuracy dominance; retain conditional invariant recovery as established baseline.',
       '2':'Reject finite RR/formation transfer as a new method: native solve already returns the same finite increment. CV enthalpy transfer also requires pressure change.',
       '3':'Reject generic transition-map interface novelty and sufficiency for later CFD density/pressure operators; existing independent codes already integrate invariant states.',
       '4':'Reject mechanism-only certification and generic predictive novelty. Observed crossing-weighted identity explains the direct jump but is not an independent prospective forecast.',
       '5':'Reject generic continuity repair novelty and physical-accuracy claim without original source data. Repair improves branch invariance but does not repair the CFD defect.'})
    (P/'thermochemical_candidate_decision.json').write_text(json.dumps(dict(summary=summary,risk=risk,
      inputSHA256={n:sha(P/n) for n in ['invariant_projection_valid_data.json','clean_thermo_reference.json','mechanism_continuity_audit.json','thermochemical_abstract_map.json']},driverSHA256=sha(__file__)),indent=2)+'\n')
    output=['# Invariant projection on continuous thermochemistry','',
      f"48 controls: {len(eligible)} scalar recoveries eligible, {len(passrows)} pass all declared endpoint gates, {len(worse)} eligible recoveries worsen temperature error. Eight GRI states have tiny negative provisional mass fractions (largest magnitude 2.465e-23); strict nonnegativity makes scalar-only recovery ineligible. These are small floating/ODE violations, not evidence of chemically substantial negative concentrations. Two other states retain mass/element residuals above 1e-12. No clipping or normalization masks these outcomes.",'',
      f'Of the observed increases, {len(separated)} exceed twice the stricter-reference temperature contrast. This contrast is an empirical uncertainty check, not a rigorous error bound; comparisons close to it are not resolved accuracy rankings. The scalar recovery restores the appropriate CV absolute internal energy or physical-CP absolute enthalpy, holding every species unchanged. It cannot remove mass/element/species trajectory errors. Both loose and strict trajectory integrations use Cantera 3.2 BDF; strict 1e-12 versus 1e-13 contrasts are reported as reference uncertainty. The root/property evaluation is independent Python NASA algebra checked against Cantera, not an independent trajectory integrator. Native Rosenbrock comparisons supply the separate source implementation evidence.','',
      'At H2 CV, T0=1100 K, rtol=1e-8, temperature error increases from 8.0013e-9 to 8.4105e-6 K after recovery. The provisional cancellation of composition and temperature errors is removed when energy is restored. This is an accuracy counterexample even though both errors are small. At H2 CV, 1500 K, rtol=1e-4, error increases from 0.00624 to 0.01780 K. Tightening the ODE can reduce species error, which the scalar operation leaves exactly unchanged.','',
      '## All controls','',table(['Mechanism','Constraint','T0','rtol','T error before (K)','T error after (K)','Max Y error','Endpoint gates'],
        [[r['mechanism'],r['constraint'],r['Tinitial'],r['rtol'],f"{r['temperatureError']:.8e}",f"{r['projected']['temperatureError']:.8e}" if not r['projected']['failed'] else 'ineligible',f"{r['speciesErrorMax']:.8e}",'PASS' if r['projected'].get('gatesPass') else 'FAIL'] for r in rows]),'',
      'These are final endpoint projections, not projections at every accepted BDF step with history/error-test correction. The rejection does not rule out the latter known approach or a full positivity-constrained species solve. CVODE eq3.11–3.12 already gives the weighted constrained manifold formulation; generic novelty fails independently of these numerical counterexamples.','',
      '## Accuracy and cost boundary','',
      'RHS/Jacobian/step counts are retained for all tolerances. Concurrent wall measurements are excluded from cost comparisons. No lower runtime/memory frontier is claimed; a candidate that already fails novelty and unconditional trajectory accuracy is not promoted on endpoint conservation. Prior native extra-pressure, dt and frozen-block baselines remain available with their original uncontended timings.','',
      'Machine evidence: invariant_projection_valid_data.json and raw InvariantProjectionValidData_v1. Root and data snapshots remain immutable.']
    (D/'invariant_projection_results.md').write_text('\n'.join(output)+'\n')
    output=['# Finite source and transition-map candidate cycles','',
      'The existing source interface already uses finite species increments. The selected integrated-reaction path computes RR_i=(c_i_new-c_i_old)W_i/dt and Qdot=-sum Hc_i RR_i. Therefore dt Qdot+sum Hc_i delta(rho Yi)=0 is an algebraic identity, independent of stiff integrator tolerance. It does not imply that the endpoint chemistry state has accurate species or preserves absolute energy. The installed instantaneous calculate() method is distinct from this selected solve path.','',
      'For continuous thermodynamics, exact scalar inversion of absolute energy/enthalpy completes a conditional conservative chemistry map. At CV, delta(rho hs)=-sum Hc_i delta q_i+delta p. Omitting delta p conserves the wrong enthalpy-density quantity and produces a CV residual equal to minus the EOS pressure change. At physical CP, delta hs=-sum Hc_i delta Yi with expansion/dilution and fixed total mass; density-scaled energy is not the invariant. Variable Cp changes inversion, not the constant formation-energy contraction.','',
      '## Independent minimal model','',
      'The Python model uses actual continuous H2 NASA properties, but a prescribed mass-balanced H2+O2/2->H2O extent with exponential progress. It is an abstract algebraic falsification model, not a replacement kinetic mechanism or a physical trajectory reference. It varies initial T, time step and CV/physical CP constraint, preserves positivity/mass/elements, and uses bisection inversion.','',
      table(['Constraint','T0 (K)','dt (s)','Invariant residual (J/kg)','Finite RR/Qdot residual (J/m3)','CV omitted-pressure error (J/m3)'],
       [[r['constraint'],r['Tinitial'],r['dt'],f"{r['specificInvariantResidual']:+.4e}",f"{r['finiteRRCancellation']:+.4e}",f"{r['formationOnlyCVResidual']:+.4e}" if r['constraint']=='CV' else 'not applicable'] for r in abstract['records']]),'',
      'The finite update cancels to roundoff; substituting an instantaneous initial source instead creates the recorded finite heat mismatch. This validates the rationale for finite increments but does not create an improvement over native RR, which is already finite.','',
      '## Post-map operator counterexample','',
      f"Two unit-volume cells have exact chemistry maps and the same final composition but unequal temperatures. Opposite density changes preserve global mass and every species inventory while pressure is reset exactly by EOS. The energy then changes by {abstract['postMapCounterexample']['energyChange']:+.9g} J. Its exact decomposition is DrhoH+DrhoC+Dpressure, with closure {abstract['postMapCounterexample']['identityClosure']:+.4e} J (roundoff against the energy scale). The prescribed density operation is not a solution of a flow equation; it is a counterexample to the claim that an invariant chemistry map alone guarantees conservation under arbitrary later pressure/density updates.",'',
      'Full native matched runs provide the stronger CFD evidence: Dchemistry remains roundoff while the density pair persists. Thus a chemistry/CFD interface rewrite cannot cancel the measured terms without changing transport or pressure/species/energy response. PelePhysics and conservative Cantera reactor state integration already implement the essential invariant-carrying architecture.','',
      'Decisions: family 2 REJECT as a new finite-RR method; family 3 REJECT as a generic new interface or sufficient CFD cure. Retain conservative maps as baselines. This does not exclude a demonstrably different operator response or source-forcing approximation. Machine evidence: thermochemical_abstract_map.json; raw ThermochemicalAbstractMap_v1.']
    (D/'finite_source_map_results.md').write_text('\n'.join(output)+'\n')
    output=['# Mechanism risk and reconstruction candidate cycles','',
      'For a CV trajectory crossing Tc, the data-jump contribution is sum_crossings sum_i c_i(Tc) Delta H_i [J/m3]. At physical CP the corresponding specific-enthalpy expression uses Yi(Tc) Delta H_i/W_i [J/kg]. Signed jumps follow crossing direction. Summing absolute contributions supplies a bound on the data jump only; it does not bound smooth ODE error, transport error or pressure coupling.','',
      '## Multi-mechanism source comparison','',table(['Mechanism','Constraint','T0','Max species h jump (J/kg)','Observed relative drift','Event-weighted prediction (relative)','Remainder'],
       [[r['mechanism'],r['constraint'],r['Tinitial'],f"{r['mechanismMaxSpecificHJump']:.6e}",f"{r['observedRelativeError']:.6e}",f"{r['normalizedPrediction']:.6e}",f"{r['normalizedUnexplainedRemainder']:.6e}"] for r in risk if r['rtol']==1e-12]),'',
      'The event-weighted quantities use observed, sample-interpolated crossing compositions. Their strong agreement for legacy H2/GRI is a verification of the jump identity, not held-out prospective prediction. Alzueta also has a smaller measured event floor. The same mechanism-wide maximum gives different invariant errors in crossing and noncrossing regimes; it cannot certify source success by itself. Continuous native spatial calls also fail in hot states despite negligible breakpoint jumps. A certificate requires both valid data and numerical/operator information.','',
      'Mech Checker (Killingsworth et al.2020, sec2.1–2.3) already combines automated constrained repair with numerical integration and pressure-coupled multizone consequences. A mechanism linter or an observed jump predictor has insufficient generic novelty. Family 4 REJECT as the primary method: no prospective, operating-condition-independent source/CFD error predictor has been validated. The event diagnostic remains useful evidence.','',
      '## Reconstruction','',
      'HS changes only upper-branch enthalpy/entropy integration constants and preserves Cp exactly. CpHS also shifts upper Cp by a small constant and then rematches h/s. Both preserve lower/reference coefficients exactly. NASA PAC fitting, RMG Wilhoit-to-NASA conversion, Boettcher Appendix H and Mech Checker already impose these types of constraints, including Cp derivatives and reference values.','',
      'The controls materially improve source breakpoint invariance, but neither supplies a validated fit to original molecular/tabulated thermochemical source data. Those source data are not available for the legacy files. Comparing a refit against samples from the old polynomial would measure approximation to that polynomial, not physical accuracy. Alternative polynomial order and reference interpolation therefore cannot be honestly ranked for physical accuracy here. No synthetic “correct” source data are substituted.','',
      'Family 5 REJECT as a generic new repair method or physical-accuracy claim. MODIFY only if independent original source data become available and a specific unresolved constrained-fit problem can be defined. This is a bounded branch decision, not a claim that all future thermochemistry reconstruction research is exhausted.','',
      'Machine evidence: thermochemical_candidate_decision.json contains all 90 tolerance/regime records and input hashes; mechanism_continuity_audit.json contains the full reaction and equilibrium rankings. The repair manifest records serialized residual jumps, not a claim of exact-real continuity.']
    (D/'thermochemical_risk_results.md').write_text('\n'.join(output)+'\n')
    print('Reported five candidate families',summary['decisions'])
if __name__=='__main__':main()
