"""Reproduce a consumed-source development probe, without network/model calls.

Read only seven explicitly pinned inputs; never scan, open a ledger or fetch URLs.
No candidate wording is generated or repaired. Author assessments are explanatory
annotations, not independent semantic acceptance or an automated entailment test.
"""
import argparse
import hashlib
import json
from pathlib import Path

try:
    from .claim_review_candidate import FACETS, Span, check
except ImportError:
    from claim_review_candidate import FACETS, Span, check

MANIFEST = Path(__file__).with_name('source_context_inputs.json')


def load_inputs(root):
    manifest = json.loads(MANIFEST.read_text())
    loaded = {}
    for name, digest in manifest['files'].items():
        path = root / name
        if path.is_symlink():
            raise ValueError('symlink input refused')
        raw = path.read_bytes()
        if hashlib.sha256(raw).hexdigest() != digest:
            raise ValueError('pinned input hash mismatch: ' + name)
        if name.endswith('.json'):
            loaded[name] = json.loads(raw)
    return manifest, loaded


def anchor(pack, identifier, passage, start_text, end_text, requires=()):
    text = pack['passages'][passage]
    # Require unambiguous supplied boundaries; never normalize or clamp offsets.
    if text.count(start_text) != 1:
        raise ValueError('ambiguous start: ' + identifier)
    start = text.index(start_text)
    end = text.index(end_text, start) + len(end_text)
    pack['spans'].append(Span(identifier, passage, start, end, tuple(requires)))


def claim(text, supports):
    return {'text': text, 'supports': supports,
            'facets': {f: list(supports) for f in FACETS}}


def probes(manifest, inputs):
    bio_pages = {str(p['page']): p['text'] for p in inputs['bio-pages.json']['pages']}
    bio_pages['61'] = next(p['text'] for p in inputs['bio-context.json']['pages'] if p['page'] == 61)
    bio = {'question': 'What does the report say about endemic avian species, and how certain is the total?',
           'passages': bio_pages, 'spans': [],
           'provenance': {'document_id': inputs['bio-meta.json']['id'],
                          'generation': manifest['generation'], 'original_sha256': inputs['bio-meta.json']['sha256']}}
    anchor(bio, 'report-date', '67', '7 March 2019', '7 March 2019')
    anchor(bio, 'secondary-method', '61', 'Overall Species Richness', 'Zoological Survey of India archive1.')
    anchor(bio, 'secondary-total', '61', 'Based on this secondary information', 'The details are presented in Table 3.19.', ('secondary-method',))
    anchor(bio, 'avian-heading', '67', 'Table 3.20 Endemic Avian', 'Study Area')
    anchor(bio, 'endemic-summary', '67', 'Endemism', 'provided below in Table 3.20',
           ('report-date', 'secondary-method', 'secondary-total', 'avian-heading', 'last-row'))
    anchor(bio, 'last-row', '66', '105 Oriolidae', '1 IV LC')
    bio_supports = ['report-date', 'secondary-method', 'secondary-total', 'avian-heading', 'endemic-summary', 'last-row']

    lake = {'question': 'What does the action plan say Bachbhatt Lake does?',
            'passages': {'23': inputs['lake-pages.json']['pages'][0]['text']}, 'spans': [],
            'provenance': {'document_id': '6dedf460d9433f0a7ca77abe-fb866f391a57', 'generation': manifest['generation']}}
    anchor(lake, 'lake-heading', '23', '24. Bachbhatt Lake', '(Salcete)')
    anchor(lake, 'lake-identity', '23', 'Bachbhatt Lake is situated', '7.5009 ha.')
    anchor(lake, 'lake-functions', '23', 'Known for housing migratory birds', 'paddy cultivation and buffalo wallowing.',
           ('lake-heading', 'lake-identity'))
    lake_supports = ['lake-heading', 'lake-identity', 'lake-functions']

    design_pages = {str(p['page']): p['text'] for p in inputs['design-pages.json']['pages']}
    design = {'question': 'What design safeguard does this extracted regulation require for rainwater storage?',
              'passages': design_pages, 'spans': [],
              'provenance': {'document_id': '131acd08c5377f26fb1250c5-2c2f91a1026b', 'generation': manifest['generation'],
                             'legal_currency': 'not_independently_verified'}}
    # This is an additional recovered obligation, not identification of the missing
    # historical annexure passage. Scope it to its actual storage-structure wording.
    anchor(design, 'storage-duty', '189', 'as per the statute. All the storage structures created', 'prevention of Vector Borne Diseases.')

    return [
        ('bio-preserving', bio, claim(
            'In the report dated 7 March 2019, the avian section says 16 of 104 recorded and reported species are endemic to the Western Ghats, with nine recorded during the primary survey. The 104 is a stated species total, not a count of individual birds. Table 3.19 ends at row 105, so the denominator needs checking.', bio_supports),
         'Author-proposed useful paraphrase: preserves report date, avian context, Western Ghats scope, primary/secondary distinction and denominator conflict.'),
        ('bio-distorted', bio, claim('Today, 16 of the 104 birds counted across Goa are endemic to Goa.', bio_supports),
         'Reject: individual birds replace species; current/statewide/Goa-endemic scope is invented despite complete selected support.'),
        ('lake-preserving', lake, claim('The action plan describes Bachbhatt Lake in Salcete as a reservoir that recharges groundwater and purifies water. It also says the lake supplies water for paddy cultivation and buffalo wallowing.', lake_supports),
         'Author-proposed useful paraphrase: explicit identifying and function spans; source attribution retained.'),
        ('lake-orphan', lake, claim('Bachbhatt Lake in Salcete recharges groundwater.', ['lake-functions']),
         'Reject mechanically: identifying spans were not explicitly selected; do not expand citation.'),
        ('lake-distorted', lake, claim('Bachbhatt Lake is in Mormugao and supplies drinking water.', lake_supports),
         'Reject semantically: wrong location and invented drinking-water use pass structural selection.'),
        ('duty-preserving', design, claim('The extracted regulation says rainwater-harvesting storage structures must meet the Goa Public Health Act, 1985 design and specification provisions for preventing vector-borne diseases. This is a reading of the supplied text, not verification of current law.', ['storage-duty']),
         'Author-proposed useful paraphrase: mandatory force and storage subject retained; current-law verification is not claimed.'),
        ('duty-weakened', design, claim('Design details are unavailable, so the source gives no storage-design requirement.', ['storage-duty']),
         'Reject semantically: unavailable detail is substituted for the explicit obligation.'),
    ]


