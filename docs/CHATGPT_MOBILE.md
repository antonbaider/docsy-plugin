# ChatGPT: mobile availability and registered-app packaging

## Confirmed behavior vs packaging

A remote HTTPS MCP server is **not inherently desktop-only** merely because
its plugin includes `mcp.json`. OpenAI documents the **Desktop only** badge
for local stdio MCP servers, local execution, and explicit
`requires_local_executor: true` settings.

For custom MCP applications added in developer mode, OpenAI currently
documents **web-only** availability (not native iOS/Android). This is a
ChatGPT surface limitation: changing the Docsy server, ZIP or icon
cannot override it.

The registered-app package below is a *personal/workspace packaging
alternative* for already-connected ChatGPT apps. It avoids two
overlapping declarations for the same remote MCP server. It is not
a bypass for the iOS/Android limitation.

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
`.mcp.json`** and no public MCP review test cases. Never use a made-up ID: get the ID of the actual registered
Docsy app from ChatGPT and confirm its availability for your role.

Keep the **standard portable distribution** and official review ZIP unchanged.
Do not delete the MCP manifests in the Claude/Cursor/Codex source package.

## Public plugin publication and mobile availability

Do **not** submit `.app.json` as a substitute for publishing a public MCP
integration. The universal public Plugin Directory requires **With MCP**
submission for a remote MCP-backed plugin, followed by review, approval, and
publication. The registration-only package is for local/workspace installs.

The app-backed packaging **does not guarantee** that a custom MCP app
works on native iOS/Android ChatGPT. OpenAI currently documents these
custom MCP apps as web-only; approved public directory plugins have their
own surface eligibility. Test on the target ChatGPT clients
and check the plugin/app's role and surface eligibility.

Official references:

- https://help.openai.com/en/articles/20001256
- https://developers.openai.com/plugins/deploy/desktop-only
- https://developers.openai.com/plugins/deploy/submission-errors
- https://developers.openai.com/plugins/build/plugins
- https://developers.openai.com/plugins/deploy/submission
- https://help.openai.com/en/articles/12584461-developer-mode-and-full-mcp-connectors-in-chatgpt
