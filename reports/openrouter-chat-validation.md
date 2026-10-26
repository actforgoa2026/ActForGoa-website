# OpenRouter research chat validation

Date: 2026-10-26. Base: origin/main 3858a45754bd467c4fdc23598b2f4e9a3c30a782.

Status: the funded OpenRouter credential works. Production remains unchanged. Qwen 3.7 failed live quality review (three rejected structures in 50 cases, plus claim concerns); GPT-5 Nano passed targeted structure, geographic-scope and brief-answer comparisons and is undergoing the final acceptance run. `/api/status.chat_ready` indicates a configured credential, not a proven working provider.

## Scope

GPT-5 Nano through OpenRouter, explicit alternative providers, conservative persistent monthly model budget, bounded prompts/output, strict citation identity validation, ten-minute first-question response reuse, provider disclosure, and Ask as the initial research mode. Existing Arc components, typography, palette and source reader remain in use. Source ingestion/index contents are unchanged.

## Verification

- 46 research tests passed, including actual local MiniLM/Zvec retrieval, document originals/checksums, OpenRouter SDK contract, provider errors, rejection of invented citations, prompt size bounds, persistent/concurrent cost reservations, UTC month rollover, cache expiry/isolation and service-only packaging. Provider responses in these tests are simulated; this is not live inference evidence.
- All 104 frontend tests passed. Production TypeScript/Vite build passed.
- Browser checks against the actual 1,156-document corpus at local API port 8093 / web port 4176: Ask initially selected, starter uses selected mode, unavailable model shows a clear error with real source results, source opens at PDF page 698 with a highlighted passage, Original page image loads, and Back to your research retains the question/results.
- Inspected desktop 1440 × 1000 and phone 390 × 844. No horizontal page overflow; phone research and source-reader checks showed zero italic/oblique UI elements. Source inspection and rendered research check found no decorative side stripes. Original document imagery is preserved unchanged.
- Impeccable source detector ran on Research.tsx and research.css with no reported findings; its regex-only output does not establish contrast or complete accessibility. Rendered review performed separately. Local captures: `.impeccable/review/openrouter/desktop.png` and `phone.png` (ignored, not deployed).
- `package_research.py --service-only` succeeded without repackaging the corpus. Existing volume and usage database must be retained.

## Release dependencies

1. The secure `OPENROUTER_API_KEY` setup is complete on the Railway research service. The key has not been printed or written into Git.
2. Run the local backend with the real corpus and credential. Execute `scripts/evaluate_live_chat.py` (50 Goa questions; billable) and review the resulting claims against evidence. Mechanical citation identity is not proof of entailment. Fix and retest any failures before enabling public answers.
3. Deploy code only to the dedicated research service, preserving `/data/research` and `.research-usage`. Verify provider status, live questions, citations, originals and exhausted-budget fallback.
4. The ORCHESTRATOR chat owns combined frontend deployment. Merge/publish through the coordinated release path after live verification. No change to actforgoa.org or the reporting service.

Default monthly cap is $5 of conservatively reserved inference, with 100 new paid attempts per UTC day. The cap excludes credit-purchase fees, tax, infrastructure and other account usage. Use a dedicated OpenRouter key limit too. Requests fail when the reviewed price or routing constraints cannot be met; they do not silently select another provider or model.
