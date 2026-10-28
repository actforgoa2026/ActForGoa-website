# Source-context assessment continuation

28 October 2026. Offline development and read-only source recovery only.
No provider calls, paid diagnostics, runtime integration, deploy, ledger access,
local execution or stopped-thread activation. Remote main remains `a786df5`.

## Decision

Do not integrate the facet prototype as an automated semantic correction. It
helps organize source-to-wording review but still accepts materially wrong prose
with complete supports. Adding role names, stricter dependency closure or a
favorable facet checklist does not establish semantic accuracy. The smaller
mechanical improvement is explicit claim-local span selection with rejection of
missing context. The semantic handling remains a candidate for review, not a
solved public-answer contract.

The required correction must preserve the source's proposition when moving into
natural prose: its subject, obligation, measure, population, time, conditions and
uncertainty. In the examples below, that means retaining an obligation even when
details are unavailable, citing the named lake's identifying text, and stating the
source's numeric conflict instead of choosing a denominator. These are substantive
source-to-claim judgments; the prototype does not automate them. No word-matching
rule or extra role enum is proposed as a substitute.

## Newly inspected sources

Public production `/api/status` reported search ready, chat disabled, generation
`20261022T155701-21661179`, 1,156 documents, 21,220 pages and 78,432 chunks.
It reported model `gpt-5-mini`, which differs from current main's Anthropic code.
This is a read-only observed response, not proof of the deployed source commit or
provider configuration behind disabled chat. No `/api/chat` call was made.

### Avian study

Saved document `1feec0377b0046ae153a7d2f-881579ce3f03`, physical PDF pages
61, 66 and 67 (printed pages 54, 59 and 60). The original document downloaded
through the source API is 17,629,647 bytes and 155 pages. Its SHA-256 matches the
API metadata:
`1feec0377b0046ae153a7d2f42a0c94028a5d31c8521db9b9459cac7f8ec1ccb`.
Rendered original pages 61, 66 and 67 were inspected in cloud, alongside extracted
text. This confirms these source pages, not source accuracy or current biodiversity.

- Original page 67 shows the report date **7 March 2019**, the endemic avian table,
  Western Ghats endemism, 104 recorded/reported species and nine endemic avian
  species recorded in the primary survey.
- Page 61 says the stated overall species total uses secondary Zoological Survey
  of India information, complementing the 25 species recorded in the primary survey.
  Its footnote identifies a January 2008 archive source. Neither year establishes
  that the field survey itself occurred on the report date.
- Table 3.19 on original page 66 ends with a row numbered **105**, while the
  narrative says **104**. Keep that inconsistency visible. Do not silently decide
  that either number is a corrected total, and do not turn species into individual
  birds. The table's primary-survey count column is a different measure.
- The statement concerns the study area and Western Ghats endemism. It does not
  establish a current statewide Goa count or endemism restricted to Goa.

These findings constrain useful wording without replacing an answer with source
quotations. The authored preserving example retains the report's 16/104 claim,
avian setting, nine primary-survey records and explicit denominator caveat. It is
an inspected development example, not an independent accepted model answer.

### Bachbhatt Lake

Saved action-plan document `6dedf460d9433f0a7ca77abe-fb866f391a57`, physical
page 23. The returned complete extracted page contains several different lakes.
Selecting the whole page therefore includes unrelated subjects. The probe selects
three separate exact spans: the Bachbhatt/Salcete heading, the identifying sentence,
and the function text. The function span requires the two identifiers explicitly;
selecting only the function span fails without expanding citations.

An additional disagreement is visible between extracted sources: the page-23
narrative says **7.5009 ha**, while the retrieved page-17 table row says
**1.5009**. The lake example therefore makes no area claim. If answering an area
question, a candidate must expose the disagreement or state the gap; it must not
choose one silently. These action-plan pages were inspected as extracted text;
the action-plan original PDF has not been downloaded or visually authenticated.

### Additional storage-design obligation

Saved regulations document `131acd08c5377f26fb1250c5-2c2f91a1026b`, extracted
physical page 189, states a design/specification obligation for rainwater-harvesting
storage structures under the Goa Public Health Act, 1985 for preventing vector-borne
diseases. The example retains mandatory force and its storage-structure subject.
It does not establish legal currency, the complete applicable amendment chain or
parcel applicability.

This is an additional recovered obligation used as a source-grounded development
probe. It has **not** been identified as the exact annexure clause from the missing
historical diagnostic. The original regulations PDF was not authenticated in this
continuation. Do not relabel this probe as replay of that failed answer.

## Reviewable packet and reproduction

