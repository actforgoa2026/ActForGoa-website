from copy import deepcopy
import unittest

from experiments.evidence_coverage_auditor.tests import test_relations

fixture, run = test_relations.fixture, test_relations.run


class ComponentTests(unittest.TestCase):
    assertFault = test_relations.AuditTests.assertFault

    def test_unknown_support_keeps_other_closure_and_declared_witness_ids(self):
        e = fixture()
        claim = e["candidate"]["claims"][0]
        claim["supports"][0]["unit_id"] = "unit:unknown"
        # An invalid range under the unresolved unit must not invent a range fault.
        claim["supports"][0]["anchors"][0]["start"] = 999
        r = run(e)
        self.assertEqual([x["code"] for x in r["errors"]], ["CLAIM_SUPPORT_REFERENCE"])
        self.assertEqual(r["claims"][0]["state"], "invalid_claim")
        self.assertEqual(r["claims"][0]["closure_unit_ids"], ["unit:scope"])
        self.assertEqual(r["claims"][0]["attached_block_ids"], ["blk:scope"])

    def test_omission_target_cannot_be_claim_support(self):
        e = fixture(1)
        e["candidate"]["claims"][0]["supports"][0]["unit_id"] = "unit:exception"
        r = run(e)
        self.assertFault(r, "CLAIM_SUPPORT_REFERENCE")
        self.assertEqual(r["claims"][0]["closure_unit_ids"], [])
        self.assertEqual(r["claims"][0]["missing_unit_ids"], [])

    def test_invalid_known_anchor_does_not_cascade_witness_error(self):
        e = fixture()
        e["candidate"]["claims"][0]["supports"][0]["anchors"][0]["text"] = "Different supplied wording"
        r = run(e)
        self.assertEqual([x["code"] for x in r["errors"]], ["CLAIM_ANCHOR"])
        self.assertEqual(r["claims"][0]["attached_block_ids"], ["blk:process", "blk:scope"])

    def test_anchor_cannot_cross_trusted_unit_boundary(self):
        e = fixture(1)
        block = e["evidence_package"]["blocks"][0]
        anchor = e["candidate"]["claims"][0]["supports"][0]["anchors"][0]
        anchor.update(start=0, end=len(block["text"]), text=block["text"])
        self.assertFault(run(e), "CLAIM_ANCHOR")

    def test_anchor_ids_are_unique_per_claim_and_reusable_in_other_claims(self):
        e = fixture()
        claim = e["candidate"]["claims"][0]
        duplicate = deepcopy(claim["supports"][0]["anchors"][0])
        claim["supports"][0]["anchors"].append(duplicate)
        r = run(e)
        self.assertEqual([x["code"] for x in r["errors"]], ["CLAIM_ANCHOR"])
        e = fixture()
        clone = deepcopy(e["candidate"]["claims"][0]); clone["id"] = "clm:clone"
        e["candidate"]["claims"].append(clone)
        e["candidate"]["paragraphs"][0]["claim_ids"].append(clone["id"])
        e["candidate"]["coverage"][0]["claim_ids"].append(clone["id"])
        self.assertEqual(run(e)["status"], "mechanically_valid")

    def test_duplicate_support_and_no_primary(self):
        e = fixture()
        claim = e["candidate"]["claims"][0]
        for support in claim["supports"]:
            support["role"] = "constraint"
        duplicate = deepcopy(claim["supports"][0]); duplicate["anchors"][0]["id"] = "anc:repeated"
        claim["supports"].append(duplicate)
        r = run(e)
        self.assertEqual([x["code"] for x in r["errors"]], ["CLAIM_SUPPORT_ROLE"] * 2)

    def test_narrow_anchor_and_contrary_role_still_activate_missing_context(self):
        e = fixture(2)
        ca = e["candidate"]
        support = deepcopy(ca["claims"][1]["supports"][0])
        support["role"] = "contrary"
        anchor = support["anchors"][0]
        anchor["id"] = "anc:tiny"
        anchor["end"] = anchor["start"] + 1
        anchor["text"] = e["evidence_package"]["blocks"][0]["text"][anchor["start"]:anchor["end"]]
        ca["claims"][0]["supports"].append(support)
        r = run(e)
        self.assertEqual([c["state"] for c in r["claims"]], ["blocked_context", "blocked_context"])
        self.assertEqual(len(r["errors"]), 2)
        self.assertTrue(all(x["code"] == "CONTEXT_UNAVAILABLE" for x in r["errors"]))

    def test_whole_block_default_is_conservative(self):
        e = fixture(1)
        ep, ca = e["evidence_package"], e["candidate"]
        block = ep["blocks"][0]
        annotation = block["partition"]["annotation_id"]
        block["partition"] = {"basis": "whole_block_default", "units": [
            {"id": "unit:whole", "range": {"start": 0, "end": len(block["text"])}}]}
        ep["annotations"] = [a for a in ep["annotations"] if a["id"] != annotation]
        ep["context_edges"][0]["from_unit_id"] = "unit:whole"
        ca["claims"][0]["supports"][0]["unit_id"] = "unit:whole"
        ca["gaps"][0]["related_unit_ids"] = ["unit:whole"]
        r = run(e)
        self.assertEqual(r["claims"][0]["state"], "blocked_context")
        self.assertEqual(r["claims"][0]["attached_block_ids"], ["blk:mixed"])

    def test_transitive_omission_closure_and_exact_multiple_events(self):
        e = fixture()
        ep, ca = e["evidence_package"], e["candidate"]
        for number, reason in ((1, "context_not_retained"), (2, "extraction_failed")):
            suffix = str(number)
            ep["annotations"].append({"id": "ann:missing-" + suffix, "kind": "dependency", "basis": "synthetic_author", "note": "Synthetic test annotation"})
            ep["context_edges"].append({"id": "dep:missing-" + suffix, "from_unit_id": "unit:scope", "to_unit_id": "unit:missing-" + suffix, "role": "exception", "annotation_id": "ann:missing-" + suffix})
            ep["omissions"].append({"id": "omit:missing-" + suffix, "target_unit_id": "unit:missing-" + suffix, "source_id": "src:a", "segment_id": "seg:missing", "reason": reason})
            ep["technical_events"].append({"id": "evt:missing-" + suffix, "kind": "context_omission", "omission_id": "omit:missing-" + suffix})
        r = run(e)
        self.assertEqual(r["claims"][0]["state"], "blocked_context")
        self.assertEqual(r["claims"][0]["missing_unit_ids"], ["unit:missing-1", "unit:missing-2"])
        self.assertEqual(len(r["errors"]), 1)
        self.assertEqual(len(r["block_notices"]), 2)
        for notice in r["block_notices"]:
            self.assertEqual(notice["event_ids"], ["evt:missing-1", "evt:missing-2"])
        gap = {"id": "gap:missing", "facet_id": "fac:route", "reason": "required_context_unavailable", "related_unit_ids": ["unit:process"], "event_ids": ["evt:missing-1"], "clarification_options": []}
        ca["gaps"].append(gap)
        ca["coverage"][0].update(disposition="claims_and_gap", gap_ids=["gap:missing"])
        self.assertEqual(run(e)["gaps"][0]["state"], "eligible_for_review")
        gap["event_ids"].append("evt:missing-2")
        self.assertFault(run(e), "GAP_EVENT_BINDING")

    def test_attachment_order_comes_from_evidence_not_sorted_ids(self):
        e = fixture()
        e["evidence_package"]["blocks"].reverse()
        r = run(e)
        self.assertEqual(r["claims"][0]["attached_block_ids"], ["blk:scope", "blk:process"])
        self.assertEqual(r["claims"][0]["closure_unit_ids"], ["unit:process", "unit:scope"])

    def test_local_error_propagates_transitively_without_importing_support(self):
        e = fixture(14)
        ca = e["candidate"]
        fourth = deepcopy(ca["claims"][2]); fourth["id"] = "clm:fourth"
        fourth["depends_on_claim_ids"] = [ca["claims"][2]["id"]]
        # Keep one genuine support with locally declared anchors and no borrowed witness.
        fourth["supports"] = [deepcopy(ca["claims"][0]["supports"][1])]
        fourth["supports"][0]["role"] = "primary"
        for slot in fourth["semantic_witness"].values():
            slot.update(state="not_stated", interpretation=None, anchor_ids=[])
        ca["claims"].append(fourth)
        ca["paragraphs"][0]["claim_ids"].append(fourth["id"])
        ca["coverage"][0]["claim_ids"].append(fourth["id"])
        r = run(e)
        self.assertEqual([c["state"] for c in r["claims"]], ["eligible_for_review", "invalid_claim", "blocked_dependency", "blocked_dependency"])
        self.assertEqual(r["claims"][3]["closure_unit_ids"], ["unit:scope"])
        self.assertEqual(r["claims"][3]["origin_error_ids"], r["claims"][1]["origin_error_ids"])
        self.assertEqual(len(r["errors"]), 1)

    def test_state_priority_and_all_direct_and_inherited_causes(self):
        e = fixture(2)
        ca = e["candidate"]
        ca["claims"][0]["supports"][0]["anchors"][0]["text"] = "bad quote"
        ca["claims"][1]["depends_on_claim_ids"] = ["clm:water"]
        r = run(e)
        self.assertEqual([c["state"] for c in r["claims"]], ["invalid_claim", "blocked_context"])
        self.assertEqual(len(r["claims"][1]["origin_error_ids"]), 2)
        ca["claims"][1]["supports"][0]["anchors"][0]["text"] = "another bad quote"
        r = run(e)
        self.assertEqual(r["claims"][1]["state"], "invalid_claim")
        self.assertEqual(len(r["claims"][1]["origin_error_ids"]), 3)

    def test_invalid_gap_does_not_invalidate_unrelated_claim_or_facet(self):
        e = fixture(1)
        e["candidate"]["gaps"][0]["event_ids"] = []
        r = run(e)
        self.assertEqual(r["claims"][0]["state"], "eligible_for_review")
        self.assertEqual([f["state"] for f in r["facets"]], ["eligible_for_review", "component_issue"])
        self.assertEqual(r["gaps"][0]["state"], "invalid_gap")

    def test_unknown_gap_references_are_local(self):
        e = fixture(1)
        e["candidate"]["gaps"][0]["related_unit_ids"] = ["unit:absent"]
        e["candidate"]["gaps"][0]["event_ids"] = ["evt:absent"]
        r = run(e)
        self.assertEqual([x["code"] for x in r["errors"]], ["GAP_REFERENCE"] * 2)
        self.assertEqual(r["claims"][0]["state"], "eligible_for_review")

    def test_semantic_gaps_cannot_borrow_events_or_options(self):
        e = fixture(1)
        gap = e["candidate"]["gaps"][0]
        gap["reason"] = "requested_current_applicability_not_established"
        gap["clarification_options"] = deepcopy(e["candidate"]["facets"][0]["request_spans"])
        r = run(e)
        self.assertFault(r, "GAP_EVENT_BINDING")
        self.assertFault(r, "GAP_CLARIFICATION")

    def test_all_context_event_reason_mappings(self):
        for reason, gap_reason in (("context_not_retained", "required_context_unavailable"),
                                   ("context_budget_excluded", "context_budget_excluded"),
                                   ("extraction_failed", "extraction_unavailable")):
            e = fixture(1)
            e["evidence_package"]["omissions"][0]["reason"] = reason
            e["candidate"]["gaps"][0]["reason"] = gap_reason
            self.assertEqual(run(e)["status"], "mechanically_valid")

    def test_clarification_options_must_be_distinct_exact_history_spans(self):
        for mode in ("too-few", "duplicate", "unknown", "altered"):
            with self.subTest(mode=mode):
                e = fixture(4)
                options = e["candidate"]["gaps"][0]["clarification_options"]
                if mode == "too-few":
                    options.pop()
                elif mode == "duplicate":
                    options.append(deepcopy(options[0]))
                elif mode == "unknown":
                    options[0]["turn_id"] = "turn:other"
                else:
                    options[0]["text"] += "x"
                self.assertFault(run(e), "GAP_CLARIFICATION")

    def test_missing_referent_requires_empty_options(self):
        e = fixture(4)
        gap = e["candidate"]["gaps"][0]
        gap["reason"] = "missing_referent"
        self.assertFault(run(e), "GAP_CLARIFICATION")
        gap["clarification_options"] = []
        self.assertEqual(run(e)["status"], "mechanically_valid")

    def test_wrong_meaning_and_shifted_original_ranges_never_upgrade_sentinels(self):
        for index in (0, 3, 13):
            r = run(fixture(index))
            self.assertEqual(r["status"], "mechanically_valid")
            self.assertEqual((r["semantic"], r["original_authentication"], r["release"], r["salvage"]),
                             ("not_assessed", "unverified", "hold", "not_performed"))


if __name__ == "__main__":
    unittest.main()
