"""Tests for change-level synchronization and append-only checks."""

from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest


SOURCE = Path(__file__).resolve().parent.parent
LOG = "00-admin-and-strategy/agent-audit-log.md"
MANIFEST = "03-evidence-and-exhibits/checksums.sha256"
INDEX = "02-discovery/_index.md"


class ChangeAuditTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        shutil.copytree(SOURCE / "scripts", self.root / "scripts", ignore=shutil.ignore_patterns("__pycache__"))
        self.git("init", "-q")
        self.git("config", "user.name", "Test")
        self.git("config", "user.email", "test@example.invalid")
        self.write(LOG, "---\nlast_updated: 2024-01-01\n---\n# Log\nold entry\n")
        self.write(MANIFEST, "# manifest\nold checksum\n")
        self.write("03-evidence-and-exhibits/_index.md", "old index\n")
        self.write(INDEX, "old index\n")
        self.git("add", ".")
        self.git("commit", "-qm", "base")
        self.base = self.git("rev-parse", "HEAD").strip()

    def git(self, *args):
        return subprocess.run(
            ["git", "-C", str(self.root), *args], check=True, text=True,
            stdout=subprocess.PIPE, stderr=subprocess.PIPE,
        ).stdout

    def write(self, name, text):
        path = self.root / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")

    def audit(self):
        self.git("add", "-A")
        self.git("commit", "-qm", "change")
        return subprocess.run(
            [sys.executable, str(self.root / "scripts/audit_changes.py"), "--base", self.base, "--head", "HEAD"],
            text=True, capture_output=True, check=False,
        )

    def test_requires_index_and_audit_entry_for_record_change(self):
        self.write("02-discovery/new.txt", "record")
        result = self.audit()
        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        self.assertIn("changes require an updated _index.md", result.stderr)
        self.assertIn("require an appended audit entry", result.stderr)

    def test_accepts_append_and_frontmatter_update(self):
        self.write("02-discovery/new.txt", "record")
        self.write(INDEX, "new index\n")
        self.write(LOG, "---\nlast_updated: 2024-02-01\n---\n# Log\nold entry\nnew entry\n")
        result = self.audit()
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_rejects_rewritten_manifest_and_audit_history(self):
        self.write(MANIFEST, "# manifest\nreplacement checksum\n")
        self.write(LOG, "---\nlast_updated: 2024-02-01\n---\n# Log\nreplacement entry\n")
        self.write("03-evidence-and-exhibits/_index.md", "updated")
        result = self.audit()
        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        self.assertIn(f"{MANIFEST}: existing content must be preserved", result.stderr)
        self.assertIn(f"{LOG}: existing content must be preserved", result.stderr)

    def test_metadata_only_log_update_is_not_an_entry(self):
        self.write(INDEX, "new index\n")
        self.write(LOG, "---\nlast_updated: 2024-02-01\n---\n# Log\nold entry\n")
        result = self.audit()
        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        self.assertIn("require an appended audit entry", result.stderr)

    def test_missing_revision_is_reported(self):
        result = subprocess.run(
            [sys.executable, str(self.root / "scripts/audit_changes.py"), "--base", "missing", "--head", "HEAD"],
            text=True, capture_output=True, check=False,
        )
        self.assertEqual(result.returncode, 1)
        self.assertIn("cannot audit changes", result.stderr)

    def test_initial_push_against_empty_tree(self):
        empty = subprocess.run(
            ["git", "-C", str(self.root), "hash-object", "-t", "tree", "--stdin"],
            input="", text=True, capture_output=True, check=True,
        ).stdout.strip()
        result = subprocess.run(
            [sys.executable, str(self.root / "scripts/audit_changes.py"), "--base", empty, "--head", "HEAD"],
            text=True, capture_output=True, check=False,
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)


if __name__ == "__main__":
    unittest.main()
