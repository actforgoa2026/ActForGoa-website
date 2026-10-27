# Evidence coverage contract version 2

Normative offline contract, 27 October 2026. This packet replaces v1 only as the
proposed grammar for a future standalone auditor. V1 is preserved. No auditor,
provider integration, semantic judge, source resolver or renderer is implemented.
All valid examples are synthetic authoring fixtures, not accepted answers.

The authoritative files are this contract, envelope.schema.json, audit.schema.json
and registry.json. JSON Schema supplies nested field/type grammar; the ordered
relational rules below are also mandatory. Passing the schema alone is insufficient.
If these files disagree, stop and revise the packet; an implementer must not choose
a convenient interpretation. Every object rejects unknown fields at every depth.

## Narrow boundary

This version accepts only evidence packages with input_kind set to synthetic.
It makes source-owned scope applicability executable for synthetic fixtures without
pretending a real-source annotation pipeline exists. Source/capability verification
is always unverified in this version. A real-source workflow or attestation format
requires another reviewed design; do not admit it through a new field or enum.

The application-owned request/evidence package is frozen before the candidate.
The combined envelope is assembled by the trusted offline harness, not accepted
as one provider-authored object. The harness must retain its own request/evidence
inputs; matching hashes cannot establish who supplied them. This design assumes
that ownership boundary and introduces no cryptographic authorship claim.
The candidate may propose claims and coverage; it cannot edit partitions, graph
edges, omissions, technical events, publication metadata or review state. A model
proposal cannot be laundered into a trusted input annotation. Model annotations
are not a supported input basis in v2 and must be rejected, even if their hash is
correct. Input authorship is an offline trust boundary, not something a content
hash authenticates.

The user goal remains conversational explanation with local citations and full
document access. Structurally valid paraphrase and useful partial answers remain
representable. Structure cannot establish intent completeness, entailment, relevance,
true independence, current applicability or gap accuracy. A source list, reject-all
or a deliberately narrowed question is not answer success.

## Parsing and canonical identity

Apply this profile before schema validation or hashing:

1. Decode UTF-8 strictly. Reject a byte-order mark, invalid UTF-8, trailing content,
   non-JSON syntax and unpaired UTF-16 surrogate escapes. A valid escaped surrogate
   pair decodes to one Unicode scalar. All accepted strings contain Unicode scalar
   values only. Preserve combining characters, CR/LF, spaces and non-ASCII characters;
   do not normalize Unicode, trim, fold case or repair malformed source text.
2. Object member names must be unique after JSON escape decoding. For example a
   literal a key and a backslash-u0061 key are duplicates. Detect before constructing
   a dictionary that would discard one. Do not normalize names before comparison.
3. Number tokens must match 0 or a nonzero ASCII digit followed by ASCII digits,
   with value at most 9007199254740991. Reject negative numbers including -0,
   decimal points, exponent forms, NaN and Infinity. Thus 1.0 and 1e0 are rejected
   even if a schema library would call them integers. A string containing these
   characters remains a string and is governed by its field grammar.
4. JSON true/false/null retain their distinct types. Never coerce a Boolean, numeric
   string or float into an integer. Python implementations must not use
   isinstance(value, int) alone for offset validation because it admits bool.
   There is no Boolean-valued field in the v2 envelope; a Boolean token therefore
   passes lexical parsing but fails the envelope schema at its location.
5. Only ordinary JSON whitespace is allowed outside strings. Formatting and escape
   spelling are not identity: canonicalization happens after this strict parse.

Let C(x) be compact JSON of the accepted parsed value, object keys sorted by Unicode
code-point order, arrays kept in their original order, no whitespace separators,
and no trailing newline. Strings use literal non-ASCII scalar values, escaped double
quotes/backslashes, short escapes for backspace/tab/LF/form-feed/CR, and lowercase
four-digit Unicode escapes for the remaining U+0000–U+001F controls. Do not escape
solidus or other scalar values. Integers use their shortest base-10 representation;
null and Booleans use their JSON spellings. Encode the result as UTF-8 without BOM.

