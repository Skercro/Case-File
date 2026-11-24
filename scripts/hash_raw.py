#!/usr/bin/env python3
"""Append SHA-256 entries for new raw files without changing existing entries."""

import sys

from audit_repo import ROOT, digest_file, files_below, read_checksums


def main():
    raw = ROOT / "03-evidence-and-exhibits/raw"
    manifest = ROOT / "03-evidence-and-exhibits/checksums.sha256"
    errors = []
    entries = read_checksums(manifest, errors)
    if not raw.is_dir() or raw.is_symlink() or raw.parent.is_symlink():
        errors.append("03-evidence-and-exhibits/raw: required real directory is missing")
    additions = []
    found = set()
    if not errors:
        for path in files_below(raw):
            name = path.relative_to(raw).as_posix()
            if path.is_symlink() or "\n" in name or "\r" in name or "\\" in name:
                errors.append(f"{path.relative_to(ROOT)}: symlink or unsupported filename")
                continue
            found.add(name)
            try:
                digest = digest_file(path)
            except OSError as exc:
                errors.append(f"{path.relative_to(ROOT)}: cannot hash file: {exc}")
                continue
            if name in entries and entries[name] != digest:
                errors.append(f"{path.relative_to(ROOT)}: existing SHA-256 mismatch; refusing to overwrite")
            elif name not in entries:
                additions.append((name, digest))
        for name in sorted(entries.keys() - found):
            errors.append(f"{manifest.relative_to(ROOT)}: entry has no raw file: {name}")
    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        return 1
    if additions:
        try:
            # Ensure a pre-existing unterminated line is never silently joined.
            with manifest.open("rb") as stream:
                stream.seek(0, 2)
                if stream.tell():
                    stream.seek(-1, 2)
                    if stream.read(1) != b"\n":
                        raise ValueError("checksum manifest must end with a newline")
            with manifest.open("a", encoding="utf-8", newline="\n") as stream:
                for name, digest in additions:
                    stream.write(f"{digest}  {name}\n")
        except (OSError, ValueError) as exc:
            print(f"ERROR: cannot append checksum entries: {exc}", file=sys.stderr)
            return 1
    print(f"Added {len(additions)} SHA-256 entr{'y' if len(additions) == 1 else 'ies'}.")
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except OSError as exc:
        print(f"ERROR: cannot traverse raw files: {exc}", file=sys.stderr)
        sys.exit(1)
