"""Focused tests for the record audit and append-only hashing utility."""

import hashlib
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
from urllib.parse import quote


SOURCE = Path(__file__).resolve().parent.parent
FOLDERS = (
    "01-pleadings-and-motions",
    "02-discovery",
    "03-evidence-and-exhibits",
    "04-chronology-and-facts",
    "05-correspondence",
)
FRONTMATTER = """---
doc_type: witness
status: draft
privilege: work_product
last_updated: 2024-02-29
updated_by: tester
verified_against_record: false
---
# Record
"""


class AuditTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        shutil.copytree(SOURCE / "scripts", self.root / "scripts", ignore=shutil.ignore_patterns("__pycache__"))
        for folder in FOLDERS:
            path = self.root / folder
            path.mkdir()
            (path / "_index.md").write_text(
                FRONTMATTER + f"\n| Record ID | File |\n| --- | --- |\n"
                f"| Index-{folder} | [_index.md](_index.md) |\n", encoding="utf-8"
            )
        (self.root / "00-admin-and-strategy").mkdir()
        (self.root / "01-pleadings-and-motions/drafts").mkdir()
        (self.root / "03-evidence-and-exhibits/raw").mkdir()
        (self.root / "03-evidence-and-exhibits/checksums.sha256").write_text(
            "# checksums\n", encoding="utf-8"
        )
        self.index("03-evidence-and-exhibits", "checksums.sha256")

    def index(self, folder, name, record_id=None):
        index = self.root / folder / "_index.md"
        record_id = record_id or f"{folder}-{len(index.read_text().splitlines())}"
        with (self.root / folder / "_index.md").open("a", encoding="utf-8") as stream:
            stream.write(f"| {record_id} | [{Path(name).name}]({quote(name)}) |\n")

    def run_script(self, name):
        return subprocess.run(
            [sys.executable, str(self.root / "scripts" / name)],
            text=True,
            capture_output=True,
            check=False,
        )

    def test_baseline_and_required_frontmatter_validation(self):
        doc = self.root / "01-pleadings-and-motions/drafts/DRAFT_record.md"
        doc.write_text(FRONTMATTER, encoding="utf-8")
        self.index("01-pleadings-and-motions", "drafts/" + doc.name)
        self.assertEqual(self.run_script("audit_repo.py").returncode, 0)
        for old, new in (
            ("status: draft", "status: invalid"),
            ("last_updated: 2024-02-29", "last_updated: 2023-02-29"),
            ("verified_against_record: false", "verified_against_record: 'false'"),
            ("updated_by: tester", "updated_by: invalid:"),
            ("updated_by: tester", "updated_by: null"),
            ("doc_type: witness", "doc_type: witness\ndoc_type: witness"),
            ("doc_type: witness\n", ""),
        ):
            with self.subTest(new=new):
                doc.write_text(FRONTMATTER.replace(old, new), encoding="utf-8")
                result = self.run_script("audit_repo.py")
                self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
                self.assertIn("DRAFT_record.md", result.stderr)

    def test_index_requires_full_filename_and_includes_nested_files(self):
        doc = self.root / "02-discovery/nested/record.txt"
        doc.parent.mkdir()
        doc.write_text("test", encoding="utf-8")
        with (self.root / "02-discovery/_index.md").open("a") as stream:
            stream.write("<!-- record.txt not indexed yet -->\n")
        result = self.run_script("audit_repo.py")
        self.assertEqual(result.returncode, 1)
        self.assertIn("file missing", result.stderr)
        self.index("02-discovery", "nested/" + doc.name)
        self.assertEqual(self.run_script("audit_repo.py").returncode, 0)

    def test_index_rejects_broken_links_duplicate_ids_and_duplicate_basenames(self):
        first = self.root / "02-discovery/a/record.txt"
        second = self.root / "02-discovery/b/record.txt"
        for path in (first, second):
            path.parent.mkdir()
            path.write_text("test", encoding="utf-8")
        self.index("02-discovery", "a/record.txt", "Shared-ID")
        self.index("02-discovery", "missing/record.txt", "shared-id")
        result = self.run_script("audit_repo.py")
        self.assertEqual(result.returncode, 1)
        self.assertIn("duplicate record ID", result.stderr)
        self.assertIn("file link is missing", result.stderr)
        self.assertIn("b/record.txt: file missing", result.stderr)

    def test_index_rejects_external_and_duplicate_file_links(self):
        self.index("02-discovery", "../03-evidence-and-exhibits/checksums.sha256")
        self.index("02-discovery", "_index.md")
        result = self.run_script("audit_repo.py")
        self.assertEqual(result.returncode, 1)
        self.assertIn("outside its folder", result.stderr)
        self.assertIn("file indexed more than once", result.stderr)

    def test_synthetic_intake_can_be_hashed_and_indexed(self):
        raw = self.root / "03-evidence-and-exhibits/raw/2025-02-03_note_delivery.txt"
        raw.write_text("The blue widget was delivered on 2025-02-03.\n", encoding="utf-8")
        self.index("03-evidence-and-exhibits", "raw/" + raw.name, "Ex-001")
        timeline = self.root / "04-chronology-and-facts/master-timeline.md"
        timeline.write_text(
            FRONTMATTER.replace("doc_type: witness", "doc_type: timeline")
            + "\nThe note states delivery on 2025-02-03. [Ex-001, line 1]\n",
            encoding="utf-8",
        )
        self.index("04-chronology-and-facts", timeline.name, "Timeline-01")
        result = self.run_script("hash_raw.py")
        self.assertEqual(result.returncode, 0, result.stderr)
        result = self.run_script("audit_repo.py")
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_hash_append_is_idempotent_and_detects_tampering(self):
        raw = self.root / "03-evidence-and-exhibits/raw"
        manifest = self.root / "03-evidence-and-exhibits/checksums.sha256"
        first = raw / "first file.txt"
        first.write_bytes(b"first")
        self.index("03-evidence-and-exhibits", "raw/" + first.name)
        self.assertEqual(self.run_script("audit_repo.py").returncode, 1)
        self.assertEqual(self.run_script("hash_raw.py").returncode, 0)
        original = manifest.read_bytes()
        self.assertIn(hashlib.sha256(b"first").hexdigest().encode(), original)
        nested = raw / "nested/second.txt"
        nested.parent.mkdir()
        nested.write_bytes(b"second")
        self.index("03-evidence-and-exhibits", "raw/nested/" + nested.name)
        self.assertEqual(self.run_script("hash_raw.py").returncode, 0)
        extended = manifest.read_bytes()
        self.assertTrue(extended.startswith(original))
        self.assertEqual(self.run_script("hash_raw.py").returncode, 0)
        self.assertEqual(manifest.read_bytes(), extended)
        self.assertEqual(self.run_script("audit_repo.py").returncode, 0)
        first.write_bytes(b"tampered")
        self.assertIn("SHA-256 mismatch", self.run_script("audit_repo.py").stderr)
        result = self.run_script("hash_raw.py")
        self.assertEqual(result.returncode, 1)
        self.assertIn("refusing to overwrite", result.stderr)
        self.assertEqual(manifest.read_bytes(), extended)
        first.unlink()
        self.assertIn("entry has no raw file", self.run_script("audit_repo.py").stderr)

    def test_malformed_duplicate_and_missing_manifest_entries_fail(self):
        manifest = self.root / "03-evidence-and-exhibits/checksums.sha256"
        for content in (
            "not a checksum\n",
            "0" * 64 + "  ../outside\n",
            ("0" * 64 + "  absent\n") * 2,
            "0" * 64 + "  absent\n",
        ):
            with self.subTest(content=content):
                manifest.write_text(content, encoding="utf-8")
                self.assertEqual(self.run_script("audit_repo.py").returncode, 1)
                self.assertEqual(self.run_script("hash_raw.py").returncode, 1)
                self.assertEqual(manifest.read_text(encoding="utf-8"), content)

    def test_symlink_cannot_escape_record(self):
        raw = self.root / "03-evidence-and-exhibits/raw"
        (raw / "external").symlink_to(self.root / "02-discovery", target_is_directory=True)
        self.assertIn("symlink", self.run_script("audit_repo.py").stderr)
        self.assertIn("symlink", self.run_script("hash_raw.py").stderr)

    def test_lfs_pointer_cannot_be_hashed_as_evidence(self):
        raw_file = self.root / "03-evidence-and-exhibits/raw/original.pdf"
        raw_file.write_text(
            "version https://git-lfs.github.com/spec/v1\n"
            + "oid sha256:" + "a" * 64 + "\nsize 100\n",
            encoding="utf-8",
        )
        self.index("03-evidence-and-exhibits", "raw/" + raw_file.name)
        result = self.run_script("hash_raw.py")
        self.assertEqual(result.returncode, 1)
        self.assertIn("Git LFS pointer", result.stderr)

    def test_hash_manifest_symlink_is_rejected(self):
        manifest = self.root / "03-evidence-and-exhibits/checksums.sha256"
        target = self.root / "outside.sha256"
        target.write_text("# outside\n", encoding="utf-8")
        manifest.unlink()
        manifest.symlink_to(target)
        self.assertIn("symlinks are not allowed", self.run_script("audit_repo.py").stderr)
        self.assertIn("symlinks are not allowed", self.run_script("hash_raw.py").stderr)
        self.assertEqual(target.read_text(encoding="utf-8"), "# outside\n")


if __name__ == "__main__":
    unittest.main()
