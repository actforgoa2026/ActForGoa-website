# Preserve uncertainty and study referents

The first two fresh diagnostic answers on integration `796089f` passed mechanical
checks but still overstated the evidence. One treated an unestablished narrower
classification as an exclusion. Another blurred the original study's location
with the unidentified receiving study area. A retained permission statement also
omitted an adjacent mandatory design condition.

This candidate changes only the native answer instructions. It asks the model to
state the evidential limit of a broader classification, identify original and
receiving studies explicitly, keep unknown receiving scope unknown, and retain
mandatory conditions when summarizing permission. Redundant wording is shortened
to preserve the existing evidence budget. Useful supported synthesis remains the
goal; these instructions do not prescribe abstention or case-specific answers.

The publication-year guard, exact native quotes, paragraph-local citations,
context dependencies, full request capture, models, effort, token/rate limits
and spending controls are unchanged. No named evaluation question, document ID,
location or taxon is embedded in the runtime change.

## Offline evidence

235 focused tests passed, including 15 new controls across both native models and
brief/standard styles. Three source-neutral authored cases cover classification,
method transfer and permission conditions. Each includes a useful supported
answer, an unsupported stronger answer and an explicit independent review
expectation. Tests verify complete evidence delivery and lossless handling of the
supported answers. Deliberately wrong answers with genuine quotes also pass the
mechanical guard, documenting why fresh semantic review is still necessary.
These authored examples are not model outputs or semantic acceptance.

The two recorded standard requests were reconstructed exactly from the immutable
capture: baseline generated request objects equal the actual captured outgoing
JSON, including history, visible evidence and schema. Explicit brief variants
were also checked. In all four comparisons, all previously retained passage
records and every non-system request field remain identical; only instructions
change. The capture SHA-256 is
`59a07b2237895a7a2ad17620581e0f78e5f9a19a5b5314c433f0c1f1149e2d48`.

| Request | Before prompt bytes | After prompt bytes | Passages | Schema bytes |
| --- | ---: | ---: | ---: | ---: |
| water, recorded standard | 22123 | 22324 | 10 | 1707 |
| water, derived brief | 22481 | 22682 | 10 | 1708 |
| species, recorded standard | 23329 | 23530 | 11 | 1777 |
| species, derived brief | 23687 | 23888 | 11 | 1778 |

All remain within the unchanged 24000-byte prompt and 4096-byte schema limits.
No paid calls, native corpus reads, ledger changes or preview changes were made.
The coordinator must independently review fresh exact-head answers before
resuming the broader acceptance run or declaring the site ready.
