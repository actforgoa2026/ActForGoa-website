# ActForGoa MCP

The read-only Streamable HTTP endpoint is `/api/mcp`. Connect a compatible MCP client using the full review-site URL shown on `/mcp`. No API key or npm package is needed for clients that support remote MCP. The server exposes `search_site`, `search_directory`, and `search_research`; it does not call the generated-answer endpoint.

The site and directory tools read the published catalogue each time. The research tool queries the current published research service, so newly published indexed generations appear without updating MCP code. Adding content to an unpublished checkout or an unindexed source does not publish it. Practical guide records ship with the website deployment. Private incident reports, CRM notes stored in users' browsers, credentials and usage data are outside the tools' scope.

Search results are evidence, not independently verified advice. Contact delivery, legal currency, locality and extraction quality require checking. The MCP client may send the query and returned data to its model provider. Research search is subject to the existing service's capacity and rate limits. No client account or usage authentication is implemented.

For deployment, verify the Vercel function is included, `/api/mcp` handles initialization and tools calls, and the frontend and source APIs are reachable. Run integration checks against a preview before promoting it. A website deployment and a research-index generation are distinct releases.
