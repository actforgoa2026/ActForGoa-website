# Hosted recorded-imagery preview — 28 October 2026

The user explicitly requested a live iterative version and a local deployment handoff. Source `18112a26ad278677bb5cbb2716758ad0fd532b62` is now published as **a read-only recorded comparison**, using the authentic verified October 10/20 Goa imagery and numeric measurements. It is not the hosted new-area/date comparison service and does not run OpenAI decisions.

Deployment: `dpl_4b7qNRdy2VsQEhXLig7bBF2sgEhP`, existing Vercel project `prj_4BRx1f4MrLFE5p6Ljnhkp33TOltz`. [Deployment URL](https://actforgoa-field-guide-jmd8zml88-zakkrevitt-gmailcoms-projects.vercel.app) requires Vercel authentication by default. The user received a deployment-scoped seven-day share link, expiring **4 November 2026, 12:25:26 UTC**. Its access token is intentionally excluded from Git.

Anonymous access through the scoped share link passed in fresh desktop/390px/320px browser contexts. Both real images decode; slider keyboard interaction, paired view, topic evidence, uncertainty labels and source anchors work. No page errors or horizontal overflow. See [live-browser.json](live-browser.json) and the screenshots. The preview build contains only 10 static HTML/JS/CSS/font/image files plus deployment-specific `vercel.json`; [deployment.json](deployment.json) records their hashes. No source archives, raw rasters, credentials, API routes or private user results were uploaded.

The main production deployment remains `dpl_FzbANqhz96u2JNt2eb6fK4BDtS7c`. Project-wide build and protection settings remain unchanged. No production promotion occurred. The preview uses per-deployment static configuration; it does not weaken the main release's research acceptance requirements.

Retained failures: new project creation returned 403 `forbidden`; the first existing-project request used an unsupported explicit `preview` target and returned 400 `bad_request`. Correcting it to omit target (the documented preview default), and putting build overrides in the deployment's `vercel.json`, succeeded. These are deployment checks, not new paid imagery/model calls.

For the complete hosted query dashboard, follow [the local deployment handoff](../../docs/SATELLITE-LOCAL-DEPLOYMENT.md). OpenAI is optional for its first live imagery version. This cloud executor cannot edit the Railway secret-host binding or export real CDSE secrets into hosting.
