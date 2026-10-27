"""Private interpreter for the frozen v2 grammar, not a general schema engine.

Only bundled internal definitions and the keywords used by these two schemas are
supported. No external references, format plugins, remote loading or coercion.
The contract's full-string pattern rule intentionally supplements JSON Schema.
"""

import json
from pathlib import Path
import re

from .profile import canonical

SPEC = Path(__file__).with_name("spec")
ENVELOPE = json.loads((SPEC / "envelope.schema.json").read_text(encoding="utf-8"))
REPORT = json.loads((SPEC / "audit.schema.json").read_text(encoding="utf-8"))
REGISTRY = json.loads((SPEC / "registry.json").read_text(encoding="utf-8"))
_KEYWORDS = {
    "$schema", "$comment", "$defs", "title", "$ref", "type", "const", "enum",
    "pattern", "minimum", "maximum", "minLength", "items", "minItems", "maxItems",
    "uniqueItems", "properties", "required", "additionalProperties", "anyOf",
    "oneOf", "not",
}
_TYPES = {"object": dict, "array": list, "string": str, "integer": int,
          "null": type(None)}


def _shared_parent(paths):
    common = list(paths[0])
    for path in paths[1:]:
        common = common[:next((i for i, (a, b) in enumerate(zip(common, path))
                               if a != b), min(len(common), len(path)))]
    return common


def paths(value, schema, path=(), *, root=ENVELOPE):
    """Return grammar failures. Call only with this module's frozen schemas."""
    path = list(path)
    if set(schema) - _KEYWORDS:
        raise ValueError("Unsupported bundled schema keyword")
    failures = []
    if "$ref" in schema:
        ref = schema["$ref"]
        if not ref.startswith("#/$defs/") or ref.count("/") != 2:
            raise ValueError("Only bundled definition references are supported")
        failures.extend(paths(value, root["$defs"][ref.split("/")[-1]], path, root=root))
    if "type" in schema and type(value) is not _TYPES[schema["type"]]:
        return failures + [path]
    if "const" in schema and canonical(value) != canonical(schema["const"]):
        failures.append(path)
    if "enum" in schema and not any(canonical(value) == canonical(v) for v in schema["enum"]):
        failures.append(path)
    if "not" in schema and not paths(value, schema["not"], path, root=root):
        failures.append(path)
    for key in ("anyOf", "oneOf"):
        if key in schema:
            variants = [paths(value, s, path, root=root) for s in schema[key]]
            matches = sum(not failures for failures in variants)
            if matches == 0:
                failures.append(_shared_parent([p for group in variants for p in group]))
            elif key == "oneOf" and matches != 1:
                failures.append(path)
    if type(value) is str:
        if len(value) < schema.get("minLength", 0):
            failures.append(path)
        if "pattern" in schema and re.fullmatch(schema["pattern"], value) is None:
            failures.append(path)
    if type(value) is int:
        if value < schema.get("minimum", value) or value > schema.get("maximum", value):
            failures.append(path)
    if type(value) is list:
        if len(value) < schema.get("minItems", 0) or len(value) > schema.get("maxItems", len(value)):
            failures.append(path)
        if schema.get("uniqueItems") and len({canonical(v) for v in value}) != len(value):
            failures.append(path)
        if "items" in schema:
            for i, item in enumerate(value):
                failures.extend(paths(item, schema["items"], path + [i], root=root))
    if type(value) is dict:
        properties = schema.get("properties", {})
        failures.extend(path + [k] for k in schema.get("required", []) if k not in value)
        if schema.get("additionalProperties") is False:
            failures.extend(path + [k] for k in value if k not in properties)
        for key in properties.keys() & value.keys():
            failures.extend(paths(value[key], properties[key], path + [key], root=root))
    return failures


def first_path(failures):
    """Compare components by canonical encoding, as required for schema errors."""
    return min(failures, key=lambda path: tuple(canonical(part) for part in path))
