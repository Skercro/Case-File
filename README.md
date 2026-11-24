---
doc_type: repository_guide
status: draft
privilege: confidential
last_updated: 2026-11-24
updated_by: framework
verified_against_record: false
---

# Litigation case-file framework

A reusable, jurisdiction-configurable framework for tech-savvy attorneys and self-represented litigants to organize a civil litigation record and adapt the workflow to a specific matter. It provides a starting structure—not a complete case-management system, legal advice, or a determination of applicable law. Adapt or remove sections that do not fit your case.

The framework does not determine legal deadlines, privilege, admissibility, or governing law. Represented users should have counsel verify legal issues and approve filings. Self-represented users are responsible for independently verifying applicable law, court procedures, deadlines, and filings.

## Start here

1. Read this guide before putting any matter information into the repository.
2. Follow [CASE-SETUP.md](CASE-SETUP.md) to create a **separate private repository for one matter**, configure it, and check the setup.
3. Use [INDEX.md](INDEX.md) as the case-file dashboard. It links to each record area and the task queue.

## Quick start

**Prerequisites:** Git, Python 3, and Git LFS if you plan to add binary files covered by `.gitattributes`.

1. Create a new, empty **private** GitHub repository for your matter. Do not put case information in this public framework or a public fork. Before adding records, verify repository visibility, who can access it, backup and retention arrangements, and whether your organization's or professional obligations permit using GitHub and any AI tools with the case data. A private repository does not itself establish privilege, confidentiality, or policy compliance.
2. Clone the framework, then point `origin` at your new private repository. Replace the example URL with your repository's URL; check `git remote -v` before pushing.

   ```sh
   git clone https://github.com/Skercro/Case-File.git My-Case-File
   cd My-Case-File
   git remote rename origin framework
   git remote add origin https://github.com/YOUR-ACCOUNT/YOUR-PRIVATE-REPO.git
   git remote -v
   git push -u origin main
   ```

   Create the destination repository empty (without a README or license) so its history does not conflict with the clone. The `framework` remote keeps the public source address; push matter-specific work only to your private `origin`.
3. Work through [CASE-SETUP.md](CASE-SETUP.md) and complete [case-config.yaml](case-config.yaml). Keep unknown values unknown; do not mark the configuration verified until a human has reviewed it.
4. Install Git LFS and enable it with `git lfs install` before adding supported binary records. Set up Python dependencies and run the configuration validator and repository audit as described in the setup guide.
5. After confirming the private workspace and its access controls, place new incoming material in [00-inbox/](00-inbox/README.md). Follow the evidence and indexing rules before promoting originals to the evidence archive.

## How the file is organized

- [00-admin-and-strategy/](00-admin-and-strategy/) — case summary, authority register, procedure, and audit log.
- [00-inbox/](00-inbox/README.md) — staging and intake for incoming material.
- [01-pleadings-and-motions/](01-pleadings-and-motions/_index.md) and [02-discovery/](02-discovery/_index.md) — filings, drafts, discovery, and privilege tracking.
- [03-evidence-and-exhibits/](03-evidence-and-exhibits/_index.md) — preserved originals, checksums, and separately identified working derivatives.
- [04-chronology-and-facts/](04-chronology-and-facts/_index.md) and [05-correspondence/](05-correspondence/_index.md) — source-linked factual analysis and communications.
- [TODO.md](TODO.md) — work items and human-verified deadlines.
- [AGENTS.md](AGENTS.md) — repository rules and optional agent handoffs.

## Integrity, limits, and maintenance

Checksums establish file-content consistency, not provenance or authenticity. Never modify, overwrite, rename, or delete an existing file in `03-evidence-and-exhibits/raw/`; choose a final filename before placing an original there. Run `python3 scripts/hash_raw.py` after adding raw evidence, preserve prior checksum entries, and update the applicable index and audit log. See [AGENTS.md](AGENTS.md) for the complete integrity and citation rules.

The framework currently supports civil litigation only. The validator checks configuration structure, not the truth of case details, legal jurisdiction, applicable law, service, deadlines, or court procedure. A human must verify those matters. See [CASE-SETUP.md](CASE-SETUP.md) for limitations, validation commands, and the complete setup sequence.