For values that passed the profile, the reference expression is
json.dumps(x, ensure_ascii=False, sort_keys=True, separators=(',', ':'),
allow_nan=False).encode('utf-8'). This expression alone is not the strict parser.

All identities use SHA-256, lowercase hexadecimal, with explicit byte domains:

| Identity | Preimage |
| --- | --- |
| request_digest | ASCII ActForGoa, NUL, ASCII evidence-coverage-v2, NUL, ASCII request, NUL, C(request) |
| evidence_digest | Same prefix, ASCII evidence, NUL, C(evidence_package) |
| candidate_digest for artifact bookkeeping | Same prefix, ASCII candidate, NUL, C(candidate) |
| envelope_digest in audit report | Same prefix, ASCII envelope, NUL, C(entire envelope) |
| block text_digest | Same prefix, ASCII text, NUL, UTF-8 of block.text directly |

Here same prefix means exactly the bytes ActForGoa NUL evidence-coverage-v2 NUL.
The envelope contract_version must equal afg-evidence-coverage-v2. The fixed domain
binds this version without a self-referential field. The candidate stores only the
request/evidence digests in binding; neither preimage contains those binding fields.
No text_digest authenticates the original file or the claimed original offset.

Manifest file_sha256 values, separately labeled as such, hash complete saved file
bytes without a domain prefix. They are file-integrity hashes, not interchangeably
usable request, evidence or text identities. V1 used a different undomained convention;
its IDs are not accepted as v2 IDs. V2 examples have newly computed bindings.

canonical-vectors.json freezes Unicode, escape-equivalent and formatting-equivalent
examples and invalid raw inputs. Invalid cases have expected rejection reasons,
not an invented canonical digest. These vectors are authored specifications, not
evidence that an auditor has run.

## Grammar and ID namespaces

All properties are required unless a schema explicitly uses a null variant. There
are no extra-property escape hatches, free-form metadata objects or arbitrary enum
extensions. Empty arrays are allowed only as specified. No automatic defaults,
case correction, field aliasing or coercion is permitted.

IDs use a namespace prefix and a lowercase ASCII suffix of one to 48 characters:
the first suffix character is a letter/digit, subsequent characters may also be a
hyphen. Prefixes and uniqueness scopes are:

| Prefix | Meaning | Unique within |
| --- | --- | --- |
| turn | Request turn | Request; question is always turn:current, forbidden in history |
| src | Saved source record | Evidence package; each document/generation pair occurs once |
| doc, gen | Claimed document and generation identity | Pair values identify a source; not independently authenticated |
| seg | Claimed source segment | A source; multiple blocks may refer to the same segment |
| blk | Supplied full block | Evidence package |
| unit | Source applicability unit or declared missing target | Evidence package, including omissions |
| ann | Input-author scope/dependency annotation | Evidence package |
| dep | Known source-context edge | Evidence package |
| omit | Declared omission | Evidence package |
| evt | Trusted-input technical event | Evidence package |
| fac, clm, gap, par | Facet, claim, gap and paragraph | Their respective candidate arrays |
| anc | Candidate support anchor | One claim only, across all of that claim's supports |
| err | Auditor-origin error | One report; decimal counter padded to at least six digits |

Request history is retained chronological context, not evidence. Roles may be user
or assistant and need not alternate. A document_scope, when non-null, constrains
every supplied or omitted source to its exact document/generation pair. Empty
evidence for a scoped request is permitted; scope does not assert a document was read.

All text offsets are zero-based Unicode code points with exclusive end. With the
scalar-only parser, these agree with Python string indexing. Bounds/range checks
must not clamp, trim or normalize. Source ranges refer to the claimed source
segment; partition and candidate anchor ranges are local to block.text.

registry.json exhaustively lists operations, witness states, context roles, gap
reasons, publication states and error codes. An operation enum declares intent;
it does not prove that the proposed facets cover the question. Witness values are
untrusted interpretations. A witness marked asserted needs nonempty interpretation
and claim-local anchor IDs; not_stated/not_applicable require null and no IDs;
unresolved has null interpretation and zero or more local IDs.

