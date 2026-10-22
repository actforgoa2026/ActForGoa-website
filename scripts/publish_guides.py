"""Prepare authored guides for the static site without publishing the research archive.

Run from the repository root after editing corpus/guides. The generated content is
committed so a Vercel build does not require the local research corpus or Python.
"""
import json
import re
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / 'corpus/guides'
PUBLIC = ROOT / 'public/guides'
CONTENT = ROOT / 'src/content'
SPECS = [
    ('farming', 'FARMING_GUIDE_DRAFT.md', 'Farming in Goa', 'Land checks, Krishi Card registration, soil advice, schemes and damage records.', ['Food & farming', 'Community & rights']),
    ('animal-welfare', 'ANIMAL_WELFARE_GUIDE_DRAFT.md', 'Animal welfare in Goa', 'Find veterinary or wildlife help, report cruelty and check current community-animal procedures.', ['Nature & wildlife', 'Health & wellbeing']),
    ('environmental-protection', 'ENVIRONMENTAL_PROTECTION_GUIDE_DRAFT.md', 'Environmental protection in Goa', 'Check tree, coastal and wetland protections, request inspection and take part in decisions.', ['Water & environment', 'Nature & wildlife']),
    ('reporting', 'REPORTING_GUIDE_DRAFT.md', 'Report a problem in Goa', 'Gather evidence, choose the authority, follow up a complaint and request official records.', ['Community & rights', 'Water & environment']),
    ('building', 'BUILDING_GUIDE_DRAFT.md', 'Building and repair in Goa', 'Check land and jurisdiction, organise permissions, and understand completion and occupancy.', ['Planning & mobility', 'Community & rights']),
]


def source_register(text):
    # The official URLs and source limitations remain public; local raw copies do not.
    text = re.sub(r'^\[Saved original\].*$', '', text, flags=re.M)
    text = re.sub(r'\[([^\]]+)\]\(\.\./research/[^)]+\)', r'\1 (retained locally)', text)
    text = re.sub(r'`\.\./research/[^`]+`', 'the local research record', text)
    return re.sub(r'\n{3,}', '\n\n', text).strip() + '\n'


def public_copy(text):
    # Preserve the website's phone-free presentation rule. Canonical research
    # copies retain source-listed numbers; published guides link to directories.
    replacements = {
        'Goa\'s official portal lists **112 for police assistance**, **101 for fire** and **108/102 for ambulance services**.': 'Use Goa\'s official emergency directory for police, fire and ambulance assistance.',
        'For immediate danger to people, use **112**; Goa also lists **108/102** for ambulance services.': 'For immediate danger to people, contact police or ambulance services through the official Goa emergency directory.',
        'and a noise-related helpline, **+91 8956487938**': 'and a source-listed noise helpline',
        'publishes **1905** and describes online/phone registration': 'publishes its current contact route and describes online/phone registration',
        'The CM Helpline describes 1905 and tracking.': 'The CM Helpline describes contact and tracking routes.',
        'Official source lists mail.gspcb@gov.in and +91 8956487938.': 'Official source lists mail.gspcb@gov.in and a noise helpline.',
        '1905 and tracking described by portal.': 'Contact and tracking routes described by portal.',
        "this guide identifies 1905 specifically as the CM Helpline's published number.": 'use the CM Helpline portal to confirm its own published contact route.',
        'AHVS head office publishes **9607948546 / 8956863414** and **dir-ahvs.goa@nic.in** for departmental enquiries; these are not established here as round-the-clock rescue numbers.': 'Use the AHVS head-office contact page for departmental enquiries; its office contacts are not established here as round-the-clock rescue services.',
        'The Forest Department publishes **0832-2228772 for North Goa** and **0832-2750246 for South Goa**, labelled as 24-hour helplines. Its general office contact is **0832-2492533**.': 'The Forest Department contact page lists separate North and South Goa helplines, labelled as available around the clock, and a general office contact.',
        '9607948546 / 8956863414 and director email read; office enquiries only, untested.': 'Head-office contact details read; office enquiries only, untested.',
    }
    for original, replacement in replacements.items():
        text = text.replace(original, replacement)
    return text


def main():
    PUBLIC.mkdir(exist_ok=True)
    CONTENT.mkdir(exist_ok=True)
    (PUBLIC / 'templates').mkdir(exist_ok=True)
    for path in (SOURCE / 'templates').iterdir():
        if path.suffix in {'.txt', '.md'}:
            shutil.copyfile(path, PUBLIC / 'templates' / path.name)
    paths = {name: '/read/guide-' + slug for slug, name, *_ in SPECS}
    paths.update({'SOURCES.md': '/read/guide-sources', 'SOURCES_NEXT.md': '/read/guide-sources', 'VERIFICATION_REGISTER.md': '/read/guide-verification', 'README.md': '/library'})

    def prepare(text):
        text = public_copy(text)
        def link(match):
            label, href = match.groups()
            if href in paths:
                return f'[{label}]({paths[href]})'
            if href.startswith('templates/'):
                return f'[{label}](/guides/{href})'
            return match.group(0)
        return re.sub(r'\[([^\]]+)\]\(([^)]+)\)', link, text)

    documents = []
    for slug, filename, title, summary, topics in SPECS:
        original = (SOURCE / filename).read_text()
        (PUBLIC / filename).write_text(prepare(original))
        templates = list(dict.fromkeys(re.findall(r'\]\((templates/[^)]+)\)', original)))
        documents.append({'id': 'guide-' + slug, 'title': title, 'heading': original.splitlines()[0].removeprefix('# '), 'summary': summary, 'topics': topics, 'markdown': prepare(original.split('\n', 1)[1].strip()), 'download': '/guides/' + filename, 'templates': [{'label': Path(t).stem[3:].replace('-', ' ').capitalize(), 'url': '/guides/' + t} for t in templates], 'listed': True})
    sources = source_register((SOURCE / 'SOURCES.md').read_text()) + '\n' + source_register((SOURCE / 'SOURCES_NEXT.md').read_text()).replace('# Sources for farming animal welfare and environmental protection', '## Farming animal welfare and environmental protection', 1)
    verification = source_register((SOURCE / 'VERIFICATION_REGISTER.md').read_text())
    for slug, title, text in [('sources', 'Official sources for the practical guides', sources), ('verification', 'What still needs verification', verification)]:
        body = prepare(text.split('\n', 1)[1].strip())
        (PUBLIC / (slug + '.md')).write_text('# ' + title + '\n\n' + body + '\n')
        documents.append({'id': 'guide-' + slug, 'title': title, 'heading': title, 'summary': '', 'topics': [], 'markdown': body, 'download': '/guides/' + slug + '.md', 'templates': [], 'listed': False})
    (CONTENT / 'guides.json').write_text(json.dumps(documents, ensure_ascii=False, indent=2) + '\n')
    print(f'Prepared {len(SPECS)} guides, 2 review documents and {len(list((PUBLIC / "templates").iterdir()))} templates')


if __name__ == '__main__':
    main()
