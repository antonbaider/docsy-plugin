# Docsy distribution status

Last technical verification: 15 October 2026. **Listings, submissions, private installations, and official approvals are different states.** See the linked primary evidence; catalogue operators control review timing.

| Channel | Status | Evidence |
| --- | --- | --- |
| GitHub organization | **Published** | [getremcp/docsy-plugin](https://github.com/getremcp/docsy-plugin) |
| GitHub Plugin v1.0.6 | **Published** | [Release ZIP and demonstration](https://github.com/getremcp/docsy-plugin/releases/tag/plugin-v1.0.6) |
| Official MCP Registry | **Active, latest v1.0.6** | [Registry query](https://registry.modelcontextprotocol.io/v0.1/servers?search=getremcp) / [OIDC publish run](https://github.com/getremcp/docsy-plugin/actions/runs/38615388001) |
| Smithery | **Public listing** | [getremcp/docsy](https://smithery.ai/servers/getremcp/docsy) |
| Awesome Remote MCP Servers | **Listed** | [Developer Tools](https://github.com/punkpeye/awesome-remote-mcp-servers#developer-tools) |
| Glama | **Connector referenced** | [Organization connector](https://glama.ai/mcp/connectors/io.github.getremcp/docsy) / [badge](https://glama.ai/mcp/connectors/io.github.getremcp/docsy/badges/score.svg) |
| Claude Code GitHub marketplace | **Installable**, last checked on ASUS | [Installation](../README.md) |
| OpenModels MCP directory | **Submitted; awaiting maintainers** | [PR #55](https://github.com/openmodelsrun/mcp/pull/55) |
| Cline Marketplace | **Submitted; awaiting maintainers** | [PR #244](https://github.com/cline/marketplace/pull/244) |
| OpenAI Plugin Directory | **Not confirmed submitted** | Publisher must attest to legal declarations in the correct OpenAI Platform account; technical ZIP alone is not an approval |
| Official Claude Directory | **Not confirmed submitted** | Separate authenticated publisher review required |
| Cursor Marketplace | **Not confirmed submitted** | [Submission form](https://cursor.com/marketplace/publish) requires publisher login/review |
| npm `@docsy/sdk` and `@docsy/cli` | **Not published** | npm scope-owner login / Trusted Publisher must be configured; do not claim npm distribution |

## Stable public MCP endpoint

`https://docsy.remcp.site/mcp/registry` is the canonical endpoint for new installs. The original `https://docsy.remcp.site/mcp` remains available for existing clients. Both passed protocol `initialize`, `tools/list`, library resolution, and source-linked `query-docs` checks on 15 October 2026.

The GitHub repository contains the MIT-licensed plugin manifests and integration material. The operational crawler, database index and API backend are a **managed hosted service**, not distributed as an open-source self-hosted implementation in this repository.

The plugin package version is **v1.0.6**; do not confuse it with the version string advertised by the hosted backend's MCP `serverInfo`, which may differ.

For personal ChatGPT use, creating and approving a custom MCP connection is an account-level action. It is **not** automatic just because Docsy appears in the official MCP Registry.
