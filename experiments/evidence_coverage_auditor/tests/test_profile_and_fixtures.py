import hashlib
import json
from pathlib import Path
import unittest

from experiments.evidence_coverage_auditor import audit_bytes
from experiments.evidence_coverage_auditor import grammar
from experiments.evidence_coverage_auditor.profile import (
    MAX_INTEGER, ProfileError, canonical, digest, strict_loads,
)

ROOT = Path(__file__).resolve().parents[1]
FIXTURES = ROOT / "tests" / "fixtures"


class FrozenConformanceTests(unittest.TestCase):
    def test_all_21_complete_reports_match_frozen_expectations(self):
        examples = json.loads((FIXTURES / "examples.json").read_text(encoding="utf-8"))["examples"]
        self.assertEqual(len(examples), 21)
        for example in examples:
            with self.subTest(example=example["id"]):
                report = audit_bytes(canonical(example["envelope"]))
                self.assertEqual(report, example["author_expected_report"])
                self.assertEqual(grammar.paths(report, grammar.REPORT, root=grammar.REPORT), [])

    def test_all_4_canonical_vectors(self):
        vectors = json.loads((FIXTURES / "canonical-vectors.json").read_text(encoding="utf-8"))
        self.assertEqual(len(vectors["valid"]), 4)
        for vector in vectors["valid"]:
            with self.subTest(vector=vector["id"]):
                raw = bytes.fromhex(vector["raw_utf8_hex"])
                if vector["domain"] == "text":
                    value = raw.decode("utf-8")
                    self.assertEqual(value, vector["parsed_text"])
                else:
                    value = strict_loads(raw)
                    self.assertEqual(value, vector["parsed_value"])
                    self.assertEqual(canonical(value).hex(), vector["canonical_utf8_hex"])
                self.assertEqual(digest(vector["domain"], value), vector["expected_digest"])

    def test_all_13_raw_parser_negative_vectors(self):
        vectors = json.loads((FIXTURES / "canonical-vectors.json").read_text(encoding="utf-8"))
        self.assertEqual(len(vectors["invalid"]), 13)
        for vector in vectors["invalid"]:
            with self.subTest(vector=vector["id"]):
                raw = bytes.fromhex(vector["raw_utf8_hex"])
                with self.assertRaises(ProfileError):
                    strict_loads(raw)
                self.assertEqual(audit_bytes(raw), vectors["expected_parse_failure_report"])

    def test_copied_artifacts_are_byte_exact_and_paths_are_relative(self):
        provenance = json.loads((ROOT / "provenance.json").read_text(encoding="utf-8"))
        self.assertEqual(provenance["source_manifest_file_sha256"],
                         "517b2f88b6c5af395b2c4a10a9c674541805489cf5e1a9811b36873c5807f50d")
        self.assertEqual(len(provenance["artifacts"]), 6)
        for name, metadata in provenance["artifacts"].items():
            with self.subTest(file=name):
                self.assertFalse(Path(name).is_absolute())
                self.assertFalse(Path(metadata["source_relative_path"]).is_absolute())
                raw = (ROOT / name).read_bytes()
                self.assertEqual(hashlib.sha256(raw).hexdigest(), metadata["file_sha256"])
                self.assertEqual(len(raw), metadata["bytes"])
                self.assertNotIn(b"/Users/", raw)


class StrictProfileTests(unittest.TestCase):
    def test_scalar_pair_and_escaped_key_identity(self):
        self.assertEqual(strict_loads(b'{"\\ud83c\\udf0a":"\\ud83c\\udf0a"}'), {"🌊": "🌊"})
        with self.assertRaises(ProfileError):
            strict_loads('{"🌊":1,"\\ud83c\\udf0a":2}'.encode())

    def test_unicode_keys_are_not_normalized(self):
        self.assertEqual(strict_loads('{"é":1,"é":2}'.encode()), {"é": 1, "é": 2})

    def test_canonical_control_escapes_and_key_order(self):
        value = strict_loads('{"🌊":"/\\u0001\\b\\t\\n\\f\\r\\\"\\\\","é":0,"a":null}'.encode())
        self.assertEqual(canonical(value), '{"a":null,"é":0,"🌊":"/\\u0001\\b\\t\\n\\f\\r\\\"\\\\"}'.encode())

    def test_safe_integer_boundary_and_distinct_boolean(self):
        self.assertEqual(strict_loads(str(MAX_INTEGER).encode()), MAX_INTEGER)
        value = strict_loads(b'[true,false,null,0,1]')
        self.assertEqual([type(v) for v in value], [bool, bool, type(None), int, int])
        self.assertNotEqual(canonical(True), canonical(1))

    def test_more_numeric_and_syntax_rejections(self):
        for raw in (b'01', b'+1', b'1E0', b'1e-0', b'1.', b'.1', b'-Infinity', b'9007199254740992',
                    b'9' * 5000, b'\v{}', b'{}\x00', b'{"x":1,}', b'{/*x*/}', b'"\\udfff"',
                    b'"\\ud800a"', b'"\\ud800\\ud800"', b'"\xed\xa0\x80"'):
            with self.subTest(raw=raw[:24]):
                self.assertEqual(audit_bytes(raw)["global_scope"], "parse")

    def test_schema_rejection_still_hashes_parsed_input(self):
        for value in (None, True, 0, [], "x", {}):
            with self.subTest(value=value):
                report = audit_bytes(canonical(value))
                self.assertEqual(report["global_scope"], "input")
                self.assertEqual(report["envelope_digest"], digest("envelope", value))

    def test_raw_bytes_are_required(self):
        with self.assertRaises(TypeError):
            audit_bytes({})

    def test_domains_cannot_be_interchanged(self):
        hashes = {digest(domain, "same") for domain in ("text", "request", "evidence", "candidate", "envelope")}
        self.assertEqual(len(hashes), 5)
        self.assertNotIn(hashlib.sha256(b"same").hexdigest(), hashes)


if __name__ == "__main__":
    unittest.main()
