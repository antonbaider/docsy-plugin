"""Keep OpenAI's original Docsy draft compatible without changing release ZIPs."""
import json
from pathlib import Path
import sys
import tempfile
import unittest
from zipfile import ZipFile

sys.path.insert(0, str(Path(__file__).parent))
from package import FILES, SERVER, build
from platform_legacy_overlay import LEGACY_URL, build_legacy_portal_update


class ExistingPlatformUpdateTests(unittest.TestCase):
    def test_preserves_all_files_except_legacy_mcp_url(self):
        with tempfile.TemporaryDirectory() as folder:
            base = Path(folder)
            source, portal = base / "release.zip", base / "platform.zip"
            build(source)
            build_legacy_portal_update(source, portal)
            with ZipFile(source) as a, ZipFile(portal) as b:
                self.assertEqual(sorted(a.namelist()), sorted(FILES))
                self.assertEqual(sorted(b.namelist()), sorted(FILES))
                self.assertEqual(json.loads(a.read("mcp.json"))["mcpServers"]["docsy"]["url"], SERVER)
                self.assertEqual(json.loads(b.read("mcp.json"))["mcpServers"]["docsy"]["url"], LEGACY_URL)
                for name in FILES:
                    if name != "mcp.json":
                        self.assertEqual(a.read(name), b.read(name), name)
                self.assertEqual(b.testzip(), None)
            self.assertTrue(source.is_file())

    def test_rebuild_is_deterministic_and_refuses_double_overlay(self):
        with tempfile.TemporaryDirectory() as folder:
            base = Path(folder)
            release = base / "release.zip"
            out1, out2 = base / "one.zip", base / "two.zip"
            build(release)
            self.assertEqual(build_legacy_portal_update(release, out1),
                             build_legacy_portal_update(release, out2))
            self.assertEqual(out1.read_bytes(), out2.read_bytes())
            with self.assertRaisesRegex(ValueError, "canonical"):
                build_legacy_portal_update(out1, base / "bad.zip")
            with self.assertRaisesRegex(ValueError, "differ"):
                build_legacy_portal_update(release, release)


if __name__ == "__main__":
    unittest.main()
