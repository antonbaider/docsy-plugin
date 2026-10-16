"""Prevent oversized handwritten source files in the publicly distributed plugin."""

from pathlib import Path
import subprocess
import unittest

ROOT = Path(__file__).resolve().parents[2]
MAX_LINES = 500
SOURCE_SUFFIXES = {".py", ".mjs", ".js", ".ts", ".tsx", ".css", ".json", ".yaml", ".yml"}


class SourceBudgetTests(unittest.TestCase):
    def test_tracked_source_files_do_not_exceed_500_lines(self):
        tracked = subprocess.check_output(
            ["git", "-C", str(ROOT), "ls-files", "-z"]
        ).decode("utf-8").split("\0")
        oversize = []
        for relative in tracked:
            if not relative:
                continue
            path = ROOT / relative
            if path.suffix not in SOURCE_SUFFIXES:
                continue
            # Never split auto-generated lockfiles by hand.
            if path.name in {"package-lock.json", "pnpm-lock.yaml", "yarn.lock"}:
                continue
            lines = len(path.read_text(encoding="utf-8").splitlines())
            if lines > MAX_LINES:
                oversize.append(f"{relative}: {lines} lines")
        self.assertEqual(
            oversize, [],
            "Break up large modules or schemas before publishing: "
            + ", ".join(oversize),
        )


if __name__ == "__main__":
    unittest.main()
