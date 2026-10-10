"""Verify that every export/source slice regenerates byte-for-byte."""
import hashlib,json
from caseFactory import ROOT,PAD,command

def fingerprint():
    index=json.loads((ROOT/'figures/index.json').read_text())
    return {r['name']+'.'+ext:hashlib.sha256((ROOT/'figures'/(r['name']+'.'+ext)).read_bytes()).hexdigest()
            for r in index for ext in ['png','pdf','svg','source.json']}

def main():
    script=PAD/'actionStudy/scripts/generateFigures.sh'
    command(['bash',script],PAD,ROOT/'data/raw/build/figureFirstGeneration.log',timeout=300)
    first=fingerprint()
    command(['bash',script],PAD,ROOT/'data/raw/build/figureRegeneration.log',timeout=300)
    second=fingerprint()
    mismatches=[key for key in first if first[key]!=second.get(key)]
    result=dict(passed=not mismatches and len(first)==len(second),files=first,mismatches=mismatches,
                scope='Two sequential independent plotting processes on the same pinned host/environment and unchanged processed data. Every PNG/PDF/SVG/source slice is hashed; cross-version font/library equality is not claimed.')
    (ROOT/'docs/figure_reproduction.json').write_text(json.dumps(result,indent=2))
    assert result['passed'],mismatches
    print('PASSED byte-identical scientific figure reproduction:',len(first),'files')

if __name__=='__main__':main()
