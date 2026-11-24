"""Tests for the civil case configuration validator."""

from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest


SOURCE = Path(__file__).resolve().parent.parent


class CaseConfigValidatorTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        shutil.copytree(SOURCE / "scripts", self.root / "scripts")
        shutil.copy(SOURCE / "requirements-dev.txt", self.root / "requirements-dev.txt")
        shutil.copy(SOURCE / "case-config.yaml", self.root / "case-config.yaml")

    def run_validator(self):
        return subprocess.run(
            [sys.executable, str(self.root / "scripts" / "validate_case_config.py")],
            cwd=self.root,
            text=True,
            capture_output=True,
            check=False,
        )

    def test_template_configuration_is_valid_and_unconfigured(self):
        result = self.run_validator()
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("status: unconfigured", result.stdout)
        self.assertIn("not verified", result.stdout)

    def test_rejects_non_civil_case_type(self):
        path = self.root / "case-config.yaml"
        path.write_text(path.read_text().replace("matter_type: civil", "matter_type: criminal"))
        result = self.run_validator()
        self.assertEqual(result.returncode, 1)
        self.assertIn("matter_type must be 'civil'", result.stderr)

    def test_rejects_duplicate_party_ids(self):
        path = self.root / "case-config.yaml"
        path.write_text(path.read_text().replace(
            "parties: []",
            "parties:\n  - id: party_001\n  - id: party_001",
        ))
        result = self.run_validator()
        self.assertEqual(result.returncode, 1)
        self.assertIn("duplicate party id", result.stderr)

    def test_verified_configuration_requires_human_review_fields(self):
        path = self.root / "case-config.yaml"
        path.write_text(path.read_text().replace(
            "configuration_status: unconfigured",
            "configuration_status: verified",
        ))
        result = self.run_validator()
        self.assertEqual(result.returncode, 1)
        self.assertIn("case.title is required", result.stderr)
        self.assertIn("verification.status must be 'verified'", result.stderr)

    def test_rejects_invalid_yaml(self):
        (self.root / "case-config.yaml").write_text("case: [not valid")
        result = self.run_validator()
        self.assertEqual(result.returncode, 1)
        self.assertIn("invalid case-config.yaml", result.stderr)


if __name__ == "__main__":
    unittest.main()
