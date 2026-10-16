"""Verify that private Plugin Creator updates cannot erase runtime bindings."""
import json
from pathlib import Path
import tempfile
import unittest
from zipfile import ZipFile

from account_overlay import ROOT, build_account_overlay, prepare_legacy


class AccountOverlayTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.plugin=json.loads((ROOT/"plugin.json").read_text())

    def previous(self):
        current=self.plugin
        return {
            "name":current["name"],"version":"1.0.6",
            "author":{"name":current["author"]["name"],"email":"publisher@example.org"},
            "skills":"./skills","mcpServers":"./.mcp.json",
            "interface":{"defaultPrompt":["Original example"]},
            "extensions":{"com.openai":{"review":{"test_cases":{"positive":[],"negative":[]}}}}
        }

    def test_preserve_runtime_bindings_and_complete_review(self):
        previous=self.previous()
        changed=prepare_legacy(previous,self.plugin)
        self.assertEqual(changed["mcpServers"],previous["mcpServers"])
        self.assertEqual(changed["skills"],previous["skills"])
        self.assertEqual(changed["author"]["email"],"publisher@example.org")
        self.assertEqual(changed["interface"]["defaultPrompt"],["Original example"])
        self.assertEqual(changed["extensions"]["com.openai"]["interface"]["defaultPrompt"],["Original example"])
        review=changed["extensions"]["com.openai"]["review"]["test_cases"]
        self.assertEqual(len(review["positive"]),5)
        self.assertEqual(len(review["negative"]),3)
        self.assertEqual(changed["interface"]["logo"],"./assets/docsy-logo-512.png")

    def test_reject_same_version_and_unexpected_plugins(self):
        bad=self.previous()
        bad["version"]=self.plugin["version"]
        with self.assertRaisesRegex(ValueError,"strictly newer"):
            prepare_legacy(bad,self.plugin)
        bad=self.previous()
        bad["mcpServers"]="different.json"
        with self.assertRaisesRegex(ValueError,"Unexpected"):
            prepare_legacy(bad,self.plugin)
        bad=self.previous()
        bad["apps"]=[{"app":"private"}]
        with self.assertRaisesRegex(ValueError,"App-backed"):
            prepare_legacy(bad,self.plugin)
        bad=self.previous()
        bad["name"]="other"
        with self.assertRaisesRegex(ValueError,"identity"):
            prepare_legacy(bad,self.plugin)

    def test_archive_has_complete_branding_and_is_reproducible(self):
        with tempfile.TemporaryDirectory() as folder:
            root=Path(folder)
            old=root/"existing.json"
            old.write_text(json.dumps(self.previous()))
            first,second=root/"first.zip",root/"second.zip"
            self.assertEqual(build_account_overlay(old,first),build_account_overlay(old,second))
            self.assertEqual(first.read_bytes(),second.read_bytes())
            with ZipFile(first) as z:
                names=z.namelist()
                self.assertIn(".codex-plugin/plugin.json",names)
                self.assertIn("plugin.json",names)
                self.assertIn("assets/docsy-icon-192.png",names)
                self.assertIn("assets/docsy-logo-512.png",names)
                self.assertIn("assets/docsy-logo-dark-512.png",names)
                self.assertNotIn(".mcp.json",names)
                updated=json.loads(z.read(".codex-plugin/plugin.json"))
                self.assertEqual(updated["version"],self.plugin["version"])
                for path in ("assets/docsy-icon-192.png","assets/docsy-logo-512.png","assets/docsy-logo-dark-512.png"):
                    self.assertTrue(z.read(path).startswith(b"\x89PNG\r\n\x1a\n"))


if __name__=="__main__":
    unittest.main()
