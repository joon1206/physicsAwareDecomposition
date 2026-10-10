"""Verify DOI/title/authors against primary registration-agency metadata."""
import datetime,difflib,html,json,os,re,urllib.parse,urllib.request
from pathlib import Path
ROOT=Path(os.environ.get('PAD_ACTION_ROOT',Path(__file__).resolve().parents[1]))
def fetch(url):
    request=urllib.request.Request(url,headers={'User-Agent':'ReactiveActionOracle/1.0 bibliographic-verification'})
    with urllib.request.urlopen(request,timeout=20) as response:return json.load(response)
def main():
    catalog=json.loads((ROOT/'docs/literature.json').read_text());rows=[]
    for record in catalog:
        row=dict(id=record['id'],searchedDOI=record.get('DOI'),searchedTitle=record['title'],checked=datetime.date(2026,10,5).isoformat())
        doi=record.get('DOI')
        if not doi:row.update(status='No DOI supplied; official-page or primary-preprint metadata is checked separately')
        else:
            try:
                if doi.startswith(('10.5281/','10.48550/')):
                    item=fetch('https://api.datacite.org/dois/'+urllib.parse.quote(doi,safe=''))['data']['attributes'];title=item['titles'][0]['title'];authors=[r['name'] for r in item['creators']];agency='DataCite'
                    publication_date=item.get('publicationYear')
                else:
                    item=fetch('https://api.crossref.org/works/'+urllib.parse.quote(doi,safe=''))['message'];title=item['title'][0];authors=[' '.join(x for x in [r.get('given',''),r.get('family','')] if x) for r in item.get('author',[])];agency='Crossref'
                    publication_date=item.get('published',item.get('issued',{})).get('date-parts')
                title=' '.join(html.unescape(re.sub('<[^>]+>','',title)).split())
                ratio=difflib.SequenceMatcher(None,record['title'].lower().replace('–','-'),title.lower().replace('–','-')).ratio()
                row.update(status='Primary DOI registry returned metadata',agency=agency,title=title,authors=authors,titleSimilarity=ratio,DOI=doi,
                    registryPublicationDate=publication_date,
                    confidence='High for DOI/title/author registration; does not verify full-text quantitative claims')
            except Exception as error:row.update(status='Metadata access failed',error=str(error),confidence='No additional verification inferred')
        rows.append(row);print('BIBLIOGRAPHY',row['id'],row['status'],row.get('titleSimilarity',''),flush=True)
        (ROOT/'docs/bibliography_metadata_verification.json').write_text(json.dumps(rows,indent=2,ensure_ascii=False))
    print('Checked',len(rows),'bibliographic records against stated sources.')
if __name__=='__main__':main()
