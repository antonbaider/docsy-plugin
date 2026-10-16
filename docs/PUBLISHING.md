# Publishing Docsy to Claude, ChatGPT/OpenAI and Cursor

Docsy exposes one **public, read-only remote MCP** endpoint:

    https://docsy.remcp.site/mcp/registry

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
    python3 scripts/publishing/package.py --output /tmp/docsy-plugin-v1.0.7.zip

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
3. Upload the verified ZIP from above in the Plugins submission portal using **With MCP**. Connect `https://docsy.remcp.site/mcp/registry` as the universal HTTPS endpoint. Complete the platform's domain challenge. No OAuth is needed for the anonymous public read-only tool set; do not pretend Docsy implements OAuth.
4. Run **Scan Tools**. Review the live name, descriptions, input schema, annotations, identity and security schemes of all five tools. Provide the four legal/support website URLs, owned logos, and accurate publisher information.
5. Confirm the five positive and three negative cases embedded in `plugin.json`. Collect real expected results from the smoke test (no forged outputs). Produce an **actual reviewer-accessible demo recording** showing tools working; do not fabricate a video URL or reviewer credentials.
6. Submit for review and act on feedback. Publish only after approval. Plugin ZIP uploads, verification and directory publishing require the publisher's account permissions.

## Anthropic Claude directory

Official source: https://claude.com/resources/articles/build-plugins-for-claude

Anthropic's plugin directory accepts a remote **single MCP connector** or a **GitHub plugin bundle**. Using a paid Claude plan, open the developer submission portal from the Claude directory.

- For the straightforward MCP-only submission, supply `https://docsy.remcp.site/mcp/registry`. Provide real publisher contacts, product description, source links, privacy/terms/support URLs, and a working review demo.
- For bundled installation, use the publicly accessible Docsy plugin repository; manifests are stored in `.claude-plugin/plugin.json` / `.mcp.json` and the documentation skill is in `skills/find-docs/`. Validate the plugin's exact root and repository URL in the portal before submission.
- Claude may audit security and compatibility and does not guarantee inclusion. Review status and analytics appear after submission/approval, where eligible.

## Cursor Marketplace

Official references:
- https://prod.cursor.com/docs/plugins
- https://cursor.com/marketplace/publish

Cursor accepts **Agent Plugins** (root `plugin.json` + `mcp.json` + skills) and standalone remote MCP servers. The repository is open source under MIT; no hooks or local executable commands are bundled.

To connect without marketplace listing, configure Cursor with:

    {"mcpServers":{"docsy":{"url":"https://docsy.remcp.site/mcp/registry"}}}

For public listing, submit the public GitHub source through Cursor Marketplace's publisher form. Cursor manually reviews submissions. Provide publisher identity, legal URLs, usage examples and the real GitHub URL. Only claim official marketplace availability once approved and indexed.

## Independent directory publication

