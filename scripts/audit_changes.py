#!/usr/bin/env python3
"""Check index synchronization and append-only records between two Git revisions."""

import argparse
from pathlib import Path
import subprocess
import sys

from audit_repo import NUMBERED, ROOT

LOG = "00-admin-and-strategy/agent-audit-log.md"
MANIFEST = "03-evidence-and-exhibits/checksums.sha256"


def git(*args):
    return subprocess.run(
        ["git", "-C", str(ROOT), *args], check=True, stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    ).stdout


def content_at(revision, path):
    names = git("ls-tree", "-z", "--name-only", revision, "--", f":(literal){path}")
    if not names:
        return None
    return git("show", f"{revision}:{path}")


def log_body(content):
    if not content.startswith(b"---\n"):
        raise ValueError(f"{LOG}: missing frontmatter")
    _, delimiter, body = content[4:].partition(b"\n---\n")
    if not delimiter:
        raise ValueError(f"{LOG}: missing closing frontmatter delimiter")
    return body


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--base", required=True, help="Base Git commit or tree")
    parser.add_argument("--head", required=True, help="Head Git commit")
    args = parser.parse_args()
    try:
        changed = {
            path.decode("utf-8")
            for path in git("diff", "--no-renames", "--name-only", "-z", args.base, args.head, "--").split(b"\0")
            if path
        }
        errors = []
        affected = {folder for folder in NUMBERED if any(path.startswith(folder + "/") for path in changed)}
        for folder in sorted(affected):
            if f"{folder}/_index.md" not in changed:
                errors.append(f"{folder}: changes require an updated _index.md")
        for path in (MANIFEST, LOG):
            if path not in changed:
                continue
            before = content_at(args.base, path)
            after = content_at(args.head, path)
            if before is not None and after is None:
                errors.append(f"{path}: existing file must not be deleted")
            elif before is not None:
                old = log_body(before) if path == LOG else before
                new = log_body(after) if path == LOG else after
                if not new.startswith(old):
                    errors.append(f"{path}: existing content must be preserved; append only")
        if affected:
            if LOG not in changed:
                errors.append(f"{LOG}: numbered-folder changes require an appended audit entry")
            else:
                before = content_at(args.base, LOG)
                after = content_at(args.head, LOG)
                if after is None or (
                    before is not None and not log_body(after)[len(log_body(before)):].strip()
                ):
                    errors.append(f"{LOG}: numbered-folder changes require an appended audit entry")
        if errors:
            for error in errors:
                print(f"ERROR: {error}", file=sys.stderr)
            return 1
        print("Change synchronization audit passed.")
        return 0
    except (subprocess.CalledProcessError, UnicodeError, ValueError, OSError) as exc:
        detail = exc.stderr.decode("utf-8", errors="replace").strip() if isinstance(exc, subprocess.CalledProcessError) else str(exc)
        print(f"ERROR: cannot audit changes: {detail}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
