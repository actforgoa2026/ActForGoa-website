"""The v2 JSON profile and domain-separated identities (standard library only)."""

import hashlib
import json
import re

VERSION = "afg-evidence-coverage-v2"
PREFIX = b"ActForGoa\0evidence-coverage-v2\0"
MAX_INTEGER = 9007199254740991


class ProfileError(ValueError):
    """Invalid raw JSON profile; messages deliberately contain no input text."""


def _reject(_value):
    raise ProfileError("Disallowed numeric token")


def _integer(token):
    if not re.fullmatch(r"0|[1-9][0-9]*", token) or len(token) > 16:
        raise ProfileError("Disallowed integer token")
    value = int(token)
    if value > MAX_INTEGER:
        raise ProfileError("Integer outside the v2 range")
    return value


def _object(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ProfileError("Duplicate decoded member name")
        result[key] = value
    return result


def strict_loads(raw: bytes):
    """Parse UTF-8 bytes without duplicate keys, numeric coercion or text repair."""
    if type(raw) is not bytes:
        raise TypeError("strict_loads requires bytes")
    try:
        text = raw.decode("utf-8", errors="strict")
        if text.startswith("\ufeff"):
            raise ProfileError("Byte order mark")
        value = json.loads(text, object_pairs_hook=_object, parse_int=_integer,
                           parse_float=_reject, parse_constant=_reject)
        pending = [value]
        while pending:
            item = pending.pop()
            if type(item) is str:
                if any(0xD800 <= ord(c) <= 0xDFFF for c in item):
                    raise ProfileError("Unpaired surrogate")
            elif type(item) is dict:
                pending.extend(item.keys())
                pending.extend(item.values())
            elif type(item) is list:
                pending.extend(item)
        return value
    except (UnicodeError, json.JSONDecodeError) as exc:
        raise ProfileError("Invalid JSON or UTF-8") from exc


def canonical(value) -> bytes:
    """Canonicalize a value that has already passed strict_loads."""
    return json.dumps(value, ensure_ascii=False, sort_keys=True,
                      separators=(",", ":"), allow_nan=False).encode("utf-8")


def digest(domain: str, value) -> str:
    if domain not in {"request", "evidence", "candidate", "envelope", "text"}:
        raise ValueError("Unknown v2 hash domain")
    payload = value.encode("utf-8") if domain == "text" else canonical(value)
    return hashlib.sha256(PREFIX + domain.encode("ascii") + b"\0" + payload).hexdigest()
