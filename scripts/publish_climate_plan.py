"""Publish the resident reading guide from the same reviewed index as the UI.

No source fetching and no PDF rewriting. Original bytes remain in docs/climate.
Run: python3 scripts/publish_climate_plan.py
"""
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
data = json.loads((ROOT / 'src/content/climate-plan.json').read_text())
source = data['source']
original = ROOT / 'docs/climate/goa-sapcc-2023-2033.pdf'
if original.exists() and hashlib.sha256(original.read_bytes()).hexdigest() != source['sha256']:
    raise SystemExit('Source PDF differs from the reviewed edition; review references before publishing.')


def pdf_page(printed):
    if not 4 <= printed <= 218:
        raise ValueError('Page outside this edition')
    return (printed + 4) // 2


def reference(r):
    label = f'p. {r["start"]}' if r['start'] == r['end'] else f'pp. {r["start"]}–{r["end"]}'
    page = pdf_page(r['start'])
    return f'[{r["label"]}, {label} · PDF page {page}]({source["url"]}#page={page})'


lines = [
    '# Goa climate action plan reading guide', '',
    'Find the parts of Goa’s State Action Plan for Climate Change (SAPCC) that relate to daily life, read selected measures, and take an informed question to a community meeting or the relevant department.', '',
    f'Plan period: {source["period"]}. Published by the Goa State Biodiversity Board on 26 April 2023, prepared through NABARD Consultancy Services (NABCONS). Government copy hosted by NITI for States, downloaded 29 October 2026.', '',
    f'[Open the complete government PDF]({source["url"]}) · 111 PDF pages · 9.2 MB.', '',
    'This ActForGoa reading guide selects 26 measures across 13 topics. It is not a complete action register or a live progress report. Department names, project statuses and timelines reflect the plan; current delivery and availability need confirmation.', '',
    '## How to read the plan', '',
    'Mitigation means reducing the emissions that cause climate change. Adaptation means preparing for and responding to its effects. Most PDF pages contain two printed pages, so the printed page numbers and PDF viewer numbers differ. The links below include both. Some viewers ignore page links; enter the stated PDF page manually.', '',
    'The maps support state-level planning and do not establish the classification, permissions or risk of an individual property. The scanned committee minutes in Annexure VII need visual reading.', '',
    '## Topics', '',
]
for t in data['topics']:
    lines.extend([f'- [{t["title"]}](#{t["id"]})'])
for t in data['topics']:
    lines.extend(['', f'<a id="{t["id"]}"></a>', f'## {t["title"]}', '', t['summary'], '', '### Selected measures in the plan', ''])
    for a in t['actions']:
        lines.extend([f'**{a["title"]}.** {a["description"]}', '', f'Named in the plan: {a["agencies"]}. {reference(a["reference"])}.', ''])
    if t.get('note'):
        lines.extend([t['note'], ''])
    lines.extend(['### A question to take forward', '', t['question'], '', '### Read the full context', ''])
    lines.extend(f'- {reference(r)}' for r in t['references'])
lines.extend(['', '## Chapter index', '', '| Section | Printed pages | PDF page |', '| --- | --- | --- |'])
for c in data['chapters']:
    pp = str(c['start']) if c['start'] == c['end'] else f'{c["start"]}–{c["end"]}'
    page = pdf_page(c['start'])
    lines.append(f'| [{c["title"]}]({source["url"]}#page={page}) | {pp} | {page} |')
    for child in c.get('children', []):
        page = pdf_page(child['start'])
        lines.append(f'| [{child["label"]}]({source["url"]}#page={page}) | {child["start"]}–{child["end"]} | {page} |')
lines.extend(['', '## Source and version notes', '',
    f'The [Goa Assembly answer dated 8 August 2025]({source["assemblyUrl"]}) identifies the 2023–2033 SAPCC and links to [GSBB]({source["originalUrl"]}). That download returned an error on 29 October 2026. The accessible NITI for States edition is used here; equivalence with the unavailable GSBB file could not be verified.', '',
    'The source’s publication page (PDF page 3) records approval in principle by the National Steering Committee on 24 August 2022 and publication on 26 April 2023. This guide does not assign a “2.0” version label: current official web listings use inconsistent version labels.', '',
    'Goa’s separate State Action Plan on Climate Change and Human Health is a different document. Older consultation drafts and that health plan remain separate sources.', '',
    'The original PDF is preserved unchanged in the project documentation. Public navigation links to the government host. The publisher asserts copyright; no public redistribution licence has been established for the original PDF.', '',
])
text = '\n'.join(lines)
for path in [ROOT/'docs/climate/READING-GUIDE.md', ROOT/'public/guides/goa-climate-plan.md']:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text)
print('Published matching documentation and downloadable reading guide.')
