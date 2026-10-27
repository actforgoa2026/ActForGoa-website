"""The eight-stage, fixed-artifact capture review contract. Standard library only."""

from copy import deepcopy
from pathlib import Path
import re

from .profile import SCHEMA, canonical, first_path, instant, loads, sha, shape_paths, value_hash

VERSION = 'afg-capture-review-v1'
PACKET_SHA = 'c80de075574077335fabb4ed05c2e59786354eab63fd570437e484e9ee101202'
# Identities only. Local delivery paths must be explicitly supplied by the caller.
ARTIFACT_KINDS = {
    'bb9be999db8253428db92ec0a46f8f3e597fe21a000347b86b3a3ceb7e00f4e9': 'capture',
    '39f9a2b4c1276e27c35a08d7c41bc03caa0e58f684cf9d17258269abd0f5fadb': 'capture',
    'ff795dbc0292bb796d2b2dc41cb5c03daae7d7a5afef980dfdc542fb9b91d265': 'review',
    '1d7321589a4476073633f701f12e02caee290196d143e9155362fa9d25353c5c': 'review',
    'dac6d127b7f639b101abfaebc14630034dd2559e9395d6c0b79d8a92e1b49cfa': 'illustration',
}
SENTINELS = {
    'semantic_judgment': 'not_assessed',
    'original_authentication': 'not_performed',
    'runtime_context_acquisition': 'unresolved',
    'public_activation': 'hold',
    'author_authentication': 'not_performed',
    'question_completeness': 'not_assessed',
}
FIELDS = ('id', 'question', 'prepared_evidence', 'request_shape', 'final_output_diagnostic',
          'answer', 'human_review', 'mechanical_passed', 'expected_behavior_passed', 'prompt_sha256')
ROOT_FIELDS = ('source_commit', 'model', 'generation', 'effort')
INDEX = r'(?:0|[1-9][0-9]*)'


def error(code, path):
    return {'code': code, 'path': list(path)}


def rejected(errors):
    unique = {(e['code'], canonical(e['path'])): e for e in errors}
    return {'version': VERSION, 'status': 'rejected',
            'errors': [unique[key] for key in sorted(unique)], **SENTINELS}


class PointerError(ValueError):
    pass


def parts(pointer):
    if not pointer.startswith('/') or re.search(r'~(?![01])', pointer):
        raise PointerError('Invalid pointer')
    return [p.replace('~1', '/').replace('~0', '~') for p in pointer.split('/')[1:]]


def resolve(value, pointer):
    for part in parts(pointer):
        if type(value) is dict and part in value:
            value = value[part]
        elif type(value) is list and re.fullmatch(INDEX, part) and int(part) < len(value):
            value = value[int(part)]
        else:
            raise PointerError('Dangling pointer')
    return value


def presence(value, pointer):
    tokens = parts(pointer)
    parent_pointer = pointer.rsplit('/', 1)[0]
    parent = resolve(value, parent_pointer) if parent_pointer else value
    if type(parent) is dict and tokens[-1] not in parent:
        return {'state': 'not_captured'}
    found = resolve(value, pointer)
    return {'state': 'captured', 'value': deepcopy(found), 'value_sha256': value_hash(found)}


def span_matches(span, text):
    return (type(text) is str and 0 <= span['start'] < span['end'] <= len(text)
            and text[span['start']:span['end']] == span['text']
            and sha(span['text'].encode('utf-8')) == span['text_sha256'])


def _references(sidecar):
    for i, case in enumerate(sidecar['cases']):
        yield case['capture_sha256'], ['sidecar', 'cases', i, 'capture_sha256']
    for i, annotation in enumerate(sidecar['annotations']):
        base = ['sidecar', 'annotations', i]
        yield annotation['target']['artifact_sha256'], base + ['target', 'artifact_sha256']
        if annotation['source_review'] is not None:
            yield annotation['source_review']['artifact_sha256'], base + ['source_review', 'artifact_sha256']


def _artifacts(invocation):
    errors, seen, documents = [], set(), {}
    for i, artifact in enumerate(invocation['artifacts']):
        digest = artifact['sha256']
        path = ['artifacts', i, 'sha256']
        if digest not in ARTIFACT_KINDS:
            errors.append(error('UNKNOWN_ARTIFACT', path))
        if digest in seen:
            errors.append(error('DUPLICATE_ID', path))
        seen.add(digest)
    if errors:
        return {}, errors, 1
    operational = False
    for i, artifact in enumerate(invocation['artifacts']):
        path = ['artifacts', i]
        try:
            raw = Path(artifact['path']).read_bytes()
        except (OSError, ValueError):
            errors.append(error('IO_FAILURE', path + ['path']))
            operational = True
            continue
        if sha(raw) != artifact['sha256']:
            errors.append(error('ARTIFACT_HASH', path + ['sha256']))
            continue
        try:
            documents[artifact['sha256']] = loads(raw)
        except (ValueError, RecursionError):
            errors.append(error('ARTIFACT_PARSE', path + ['path']))
    if errors:
        return {}, errors, 2 if operational else 1
    errors = [error('MISSING_ARTIFACT', path)
              for digest, path in _references(invocation['sidecar']) if digest not in documents]
    return documents, errors, 1


