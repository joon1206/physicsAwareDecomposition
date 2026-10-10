"""Scientific continuation checks, independent of the unchanged historical 38."""
from pathlib import Path
import csv,json,math,unittest
from thermo_continuity import sha,properties,CONTROL
from thermo_reference import parse_nasa
ROOT=Path(__file__).resolve().parents[1];STUDY=ROOT/'candidateStudy';P=STUDY/'data/processed';RAW=STUDY/'data/raw'
def read(n):return json.loads((P/n).read_text())

class Verification(unittest.TestCase):
    def test_continuity_and_reference_controls(self):
        m=json.loads((CONTROL/'manifest.json').read_text());base=parse_nasa(ROOT/m['sourcePath'])
        self.assertEqual(sha(ROOT/m['sourcePath']),m['sourceSHA256'])
        self.assertEqual(sha(CONTROL/'driver_snapshot.py'),m['driverSHA256'])
        for mode,control in m['controls'].items():
            self.assertEqual(sha(CONTROL/f'{mode}.dat'),control['sha256'])
            actual=parse_nasa(CONTROL/f'{mode}.dat')
            for name,s in actual.items():
                self.assertEqual(s['low'],base[name]['low'])
                if mode=='HS':self.assertEqual(s['high'][:5],base[name]['high'][:5])
                a,b=properties(s['low'],s['mid']),properties(s['high'],s['mid'])
                self.assertLess(abs(a['h']-b['h']),3e-5)
                self.assertLess(abs(a['s']-b['s']),4e-9)
                if mode=='CpHS':self.assertLess(abs(a['Cp']-b['Cp']),1e-9)

    def test_all_declared_mechanisms_and_retained_sets(self):
        a=read('mechanism_continuity_audit.json');names={r['name']:r for r in a['mechanisms']}
        self.assertEqual(set(names),{'legacyH2','installedGRI','Alzueta2023_baseline','H2_HS','H2_CpHS'})
        self.assertEqual((names['Alzueta2023_baseline']['nSpecies'],names['Alzueta2023_baseline']['nReactions']),(42,281))
        self.assertEqual(len(a['retainedCoefficientSets']),6)
        for r in a['retainedCoefficientSets']:
            self.assertEqual(sha(ROOT/r['sourcePath'].replace('\\','/')),r['sourceSHA256']);self.assertTrue(r['usedBy'])

    def test_reaction_elements_and_independent_properties(self):
        for r in read('mechanism_continuity_audit.json')['mechanisms']:
            self.assertLess(r['reactionElementResidualAtoms'],1e-12)
            self.assertLess(r['independentCanteraPropertyMaxRelativeDifference'],1e-11)
            self.assertEqual(len(r['species']),r['nSpecies'])
            mids={s['Tcommon'] for s in r['species']}
            self.assertEqual(len(r['reactions']),r['nReactions']*len(mids))
            self.assertEqual({(a['index'],a['Tcommon']) for a in r['reactions']},{(i,t) for i in range(r['nReactions']) for t in mids})

    def test_complete_matched_h2_matrix(self):
        rows=read('clean_thermo_campaign.json');self.assertEqual(len(rows),18)
        self.assertTrue(all('signedEnergyDrift' in r for r in rows))
        self.assertEqual(len({r['name'] for r in rows}),18)
        for r in rows:
            self.assertTrue((RAW/r['name']/'result.json').exists());self.assertEqual(r['ranks'],4)
            self.assertEqual(r['nCells'],256);self.assertAlmostEqual(r['steps']*r['dt'],240e-6,places=14)

    def test_matched_native_inputs(self):
        for r in read('clean_thermo_campaign.json'):
            if r['thermoControl']=='legacy':continue
            case=RAW/r['name'];suffix='_cvSource_rtol1e-10_dfdt0' if r['sourcePathControl']=='CV' else ''
            base=RAW/f"F_{r['mode']}_dt{r['dt']:g}_s1_g0_o1_p1{suffix}"
            self.assertEqual(sha(case/'chemkin/chem.inp'),sha(base/'chemkin/chem.inp'))
            for file in (base/'0').iterdir():
                if file.is_file():self.assertEqual(sha(case/'0'/file.name),sha(file),str(file))
            for name in ['thermophysicalProperties','combustionProperties','chemistryProperties','turbulenceProperties']:
                self.assertEqual(sha(case/'constant'/name),sha(base/'constant'/name),name)
            self.assertEqual(sha(case/'system/fvSchemes'),sha(base/'system/fvSchemes'))
            self.assertEqual(sha(case/'system/fvSolution'),sha(base/'system/fvSolution'))

    def test_eight_term_and_corrected_cell_ledgers(self):
        for r in read('clean_thermo_campaign.json')+read('clean_gri_campaign.json'):
            self.assertLess(r['maxStepClosure'],1e-12);self.assertLess(r['maxCellClosure'],1e-12)
            change=r['end']['E_stored']-r['initial']['E_stored']
            self.assertLess(abs(math.fsum(r['cellCumulativeTerms'].values())-change),2e-12)
            if r['mode']=='none':self.assertLess(abs(math.fsum(r['cumulativeTerms'].values())-change),2e-12)
            self.assertLess(abs(r['independentNativeEnergyDifference']),1e-12)
            self.assertLess(abs(r['thermoInventoryDifference']),1e-10)
            self.assertLess(r['maxEOSRelative'],1e-10)

    def test_density_defect_persists_h2_and_gri(self):
        for rows in [read('clean_thermo_campaign.json'),read('clean_gri_campaign.json')]:
            group=[r for r in rows if r.get('sourcePathControl','native')=='native']
            for dt in [2e-6,1e-6]:
                legacy=next(r for r in group if r['dt']==dt and r['thermoControl']=='legacy')
                clean=next(r for r in group if r['dt']==dt and r['thermoControl']=='CpHS')
                pair=lambda r:r['cellCumulativeTerms']['DrhoH']+r['cellCumulativeTerms']['DrhoC']
                self.assertGreater(abs(pair(clean)),1e-4)
                self.assertLess(abs(pair(clean)-pair(legacy))/abs(pair(legacy)),1e-3)

    def test_gri_kinetics_and_field_equivalence(self):
        rows=read('clean_gri_campaign.json');self.assertEqual(len(rows),4)
        for dt in [2e-6,1e-6]:
            a,b=[RAW/next(r['name'] for r in rows if r['dt']==dt and r['thermoControl']==t) for t in ['legacy','CpHS']]
            self.assertEqual(sha(a/'chemkin/chem.inp'),sha(b/'chemkin/chem.inp'))
            for file in (a/'0').iterdir():
                if file.is_file():self.assertEqual(sha(file),sha(b/'0'/file.name))
            self.assertEqual(sha(a/'system/fvSolution'),sha(b/'system/fvSolution'))
            original,continuous=parse_nasa(a/'chemkin/therm.dat'),parse_nasa(b/'chemkin/therm.dat')
            for name,s in continuous.items():
                self.assertEqual(s['low'],original[name]['low'])
                self.assertEqual(s['high'][1:5],original[name]['high'][1:5])
                left,right=properties(s['low'],s['mid']),properties(s['high'],s['mid'])
                self.assertLess(abs(left['Cp']-right['Cp']),1e-8)
                self.assertLess(abs(left['h']-right['h']),1e-3)
                self.assertLess(abs(left['s']-right['s']),1e-7)

    def test_direct_clean_branch_floor_removed(self):
        rows=read('clean_thermo_branch.json');self.assertEqual(len(rows),18)
        self.assertTrue(all(r['relativeEnergyChange']<1e-10 for r in rows))
        self.assertEqual(sum(r['Tinitial']==999 for r in rows),6)
        for r in rows:self.assertTrue((RAW/r['name']/'probe_result.json').exists())

    def test_continuous_source_failures_are_not_hidden(self):
        rows=read('clean_thermo_campaign.json')
        for r in rows:
            if r['sourcePathControl']!='CV':continue
            events=[]
            for fp in (RAW/r['name']).glob('**/cvChemistry/rank*.csv'):
                with fp.open() as f:events.extend({k:float(v) for k,v in row.items()} for row in csv.DictReader(f))
            errors=[abs(x['energyFinal']-x['energyInitial'])/max(abs(x['energyInitial']),1) for x in events]
            self.assertEqual(r['sourceCalls'],len(errors));self.assertEqual(r['sourceGate'],1e-10)
            self.assertEqual(r['failedSourceEnergyCalls'],sum(e>1e-10 for e in errors))
            self.assertEqual(r['maxSourceRelativeEnergyChange'],max(errors))
            if r['mode']=='none' and r['thermoControl']!='legacy':
                self.assertGreater(r['failedSourceEnergyCalls'],0);self.assertLess(max(errors),1e-8)

    def test_independent_cv_cp_controls_and_event_identity(self):
        records=read('clean_thermo_reference.json')['records'];self.assertEqual(len(records),90)
        for r in records:
            self.assertTrue(r['reactorClone'] is False)
            self.assertLess(r['maxElementResidual'],1e-11)
            if r['rtol']==1e-12 and r['Tinitial']==999:
                self.assertLess(r['jumpSubtractedRelativeError'],2e-12)
                if r['mechanism'] in ['legacy','GRI']:self.assertGreater(r['relativeInvariantChange'],1e-8)
                if r['mechanism'] in ['HS','CpHS']:self.assertLess(r['relativeInvariantChange'],1e-10)

    def test_projection_falsification_and_conditional_gates(self):
        rows=read('invariant_projection_valid_data.json')['records'];self.assertEqual(len(rows),48)
        eligible=[r for r in rows if not r['projected']['failed']]
        self.assertEqual(len(eligible),40)
        self.assertEqual(sum(r['projected']['temperatureError']>r['temperatureError'] for r in eligible),25)
        self.assertEqual(sum(r['projected']['gatesPass'] for r in eligible),38)
        for r in eligible:
            pr=r['projected'];self.assertEqual(pr['speciesErrorMax'],r['speciesErrorMax'])
            self.assertEqual(pr['speciesChangeMax'],0)
            self.assertLess(pr['relativeCanteraInvariantResidual'],1e-10)
            independently_pass=(abs(r['massResidual'])<=1e-12 and r['elementResidual']<=1e-12 and r['minY']>=0 and abs(pr['EOSResidual'])/pr['p']<=1e-10 and pr['T']>0)
            self.assertEqual(pr['gatesPass'],independently_pass)
        self.assertTrue(all(r['minY']<0 for r in rows if r['projected']['failed']))

    def test_abstract_map_algebra_and_post_map_counterexample(self):
        result=read('thermochemical_abstract_map.json');self.assertEqual(len(result['records']),18)
        for r in result['records']:
            self.assertLess(abs(r['specificInvariantResidual']),1e-8)
            self.assertLess(abs(r['finiteSensibleIdentityResidual']),1e-8)
            self.assertLess(abs(r['finiteRRCancellation']),1e-8)
            self.assertLess(r['maxElementResidual'],1e-14);self.assertLess(abs(r['massResidual']),1e-14)
            self.assertGreaterEqual(r['minY'],0)
            self.assertLess(abs(r['formationOnlyCVResidual']+r['formationOnlyCVPressureChange']),1e-6)
            self.assertGreater(abs(r['formationOnlyCVResidual']),100)
        c=result['postMapCounterexample'];self.assertEqual(c['massChange'],0)
        self.assertLess(c['maxSpeciesInventoryChange'],1e-14)
        self.assertGreater(abs(c['energyChange']),1000);self.assertLess(abs(c['identityClosure']),1e-8)

    def test_reference_parser_failures_preserved(self):
        failures=list(RAW.glob('CleanReference_Alzueta*/failure.json'));self.assertEqual(len(failures),14)
        self.assertTrue(all(not (f.parent/'result.json').exists() for f in failures))
        v5=next(f.parent for f in failures if 'syntax5' in f.parent.name)
        self.assertIn('PLOG',(v5/'solver.log').read_text())

    def test_primary_method_snapshots_and_five_decisions(self):
        directory=ROOT/'sourceAudit/thermoInvariants_v1'
        m=json.loads((directory/'manifest.json').read_text())
        self.assertEqual(len(m['records']),7)
        for r in m['records']:
            self.assertNotIn('error',r);self.assertEqual(sha(directory/r['name']),r['sha256'])
        decisions=read('thermochemical_candidate_decision.json')['summary']['decisions']
        self.assertEqual(set(decisions),{'1','2','3','4','5'})
        self.assertTrue(all(v.startswith('Reject') for v in decisions.values()))

    def test_report_hashes_and_interaction_completeness(self):
        source=read('clean_thermo_report_sources.json');self.assertEqual(source['completedMatchedRecords'],18)
        self.assertEqual(source['driverSHA256'],sha(ROOT/'scripts/clean_thermo_report.py'))
        for n,h in source['inputs'].items():self.assertEqual(sha(P/n),h)
        interactions=read('clean_thermo_interactions.json')['records']
        self.assertEqual(len(interactions),4*13)
        self.assertTrue(any(abs(r['interaction'])>1e-9 for r in interactions))

    def test_phase_manifest_and_raw_snapshot_integrity(self):
        m=read('thermochemical_phase_manifest.json');self.assertEqual(len(m['nativeMatched']),22)
        self.assertEqual(len(m['nativeReferenceParserFailures']),14)
        for r in m['nativeMatched']:
            self.assertEqual(r['status'],'completed')
            expected='sourceEnergyGateFailed' if r['failedSourceCalls'] else 'sourceGatePassed' if r['sourceCalls'] else 'sourceEndpointNotTraced'
            self.assertEqual(r['scientificStatus'],expected)
        for n,h in m['processedSHA256'].items():self.assertEqual(sha(P/n),h)
        for r in m['otherRetained']:
            for n,h in r['files'].items():self.assertEqual(sha(RAW/r['name']/n),h)

if __name__=='__main__':unittest.main(verbosity=2)
