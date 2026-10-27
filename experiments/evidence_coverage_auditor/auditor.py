"""Deterministic synthetic-input auditor. No fetching, generation or repair."""

from collections import Counter, defaultdict, deque
from datetime import date
import re

from . import grammar
from .profile import VERSION, ProfileError, canonical, digest, strict_loads

EP = ["evidence_package"]
CA = ["candidate"]
_SCOPES = ("parse", "input", "candidate", "claim", "gap")


def _report(envelope_digest):
    return {
        "contract_version": VERSION, "envelope_digest": envelope_digest,
        "status": "mechanically_valid", "global_scope": None, "errors": [],
        "claims": [], "gaps": [], "facets": [], "source_dates": [], "block_notices": [],
        "semantic": "not_assessed", "original_authentication": "unverified",
        "release": "hold", "salvage": "not_performed",
    }


def _number_errors(errors):
    unique = {(e["scope"], e["subject_id"], e["code"], canonical(e["path"])): e
              for e in errors}
    ordered = sorted(unique.values(), key=lambda e: (
        _SCOPES.index(e["scope"]), e["subject_id"] or "", e["code"], canonical(e["path"])))
    return [dict(id=f"err:{i:06d}", **error) for i, error in enumerate(ordered, 1)]


def _cyclic(graph):
    """Iterative DAG check; a long valid chain does not consume Python stack."""
    incoming = Counter({node: 0 for node in graph})
    for targets in graph.values():
        incoming.update(targets)
    ready = deque(node for node, count in incoming.items() if count == 0)
    visited = 0
    while ready:
        node = ready.popleft()
        visited += 1
        for target in graph.get(node, ()):
            incoming[target] -= 1
            if incoming[target] == 0:
                ready.append(target)
    return visited != len(incoming)


def publication_state(source):
    """Derive only a publication-year metadata label, never current applicability."""
    years = set()
    invalid = False
    for item in source["publication_inputs"]:
        value = item["value"]
        match = re.fullmatch(r"([0-9]{4})(?:([-\/])([0-9]{2})\2([0-9]{2}))?", value)
        try:
            if match is None:
                raise ValueError
            year = int(match[1])
            date(year, int(match[3]) if match[3] else 1,
                 int(match[4]) if match[4] else 1)
            years.add(year)
        except ValueError:
            invalid = True
    if not source["publication_inputs"]:
        state, year, label = "metadata_unknown", None, "Source publication year not established"
    elif invalid:
        state, year, label = "metadata_invalid", None, "Source publication year unresolved"
    elif len(years) > 1:
        state, year, label = "metadata_conflict", None, "Source publication year unresolved"
    else:
        year = next(iter(years))
        state, label = "metadata_consistent", f"Source publication year: {year:04d} (source metadata)"
    return {"source_id": source["id"], "state": state, "year": year, "label": label}


class _GlobalReject(Exception):
    pass


