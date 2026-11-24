#!/usr/bin/env python3
"""Audit the case record using only the Python standard library."""

import hashlib
import os
from pathlib import Path
import re
import sys
from urllib.parse import unquote, urlsplit

ROOT = Path(__file__).resolve().parent.parent
NUMBERED = (
    "01-pleadings-and-motions",
    "02-discovery",
    "03-evidence-and-exhibits",
    "04-chronology-and-facts",
    "05-correspondence",
)
FRONTMATTER_DIRS = (
    "00-admin-and-strategy",
    "01-pleadings-and-motions/drafts",
    "04-chronology-and-facts",
)
REQUIRED = {"doc_type", "status", "last_updated", "updated_by", "verified_against_record"}
DOC_TYPES = {
    "repository_guide", "inbox_guide", "folder_index", "task_queue",
    "case_summary", "theory_of_case", "procedural_history", "audit_log",
    "pleading_draft", "legal_memo", "exhibit_sheet", "privilege_log", "authority_register",
    "timeline", "contradictions_log", "witness",
}
STATUSES = {"draft", "in_review", "verified", "filed", "superseded"}
PRIVILEGES = {"none", "attorney_client", "work_product", "confidential"}
HASH_LINE = re.compile(r"^([0-9a-f]{64})  (.+)$")


def files_below(directory):
    """Yield files without following symlinks; report symlinks separately."""
    def raise_walk_error(error):
        raise error

    for current, dirs, files in os.walk(directory, followlinks=False, onerror=raise_walk_error):
        dirs.sort()
        files.sort()
        for name in dirs + files:
            path = Path(current) / name
            if path.is_symlink():
                yield path
            elif name in files:
                yield path


def parse_scalar(raw):
    """Parse the documented single-line YAML scalar subset."""
    raw = raw.strip()
    if not raw:
        raise ValueError("empty value")
    if any(ord(c) < 32 and c != "\t" or ord(c) in {127, 0xFFFE, 0xFFFF} for c in raw):
        raise ValueError("invalid YAML control character")
    if raw.startswith("'"):
        if not raw.endswith("'") or len(raw) < 2:
            raise ValueError("unterminated quoted scalar")
        inner = raw[1:-1]
        if "'" in inner.replace("''", ""):
            raise ValueError("invalid single-quoted scalar")
        return inner.replace("''", "'"), True
    if raw.startswith('"'):
        # Restrict double quotes to unescaped text, valid in both YAML and JSON.
        if len(raw) < 2 or not raw.endswith('"') or '"' in raw[1:-1] or "\\" in raw:
            raise ValueError("invalid double-quoted scalar")
        return raw[1:-1], True
    if (
        raw[0] in "-?:,[]{}#&*!|>'\"%@`"
        or ": " in raw
        or raw.endswith(":")
        or re.search(r"\s#", raw)
        or any(c in raw for c in "[]{}")
    ):
        raise ValueError("unsupported or invalid plain scalar")
    return raw, False


