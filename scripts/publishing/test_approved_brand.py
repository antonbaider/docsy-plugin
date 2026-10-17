from hashlib import sha256
from pathlib import Path
import unittest

ROOT=Path(__file__).resolve().parents[2]

# Immutable source image hashes from Docsy Brand Kit 2026. All are exact
# approved PNGs; release packaging must not silently substitute a second logo.
ASSETS={
    "assets/docsy-icon-192.png":"886202fc3e31132696662c66294723e60299db2bdf9fc20df3a235198f41c729",
    "assets/docsy-logo-512.png":"2ca68715e0694bf0fad9c90704d4b6daffe3935b6b11c15f6c15e3269b5bd527",
    "assets/docsy-logo-dark-512.png":"7db3e3eaa227901e98f52114f6a32a07780547e606a54506989afdae60adfffc",
}
class BrandIntegrityTests(unittest.TestCase):
    def test_approved_chatgpt_brand_images(self):
        for name,expected in ASSETS.items():
            with self.subTest(name=name):
                file=ROOT/name
                self.assertTrue(file.is_file())
                self.assertEqual(sha256(file.read_bytes()).hexdigest(),expected)
                self.assertTrue(file.read_bytes().startswith(bytes.fromhex("89504e470d0a1a0a")))
