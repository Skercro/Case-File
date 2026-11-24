---
doc_type: repository_guide
status: draft
privilege: confidential
last_updated: 2026-11-24
updated_by: framework
verified_against_record: false
---

# Operating a private case workspace

These are operational controls, not a guarantee of privilege, authenticity, or legal compliance. Confirm them with the person responsible for the matter before introducing case data. If a control is unavailable or unapproved, stop and use an approved alternative.

## Repository access and branch protection

1. Verify the destination's actual private visibility and identity in the host's settings, not just its URL or name. Restrict members, teams, connected applications, deploy keys, and AI access to approved uses. Review access and retention regularly.
2. Before matter work, configure a ruleset or branch protection on the private repository's default branch: require pull requests and the **Audit case record** job to pass, require branches to be up to date, and restrict direct pushes, force pushes, deletion, and bypass. Enable appropriate human review and protect workflow and governance changes from unauthorized edits. A repository administrator must confirm these settings; this framework cannot enable or verify them for you.
3. If the host or plan cannot enforce these controls, do not claim that CI enforces immutability. Document the limitation and use another approved control or workspace. Administrators and bypass actors can still alter history unless restricted by the host's settings.

The audit compares a change to its Git base, rejects changes to existing raw files, requires updated indexes and an appended audit entry for changes in folders `01`–`05`, and protects existing checksum and audit-log history. It cannot stop local edits, unauthorized pushes, history rewrites, a compromised workflow, or deletion of hosted data. Protect the workflow and preserve an independent baseline.

## Before every push

- Inspect `git remote -v`; independently verify the **exact push destination**, visibility, and permissions. Never push matter data to the public `framework` remote. An agent must receive explicit approval for the destination and push.
- Review `git status --short`, staged and committed changes, filenames, commit messages, and any Git LFS objects for unintended case data, privilege, secrets, or material beyond the approved scope. A private repository does not make an inappropriate disclosure safe.
- Confirm AI services, connected tools, access, retention, and the backup plan are approved. Run the local configuration validator, repository audit, and tests; review any warnings. On a pull request, confirm the required change audit and human review have passed before merging.
- Stop if destination, authorization, privacy, integrity, or review is uncertain. Correct or escalate before pushing; do not rely on a filename or a local check to prove the destination is private.

## Custody and recovery

Record source, custodian, acquisition time, transfers, and relevant restrictions in the evidence index or an approved restricted custody record. Preserve originals and separately identify derivatives. Hashes detect content differences against a trusted baseline; they do not prove source, custody, or authenticity.

Maintain independent, access-controlled, encrypted backups under an approved retention policy. Include Git history, all Git LFS objects, and any separately stored custody records; a Git clone with LFS pointer files alone is not a complete backup. Establish owners and a recovery schedule. Periodically restore to a separate authorized private environment, hydrate LFS objects, run the checksum audit, and compare the restored manifest with a separately protected baseline. Record the restore outcome without disclosing case details unnecessarily. Never restore over existing originals without an approved incident procedure.

## Updating from the framework

Keep the public source as `framework` and the private matter repository as `origin`. In a clean workspace, fetch `framework`, create a branch in the private repository, and merge or selectively apply reviewed upstream changes. Review conflicts, workflow and agent instructions, configuration, indexes, and the audit log; do not overwrite or silently resolve conflicts involving originals, checksum history, or case-specific work. Escalate those conflicts. Run the local checks, review the private repository's change audit, and merge only after authorized review. Never push matter branches to `framework`. Back up first and preserve the existing history; do not force-push to adopt an update.
