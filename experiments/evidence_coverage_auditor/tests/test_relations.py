"""Additional synthetic cases; the frozen fixture/report pairs are never changed."""

from copy import deepcopy
import json
from pathlib import Path
import unittest
from unittest.mock import patch

from experiments.evidence_coverage_auditor import audit_bytes
from experiments.evidence_coverage_auditor import grammar
from experiments.evidence_coverage_auditor.auditor import publication_state
from experiments.evidence_coverage_auditor.profile import canonical, digest

EXAMPLES = json.loads((Path(__file__).parent / "fixtures" / "examples.json").read_text(encoding="utf-8"))["examples"]


def fixture(index=0):
    return deepcopy(EXAMPLES[index]["envelope"])


def run(envelope, rebind=True):
    # A fresh synthetic harness freezes modified input before proposing a candidate.
    # This helper is never applied to frozen expected reports or deliberate binding tests.
    if rebind and type(envelope.get("candidate")) is dict:
        envelope["candidate"]["binding"] = {
            "request_digest": digest("request", envelope["request"]),
            "evidence_digest": digest("evidence", envelope["evidence_package"]),
        }
    report = audit_bytes(canonical(envelope))
    if grammar.paths(report, grammar.REPORT, root=grammar.REPORT):
        raise AssertionError("Report does not conform to frozen audit grammar")
    return report


