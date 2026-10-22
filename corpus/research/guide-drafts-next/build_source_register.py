import json,re,hashlib
from pathlib import Path
from urllib.parse import unquote
ROOT=Path(__file__).resolve().parents[3]
G=ROOT/'corpus/guides'
M=[json.loads(p.read_text()) for p in (ROOT/'corpus/metadata').glob('*.json')]
loc={
'FR1':('Krishi Card checklist physical page 2; support headings pages 3–31; regulated input businesses pages 33–41; offices pages 42–43.','Checklist page visually inspected. Scheme rates, eligibility and service operation require current confirmation.'),
'FR2':('Sections 1–4, physical pages 1–3.','Original 2023 Act; narrow statutory definition read. Commencement, rules, amendments and parcel application not consolidated.'),
'FR3':('Title and tenancy framework; opening provisions.','Use for separate tenancy review, not transaction eligibility or a consolidated current-law opinion.'),
'FR4':('Individual farmer application.','Official form collected previously; current acceptance to confirm.'),
'FR5':('Farmers group application.','Official form collected previously; applicant category and acceptance to confirm.'),
'FR6':('Press release dated 19 June 2025.','Bank mandate and Aadhaar Payment Bridge update; individual bank mapping not tested.'),
'FR7':('Where to analyse your soil samples table.','Three laboratory locations listed. Page also returns a PHP warning; laboratory availability and prices untested.'),
'FR8':('Dissemination Centre objectives and services.','Crop advice, practices, publications and planting-material service scope; availability untested.'),
'FR9':('Ground Water Act index.','Separate regulatory framework; no universal well exemption or permit granted.'),
'FR10':('Section 17A procedure and document list.','Hill cutting/low-lying filling permission enquiry; site classification unverified.'),
'AN1':('Emergency Contact against Animal Cruelty, Animals in Distress, Animal accidents and Animal Rescue.','Official routing page to veterinary, police, Panchayat, DSPCA and nodal resources; downstream rosters and live dispatch not tested.'),
'AN2':('Emergency Contact directory.','Published veterinary locations and officers; hours, service coverage and phone availability untested.'),
'AN3':('Prevention; Post-exposure prophylaxis; exposure-risk table.','WHO official medical source used for immediate washing and urgent assessment. No treatment dose or local stock claim.'),
'AN4':('Important Helpline Numbers.','Official web reading from the earlier reporting-guide check; no calls made.'),
'AN5':('Aims/objectives; hospital and APIO directory.','Office contacts are not asserted to be emergency dispatch numbers.'),
'AN6':('Head office contact block.','9607948546 / 8956863414 and director email read; office enquiries only, untested.'),
'AN7':('Contact Us helpline block.','North/South labels and 24 X 7 wording published by Forest Department; no operational test.'),
'AN8':('Forest responsibilities and wildlife/private-forest resource links.','Routing/reference index, not a complete current wildlife-law consolidation.'),
'AN9':('PCA Act sections 3 and 11.','Basic duty and cruelty framework; current offence selection/procedure must be checked for the case.'),
'AN10':('Physical page 1 of 2020 SOP.','Earlier visual inspection recorded. Old criminal-law citations must not be reused as current charges.'),
'AN11':('Legal Aid page.','Service/eligibility signpost; no representation promised.'),
'AN12':('English rules 3, 8–14, 20 and monitoring schedules; physical pages 24–32 and 38–40.','Read together with later court directions. No universal feeding/re-release claim.'),
'AN13':('2026 INSC 506, paragraphs 75–76, 108(D), 111; physical pages 90–91, 119, 124–128.','Institutional-premises conclusion visually inspected on page 90. Later Supreme Court/Goa High Court and local implementation review remains open.'),
'EN1':('Private forest, tree felling, wildlife and protected-area resource links.','Site-specific final boundaries, delegated officers and subsequent orders need checking.'),
'EN2':('Citizen Charter, physical pages 1 and 5.','Department and authority roles; historical contact material.'),
'EN3':('GCZMA home and Final CZMP navigation.','Web search/read available; local HTML is minimal/script dependent, not a downloaded approved map.'),
'EN4':('Section 17A procedure.','Separate hill cutting and filling permission enquiry.'),
'EN5':('Complaint email notice on home page.','Source inspected in earlier reporting draft; current web refetch timed out; no complaint submitted.'),
'EN6':('Groundwater legal framework index.','Locate applicable WRD rules/authority; watercourse ownership or project requirements not determined.'),
'EN7':('Preservation of Trees Act sections 8–10, physical pages 4–5.','Goa portal compilation, not certified current consolidation; do not infer publication date from upload path.'),
'EN8':('Goa Online Form B service.','Search-visible procedure; local HTML is minimal/script dependent. Submission not tested.'),
'EN9':('Form B procedure/checklist, physical pages 1–6.','Approval-band inequalities overlap in published checklist; no threshold or deadline copied into guide.'),
'EN10':('Final CZMP Goa navigation/page.','Obtain actual approved sheets and approval letters; page name alone does not settle draft/final status.'),
'EN11':('Central CRZ 2019 and amendments compilation.','Official Kerala-hosted central instrument; not proof of the applicable Goa plan or plot classification.'),
'EN12':('Wetlands Rules 2017 rules 2(g), 3 and 4, physical page 9.','Official national wetlands portal copy; definitions/exclusions and scope retained, site/court protection unresolved.'),
'EN13':('Draft-notification notices and proposed schedules.','Expressly draft; not final designation evidence or an open 2026 submission window.'),
'EN14':('2020 implementation guidance sections II, V–VI, VIII–XIV.','National guidance for identification, delineation, activities and notification; no individual site designation.'),
'EN15':('Gazette Notification index, official search discovery.','Direct requests failed (404; web 403). Final notifications and maps not established from this page.'),
'EN16':('Project-specific public hearing notice and supporting document links.','Example of notice-led participation; not an invitation to an assumed currently open hearing.'),
'EN17':('Opening BMC functions and local-committee list.','Current membership and meeting availability require local check.'),
'EN18':('Opening PBR explanation.','Documentation/traditional knowledge role; no licence to collect or disclose sensitive knowledge.'),
'EN19':('India Code NGT Act record and sections 14–16 listing.','Act record available through official web retrieval. Fresh PDF timed out; no numerical limitation advice copied.'),
}
rows={}
for name in ['FARMING','ANIMAL_WELFARE','ENVIRONMENTAL_PROTECTION']:
 for label,url in re.findall(r'^\[([^]]+)\]: (https?://\S+)',(G/(name+'_GUIDE_DRAFT.md')).read_text(),re.M):
  if url in rows:rows[url]['labels'].append(label);continue
  meta=next((m for m in M if unquote(m['url'])==unquote(url)),{})
  locator,limit=loc[label]
  title = 'Goa Restriction on Transfer of Agricultural Land Act, 2023' if label == 'FR2' else meta.get('title') or label+' official source'
  rows[url]={'labels':[label],'url':url,'title':title,'source_id':meta.get('id'),'status':meta.get('status','web_only'),'locator':locator,'use_and_limit':limit,**{k:meta.get(k) for k in ['retrieved_at','raw_path','sha256','text_path','pages_path','error']}}
