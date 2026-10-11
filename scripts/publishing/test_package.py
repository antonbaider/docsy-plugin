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
        self.assertEqual(plugin["version"],"1.0.4")
        review=plugin["extensions"]["com.openai"]["review"]
        self.assertEqual(len(review["test_cases"]["positive"]),5)
        self.assertEqual(len(review["test_cases"]["negative"]),3)
        self.assertIn("plugin-v1.0.4",review["demo_recording_url"])
        self.assertTrue(review["demo_recording_url"].endswith(".mp4"))
        self.assertTrue(plugin["extensions"]["com.openai"]["publication"]["release_notes"])

        interface=plugin["extensions"]["com.openai"]["interface"]
        for key in ["websiteURL","supportURL","privacyPolicyURL","termsOfServiceURL"]:
            self.assertTrue(interface[key].startswith("https://docsy.remcp.site"))
        self.assertEqual(json.loads((ROOT/"mcp.json").read_text())["mcpServers"]["docsy"]["url"],SERVER)
        self.assertEqual(json.loads((ROOT/".mcp.json").read_text())["mcpServers"]["docsy"]["type"],"http")

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
