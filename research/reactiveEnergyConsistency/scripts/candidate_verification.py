"""Executed-evidence regression checks; never rewrites accepted artifacts."""
from pathlib import Path
import csv,hashlib,json,math,unittest
ROOT=Path(__file__).resolve().parents[1];REPO=ROOT.parents[1];STUDY=ROOT/'candidateStudy'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
class Verification(unittest.TestCase):
    def test_accepted_audit_frozen(self):
        v=json.loads((ROOT/'docs/baseline_audit_freeze.json').read_text())
        for p,h in v['files'].items():self.assertEqual(sha(ROOT/p),h,p)
    def test_published_actionStudy_frozen(self):
        v=json.loads((ROOT/'docs/actionStudy_freeze.json').read_text())
        self.assertEqual(len(v['files']),499)
        for p,h in v['files'].items():self.assertEqual(sha(REPO/p),h,p)
    def test_all_experiments_have_exact_source(self):
        metas=list((STUDY/'data/raw').glob('*/experiment.json'))+list((STUDY/'data/raw').glob('*/wave_experiment.json'))+list((STUDY/'data/raw').glob('*/central_experiment.json'))
        for meta in metas:
            v=json.loads(meta.read_text());snapshot=ROOT/v['sourceSnapshot']
            for p,h in v['source'].items():self.assertEqual(sha(snapshot/p),h,str(meta)+p)
            if 'chemistrySourceSnapshot' in v:
                chemistry=ROOT/v['chemistrySourceSnapshot']
                for p,h in v['chemistrySource'].items():self.assertEqual(sha(chemistry/p),h,str(meta)+p)
    def test_local_and_global_ledgers(self):
        records=json.loads((STUDY/'data/processed/screen_summary.json').read_text())
        self.assertGreaterEqual(len(records),25)
        for r in records:
            self.assertLess(r['maxCellClosure'],1e-12,r['name'])
            self.assertLess(r['maxCellGlobalClosure'],1e-12,r['name'])
            self.assertLess(abs(r['localInventoryDifference']),1e-12,r['name'])
    def test_nonreacting_offsets_same_fields(self):
        v=json.loads((STUDY/'data/processed/ablation_analysis.json').read_text())
        for n,fields in v['mixFieldComparisons'].items():
            self.assertLess(fields['T']['Linf'],1e-9,n);self.assertLess(fields['rho']['Linf'],1e-12,n)
    def test_species_remap_elemental_balance(self):
        v=json.loads((STUDY/'data/processed/screen_summary.json').read_text())
        rows=[r for r in v if r['mode']=='speciesFlux' and r['kind']=='Mix']
        self.assertEqual(len(rows),2)
        for r in rows:
            self.assertLess(max(abs(x) for x in r['elementDrift'].values()),1e-12)
            self.assertLess(r['maxEOSRelative'],1e-12)
    def test_rejected_failures_retained(self):
        failures=json.loads((STUDY/'data/processed/failures.json').read_text())
        self.assertTrue(any(x.get('mode')=='scalarDensity' for x in failures))
        self.assertTrue(any(x.get('mode')=='localInternal' and x['formationAblation']['elementGauge'] for x in failures))
    def test_cantera_reference_tolerance(self):
        r=json.loads((STUDY/'data/processed/cantera_reference.json').read_text())
        self.assertLess(r['toleranceEndpointDifference']['T'],1e-4)
        self.assertLess(r['records'][-1]['maxEnergyDrift'],1e-9)
    def test_reference_phase_initialization(self):
        r=json.loads((STUDY/'data/processed/cantera_reference.json').read_text())
        for trial in r['records']:
            self.assertFalse(trial['reactorClone'])
            self.assertLess(trial['reactorMolecularWeightMaxError'],1e-12)
            self.assertLess(abs(trial['initialPressure']-101325),1e-8)
        check=json.loads((STUDY/'data/processed/reference_phase_identity.json').read_text())
        self.assertGreater(check['cloned']['molecularWeightError'],1e-4)
        self.assertLess(check['originalPhase']['molecularWeightError'],1e-12)
    def test_independent_homogeneous_first_order(self):
        r=json.loads((STUDY/'data/processed/cantera_reference.json').read_text())
        for mode in ['none','conservativeState']:
            rows=sorted([x for x in r['comparisons'] if x['mode']==mode and x['name'].endswith('_oneColumn') and x['dt']<=.125e-6],key=lambda x:x['dt'],reverse=True)
            self.assertEqual(len(rows),3)
            for coarse,fine in zip(rows,rows[1:]):
                order=math.log(coarse['errors']['T']['Linf']/fine['errors']['T']['Linf'],2)
                self.assertGreater(order,.9);self.assertLess(order,1.15)
    def test_analytic_reacting_transport(self):
        records=json.loads((STUDY/'data/processed/candidate_reacting_wave.json').read_text())
        for mode in ['none','conservativeState','blockConservative']:
            rows=sorted([r for r in records if r['mode']==mode and r['dt']==20e-9],key=lambda r:r['nx'])
            self.assertEqual(len(rows),3)
            for r in rows:
                self.assertLess(r['maxCellClosure'],1e-12)
                self.assertLess(abs(r['massDrift']),1e-12)
                self.assertLess(r['sumYError'],1e-12)
                self.assertGreaterEqual(r['minY'],-1e-12)
                if mode!='none':self.assertLess(abs(r['signedEnergyDrift']),1e-12)
            for a,b in zip(rows,rows[1:]):
                for field in ['T','A']:
                    order=math.log(a['errors'][field]['L1']/b['errors'][field]['L1'],2)
                    self.assertGreater(order,.9);self.assertLess(order,1.1)
    def test_independent_central_reference(self):
        records=json.loads((STUDY/'data/processed/central_verification.json').read_text())
        current=[r for r in records if r['name'].endswith('_hRecovery3')]
        self.assertGreaterEqual(len(current),10)
        for r in current:
            self.assertLess(r['maxLocalEnergyResidual'],1e-12,r['name'])
            self.assertLess(r['maxThermoEnergyMismatch'],1e-12,r['name'])
            self.assertLess(abs(r['signedEnergyDrift']),1e-10,r['name'])
            self.assertLess(abs(r['massDrift']),1e-10,r['name'])
            self.assertLess(r['maxYsumError'],1e-12,r['name'])
            self.assertGreaterEqual(r['minY'],-1e-12,r['name'])
        for kind in ['Wave','ReactingWave']:
            rows=sorted([r for r in current if r['kind']==kind],key=lambda r:r['nx'])
            self.assertEqual(len(rows),3)
            for a,b in zip(rows,rows[1:]):
                for f in (['T','A'] if kind=='ReactingWave' else ['T']):
                    self.assertLess(b['errors'][f]['L1'],a['errors'][f]['L1'])
                    order=math.log(a['errors'][f]['L1']/b['errors'][f]['L1'],2)
                    self.assertGreater(order,.8);self.assertLess(order,1.1)
    def test_conservative_reference_restriction(self):
        report=json.loads((STUDY/'data/processed/inviscid_field_comparison.json').read_text())
        self.assertGreaterEqual(report['referenceNx'],256)
        self.assertGreaterEqual(len(report['records']),3)
        for r in report['records']:
            self.assertLess(max(r['restriction']['conservationMismatch'].values()),1e-12,r['name'])
            self.assertLess(r['restriction']['maxThermodynamicRootResidual'],1e-6,r['name'])
    def test_independent_hllc_contact_reference(self):
        records=json.loads((STUDY/'data/processed/hllc_verification.json').read_text())
        for r in records:
            self.assertLess(abs(r['signedEnergyDrift']),1e-10,r['name'])
            self.assertLess(abs(r['massDrift']),1e-10,r['name'])
            self.assertLess(r['maxLocalEnergyResidual'],1e-12,r['name'])
            self.assertLess(r['maxThermoEnergyMismatch'],1e-12,r['name'])
            self.assertLess(r['maxYsumError'],1e-12,r['name'])
            self.assertGreaterEqual(r['minY'],-1e-12,r['name'])
            if 'elementDrift' in r:self.assertLess(max(abs(x) for x in r['elementDrift'].values()),1e-10,r['name'])
        for kind in ['Wave','ReactingWave']:
            rows=sorted([r for r in records if r['kind']==kind],key=lambda r:r['nx'])
            self.assertEqual(len(rows),3)
            for r in rows:
                self.assertLess(r['errors']['p']['Linf'],1e-6,r['name'])
                self.assertLess(r['errors']['Ux']['Linf'],1e-7,r['name'])
                self.assertLess(abs(r['signedEnergyDrift']),1e-10,r['name'])
                self.assertLess(r['maxYsumError'],1e-12,r['name'])
                self.assertLess(r['maxThermoEnergyMismatch'],1e-12,r['name'])
            for a,b in zip(rows,rows[1:]):
                for f in (['T','A'] if kind=='ReactingWave' else ['T']):
                    order=math.log(a['errors'][f]['L1']/b['errors'][f]['L1'],2)
                    self.assertGreater(order,.9);self.assertLess(order,1.1)
    def test_unequal_thermodynamic_wave(self):
        rows=json.loads((STUDY/'data/processed/mixture_wave.json').read_text())
        self.assertEqual(len(rows),15)
        for mode in ['none','conservativeState','blockConservative','central','hllc']:
            rr=sorted([r for r in rows if r['mode']==mode],key=lambda r:r['nx'])
            self.assertEqual([r['nx'] for r in rr],[32,64,128])
            for r in rr:
                self.assertLess(abs(r['massDrift']),1e-9,r['name'])
                self.assertLess(r['sumYError'],1e-12,r['name'])
                self.assertGreaterEqual(r['minY'],-1e-12,r['name'])
                self.assertLess(r['maxEOSRelative'],1e-9,r['name'])
                self.assertLess(r['maxLocalEnergyResidual'],1e-12,r['name'])
                if mode!='none':
                    self.assertLess(abs(r['signedEnergyDrift']),1e-9,r['name'])
                    self.assertLess(max(abs(x) for x in r['elementDrift'].values()),1e-9,r['name'])
            for a,b in zip(rr,rr[1:]):
                for f in ['T','H2']:
                    order=math.log(a['errors'][f]['L1']/b['errors'][f]['L1'],2)
                    self.assertGreater(order,.7);self.assertLess(order,1.2)
            # Exact pressure is constant, but conserved energy does not ensure it.
            self.assertGreater(rr[-1]['errors']['p']['Linf'],.1)
    def test_mixture_remap_gauge_covariance(self):
        data=json.loads((STUDY/'data/processed/mixture_mixing_identity.json').read_text())
        for r in data['records']:
            self.assertLess(abs(r['gaugeMismatchDifference']),1e-8)
            self.assertLess(abs(r['conservativeRecovery']['rootResidual']),1e-8)
        mid=next(r for r in data['records'] if r['weight']==.5)
        self.assertGreater(abs(mid['conservativeRecovery']['p']-101325),1000)
        self.assertGreater(abs(mid['energyDensityMismatch']),3000)
    def test_exact_species_enthalpy_diffusion(self):
        data=json.loads((STUDY/'data/processed/diffusion_compatibility.json').read_text());rows=data['records']
        self.assertEqual(len(rows),42)
        for r in rows:
            self.assertLess(abs(r['massDrift']),1e-9,r['name'])
            self.assertLess(r['sumYError'],1e-12,r['name'])
            self.assertGreater(r['minY'],0,r['name'])
            self.assertLess(r['maxEOSRelative'],1e-10,r['name'])
            self.assertLess(r['maxLocalEnergyResidual'],1e-12,r['name'])
            physical=r['Pr']==1 or r.get('compatibleSpeciesHeatFlux') is True
            if physical:
                self.assertLess(r['errors']['T']['Linf'],1e-8,r['name'])
                self.assertLess(r['errors']['p']['Linf'],1e-6,r['name'])
            else:self.assertGreater(r['errors']['T']['L1'],1,r['name'])
            if r['mode']!='none' or physical:self.assertLess(abs(r['signedEnergyDrift']),1e-10,r['name'])
            if r.get('compatibleSpeciesHeatFlux') is not None:
                self.assertLess(r['maxExtraFluxNetStepEnergy'],1e-17,r['name'])
                if not r['compatibleSpeciesHeatFlux']:
                    self.assertEqual(r['maxExtraFluxAbsStepEnergy'],0,r['name'])
                elif r['Pr']==1:self.assertLess(r['maxExtraFluxAbsStepEnergy'],1e-20,r['name'])
                else:self.assertGreater(r['maxExtraFluxAbsStepEnergy'],0,r['name'])
        for r in data['comparisons']:
            self.assertTrue(all(v['Linf']==0 for v in r['fields'].values()),r['b'])
        for r in data['orders']:
            self.assertGreater(r['speciesOrder'],.85);self.assertLess(r['speciesOrder'],1.1)
    def test_coupled_species_heat_flux_conservation(self):
        data=json.loads((STUDY/'data/processed/transport_compatibility.json').read_text())
        current=data['sets']['coupledSync'];self.assertGreaterEqual(len(current),8)
        for r in current:
            self.assertLess(abs(r['cumulativeExtraFluxNetEnergy']),1e-17,r['name'])
            self.assertLess(r['maxCellClosure'],1e-12,r['name'])
            self.assertLess(abs(r['localInventoryDifference']),1e-12,r['name'])
            self.assertLess(abs(r['independentNativeEnergyDifference']),1e-12,r['name'])
            if r['mode']=='conservativeState':
                self.assertLess(abs(r['signedEnergyDrift']),1e-10,r['name'])
                self.assertLess(abs(r['massDrift']),1e-9,r['name'])
                self.assertLess(max(abs(v) for v in r['elementDrift'].values()),1e-9,r['name'])
        for r in data['comparisons']:
            if r['group']=='zero':self.assertTrue(all(v['Linf']==0 for v in r['fields'].values()))
    def test_partition_inversion_hypothesis_rejected(self):
        data=json.loads((STUDY/'data/processed/transport_compatibility.json').read_text())
        hypothesis=data['extraThermoPartitionHypothesis']
        self.assertTrue(hypothesis['executed']);self.assertFalse(hypothesis['supported'])
        rows=[r for r in data['comparisons'] if r['kind']=='serialParallel' and r['group']=='thermo4' and '_conservativeState_' in r['b']]
        self.assertEqual(len(rows),2)
        for r in rows:self.assertGreater(r['fields']['T']['Linf'],hypothesis['thresholdTemperatureLinf'],r['b'])
    def test_initial_coupled_flux_failure_retained(self):
        data=json.loads((STUDY/'data/processed/transport_compatibility.json').read_text())
        first=next(r for r in data['sets']['firstNonzero'] if r['kind']=='Mix' and r['mode']=='conservativeState' and r['compatibleSpeciesHeatFlux'])
        self.assertGreater(abs(first['signedEnergyDrift']),1e-9)
        self.assertGreater(abs(first['cumulativeExtraFluxNetEnergy']),1e-10)
        self.assertLess(abs(first['cumulativeExtraFluxNetEnergy']-(first['end']['E_stored']-first['initial']['E_stored'])),1e-15)
    def test_native_autonomous_chemistry_interface(self):
        rows=json.loads((STUDY/'data/processed/cv_chemistry_probe.json').read_text())
        self.assertEqual(len(rows),16)
        self.assertEqual({r['path'] for r in rows},{'constantPressure','constantVolume'})
        for r in rows:
            self.assertEqual(r['timeDerivativeMax'],0)
            self.assertLess(r['directionalJacobianRelativeError'],1e-4)
            for k in ['massResidualRelative','thermalResidualRelative','pressureResidualRelative']:
                self.assertLess(r[k],1e-12)
    def test_corrected_homogeneous_thermal_path(self):
        data=json.loads((STUDY/'data/processed/cv_chemistry.json').read_text());rows=data['records']
        cv=[r for r in rows if r['odeThermalPath']=='constantVolume' and r['odeRelativeTolerance']==1e-10]
        self.assertEqual(len(cv),8)
        for r in cv:
            self.assertTrue(r['name'].endswith('_dfdt0'))
            self.assertLess(r['maxSourceRelativeMassChange'],1e-12,r['name'])
            self.assertLess(r['maxSourceRelativeEnergyChange'],1e-10,r['name'])
            self.assertLess(r['maxSourcePressureSlotRelativeMismatch'],1e-10,r['name'])
            self.assertGreaterEqual(r['minAcceptedConcentration'],-1e-20,r['name'])
            self.assertLess(r['maxCellClosure'],1e-12,r['name'])
            self.assertLess(r['maxEOSRelative'],1e-10,r['name'])
            self.assertLess(abs(r['massDrift']),1e-10,r['name'])
            self.assertLess(max(abs(v) for v in r['elementDrift'].values()),1e-9,r['name'])
            if r['mode']=='conservativeState':
                self.assertLess(r['errors']['T']['Linf'],1e-5,r['name'])
                self.assertLess(abs(r['signedEnergyDrift']),1e-10,r['name'])
            else:
                self.assertGreater(r['errors']['T']['Linf'],1e-4,r['name'])
                self.assertGreater(abs(r['signedEnergyDrift']),1e-8,r['name'])
        cp=[r for r in rows if r['odeThermalPath']=='constantPressure']
        self.assertEqual(len(cp),1)
        self.assertGreater(cp[0]['errors']['T']['Linf'],1e-4)
        self.assertLess(abs(cp[0]['signedEnergyDrift']),1e-10)
        self.assertGreater(cp[0]['maxSourceRelativeEnergyChange'],.01)
    def test_superseded_chemistry_evidence_retained(self):
        data=json.loads((STUDY/'data/processed/cv_chemistry.json').read_text())
        self.assertEqual(len(data['superseded']),10)
        for r in data['superseded']:
            self.assertFalse(r['name'].endswith('_dfdt0'))
            self.assertTrue((STUDY/'data/raw'/r['name']/'cv_result.json').exists())
        case=STUDY/'data/raw/F_none_dt2e-06_s1_g0_o1_p1_cvSource_rtol1e-10'
        failure=json.loads((case/'failure.json').read_text())
        self.assertIn('Intentionally interrupted',failure['error'])
        self.assertTrue((case/'solver.log').exists())
    def test_corrected_spatial_source_controls(self):
        rows=json.loads((STUDY/'data/processed/cv_reacting_screen.json').read_text())
        self.assertEqual(len(rows),8)
        for r in rows:
            self.assertNotIn('error',r)
            self.assertTrue(r['name'].endswith('_dfdt0'))
            self.assertLess(r['maxSourceRelativeMassChange'],1e-12,r['name'])
            self.assertLess(r['maxCellClosure'],1e-12,r['name'])
            self.assertLess(r['maxEOSRelative'],1e-10,r['name'])
            self.assertLess(abs(r['massDrift']),1e-9,r['name'])
            self.assertGreaterEqual(r['minAcceptedConcentration'],-1e-20,r['name'])
            if r['odeThermalPath']=='constantVolume':
                self.assertLess(r['maxSourcePressureSlotRelativeMismatch'],1e-10,r['name'])
            if r['mode']=='conservativeState':
                self.assertLess(abs(r['signedEnergyDrift']),1e-10,r['name'])
                self.assertLess(max(abs(x) for x in r['elementDrift'].values()),1e-9,r['name'])
                # Retain the coarse-step counterexample; conservation did not
                # make the reacting trajectory insensitive to the timestep.
                if r['dt']==2e-6:self.assertLess(r['meanTemperature'],800)
                else:self.assertGreater(r['meanTemperature'],2800)
            else:self.assertGreater(abs(r['signedEnergyDrift']),1e-3,r['name'])
    def test_broader_cv_regime_failure_retained(self):
        rows=json.loads((STUDY/'data/processed/cv_chemistry_regimes.json').read_text())
        self.assertEqual(len(rows),4)
        cold=next(r for r in rows if r['regime']=='coldHighPressure' and r['mode']=='conservativeState')
        self.assertIn('error',cold)
        self.assertTrue((STUDY/'data/raw'/cold['name']/'failure.json').exists())
        hot=next(r for r in rows if r['regime']=='hot' and r['mode']=='conservativeState')
        self.assertLess(hot['errors']['T']['Linf'],1e-5)
        self.assertLess(abs(hot['signedEnergyDrift']),1e-9)
    def test_component_cap_fallback_independent_gates(self):
        data=json.loads((STUDY/'data/processed/component_tolerance_cap.json').read_text())
        rows=data['records'];self.assertEqual(len(rows),10)
        self.assertEqual(sum('error' in r for r in rows),1)
        cold=next(r for r in rows if 'coldHighPressure' in r['name'] and r['componentEnergyTolerance'])
        self.assertNotIn('error',cold)
        self.assertLess(cold['errors']['T']['Linf'],max(1e-5,10*cold['referenceTemperatureToleranceContrast']))
        self.assertGreater(cold['maxAcceptedEnergyResidual'],5e-18)
        self.assertLessEqual(cold['maxAcceptedScaledResidual'],1)
        for r in rows:
            if 'error' in r:continue
            self.assertLess(abs(r['signedEnergyDrift']),1e-9,r['name'])
            self.assertLess(abs(r['massDrift']),1e-9,r['name'])
            self.assertLess(max(abs(v) for v in r['elementDrift'].values()),1e-9,r['name'])
            self.assertLess(r['maxEOSRelative'],1e-10,r['name'])
    def test_component_cap_preserves_completing_controls(self):
        data=json.loads((STUDY/'data/processed/component_tolerance_cap.json').read_text())
        self.assertEqual(len(data['comparisons']),4)
        for r in data['comparisons']:
            self.assertTrue(all(v['Linf']==0 for v in r['fields'].values()),r['kind'])
    def test_component_failed_hypothesis_retained(self):
        initial=json.loads((STUDY/'data/processed/component_tolerance_allowance_only.json').read_text())
        cycle=json.loads((STUDY/'data/processed/component_tolerance.json').read_text())
        self.assertEqual(len(initial['records']),8)
        self.assertEqual(len(cycle['records']),10)
        self.assertEqual(sum('error' in r for r in cycle['records']),2)
        for flag in [False,True]:
            self.assertIn('error',next(r for r in cycle['records'] if 'coldHighPressure' in r['name'] and r['componentEnergyTolerance']==flag))
        warm=[r for r in initial['records'] if '_standard_' in r['name']]
        off=next(r for r in warm if not r['componentEnergyTolerance'])
        on=next(r for r in warm if r['componentEnergyTolerance'])
        self.assertGreater(abs(on['signedEnergyDrift']),100*abs(off['signedEnergyDrift']))
    def test_component_accepted_trace_accumulation(self):
        data=json.loads((STUDY/'data/processed/component_tolerance_bounds.json').read_text())
        self.assertEqual(len(data['records']),24)
        cold=[r for r in data['records'] if 'coldHighPressure' in r['name']]
        self.assertEqual(len(cold),2)
        for r in cold:
            self.assertEqual(r['acceptedRankSteps'],240)
            self.assertLess(r['absoluteInventoryChange'],r['accumulatedResidualMagnitudeUpperSum'])
            self.assertLess(r['accumulatedResidualMagnitudeUpperSum'],r['accumulatedComponentAllowanceUpperSum'])
    def test_taylor_order_and_stiff_counterexample(self):
        data=json.loads((STUDY/'data/processed/thermal_path_taylor.json').read_text())
        self.assertEqual(len(data['records']),10)
        for r in data['orders']:
            lo,hi=(1.9,2.2) if r['compensated'] else (.9,1.2)
            self.assertGreater(r['order'],lo);self.assertLess(r['order'],hi)
        bare=next(r for r in data['records'] if r['regime']=='stiff' and r['compensated'])
        self.assertFalse(bare['admissible']);self.assertLess(bare['minY'],-1)
        self.assertLess(abs(bare['endpoint']['energyResidual'])/(700*1000+2e6*.5),1e-12)
    def test_positive_taylor_limiter_accuracy_failure(self):
        data=json.loads((STUDY/'data/processed/thermal_path_limiter.json').read_text())
        self.assertFalse(data['bare']['admissible'])
        limited=data['limited'];self.assertTrue(limited['admissible'])
        self.assertGreater(limited['theta'],0);self.assertLess(limited['theta'],1)
        self.assertGreater(data['limitedToBaselineTemperatureErrorRatio'],10)
        self.assertLess(abs(limited['energyResidual'])/(700*1000+2e6*.5),1e-12)
        self.assertEqual(limited['massResidual'],0);self.assertEqual(limited['eosResidual'],0)
    def test_element_reduction_compatibility_boundary(self):
        data=json.loads((STUDY/'data/processed/element_invariant_screen.json').read_text())
        rows=data['records'];self.assertEqual(len(rows),3)
        good=rows[0];self.assertTrue(good['eligible'])
        self.assertEqual(good['originalSolveCount'],10);self.assertEqual(good['independentSolveCount'],6)
        for k in ['maxFieldDifference','reconstructedEquationResidualRelative','maxReconstructedSumYError','maxElementFieldDifference']:
            self.assertLess(good[k],1e-12,k)
        self.assertGreaterEqual(good['minReconstructedY'],-1e-12)
        for r in rows[1:]:
            self.assertFalse(r['eligible'])
            self.assertGreater(r['maxFieldDifference'],1e-12)
            self.assertGreater(r['reconstructedEquationResidualRelative'],1e-12)
    def test_spatial_cv_source_energy_gate_failure_retained(self):
        # Evidence check of a failed scientific gate. Keep the original
        # source-energy threshold; never classify these cases as passing it.
        data=json.loads((STUDY/'data/processed/cv_source_invariant_audit.json').read_text())
        self.assertEqual(len(data['records']),4)
        self.assertEqual(sum(r['failingSourceCalls'] for r in data['records']),583)
        for r in data['records']:
            groups={g['endpointStraddlesMidpoint']:g for g in r['categories']}
            self.assertEqual(groups[True]['invariantFailures'],groups[True]['sourceCalls'])
            if r['mode']=='conservativeState' and r['dt']==2e-6:
                self.assertEqual(r['failingSourceCalls'],0)
            else:
                self.assertGreater(r['failingSourceCalls'],0)
                self.assertGreater(groups[True]['maxRelativeEnergyChange'],1e-10)
    def test_native_source_branch_jump_diagnostic(self):
        rows=json.loads((STUDY/'data/processed/cv_branch_probe.json').read_text())
        self.assertEqual(len(rows),18)
        for r in rows:
            self.assertLess(r['nativeIndependentJumpDifferenceMax'],1e-6)
            self.assertGreaterEqual(r['minAcceptedConcentration'],-1e-20)
            self.assertLess(r['pressureSlotRelativeMismatch'],1e-10)
            if r['Tinitial']==999:
                self.assertEqual(r['crossings'],1)
                self.assertGreater(r['relativeEnergyChange'],1e-8)
                if r['chunks']==1000:self.assertLess(r['relativeJumpUnexplainedEnergy'],1e-10)
            else:
                self.assertEqual(r['crossings'],0)
                self.assertLess(r['relativeEnergyChange'],1e-10)
    def test_independent_source_branch_counterexample(self):
        cases=json.loads((STUDY/'data/processed/cantera_branch_probe.json').read_text())
        self.assertEqual(len(cases),3)
        crossing=next(r for r in cases if r['Tinitial']==999)
        for r in crossing['records']:
            self.assertFalse(r['reactorClone'])
            self.assertLess(r['reactorMolecularWeightMaxError'],1e-12)
            self.assertGreater(r['end']['energyDrift'],1e-8)
        strict=crossing['records'][-1]
        for r in strict['comparisons']:
            self.assertLess(r['nativeTemperatureDifference'],1e-6)
            self.assertLess(r['nativeEnergyDriftDifference'],1e-10)
    def test_legacy_thermo_missing_and_multiple_roots(self):
        data=json.loads((STUDY/'data/processed/thermo_branch_inversion.json').read_text())
        gap=data['gap'];overlap=data['overlap']
        self.assertGreater(gap['gapWidth'],.01)
        self.assertLess(gap['energyLowLimit'],gap['targetEnergy'])
        self.assertLess(gap['targetEnergy'],gap['energyHighLimit'])
        self.assertEqual(gap['massDifference'],0)
        self.assertLess(max(abs(v) for v in gap['elementDifference'].values()),1e-12)
        self.assertGreaterEqual(min(gap['targetComposition'].values()),0)
        self.assertGreater(overlap['overlapWidth'],.001)
        self.assertLess(overlap['lowBranchRoot']['T'],1000)
        self.assertGreater(overlap['highBranchRoot']['T'],1000)
        for r in [overlap['lowBranchRoot'],overlap['highBranchRoot']]:
            self.assertLess(abs(r['energyResidual']),1e-8)
            self.assertGreater(r['p'],0)
        for case in [gap,overlap]:
            for bound in case['branchCvBounds']:
                self.assertGreater(int(bound['exactMinimumNumerator']),0)
                self.assertGreater(bound['positiveCvLowerBound'],100)
    def test_combined_defect_controller_counterexample(self):
        data=json.loads((STUDY/'data/processed/combined_defect_counterexample.json').read_text())
        self.assertEqual(len(data['records']),3)
        for r in data['records']:
            for key in ['relativeMassResidual','relativeMomentumResidual','relativeEnergyResidual']:
                self.assertLess(r[key],1e-12)
            self.assertLess(abs(r['relativeMassInventoryChange']),1e-12)
            self.assertLess(abs(r['relativeEnergyInventoryChange']),1e-12)
            self.assertEqual(r['finalPressureCorrection'],0)
            self.assertEqual(r['sourceStepError'],0)
            self.assertGreater(r['minDensity'],0);self.assertGreater(r['minT'],0)
            self.assertGreater(r['temperatureError']['L1'],1)
    def test_analytical_sources_and_failed_gate_classification(self):
        data=json.loads((STUDY/'data/processed/reproducibility_manifest.json').read_text())
        self.assertEqual(len(data['analyticalExperiments']),5)
        for r in data['analyticalExperiments']:
            snapshot=ROOT/r['declaredScriptSnapshot']
            for name,expected in r['source'].items():self.assertEqual(sha(snapshot/name),expected)
        failed=[r for r in data['experiments'] if r['scientificStatus']=='sourceEnergyGateFailed']
        self.assertEqual(len(failed),3)
        self.assertTrue(all(r['status']=='completed' for r in failed))
        self.assertEqual(sum(r['scientificStatus']=='superseded' for r in data['experiments']),11)
        self.assertEqual(data['statusCounts']['incomplete'],0)
if __name__=='__main__':unittest.main(verbosity=2)
