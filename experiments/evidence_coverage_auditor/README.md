# Offline evidence coverage auditor

This experiment checks the mechanics of a supplied synthetic evidence envelope:
strict JSON parsing, exact text anchors, source-context dependencies, declared
omissions, publication metadata, candidate coverage and deterministic error
propagation. It does not generate an answer or decide whether a claim is true,
relevant, complete, current or supported by the meaning of its quotations.

Every report retains these limits, even when mechanically valid:

```json
{"semantic":"not_assessed","original_authentication":"unverified","release":"hold","salvage":"not_performed"}
```

The input must be assembled by a trusted offline harness that owns and retains the
frozen request and evidence separately from the candidate. Matching hashes cannot
establish that ownership. Only `input_kind: synthetic` is supported. This command
is not a safe interface for trusting an entire provider-authored envelope.

## Run

From the repository root, with Python 3.10 or newer and no added dependencies:

```sh
python3 -m experiments.evidence_coverage_auditor envelope.json --output audit.json
python3 -m experiments.evidence_coverage_auditor - < envelope.json
python3 -m unittest discover -s experiments/evidence_coverage_auditor/tests -v
```

The first argument is an explicitly supplied local JSON file, or `-` for stdin.
Without `--output`, the JSON report goes to stdout. A report path is created
exclusively: existing files and symlinks are refused, including the input file.
There is no force/overwrite switch. Exit status is 0 for mechanically valid, 1
for a completed audit with a rejection or component issues, and 2 for a command,
I/O or interpreter nesting-capacity failure. An operational failure is not an
audit verdict. This small offline tool is not a resource-bounded public service.

The callable entry point is `audit_bytes(raw: bytes) -> dict`. Raw bytes are
required so duplicate fields and invalid numeric syntax cannot disappear before
validation. The callable does no I/O. The package reads only its fixed bundled
grammar/registry at import; the CLI reads only the explicitly named input and
writes only the requested report. Locator strings in evidence are never opened.

## Contract and provenance

The normative [contract](spec/contract.md), [envelope grammar](spec/envelope.schema.json),
[report grammar](spec/audit.schema.json) and [registry](spec/registry.json) are
byte-exact copies from the independently reviewed v2 design packet. The two
[synthetic fixture files](tests/fixtures/) are also byte-exact, including their
original authoring-status fields. The implementation does not rewrite frozen
expected reports. [provenance.json](provenance.json) records relative paths, sizes
and raw SHA-256 hashes, plus the approved source manifest's hash. No private
review reports, controls, corpus, credentials or absolute workstation paths are
included.

`grammar.py` is a private interpreter for the limited keywords in the two bundled
schemas. It is not a general JSON Schema library: it cannot fetch references or
load user schemas. In accordance with the normative contract, it uses true integer
types, scalar Unicode and full-string pattern matching. Input failures are checked
before candidate failures; local claim errors propagate only through declared
claim prerequisites. Full-block attachment is a diagnostic inspection plan,
never automatic salvage or an original-document authentication claim.

The tests replay all 21 complete frozen report pairs, four canonical vectors and
13 raw parser negatives. Additional synthetic cases exercise error precedence,
unknown fields, exhaustive partitions, graph closure, independent partial
results, local witnesses, dates, clarification, CLI output protection and the
distinction between structural eligibility and semantic acceptance. Independent
review of this implementation remains separate from author tests.

There are no production imports or changes to chat, search, API providers, UI,
native indexes, accounting, caches, source ingestion or deployment. A passing
experiment does not clear the separate conversational-answer and release holds.
