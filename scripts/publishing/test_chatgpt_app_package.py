"""Regression checks for the ChatGPT registered-app variant."""
import json
from pathlib import Path
import sys
import tempfile
import unittest
from zipfile import ZipFile

sys.path.insert(0, str(Path(__file__).parent))
from package_chatgpt_app import build_app_package

TEST_ID = "asdk_app_6accc712ce9081919cbd3a9ecc4d8755"


class ChatGPTAppPackageTests(unittest.TestCase):
    def test_app_binding_and_no_desktop_only_mcp_manifests(self):
        with tempfile.TemporaryDirectory() as temp:
            archive_path = Path(temp) / "docsy-app.zip"
            digest = build_app_package(archive_path, TEST_ID)
            self.assertEqual(len(digest), 64)
            with ZipFile(archive_path) as archive:
                names = set(archive.namelist())
                self.assertIn("plugin.json", names)
                self.assertIn(".app.json", names)
                self.assertIn("skills/find-docs/SKILL.md", names)
                self.assertNotIn("mcp.json", names)
                self.assertNotIn(".mcp.json", names)
                self.assertNotIn(".codex-plugin/plugin.json", names)
                plugin = json.loads(archive.read("plugin.json"))
                app = json.loads(archive.read(".app.json"))
                self.assertEqual(plugin["extensions"]["com.openai"]["apps"], "./.app.json")
                self.assertNotIn("review", plugin["extensions"]["com.openai"])
                self.assertNotIn("requires_local_executor", plugin["extensions"]["com.openai"])
                self.assertEqual(app["apps"]["docsy"], {"id": TEST_ID, "required": True})

    def test_determinism_and_reject_invalid_id(self):
        with tempfile.TemporaryDirectory() as temp:
            one, two = Path(temp) / "a.zip", Path(temp) / "b.zip"
            self.assertEqual(build_app_package(one, TEST_ID), build_app_package(two, TEST_ID))
            self.assertEqual(one.read_bytes(), two.read_bytes())
            with self.assertRaises(ValueError):
                build_app_package(one, "local_mcp_server")


if __name__ == "__main__":
    unittest.main()
