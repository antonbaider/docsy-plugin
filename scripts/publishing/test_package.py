"""Release packaging regression checks, independent of CI network access."""
import hashlib
import json
from pathlib import Path
import sys
import tempfile
import unittest
from zipfile import ZipFile

sys.path.insert(0,str(Path(__file__).parent))
import cursor_deeplink as cursor
from package import ROOT,FILES,SERVER,build,validate

class PluginPackageTests(unittest.TestCase):
    def test_manifests_reference_one_public_mcp_and_owned_icons(self):
        plugin=validate()
        self.assertEqual(plugin["name"],"docsy")
        self.assertEqual(plugin["license"],"MIT")
        self.assertEqual(plugin["version"],"1.0.7")
        self.assertEqual(plugin["author"]["name"],"Anton Baider")
        self.assertEqual(plugin["extensions"]["com.openai"]["interface"]["developerName"],"Anton Baider")
        self.assertNotIn("free",plugin["extensions"]["com.openai"]["interface"]["longDescription"].lower())
        review=plugin["extensions"]["com.openai"]["review"]
        self.assertEqual(len(review["test_cases"]["positive"]),5)
        self.assertEqual(len(review["test_cases"]["negative"]),3)
        self.assertIn("plugin-v1.0.7",review["demo_recording_url"])
        self.assertTrue(review["demo_recording_url"].endswith(".mp4"))
        self.assertTrue(plugin["extensions"]["com.openai"]["publication"]["release_notes"])

        interface=plugin["extensions"]["com.openai"]["interface"]
        for key in ["websiteURL","supportURL","privacyPolicyURL","termsOfServiceURL"]:
            self.assertTrue(interface[key].startswith("https://docsy.remcp.site"))
        self.assertEqual(json.loads((ROOT/"mcp.json").read_text())["mcpServers"]["docsy"]["url"],SERVER)
        self.assertEqual(json.loads((ROOT/".mcp.json").read_text())["mcpServers"]["docsy"]["type"],"http")

    def test_installation_docs_cover_personal_chatgpt_and_clients_without_claiming_approval(self):
        readme=(ROOT/"README.md").read_text()
        self.assertIn("ChatGPT Work before public directory approval",readme)
        self.assertIn("No authentication",readme)
        self.assertIn("codex mcp add docsy --url https://docsy.remcp.site/mcp/registry",readme)
        self.assertIn("MCP: Open User Configuration",readme)
        self.assertIn("getremcp/docsy-plugin",readme)
        self.assertIn("not yet approved",readme)

    def test_distribution_status_tracks_current_plugin_release(self):
        version=validate()["version"]
        status=(ROOT/"docs/DISTRIBUTION-STATUS.md").read_text()
        readme=(ROOT/"README.md").read_text()
        self.assertIn(f"GitHub Plugin v{version}",status)
        self.assertIn(f"Active, latest v{version}",status)
        self.assertIn(f"The plugin package version is **v{version}**",status)
        self.assertIn(f"Installable v{version}",status)
        self.assertIn("Codex Git marketplace",status)
        self.assertIn(f"plugin-v{version}/docsy-review-walkthrough-v{version}.mp4",readme)
        self.assertIn(f"/tmp/docsy-plugin-v{version}.zip",readme)

    def test_official_mcp_registry_has_owned_remote_and_no_unpublished_package(self):
        plugin=json.loads((ROOT/"plugin.json").read_text())
        registry=json.loads((ROOT/"server.json").read_text())
        self.assertEqual(registry["name"],"io.github.getremcp/docsy")
        self.assertEqual(registry["version"],plugin["version"])
        self.assertEqual(registry["title"],"Docsy")
        self.assertEqual(registry["repository"]["url"],"https://github.com/getremcp/docsy-plugin")
        self.assertEqual(registry["remotes"],[{"type":"streamable-http","url":"https://docsy.remcp.site/mcp/registry"}])
        self.assertNotIn("packages",registry)

    def test_public_claude_marketplace_can_reference_plugin(self):
        marketplace=json.loads((ROOT/".claude-plugin/marketplace.json").read_text())
        self.assertEqual(marketplace["name"],"docsy-community")
        self.assertEqual(len(marketplace["plugins"]),1)
        plugin=marketplace["plugins"][0]
        self.assertEqual(plugin["name"],"docsy")
        self.assertEqual(plugin["source"],"./")
        # A plugin co-located with its marketplace should not force GitHub SSH
        # auth on public installs: Claude Code's github-source clone uses SSH.
        # Relative paths are read from the already-downloaded marketplace.

    def test_cursor_one_click_link_contains_only_public_remote_url(self):
        link=cursor.install_link()
        self.assertTrue(link.startswith("cursor://anysphere.cursor-deeplink/mcp/install?"))
        self.assertTrue(cursor.verify(link))
        self.assertNotIn("Bearer",link)

    def test_smoke_targets_exact_submitted_endpoint_not_legacy_alias(self):
        source=(ROOT/"scripts/publishing/mcp-review-smoke.mjs").read_text()
        self.assertIn('new URL("../../mcp.json",import.meta.url)',source)
        self.assertIn('process.env.DOCSY_MCP_URL',source)
        self.assertEqual(source.count('fetch(mcpUrl,{'),3)
        self.assertNotIn('fetch(base+"/mcp",',source)
        self.assertEqual(json.loads((ROOT/"mcp.json").read_text())["mcpServers"]["docsy"]["url"],SERVER)

    def test_codex_marketplace_entry_is_rooted_and_complete(self):
        catalog=json.loads((ROOT/".agents/plugins/marketplace.json").read_text())
        self.assertEqual(catalog["name"],"docsy-community")
        self.assertEqual(len(catalog["plugins"]),1)
        entry=catalog["plugins"][0]
        self.assertEqual(entry["name"],"docsy")
        self.assertEqual(entry["category"],"Developer Tools")
        self.assertEqual(entry["policy"]["installation"],"AVAILABLE")
        self.assertEqual(entry["policy"]["authentication"],"ON_INSTALL")
        self.assertEqual(entry["source"],{"source":"local","path":"./"})
        self.assertTrue((ROOT/"plugin.json").is_file())
        self.assertTrue((ROOT/"mcp.json").is_file())

    def test_zip_is_deterministic_and_contains_no_repo_secrets_or_sources(self):
        with tempfile.TemporaryDirectory() as folder:
            a=Path(folder)/"first.zip"
            b=Path(folder)/"second.zip"
            digest1=build(a)
            digest2=build(b)
            self.assertEqual(digest1,digest2)
            self.assertEqual(a.read_bytes(),b.read_bytes())
            self.assertEqual(digest1,hashlib.sha256(a.read_bytes()).hexdigest())
            with ZipFile(a) as archive:
                self.assertEqual(sorted(archive.namelist()),sorted(FILES))
                for info in archive.infolist():
                    self.assertFalse(info.filename.startswith("/"))
                    self.assertNotIn("..",Path(info.filename).parts)
                    self.assertGreater(info.file_size,0)
                self.assertNotIn(".env",archive.namelist())
                self.assertNotIn(".mcp.json",archive.namelist())
                self.assertNotIn("docs/PUBLISHING.md",archive.namelist())

if __name__=="__main__":
    unittest.main()
