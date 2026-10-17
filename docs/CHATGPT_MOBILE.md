# ChatGPT installation: desktop-only classification

## Root cause

Docsy's standard portable package has a root `mcp.json` (and legacy
`.mcp.json`) for clients including Codex, Claude, and Cursor. An imported
ChatGPT plugin can be marked **Desktop only** merely because it contains MCP
manifest files, **even if the URL is a remote HTTPS service**.

This label does not mean the Docsy backend must be executed locally.

## ChatGPT-specific registered-app package

For **personal/workspace testing** where a Docsy app has already been
registered in ChatGPT and the current user/role can access it:

```sh
python3 scripts/publishing/package_chatgpt_app.py \
  --app-id "asdk_app_YOUR_REGISTERED_DOCSY_APP_ID" \
  --output /tmp/docsy-chatgpt-app.zip
```

Import the generated ZIP as a new plugin package, or update the existing
eligible package. It contains `.app.json` with the registered app ID and
`extensions.com.openai.apps="./.app.json"`, but **no `mcp.json` or
`.mcp.json`**. Never use a made-up ID: get the ID of the actual registered
Docsy app from ChatGPT and confirm its availability for your role.

Keep the **standard portable distribution** and official review ZIP unchanged.
Do not delete the MCP manifests in the Claude/Cursor/Codex source package.

## Public plugin publication and mobile availability

Do **not** submit `.app.json` as a substitute for publishing a public MCP
integration. The universal public Plugin Directory requires **With MCP**
submission for a remote MCP-backed plugin, followed by review, approval, and
publication. The registration-only package is for local/workspace installs.

Removing an import-time Desktop only classification **does not guarantee**
that the underlying custom MCP app works on the native iOS/Android ChatGPT
client. OpenAI currently documents custom MCP apps as web-only; specific
plugin capabilities vary by surface. Test on the target ChatGPT clients
and check the plugin/app's role and surface eligibility.

Official references:

- https://help.openai.com/en/articles/20001256
- https://developers.openai.com/plugins/build/plugins
- https://developers.openai.com/plugins/deploy/submission
- https://help.openai.com/en/articles/12584461-developer-mode-and-full-mcp-connectors-in-chatgpt
