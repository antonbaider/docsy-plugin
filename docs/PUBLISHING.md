# Publishing Docsy to Claude, ChatGPT/OpenAI and Cursor

Docsy exposes one **public, read-only remote MCP** endpoint:

    https://docsy.remcp.site/mcp

Tools: `resolve-library-id`, `query-docs`, `list-library-versions`, `search`, `fetch`. The endpoint uses Streamable HTTP, supports anonymous public lookups with rate limits, and does not require an API key. Never claim that anonymous retrieval provides access to private repositories or user account data.

## Shared source-of-truth

- `plugin.json`: portable Agent Plugins manifest and OpenAI-specific directory metadata under `extensions.com.openai`.
- `mcp.json`: portable remote Streamable HTTP server entry.
- `skills/find-docs/SKILL.md`: bounded documentation lookup instructions.
- `assets/`: owned Docsy icons (no platform trademarks).
- `.claude-plugin/plugin.json` and `.mcp.json`: Claude plugin and remote HTTP compatibility.
- `scripts/publishing/package.py`: deterministic, allowlisted OpenAI review ZIP with six files only.

Validate and build the release:

    python3 scripts/publishing/package.py --check
    python3 scripts/publishing/package.py --output /tmp/docsy-plugin-v1.0.5.zip

Never include API keys, Firebase service secrets, database URLs, or credential files inside a public plugin ZIP. The package builder uses an explicit file allowlist rather than zipping the entire monorepo.

## Test before every review

Execute the actual publicly deployed tools, including success/failure cases:

    node scripts/publishing/mcp-review-smoke.mjs

This requires deployed and reachable `/privacy`, `/terms` and `/support` pages. For pre-deploy development only, use `--skip-public-pages`. The test must not be skipped when preparing a real directory submission. Also run the regular repository CI and production smoke. Confirm that all five tools have correct, truthful read-only annotations and no credentials are sent. Source-linked excerpts should be checked against their original documentation.

## OpenAI / ChatGPT / Codex directory

Official references:
- https://developers.openai.com/plugins/build/plugins
- https://developers.openai.com/plugins/deploy/submission
- https://developers.openai.com/plugins/deploy/app-review

1. Verify your publisher identity in the OpenAI Platform organization. The verified individual/business name must match the directory publisher. The placeholder contributor attribution in the manifest must be corrected to the verified identity if needed.
2. Ensure account/project can submit remote MCP plugins and has `api.apps.write`. Projects in EU-only data residency cannot currently submit MCP plugins; use an eligible project.
3. Upload the verified ZIP from above in the Plugins submission portal using **With MCP**. Connect `https://docsy.remcp.site/mcp` as the universal HTTPS endpoint. Complete the platform's domain challenge. No OAuth is needed for the anonymous public read-only tool set; do not pretend Docsy implements OAuth.
4. Run **Scan Tools**. Review the live name, descriptions, input schema, annotations, identity and security schemes of all five tools. Provide the four legal/support website URLs, owned logos, and accurate publisher information.
5. Confirm the five positive and three negative cases embedded in `plugin.json`. Collect real expected results from the smoke test (no forged outputs). Produce an **actual reviewer-accessible demo recording** showing tools working; do not fabricate a video URL or reviewer credentials.
6. Submit for review and act on feedback. Publish only after approval. Plugin ZIP uploads, verification and directory publishing require the publisher's account permissions.

## Anthropic Claude directory

Official source: https://claude.com/resources/articles/build-plugins-for-claude

Anthropic's plugin directory accepts a remote **single MCP connector** or a **GitHub plugin bundle**. Using a paid Claude plan, open the developer submission portal from the Claude directory.

- For the straightforward MCP-only submission, supply `https://docsy.remcp.site/mcp`. Provide real publisher contacts, product description, source links, privacy/terms/support URLs, and a working review demo.
- For bundled installation, use the publicly accessible Docsy plugin repository; manifests are stored in `.claude-plugin/plugin.json` / `.mcp.json` and the documentation skill is in `skills/find-docs/`. Validate the plugin's exact root and repository URL in the portal before submission.
- Claude may audit security and compatibility and does not guarantee inclusion. Review status and analytics appear after submission/approval, where eligible.

