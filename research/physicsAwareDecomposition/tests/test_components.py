import math,sys,tempfile,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from models import weights,composite,metrics,correlation,break_even,lpt
from foamio import read_field,read_labels,write_scalar
class Models(unittest.TestCase):
    def test_uniform(self):self.assertEqual(weights([(.2,.3,0),(.6,.8,0)]),[1,1])
    def test_gaussian(self):self.assertAlmostEqual(weights([(.5,.5,0)],'gaussian',20,.1,(.5,.5,0))[0],21)
    def test_slab_and_half(self):
        pts=[(.25,.5,0),(.75,.5,0)]
        self.assertEqual(weights(pts,'half',9),[10,1])
        self.assertEqual(weights(pts,'slab',9,.1,(.25,.5,0)),[10,1])
    def test_invalid(self):
        for kw in [dict(width=0),dict(amplitude=-1),dict(amplitude=float('nan'))]:
            with self.assertRaises(ValueError):weights([(0,0,0)],**kw)
        for costs in [[-1],[float('inf')],[]]:
            with self.assertRaises(ValueError):composite(costs,1)
    def test_normalize_clip_smooth(self):
        self.assertEqual(composite([2,2],9),[1,1])
        self.assertEqual(composite([0,1000],100,lo=.1,hi=1.5),[.1,1.5])
        self.assertEqual(composite([0,2],1,alpha=0,previous=[1,1]),[1,1])
        self.assertEqual(composite([0,0],20),[1,1])
    def test_metrics(self):
        self.assertEqual(metrics([1,3])['imbalance'],1.5)
        self.assertEqual(metrics([0,0])['cv'],0)
        self.assertEqual(metrics([1,3])['idleProxy'],2)
    def test_prediction(self):
        self.assertAlmostEqual(correlation([1,2,3],[3,2,1]),-1)
        self.assertIsNone(correlation([1,1],[2,3]))
        self.assertEqual(break_even(2,3,.5),10)
        self.assertIsNone(break_even(2,3,0))
    def test_ideal(self):self.assertEqual(sorted(lpt([8,7,6,5,4],2)[0]),[13,17])
class Fields(unittest.TestCase):
    def test_roundtrip(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/'cellWeight';write_scalar(p,[1,2,3],[('a','patch')]);self.assertEqual(read_field(p,3),[1,2,3])
    def test_uniform_vector(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/'U';p.write_text('internalField uniform (1 2 3);');self.assertEqual(read_field(p,2),[(1,2,3)]*2)
    def test_nongreedy(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/'T';p.write_text('internalField nonuniform List<scalar> 2 (1 2); boundaryField {a {value nonuniform List<scalar> 2 (3 4);}}');self.assertEqual(read_field(p,2),[1,2])
    def test_reject_wrong_size(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/'T';p.write_text('internalField nonuniform List<scalar> 3 (1 2);')
            with self.assertRaises(ValueError):read_field(p)
    def test_label_header(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/'list';p.write_text('/* fake ( comments */ FoamFile {version 2.0;} 3 (0 5 8)')
            self.assertEqual(read_labels(p),[0,5,8])
if __name__=='__main__':unittest.main()
