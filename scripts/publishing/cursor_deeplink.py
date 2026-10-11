#!/usr/bin/env python3
"""Create and verify an official Cursor MCP install deeplink.

This uses the documented single-server JSON configuration and no user token.
"""
import base64
import json
from pathlib import Path
from urllib.parse import quote,parse_qs,urlsplit

ROOT=Path(__file__).resolve().parents[2]
SERVER="https://docsy.remcp.site/mcp"
PREFIX="cursor://anysphere.cursor-deeplink/mcp/install"

def install_link():
    data=json.loads((ROOT/".cursor/mcp.json").read_text(encoding="utf-8"))
    assert data=={"mcpServers":{"docsy":{"url":SERVER}}}
    config=json.dumps({"docsy":{"url":SERVER}},separators=(",",":"))
    encoded=base64.b64encode(config.encode("utf-8")).decode("ascii")
    return f"{PREFIX}?name=docsy&config={quote(encoded,safe='')}"

def verify(link):
    url=urlsplit(link)
    assert url.scheme=="cursor"
    assert url.netloc=="anysphere.cursor-deeplink"
    assert url.path=="/mcp/install"
    query=parse_qs(url.query,strict_parsing=True)
    assert query["name"]==["docsy"]
    decoded=json.loads(base64.b64decode(query["config"][0],validate=True))
    assert decoded=={"docsy":{"url":SERVER}}
    return True

if __name__=="__main__":
    link=install_link()
    assert verify(link)
    print(link)