The organization-owned [MCP Registry listing](https://registry.modelcontextprotocol.io/v0.1/servers?search=getremcp) is the canonical source for automatic directory discovery. As of 2026-10-16, [mcpub](https://mcpub.dev/) reports Docsy registered and publicly searchable; [MCP.Directory](https://mcp.directory/submit) accepted the public GitHub repository for review; and [mcp.tc](https://mcp.tc/s/dc7OMIJio-fn2yHv) is awaiting human review. See [distribution status](DISTRIBUTION-STATUS.md) for evidence; do not confuse submissions with live listings. The public server card is at `https://docsy.remcp.site/.well-known/mcp.json`.

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

`server.json` is a dedicated manifest for the official MCP Registry in the GitHub-owned namespace `io.github.getremcp/docsy`. The only transport is the publicly reachable Streamable HTTP endpoint, `https://docsy.remcp.site/mcp/registry`; no unpublished npm package is listed.

Run **Publish Docsy MCP Registry** from GitHub Actions on `main` to validate and publish with GitHub-hosted OIDC. The publisher CLI v1.8.1 is downloaded from the official registry release and verified by pinned SHA-256. No personal access token or long-lived secret is used. Publication must be confirmed from the workflow result and registry response; a prepared manifest alone is not a listing.

## Verified listings, 2026-10-14

The official MCP Registry confirmed `io.github.getremcp/docsy` version `1.0.5` with status `active`. GitHub OIDC publication completed in [workflow #38594454932](https://github.com/getremcp/docsy-plugin/actions/runs/38594454932), using the public Streamable HTTP endpoint. Registry API: https://registry.modelcontextprotocol.io/v0.1/servers?search=docsy .

Smithery accepted the `antonbaider/docsy` external remote at https://smithery.ai/servers/antonbaider/docsy . The initial deployment ID was `4909e9c3-301e-435f-90dc-4e8a89529bd9`; this is not an OpenAI, Claude or Cursor plugin-directory approval.

The OpenAI draft is `v1.0.5` with domain/MCP verified; **submission is still pending the individual publisher's own six legal declarations**. The private backend's npm SDK/CLI have not been published because `@docsy` scope ownership and npm authentication are not available.


## Organization registry endpoint migration

The GitHub repository moved to `getremcp/docsy-plugin` on 2026-10-14. The original official MCP Registry entry `io.github.antonbaider/docsy` already claimed `https://docsy.remcp.site/mcp/registry`, and the official Registry enforces one server name per remote URL. To preserve all previously installed clients, the edge now hosts the separately tested, stable organizational route `https://docsy.remcp.site/mcp/registry`, which securely proxies to the same read-only MCP backend and retains exactly the existing rate limits, security headers and body cap.

The new `io.github.getremcp/docsy` listing uses only the distinct organizational endpoint; the old `/mcp` endpoint and legacy entry stay available for existing users. The two real endpoints were verified with MCP initialize, tools/list, resolve and cited document retrieval. Do not claim the organization registry is active until the new OIDC publish workflow succeeds and the Registry API reports `active`.

## Organizational listings verified (2026-10-14)

The organization-owned official MCP Registry listing **`io.github.getremcp/docsy` version 1.0.5** is published and marked `active` by the Registry API. [The OIDC publisher run #38599097649](https://github.com/getremcp/docsy-plugin/actions/runs/38599097649) succeeded. It uses the fully functional `https://docsy.remcp.site/mcp/registry` endpoint.

Smithery also accepted `getremcp/docsy` as an external MCP release. The organization-specific public listing is [smithery.ai/servers/getremcp/docsy](https://smithery.ai/servers/getremcp/docsy); its initial deployment ID was `0c8e292e-147c-49eb-9666-1ad22297e80a`. The older `antonbaider/docsy` listing remains available for compatibility.

These public MCP directory publications do not imply approval by the OpenAI, Claude or Cursor official plugin marketplaces.

## v1.0.6 organizational release (October 14, 2026)

The canonical public client transport for the new release is `https://docsy.remcp.site/mcp/registry`, owned by organizational registry entry `io.github.getremcp/docsy`. The legacy `/mcp` endpoint remains active to avoid breaking existing installations. The release should include a deterministic ZIP and a real-response review video, both generated from its immutable `plugin-v1.0.6` tag; successful release-integrity CI and MCP Registry OIDC publication must be verified before announcing it.


## v1.0.7 verified public release (October 16, 2026)

- [Public ZIP and real-response review recording](https://github.com/getremcp/docsy-plugin/releases/tag/plugin-v1.0.7).
- [GitHub release-integrity validation](https://github.com/getremcp/docsy-plugin/actions/runs/38953672390) confirmed that the attached ZIP matches immutable tag source.
- [MCP Registry OIDC publish run](https://github.com/getremcp/docsy-plugin/actions/runs/38953737055) passed, and the Registry API reported `io.github.getremcp/docsy@1.0.7` as `active` and `isLatest=true`.
- The video uses newly captured real public MCP responses, not an impersonated ChatGPT UI.
- The portable ZIP contains the full five positive and three negative review cases, verified PNG artwork and a single existing public MCP endpoint. The tools remain read-only.

A public GitHub release or MCP Registry listing does **not** imply that the OpenAI Plugin Directory accepted a submitted draft, completed identity/legal review, or published a marketplace listing. Personal Plugin Creator releases use a separate author-account update path and must be verified independently.

## Updating the existing private Plugin Creator installation

The public OpenAI submission ZIP and a personal Plugin Creator update are
different archives. A personal plugin may have a legacy compatibility
manifest and existing user prompts which must not be replaced by a clean
public ZIP. Never use create_plugin to repair an existing installation.

1. Read the exact private plugin by backend plugin_id via Plugin Creator
   get_plugin_files; record its current_release_id. Save its existing
   .codex-plugin/plugin.json into a local file outside the repository.
2. Prepare a public release with a strictly higher semantic version than
   that stored personal release. The script rejects equal or older versions
   instead of silently triggering the platform's automatic patch bump.
3. From the same immutable release source, build a dedicated overlay:

       python3 scripts/publishing/account_overlay.py \
         --existing-legacy /path/to/existing-codex-plugin.json \
         --output /tmp/docsy-plugin-account-update.zip

   It includes the original public package files, owned icons, and a legacy
   compatibility manifest; it retains the prior publisher email, exact user
   default prompts, skill path, and MCP binding. The archive must not contain
   a private .mcp.json, .app.json, credentials, or account tokens.
4. Pass the ZIP as a host-uploaded file available to Plugin Creator
   update_plugin, with the exact plugin_id and saved current_release_id as its
   expected_release_id. A path on another paired machine is not a
   host-uploaded file and fails with UNREGISTERED_FILE_REFERENCE; do not
   assert success or fabricate a local file reference.
5. Re-read the saved release with get_plugin_files and verify its version,
   manifests, complete five positive/three negative review tests, icon
   inventory, and unchanged MCP endpoint.

This private update is not an OpenAI public-directory submission.
Publisher verification, the submission portal, legal declarations, review,
and subsequent publication remain separate.
