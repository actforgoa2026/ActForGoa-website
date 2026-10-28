# Paired image decisions and interpretation — 28 October 2026

This continuation makes the selected-area comparison explain its evidence. OpenAI Decisions is the default image assessor. The two presence questions return `yes`, `no` or `uncertain` for resolvable canopy in the same common-clear footprint on the two actual acquisition dates. The result does not track the identity of a single tree.

| Before / after | Interpretation |
| --- | --- |
| Yes / no | Possible canopy disappearance; cause and individual-tree identity remain unknown |
| No / yes | Possible appearance; growth, seasonality and visibility need review |
| Yes / yes | Canopy visible both times; partial loss is still possible |
| No / no | Canopy not identified; not proof that no trees existed |
| Either uncertain | No reliable presence-to-absence inference |

Server-generated wording reconciles these decisions with numeric candidates, clear coverage and the requested period. Contradictory checks stay explicit. Every statement links to the images, visibility, numeric evidence or image decisions. Model-generated prose, geometry, tree counts and exact event dates are not accepted. The dashboard shows the presence decisions before the explanation and keeps secondary assessments expandable.

Anthropic remains the question planner. An optional Anthropic image adapter is available only through explicit service configuration (`SATELLITE_CLASSIFIER=anthropic`, or opt-in `auto`); the default does not silently substitute it for missing OpenAI credentials or retry failed Decisions calls on another provider. Classification attempts are reserved persistently, including failures; failures retain the imagery evidence. Reported input/output token usage is retained without presenting model confidence as field accuracy.

Checks: **50 Python satellite tests**, **181 Node tests**, production build, and three Chromium flows at 1440, 390 and 320 px pass. The browser flows use real local named-account authentication and the actual admin proxy/Python service with synthetic provider responses. They verify yes/no display, interpretation and timing caveats, evidence links, decoded images, result clearing, upright text and no overflow/page errors. See [browser.json](browser.json) and the explicitly labelled screenshots. The installed Impeccable skill is unavailable; existing design guidance and rendered inspection were used.

**No live OpenAI inference has run.** The OpenAI credential setup remains incomplete. These are contract and UI checks, not field-accuracy evidence. Earlier real CDSE retrieval evidence remains in [the live imagery report](../satellite-live-2026-10-28/README.md). No new CDSE calls, model calls or deployment were made for this checkpoint.