## One supplied set and one authoritative graph

evidence_package.blocks is exactly the set of full text blocks supplied to the
candidate. There is no wider candidate-block table, dispatched_block_ids,
context_ids or omitted_bundle_ids in this version. Such fields are schema errors.
Support/anchor resolution must not search the corpus or another package. Omissions
contain no text and are not evidence. All blocks remain attached in full when used;
unit selection does not replace a block with a clipped excerpt.

context_edges is the sole authoritative dependency graph, over unit IDs. Edges
are source-context requirements, not optional suggestions. Each edge has one
synthetic-author dependency annotation. Derive same-document/version from the
source records of its endpoints; do not accept same_document_version or
same_page_required Booleans. An edge may cross segments within the same saved
document/version. Cross-source premises require separate claim support, not a
context edge disguised as continuation.

Duplicate directed endpoint pairs are forbidden even when their role or annotation
differs. Self-edges and source-context cycles are global input errors. Different
edges may share a target. Graph discovery of an undeclared exception remains outside
the contract; closure only establishes the declared graph's consequences.

## Trusted applicability within a complete block

Every block has an exhaustive, ordered partition. Units cover [0, len(block.text))
without gaps, overlaps, empty ranges or reordering. Whitespace belongs to one of the
adjacent units and remains in the full block. This partition is fixed by the input
author before the candidate; the candidate cannot create or move a boundary.

Without an explicit annotation, whole_block_default has exactly one unit covering
the entire block. synthetic_author_partition requires at least two units and one
input-author partition annotation. Such an annotation asserts the intended source
scope only for this synthetic fixture. Its semantic correctness and real-source
generalization are not certified by the auditor. Model-proposed partitions, role
guesses and string heuristics are not admitted as authoritative bases.

A claim activates every unit in its supports, regardless of support role or where
inside that unit its exact anchor lies. It then activates every transitively required
unit through context_edges. Choosing a narrower anchor cannot waive an edge attached
to its unit. Every support must have at least one exact nonempty anchor wholly inside
the referenced unit. Anchors still do not prove the claim's meaning.

This resolves the within-block tension conditionally: a trusted synthetic partition
can separate a complete recharge statement from a second statement with an unavailable
permit exception. The recharge unit has no permit edge; the permit unit does. A
recharge claim remains structurally eligible for review, with the entire mixed block
attached. A permit claim activates the missing exception and is blocked_context.
With whole_block_default, the same known edge applies to the whole unit and both
claims are conservatively blocked. Do not claim independent-positive preservation
for an unannotated real block.

For each attached full block, report a block_notice for every unit in that block
whose known closure reaches an omission, even when that unit was not activated by
the claim. Include missing unit IDs and corresponding events. This retains the
known limitation of the other statement in the full-source view; it does not block
the independent claim automatically. No display or omission-warning UI is built here.

A candidate can still misbind a permit assertion to the recharge unit. If its anchors
are valid, the mechanical audit may pass while semantic review must reject the
wrong local support. The packet includes this contrast so the design cannot present
scope selection as an entailment check. Missing undeclared constraints remain a
separate blind spot.

## Ordered input invariants

Validate the envelope's keys/version and the presence of candidate first, then
Request and EvidencePackage grammar. Do not validate candidate contents in this
phase: its shape is checked at the later candidate phase. The whole-envelope schema
is a grammar reference; a validator must not classify a nested candidate type error
as an input error merely because it used one schema-validation call.

After these envelope/input grammar checks, apply these rules before
examining candidate content. Any failure here makes the whole input invalid:

1. Enforce namespace uniqueness. Source document/generation pairs are unique.
   Unit IDs are unique across supplied partitions and declared missing targets.
2. Source references resolve. The set of sources equals those used by blocks or
   omissions; unrelated unused source records are rejected. Locator.segment_id
   equals its block.segment_id. A non-null document_scope matches every source pair.
3. Each source_range satisfies 0 <= start < end and end-start equals the block's
   code-point length. text_digest matches its domain hash. For overlapping ranges
   of blocks in the same source/segment, supplied overlap text must agree exactly.
   Nonoverlap needs no invented missing source bytes. These arithmetic checks do
   not validate the asserted original offsets against an original document.
