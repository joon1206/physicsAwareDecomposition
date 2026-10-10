"""Executable-data acceptance gates; fails when required evidence is absent."""
from pathlib import Path
import json,hashlib,unittest,sys,math
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
from thermo_reference import parse_nasa,ha,RU
class AuditTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.summary={r['name']:r for r in json.loads((ROOT/'data/processed/audit_summary.json').read_text())}
        cls.gates=json.loads((ROOT/'data/processed/gates.json').read_text())
        cls.budgets=json.loads((ROOT/'data/processed/step_budgets.json').read_text())
    def test_published_artifact_frozen(self):
        frozen=json.loads((ROOT/'docs/actionStudy_freeze.json').read_text())
        for p,s in frozen['files'].items():
            with self.subTest(file=p):self.assertEqual(hashlib.sha256((ROOT.parents[1]/p).read_bytes()).hexdigest(),s)
    def test_independent_thermodynamics(self):
        for name,r in self.summary.items():
            with self.subTest(case=name):
                self.assertLess(abs(r['independentNativeEnergyDifference']),1e-12)
                self.assertLess(abs(r['thermoInventoryDifference']),1e-10)
    def test_every_equation_budget_closes(self):
        for name,rows in self.budgets.items():
            if not rows:continue
            r=self.summary[name]
            with self.subTest(case=name):
                self.assertEqual(len(rows),r['steps'])
                self.assertLess(max(abs(x['closure']) for x in rows),1e-12)
                self.assertLess(abs(math.fsum(x['DE'] for x in rows)-(r['end']['E_stored']-r['initial']['E_stored'])),1e-12)
    def test_closed_static_machine_precision(self):
        self.assertLess(self.summary['A_static']['absoluteEnergyDrift'],1e-13)
    def test_mass_elements_species_positivity(self):
        for name,g in self.gates.items():
            with self.subTest(case=name):
                for key in ['mass','elements','normalization','positivity']:
                    if key in g:self.assertTrue(g[key],key)
    def test_instrumentation_has_no_field_effect(self):
        for name in ['F_ledger_off','F_original','F_balanced']:
            for field,norm in self.gates[name]['fieldNorms'].items():
                with self.subTest(case=name,field=field):self.assertEqual(norm['Linf'],0)
    def test_serial_and_restart_equivalence(self):
        for name in ['F_serial','F_restart']:
            self.assertTrue(self.gates[name]['equivalence'])
            self.assertLess(self.gates[name]['fieldNorms']['T']['Linf'],1e-4)
    def test_documented_drift_reproduced(self):
        self.assertAlmostEqual(self.summary['F_dt2e-06_p1']['signedEnergyDrift'],-.17388659758380884,places=10)
    def test_closed_transports_and_residuals_are_small(self):
        r=self.summary['F_dt2e-06_p1']['cumulativeTerms']
        self.assertLess(abs(r['Dequation']),1e-10)
        # Tiny initially constructed cyclic-flux mismatch is recorded, not zeroed.
        self.assertLess(abs(r['Dtransport']),1e-7)
    def test_exact_solution_and_conservative_reference(self):
        data=json.loads((ROOT/'data/processed/exact_wave.json').read_text())
        for r in data['records']:
            self.assertLess(abs(r['massDrift']),1e-9)
            if r['solver']=='rhoCentralFoam':self.assertLess(abs(r['signedEnergyDrift']),1e-11)
        pressure=[r for r in data['spatialOrders'] if r['solver']=='reactingEnergyAudit']
        self.assertEqual(len(pressure),2)
        for r in pressure:self.assertGreater(r['T_L1_order'],.9)
    def test_stage_snapshots_preserve_rank_count_and_order(self):
        slices=json.loads((ROOT/'data/processed/stage_slices.json').read_text())
        for name,rows in slices.items():
            for row in rows:
                with self.subTest(case=name,step=row['step'],checkpoint=row['checkpoint']):
                    self.assertEqual(row['ranks'],self.summary[name]['ranks'])
        first=sorted([r for r in slices['F_dt2e-06_p1'] if r['step']==1],key=lambda r:r['checkpoint'])
        self.assertEqual([r['stage'] for r in first].count('rho_thermo'),2)
        self.assertEqual(first[0]['stage'],'timestep_start')
        self.assertEqual(first[-1]['stage'],'timestep_end')
if __name__=='__main__':unittest.main(verbosity=2)