class AuditTests(unittest.TestCase):
    def assertFault(self, report, code, path=None, scope=None):
        self.assertIn(code, [e["code"] for e in report["errors"]])
        if path is not None:
            self.assertIn(path, [e["path"] for e in report["errors"] if e["code"] == code])
        if scope:
            self.assertEqual(report["global_scope"], scope)
            for key in ("claims", "gaps", "facets", "source_dates", "block_notices"):
                self.assertEqual(report[key], [])

    def test_schema_phases_and_no_candidate_cascade(self):
        e = fixture()
        e["candidate"] = None
        e["evidence_package"]["blocks"][0]["text_digest"] = "0" * 64
        r = run(e)
        self.assertFault(r, "INPUT_TEXT_DIGEST", scope="input")
        e["evidence_package"]["blocks"][0]["text_digest"] = digest("text", e["evidence_package"]["blocks"][0]["text"])
        self.assertFault(run(e), "CANDIDATE_SCHEMA", ["candidate"], "candidate")
        del e["candidate"]
        self.assertFault(run(e), "INPUT_SCHEMA", ["candidate"], "input")

    def test_true_false_string_offsets_fail_without_coercion(self):
        for value in (True, False, "0"):
            for field in ("source", "candidate"):
                with self.subTest(value=value, field=field):
                    e = fixture()
                    if field == "source":
                        e["evidence_package"]["blocks"][0]["source_range"]["start"] = value
                        self.assertFault(run(e), "INPUT_SCHEMA", scope="input")
                    else:
                        e["candidate"]["claims"][0]["supports"][0]["anchors"][0]["start"] = value
                        self.assertFault(run(e), "CANDIDATE_SCHEMA", scope="candidate")

    def test_full_string_identifier_and_digest_patterns(self):
        for ending in ("\n", "\r", "\r\n", "\u2028", " "):
            with self.subTest(ending=repr(ending)):
                e = fixture()
                e["evidence_package"]["sources"][0]["id"] += ending
                self.assertFault(run(e), "INPUT_SCHEMA", ["evidence_package", "sources", 0, "id"])
                e = fixture()
                e["candidate"]["binding"]["request_digest"] += ending
                self.assertFault(run(e, rebind=False), "CANDIDATE_SCHEMA", ["candidate", "binding", "request_digest"])

    def test_unknown_properties_rejected_at_every_reachable_object(self):
        for index in (0, 1, 4, 5):
            original = fixture(index)
            objects = []

            def collect(value, path):
                if type(value) is dict:
                    objects.append(path)
                    for key, child in value.items():
                        collect(child, path + [key])
                elif type(value) is list:
                    for i, child in enumerate(value):
                        collect(child, path + [i])

            collect(original, [])
            for path in objects:
                with self.subTest(fixture=index, path=path):
                    e = deepcopy(original)
                    target = e
                    for part in path:
                        target = target[part]
                    target["unsupported"] = "synthetic"
                    r = run(e, rebind=False)
                    expected = "CANDIDATE_SCHEMA" if path[:1] == ["candidate"] else "INPUT_SCHEMA"
                    self.assertFault(r, expected)

    def test_schema_failure_order_and_union_parent(self):
        e = fixture()
        e["request"]["zzz"] = None
        e["request"]["aaa"] = None
        self.assertEqual(run(e)["errors"][0]["path"], ["request", "aaa"])
        e = fixture()
        e["evidence_package"]["blocks"][0]["partition"]["basis"] = "model"
        self.assertFault(run(e), "INPUT_SCHEMA", ["evidence_package", "blocks", 0, "partition"])

    def test_duplicate_ids_stop_before_reference_faults(self):
        e = fixture()
        ep = e["evidence_package"]
        ep["sources"].append(deepcopy(ep["sources"][0]))
        ep["blocks"][0]["source_id"] = "src:unknown"
        r = run(e)
        self.assertFault(r, "INPUT_ID", ["evidence_package", "sources", 1, "id"], "input")
        self.assertEqual(len(r["errors"]), 1)

    def test_source_pair_unique_even_with_new_id(self):
        e = fixture()
        source = deepcopy(e["evidence_package"]["sources"][0])
        source["id"] = "src:duplicate-pair"
        e["evidence_package"]["sources"].append(source)
        self.assertFault(run(e), "INPUT_ID")

    def test_history_id_uniqueness(self):
        e = fixture(4)
        e["request"]["history"].append(deepcopy(e["request"]["history"][0]))
        self.assertFault(run(e), "INPUT_ID")

    def test_missing_target_cannot_share_supplied_identity(self):
        e = fixture(1)
        e["evidence_package"]["omissions"][0]["target_unit_id"] = "unit:water"
        self.assertFault(run(e), "INPUT_ID")

    def test_unknown_unused_source_and_locator(self):
        e = fixture()
        e["evidence_package"]["blocks"][0]["source_id"] = "src:absent"
        self.assertFault(run(e), "INPUT_REFERENCE", ["evidence_package", "blocks", 0, "source_id"])
        e = fixture()
        extra = deepcopy(e["evidence_package"]["sources"][0])
        extra.update(id="src:unused", document_id="doc:unused")
        e["evidence_package"]["sources"].append(extra)
        self.assertFault(run(e), "INPUT_REFERENCE", ["evidence_package", "sources", 1, "id"])
        e = fixture()
        e["evidence_package"]["blocks"][0]["locator"]["segment_id"] = "seg:other"
        self.assertFault(run(e), "INPUT_REFERENCE", ["evidence_package", "blocks", 0, "locator", "segment_id"])

    def test_document_scope_and_empty_scoped_package(self):
        e = fixture()
        e["request"]["document_scope"] = {"document_id": "doc:other", "generation_id": "gen:v1"}
        self.assertFault(run(e), "INPUT_SCOPE", scope="input")
        e = fixture(4)
        for field in ("sources", "blocks", "annotations", "context_edges", "omissions", "technical_events"):
            e["evidence_package"][field] = []
        e["request"]["document_scope"] = {"document_id": "doc:none", "generation_id": "gen:none"}
        self.assertEqual(run(e)["status"], "mechanically_valid")

    def test_range_digest_precedence(self):
        e = fixture()
        b = e["evidence_package"]["blocks"][0]
        b["source_range"]["end"] += 1
        b["text_digest"] = "0" * 64
        r = run(e)
        self.assertEqual([x["code"] for x in r["errors"]], ["INPUT_RANGE"])
        b["source_range"]["end"] -= 1
        self.assertFault(run(e), "INPUT_TEXT_DIGEST")

    def test_overlapping_source_ranges_require_matching_supplied_text(self):
        e = fixture()
        ep = e["evidence_package"]
        overlap = deepcopy(ep["blocks"][0])
        overlap["id"] = "blk:overlap"
        overlap["partition"]["units"][0]["id"] = "unit:overlap"
        ep["blocks"].append(overlap)
        self.assertEqual(run(e)["status"], "mechanically_valid")
        overlap["text"] = "x" + overlap["text"][1:]
        overlap["text_digest"] = digest("text", overlap["text"])
        self.assertFault(run(e), "INPUT_RANGE", ["evidence_package", "blocks", 2, "source_range"])

    def test_partition_gap_overlap_reordering_and_empty_range(self):
        for mode in ("gap", "overlap", "reverse", "empty"):
            with self.subTest(mode=mode):
                e = fixture(1)
                units = e["evidence_package"]["blocks"][0]["partition"]["units"]
                if mode == "gap":
                    units[1]["range"]["start"] += 1
                elif mode == "overlap":
                    units[1]["range"]["start"] -= 1
                elif mode == "reverse":
                    units.reverse()
                else:
                    units[0]["range"]["end"] = units[0]["range"]["start"]
                self.assertFault(run(e), "INPUT_PARTITION")

    def test_annotation_resolution_kind_and_use_counts(self):
        for mode in ("unknown", "wrong-kind", "unused", "reuse"):
            with self.subTest(mode=mode):
                e = fixture(1)
                ep = e["evidence_package"]
                if mode == "unknown":
                    ep["context_edges"][0]["annotation_id"] = "ann:absent"
                elif mode == "wrong-kind":
                    ep["context_edges"][0]["annotation_id"] = ep["blocks"][0]["partition"]["annotation_id"]
                elif mode == "unused":
                    extra = deepcopy(ep["annotations"][0]); extra["id"] = "ann:unused"
                    ep["annotations"].append(extra)
                else:
                    extra = deepcopy(ep["context_edges"][0]); extra["id"] = "dep:reuse"
                    ep["context_edges"].append(extra)
                self.assertFault(run(e), "INPUT_ANNOTATION")

    def test_source_graph_unknown_start_cross_source_duplicate_and_self(self):
        for mode in ("start", "cross-source", "duplicate", "self"):
            with self.subTest(mode=mode):
                e = fixture()
                ep = e["evidence_package"]
                if mode == "start":
                    ep["context_edges"][0]["from_unit_id"] = "unit:absent"
                    code = "INPUT_REFERENCE"
                elif mode == "cross-source":
                    source = deepcopy(ep["sources"][0]); source.update(id="src:second", document_id="doc:second")
                    ep["sources"].append(source); ep["blocks"][1]["source_id"] = source["id"]
                    code = "INPUT_SCOPE"
                elif mode == "duplicate":
                    edge = deepcopy(ep["context_edges"][0]); edge.update(id="dep:duplicate", annotation_id="ann:duplicate", role="exception")
                    ann = deepcopy(ep["annotations"][0]); ann["id"] = "ann:duplicate"
                    ep["context_edges"].append(edge); ep["annotations"].append(ann)
                    code = "INPUT_GRAPH"
                else:
                    ep["context_edges"][0]["to_unit_id"] = ep["context_edges"][0]["from_unit_id"]
                    code = "INPUT_GRAPH"
                self.assertFault(run(e), code, scope="input")

    def test_omission_requires_incoming_edge(self):
        e = fixture(1)
        ep = e["evidence_package"]
        annotation = ep["context_edges"][0]["annotation_id"]
        ep["context_edges"] = []
        ep["annotations"] = [a for a in ep["annotations"] if a["id"] != annotation]
        self.assertFault(run(e), "INPUT_OMISSION")

    def test_missing_duplicate_and_dangling_events(self):
        for mode in ("missing", "duplicate", "dangling"):
            with self.subTest(mode=mode):
                e = fixture(1)
                events = e["evidence_package"]["technical_events"]
                if mode == "missing":
                    events.clear()
                elif mode == "duplicate":
                    event = deepcopy(events[0]); event["id"] = "evt:duplicate"; events.append(event)
                else:
                    events[0]["omission_id"] = "omit:absent"
                self.assertFault(run(e), "INPUT_EVENT")

    def test_binding_mismatches_both_reported(self):
        e = fixture()
        e["candidate"]["binding"] = {"request_digest": "0"*64, "evidence_digest": "0"*64}
        r = run(e, rebind=False)
        self.assertEqual([e["code"] for e in r["errors"]], ["BINDING_MISMATCH"] * 2)
        self.assertEqual(r["errors"][0]["path"][-1], "evidence_digest")

    def test_candidate_duplicate_identity(self):
        for field in ("facets", "claims", "paragraphs"):
            e = fixture()
            e["candidate"][field].append(deepcopy(e["candidate"][field][0]))
            self.assertFault(run(e), "CANDIDATE_ID", scope="candidate")

    def test_request_span_exactness_nonempty_and_no_duplicates(self):
        for mode in ("unknown", "history", "offset", "text", "duplicate"):
            with self.subTest(mode=mode):
                e = fixture()
                spans = e["candidate"]["facets"][0]["request_spans"]
                if mode == "unknown":
                    spans[0]["turn_id"] = "turn:absent"
                elif mode == "history":
                    e["candidate"]["facets"][0]["history_spans"] = deepcopy(spans)
                elif mode == "offset":
                    spans[0]["end"] += 1
                elif mode == "text":
                    spans[0]["text"] += "x"
                else:
                    spans.append(deepcopy(spans[0]))
                self.assertFault(run(e), "REQUEST_SPAN", scope="candidate")

    def test_coverage_links_reciprocity_and_disposition(self):
        for mode in ("unknown-claim", "unknown-facet", "missing-row", "duplicate-row", "orphan-claim", "wrong-disposition", "clarification-mix"):
            with self.subTest(mode=mode):
                e = fixture(1)
                ca = e["candidate"]
                if mode == "unknown-claim":
                    ca["coverage"][0]["claim_ids"] = ["clm:absent"]
                elif mode == "unknown-facet":
                    ca["claims"][0]["facet_ids"] = ["fac:absent"]
                elif mode == "missing-row":
                    ca["coverage"].pop()
                elif mode == "duplicate-row":
                    ca["coverage"].append(deepcopy(ca["coverage"][0]))
                elif mode == "orphan-claim":
                    ca["coverage"][0]["claim_ids"] = []
                elif mode == "wrong-disposition":
                    ca["coverage"][0]["disposition"] = "gap"
                else:
                    ca["gaps"][0]["reason"] = "missing_referent"
                self.assertFault(run(e), "COVERAGE_LINK", scope="candidate")

    def test_gap_reason_must_be_distinct_within_facet(self):
        e = fixture(1)
        gap = deepcopy(e["candidate"]["gaps"][0]); gap["id"] = "gap:again"
        e["candidate"]["gaps"].append(gap)
        e["candidate"]["coverage"][1]["gap_ids"].append(gap["id"])
        self.assertFault(run(e), "COVERAGE_LINK")

    def test_paragraphs_cannot_drop_repeat_or_invent_claims(self):
        for mode in ("missing", "duplicate", "unknown"):
            e = fixture()
            if mode == "missing":
                e["candidate"]["paragraphs"] = []
            elif mode == "duplicate":
                p = deepcopy(e["candidate"]["paragraphs"][0]); p["id"] = "par:second"
                e["candidate"]["paragraphs"].append(p)
            else:
                e["candidate"]["paragraphs"][0]["claim_ids"].append("clm:absent")
            self.assertFault(run(e), "PARAGRAPH_MEMBERSHIP")

    def test_claim_dependency_references_self_and_render_order(self):
        for mode in ("unknown", "self", "order"):
            e = fixture(14)
            ca = e["candidate"]
            if mode == "unknown":
                ca["claims"][0]["depends_on_claim_ids"] = ["clm:absent"]
            elif mode == "self":
                ca["claims"][0]["depends_on_claim_ids"] = [ca["claims"][0]["id"]]
            else:
                ids = [c for p in ca["paragraphs"] for c in p["claim_ids"]]
                ca["paragraphs"] = [{"id": "par:reverse", "claim_ids": list(reversed(ids))}]
            self.assertFault(run(e), "CLAIM_DEPENDENCY_GRAPH")

    def test_opaque_locators_are_never_opened(self):
        e = fixture()
        for reference in ("file:///does-not-exist/private", "https://invalid.example/source", "../../private"):
            e["evidence_package"]["blocks"][0]["locator"]["original_reference"] = reference
            e["candidate"]["binding"]["evidence_digest"] = digest("evidence", e["evidence_package"])
            raw = canonical(e)
            with patch("builtins.open", side_effect=AssertionError("Unexpected I/O")), \
                 patch.object(Path, "open", side_effect=AssertionError("Unexpected I/O")):
                self.assertEqual(audit_bytes(raw)["status"], "mechanically_valid")


