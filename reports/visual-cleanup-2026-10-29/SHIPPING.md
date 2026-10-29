# Shipping status

PR #105 merged at `21e4dcac46b4299d586b79e229ff4faa3dc46fc4` after the user explicitly requested shipping. Subsequent main `f20fc25` changes satellite documentation only.

The guarded release preflight fails at `vercel inspect`: Vercel CLI 65.7.0 reports `User not found` from `/v2/user`. The configured injected credential can read this project's REST metadata but does not complete CLI principal authentication. Normal auth-config storage was tested with the same credential to avoid lexical rejection of the proxy marker. Explicit verified team configuration also fails. No replacement credentials, modified CLI code, direct deployment fallback or release-guard bypass was used.

No deployment/promotion occurred. Existing alias remains `dpl_LWEsW2jqaauxfyhbHF5ZNGYCuykD`. The original domain, satellite services and backend are unchanged by this chat.

The 211 passing tests, build and feature screenshots remain applicable. Expanded local production-preview checks cover required desktop/phone routes using read-only public API responses. A historical document URL was unavailable; a current document located via live library search opens successfully on both widths. No paid inference or private writes. Exact-tree preflight evidence/logs are retained under ignored `.reports/visual-cleanup-release/` in the isolated cloud checkout.

Release coordinator: restore supported Vercel CLI access, fetch latest main, refresh evidence and use `npm run release:review`. Preserve source/alias checks and verify the hosted result before declaring completion.