## Cursor Marketplace

Official references:
- https://prod.cursor.com/docs/plugins
- https://cursor.com/marketplace/publish

Cursor accepts **Agent Plugins** (root `plugin.json` + `mcp.json` + skills) and standalone remote MCP servers. The repository is open source under MIT; no hooks or local executable commands are bundled.

To connect without marketplace listing, configure Cursor with:

    {"mcpServers":{"docsy":{"url":"https://docsy.remcp.site/mcp"}}}

For public listing, submit the public GitHub source through Cursor Marketplace's publisher form. Cursor manually reviews submissions. Provide publisher identity, legal URLs, usage examples and the real GitHub URL. Only claim official marketplace availability once approved and indexed.

## Outstanding externally controlled items

These cannot be asserted or completed by editing source code alone:

- OpenAI organization/publisher identity verification and `api.apps.write` access.
- OAuth/domain or connection challenge that a dashboard presents during review.
- Reviewer-accessible video and secure test credentials if requested. Docsy public lookup needs none.
- Claude paid-developer portal access and submission approval.
- Cursor publisher application, identity verification and manual approval.

**Never add Claude, OpenAI or Cursor badges implying marketplace approval before an actual listing is published.** Retain a dated release ZIP and Git commit hash for any submission. When tools, privacy policy or package metadata change, follow each platform's rescan or new-version review requirements.

## Review walkthrough

The release includes a 45-second publicly accessible MCP demonstration video,
recorded from real live responses and rendered without impersonating any
provider's interface. A reviewer can view it at the
`review.demo_recording_url` in `plugin.json`. The test capture script
retrieves only public source citations, result counts, tool status and errors;
private documents, API keys and account data are deliberately excluded.
Provider reviewers may still request an additional in-product recording.


## Official MCP Registry (remote server)

`server.json` is a dedicated manifest for the official MCP Registry in the GitHub-owned namespace `io.github.getremcp/docsy`. The only transport is the publicly reachable Streamable HTTP endpoint, `https://docsy.remcp.site/mcp`; no unpublished npm package is listed.

Run **Publish Docsy MCP Registry** from GitHub Actions on `main` to validate and publish with GitHub-hosted OIDC. The publisher CLI v1.8.1 is downloaded from the official registry release and verified by pinned SHA-256. No personal access token or long-lived secret is used. Publication must be confirmed from the workflow result and registry response; a prepared manifest alone is not a listing.

## Verified listings, 2026-10-14

The official MCP Registry confirmed `io.github.getremcp/docsy` version `1.0.5` with status `active`. GitHub OIDC publication completed in [workflow #38594454932](https://github.com/getremcp/docsy-plugin/actions/runs/38594454932), using the public Streamable HTTP endpoint. Registry API: https://registry.modelcontextprotocol.io/v0.1/servers?search=docsy .

Smithery accepted the `antonbaider/docsy` external remote at https://smithery.ai/servers/antonbaider/docsy . The initial deployment ID was `4909e9c3-301e-435f-90dc-4e8a89529bd9`; this is not an OpenAI, Claude or Cursor plugin-directory approval.

The OpenAI draft is `v1.0.5` with domain/MCP verified; **submission is still pending the individual publisher's own six legal declarations**. The private backend's npm SDK/CLI have not been published because `@docsy` scope ownership and npm authentication are not available.


## Organization registry endpoint migration

The GitHub repository moved to `getremcp/docsy-plugin` on 2026-10-14. The original official MCP Registry entry `io.github.antonbaider/docsy` already claimed `https://docsy.remcp.site/mcp`, and the official Registry enforces one server name per remote URL. To preserve all previously installed clients, the edge now hosts the separately tested, stable organizational route `https://docsy.remcp.site/mcp/registry`, which securely proxies to the same read-only MCP backend and retains exactly the existing rate limits, security headers and body cap.

The new `io.github.getremcp/docsy` listing uses only the distinct organizational endpoint; the old `/mcp` endpoint and legacy entry stay available for existing users. The two real endpoints were verified with MCP initialize, tools/list, resolve and cited document retrieval. Do not claim the organization registry is active until the new OIDC publish workflow succeeds and the Registry API reports `active`.
