"""Regression for the inherited-timeIndex failure and rank-local endpoint CSV."""
import csv,sys,tempfile,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from caseFactory import assert_endpoint,set_control
from foamio import read_field

class EndpointTests(unittest.TestCase):
    def fixture(self,root,actual=54e-6,rows=7):
        (root/'system').mkdir();set_control(root,start=40e-6,steps=7,dt=2e-6)
        for rank in range(2):
            base=root/f'processor{rank}';directory=base/format(actual,'.12g');directory.mkdir(parents=True)
            for field in ['T','h','rho']:(directory/field).write_text('written endpoint')
            output=base/'postProcessing/performance';output.mkdir(parents=True)
            with (output/f'rank{rank:04d}.csv').open('w') as f:
                writer=csv.DictWriter(f,fieldnames=['time','timeIndex','rank']);writer.writeheader()
                for i in range(rows):writer.writerow(dict(time=40e-6+(i+1)*2e-6,timeIndex=21+i,rank=rank))
    def test_inherited_index_endpoint(self):
        with tempfile.TemporaryDirectory() as name:
            root=Path(name);self.fixture(root);assert_endpoint(root,2)
    def test_interior_checkpoint_rejected(self):
        with tempfile.TemporaryDirectory() as name:
            root=Path(name);self.fixture(root,actual=42e-6)
            with self.assertRaises(RuntimeError):assert_endpoint(root,2)
    def test_incomplete_csv_rejected(self):
        with tempfile.TemporaryDirectory() as name:
            root=Path(name);self.fixture(root,rows=6)
            with self.assertRaises(RuntimeError):assert_endpoint(root,2)
    def test_field_parser_reads_uniform_and_nonuniform(self):
        with tempfile.TemporaryDirectory() as name:
            path=Path(name)/'T';path.write_text('internalField uniform 700;')
            self.assertEqual(read_field(path,3),[700.]*3)
            path.write_text('internalField nonuniform List<scalar>\n3\n(1\n2\n3\n);')
            self.assertEqual(read_field(path,3),[1.,2.,3.])

if __name__=='__main__':unittest.main()