def audit_frontmatter(path, errors):
    label = path.relative_to(ROOT).as_posix()
    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except (OSError, UnicodeError) as exc:
        errors.append(f"{label}: cannot read UTF-8: {exc}")
        return
    if not lines or lines[0] != "---":
        errors.append(f"{label}: missing opening YAML frontmatter delimiter")
        return
    try:
        end = lines.index("---", 1)
    except ValueError:
        errors.append(f"{label}: missing closing YAML frontmatter delimiter")
        return
    values = {}
    invalid = False
    for line in lines[1:end]:
        if not line.strip() or line.startswith("#"):
            continue
        match = re.fullmatch(r"([a-z][a-z0-9_]*):[ \t]+(.*)", line)
        if not match:
            errors.append(f"{label}: invalid frontmatter line: {line!r}")
            invalid = True
            continue
        key, raw = match.groups()
        if key in values:
            errors.append(f"{label}: duplicate frontmatter key: {key}")
            invalid = True
            continue
        try:
            values[key] = parse_scalar(raw)
        except ValueError as exc:
            errors.append(f"{label}: {key}: {exc}")
            invalid = True
    missing = REQUIRED - values.keys()
    if missing:
        errors.append(f"{label}: missing required keys: {', '.join(sorted(missing))}")
    if invalid or missing:
        return
    if values["doc_type"][0] not in DOC_TYPES:
        errors.append(f"{label}: invalid doc_type: {values['doc_type'][0]}")
    if values["status"][0] not in STATUSES:
        errors.append(f"{label}: invalid status: {values['status'][0]}")
    if "privilege" in values and values["privilege"][0] not in PRIVILEGES:
        errors.append(f"{label}: invalid privilege: {values['privilege'][0]}")
    date, _ = values["last_updated"]
    if not re.fullmatch(r"[0-9]{4}-[0-9]{2}-[0-9]{2}", date):
        errors.append(f"{label}: last_updated must be YYYY-MM-DD")
    else:
        # datetime is intentionally not required by the restricted import policy.
        year, month, day = map(int, date.split("-"))
        leap = year % 4 == 0 and (year % 100 != 0 or year % 400 == 0)
        lengths = (31, 29 if leap else 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31)
        if year < 1 or not 1 <= month <= 12 or not 1 <= day <= lengths[month - 1]:
            errors.append(f"{label}: last_updated is not a calendar date: {date}")
    updated_by, quoted = values["updated_by"]
    if not updated_by.strip():
        errors.append(f"{label}: updated_by must not be empty")
    elif not quoted and (
        updated_by.lower() in {"null", "true", "false", "~"}
        or re.fullmatch(r"[+-]?(?:\d[\d_]*)(?:\.[\d_]*)?(?:[eE][+-]?\d+)?", updated_by)
        or re.fullmatch(r"\d{4}-\d{2}-\d{2}", updated_by)
    ):
        errors.append(f"{label}: updated_by must be a YAML string")
    verified, quoted = values["verified_against_record"]
    if quoted or verified not in {"true", "false"}:
        errors.append(f"{label}: verified_against_record must be a YAML boolean (true or false)")


def read_checksums(manifest, errors):
    entries = {}
    if manifest.is_symlink() or manifest.parent.is_symlink():
        errors.append(f"{manifest.relative_to(ROOT)}: symlinks are not allowed")
        return entries
    try:
        lines = manifest.read_text(encoding="utf-8").splitlines()
    except (OSError, UnicodeError) as exc:
        errors.append(f"{manifest.relative_to(ROOT)}: cannot read checksum manifest: {exc}")
        return entries
    for number, line in enumerate(lines, 1):
        if not line or line.startswith("#"):
            continue
        match = HASH_LINE.fullmatch(line)
        if not match:
            errors.append(f"{manifest.relative_to(ROOT)}:{number}: invalid checksum entry")
            continue
        digest, name = match.groups()
        parts = name.split("/")
        if name.startswith("/") or "\\" in name or any(part in {"", ".", ".."} for part in parts):
            errors.append(f"{manifest.relative_to(ROOT)}:{number}: invalid raw-relative path: {name!r}")
        elif name in entries:
            errors.append(f"{manifest.relative_to(ROOT)}:{number}: duplicate checksum entry: {name}")
        else:
            entries[name] = digest
    return entries