Private input files and output remain under the cloud worktree's ignored
`.reports/source-context-assessment/`. No raw research archives or original PDFs
are added to Git or static deployment. The tracked
`experiments/source_context_inputs.json` pins seven files by raw SHA-256.
`experiments/source_context_probe.py` reads only those explicit inputs, verifies
the pins and refuses output overwrite. It makes no network requests and reads no
credential, ledger or native index. It retains entire supplied page texts and
exact Unicode span offsets, without normalizing, clipping or assembling supports
to evade limits. Each selected span is at most 621 characters in these examples;
no example selects more than five supports.

From the cloud worktree:

```sh
python3 experiments/source_context_probe.py \
  --input-directory .reports/source-context-assessment \
  --output .reports/source-context-assessment/new-review-packet.json
```

Immutable packet `review-packet-v2.json` SHA-256:
`d7d0dd589e88a00da1f9a5c3250b62abe61f2daffd39543c2ef4c28104d66954`.
The unchanged `v1` and `v2` outputs have identical hashes; neither overwrites the
other. Every result retains semantic unassessed and launch hold. Explanatory
annotations are explicitly development-author opinions, never machine-derived
semantic verdicts or independent reviewer acceptance.

| Authored probe | Mechanical result | Substantive assessment |
| --- | --- | --- |
| Avian/date/denominator-preserving prose | Valid | Proposed positive control; independent review pending |
| Current statewide individual-bird/Goa-endemism claim | Valid | Wrong measure, scope, geography and time despite complete supports |
| Named lake and supported functions | Valid | Proposed positive control; independent review pending |
| Lake function without identifying spans | Rejected | Selection remains unchanged; no citation expansion |
| Wrong lake location and drinking-water use | Valid | Wrong subject attributes and unsupported use |
| Storage-design duty retained | Valid | Proposed positive control; legal currency remains unresolved |
| Duty replaced by unavailable design details | Valid | Explicit obligation was lost |

The three full source packs serialize to 12,447, 3,829 and 15,038 UTF-8 bytes.
These are pack-only measurements, not native requests, schema measurements,
final-message totals or complete-set sizing. They do not establish compliance
with any provider prompt cap. No new model, effort, prompt or judge configuration
has been tried.

## Corrected prototype semantics and checks

Question and provenance now participate in the review fingerprint. Edited question,
generation, source text, spans or claims invalidate the old review identity.
A favorable facet checklist records `facet_review: recorded_pass`, while semantic
status remains `not_assessed`. This fixes the prototype's earlier overly broad
`reviewer_accepted` label. Unknown or excessive supports and selected spans over
the existing 1,600-character quote allowance fail; evidence is never shortened.
These restrictions apply only to this offline probe, not to deployed runtime.

Verification performed:

- Experiment discovery with the explicit source packet: 75 tests run, one skipped
  (the unrelated historical frozen capture packet remains unavailable).
- Existing evidence-coverage auditor: 64 tests passed.
- Existing capture-review adapter: 40 tests run, one skipped for its missing frozen
  packet. Its specifications, fixtures and expected reports remain unchanged.
- `git diff --check` passed. Production files and the 71 semantic cases plus three
  HTTP journeys are unchanged. The counts above are unrelated to those gates.

No new research-runtime change was made, so its previously passing 121 tests were
not repeated. No browser/product visual work was performed.

## Remaining boundary

The initial semantic cases are now consumed development probes. Their authored
wording cannot be presented as model performance or used as new independent
acceptance. Whole-source context relationships outside these inspected examples,
complete-set bounds, the missing historical captures and actual persistent
accounting remain unresolved. There is no semantically accepted automated runtime
candidate yet. Do not begin paid acceptance on the basis of this packet.

Next useful work requires the cloud transfer of the historical source-dependency
artifact, review captures and frozen acceptance manifest, or explicit review of
this packet to select a bounded next implementation. Preserve all specified call,
reservation, byte, output, deadline and spending limits. Actual Goa-question,
citation, full-document and desktop/phone production launch checks remain separate
and must follow acceptance; these early source-route observations do not clear them.

Read-only inspection of coordination issue #89 also found a later durable report
([comment 6467306803](https://github.com/actforgoa2026/ActForGoa-website/issues/89#issuecomment-6467306803))
claiming 39 attempts and 2,360,028 monthly microdollars, beyond this chat's historical
28/2,316,292 checkpoint. Neither report is a substitute for persistent-ledger
reconciliation. The issue's historical temporary testing allowance and local
promotion instructions do not override this user's current 100-attempt/cloud-only
constraints or authorize paid continuation. No cloud location for the missing
private assessment/acceptance artifacts was supplied in those comments.