def _cases(sidecar, documents):
    bound, errors, pairs = {}, [], set()
    for i, case in enumerate(sidecar['cases']):
        path = ['sidecar', 'cases', i]
        pair = (case['capture_sha256'], case['pointer'])
        duplicate = case['key'] in bound or pair in pairs
        if duplicate:
            errors.append(error('DUPLICATE_ID', path))
        pairs.add(pair)
        try:
            if ARTIFACT_KINDS.get(case['capture_sha256']) != 'capture' or not re.fullmatch('/cases/' + INDEX, case['pointer']):
                raise PointerError()
            selected = resolve(documents[case['capture_sha256']], case['pointer'])
            if type(selected) is not dict or selected.get('id') != case['case_id']:
                raise PointerError()
        except PointerError:
            errors.append(error('CASE_BINDING', path))
        if not duplicate:
            bound[case['key']] = case
    for array in ('observations', 'annotations', 'coverage'):
        seen = set()
        for i, item in enumerate(sidecar[array]):
            if item['id'] in seen:
                errors.append(error('DUPLICATE_ID', ['sidecar', array, i, 'id']))
            seen.add(item['id'])
    return bound, errors


def _target(annotation, case, documents):
    target = annotation['target']
    pointer = target['pointer']
    digest = target['artifact_sha256']
    if target['representation'] == 'illustrative':
        if ARTIFACT_KINDS.get(digest) != 'illustration':
            return 'TARGET_CASE', []
        match = re.fullmatch(r'/cases/(' + INDEX + r')/claims/(' + INDEX + r')/text', pointer)
        if not match:
            return 'TARGET_REPRESENTATION', []
        try:
            document = documents[digest]
            if shape_paths(document, SCHEMA['$defs']['Illustrations']) or not instant(document['author']['at']):
                return 'TARGET_REPRESENTATION', []
            illustration = resolve(document, '/cases/' + match[1])
            if any(illustration[k] != case[v] for k, v in (
                ('capture_sha256', 'capture_sha256'), ('capture_case_pointer', 'pointer'), ('case_id', 'case_id'))):
                return 'TARGET_CASE', []
            if illustration['question'] != resolve(documents[case['capture_sha256']], case['pointer'] + '/question'):
                return 'TARGET_CASE', []
        except PointerError:
            return 'TARGET_POINTER', ['pointer']
    else:
        prefix = re.match(r'^/cases/([^/]+)', pointer)
        if digest != case['capture_sha256'] or (prefix and prefix[0] != case['pointer']):
            return 'TARGET_CASE', []
        family = '/final_output_diagnostic/answer' if target['representation'] == 'raw_diagnostic' else '/answer'
        if not re.fullmatch(re.escape(case['pointer'] + family) + '/paragraphs/' + INDEX + '/text', pointer):
            return 'TARGET_REPRESENTATION', []
    try:
        text = resolve(documents[digest], pointer)
        if type(text) is not str:
            raise PointerError()
    except PointerError:
        return 'TARGET_POINTER', ['pointer']
    if not span_matches(target['span'], text):
        return 'TARGET_SPAN', ['span']
    return None


def _evidence(item, case, capture):
    pointer = item['block_pointer']
    prefix = re.match(r'^/cases/([^/]+)', pointer)
    if prefix and prefix[0] != case['pointer']:
        return 'SOURCE_CASE', []
    try:
        if not re.fullmatch(re.escape(case['pointer']) + '/prepared_evidence/' + INDEX, pointer):
            raise PointerError()
        block = resolve(capture, pointer)
        if type(block) is not dict or block.get('id') != item['block_id'] or value_hash(block) != item['block_value_sha256']:
            raise PointerError()
    except PointerError:
        return 'SOURCE_BINDING', []
    selection = item['selection']
    try:
        valid = (span_matches(selection['span'], resolve(block, selection['pointer']))
                 if selection['kind'] == 'text_span'
                 else canonical(presence(block, selection['pointer'])) == canonical(selection['expected']))
        if not valid:
            raise PointerError()
    except PointerError:
        return 'SOURCE_SELECTION', ['selection']
    return None


def _review_matches(reference, documents):
    if reference is None:
        return True
    if ARTIFACT_KINDS.get(reference['artifact_sha256']) != 'review':
        return False
    review = documents[reference['artifact_sha256']]
    try:
        return (value_hash(resolve(review, reference['finding_pointer'])) == reference['finding_value_sha256']
                and resolve(review, reference['author_pointer']) == reference['author_value']
                and resolve(review, reference['time_pointer']) == reference['time_value']
                and instant(reference['time_value']))
    except PointerError:
        return False


