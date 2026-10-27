"""Local FTS5 query. Example: python scripts/search_goa_corpus.py 'khazan OR tenancy'."""
import argparse,json,sqlite3
from pathlib import Path
ap=argparse.ArgumentParser();ap.add_argument('query');ap.add_argument('--limit',type=int,default=10);a=ap.parse_args()
db=sqlite3.connect(Path(__file__).resolve().parents[1]/'corpus/search.sqlite');db.row_factory=sqlite3.Row
try:
 rows=db.execute('SELECT s.title,s.url,s.publisher_class,s.legal_currency,p.source_id,p.page,p.passage,p.text_origin,s.raw_path,s.text_path,snippet(passages,4,"[", "]", " … ",40) AS excerpt FROM passages p JOIN sources s ON s.id=p.source_id WHERE passages MATCH ? ORDER BY bm25(passages) LIMIT ?',(a.query,a.limit)).fetchall()
 print(json.dumps([dict(r) for r in rows],ensure_ascii=False,indent=2))
except sqlite3.OperationalError as e:ap.error(str(e))