4. Partitions satisfy the exhaustive rules above. Default partitions have no
   annotation field. Each scoped partition references a partition-kind annotation;
   each graph edge references a dependency-kind annotation. Each annotation is
   referenced exactly once. Duplicate, unused or wrong-kind annotations are invalid.
5. Every edge starts at a supplied unit. Its target is either a supplied unit or
   exactly one declared omitted unit. Both endpoints belong to the same source
   document/generation. Reject undeclared targets, duplicate pairs and cycles.
6. Every omission target is absent from supplied units and has at least one incoming
   edge. Its source resolves and matches each predecessor's source. Omission reasons
   are context_not_retained, context_budget_excluded or extraction_failed. Omission
   records contain only claimed identity/location and reason, never source text.
7. Each omission has exactly one context_omission event referencing it. Each source
   whose publication state is not metadata_consistent has exactly one
   publication_unresolved event; consistent sources have none. Reject duplicates,
   dangling events, wrong event kinds and invented events. Event IDs are unique.

Known unavailable context is therefore a valid incomplete package with a declared
target, omission and corresponding event. A dangling edge without that path is
malformed input. A matching hash cannot change either classification. Input authors'
statements that a budget excluded something are preserved, not verified against a
provider budget by this auditor; no actual cap or reservation changes occur.

## Publication metadata state

Only the four publication fields enumerated in the schema are accepted. Input values
are raw strings and may be empty or malformed. Duplicate entries in this array are
permitted and preserved; unlike object member names they are not parser ambiguity.

A value parses only as exactly four ASCII digits YYYY, YYYY-MM-DD or YYYY/MM/DD,
with year 0001–9999 and a valid proleptic Gregorian calendar date when a month/day
is present. No trimming, timezone inference, upload-path parsing or substring date
extraction. Leap years are divisible by 4, excluding centuries not divisible by 400.

Derive one state per source in this precedence order:

- Empty publication_inputs: metadata_unknown, year null.
- Any malformed input: metadata_invalid, year null, even if another input is valid.
- Otherwise more than one distinct parsed year: metadata_conflict, year null.
- Otherwise one year: metadata_consistent and that year. Different full dates within
  that same year do not conflict for this year-only label; retain their raw inputs.

Labels are exact: metadata_consistent uses `Source publication year: YYYY (source
metadata)` with four-digit year; unknown uses `Source publication year not established`;
invalid/conflict use `Source publication year unresolved`. State remains available
separately so these last two cannot be conflated internally. These are source-metadata
labels, not verification of publisher identity, observation period or present force.
retrieved_at is an uninterpreted provenance string/null and never a publication input.

An unresolved publication date does not automatically invalidate a factual claim.
It does produce the unresolved label/event. A date-related gap is permitted only
under the event rules below; whether that gap answers the user's request is semantic.

## Candidate global consistency

Candidate type/unknown-field failure rejects the candidate globally. For a typed
candidate, these additional global rules precede component auditing:

1. binding digests match the frozen request and evidence. No correction or fallback
   to v1 serialization is allowed.
2. Facet, claim, gap and paragraph IDs are unique. There is exactly one coverage row
   for each facet and no other row. Every request_span is an exact nonempty range in
   turn:current; every history_span is an exact nonempty range in a retained history
   turn. Repeated identical (turn,start,end) spans within one array are forbidden.
3. Claim facet_ids resolve and are nonempty. A claim ID appears in a facet's coverage
   row if and only if the claim lists that facet. A gap is referenced exactly once,
   in the row of its own existing facet. All coverage links resolve; no orphan
   claim/gap/facet is accepted.
4. claims means nonempty claim_ids and empty gap_ids. claims_and_gap requires both
   nonempty. gap means empty claim_ids and nonempty non-clarification gaps.
   needs_clarification means no claims and nonempty clarification-family gaps only.
   Non-clarification rows cannot contain clarification gaps. Multiple gaps on one
   facet must have distinct reason codes. These are declared dispositions, not proof
   of semantic coverage.