class _Audit:
    def __init__(self, envelope):
        self.envelope = envelope
        self.report = _report(digest("envelope", envelope))
        self.errors = []

    def error(self, code, path, subject=None):
        self.errors.append({"code": code, "scope": grammar.REGISTRY["error_code_scope"][code],
                            "subject_id": subject, "path": path})

    def stop_if_errors(self):
        if self.errors:
            raise _GlobalReject

    def check_grammar(self, value, schema, path, code):
        failures = grammar.paths(value, schema, path)
        if failures:
            self.error(code, grammar.first_path(failures))
            self.stop_if_errors()

    def duplicates(self, records, path, field, code, seen=None):
        seen = set() if seen is None else seen
        for i, record in enumerate(records):
            identity = record[field]
            if identity in seen:
                self.error(code, path + [i, field])
            seen.add(identity)
        return seen

    def input_checks(self):
        schema = grammar.ENVELOPE
        # Candidate is required by the shell, but its contents belong to a later phase.
        shell = {k: v for k, v in schema.items() if k != "properties"}
        shell["properties"] = {k: (v if k == "contract_version" else {})
                               for k, v in schema["properties"].items()}
        self.check_grammar(self.envelope, shell, [], "INPUT_SCHEMA")
        failures = []
        for field in ("request", "evidence_package"):
            failures += grammar.paths(self.envelope[field], schema["properties"][field], [field])
        if failures:
            self.error("INPUT_SCHEMA", grammar.first_path(failures))
            self.stop_if_errors()
        self.request = self.envelope["request"]
        self.evidence = ep = self.envelope["evidence_package"]

        # Input rule 1: identities must be unambiguous before constructing lookup tables.
        self.duplicates(self.request["history"], ["request", "history"], "id", "INPUT_ID",
                        {self.request["question"]["id"]})
        for key in ("sources", "blocks", "annotations", "context_edges", "omissions", "technical_events"):
            self.duplicates(ep[key], EP + [key], "id", "INPUT_ID")
        pairs = set()
        for i, source in enumerate(ep["sources"]):
            pair = (source["document_id"], source["generation_id"])
            if pair in pairs:
                self.error("INPUT_ID", EP + ["sources", i, "id"])
            pairs.add(pair)
        seen_units = set()
        for i, block in enumerate(ep["blocks"]):
            self.duplicates(block["partition"]["units"], EP + ["blocks", i, "partition", "units"],
                            "id", "INPUT_ID", seen_units)
        self.duplicates(ep["omissions"], EP + ["omissions"], "target_unit_id", "INPUT_ID", seen_units)
        self.stop_if_errors()
        self.sources = {s["id"]: s for s in ep["sources"]}
        self.blocks = {b["id"]: b for b in ep["blocks"]}
        self.units = {u["id"]: (b, u) for b in ep["blocks"] for u in b["partition"]["units"]}
        self.omissions = {o["id"]: o for o in ep["omissions"]}
        self.missing = {o["target_unit_id"]: o for o in ep["omissions"]}
        self.annotations = {a["id"]: a for a in ep["annotations"]}
        self.events = {e["id"]: e for e in ep["technical_events"]}

        # Rule 2: references, unused sources, locator identity, then request scope.
        for key in ("blocks", "omissions"):
            for i, item in enumerate(ep[key]):
                if item["source_id"] not in self.sources:
                    self.error("INPUT_REFERENCE", EP + [key, i, "source_id"])
        self.stop_if_errors()
        used_sources = {item["source_id"] for key in ("blocks", "omissions") for item in ep[key]}
        for i, source in enumerate(ep["sources"]):
            if source["id"] not in used_sources:
                self.error("INPUT_REFERENCE", EP + ["sources", i, "id"])
        self.stop_if_errors()
        for i, block in enumerate(ep["blocks"]):
            if block["locator"]["segment_id"] != block["segment_id"]:
                self.error("INPUT_REFERENCE", EP + ["blocks", i, "locator", "segment_id"])
        self.stop_if_errors()
        scope = self.request["document_scope"]
        if scope is not None:
            for i, source in enumerate(ep["sources"]):
                if any(source[k] != scope[k] for k in ("document_id", "generation_id")):
                    self.error("INPUT_SCOPE", EP + ["sources", i])
        self.stop_if_errors()

        # Rule 3: local arithmetic is not original-document authentication.
        for i, block in enumerate(ep["blocks"]):
            start, end = block["source_range"]["start"], block["source_range"]["end"]
            if start >= end or end - start != len(block["text"]):
                self.error("INPUT_RANGE", EP + ["blocks", i, "source_range"])
        self.stop_if_errors()
        by_segment = defaultdict(list)
        for i, block in enumerate(ep["blocks"]):
            start, end = block["source_range"]["start"], block["source_range"]["end"]
            prior = by_segment[(block["source_id"], block["segment_id"])]
            for other in prior:
                a, b = other["source_range"]["start"], other["source_range"]["end"]
                left, right = max(start, a), min(end, b)
                if left < right and block["text"][left-start:right-start] != other["text"][left-a:right-a]:
                    self.error("INPUT_RANGE", EP + ["blocks", i, "source_range"])
            prior.append(block)
        self.stop_if_errors()
        for i, block in enumerate(ep["blocks"]):
            if block["text_digest"] != digest("text", block["text"]):
                self.error("INPUT_TEXT_DIGEST", EP + ["blocks", i, "text_digest"])
        self.stop_if_errors()

        # Rule 4: exhaustive units, then annotation resolution, kind and use count.
        annotation_uses = []
        for i, block in enumerate(ep["blocks"]):
            partition = block["partition"]
            cursor = 0
            valid = True
            for unit in partition["units"]:
                start, end = unit["range"]["start"], unit["range"]["end"]
                valid &= start == cursor and start < end
                cursor = end
            if not valid or cursor != len(block["text"]):
                self.error("INPUT_PARTITION", EP + ["blocks", i, "partition"])
            if "annotation_id" in partition:
                annotation_uses.append((partition["annotation_id"], "partition",
                                        EP + ["blocks", i, "partition", "annotation_id"]))
        self.stop_if_errors()
        annotation_uses += [(e["annotation_id"], "dependency", EP + ["context_edges", i, "annotation_id"])
                            for i, e in enumerate(ep["context_edges"])]
        for identity, kind, path in annotation_uses:
            if identity not in self.annotations:
                self.error("INPUT_ANNOTATION", path)
        self.stop_if_errors()
        for identity, kind, path in annotation_uses:
            if self.annotations[identity]["kind"] != kind:
                self.error("INPUT_ANNOTATION", path)
        self.stop_if_errors()
        counts = Counter(identity for identity, _, _ in annotation_uses)
        for i, annotation in enumerate(ep["annotations"]):
            if counts[annotation["id"]] != 1:
                self.error("INPUT_ANNOTATION", EP + ["annotations", i, "id"])
        self.stop_if_errors()

        # Rule 5: the only context graph is over supplied units and declared omissions.
        for i, edge in enumerate(ep["context_edges"]):
            if edge["from_unit_id"] not in self.units:
                self.error("INPUT_REFERENCE", EP + ["context_edges", i, "from_unit_id"])
            if edge["to_unit_id"] not in self.units and edge["to_unit_id"] not in self.missing:
                self.error("INPUT_REFERENCE", EP + ["context_edges", i, "to_unit_id"])
        self.stop_if_errors()
        for i, edge in enumerate(ep["context_edges"]):
            source_id = self.unit_source(edge["from_unit_id"])
            target_source = self.unit_source(edge["to_unit_id"])
            if source_id != target_source:
                self.error("INPUT_SCOPE", EP + ["context_edges", i])
        self.stop_if_errors()
        pairs = set()
        for i, edge in enumerate(ep["context_edges"]):
            pair = edge["from_unit_id"], edge["to_unit_id"]
            if pair in pairs:
                self.error("INPUT_GRAPH", EP + ["context_edges", i])
            pairs.add(pair)
        self.stop_if_errors()
        for i, edge in enumerate(ep["context_edges"]):
            if edge["from_unit_id"] == edge["to_unit_id"]:
                self.error("INPUT_GRAPH", EP + ["context_edges", i])
        self.stop_if_errors()
        self.graph = defaultdict(list)
        for edge in ep["context_edges"]:
            self.graph[edge["from_unit_id"]].append(edge["to_unit_id"])
        if _cyclic(self.graph):
            self.error("INPUT_GRAPH", EP + ["context_edges"])
        self.stop_if_errors()

        # Rule 6: no orphan omission. Identity/source checks have already passed.
        targets = {e["to_unit_id"] for e in ep["context_edges"]}
        for i, omission in enumerate(ep["omissions"]):
            if omission["target_unit_id"] not in targets:
                self.error("INPUT_OMISSION", EP + ["omissions", i, "target_unit_id"])
        self.stop_if_errors()

        # Rule 7: technical events are exactly those implied by the trusted inputs.
        self.dates = [publication_state(source) for source in ep["sources"]]
        unresolved = {s["source_id"] for s in self.dates if s["state"] != "metadata_consistent"}
        for i, event in enumerate(ep["technical_events"]):
            known = (event["omission_id"] in self.omissions if event["kind"] == "context_omission"
                     else event["source_id"] in self.sources)
            if not known:
                self.error("INPUT_EVENT", EP + ["technical_events", i])
        self.stop_if_errors()
        context_events, publication_events = {}, {}
        for i, event in enumerate(ep["technical_events"]):
            if event["kind"] == "context_omission":
                key, table, allowed = event["omission_id"], context_events, True
            else:
                key, table = event["source_id"], publication_events
                allowed = key in unresolved
            if key in table or not allowed:
                self.error("INPUT_EVENT", EP + ["technical_events", i])
            table.setdefault(key, event["id"])
        for i, omission in enumerate(ep["omissions"]):
            if omission["id"] not in context_events:
                self.error("INPUT_EVENT", EP + ["omissions", i])
        for i, source in enumerate(ep["sources"]):
            if source["id"] in unresolved and source["id"] not in publication_events:
                self.error("INPUT_EVENT", EP + ["sources", i])
        self.stop_if_errors()
        self.context_events, self.publication_events = context_events, publication_events

    def unit_source(self, identity):
        return (self.units[identity][0]["source_id"] if identity in self.units
                else self.missing[identity]["source_id"])

    def closure(self, roots):
        visited, pending = set(), list(roots)
        while pending:
            identity = pending.pop()
            if identity not in visited:
                visited.add(identity)
                pending.extend(self.graph.get(identity, ()))
        return visited & self.units.keys(), visited & self.missing.keys()

    def omission_events(self, missing):
        return {self.context_events[self.missing[u]["id"]] for u in missing}

    def candidate_checks(self):
        self.candidate = ca = self.envelope["candidate"]
        self.check_grammar(ca, grammar.ENVELOPE["$defs"]["Candidate"], CA, "CANDIDATE_SCHEMA")
        for field, domain, value in (("request_digest", "request", self.request),
                                     ("evidence_digest", "evidence", self.evidence)):
            if ca["binding"][field] != digest(domain, value):
                self.error("BINDING_MISMATCH", CA + ["binding", field])
        self.stop_if_errors()

        for key in ("facets", "claims", "gaps", "paragraphs"):
            self.duplicates(ca[key], CA + [key], "id", "CANDIDATE_ID")
        self.stop_if_errors()
        self.facets = {f["id"]: f for f in ca["facets"]}
        self.claims = {c["id"]: c for c in ca["claims"]}
        self.gaps = {g["id"]: g for g in ca["gaps"]}
        turns = {t["id"]: t["text"] for t in self.request["history"]}
        for i, facet in enumerate(ca["facets"]):
            for field in ("request_spans", "history_spans"):
                texts = ({"turn:current": self.request["question"]["text"]}
                         if field == "request_spans" else turns)
                seen = set()
                for j, span in enumerate(facet[field]):
                    key = span["turn_id"], span["start"], span["end"]
                    text = texts.get(span["turn_id"])
                    valid = (text is not None and span["start"] < span["end"] <= len(text)
                             and text[span["start"]:span["end"]] == span["text"])
                    if not valid or key in seen:
                        self.error("REQUEST_SPAN", CA + ["facets", i, field, j])
                    seen.add(key)
        self.stop_if_errors()

        # Resolve links and the one-row-per-facet table before checking reciprocity.
        rows = {}
        for i, row in enumerate(ca["coverage"]):
            fid = row["facet_id"]
            if (fid not in self.facets or fid in rows
                    or any(c not in self.claims for c in row["claim_ids"])
                    or any(g not in self.gaps for g in row["gap_ids"])):
                self.error("COVERAGE_LINK", CA + ["coverage", i])
            rows.setdefault(fid, row)
        if self.facets.keys() - rows.keys():
            self.error("COVERAGE_LINK", CA + ["coverage"])
        for i, claim in enumerate(ca["claims"]):
            if any(f not in self.facets for f in claim["facet_ids"]):
                self.error("COVERAGE_LINK", CA + ["claims", i, "facet_ids"])
        for i, gap in enumerate(ca["gaps"]):
            if gap["facet_id"] not in self.facets:
                self.error("COVERAGE_LINK", CA + ["gaps", i, "facet_id"])
        self.stop_if_errors()
        for i, row in enumerate(ca["coverage"]):
            fid = row["facet_id"]
            expected_claims = {c["id"] for c in ca["claims"] if fid in c["facet_ids"]}
            expected_gaps = {g["id"] for g in ca["gaps"] if fid == g["facet_id"]}
            if set(row["claim_ids"]) != expected_claims or set(row["gap_ids"]) != expected_gaps:
                self.error("COVERAGE_LINK", CA + ["coverage", i])
        self.stop_if_errors()
        clarification = set(grammar.REGISTRY["clarification_reasons"])
        for i, row in enumerate(ca["coverage"]):
            claims, gaps = row["claim_ids"], row["gap_ids"]
            reasons = [self.gaps[g]["reason"] for g in gaps]
            disposition = row["disposition"]
            valid = {
                "claims": bool(claims) and not gaps,
                "claims_and_gap": bool(claims) and bool(gaps),
                "gap": not claims and bool(gaps),
                "needs_clarification": not claims and bool(gaps),
            }[disposition]
            valid &= all((r in clarification) == (disposition == "needs_clarification") for r in reasons)
            valid &= len(reasons) == len(set(reasons))
            if not valid:
                self.error("COVERAGE_LINK", CA + ["coverage", i])
        self.stop_if_errors()
        self.coverage = rows

        self.claim_order, seen = [], set()
        for i, paragraph in enumerate(ca["paragraphs"]):
            for j, identity in enumerate(paragraph["claim_ids"]):
                if identity not in self.claims or identity in seen:
                    self.error("PARAGRAPH_MEMBERSHIP", CA + ["paragraphs", i, "claim_ids", j])
                self.claim_order.append(identity)
                seen.add(identity)
        if self.claims.keys() - seen:
            self.error("PARAGRAPH_MEMBERSHIP", CA + ["paragraphs"])
        self.stop_if_errors()
        for i, claim in enumerate(ca["claims"]):
            if any(c not in self.claims for c in claim["depends_on_claim_ids"]):
                self.error("CLAIM_DEPENDENCY_GRAPH", CA + ["claims", i, "depends_on_claim_ids"])
        self.stop_if_errors()
        for i, claim in enumerate(ca["claims"]):
            if claim["id"] in claim["depends_on_claim_ids"]:
                self.error("CLAIM_DEPENDENCY_GRAPH", CA + ["claims", i, "depends_on_claim_ids"])
        self.stop_if_errors()
        if _cyclic({c["id"]: c["depends_on_claim_ids"] for c in ca["claims"]}):
            self.error("CLAIM_DEPENDENCY_GRAPH", CA + ["claims"])
        self.stop_if_errors()
        positions = {identity: i for i, identity in enumerate(self.claim_order)}
        for i, claim in enumerate(ca["claims"]):
            if any(positions[c] >= positions[claim["id"]] for c in claim["depends_on_claim_ids"]):
                self.error("CLAIM_DEPENDENCY_GRAPH", CA + ["claims", i, "depends_on_claim_ids"])
        self.stop_if_errors()

    def claim_check(self, i, claim):
        path, cid = CA + ["claims", i], claim["id"]
        seen_units, seen_anchors = set(), set()
        for j, support in enumerate(claim["supports"]):
            sp = path + ["supports", j]
            uid = support["unit_id"]
            if uid not in self.units:
                self.error("CLAIM_SUPPORT_REFERENCE", sp + ["unit_id"], cid)
            if uid in seen_units:
                self.error("CLAIM_SUPPORT_ROLE", sp, cid)
            seen_units.add(uid)
            for k, anchor in enumerate(support["anchors"]):
                invalid = anchor["id"] in seen_anchors
                seen_anchors.add(anchor["id"])
                if uid in self.units:
                    block, unit = self.units[uid]
                    start, end = anchor["start"], anchor["end"]
                    invalid |= not (unit["range"]["start"] <= start < end <= unit["range"]["end"]
                                    and block["text"][start:end] == anchor["text"])
                if invalid:
                    self.error("CLAIM_ANCHOR", sp + ["anchors", k], cid)
        if not any(s["role"] == "primary" for s in claim["supports"]):
            self.error("CLAIM_SUPPORT_ROLE", path + ["supports"], cid)
        for slot, witness in claim["semantic_witness"].items():
            if any(a not in seen_anchors for a in witness["anchor_ids"]):
                self.error("CLAIM_WITNESS_REFERENCE", path + ["semantic_witness", slot, "anchor_ids"], cid)
        supplied, missing = self.closure(seen_units & self.units.keys())
        if missing:
            self.error("CONTEXT_UNAVAILABLE", path + ["supports"], cid)
        blocks = {self.units[u][0]["id"] for u in supplied}
        return {
            "id": cid, "state": "eligible_for_review", "origin_error_ids": [],
            "closure_unit_ids": sorted(supplied), "missing_unit_ids": sorted(missing),
            "attached_block_ids": [b["id"] for b in self.evidence["blocks"] if b["id"] in blocks],
        }

    def gap_check(self, i, gap):
        path, gid = CA + ["gaps", i], gap["id"]
        roots, events = set(gap["related_unit_ids"]), set(gap["event_ids"])
        roots_known = roots <= self.units.keys()
        if not roots_known:
            self.error("GAP_REFERENCE", path + ["related_unit_ids"], gid)
        if not events <= self.events.keys():
            self.error("GAP_REFERENCE", path + ["event_ids"], gid)
        reason, options = gap["reason"], gap["clarification_options"]
        semantic = grammar.REGISTRY["semantic_gap_reasons"]
        clarification = grammar.REGISTRY["clarification_reasons"]
        if reason in semantic:
            if events:
                self.error("GAP_EVENT_BINDING", path + ["event_ids"], gid)
        elif reason in clarification:
            if roots or events:
                self.error("GAP_EVENT_BINDING", path + ["event_ids"], gid)
        elif not roots:
            self.error("GAP_EVENT_BINDING", path + ["event_ids"], gid)
        elif roots_known:
            if reason == "publication_metadata_unresolved":
                source_ids = {self.unit_source(u) for u in roots}
                expected = {self.publication_events[s] for s in source_ids if s in self.publication_events}
            else:
                _, missing = self.closure(roots)
                omission_reason = grammar.REGISTRY["technical_gap_reason_to_event_target"][reason]
                expected = self.omission_events(u for u in missing if self.missing[u]["reason"] == omission_reason)
            if not expected or events != expected:
                self.error("GAP_EVENT_BINDING", path + ["event_ids"], gid)
        if reason == "ambiguous_referent":
            unique_options = {canonical(option) for option in options}
            history = {canonical(span) for span in self.facets[gap["facet_id"]]["history_spans"]}
            if len(unique_options) < 2 or len(unique_options) != len(options) or not unique_options <= history:
                self.error("GAP_CLARIFICATION", path + ["clarification_options"], gid)
        elif options:
            self.error("GAP_CLARIFICATION", path + ["clarification_options"], gid)
        return {"id": gid, "state": "eligible_for_review", "origin_error_ids": []}

    def component_checks(self):
        claims = [self.claim_check(i, claim) for i, claim in enumerate(self.candidate["claims"])]
        gaps = [self.gap_check(i, gap) for i, gap in enumerate(self.candidate["gaps"])]
        errors = _number_errors(self.errors)
        direct = defaultdict(list)
        for error in errors:
            direct[error["subject_id"]].append(error)
        by_claim = {claim["id"]: claim for claim in claims}
        for cid in self.claim_order:
            claim = by_claim[cid]
            local = direct[cid]
            inherited = {e for dep in self.claims[cid]["depends_on_claim_ids"]
                         for e in by_claim[dep]["origin_error_ids"]}
            if any(e["code"] != "CONTEXT_UNAVAILABLE" for e in local):
                claim["state"] = "invalid_claim"
            elif local:
                claim["state"] = "blocked_context"
            elif inherited:
                claim["state"] = "blocked_dependency"
            claim["origin_error_ids"] = sorted(inherited | {e["id"] for e in local})
        for gap in gaps:
            gap["origin_error_ids"] = sorted(e["id"] for e in direct[gap["id"]])
            if gap["origin_error_ids"]:
                gap["state"] = "invalid_gap"
        by_component = {c["id"]: c for c in claims + gaps}
        facets = []
        for facet in self.candidate["facets"]:
            row = self.coverage[facet["id"]]
            origins = sorted({e for c in row["claim_ids"] + row["gap_ids"]
                              for e in by_component[c]["origin_error_ids"]})
            facets.append({"id": facet["id"], "state": "component_issue" if origins else "eligible_for_review",
                           "origin_error_ids": origins})
        attached = {b for claim in claims for b in claim["attached_block_ids"]}
        notices = []
        for block in self.evidence["blocks"]:
            if block["id"] not in attached:
                continue
            for unit in block["partition"]["units"]:
                _, missing = self.closure([unit["id"]])
                if missing:
                    notices.append({"block_id": block["id"], "unit_id": unit["id"],
                                    "missing_unit_ids": sorted(missing),
                                    "event_ids": sorted(self.omission_events(missing))})
        self.report.update(status="component_issues" if errors else "mechanically_valid", errors=errors,
                           claims=claims, gaps=gaps, facets=facets, source_dates=self.dates, block_notices=notices)

    def run(self):
        try:
            self.input_checks()
            self.candidate_checks()
        except _GlobalReject:
            self.report.update(status="global_reject", global_scope=self.errors[0]["scope"],
                               errors=_number_errors(self.errors))
            return self.report
        self.component_checks()
        return self.report


def audit_bytes(raw: bytes) -> dict:
    """Audit one raw synthetic envelope. Output always holds semantic/release status.

    Only JSON bytes are accepted so callers cannot bypass the lexical profile by
    supplying already-decoded dictionaries. This function performs no I/O.
    """
    try:
        value = strict_loads(raw)
    except ProfileError:
        report = _report(None)
        report.update(status="global_reject", global_scope="parse", errors=_number_errors([
            {"code": "PARSE_PROFILE", "scope": "parse", "subject_id": None, "path": []}]))
        return report
    return _Audit(value).run()
