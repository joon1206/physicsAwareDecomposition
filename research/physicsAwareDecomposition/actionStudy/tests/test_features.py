import math,sys,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from features import correlation,top_overlap,normalize,center

class FeatureTests(unittest.TestCase):
    def test_correlation_identity(self):self.assertAlmostEqual(correlation([1,2,4],[1,2,4]),1)
    def test_correlation_reverse(self):self.assertAlmostEqual(correlation([1,2,3],[3,2,1]),-1)
    def test_constant_identical(self):self.assertEqual(correlation([2,2],[2,2]),1)
    def test_constant_changed(self):self.assertEqual(correlation([2,2],[3,3]),0)
    def test_mismatch(self):
        with self.assertRaises(ValueError):correlation([1],[1,2])
    def test_top_identical(self):self.assertEqual(top_overlap([0,1,9],[0,1,9]),1)
    def test_top_disjoint(self):self.assertEqual(top_overlap([9,0,1],[0,9,1]),0)
    def test_uniform_weight(self):self.assertEqual(normalize([3,3]),[1,1])
    def test_zero_weight(self):self.assertTrue(all(math.isfinite(x) for x in normalize([0,0])))
    def test_mean_normalization(self):self.assertAlmostEqual(sum(normalize([1,2,3]))/3,1)
    def test_clipping(self):self.assertTrue(all(.5<=x<=1.5 for x in normalize([0,0,100],upper=1.5,lower=.5)))
    def test_invalid_cost(self):
        for costs in [[-1],[float('nan')],[float('inf')],[]]:
            with self.assertRaises(ValueError):normalize(costs)
    def test_center_zero(self):self.assertEqual(center([0]*4,2,2),(.01,.004))
    def test_center_periodic(self):
        x,y=center([1,0,0,1],4,1)
        self.assertTrue(x<1e-10 or abs(x-.02)<1e-10)
        self.assertAlmostEqual(y,.004)

if __name__=='__main__':unittest.main()
