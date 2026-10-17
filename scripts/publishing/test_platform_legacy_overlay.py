"""Keep OpenAI's original Docsy draft compatible without changing release ZIPs."""
import json
import hashlib
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

    def test_historical_releases_require_pinned_version_and_digest(self):
        with tempfile.TemporaryDirectory() as folder:
            base = Path(folder)
            source, legacy = base / "old-release.zip", base / "review.zip"
            build(source)
            with ZipFile(source) as zip_file:
                payload = {name: zip_file.read(name) for name in FILES}
            manifest = json.loads(payload["plugin.json"])
            manifest["version"] = "1.0.8"
            payload["plugin.json"] = (json.dumps(manifest) + "\n").encode()
            with ZipFile(source, "w") as zip_file:
                for name in sorted(payload):
                    zip_file.writestr(name, payload[name])
            digest = hashlib.sha256(source.read_bytes()).hexdigest()
            with self.assertRaisesRegex(ValueError, "pinned SHA-256"):
                build_legacy_portal_update(source, legacy, expected_version="1.0.8")
            with self.assertRaisesRegex(ValueError, "does not match"):
                build_legacy_portal_update(source, legacy, expected_version="1.0.8",
                                           expected_sha256="0" * 64)
            with self.assertRaisesRegex(ValueError, "strict semver"):
                build_legacy_portal_update(source, legacy, expected_version="../old",
                                           expected_sha256=digest)
            build_legacy_portal_update(source, legacy, expected_version="1.0.8",
                                       expected_sha256=digest)
            with ZipFile(legacy) as archive:
                self.assertEqual(json.loads(archive.read("plugin.json"))["version"], "1.0.8")
                self.assertEqual(json.loads(archive.read("mcp.json"))["mcpServers"]["docsy"]["url"], LEGACY_URL)

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