5. Paragraphs reference every claim exactly once across the complete ordered array,
   with no unknown or duplicate membership. No claim means no paragraphs. There is
   no free-form answer text outside claim.text.
6. depends_on_claim_ids resolve to other claims, with no self-link or claim-dependency
   cycle. Every prerequisite precedes its dependent in flattened paragraph order.
   This graph is distinct from source-context edges. Facet dependency fields from
   v1 are not supported; inter-claim prerequisites use this one candidate graph.

These global failures prevent unambiguous component reporting. They are technical
rejection, not absence of evidence. In particular, a malformed Boolean/string offset
does not become a valid range by coercion. Structural schemas cannot determine whether
the facet list faithfully decomposes the question.

## Component rules and gap registry

After global checks, audit all claims and gaps without publishing or repairing any.

For each claim, support unit IDs must refer to supplied units, not omission targets.
Each unit appears at most once in supports and at least one support has role primary.
Every anchor lies inside its unit, reproduces block.text[start:end] exactly and has
a claim-local unique anc ID. Witness IDs resolve only within that same claim's anchors.
An anchor elsewhere in the candidate cannot satisfy a missing local witness. A
second claim may repeat its own support/anchor explicitly. Incorrect source roles,
an irrelevant genuine quote and a deceptive witness remain semantic failures even
when these local checks pass.

From every resolvable support unit, follow all known edges. Record the closure,
missing targets and their events. Any reachable omission blocks that claim as
blocked_context. Merely citing the omission's source record cannot supply the
missing text. Full blocks containing all reachable supplied units remain attached
as diagnostics. Their order follows evidence_package.blocks, not a newly invented
source chronology. Closure/missing lists are sorted lexicographically by ID.
closure_unit_ids contains reachable supplied units only, including the supplied
roots; missing_unit_ids contains reachable declared omission targets separately.
An unknown support unit yields a local reference error; no anchor/range/closure
checks are invented for that unknown unit. Other resolvable supports are still
reported diagnostically. Claim dependencies propagate errors only; they never
import another claim's support, anchors, closure or citations.

Gap fields do not contain generated factual prose. Scope is always the actual
supplied package. Their registry rules are:

| Gap family | Allowed fields and exact binding |
| --- | --- |
| semantic reasons in registry | event_ids and clarification_options empty; related_unit_ids are supplied units or empty |
| required_context_unavailable | related supplied roots nonempty; event_ids equal all context events for context_not_retained omissions reachable from those roots, and are nonempty |
| context_budget_excluded | Same rule for context_budget_excluded omissions |
| extraction_unavailable | Same rule for extraction_failed omissions |
| publication_metadata_unresolved | related supplied units nonempty; event_ids equal all publication_unresolved events for their source IDs and are nonempty |
| ambiguous_referent | related_unit_ids/event_ids empty; at least two distinct clarification_options, each exactly one of that facet's history_spans |
| missing_referent | related_unit_ids/event_ids/clarification_options empty; facet still has its exact current-question span |

All non-clarification reasons require empty clarification_options. Technical gaps
use only their mapped event family; a matching-looking invented ID or a different
source's date event fails locally. Every referenced related unit/event must exist.
For technical reachability, roots must be supplied units; omission targets cannot
serve as roots. A technical gap can represent known missing context while independent
claims remain eligible for review. An invalid gap does not become a claim that the
corpus lacks the requested fact.

Current applicability is not a publication-metadata event: a historical value plus
unknown present applicability uses the semantic reason
requested_current_applicability_not_established and claims_and_gap, even when the
source publication year is known. A false semantic gap can pass structure and must
fail independent usefulness review. Likewise, a valid ambiguity record does not
prove that clarification is actually necessary.

## Error scope and deterministic propagation

registry.json fixes every error code's scope. Report field paths as arrays of member
names/indices, not copied input values. On a strict parse failure return one
PARSE_PROFILE error at the root; no canonical envelope digest is available. On a
schema failure report the lexicographically first failing member path and the stage's
SCHEMA code. Missing-required-field paths include the missing member name; an extra
field path names that member. Compare path components by their C encoding so different
implementations choose the same first schema location; conditional branches use the
deepest shared parent path when no union variant matches.

