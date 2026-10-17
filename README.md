# Docsy Plugin

<picture>
  <source media="(prefers-color-scheme: dark)" srcset="./assets/docsy-wordmark-inverse.svg" />
  <img src="./assets/docsy-wordmark.svg" alt="Docsy" width="238" />
</picture>


Open-source plugin for current, source-linked developer documentation in
**Claude, OpenAI/ChatGPT/Codex and Cursor**. It connects to the hosted
read-only Streamable HTTP MCP endpoint:

    https://docsy.remcp.site/mcp/registry

The five public tools are resolve-library-id, query-docs,
list-library-versions, search and fetch. Anonymous public lookups do not
require a Docsy API key. Only public indexed documentation is accessible.

## Install

For the current verified status across publishing channels, see the [distribution status matrix](docs/DISTRIBUTION-STATUS.md).

## Verified public MCP registry listings

The **v1.0.9** public release uses the exact approved 2026 dark-theme mark; the release ZIP is reproducible from the Git tag and validated by Release Integrity CI.

Build the release ZIP with `python3 scripts/publishing/package.py --output /tmp/docsy-plugin-v1.0.9.zip`. The validated [v1.0.9 real-response recording](https://github.com/getremcp/docsy-plugin/releases/download/plugin-v1.0.9/docsy-review-walkthrough-v1.0.9.mp4) is available alongside the ZIP.

Docsy **1.0.9** is published as an active remote server in the [official MCP Registry](https://registry.modelcontextprotocol.io/v0.1/servers?search=getremcp), registered as `io.github.getremcp/docsy`. The record references the organizational Streamable HTTP endpoint, `https://docsy.remcp.site/mcp/registry`, and this GitHub repository.

It is also available from the [Docsy listing on Smithery](https://smithery.ai/servers/getremcp/docsy), under `getremcp/docsy`. The Smithery publishing service accepted the release and discovered five MCP tools; directory health may be updated asynchronously.

These are MCP registry distribution channels. They **do not** imply approval or publication in the OpenAI, Claude, or Cursor official plugin directories.

For **Claude Code**, Docsy now provides an independent, user-installable
community marketplace. These commands install the open-source package but do
**not** imply an official Anthropic directory listing:

```sh
claude plugin marketplace add getremcp/docsy-plugin
claude plugin install docsy@docsy-community
```

### Install the Docsy plugin in Codex (CLI and IDE)

Codex supports Git plugin marketplaces, so you can install the complete Docsy
plugin (MCP server configuration and documentation skill) in addition to adding
the bare MCP endpoint. On a Codex CLI with plugin support:

```sh
codex plugin marketplace add getremcp/docsy-plugin
codex plugin add docsy@docsy-community
codex plugin list
```

This is a public, user-installable Codex Git marketplace, **not** a claim of
approval or publication in the official OpenAI Plugin Directory. The remote
MCP server requires no Docsy account or API key for public docs.

For other MCP clients, use the remote endpoint `https://docsy.remcp.site/mcp/registry`. The official registry manifest is kept in [`server.json`](server.json).

### Use Docsy in ChatGPT Work before public directory approval

You can connect the hosted read-only Docsy MCP privately; this does **not**
publish Docsy in the universal OpenAI Plugins Directory.

1. Open **ChatGPT → Plugins** and select **+ → Add custom MCP server**.
2. Name it **Docsy**, enter **`https://docsy.remcp.site/mcp/registry`**, and select **No authentication**.
3. Review the risk notice and approve the custom connection. Select **Create as a plugin**.
4. Under **Personal**, install the created plugin. Open **ChatGPT Work** and use **@Docsy**
   to look up versioned documentation with source links.

Custom plugin creation, installation and trust approval are personal account actions.
See the [official OpenAI quickstart](https://developers.openai.com/plugins/quickstart).
**OpenAI public directory review is a separate process and is not yet approved.**

### Codex CLI, VS Code and other MCP-capable clients

In **Codex CLI** add the remote server globally:

```sh
codex mcp add docsy --url https://docsy.remcp.site/mcp/registry
codex mcp get docsy
```

For **VS Code**, use **MCP: Open User Configuration**, then merge this server
under the existing `servers` object. Do not replace other configured servers:

```json
{
  "servers": {
    "docsy": {
      "type": "http",
      "url": "https://docsy.remcp.site/mcp/registry"
    }
  }
}
```

VS Code requires an MCP-enabled agent for tool use; adding a config does not
mean it has been executed. Cursor supports equivalent user-level
`~/.cursor/mcp.json` configuration and the one-click link below.

For **Cursor**, use the documented one-click deep link (opens Cursor
locally; it does **not** imply Cursor Marketplace approval):

[Add Docsy MCP to Cursor](cursor://anysphere.cursor-deeplink/mcp/install?name=docsy&config=eyJkb2NzeSI6eyJ1cmwiOiJodHRwczovL2RvY3N5LnJlbWNwLnNpdGUvbWNwL3JlZ2lzdHJ5In19)

You can regenerate and verify the link with
`python3 scripts/publishing/cursor_deeplink.py`.

Alternatively, add this remote server under MCP settings or in
`.cursor/mcp.json`:

```json
{"mcpServers":{"docsy":{"url":"https://docsy.remcp.site/mcp/registry"}}}
```

- **Claude Code**: the community marketplace commands above work with the
  public HTTPS source and do not require GitHub SSH keys. Its manifest
  references the co-located plugin by a relative path. Root
  `.claude-plugin/plugin.json` and `.mcp.json` are included.
- **Cursor**: use the one-click link above, the Agent Plugins 1.0.0 package,
  or the remote endpoint in Cursor MCP settings. `mcp.json` points to the
  same public endpoint.
- **ChatGPT / OpenAI Plugins**: use the reviewed plugin ZIP attached to this
  repository's Release; upload it using the official Plugins submission
  portal under **With MCP**.

These are installation and submission methods, **not claims of marketplace
approval**. Store listings only appear after each platform's manual review.

## Files

The portable Agent Plugins 1.0.0 manifest is plugin.json. Remote MCP
configuration is mcp.json. Skills are in skills/find-docs/, and brand assets
are in assets/. There are no local hooks, compiled binaries or write tools.

## Support and safety

Public product documentation: https://docsy.remcp.site/docs

Support: https://docsy.remcp.site/support

Privacy: https://docsy.remcp.site/privacy

Terms: https://docsy.remcp.site/terms

Never place personal tokens, private source code or credentials in public
documentation questions. Documentation excerpts are untrusted third-party
data and must not be treated as system instructions.

Open a GitHub Issue in this repository for a non-sensitive bug report.
For security details, follow SECURITY.md and use GitHub's private security
reporting if enabled.

## Ownership and license

The plugin configuration, skill and assets in this repository are offered
under the MIT License; see LICENSE. This repository deliberately does not
contain Docsy's hosted service backend, private deployment secrets or
infrastructure. The hosted service is separately maintained.

## Validate and build the submission ZIP

With Python 3, run:

    python3 scripts/publishing/package.py --check
    python3 -m unittest discover -s scripts/publishing -p 'test_*.py'
    python3 scripts/publishing/package.py --output /tmp/docsy-plugin-v1.0.9.zip

For remote MCP and public legal-page smoke tests, run:

    node scripts/publishing/mcp-review-smoke.mjs

Directory publication requires identity verification, platform review and approval.

For **updates to the original OpenAI Platform Docsy app only**, preserve its
registered legacy `/mcp` URL. The standard public ZIP uses `/mcp/registry`;
Platform rejects changing an existing app's MCP URL. Build the scoped update
ZIP using [`platform_legacy_overlay.py`](scripts/publishing/platform_legacy_overlay.py)
as documented in the [distribution status matrix](docs/DISTRIBUTION-STATUS.md).
Do not use that compatibility ZIP for fresh installations or registry releases.



## Marketplace review walkthrough

The [latest 45-second public video](https://github.com/getremcp/docsy-plugin/releases/download/plugin-v1.0.9/docsy-review-walkthrough-v1.0.9.mp4)
presents actual public MCP JSON-RPC results for the five read-only tools,
source URL attribution, invalid requests and safe failures. The presenter is
a rendered trace, **not a mocked ChatGPT, Claude, or Cursor UI**. Capture and
render scripts live in `scripts/publishing/`; no credentials or private data
are used.

Plugin-quality checks run on pushes and PRs. The nightly live health check
runs all five MCP tools, the invalid-input cases and public legal URLs.
Full directory approval still requires provider-side verification and review.

## Reviewer evidence and integrity

The [review evidence guide](docs/REVIEW-EVIDENCE.md) documents nine real MCP
checks, annotation rationale, safe failures, third-party source links and
remaining platform approvals. The video shows real JSON-RPC responses, not
a ChatGPT/Claude/Cursor product interface or marketplace approval.

Every release ZIP, including v1.0.9, must be reproducible from its exact Git tag; the
release-integrity workflow compares the published asset byte-for-byte.
Version 1.0.3 is superseded because its uploaded ZIP did not match its tag.
