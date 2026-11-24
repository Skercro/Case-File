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
2. Clone this framework into a local workspace and open it in an AI-enabled coding environment that can read/edit files and run local commands.
3. Start the **case-setup** agent (see [SETUP-AGENT.md](SETUP-AGENT.md) or [.github/agents/case-setup.agent.md](.github/agents/case-setup.agent.md)). It will guide you through setup as a conversational intake, install dependencies, configure the setup files, and run validation.
4. Use [INDEX.md](INDEX.md) as the case-file dashboard after setup.

The setup agent is optional. If you prefer to work manually, follow [CASE-SETUP.md](CASE-SETUP.md).

## Quick start

**Prerequisites:** Git, Python 3.9 or newer, and a separate empty private repository for the matter. An AI-enabled coding agent is optional. Git LFS is needed before adding binary files covered by `.gitattributes`.

1. Create a new, empty **private** repository for your matter. Do not put case information in this public framework or a public fork. Before sharing matter information with an AI tool, verify that your repository, AI service, connected tools, access controls, retention, and backup arrangements are approved for the matter. A private repository alone does not establish privilege, confidentiality, or policy compliance.
2. Clone this framework and open the local clone in your AI-enabled coding environment:

   ```sh
   git clone https://github.com/Skercro/Case-File.git My-Case-File
   cd My-Case-File
   ```

3. Run the case-setup agent. It will ask for the private repository URL, verify the workspace and privacy prerequisites, collect matter details in manageable sections, and ask you to confirm the summary before writing setup files. It will run `scripts/bootstrap_setup.sh` to create `.venv`, install `requirements-dev.txt`, and verify PyYAML **before** running project Python utilities.
4. The agent will configure `case-config.yaml`, prepare approved setup records, run the validator, repository audit, and tests, and report unresolved human-review items. It must not mark legal or jurisdictional details verified by itself.
5. Review the final remote configuration and explicitly approve any push. Matter-specific work belongs only in the separate private repository. Never push matter data to the public `framework` remote.

If the agent is unavailable, follow [CASE-SETUP.md](CASE-SETUP.md) for manual setup. Create the private destination empty (without a README or license) so the clone's history can be pushed without conflict. The public source remote should be named `framework`; the private matter remote should be named `origin`.

## How the file is organized

- [00-admin-and-strategy/](00-admin-and-strategy/) — case summary, authority register, procedure, and audit log.
- [00-inbox/](00-inbox/README.md) — staging and intake for incoming material.
- [01-pleadings-and-motions/](01-pleadings-and-motions/_index.md) and [02-discovery/](02-discovery/_index.md) — filings, drafts, discovery, and privilege tracking.
- [03-evidence-and-exhibits/](03-evidence-and-exhibits/_index.md) — preserved originals, checksums, and separately identified working derivatives.
- [04-chronology-and-facts/](04-chronology-and-facts/_index.md) and [05-correspondence/](05-correspondence/_index.md) — source-linked factual analysis and communications.
- [TODO.md](TODO.md) — work items and human-verified deadlines.
- [AGENTS.md](AGENTS.md) — repository rules and optional agent handoffs.

## Integrity, limits, and maintenance

Checksums establish file-content consistency, not provenance or authenticity. Never modify, overwrite, rename, or delete an existing file in `03-evidence-and-exhibits/raw/`; choose a final filename before placing an original there. Run `.venv/bin/python scripts/hash_raw.py` after adding raw evidence, preserve prior checksum entries, and update the applicable index and audit log. See [AGENTS.md](AGENTS.md) for the complete integrity and citation rules.

The framework currently supports civil litigation only. The validator checks configuration structure, not the truth of case details, legal jurisdiction, applicable law, service, deadlines, or court procedure. A human must verify those matters. See [SETUP-AGENT.md](SETUP-AGENT.md) for the agent workflow and [CASE-SETUP.md](CASE-SETUP.md) for manual setup.

Before using a matter workspace, configure the branch, access, backup, and pre-push controls in [OPERATIONS.md](OPERATIONS.md). See the [synthetic intake walkthrough](examples/synthetic-intake.md) for a non-sensitive example and the [MIT license](LICENSE) for reuse terms.