For relational checks, run the input phase, then candidate-global phase, then all
components. Finish one phase before deciding whether to advance. If a prerequisite
table is ambiguous or malformed, stop at that rule group; do not invent cascaded
reference errors using a partly built table. The phase/rule ordering above is
normative. Within an applicable group, collect all independent instances and sort
them by scope order parse,input,candidate,claim,gap; then subject ID (null first),
code, and C(path). Collapse identical (scope,subject,code,path) records. Number the
sorted records err:000001 upward. Cases specify stage/code and path for primary
faults, not imaginary semantic verdicts.

The following mapping fixes the relational error choices. Follow the numbered
input/global rules in their stated order; where a row names several subchecks, use
their written left-to-right order. Within one subcheck, collect all independent
faults before stopping that group. Later groups are not evaluated after a global
fault. Components are all evaluated because their ID/dependency tables are valid.

| Check | Error code and path |
| --- | --- |
| Envelope/request/package grammar | INPUT_SCHEMA at failing path |
| Input rule 1 duplicate IDs or source pairs | INPUT_ID at each duplicate-after-first record's id or target_unit_id; source-pair duplicate uses id |
| Input rule 2 block/omission source reference, unused source, locator segment mismatch | INPUT_REFERENCE at source_id, unused source id, or locator.segment_id respectively |
| Input rule 2 document_scope mismatch | INPUT_SCOPE at offending source record |
| Input rule 3 range arithmetic, then overlap disagreement | INPUT_RANGE at source_range; for disagreement use the later block's source_range |
| Input rule 3 text digest mismatch | INPUT_TEXT_DIGEST at text_digest |
| Input rule 4 partition coverage/order/default count | INPUT_PARTITION at partition |
| Input rule 4 annotation reference/kind/use count | INPUT_ANNOTATION at annotation_id, or unused/reused annotation's id |
| Input rule 5 edge endpoint unresolved, then same-source mismatch | INPUT_REFERENCE at endpoint; INPUT_SCOPE at edge record |
| Input rule 5 duplicate pair, then self-edge, then cycle | INPUT_GRAPH at duplicate-after-first edge, self-edge, or context_edges array for any cycle |
| Input rule 6 omission without incoming edge | INPUT_OMISSION at target_unit_id |
| Input rule 7 event dangling reference, then multiplicity/state mismatch | INPUT_EVENT at event record for dangling/excess event; at omission or source record for missing event |
| Candidate grammar | CANDIDATE_SCHEMA at failing candidate path |
| Candidate rule 1 | BINDING_MISMATCH at mismatching digest field |
| Candidate rule 2 IDs, then request/history spans | CANDIDATE_ID at duplicate-after-first id; REQUEST_SPAN at bad/repeated span |
| Candidate rules 3–4 links/reciprocity/cardinality | COVERAGE_LINK at affected claim.facet_ids, gap.facet_id, or coverage row; missing row uses coverage array |
| Candidate rule 5 | PARAGRAPH_MEMBERSHIP at duplicate/unknown membership; missing claim uses paragraphs array |
| Candidate rule 6 references, self-link, cycle, then order | CLAIM_DEPENDENCY_GRAPH at bad dependency list, claims array for a cycle, or dependent's dependency list for order |
| Claim support unknown/omitted target | CLAIM_SUPPORT_REFERENCE at support.unit_id |
| Claim duplicate support unit or no primary | CLAIM_SUPPORT_ROLE at repeated support, or supports array for no primary |
| Claim invalid/nonlocal/duplicate anchor | CLAIM_ANCHOR at anchor record; duplicate-after-first local ID is reported |
| Claim witness borrowing/unresolved ID | CLAIM_WITNESS_REFERENCE at slot.anchor_ids |
| Claim known context unavailable | CONTEXT_UNAVAILABLE at supports array, one per claim regardless of number of missing targets |
| Gap unknown related unit/event | GAP_REFERENCE at related_unit_ids or event_ids |
| Gap family/event-set mismatch | GAP_EVENT_BINDING at event_ids |
| Gap invalid clarification-options membership/count or forbidden options | GAP_CLARIFICATION at clarification_options |

