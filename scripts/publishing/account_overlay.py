#!/usr/bin/env python3
"""Prepare a safe, deterministic Plugin Creator update of an existing Docsy plugin.

The author-supplied public ZIP is intentionally independent of private Plugin
Creator state. This script generates a separate incremental account update
which preserves the legacy compatibility declaration and managed MCP binding.
It never uploads, creates, or publishes a plugin.
"""
import argparse
from copy import deepcopy
import hashlib
import json
from pathlib import Path
import re
from zipfile import ZIP_DEFLATED, ZipFile, ZipInfo

from package import ASSETS, ROOT, SERVER, validate


def parse_semver(value):
    if not isinstance(value, str) or not re.fullmatch(r"\d+\.\d+\.\d+", value):
        raise ValueError("Expected strict semantic version, e.g. 1.0.8")
    return tuple(map(int, value.split(".")))


def prepare_legacy(previous, current):
    """Preserve existing runtime paths and instructions; update review metadata."""
    if previous.get("name") != current.get("name"):
        raise ValueError("Plugin identity does not match the stored plugin")
    if parse_semver(current["version"]) <= parse_semver(previous.get("version")):
        raise ValueError("Plugin Creator requires a strictly newer semantic version")
    if previous.get("skills") != "./skills" or previous.get("mcpServers") != "./.mcp.json":
        raise ValueError("Unexpected private skills/MCP binding; inspect before update")
    previous_ext = previous.get("extensions", {}).get("com.openai", {})
    if previous.get("apps") is not None or previous_ext.get("apps") is not None:
        raise ValueError("App-backed plugin cannot be overwritten by this standalone overlay")
    updated = deepcopy(previous)
    for key in ("version", "description", "homepage", "repository", "license", "keywords"):
        updated[key] = deepcopy(current[key])
    updated["interface"] = deepcopy(current["extensions"]["com.openai"]["interface"])
    # Personal prompts may have been customized after installation. Preserve
    # their original string/list type, wording, and order exactly.
    if "defaultPrompt" in previous.get("interface", {}):
        updated["interface"]["defaultPrompt"] = deepcopy(previous["interface"]["defaultPrompt"])
    updated.setdefault("extensions", {})["com.openai"] = deepcopy(current["extensions"]["com.openai"])
    updated["extensions"]["com.openai"]["interface"] = deepcopy(updated["interface"])
    # Keep previously selected publisher email and all existing runtime bindings.
    updated.setdefault("author", {}).update(current["author"])
    return updated


def build_account_overlay(existing_legacy, output, root=ROOT):
    current=validate() if root == ROOT else json.loads((root/"plugin.json").read_text())
    portable=json.loads((root/"mcp.json").read_text())
    installed=json.loads((root/".mcp.json").read_text())
    url=portable["mcpServers"]["docsy"]["url"]
    if url != SERVER or installed["mcpServers"]["docsy"]["url"] != url:
        raise ValueError("MCP endpoint drift: leave existing plugin binding unchanged")
    previous=json.loads(existing_legacy.read_text())
    updated=prepare_legacy(previous,current)
    files={
        "plugin.json":(root/"plugin.json").read_bytes(),
        "mcp.json":(root/"mcp.json").read_bytes(),
        ".codex-plugin/plugin.json":(json.dumps(updated,ensure_ascii=False,indent=2)+"\n").encode(),
        "skills/find-docs/SKILL.md":(root/"skills/find-docs/SKILL.md").read_bytes()
    }
    for asset in ASSETS:
        files[asset]=(root/asset).read_bytes()
    output.parent.mkdir(parents=True,exist_ok=True)
    with ZipFile(output,"w",compression=ZIP_DEFLATED,compresslevel=9) as archive:
        for name in sorted(files):
            info=ZipInfo(name,(2026,10,16,0,0,0))
            info.compress_type=ZIP_DEFLATED
            info.external_attr=0o644<<16
            archive.writestr(info,files[name],compress_type=ZIP_DEFLATED,compresslevel=9)
    with ZipFile(output) as archive:
        if archive.testzip() is not None or sorted(archive.namelist()) != sorted(files):
            raise ValueError("Invalid Plugin Creator update archive")
    return hashlib.sha256(output.read_bytes()).hexdigest()


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--existing-legacy",type=Path,required=True,
                        help="Saved .codex-plugin/plugin.json from the exact existing plugin")
    parser.add_argument("--output",type=Path,required=True)
    args=parser.parse_args()
    checksum=build_account_overlay(args.existing_legacy,args.output)
    print("Prepared account update:",args.output,"SHA256",checksum)


if __name__=="__main__":
    main()
