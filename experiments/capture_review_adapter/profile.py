"""Strict JSON, exact bookkeeping hashes, and the bundled closed grammar."""

from datetime import datetime
import hashlib
import json
import math
from pathlib import Path
import re

SCHEMA = json.loads((Path(__file__).with_name('spec') / 'shapes.schema.json').read_text())


def canonical(value):
    return json.dumps(value, ensure_ascii=False, sort_keys=True,
                      separators=(',', ':'), allow_nan=False).encode('utf-8')


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def value_hash(value):
    return sha(canonical(value))


def _pairs(pairs):
    value = {}
    for key, item in pairs:
        if key in value:
            raise ValueError('Duplicate JSON member')
        value[key] = item
    return value


def _constant(_token):
    raise ValueError('Non-finite JSON number')


def loads(raw):
    text = raw.decode('utf-8', errors='strict')
    if text.startswith('\ufeff'):
        raise ValueError('JSON BOM')
    value = json.loads(text, object_pairs_hook=_pairs, parse_constant=_constant)
    pending = [value]
    while pending:
        item = pending.pop()
        if type(item) is str and any(0xD800 <= ord(c) <= 0xDFFF for c in item):
            raise ValueError('Unpaired surrogate')
        if type(item) is float and not math.isfinite(item):
            raise ValueError('Non-finite JSON number')
        if type(item) is dict:
            pending.extend(item.keys())
            pending.extend(item.values())
        elif type(item) is list:
            pending.extend(item)
    return value


def instant(text):
    if not re.fullmatch(r'[0-9]{4}-[0-9]{2}-[0-9]{2}[Tt][0-9]{2}:[0-9]{2}:[0-9]{2}(?:\.[0-9]+)?(?:[Zz]|[+-](?:[01][0-9]|2[0-3]):[0-5][0-9])', text):
        return False
    try:
        datetime.fromisoformat(text.upper().replace('Z', '+00:00'))
        return True
    except ValueError:
        return False


def _common(paths):
    common = list(paths[0])
    for path in paths[1:]:
        common = common[:next((i for i, (a, b) in enumerate(zip(common, path))
                               if a != b), min(len(common), len(path)))]
    return common


def shape_paths(value, schema, path=()):
    """Private interpreter for the pinned schema, never user-supplied schemas."""
    path = list(path)
    if '$ref' in schema:
        return shape_paths(value, SCHEMA['$defs'][schema['$ref'].split('/')[-1]], path)
    types = {'object': dict, 'array': list, 'string': str, 'integer': int, 'null': type(None)}
    if 'type' in schema and type(value) is not types[schema['type']]:
        return [path]
    failures = []
    if 'const' in schema and canonical(value) != canonical(schema['const']):
        failures.append(path)
    if 'enum' in schema and not any(canonical(value) == canonical(v) for v in schema['enum']):
        failures.append(path)
    for union in ('anyOf', 'oneOf'):
        if union in schema:
            variants = [shape_paths(value, child, path) for child in schema[union]]
            count = sum(not errors for errors in variants)
            if not count:
                failures.append(_common([p for errors in variants for p in errors]))
            elif union == 'oneOf' and count != 1:
                failures.append(path)
    if type(value) is str:
        if len(value) < schema.get('minLength', 0):
            failures.append(path)
        if 'pattern' in schema and not re.fullmatch(schema['pattern'], value):
            failures.append(path)
    if type(value) is int:
        if not schema.get('minimum', value) <= value <= schema.get('maximum', value):
            failures.append(path)
    if type(value) is list:
        if len(value) < schema.get('minItems', 0):
            failures.append(path)
        if 'items' in schema:
            for i, item in enumerate(value):
                failures.extend(shape_paths(item, schema['items'], path + [i]))
    if type(value) is dict:
        fields = schema.get('properties', {})
        failures.extend(path + [k] for k in schema.get('required', []) if k not in value)
        if schema.get('additionalProperties') is False:
            failures.extend(path + [k] for k in value if k not in fields)
        for k in fields.keys() & value.keys():
            failures.extend(shape_paths(value[k], fields[k], path + [k]))
    return failures


def first_path(paths):
    return min(paths, key=lambda p: tuple(canonical(part) for part in p))
