import sys,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from analysis import ridge,predict,solve_linear,choose,replay

class ModelTests(unittest.TestCase):
    def test_known_system(self):
        self.assertEqual(solve_linear([[2,0],[0,4]],[6,8]),[3,2])
    def test_constant_feature(self):
        model=ridge([[1],[1],[1]],[3,3,3]);self.assertAlmostEqual(predict(model,[1]),3)
    def test_linear_fit(self):
        model=ridge([[i] for i in range(5)],[2*i+1 for i in range(5)],penalty=0)
        self.assertAlmostEqual(predict(model,[6]),13)
    def test_cooldown(self):
        m=dict(variant='onlyImbalance',models={a:dict(mu=[1],scale=[1],beta=[-10,0]) for a in ['AC','AM','AH']},
            setup={a:0 for a in ['AC','AM','AH']},uncertainty={a:0 for a in ['AC','AM','AH']})
        f=dict(chemistrySeconds=.1,chemistryImbalance=2,lifetimeSteps=100,transportSeconds=.1,
            pressureSeconds=.1,processorFaces=10,nCells=100,timestepSeconds=1)
        self.assertEqual(choose(m,f,80,elapsed=1)[0],'A0')
        self.assertEqual(choose(m,f,80,elapsed=80)[0],'AC')
    def test_migration_cost_can_reverse_profitable_solver_delta(self):
        m=dict(variant='onlyImbalance',models={a:dict(mu=[1],scale=[1],beta=[-.1,0]) for a in ['AC','AM','AH']},
            setup={a:.2 for a in ['AC','AM','AH']},uncertainty={a:0 for a in ['AC','AM','AH']})
        f=dict(chemistrySeconds=.1,chemistryImbalance=2,lifetimeSteps=100,transportSeconds=.1,
            pressureSeconds=.1,processorFaces=10,nCells=100,timestepSeconds=.01)
        self.assertEqual(choose(m,f,4)[0],'A0')
        self.assertEqual(choose(m,f,4,variant='noMigration')[0],'AC')
    def test_uncertainty_guard(self):
        m=dict(variant='onlyImbalance',models={a:dict(mu=[1],scale=[1],beta=[-.1,0]) for a in ['AC','AM','AH']},
            setup={a:0 for a in ['AC','AM','AH']},uncertainty={a:.2 for a in ['AC','AM','AH']})
        f=dict(chemistrySeconds=.1,chemistryImbalance=2,lifetimeSteps=100,transportSeconds=.1,
            pressureSeconds=.1,processorFaces=10,nCells=100,timestepSeconds=.01)
        self.assertEqual(choose(m,f,4)[0],'A0')
        self.assertEqual(choose(m,f,4,variant='noUncertainty')[0],'AC')
    def replay_fixture(self,mesh_delta):
        m=dict(variant='full',models={a:dict(mu=[0]*5,scale=[1]*5,beta=[mesh_delta if a=='AM' else 1]+[0]*5) for a in ['AC','AM','AH']},
            setup={a:0 for a in ['AC','AM','AH']},uncertainty={a:0 for a in ['AC','AM','AH']})
        f=dict(chemistrySeconds=.1,chemistryImbalance=2,lifetimeSteps=100,transportSeconds=.1,
            pressureSeconds=.1,processorFaces=10,nCells=100,timestepSeconds=.01)
        actions={a:dict(valid=True,total=dict(median=t),extraction=.5) for a,t in zip(['A0','AC','AM','AH'],[10,9,8,12])}
        state=dict(regime='fixture',checkpoint='0.1',H=4,features=f,actions=actions,winner='AM',split='test')
        rows,_=replay([state],m,{})
        return next(r for r in rows if r['policy']=='wholeSolver')
    def test_mesh_replay_reuses_paid_weight_acquisition(self):
        row=self.replay_fixture(-3)
        self.assertEqual(row['chosen'],'AM');self.assertTrue(row['sharedWeightAcquisition'])
        self.assertEqual(row['featureWall'],0)
        self.assertAlmostEqual(row['cost']-row['inferenceWall'],8)
    def test_abstaining_replay_still_pays_for_its_features(self):
        row=self.replay_fixture(1)
        self.assertEqual(row['chosen'],'A0');self.assertFalse(row['sharedWeightAcquisition'])
        self.assertEqual(row['featureWall'],.5)
        self.assertAlmostEqual(row['cost']-row['inferenceWall'],10.5)

if __name__=='__main__':unittest.main()
