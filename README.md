# Docsy Plugin

Open-source plugin for current, source-linked developer documentation in
**Claude, OpenAI/ChatGPT/Codex and Cursor**. It connects to the hosted
read-only Streamable HTTP MCP endpoint:

    https://docsy.remcp.site/mcp

The five public tools are resolve-library-id, query-docs,
list-library-versions, search and fetch. Anonymous public lookups do not
require a Docsy API key. Only public indexed documentation is accessible.

## Install

- **Claude Code**: import this repository as a plugin, or add the public
  remote MCP server URL above. Root .claude-plugin/plugin.json and .mcp.json
  are included for Claude Code compatibility.
- **Cursor**: use the Agent Plugins 1.0.0 package from this repository or
  add the remote server in Cursor MCP settings. mcp.json contains the same
  remote endpoint.
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
    python3 scripts/publishing/package.py --output /tmp/docsy-plugin-v1.0.1.zip

For remote MCP and public legal-page smoke tests, run:

    node scripts/publishing/mcp-review-smoke.mjs

Directory publication requires identity verification, platform review and approval.