def annexure_probes(root):
    pin = json.loads(Path(__file__).with_name('annexure_duty_input.json').read_text())
    path = root / pin['file']
    if path.is_symlink():
        raise ValueError('symlink input refused')
    raw = path.read_bytes()
    if hashlib.sha256(raw).hexdigest() != pin['sha256']:
        raise ValueError('annexure input hash mismatch')
    page = json.loads(raw)['pages'][0]
    if page['page'] != pin['physical_page']:
        raise ValueError('annexure physical page differs')
    pack = {'question': 'What does the supplied rule permit for groundwater recharge, and what design condition applies?',
            'passages': {'118': page['text']}, 'spans': [], 'provenance': pin}
    anchor(pack, 'recharge-permission', '118', 'However, Rain Water Harvesti ng', 'Water Resource Department, Government of Goa.')
    anchor(pack, 'annexure-duty', '118', 'The details of the structures', 'in Annexure-V (27.V).', ('recharge-permission',))
    ids = ['recharge-permission', 'annexure-duty']
    return [
        ('annexure-duty-preserving', pack, claim(
            'The supplied regulation permits rainwater harvesting for groundwater recharge in areas designated by Goa’s Water Resource Department. The structures and design must follow Annexure V (27.V). This page does not give the annexure’s detailed specifications, and current applicability has not been verified.', ids),
         'Author-proposed positive: permission and mandatory condition coexist; unavailable details do not remove the duty. The exact historical diagnostic identity is not established.'),
        ('annexure-duty-lost', pack, claim(
            'Groundwater recharge is permitted in designated areas. Design details are in an unavailable annexure.', ids),
         'Reject semantically: mandatory compliance is replaced by an access gap, despite complete selected support.'),
    ]


def run(root, *, include_annexure=False):
    manifest, inputs = load_inputs(root)
    reports = []
    cases = probes(manifest, inputs)
    if include_annexure:
        cases += annexure_probes(root)
    for identifier, pack, candidate, annotation in cases:
        try:
            result = check(pack, [candidate])
        except ValueError as error:
            result = {'mechanical': 'rejected', 'reason': str(error), 'semantic': 'not_assessed', 'release': 'hold'}
        # Include originals and all selected ranges in private output. No truncation,
        # source text rewriting, automatic closure or inference from reviewer labels.
        reports.append({'id': identifier, 'pack': {**pack, 'spans': [s.__dict__ for s in pack['spans']]},
                        'candidate': candidate, 'checks': result, 'development_author_annotation': annotation})
    return {'kind': 'consumed_source_development_probe', 'inputs': manifest,
            'independent_semantic_acceptance': 'not_performed', 'launch': 'hold', 'cases': reports}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--input-directory', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--include-annexure-duty', action='store_true')
    args = parser.parse_args()
    result = run(args.input_directory, include_annexure=args.include_annexure_duty)
    # Exclusive output prevents overwriting a historical report or input.
    import os
    fd = os.open(args.output, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    with os.fdopen(fd, 'w') as stream:
        json.dump(result, stream, ensure_ascii=False, indent=2)
        stream.write('\n')


if __name__ == '__main__':
    main()
