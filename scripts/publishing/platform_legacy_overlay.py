#!/usr/bin/env python3
"""Build a review ZIP for the original Docsy OpenAI Platform MCP binding.

Existing Platform apps cannot change their MCP URL during a ZIP update. This
changes only mcp.json's public endpoint alias, never the normal release ZIP.
"""
import argparse
import hashlib
import json
from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile, ZipInfo

from package import FILES, SERVER, validate

LEGACY_URL = "https://docsy.remcp.site/mcp"


def build_legacy_portal_update(source: Path, output: Path):
    if source.resolve() == output.resolve():
        raise ValueError("Input and output ZIP paths must differ")
    version = validate()["version"]
    with ZipFile(source) as archive:
        if archive.testzip() is not None:
            raise ValueError("Source ZIP is corrupt")
        if sorted(archive.namelist()) != sorted(FILES):
            raise ValueError("Unexpected source ZIP contents")
        files = {name: archive.read(name) for name in FILES}
    plugin = json.loads(files["plugin.json"])
    if plugin["name"] != "docsy" or plugin["version"] != version:
        raise ValueError("Source release is not the current Docsy version")
    mcp = json.loads(files["mcp.json"])
    if list(mcp["mcpServers"]) != ["docsy"]:
        raise ValueError("Unexpected MCP server manifest")
    server = mcp["mcpServers"]["docsy"]
    if server != {"type": "streamable-http", "url": SERVER}:
        raise ValueError("Expected the canonical public read-only MCP server")
    server["url"] = LEGACY_URL
    files["mcp.json"] = (json.dumps(mcp, indent=2, ensure_ascii=False) + "\n").encode()
    output.parent.mkdir(parents=True, exist_ok=True)
    with ZipFile(output, "w", compression=ZIP_DEFLATED, compresslevel=9) as archive:
        for name in sorted(files):
            info = ZipInfo(name, (2026, 10, 16, 0, 0, 0))
            info.compress_type = ZIP_DEFLATED
            info.external_attr = 0o644 << 16
            archive.writestr(info, files[name], compress_type=ZIP_DEFLATED, compresslevel=9)
    with ZipFile(output) as archive:
        if archive.testzip() is not None:
            raise ValueError("Output ZIP is corrupt")
    return hashlib.sha256(output.read_bytes()).hexdigest()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    print("Existing Platform MCP alias:", LEGACY_URL)
    print("Created", args.output, "SHA256", build_legacy_portal_update(args.input, args.output))
