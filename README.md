---
doc_type: repository_guide
status: draft
privilege: confidential
last_updated: 2026-11-24
updated_by: scaffold
verified_against_record: false
---

# Litigation case file

A jurisdiction-agnostic scaffold for organizing a litigation record with human supervision and GitHub Copilot agents. It does not determine legal deadlines, privilege, admissibility, or applicable law. Counsel must verify those matters and approve all filings.

## Architecture

Start with [INDEX.md](INDEX.md) for the repository map, [TODO.md](TODO.md) for deadlines and work, and [AGENTS.md](AGENTS.md) for the mandatory agent rules. Numbered folders separate filings, discovery, immutable source evidence, factual analysis, and correspondence. Each numbered folder has its own `_index.md`; evidence transcripts are working derivatives, not replacements for originals.

## Quick start

1. Restrict repository access and confirm that the hosting, retention, confidentiality, privilege, and AI-processing policies are appropriate for the matter. Do not put secrets in the repository. Treat attorney review as mandatory.
2. Install Git LFS and enable it locally: `git lfs install`. The included `.gitattributes` tracks the listed lowercase binary extensions; use lowercase extensions when naming records. Install LFS before adding those files; existing tracked files need a separately reviewed migration. LFS storage and bandwidth may incur costs.
3. Place incoming material in [00-inbox/](00-inbox/README.md), then ask `@intake-clerk` to triage it. Choose the final raw evidence name before placing a copy in `03-evidence-and-exhibits/raw/`; never change an existing raw file.
4. Run `python3 scripts/hash_raw.py`, update relevant folder indexes and the audit log, and run `python3 scripts/audit_repo.py`. Review the changes in a pull request. CI checks the raw evidence diff and audits the checked-out record.
5. Dispatch chronology, discovery, research, and record-audit work using the agent routing table in [AGENTS.md](AGENTS.md) or the issue forms. A qualified human verifies citations, dates, authorities, privilege decisions, and deadlines.

## Integrity and limitations

Checksums cover file contents, not provenance or authenticity. Paths in `03-evidence-and-exhibits/checksums.sha256` are relative to `raw/`; validate externally with `cd 03-evidence-and-exhibits/raw && sha256sum -c ../checksums.sha256`. The checked-in `.gitkeep` is itself hashed and immutable. The scripts reject unhydrated Git LFS pointers and symlinks; run `git lfs pull` if needed. Run the hash utility with a single writer, and resolve concurrent changes through reviewed PRs. Scripts require Python 3 and only the standard library; run their tests with `python3 -m unittest discover -s tests -v`.

The audit checks frontmatter in the specified directories, filename mentions in each numbered folder's index, and raw checksums. It cannot verify legal claims, meaningful index descriptions, log completeness, historical chain of custody, or citations. CI compares the base and head snapshots, not every intermediate commit. Configure branch protection or rulesets to require the audit, restrict direct pushes and force pushes, and require human review. Keep independent, access-controlled backups; Git and checksums alone are not a records-retention system. CI uses LFS checkout so hashes are calculated over actual content, not LFS pointers.
