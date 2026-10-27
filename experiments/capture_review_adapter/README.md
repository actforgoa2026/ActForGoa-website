# Offline capture review adapter

This standalone tool links review annotations to five fixed local artifacts: two
historical captures, two review records and an unaccepted illustration. It checks
identity, pointers, exact Unicode spans, provenance and coverage links. A result
is `linked_for_review`; it never claims semantic accuracy or release acceptance.

The complete historical `human_review`, prepared evidence, raw diagnostic and
normalized answer remain distinct and unchanged. Missing members have no value;
captured null and empty values retain their values and hashes. Later opinions are
kept in a separate `review_annotations` field.

## Use

From the repository root, with Python 3.10 or later and no added dependencies:

```sh
python3 -m experiments.capture_review_adapter input.json
python3 -m experiments.capture_review_adapter input.json --output review.json
```

The input follows `spec/shapes.schema.json`, definition `Input`. It supplies each
artifact's local path and its pinned raw-file SHA256. Delivery paths are not
embedded in the implementation. The identities are fixed in `adapter.py`; there
is no command-line option to add artifacts or reinterpret a different contract.
The tool does not scan directories, retrieve URLs or open native stores.

Without `--output`, one complete JSON result goes to stdout. With `--output`, the
complete result goes to a new file with private permissions; stdout stays empty.
Exit 0 means linked, 1 means rejected, and 2 means an operational failure with
error-only JSON on stderr. An unreadable input uses `IO_FAILURE` at `["input"]`.
Existing output paths, including dangling symlinks, are never replaced. A fully
written, flushed temporary file is published with an atomic no-replace hard link.
If the filesystem cannot provide that operation, publication fails closed.

The normative `spec/contract.txt` and schema are exact copies of the approved v2
packet. Their provenance is recorded in `provenance.json`. The frozen packet and
original captures remain outside Git and are not included in static deployments.

## Verification

Run the synthetic unit and publication tests:

```sh
python3 -m unittest discover -s experiments/capture_review_adapter/tests -t . -v
```

The frozen fixture test is skipped unless the explicit local packet is supplied:

```sh
AFG_CAPTURE_REVIEW_PACKET=/absolute/path/to/capture-semantic-bridge-v2 \
  python3 -m unittest discover -s experiments/capture_review_adapter/tests -t . -v
```

That opt-in test checks the pinned manifest first, runs all 19 complete authored
inputs through the CLI, compares whole expected results, exit codes and output
channels, then rehashes the approved packet and original inputs. Synthetic tests
patch the internal artifact map only inside their test process. The CLI never
accepts those test identities.

This module has no application, provider, key, usage, native corpus or synthetic
auditor imports. It does not change runtime answers, spending limits, previews or
deployment. Real-source authentication, semantic judgments, context acquisition,
question completeness and public activation remain unresolved in every result.