def digest_file(path):
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        prefix = stream.read(1024)
        if re.fullmatch(
            rb"version https://git-lfs\.github\.com/spec/v1\r?\n"
            rb"oid sha256:[0-9a-f]{64}\r?\nsize [0-9]+\r?\n",
            prefix,
        ):
            raise OSError("Git LFS pointer found instead of file content; fetch LFS objects")
        stream.seek(0)
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def audit_index(directory, ids, errors):
    index = directory / "_index.md"
    label = index.relative_to(ROOT).as_posix()
    try:
        text = index.read_text(encoding="utf-8")
    except (OSError, UnicodeError) as exc:
        errors.append(f"{label}: cannot read index: {exc}")
        return
    text = re.sub(
        r"<!--.*?-->", lambda match: "\n" * match.group().count("\n"),
        text, flags=re.DOTALL,
    )
    indexed = set()
    for number, line in enumerate(text.splitlines(), 1):
        if not line.strip().startswith("|"):
            continue
        columns = [column.strip() for column in line.strip().strip("|").split("|")]
        if len(columns) < 2:
            errors.append(f"{label}:{number}: index row needs a record ID and file link")
            continue
        record_id, link = columns[:2]
        if record_id == "Record ID" and link == "File":
            continue
        if all(re.fullmatch(r":?-{3,}:?", column) for column in columns):
            continue
        if not record_id:
            errors.append(f"{label}:{number}: record ID must not be empty")
        elif record_id.casefold() in ids:
            errors.append(f"{label}:{number}: duplicate record ID {record_id!r} (also in {ids[record_id.casefold()]})")
        else:
            ids[record_id.casefold()] = f"{label}:{number}"
        match = re.fullmatch(r"\[([^\]]+)\]\(([^)]+)\)", link)
        if not match:
            errors.append(f"{label}:{number}: file must be a Markdown relative link")
            continue
        link_label, target = match.groups()
        try:
            parsed = urlsplit(target)
        except ValueError:
            errors.append(f"{label}:{number}: invalid file link: {target}")
            continue
        relative = unquote(parsed.path)
        if (parsed.scheme or parsed.netloc or parsed.query or parsed.fragment
                or not relative or relative.startswith("/") or "\\" in relative
                or any(ord(char) < 32 or ord(char) == 127 for char in relative)):
            errors.append(f"{label}:{number}: file link must be a relative path without query or fragment")
            continue
        path = (directory / relative).resolve()
        if not path.is_relative_to(directory.resolve()) or not path.is_file():
            errors.append(f"{label}:{number}: file link is missing or outside its folder: {target}")
            continue
        if link_label != path.name:
            errors.append(f"{label}:{number}: link text must be the exact filename: {path.name}")
        if path in indexed:
            errors.append(f"{label}:{number}: file indexed more than once: {target}")
        indexed.add(path)
    for path in files_below(directory):
        if path.is_symlink():
            errors.append(f"{path.relative_to(ROOT)}: symlinks are not allowed")
        elif path.name != ".gitkeep" and path.resolve() not in indexed:
            errors.append(f"{path.relative_to(ROOT)}: file missing from {label}")


def main():
    errors = []
    for relative in FRONTMATTER_DIRS:
        directory = ROOT / relative
        if not directory.is_dir() or directory.is_symlink():
            errors.append(f"{relative}: required real directory is missing")
            continue
        for path in files_below(directory):
            if path.is_symlink():
                errors.append(f"{path.relative_to(ROOT)}: symlinks are not allowed")
            elif path.suffix.lower() == ".md":
                audit_frontmatter(path, errors)

    ids = {}
    for relative in NUMBERED:
        directory = ROOT / relative
        if not directory.is_dir() or directory.is_symlink():
            errors.append(f"{relative}: required real directory is missing")
            continue
        audit_index(directory, ids, errors)

    raw = ROOT / "03-evidence-and-exhibits/raw"
    manifest = ROOT / "03-evidence-and-exhibits/checksums.sha256"
    entries = read_checksums(manifest, errors)
    found = set()
    if not raw.is_dir() or raw.is_symlink():
        errors.append("03-evidence-and-exhibits/raw: required real directory is missing")
    else:
        for path in files_below(raw):
            name = path.relative_to(raw).as_posix()
            if path.is_symlink():
                errors.append(f"{path.relative_to(ROOT)}: symlinks are not allowed in raw")
                continue
            if "\n" in name or "\r" in name or "\\" in name:
                errors.append(f"{path.relative_to(ROOT)!s}: unsupported raw filename")
                continue
            found.add(name)
            if name not in entries:
                errors.append(f"{path.relative_to(ROOT)}: missing SHA-256 entry")
                continue
            try:
                if digest_file(path) != entries[name]:
                    errors.append(f"{path.relative_to(ROOT)}: SHA-256 mismatch")
            except OSError as exc:
                errors.append(f"{path.relative_to(ROOT)}: cannot hash file: {exc}")
    for name in sorted(entries.keys() - found):
        errors.append(f"{manifest.relative_to(ROOT)}: entry has no raw file: {name}")
    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        return 1
    print("Repository audit passed.")
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except OSError as exc:
        print(f"ERROR: cannot traverse repository: {exc}", file=sys.stderr)
        sys.exit(1)
