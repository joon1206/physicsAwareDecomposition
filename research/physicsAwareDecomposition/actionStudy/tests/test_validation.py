import tempfile,unittest
from pathlib import Path
from validation import numerical_gate

class AdmissibilityTests(unittest.TestCase):
    def fixture(self,directory,rho='1 1',temperature='800 800'):
        directory.mkdir()
        values={'T':temperature,'p':'101325 101325','rho':rho,'h':'100 100','Qdot':'0 0','A':'.2 .2','B':'.8 .8'}
        for name,text in values.items():
            (directory/name).write_text(f'internalField nonuniform List<scalar>\n2\n( {text} );\n')
        (directory/'U').write_text('internalField nonuniform List<vector>\n2\n( (0 0 0) (0 0 0) );\n')
    def test_identical_negative_density_is_not_a_valid_trajectory(self):
        with tempfile.TemporaryDirectory() as root:
            paths=[Path(root)/name for name in ['reference','candidate']]
            for path in paths:self.fixture(path,rho='-.1 1')
            gate=numerical_gate(*paths,dict(nCells=2,species=['A','B']))
            self.assertFalse(gate['pass_']);self.assertEqual(gate['fields']['rho']['Linf'],0)
            self.assertFalse(gate['fields']['rho']['admissible'])
    def test_nan_after_a_finite_cell_cannot_hide_in_maximum_norm(self):
        with tempfile.TemporaryDirectory() as root:
            paths=[Path(root)/name for name in ['reference','candidate']]
            for path in paths:self.fixture(path,temperature='800 nan')
            with self.assertRaisesRegex(ValueError,'nonfinite field'):
                numerical_gate(*paths,dict(nCells=2,species=['A','B']))
if __name__=='__main__':unittest.main()
