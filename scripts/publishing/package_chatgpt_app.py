#!/usr/bin/env python3
"""Build an app-backed Docsy plugin for ChatGPT without an embedded MCP manifest.

The canonical review package remains unchanged and includes portable mcp.json.
This separate package is for a registered, eligible ChatGPT app connection.
"""
import argparse
import json
import re
from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile, ZipInfo

from package import FILES, ROOT, validate

APP_ID_RE = re.compile(r"^(?:asdk_app_|connector_|templated_apps_)[A-Za-z0-9][A-Za-z0-9_-]*$")


def build_app_package(output: Path, app_id: str) -> str:
    """Create a deterministic archive; return SHA-256 hex digest."""
    import hashlib

    if not APP_ID_RE.fullmatch(app_id):
        raise ValueError("Invalid registered app ID; expected asdk_app_, connector_, or templated_apps_")
    validate()
    manifest = json.loads((ROOT / "plugin.json").read_text(encoding="utf-8"))
    extension = manifest.setdefault("extensions", {}).setdefault("com.openai", {})
    extension["apps"] = "./.app.json"
    # A local-only declaration can override an eligible remote app mapping.
    extension.pop("requires_local_executor", None)
    manifest_bytes = (json.dumps(manifest, indent=2, ensure_ascii=False) + "\n").encode("utf-8")
    app_bytes = (
        json.dumps({"apps": {"docsy": {"id": app_id, "required": True}}}, indent=2) + "\n"
    ).encode("utf-8")

    # Local MCP files cause imported plugins to be classified as Desktop only.
    sources = {
        p: (ROOT / p).read_bytes()
        for p in FILES
        if p != "mcp.json"
    }
    sources["plugin.json"] = manifest_bytes
    sources[".app.json"] = app_bytes
    output.parent.mkdir(parents=True, exist_ok=True)
    with ZipFile(output, "w", compression=ZIP_DEFLATED, compresslevel=9) as archive:
        for name in sorted(sources):
            entry = ZipInfo(name, (2026, 10, 17, 0, 0, 0))
            entry.compress_type = ZIP_DEFLATED
            entry.external_attr = 0o644 << 16
            archive.writestr(entry, sources[name], compress_type=ZIP_DEFLATED, compresslevel=9)
    return hashlib.sha256(output.read_bytes()).hexdigest()


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--app-id", required=True, help="ID of your registered Docsy ChatGPT app")
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    sha = build_app_package(args.output, args.app_id)
    print(f"Created {args.output} SHA256 {sha}")


if __name__ == "__main__":
    main()