Do not cascade local witness-reference errors from an invalid known anchor: its
ID still exists locally, although the anchor error already makes the claim invalid.
An anchor ID under an unknown support is also a declared local ID for reference
purposes; it is unusable evidence because the support error persists. Duplicate
anchor IDs retain an error and never resolve to another claim's anchor.

| Condition | Classification and action |
| --- | --- |
| Strict JSON profile failure | global_reject, global_scope parse, no component/source/notice arrays |
| Malformed source, invalid partition/graph, undeclared missing target or inconsistent event | global_reject, input; no candidate traversal |
| Binding, candidate schema/ID/coverage/paragraph or declared claim-DAG failure | global_reject, candidate; no component traversal |
| Unknown local support, bad anchor, missing local witness or invalid support roles | Direct invalid_claim error; keep diagnostic record, do not repair |
| Declared unavailable context reachable from a claim | Direct CONTEXT_UNAVAILABLE error; blocked_context, not malformed input |
| Invalid gap reference/event/clarification linkage | Direct invalid_gap error; no negative evidence conclusion |
| Declared claim dependent on an affected claim | Propagate originating claim error IDs along prerequisite-to-dependent direction |
| Facet references an affected claim or gap | component_issue with the union of referenced origin error IDs; no semantic reclassification |

Claim propagation uses the acyclic depends_on_claim_ids graph after global checks.
For each claim, its origin_error_ids are its direct local errors plus the transitive
origin errors of its prerequisites. If it has any direct non-context error, state is
invalid_claim; else a direct CONTEXT_UNAVAILABLE yields blocked_context; else inherited
errors yield blocked_dependency; otherwise eligible_for_review. Retain all causes
regardless of the chosen primary state. No new error is invented for each descendant.
Gap errors do not propagate into claims because there is no gap-to-claim dependency
field. A facet is eligible_for_review only when all its linked components are;
this still means structural eligibility, not answer sufficiency.

Overall status is component_issues if any component has an error, otherwise
mechanically_valid. Global rejection empties claims/gaps/facets/source_dates/
block_notices and sets global_scope. Non-global results include every original
claim/gap/facet in input array order and one source date per source in source order.
block_notices follow block order, then unit order. All ID sets inside records are
deduplicated and sorted. On parsed input, envelope_digest uses the canonical domain
even if later validation rejects it; on parse failure it is null.

There is no synthesized-answer field or filtered paragraph output in the report.
Attached-block lists are inspection plans, not automatic salvage. Every result,
including parse rejection, has semantic not_assessed, original_authentication
unverified, release hold and salvage not_performed. Report eligibility never means
supported, safe, semantically accepted or ready for display.

## Capabilities not established

Block hashes and arithmetic can establish internal identity and offset consistency.
They cannot authenticate original files, source authorship, dates, page numbering,
an original download, a reader URL, extraction completeness or the asserted source
offset against unseen text. original_reference is opaque data and must never be
opened by the proposed auditor. All locator kinds, including pdf_page, remain
unverified. A deliberate shifted-but-consistent original range illustrates this
limit. Separate evidence and authorization would be needed to validate capabilities;
this schema has no flag that can silently upgrade them.

No semantic/control expectations are part of the candidate envelope. Fixture labels
and expected audit reports are external authoring files, never input hints for a
future generator. The visible table_heading_and_footnote scenario is corrected to
direct in fixture-corrections.json; no private control or historical acceptance is
changed. New optional fee/conflict semantic scenarios are deferred to keep this
revision focused on executable mechanical rules.

The next decision is review of this v2 packet, not permission to implement its
auditor. All provider/native/private-control/key/ledger/cap/preview/runtime/UI/deploy
restrictions remain. The 5 USD monthly and 100 UTC-day caps and failed reservations
are unchanged. Full AI accuracy and accounting holds remain in force.
