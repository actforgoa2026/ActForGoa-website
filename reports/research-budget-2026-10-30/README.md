# October AI budget increase

The user explicitly approved **$100 total for October** on 30 October 2026 after the public answer service reported `monthly_limit`. The previous allowance was $50. Only the dated research allowance changed: $100 applies October 30–31 UTC, the 500 model-attempt daily limit remains, and November returns automatically to 100/day and $5/month. Reservations include earlier usage and failures; these conservative amounts are not the provider's final bill.

## Live result

- Source: `4aeed676c73cbc910f784af24d682d15eb3a924e`; [PR #147](https://github.com/actforgoa2026/ActForGoa-website/pull/147).
- Existing Railway research service: `f3c5348d-3bfe-47b0-98a4-22428580937f` in project `512430bc-234d-4582-b4dd-47770e3c9114`.
- Deployment: `98e770fd-b085-4dcb-ba2f-3964bb8f0aca`, verified successful. Rollback: `96bfcdbe-22e5-4ab9-9f16-3986ad1ac2f7`.
- Public `/api/status` changed from `chat_ready:false`, `monthly_limit` to `chat_ready:true`, no unavailable reason. Source search remained ready.
- A fresh browser question about SAPCC waste segregation and village collection completed with seven source links. It used five metered model attempts and $1.978604 in conservative reservations; no automatic retry or second test conversation ran.

## Preservation and validation

The production SQLite ledger was backed up on its existing volume before deployment. Every row was hash-identical immediately after deployment and starter-cache revalidation, with October reservations unchanged at $49.752368 and today's attempt count unchanged at 68. After the one live verification question, totals were $51.730972 reserved and 73 attempts. Earlier usage, imports and reservations remain present.

Generation `20261030-sapcc-native-v2` and its source database SHA-256 `be9d0b81256a65b9258366415178f549ddfa7c362e601fa67e69fc0b318d8fba` are unchanged. Packaged/live backend comparison confirms `hosting.py` is the only changed Python runtime file. The three reviewed starter answers were revalidated against the same original citations after the budget-only runtime fingerprint changed; their exact answer hashes, review timestamps and original expiry remain intact. No provider requests were used for cache preservation.

Validation passed: 80 focused budget, hosting, stage-reservation and reconciliation tests; all 283 Node tests; full production build including the landing bundle. The first build attempt used older shared dependencies and could not resolve the newly added landing libraries; a clean `npm ci` and complete build passed. No frontend, satellite, corpus, provider-credential or default environment-variable change was made. The original WordPress site is unchanged.

Private snapshots, package manifest, deployment metadata, cache-validation record and build logs are under ignored `.reports/budget-october/`. Browser captures are in the original task workspace at `reports/buildathon-screenshots-2026-10-30/`. Temporary SSH access was used only for ledger backup and preservation verification and is revoked after completion.
