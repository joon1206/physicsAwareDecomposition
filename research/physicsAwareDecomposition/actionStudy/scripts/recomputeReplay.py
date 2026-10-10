"""Refresh cost accounting without fitting or changing any frozen coefficient."""
import collections,hashlib,json,random,statistics
from analysis import ROOT,replay
def main():
    path=ROOT/'data/processed/model.json';fingerprint=hashlib.sha256(path.read_bytes()).hexdigest()
    states=json.loads((ROOT/'data/processed/oracle_summary.json').read_text())
    model=json.loads(path.read_text());ablations=json.loads((ROOT/'data/processed/ablation_models.json').read_text())
    decisions,results=replay(states,model,ablations)
    raw=json.loads((ROOT/'data/processed/oracle_raw.json').read_text());groups=collections.defaultdict(list)
    for row in raw:groups[(row['regime'],row['checkpoint'],row['horizonSteps'],row['action'])].append(row['totalWall'])
    rng=random.Random(390519)
    for policy,metrics in results['test'].items():
        selected=[r for r in decisions if r['split']=='test' and r['policy']==policy];ratios=[]
        for _ in range(4000):
            numerator=denominator=0.
            for row in selected:
                key=(row['regime'],row['checkpoint'],row['H']);baseline=groups[key+('A0',)]
                baseline_median=statistics.median(rng.choices(baseline,k=len(baseline)))
                if row['chosen']=='A0':candidate=baseline_median
                else:
                    values=groups[key+(row['chosen'],)];candidate=statistics.median(rng.choices(values,k=len(values)))
                numerator+=baseline_median;denominator+=candidate+row['featureWall']+row['inferenceWall']
            ratios.append(numerator/denominator)
        ratios.sort();metrics['aggregateSpeedupCI']=[ratios[100],ratios[3900]]
        metrics['CIScope']='Within-state resampling of the same six fixed held-out checkpoint states, conditional on frozen policy choices, observed oracle labels and fixed decision-overhead estimates; excludes case-population and model-fitting uncertainty. A0 uses shared baseline draws.'
    for name,data in [('policy_decisions',decisions),('policy_summary',results)]:
        (ROOT/f'data/processed/{name}.json').write_text(json.dumps(data,indent=2))
    if hashlib.sha256(path.read_bytes()).hexdigest()!=fingerprint:raise RuntimeError('frozen model changed')
    (ROOT/'data/processed/replay_accounting.json').write_text(json.dumps(dict(modelSHA256=fingerprint,modelRefit=False,
        correction='Feature-driven AM/AH reuse the required weight acquisition already charged in J; only additional inference is added. A0/AC selections pay feature acquisition. Each inference timer executes the corresponding frozen policy.'),indent=2))
    print('REFRESHED replay accounting; frozen model unchanged',fingerprint)
if __name__=='__main__':main()
