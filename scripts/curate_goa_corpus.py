"""Refine provenance from archived indexes and audit local corpus integrity.
Does not fetch, rewrite originals, or determine legal currency.
"""
import argparse,collections,hashlib,json,re,sqlite3
from pathlib import Path
from urllib.parse import urlsplit,unquote
from bs4 import BeautifulSoup
from ingest_goa_corpus import ROOT,C,canonical,dump,extract,publisher_class,topic_tags,build_index

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--audit-only',action='store_true');args=ap.parse_args()
 rows=[json.loads(p.read_text()) for p in sorted((C/'metadata').glob('*.json'))]
 labels={}
 for r in rows:
  if r.get('format')!='html' or not r.get('raw_path'):continue
  soup=BeautifulSoup((ROOT/r['raw_path']).read_bytes(),'lxml')
  for holder in soup.select('.document_holder'):
   n=holder.select_one('.doc_name')
   if not n:continue
   for a in holder.select('a[href]'):
    u=canonical(a['href'],r.get('final_url',r['url']))
    labels[u]={'title':n.get_text(' ',strip=True),'discovery_context':holder.get_text(' ',strip=True),'source_listing_dates':re.findall(r'Date\s*:\s*(\d{2}/\d{2}/\d{4})',holder.get_text(' ',strip=True)),'title_evidence_source':r['url']}
 overrides=json.loads((C/'research'/'curation-overrides.json').read_text()) if (C/'research'/'curation-overrides.json').exists() else {}
 if not args.audit_only:
  for r in rows:
   if r['status']!='downloaded':continue
   if r['url'] in labels:
    evidence=labels[r['url']];r['original_title_hint']=r.get('title_hint');r.update(evidence);r['title_hint']=evidence['title']
    r['source_listing_date_note']='Portal listing date, not independently verified legal publication or commencement'
   # Re-extract HTML with archive-aware DOM selection; PDF native text remains untouched.
   if r.get('format')=='html':r.update(extract(r,(ROOT/r['raw_path']).read_bytes()))
   title=r.get('title','');u=r['url'];t=(ROOT/r['text_path']).read_text() if r.get('text_path') else ''
   if title.lower() in ['download','view','here','pdf','click here','act','rules','']:
    r['title']=unquote(Path(urlsplit(u).path).name).replace('-',' ').replace('_',' ')
    r['title_quality']='URL filename fallback; verify document heading'
   else:r['title_quality']='source discovery or document heading; not independently verified'
   r['publisher_class']=publisher_class(u)
   r['inclusion_status']='included'
   r['corpus_role']='legacy_site_baseline' if r['publisher_class']=='act_for_goa' else 'research_source'
   if re.search(r'log_file_|connection-test|page-with-(?:no|left|right)-sidebar|default-template|shortcodes|elements(?:/|$)|typography|accordion|button|carousel|tabs(?:/|$)|icon(?:s)?(?:/|$)|portfolio-(?:single|masonry|gallery|standard)|blog-(?:masonry|standard)|countdown|pie-chart|progress-bar|testimonials|pricing-table|social-icons',u,re.I):
    r['inclusion_status']='excluded_nonresearch';r['exclusion_reason']='Website template, demonstration component, or technical import log'
   elif re.search(r'privacy-policy|terms-and-conditions|refund-cancellation|donation-form|wp-json|/feed/|/give/',u,re.I):
    r['inclusion_status']='excluded_nonresearch';r['exclusion_reason']='Transactional, administrative, syndication, or generic site policy'
   elif len(t.strip())<100 and r.get('format')=='html':
    r['inclusion_status']='excluded_insufficient_text';r['exclusion_reason']='Empty or script-dependent page; raw response retained'
   elif re.search('lorem ipsum',t,re.I) and len(t)<2500 and r['publisher_class']=='act_for_goa':
    r['inclusion_status']='excluded_nonresearch';r['exclusion_reason']='Short page containing placeholder text'
   r['topics']=sorted(set(topic_tags(r.get('title','')+' '+t[:20000])+r.get('topics',[])))
   r['extraction_quality_flags']=[]
   if t and t.count('\ufffd')/max(1,len(t))>.005:r['extraction_quality_flags'].append('replacement_characters_review_encoding')
   if r.get('pages_needing_ocr_review'):r['extraction_quality_flags'].append('low_text_pages_scan_or_map_review')
   if re.search(r'draft',r.get('title',''),re.I):r['document_kind_hint']='draft_document'
   elif re.search(r'amend|corrigendum',r.get('title',''),re.I):r['document_kind_hint']='amendment_or_corrigendum'
   elif re.search(r'\b(act|rules|regulations|code)\b',r.get('title',''),re.I):r['document_kind_hint']='legislation_or_notification'
   r['rights_status']='publicly_accessible_source; republication_license_not_verified'
   if r['id'] in overrides:r.update(overrides[r['id']])
   dump(C/'metadata'/f'{r["id"]}.json',r)
  build_index()
 errors=[];hashes={};good=0;native_pages=0
 for r in rows:
  if r.get('raw_path'):
   p=ROOT/r['raw_path']
   if not p.exists():errors.append({'id':r['id'],'error':'raw missing'})
   elif hashlib.sha256(p.read_bytes()).hexdigest()!=r['sha256']:errors.append({'id':r['id'],'error':'raw hash mismatch'})
   else:good+=1
  if r.get('text_path'):
   p=ROOT/r['text_path']
   if not p.exists():errors.append({'id':r['id'],'error':'text missing'})
   elif hashlib.sha256(p.read_bytes()).hexdigest()!=r.get('text_sha256'):errors.append({'id':r['id'],'error':'text hash mismatch'})
  if r.get('pages_path'):
   ps=json.loads((ROOT/r['pages_path']).read_text());native_pages+=len(ps)
   if len(ps)!=r['page_count'] or [p['page'] for p in ps]!=list(range(1,len(ps)+1)):errors.append({'id':r['id'],'error':'page sequence mismatch'})
  if r.get('ocr_pages_path'):
   p=ROOT/r['ocr_pages_path']
   if not p.exists() or hashlib.sha256(p.read_bytes()).hexdigest()!=r['ocr_sha256']:errors.append({'id':r['id'],'error':'OCR derivative missing or hash mismatch'})
  if r.get('sha256') and r['status']=='downloaded':hashes.setdefault(r['sha256'],[]).append(r['id'])
 db=sqlite3.connect(C/'search.sqlite');integrity=db.execute('PRAGMA integrity_check').fetchone()[0]
 queries={q:db.execute('SELECT count(*) FROM passages WHERE passages MATCH ?',(q,)).fetchone()[0] for q in ['khazan','tenancy','"ground water"','"birth control"','"coastal regulation"','"Right to Information"','"Solid Waste"','"Panchayat"']}
 db.close()
 report={'raw_files_hash_verified':good,'pdf_page_records_checked':native_pages,'errors':errors,'sqlite_integrity':integrity,'search_smoke_queries':queries,'duplicate_content_groups':sum(len(x)>1 for x in hashes.values()),'metadata_scope_counts':dict(collections.Counter(r.get('inclusion_status',r['status']) for r in rows))}
 dump(C/'research'/'validation.json',report);dump(C/'research'/'duplicate-content.json',[{'sha256':k,'source_ids':v} for k,v in hashes.items() if len(v)>1]);print(json.dumps(report,indent=2))

if __name__=='__main__':main()
