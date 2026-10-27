"""Generate documentary coverage, baseline comparison and a compact source map."""
import collections,json,re
from pathlib import Path
from bs4 import BeautifulSoup
from ingest_goa_corpus import ROOT,C,dump,now,TOPICS,canonical
rows=[json.loads(l) for l in (C/'catalog.jsonl').read_text().splitlines()]
good=[r for r in rows if r['status']=='downloaded' and not r.get('inclusion_status','included').startswith('excluded')]
baseline=[r for r in good if r['publisher_class']=='act_for_goa']
external=[r for r in good if r['publisher_class']!='act_for_goa']
afg_links=set()
for r in baseline:
 if r.get('format')=='html':
  soup=BeautifulSoup((ROOT/r['raw_path']).read_bytes(),'lxml')
  afg_links.update(canonical(a['href'],r['url']) for a in soup.select('a[href]'))
afg_hashes={r['sha256'] for r in baseline}
additions=[]
for r in external:
 linked=r['url'] in afg_links or r.get('final_url') in afg_links
 duplicate=r['sha256'] in afg_hashes
 additions.append({'id':r['id'],'title':r.get('title'),'url':r['url'],'format':r.get('format'),'publisher_class':r['publisher_class'],'directly_linked_from_captured_actforgoa':linked,'identical_content_in_actforgoa_capture':duplicate,'addition_status':'existing_link_or_identical_content' if linked or duplicate else 'independently_discovered_addition','comparison_limit':'Checks direct links and exact bytes only; not semantic absence from Act for Goa'})
dump(C/'research'/'external-additions.json',additions)
groups=[
 ('Building and planning','building_planning_land',r'town.*country.*planning|gldbcr|building.*construction|land.*development', 'Consolidate principal legislation, amendments and court orders; check the local authority, zone and plot-specific records before producing a permission guide.'),
 ('Agricultural land and livelihoods','agriculture_food',r'agricultur|tenancy|khazan|fertili|seeds.*act|insecticides|nurser', 'Separate land tenure and transfer restrictions from farming practice and scheme eligibility; verify current schemes and farmer service contacts.'),
 ('Animals and wildlife','animals_wildlife',r'animal|cruelty|birth.*control|wildlife|wild.life|dog|veterinar', 'Reconcile older local advice, ABC rules, later circulars and court directions; verify present-day rescue coverage without inferring availability from old contacts.'),
 ('Coasts, wetlands and water','coasts_wetlands_water',r'coast|crz|wetland|ground.?water|irrigation|fishing|water.*supply', 'Distinguish draft and final notifications; verify approved CZMP and wetland maps, zone of influence and site-specific water permissions.'),
 ('Forests, trees and biodiversity','forests_trees_biodiversity',r'forest|trees|biological.*divers|biodivers|afforestation', 'Pair tree protection, forest and biodiversity legislation with amendments, private-forest records and local BMC/PBR material; retain community and forest rights context.'),
 ('Pollution, waste and climate','pollution_waste_climate',r'pollution|waste|environment.*protection|climate|eia|noise', 'Reconcile newer waste rules with historic guidance; collect location-specific consent/public-hearing records and current complaint routing.'),
 ('Reporting, information and legal access','reporting_rights_governance',r'complaint|grievance|right.*information|rti|tribunal|legal.*aid|panchayat|citizen.*charter', 'Verify office jurisdiction, PIOs, application routes, fees, time limits and escalation procedures before publishing actionable guides.'),
]
coverage=[]
for title,tag,pattern,gap in groups:
 candidates=[r for r in external if re.search(pattern,r.get('title','')+' '+r['url'],re.I)]
 candidates.sort(key=lambda r:(r.get('format')!='pdf',r['publisher_class']!='government_or_court',-int(max(re.findall(r'20[0-2]\d',r.get('title','')) or ['2000'])),r.get('title','')))
 afg=[r for r in baseline if re.search(pattern,r.get('title','')+' '+r['url'],re.I)]
 coverage.append({'area':title,'topic_key':tag,'external_title_or_url_matches':len(candidates),'actforgoa_title_or_url_matches':len(afg),'external_examples':[{'id':r['id'],'title':r.get('title'), 'url':r['url'],'raw_path':r['raw_path']} for r in candidates[:12]],'actforgoa_examples':[{'id':r['id'],'title':r.get('title'),'url':r['url']} for r in afg[:8]],'review_needed':gap,'method':'Title and URL keyword matches, not a legal completeness assessment; baseline is captured material only'})
