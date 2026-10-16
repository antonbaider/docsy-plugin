# Docsy distribution status

Last technical verification: 16 October 2026. **Listings, submissions, private installations, and official approvals are different states.** See the linked primary evidence; catalogue operators control review timing.

| Channel | Status | Evidence |
| --- | --- | --- |
| GitHub organization | **Published** | [getremcp/docsy-plugin](https://github.com/getremcp/docsy-plugin) |
| GitHub Plugin v1.0.7 | **Published** | [Release ZIP and demonstration](https://github.com/getremcp/docsy-plugin/releases/tag/plugin-v1.0.7) |
| Official MCP Registry | **Active, latest v1.0.7 (verified via Registry API)** | [Registry query](https://registry.modelcontextprotocol.io/v0.1/servers?search=getremcp) / [OIDC publish run](https://github.com/getremcp/docsy-plugin/actions/runs/38953737055) |
| Smithery | **Public listing** | [getremcp/docsy](https://smithery.ai/servers/getremcp/docsy) |
| Awesome Remote MCP Servers | **Listed** | [Developer Tools](https://github.com/punkpeye/awesome-remote-mcp-servers#developer-tools) |
| Glama | **Connector referenced** | [Organization connector](https://glama.ai/mcp/connectors/io.github.getremcp/docsy) / [badge](https://glama.ai/mcp/connectors/io.github.getremcp/docsy/badges/score.svg) |
| Claude Code GitHub marketplace | **Installable**, last checked on ASUS | [Installation](../README.md) |
| Codex Git marketplace | **Installable v1.0.7**, verified on ASUS and MacBook | [Installation](../README.md) |
| OpenModels MCP directory | **Submitted; awaiting maintainers** | [PR #55](https://github.com/openmodelsrun/mcp/pull/55) |
| Cline Marketplace | **Submitted; awaiting maintainers** | [PR #244](https://github.com/cline/marketplace/pull/244) |
| MCP.Directory | **Submitted; awaiting review** | [Submission portal](https://mcp.directory/submit), accepted in public UI on 2026-10-16; not yet a published listing |
| mcp.tc | **Queued for human review** | [Docsy submission status](https://mcp.tc/s/dc7OMIJio-fn2yHv); endpoint detected, no public listing yet |
| mcpub | **Registered; discoverable in public search** | [mcpub](https://mcpub.dev/): verified public MCP tools `submit`, `get` and `search` on 2026-10-16; Docsy registered under `https://docsy.remcp.site` |
| OpenAI Plugin Directory | **In review: v1.0.7** | Submitted on 2026-10-16 in the verified individual publisher account; **not approved or published**. Review status is visible only in the signed-in OpenAI Platform dashboard. |
| Official Claude Directory | **Not confirmed submitted** | Separate authenticated publisher review required |
| Cursor Marketplace | **Not confirmed submitted** | [Submission form](https://cursor.com/marketplace/publish) requires publisher login/review |
| npm `@docsy/sdk` and `@docsy/cli` | **Not published** | npm scope-owner login / Trusted Publisher must be configured; do not claim npm distribution |

## Stable public MCP endpoint

`https://docsy.remcp.site/mcp/registry` is the canonical endpoint for new installs. The original `https://docsy.remcp.site/mcp` remains available for existing clients. Both passed protocol `initialize`, `tools/list`, library resolution, and source-linked `query-docs` checks on 15 October 2026.

The GitHub repository contains the MIT-licensed plugin manifests and integration material. The operational crawler, database index and API backend are a **managed hosted service**, not distributed as an open-source self-hosted implementation in this repository.

The plugin package version is **v1.0.7**; do not confuse it with the version string advertised by the hosted backend's MCP `serverInfo`, which may differ.

### Original OpenAI Platform application

The existing Docsy Platform app was created with `https://docsy.remcp.site/mcp`,
which remains healthy and domain-verified. Platform refuses an update that
changes its registered MCP URL (`MCP URL must match the existing app`). Its
v1.0.7 review submission therefore retains that original alias **only in the
Platform update ZIP**. This does not change the canonical endpoint used by
the official MCP Registry, new users, Codex or the Git marketplace.

To reproduce the submission-specific ZIP from the standard public release ZIP:

```sh
python3 scripts/publishing/package.py --output /tmp/docsy-plugin-v1.0.7.zip
python3 scripts/publishing/platform_legacy_overlay.py \
  --input /tmp/docsy-plugin-v1.0.7.zip \
  --output /tmp/docsy-plugin-v1.0.7-openai-existing-app.zip
```

The helper checks the original release contents and changes exactly one
`mcp.json` URL. Never upload this compatibility variant for a **new** app;
new OpenAI submissions should use the canonical `/mcp/registry` URL.

For personal ChatGPT use, creating and approving a custom MCP connection is an account-level action. It is **not** automatic just because Docsy appears in the official MCP Registry.

## Discovery metadata

The public plugin repository is tagged with MCP, remote MCP, developer documentation, Claude Code and Cursor topics and points to the live service homepage. A domain-level discovery manifest has been merged in [core PR #158](https://github.com/antonbaider/docsy/pull/158), live and verified via HTTPS on 2026-10-16.