# Record review details for shared URLs, not only their first label.
for row in rows.values():row['label_notes']={l:{'locator':loc[l][0],'limit':loc[l][1]} for l in row['labels']}
Path(__file__).with_name('sources.json').write_text(json.dumps(list(rows.values()),ensure_ascii=False,indent=2)+'\n')
out=['# Sources for farming animal welfare and environmental protection','Source review: 22 October 2026. Official source material supports the linked steps. Published information, current legal effect and live service operation are distinct checks. Local originals are retained separately from new explanatory text.']
for r in rows.values():
 out+=['## '+' and '.join(r['labels']),f"[{r['title']}]({r['url']})",'**Location:** '+r['locator'],r['use_and_limit']]
 if r['status']=='downloaded' and r['raw_path']:
  out+=[f"[Saved original](../raw/{Path(r['raw_path']).name}). Corpus record `{r['source_id']}`. "+('Limited HTML; no usable extracted body.' if not r['text_path'] and not r['pages_path'] else '')]
 else:out+=['No usable local original for this exact URL. '+str(r.get('error') or 'Official web retrieval/search only; limitations above apply.')]
(G/'SOURCES_NEXT.md').write_text('\n\n'.join(line.rstrip() for line in out)+'\n')
print(len(rows),'unique cited URLs')
