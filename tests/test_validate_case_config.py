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

    def test_malformed_verification_status_reports_error(self):
        path = self.root / "case-config.yaml"
        path.write_text(path.read_text().replace("status: not_reviewed", "status: []"))
        result = self.run_validator()
        self.assertEqual(result.returncode, 1)
        self.assertIn("verification.status must be", result.stderr)
        self.assertNotIn("Traceback", result.stderr)

    def test_disabled_controls_are_explicitly_reported(self):
        path = self.root / "case-config.yaml"
        path.write_text(path.read_text().replace("human_review_required: true", "human_review_required: false"))
        result = self.run_validator()
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("WARNING: operating_controls.human_review_required is disabled", result.stderr)

    def test_rejects_invalid_operating_controls(self):
        path = self.root / "case-config.yaml"
        path.write_text(path.read_text().replace("filing_approval_required: true", "filing_approval_required: []"))
        result = self.run_validator()
        self.assertEqual(result.returncode, 1)
        self.assertIn("filing_approval_required must be a boolean", result.stderr)

    def test_verified_review_date_must_be_a_calendar_date(self):
        path = self.root / "case-config.yaml"
        path.write_text(path.read_text().replace(
            "configuration_status: unconfigured", "configuration_status: verified"
        ).replace("last_reviewed: null", "last_reviewed: 'not-a-date'"))
        result = self.run_validator()
        self.assertEqual(result.returncode, 1)
        self.assertIn("verification.last_reviewed must be a valid ISO date", result.stderr)

    def test_accepts_valid_unquoted_yaml_review_date(self):
        path = self.root / "case-config.yaml"
        text = path.read_text()
        for old, new in (
            ("configuration_status: unconfigured", "configuration_status: verified"),
            ("title: null", "title: Example"),
            ("case_number: null", "case_number: '123'"),
            ("country: null", "country: Example"),
            ("state_or_province: null", "state_or_province: Example"),
            ("county_or_district: null", "county_or_district: Example"),
            ("name: null", "name: Example"),
            ("status: not_reviewed", "status: verified"),
            ("reviewed_by: null", "reviewed_by: Reviewer"),
            ("last_reviewed: null", "last_reviewed: 2024-02-29"),
        ):
            text = text.replace(old, new)
        path.write_text(text)
        result = self.run_validator()
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_rejects_duplicate_yaml_keys(self):
        path = self.root / "case-config.yaml"
        path.write_text(path.read_text() + "\nconfiguration_status: verified\n")
        result = self.run_validator()
        self.assertEqual(result.returncode, 1)
        self.assertIn("duplicate key", result.stderr)

    def test_invalid_unquoted_yaml_date_reports_error(self):
        path = self.root / "case-config.yaml"
        path.write_text(path.read_text().replace("last_reviewed: null", "last_reviewed: 2024-02-31"))
        result = self.run_validator()
        self.assertEqual(result.returncode, 1)
        self.assertIn("invalid case-config.yaml", result.stderr)
        self.assertNotIn("Traceback", result.stderr)


if __name__ == "__main__":
    unittest.main()
