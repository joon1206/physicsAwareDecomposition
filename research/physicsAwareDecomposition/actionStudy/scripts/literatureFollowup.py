"""Retain small primary-source documents from the final novelty search."""
import datetime,hashlib,json,os,urllib.request
from pathlib import Path
ROOT=Path(os.environ.get('PAD_ACTION_ROOT',Path(__file__).resolve().parents[1]))
SOURCES={
    'drama2000.pdf':'https://chriswalshaw.co.uk/papers/fulltext/BasermannApMM00.pdf',
    'drama1999_cost_model.pdf':'https://chriswalshaw.co.uk/papers/fulltext/BasermannTR99.pdf',
    'fluent2025_partitioning.html':'https://ansyshelp.ansys.com/public/Views/Secured/corp/v252/en/flu_ug/flu_ug_GridPartition.html',
    'openfpm_examples.html':'https://ppmcore.mpi-cbg.de/vector-example/',
}
def main():
    destination=ROOT/'data/raw/literatureFollowup';destination.mkdir(parents=True,exist_ok=True)
    rows=[]
    for name,url in SOURCES.items():
        row=dict(url=url,path=str((destination/name).relative_to(ROOT)),checkedUTC=datetime.datetime.now(datetime.timezone.utc).isoformat())
        try:
            request=urllib.request.Request(url,headers={'User-Agent':'ReactiveActionOracle/1.0 primary-source-research'})
            with urllib.request.urlopen(request,timeout=20) as response:
                content=response.read(5_000_001);row['contentType']=response.headers.get('Content-Type')
            if len(content)>5_000_000:raise ValueError('bounded primary document exceeds 5 MB')
            if name.endswith('.pdf') and not content.startswith(b'%PDF'):raise ValueError('response is not a PDF')
            (destination/name).write_bytes(content)
            row.update(status='Downloaded primary source',bytes=len(content),SHA256=hashlib.sha256(content).hexdigest())
        except Exception as error:row.update(status='Fetch failed; web verification access retained separately',error=str(error))
        rows.append(row);print('PRIMARY FOLLOWUP',name,row['status'],flush=True)
    (ROOT/'docs/fulltext_access_followup.json').write_text(json.dumps(rows,indent=2))
if __name__=='__main__':main()
