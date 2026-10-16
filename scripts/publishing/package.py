#!/usr/bin/env python3
"""Build a deterministic, minimal, secret-free Docsy submission ZIP."""
import argparse
import hashlib
import json
from pathlib import Path
import re
import sys
from zipfile import ZIP_DEFLATED, ZipFile, ZipInfo

ROOT=Path(__file__).resolve().parents[2]
ASSETS=[
    "assets/docsy-icon-192.png",
    "assets/docsy-logo-512.png",
    "assets/docsy-logo-dark-512.png"
]
FILES=["plugin.json","mcp.json","skills/find-docs/SKILL.md",*ASSETS]
SERVER="https://docsy.remcp.site/mcp/registry"
FIELDS=["websiteURL","privacyPolicyURL","termsOfServiceURL","supportURL"]

def validate():
    plugin=json.loads((ROOT/"plugin.json").read_text())
    mcp=json.loads((ROOT/"mcp.json").read_text())
    assert plugin.get("$schema")=="https://agent-plugins.org/schemas/1.0.0/plugin.schema.json"
    assert re.fullmatch(r"[a-z][a-z0-9]*(?:-[a-z0-9]+)*",plugin["name"])
    assert re.fullmatch(r"\d+\.\d+\.\d+",plugin["version"])
    server=mcp["mcpServers"]["docsy"]
    assert server["type"]=="streamable-http" and server["url"]==SERVER
    interface=plugin["extensions"]["com.openai"]["interface"]
    assert interface["displayName"]=="Docsy"
    assert len(interface["displayName"])<=30
    assert 0<len(interface["shortDescription"])<=30
    assert interface["category"]=="Developer Tools"
    # Public review rejects missing/malformed listing copy and icon assets,
    # even if the Agent Plugins manifest itself can still be parsed.
    assert plugin.get("apps") is None and plugin["extensions"]["com.openai"].get("apps") is None, "Upload must not embed private app bindings"
    for key,limit in (("longDescription",4000),("developerName",80)):
        value=interface.get(key)
        assert isinstance(value,str) and 0<len(value.strip())<=limit, f"Invalid {key}"
    prompts=interface.get("defaultPrompt")
    assert isinstance(prompts,list) and 1<=len(prompts)<=3, "Need 1-3 default prompts"
    normalized=[]
    for prompt in prompts:
        assert isinstance(prompt,str) and prompt.strip() and len(prompt)<=128, "Invalid default prompt"
        assert "\n" not in prompt and "\r" not in prompt, "Default prompts must be single-line"
        assert "@" not in prompt, "Default prompts must not contain app mentions"
        normalized.append(" ".join(prompt.split()).casefold())
    assert len(set(normalized))==len(normalized), "Duplicate default prompts"
    for key,min_side in (("composerIcon",48),("logo",256),("logoDark",256)):
        if key=="logoDark" and not interface.get(key):
            continue
        path=ROOT/interface[key].lstrip("./")
        assert path.is_file(), f"Missing asset: {key}"
        raw=path.read_bytes()
        assert len(raw)<=5*1024*1024, f"Oversized PNG asset: {key}"
        assert raw.startswith(b"\x89PNG\r\n\x1a\n") and raw[12:16]==b"IHDR", f"Non-PNG asset: {key}"
        width=int.from_bytes(raw[16:20],"big")
        height=int.from_bytes(raw[20:24],"big")
        assert width==height and width>=min_side, f"Invalid square PNG dimensions: {key}"
    assert plugin["author"]["name"]==interface["developerName"]
    for key in FIELDS:
        assert interface[key].startswith("https://docsy.remcp.site/") or (
            key=="websiteURL" and interface[key]=="https://docsy.remcp.site"
        ),key
    for key in ["composerIcon","logo","logoDark"]:
        assert interface[key].lstrip("./") in ASSETS
    review=plugin["extensions"]["com.openai"]["review"]["test_cases"]
    assert len(review["positive"])==5 and len(review["negative"])==3
    assert all(row.get("description") and len(row["description"])<=4000 for row in review["positive"]+review["negative"])
    assert plugin["extensions"]["com.openai"]["publication"]["release_notes"].strip()
    demo=plugin["extensions"]["com.openai"]["review"].get("demo_recording_url")
    assert (
        isinstance(demo,str) and demo.startswith(
            "https://github.com/getremcp/docsy-plugin/releases/download/"
        ) and demo.endswith(".mp4") and
        ("/plugin-v"+plugin["version"]+"/") in demo
    ), "version-matched public review video URL required"
    assert plugin["extensions"]["com.openai"].get("onboardingSkill")=="./skills/find-docs/SKILL.md"
    assert all(row.get("prompt") and row.get("tools_triggered") and row.get("expected_behavior") for row in review["positive"])
    assert all(row.get("prompt") and row.get("expected_behavior") for row in review["negative"])
    toolset={"resolve-library-id","query-docs","list-library-versions","search","fetch"}
    assert all(set(t.strip() for t in row["tools_triggered"].split(",")) <= toolset for row in review["positive"])
    assert (ROOT/"skills/find-docs/SKILL.md").read_text().startswith("---\nname: find-docs\n")
    assert all((ROOT/file).is_file() and not (ROOT/file).is_symlink() and
               (ROOT/file).stat().st_size>0 for file in FILES)
    claude=json.loads((ROOT/".claude-plugin/plugin.json").read_text())
    legacy=json.loads((ROOT/".mcp.json").read_text())
    assert claude["name"]==plugin["name"] and legacy["mcpServers"]["docsy"]["url"]==SERVER
    assert len(set(FILES))==len(FILES)
    return plugin

def build(output):
    validate()
    output.parent.mkdir(parents=True,exist_ok=True)
    with ZipFile(output,"w",compression=ZIP_DEFLATED,compresslevel=9) as archive:
        for name in sorted(FILES):
            raw=(ROOT/name).read_bytes()
            info=ZipInfo(name,(2026,10,11,0,0,0))
            info.compress_type=ZIP_DEFLATED
            info.external_attr=0o644<<16
            archive.writestr(info,raw,compress_type=ZIP_DEFLATED,compresslevel=9)
    with ZipFile(output) as zipfile:
        assert sorted(zipfile.namelist())==sorted(FILES)
    return hashlib.sha256(output.read_bytes()).hexdigest()

if __name__=="__main__":
    parser=argparse.ArgumentParser()
    parser.add_argument("--check",action="store_true")
    parser.add_argument("--output",type=Path,default=None)
    args=parser.parse_args()
    try:
        if args.check:
            plugin=validate()
            print("Plugin metadata valid:",plugin["name"],plugin["version"],"files",len(FILES))
        else:
            output=args.output or Path("/tmp/docsy-plugin-"+validate()["version"]+".zip")
            checksum=build(output)
            print("Created",output,"SHA256",checksum)
    except (KeyError,AssertionError,ValueError,IndexError,TypeError) as error:
        print("Plugin validation failed:",str(error),file=sys.stderr)
        sys.exit(1)
