# Docsy Directory Review Evidence (October 11, 2026)

This document explains what is actually available, what each tool does, and
what remains necessary for a verified publisher to submit Docsy to the
OpenAI, Claude, or Cursor directories.

## Proof of public availability

- Product / docs: https://docsy.remcp.site/docs
- Remote MCP: https://docsy.remcp.site/mcp
- Privacy: https://docsy.remcp.site/privacy
- Terms: https://docsy.remcp.site/terms
- Support / public issues: https://docsy.remcp.site/support
- Open-source plugin: https://github.com/antonbaider/docsy-plugin
- Public plugin ZIP: https://github.com/antonbaider/docsy-plugin/releases/tag/plugin-v1.0.4
- On-demand validation: `node scripts/publishing/mcp-review-smoke.mjs`
- Automated release build: GitHub Actions → Public plugin quality.

The MCP endpoint uses stateless Streamable HTTP and accepts anonymous public
read requests with rate limits. This plugin does **not** provide private
repository access or require OAuth. It has no custom MCP UI (so no client UI
screenshots are supplied). The hosted crawler, database and API are operated
separately from the open-source plugin; their code is not part of this package.

## Real demonstration recording

The [public v1.0.4 review video](https://github.com/antonbaider/docsy-plugin/releases/download/plugin-v1.0.4/docsy-review-walkthrough-v1.0.4.mp4) shows nine panels derived from **actual, timestamped
JSON-RPC MCP calls** made on October 11, 2026. This is a visual walkthrough of
live requests and sanitized metadata/results, not a claim to show the
ChatGPT, Codex, Cursor or Claude user interface. It documents:

1. MCP initialize and tool discovery.
2. Resolve React's official library ID.
3. Query React useEffect cleanup with original source URLs.
4. List indexed React versions.
5. Search public documentation and obtain a stable document ID.
6. Fetch the selected document with source attribution.
7. Resolve Fastify and fetch request-validation documentation.
8. Refuse an unknown delete tool, incomplete arguments, and missing ID.
9. Verify HTTPS privacy, terms and support pages.

The capture intentionally omits full copyrighted third-party excerpts,
personal tokens and user-specific usage information. To reproduce the
recording data, use `node scripts/publishing/review-demo-data.mjs`.

This recording may not satisfy a marketplace requirement to show its *own
client interface*. If a reviewer requests a native ChatGPT/Codex or Claude
workflow recording, the publisher must create it after completing login and
identity verification. Do not describe this as platform approval.

## MCP tool and security annotation rationale

The public MCP intentionally exposes only five documentation retrieval
tools; there are no create, update, delete, send, purchase or payment tools.
Each advertises `readOnlyHint: true`, `destructiveHint: false` and
`openWorldHint: true`. Repeated retrievals are marked idempotent. These are
**user-facing operation hints**, not a claim that a hosted service never
writes operational telemetry or updates its own caches.

| Tool | Retrieval behavior | Why open-world? | Why non-destructive? |
|---|---|---|---|
| `resolve-library-id` | Resolve a public library name and rank candidate IDs | Registry represents GitHub and other external open-source documentation | Cannot change libraries, user repositories or account settings |
| `query-docs` | Return versioned excerpts and original source links | Retrieves public material from external project documentation; historical or cold versions can be hydrated | Cannot edit third-party content or submit mutations on behalf of the user |
| `list-library-versions` | List indexed version labels and stable public releases | May look up public GitHub version metadata | Only returns version identifiers |
| `search` | Search the public indexed document corpus | Source repositories and websites are public and open-ended | Outputs result IDs and source URLs only |
| `fetch` | Retrieve one previously indexed chunk by document ID | Chunk links to its original external public source | Returns content without any edit operation |

**Operational side effects for reviewers:** Like most hosted retrieval
services, Docsy records request counts, rate-limit events and aggregate
library usage in its own infrastructure. `query-docs` may trigger
server-side archival cache recovery or lazy public-version indexing if
content is missing. These internal maintenance effects do not give clients
the ability to modify published documentation or private repositories.
If the directory interprets `readOnlyHint` as forbidding even cache
maintenance or internal telemetry, reviewers should flag the tool's
classification for an updated MCP scan **before publication**. Do not
conceal these internal operations.

## Exactly five positive and three negative examples

The exact prompts, expected tool names and results are embedded in
`plugin.json` under `extensions.com.openai.review.test_cases`. Live tool
semantics are also checked by the repository smoke command.

Positive cases: React effect cleanup; React version listing; public
cross-library search; document fetch by returned ID; Fastify validation docs.

Negative cases: private GitHub content; deletion of all indexed documents;
disclosure of account API keys.

For the two malformed-tool safety checks, Docsy refuses an unknown mutation
tool and incomplete `query-docs` arguments with MCP errors. A syntactically
valid but nonexistent document ID returns `Document not found.`.

## Remaining account actions — not completed by this repository

- OpenAI: verify an individual/business publisher, upload the ZIP to
  https://platform.openai.com/plugins, scan the current MCP, complete domain
  verification with the exact portal-generated challenge token, review
  annotations, save test cases and recording, attest and **submit for review**.
  Approval must be followed by an explicit **Publish** action.
- Claude: log in using an eligible paid account at
  https://claude.ai/directory/manage/new, submit the MCP URL or this public
  GitHub repository, respond to validation and approval.
- Cursor: sign in at https://cursor.com/marketplace/publish, submit this
  public repository, then wait for manual review.

No app-store logo, endorsement, marketplace listing or publisher approval
should be advertised until independently confirmed.

## Reproducibility and release provenance

The canonical submitted package is the ZIP attached to the **v1.0.4**
GitHub release. Rebuilding from the release tag must produce the same SHA-256
as the downloadable asset. The earlier v1.0.3 ZIP had a mismatch caused by
building from an uncommitted working tree; do not submit v1.0.3. The v1.0.4
source and artifact are verified before release.