class PublicationTests(unittest.TestCase):
    def state(self, values):
        return publication_state({"id": "src:test", "publication_inputs": [
            {"field": "datePublished", "value": v} for v in values]})

    def test_gregorian_dates_full_strings_and_precedence(self):
        for value in ("2000-02-29", "2024/02/29", "0001", "9999-12-31"):
            self.assertEqual(self.state([value])["state"], "metadata_consistent")
        for value in ("1900-02-29", "2023/02/29", "0000", "2024-02/29", "2024\n", " 2024", "2024 ", "2024-13-01", "２０２４", "", "2024-1-01"):
            with self.subTest(value=value):
                self.assertEqual(self.state(["2022", "2023", value])["state"], "metadata_invalid")
        self.assertEqual(self.state([])["state"], "metadata_unknown")
        self.assertEqual(self.state(["2022", "2023"])["state"], "metadata_conflict")
        self.assertEqual(self.state(["2022-01-01", "2022/12/31", "2022"])["year"], 2022)
        self.assertEqual(self.state(["0001"])["label"], "Source publication year: 0001 (source metadata)")

    def test_retrieval_time_does_not_become_publication_date(self):
        e = fixture(6)
        e["evidence_package"]["sources"][0]["retrieved_at"] = "2026-10-27"
        r = run(e)
        self.assertEqual(r["status"], "mechanically_valid")
        self.assertEqual(r["source_dates"][0]["state"], "metadata_unknown")


if __name__ == "__main__":
    unittest.main()
