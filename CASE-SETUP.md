---
doc_type: repository_guide
status: draft
privilege: confidential
last_updated: 2026-11-24
updated_by: framework
verified_against_record: false
---

# Set up a private workspace for your case

## Choose your setup path

**Recommended: use the case-setup agent.** Clone this framework, open the local folder in an AI-enabled coding environment with file-editing and terminal access, and start [the case-setup agent](.github/agents/case-setup.agent.md). The agent follows [SETUP-AGENT.md](SETUP-AGENT.md): it confirms the workspace and privacy prerequisites, collects case details conversationally, summarizes them for your approval, installs dependencies, configures setup files, and runs validation.

The agent is an assistant, not a legal reviewer. It must not guess missing details, determine applicable law, calculate deadlines, or mark legal information verified. It should leave unknown values blank and report items that require human review.

**Manual setup:** Follow the remaining sections if you prefer not to use an AI agent or your environment cannot run one.

## Purpose and scope

This guide helps attorneys and self-represented litigants make a clean copy of this civil-litigation framework, secure a matter-specific workspace, configure the case, and check the setup before adding records. Adapt the folder structure and workflow to the needs of your case; not every section will apply.

The framework supports civil litigation only. It assumes no particular state, court, or rules, and is not legal advice or a substitute for reviewing authoritative sources. Configuration is not a case summary, legal opinion, or docket. Keep detailed facts, evidence, procedural events, and legal analysis in their designated records.

## Before you begin

Have Git, Python 3.9 or newer, and access to a GitHub account or another approved private Git host. Git LFS is needed before adding binary file types covered by `.gitattributes`. Before sharing matter information with an AI tool or copying case material, confirm that the host, AI service, connected tools, access controls, retention, and backup settings are permitted for the matter. A private repository alone does not ensure confidentiality, privilege, or compliance with professional or organizational obligations.

## Manual setup sequence

### 1. Create a separate private repository for the matter

Create a new, empty private repository. Do not use this public framework itself for case information, and do not assume a public fork can be made suitable for confidential case material. Do not add a README or license to the new repository; it will receive the framework's existing history.

Clone the framework:

```sh
git clone https://github.com/Skercro/Case-File.git My-Case-File
cd My-Case-File
```

Install Git LFS before pushing if the clone contains LFS-managed files, and hydrate those objects:

```sh
git lfs install
git lfs pull
```

Then update the remotes. Replace the URL with the private repository URL and inspect the output:

```sh
git remote rename origin framework
git remote add origin https://github.com/YOUR-ACCOUNT/YOUR-PRIVATE-REPO.git
git remote -v
```

The `framework` remote is the public source; `origin` is the private matter repository. Never push matter-specific work to `framework`. If using another Git host, follow its equivalent process and confirm the destination is private.

### 2. Confirm privacy and access before adding case records

Verify that the exact `origin` destination is private and grant access only to approved people. Review connected apps, AI-processing terms, retention, and independent backups against applicable client, court, organizational, and professional requirements. Do not commit passwords, access tokens, financial account details, or other secrets. If these conditions cannot be verified, stop before adding case material and use an approved alternative.

Follow the [pre-push checklist](OPERATIONS.md#before-every-push) before the initial push, then push the clean framework to the verified private destination with `git push -u origin main`. Configure the [branch protection and backup controls](OPERATIONS.md) before adding matter information. Agents must obtain explicit approval before any push.

### 3. Prepare the local tools

From the repository root, run:

```sh
bash scripts/bootstrap_setup.sh
```

The script creates a local `.venv`, installs the declared dependencies from `requirements-dev.txt`, and verifies that PyYAML imports successfully. Use the virtual-environment interpreter for subsequent commands:

- macOS/Linux: `.venv/bin/python`
- Windows: `.venv/Scripts/python.exe`

If the script fails, resolve the reported Python/venv/pip issue before running project Python utilities. Do not silently fall back to an unprepared global Python environment.

Install Git LFS and enable it before adding binary files tracked by `.gitattributes`:

```sh
git lfs install
```

LFS storage and bandwidth may incur costs. Existing tracked files need a separately reviewed migration. If the clone contains LFS pointers, run `git lfs pull` before hashing or auditing evidence.

### 4. Configure the case from authoritative records

Edit `case-config.yaml` in the private matter repository, using authoritative filed documents, the docket, applicable rules, and official court sources. Keep the status `unconfigured` while beginning; set it to `in_progress` as you populate the fields.

- Use the court's exact name and case number. Use ISO dates (`YYYY-MM-DD`) where possible and preserve original source dates when material.
- Distinguish subject-matter jurisdiction, personal jurisdiction, venue, and choice of law; they are not interchangeable. Record candidate authority sources as research leads, not as controlling law.
- Identify parties and counsel with stable party IDs. Use `null` for an unknown single value and an empty list when there are no entries; do not guess.
- Add claims, defenses, requested relief, proceedings, orders, hearings, and known deadlines only with source references. Every deadline must include its source and triggering event in the case record and be independently verified by a human.
- Review operating controls, permitted data sources, and prohibited actions. Keep detailed facts and evidence in designated case records, not in configuration notes.

Leave `configuration_status` as `unconfigured` or `in_progress` until a human has reviewed the material fields. Set it to `verified` only after required identity and jurisdiction fields are complete, `verification.status` is `verified`, the reviewer and review date are recorded, and unresolved items have been cleared or explicitly resolved. A verified status is a human attestation, not an automated legal finding.

### 5. Check the setup

From the repository root, run:

```sh
.venv/bin/python scripts/validate_case_config.py
.venv/bin/python scripts/audit_repo.py
.venv/bin/python -m unittest discover -s tests -v
```

On Windows, use `.venv/Scripts/python.exe` instead. The configuration validator checks YAML syntax, required structure, supported civil matter type, and fields required for a configuration marked verified; it warns if a protective operating control is disabled. The repository audit checks selected metadata, folder indexes, and raw-evidence checksums. The CI change audit checks index and audit-log synchronization and append-only history against the Git base. None of these commands verifies the truth of case details, legal conclusions, court rules, deadlines, service, or authenticity. Resolve reported failures and review warnings; do not bypass them or mark legal information verified merely because a script passes.

### 6. Begin intake and preserve the record

After confirming that the private workspace is ready, stage new incoming material in `00-inbox/` and use the intake instructions there. Choose the final name for each original before placing it in `03-evidence-and-exhibits/raw/`. Never modify, overwrite, rename, or delete an existing raw file. Keep OCR, annotations, and corrections as separate, clearly identified derivatives outside `raw/`.

After adding raw evidence, run `.venv/bin/python scripts/hash_raw.py`, retain existing checksum entries, and record provenance and custody details in the evidence index. Update the relevant numbered folder's `_index.md` and append a timestamped entry to `00-admin-and-strategy/agent-audit-log.md` whenever a file in folders `01` through `05` is created, moved, or updated. Review those changes together; use a pull request if your repository workflow supports it.

## Validation limits

Automated validation checks structure only. It does not verify case facts, jurisdiction, applicable law, service, deadlines, court procedures, privilege, admissibility, or whether the repository's technology and access controls are appropriate for the matter. A human remains responsible for legal verification and approval.
