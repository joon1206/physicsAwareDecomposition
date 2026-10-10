"""Compact campaign status without reading retained CFD fields."""
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
print('completed oracle:',len(list((ROOT/'data/raw/oracle').glob('*/*/manifest.json'))),flush=True)
if (ROOT/'data/processed/campaign_status.json').exists():print((ROOT/'data/processed/campaign_status.json').read_text(),flush=True)
for p in sorted((ROOT/'data/raw/campaignLogs').glob('*.log')):
    print(p.name, '\n'.join(p.read_text().splitlines()[-4:]),flush=True)