def _coverage(sidecar, bound, documents):
    annotations = {a['id']: a for a in sidecar['annotations']}
    linked, covered, errors = set(), set(), []
    for i, row in enumerate(sidecar['coverage']):
        path = ['sidecar', 'coverage', i]
        case = bound.get(row['case_key'])
        if case is None:
            errors.append(error('COVERAGE_LINK', path))
            continue
        covered.add(case['key'])
        refs = row['annotation_ids']
        good_refs = [ref for ref in refs if ref in annotations and annotations[ref]['case_key'] == case['key']]
        linked.update(good_refs)
        valid = len(good_refs) == len(refs) and len(set(refs)) == len(refs)
        valid = valid and (row['state'] != 'reviewed_part' or bool(refs))
        try:
            valid = (valid and row['question_pointer'] == case['pointer'] + '/question'
                     and span_matches(row['question_span'], resolve(documents[case['capture_sha256']], row['question_pointer'])))
        except PointerError:
            valid = False
        if not valid:
            errors.append(error('COVERAGE_LINK', path))
    errors.extend(error('COVERAGE_LINK', ['sidecar', 'annotations', i])
                  for i, a in enumerate(sidecar['annotations']) if a['id'] not in linked)
    errors.extend(error('COVERAGE_LINK', ['sidecar', 'cases', i])
                  for i, c in enumerate(sidecar['cases']) if c['key'] not in covered)
    return errors


def _project(case, capture):
    def field(name, pointer):
        return {'name': name, 'pointer': pointer, 'presence': presence(capture, pointer)}
    contexts = []
    selected = resolve(capture, case['pointer'])
    for i, block in enumerate(selected.get('prepared_evidence', [])):
        pointer = case['pointer'] + f'/prepared_evidence/{i}/context_ids'
        contexts.append({'block_id': block['id'], 'pointer': pointer, 'presence': presence(capture, pointer)})
    return {'binding': deepcopy(case),
            'capture_observations': [field(name, '/' + name) for name in ROOT_FIELDS],
            'captured_fields': [field(name, case['pointer'] + '/' + name) for name in FIELDS],
            'block_context_observations': contexts}


def link(raw):
    """Return (complete result, exit code); never expose partial data on failure."""
    try:
        invocation = loads(raw)
    except (ValueError, RecursionError):
        return rejected([error('INPUT_SHAPE', [])]), 1
    failures = shape_paths(invocation, SCHEMA['$defs']['Input'])
    # Calendar validation participates in the same first-member ordering as the
    # closed shape, including when an unrelated shape member is also invalid.
    sidecar_value = invocation.get('sidecar') if type(invocation) is dict else None
    annotations = sidecar_value.get('annotations') if type(sidecar_value) is dict else None
    if type(annotations) is list:
        for i, annotation in enumerate(annotations):
            author = annotation.get('author') if type(annotation) is dict else None
            at = author.get('at') if type(author) is dict else None
            if type(at) is str and not instant(at):
                failures.append(['sidecar', 'annotations', i, 'author', 'at'])
    if failures:
        return rejected([error('INPUT_SHAPE', first_path(failures))]), 1
    documents, errors, code = _artifacts(invocation)
    if errors:
        return rejected(errors), code
    sidecar = invocation['sidecar']
    bound, errors = _cases(sidecar, documents)
    if errors:
        return rejected(errors), 1
    for i, annotation in enumerate(sidecar['annotations']):
        path = ['sidecar', 'annotations', i]
        case = bound.get(annotation['case_key'])
        if case is None:
            errors.append(error('CASE_BINDING', path))
        else:
            failure = _target(annotation, case, documents)
            if failure:
                errors.append(error(failure[0], path + ['target'] + failure[1]))
    if errors:
        return rejected(errors), 1
    for i, annotation in enumerate(sidecar['annotations']):
        case = bound[annotation['case_key']]
        for j, item in enumerate(annotation['evidence']):
            failure = _evidence(item, case, documents[case['capture_sha256']])
            if failure:
                errors.append(error(failure[0], ['sidecar', 'annotations', i, 'evidence', j] + failure[1]))
    if errors:
        return rejected(errors), 1
    for i, annotation in enumerate(sidecar['annotations']):
        if not _review_matches(annotation['source_review'], documents):
            errors.append(error('REVIEW_PROVENANCE', ['sidecar', 'annotations', i, 'source_review']))
    if errors:
        return rejected(errors), 1
    for i, observation in enumerate(sidecar['observations']):
        path = ['sidecar', 'observations', i]
        case = bound.get(observation['case_key'])
        try:
            if case is None:
                raise PointerError()
            pointer = observation['pointer']
            tokens = parts(pointer)
            case_tokens = parts(case['pointer'])
            if pointer != '/effort' and not (tokens[:2] == case_tokens and len(tokens) >= 3 and tokens[2] in FIELDS):
                raise PointerError()
            actual = presence(documents[case['capture_sha256']], pointer)
        except PointerError:
            errors.append(error('OBSERVATION_POINTER', path))
            continue
        if canonical(actual) != canonical(observation['expected']):
            errors.append(error('OBSERVATION_MISMATCH', path + ['expected']))
    if errors:
        return rejected(errors), 1
    errors = _coverage(sidecar, bound, documents)
    if errors:
        return rejected(errors), 1
    return {'version': VERSION, 'status': 'linked_for_review',
            'selected_cases': [_project(case, documents[case['capture_sha256']]) for case in sidecar['cases']],
            'review_annotations': deepcopy(sidecar), **SENTINELS}, 0
