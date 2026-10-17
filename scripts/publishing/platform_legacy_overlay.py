#!/usr/bin/env python3
"""Build a review ZIP for the original Docsy OpenAI Platform MCP binding.

Existing Platform apps cannot change their MCP URL during a ZIP update. This
changes only mcp.json's public endpoint alias, never the normal release ZIP.
"""
import argparse
import hashlib
import json
import re
from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile, ZipInfo

from package import FILES, SERVER, validate

LEGACY_URL = "https://docsy.remcp.site/mcp"


def build_legacy_portal_update(source: Path, output: Path, *,
                               expected_version: str | None = None,
                               expected_sha256: str | None = None):
    if source.resolve() == output.resolve():
        raise ValueError("Input and output ZIP paths must differ")
    current_version = validate()["version"]
    version = expected_version or current_version
    if re.fullmatch(r"[0-9]+\.[0-9]+\.[0-9]+", version) is None:
        raise ValueError("Expected version must be a strict semver release")
    if version != current_version and not expected_sha256:
        raise ValueError("Historical release requires a pinned SHA-256 digest")
    if expected_sha256 is not None:
        if re.fullmatch(r"[0-9a-fA-F]{64}", expected_sha256) is None:
            raise ValueError("Expected SHA-256 must be 64 hex characters")
        if hashlib.sha256(source.read_bytes()).hexdigest() != expected_sha256.lower():
            raise ValueError("Source release SHA-256 does not match the pinned digest")
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
    parser.add_argument("--expected-version", help="Immutable older release version")
    parser.add_argument("--expected-sha256", help="Pinned source release asset checksum")
    args = parser.parse_args()
    print("Existing Platform MCP alias:", LEGACY_URL)
    print("Created", args.output, "SHA256", build_legacy_portal_update(
        args.input, args.output,
        expected_version=args.expected_version,
        expected_sha256=args.expected_sha256))
