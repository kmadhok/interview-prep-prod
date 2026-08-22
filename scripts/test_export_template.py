#!/usr/bin/env python3
"""Optional developer self-test for the clean template exporter."""
from __future__ import annotations

import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

from export_template import REQUIRED_EXPORT_FILES, check_required_files, export_template


class ExportTemplateTest(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary_directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary_directory.cleanup)
        self.temp_root = Path(self.temporary_directory.name)
        self.export = export_template(self.temp_root / "export", force=True)

    def test_required_files_exist(self) -> None:
        for relative in REQUIRED_EXPORT_FILES:
            with self.subTest(relative=relative):
                self.assertTrue((self.export / relative).is_file())

    def test_required_files_pass_validation(self) -> None:
        self.assertEqual(check_required_files(self.export), [])

    def test_fixture_profiles_are_not_ignored(self) -> None:
        if shutil.which("git") is None:
            self.skipTest("git is not available")

        git_dir = self.temp_root / "git-dir"
        subprocess.run(
            [
                "git",
                "--git-dir",
                str(git_dir),
                "--work-tree",
                str(self.export),
                "init",
                "-q",
            ],
            check=True,
        )
        for relative in ("templates/profile.yaml", "evals/fixtures/profile.yaml"):
            with self.subTest(relative=relative):
                result = subprocess.run(
                    [
                        "git",
                        "--git-dir",
                        str(git_dir),
                        "--work-tree",
                        str(self.export),
                        "check-ignore",
                        "-q",
                        relative,
                    ],
                    check=False,
                )
                self.assertEqual(result.returncode, 1)

    def test_export_contains_no_git_directory(self) -> None:
        self.assertFalse((self.export / ".git").exists())


if __name__ == "__main__":
    unittest.main()
