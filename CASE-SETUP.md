---
doc_type: repository_guide
status: draft
privilege: confidential
last_updated: 2026-11-24
updated_by: framework
verified_against_record: false
---

# Set up a private workspace for your case

## Purpose and scope

This guide walks attorneys and self-represented litigants through making a clean copy of this civil-litigation framework, securing a matter-specific workspace, configuring the case, and checking the setup before adding records. Adapt the folder structure and workflow to the needs of your case; not every section will apply.

The framework is jurisdiction-configurable but supports civil litigation only. It assumes no particular state, court, or rules, and is not legal advice or a substitute for reviewing authoritative sources. Configuration is not a case summary, legal opinion, or docket. Keep detailed facts, evidence, procedural events, and legal analysis in their designated records.

## Before you begin

Have Git, Python 3, and access to a GitHub account or another approved private Git host. Git LFS is needed before adding binary file types covered by `.gitattributes`. Before copying any case material, confirm that your chosen host, access controls, retention and backup settings, and any AI or automation tools are permitted for the matter. A private repository alone does not ensure confidentiality, privilege, or compliance with professional or organizational obligations.

## Setup sequence

### 1. Create a separate private repository for the matter

Create a new, empty private repository. Do not use this public framework itself for case information, and do not assume a public fork can be made suitable for confidential case material. Do not add a README or license to the new repository; it will receive the framework's existing history.

Clone the framework, update the remote, verify the destination, and push the initial copy. Replace the URL with the URL of the private repository you just created.

```sh
git clone https://github.com/Skercro/Case-File.git My-Case-File
cd My-Case-File
git remote rename origin framework
git remote add origin https://github.com/YOUR-ACCOUNT/YOUR-PRIVATE-REPO.git
git remote -v
git push -u origin main
```

In the `git remote -v` output, make sure `origin` points to your private matter repository before pushing. The `framework` remote is the public source; do not push matter-specific changes there. If using a different Git host, follow its equivalent process and confirm the private destination before adding case records.

### 2. Confirm privacy and access before adding case records

Set repository visibility to private and grant access only to approved people. Review connected apps, AI-processing terms, retention, and independent backups against the applicable client, court, organizational, and professional requirements. Do not commit passwords, access tokens, financial account details, or other secrets. If these conditions cannot be verified, stop before adding case material and use an approved alternative.

### 3. Prepare the local tools

Install and enable Git LFS before adding binary files tracked by `.gitattributes`. The configured extensions are lowercase; use lowercase extensions when naming those records. LFS storage and bandwidth may incur costs. Existing tracked files need a separately reviewed migration. If the clone contains LFS-managed files that are not available locally, run `git lfs pull`.

Install the Python development dependency (PyYAML) from the repository root:

```sh
python3 -m pip install -r requirements-dev.txt
```

If you use a virtual environment, activate it before installing dependencies. On Windows, use the Python launcher (for example, `py -3`) in place of `python3` where needed.

### 4. Configure the case from authoritative records

Edit `case-config.yaml` in the private matter repository, using an authoritative filed document, docket, applicable rules, and official court sources. Keep the status `unconfigured` while beginning; set it to `in_progress` as you populate and verify fields.

- Use the court's exact name and case number. Use ISO dates (`YYYY-MM-DD`) where possible and preserve original source dates when material.
- Distinguish subject-matter jurisdiction, personal jurisdiction, venue, and choice of law; they are not interchangeable. Record candidate authority sources as research leads, not as controlling law.
- Identify parties and counsel with stable party IDs. Use `null` for an unknown single value and an empty list when there are no entries; do not guess.
- Add claims, defenses, requested relief, proceedings, orders, hearings, and known deadlines only with source references. Every deadline must include its source and triggering event in the case record and be independently verified by a human.
- Review operating controls, permitted data sources, and prohibited actions. Keep detailed facts and evidence in the designated case records, not in configuration notes.

Leave `configuration_status` as `unconfigured` or `in_progress` until a human has reviewed the material fields. Set it to `verified` only after required identity and jurisdiction fields are complete, `verification.status` is `verified`, the reviewer and review date are recorded, and unresolved items have been cleared or explicitly resolved. A verified status is a human attestation, not an automated legal finding.

### 5. Check the setup

From the repository root, run:

```sh
python3 scripts/validate_case_config.py
python3 scripts/audit_repo.py
python3 -m unittest discover -s tests -v
```

Use `py -3` instead of `python3` on Windows if needed. The configuration validator checks YAML syntax, required structure, supported civil matter type, and fields required for a configuration marked verified. The repository audit checks selected metadata, folder indexes, and raw-evidence checksums. Tests check the repository utilities. None of these commands verifies the truth of case details, legal conclusions, court rules, deadlines, service, or authenticity. Resolve reported failures; do not bypass them or mark legal information verified merely because a script passes.

### 6. Begin intake and preserve the record

After confirming that the private workspace is ready, stage new incoming material in `00-inbox/` and use the intake instructions there. Choose the final name for each original before placing it in `03-evidence-and-exhibits/raw/`. Never modify, overwrite, rename, or delete an existing raw file. Keep OCR, annotations, and corrections as separate, clearly identified derivatives outside `raw/`.

After adding raw evidence, run `python3 scripts/hash_raw.py`, retain existing checksum entries, and record provenance and custody details in the evidence index. Update the relevant numbered folder's `_index.md` and append a timestamped entry to `00-admin-and-strategy/agent-audit-log.md` whenever a file in folders `01` through `05` is created, moved, or updated. Review those changes together; use a pull request if your repository workflow supports it.

## Agent behavior and validation limits

Agents must read this guide and `case-config.yaml` before matter-specific work. While setup is unconfigured or in progress, work may organize material and identify missing information, but must not assert jurisdiction, venue, rule applicability, or deadline correctness. A human verifies legal conclusions and deadlines.

Automated validation checks structure only. It does not verify case facts, jurisdiction, applicable law, service, deadlines, court procedures, privilege, admissibility, or whether the repository's technology and access controls are appropriate for the matter.