checks=[
 ('Goa Town and Country Planning Act',r'town.*country.*planning.*(?:1974|act)'),
 ('Goa land development and building regulations',r'gldbcr|building.*construction.*regulation'),
 ('Agricultural Tenancy Act',r'agricultural.*tenancy.*act|agricultural_tenancy'),
 ('Goa agricultural land transfer restrictions',r'restriction.*transfer.*agricultural'),
 ('Goa Land Use Regulation Act and amendments',r'land.use.*regulation'),
 ('Goa Land Revenue Code',r'land.revenue.*code'),
 ('Panchayat Raj Act and rules',r'panchayat.*raj'),
 ('Mundkar protections',r'mundkar'),
 ('Agriculture Policy 2025',r'amritkal|2526-18-SI-SUG-2'),
 ('Tree preservation legislation',r'preservation.*trees|tree.*preservation|pta.pdf'),
 ('Forest rights legislation',r'forest.rights|FRA-Act'),
 ('Wildlife protection legislation',r'wild.?life.*protection|wpa.pdf'),
 ('Biodiversity Rules 2024',r'biological.*diversity.*rules.*2024'),
 ('CRZ 2019 national notification',r'crz.*2019'),
 ('Groundwater legislation',r'ground.?water.*(?:act|rules)'),
 ('Environment Protection Act',r'environment.*protection.*act|EPA1986|epa.pdf'),
 ('Solid Waste Management Rules 2026',r'solid.*waste.*2026'),
 ('Construction and Demolition Rules 2025',r'construction.*demolition.*2025|262313'),
 ('Animal Birth Control Rules 2023',r'animal.*birth.*control.*2023'),
 ('Later animal welfare SOP and court directions',r'176431409245|SOP.*07.11.2025'),
 ('Right to Information Act',r'right.*information.*act|rti.pdf|a2005-22'),
 ('National Green Tribunal Act',r'national.*green.*tribunal.*act|e1005.pdf'),
 ('Fertiliser Control Order',r'fertiliser.*control|fert_order'),
 ('Insecticides Act',r'insecticides.*act'),
 ('Seeds Act and Rules',r'seeds?.*act|seeds?.*rules|seed.order'),
]
register=[]
for label,pattern in checks:
 matches=[r for r in rows if re.search(pattern,r.get('title',r.get('title_hint',''))+' '+r['url'],re.I)]
 downloaded=[r for r in matches if r['status']=='downloaded' and r.get('format') in ['pdf','docx']]
 register.append({'subject':label,'status':'document_downloaded' if downloaded else ('page_or_failed_attempt_only' if matches else 'not_located_in_captured_set'),'documents':[{'id':r['id'],'title':r.get('title'), 'url':r['url'],'status':r['status'],'format':r.get('format'),'extraction_status':r.get('extraction_status'),'raw_path':r.get('raw_path')} for r in matches],'currency_review':'not_completed'})
dump(C/'research'/'coverage.json',{'generated_at':now(),'areas':coverage,'key_document_register':register,'baseline_note':'Comparison of captured Act for Goa title/URL evidence against external source records. Counts are not proof of absence from the live site. Topic tagging is automated and overlapping.'})
lines=['# Source map and editorial review queue','', 'Generated from the local catalogue. These are documentary starting points, not statements of current legal effect.','', '| Area | External title/URL matches | Act for Goa title/URL matches |','| --- | ---: | ---: |']
for c in coverage:lines.append(f'| {c["area"]} | {c["external_title_or_url_matches"]} | {c["actforgoa_title_or_url_matches"]} |')
for c in coverage:
 lines+=['','## '+c['area'],'',c['review_needed'],'']
 for r in c['external_examples'][:6]:
  title=r['title'].replace('[','(').replace(']',')').replace('\n',' ')
  lines.append(f'- [{title}](../{r["raw_path"].removeprefix("corpus/")}) ([source]({r["url"]})); record `{r["id"]}`.')
lines+=['','## Priority documents not yet downloaded','']
missing=[r for r in register if r['status']!='document_downloaded']
lines+=['- '+r['subject']+': '+r['status'].replace('_',' ')+'.' for r in missing] or ['All subjects in this bounded register have at least one downloaded document. Legal currency remains unverified.']
lines+=['','## Remaining collection and quality gaps','','- Court histories and later amendments are not exhaustively traced. A judgment or order may have later appeals, stays or modifications.','- Village-specific bylaws, Gram Sabha records, cadastral/CZMP layers, final wetland boundaries and current complaint-resolution outcomes require further collection.','- English-only OCR is supplementary and unverified. Scanned maps and non-English documents still require dedicated review.','- Some originals were unavailable because of server errors, TLS failures, timeouts, robots directives or the response-size limit; see `failures.json`.','- Discovery backlogs are preserved in `pending-*.json` and `pending-discovered.json`. They are candidate URLs, not promises that every link belongs in the corpus.','- Articles and civil-society accounts describe their authors’ views and may refer to litigation without containing the underlying final judgment.','- Contact details and scheme eligibility have not been tested by submitting applications or contacting anyone.','']
lines+=['## Additions beyond the captured Act for Goa material','',f'{sum(r["addition_status"]=="independently_discovered_addition" for r in additions)} external source records were independently discovered without a matching direct link or identical file in the captured Act for Goa material. `external-additions.json` contains the record-level comparison. This is evidence of collection expansion, not proof that the topic is absent from the live website.','']
(C/'research'/'SOURCE_MAP.md').write_text('\n'.join(lines))
print(json.dumps({'areas':len(coverage),'key_subjects':len(register),'subjects_without_downloaded_document':[r['subject'] for r in missing]},indent=2))
