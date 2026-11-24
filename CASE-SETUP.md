---
doc_type: repository_guide
status: draft
privilege: confidential
last_updated: 2026-11-24
updated_by: framework
verified_against_record: false
---

# Civil case setup guide

## Purpose

Use `case-config.yaml` as the single structured source for case identity, jurisdiction, court, parties, procedural posture, claims, requested relief, authority-research scope, and operating controls. This framework currently supports civil litigation and is jurisdiction-configurable; it assumes no particular state, court, or rules.

This configuration is not a case summary, legal opinion, docket, or substitute for reviewing source documents. Keep detailed facts, evidence, procedural events, and legal analysis in their designated records.

## Initialization sequence

1. Create a separate private repository for each matter from the clean framework. Never put actual party names, case numbers, evidence, or confidential case details in a public reusable framework repository.
2. Review access, retention, AI-processing, and backup settings before adding case material.
3. Complete the case section from an authoritative filing or docket source.
4. Complete jurisdiction from pleadings, docket, statutes, rules, and official court sources. Distinguish subject-matter jurisdiction, personal jurisdiction, venue, and choice of law; they are not interchangeable.
5. Identify parties and counsel. Use stable party IDs.
6. Populate claims, defenses, requested relief, pending motions, hearings, known deadlines, orders, and ADR information. Every deadline must cite its source and trigger in the case record and be independently verified by a human.
7. Track candidate authorities in the authority register. Verify current text, effective date, court, precedential status, and applicability before treating an authority as controlling.
8. Review operating controls, permitted data sources, and prohibited actions.
9. Keep configuration_status as unconfigured or in_progress until a human reviews the material fields. Set it to verified only when required identity and jurisdiction fields are complete, verification.status is verified, reviewer and date are recorded, and unresolved items are cleared or expressly resolved.

## Field and evidence rules

- Use the court's exact name and case number from an authoritative docket or filed document.
- Use ISO dates (YYYY-MM-DD) where possible. Preserve original source dates where material.
- Use null for unknown single values and empty lists for no entries. Do not guess.
- A party allegation is not automatically a verified fact. Cite its source and label its status in the factual record.
- Sources listed as governing law or research leads are not automatically controlling.
- Local rules, standing orders, judge-specific procedures, and administrative orders may matter independently of statewide rules.
- Never store passwords, access tokens, financial account details, or other secrets here.

## Agent behavior and validation

Agents must read this file and the configuration before matter-specific work. If setup is unconfigured or in progress, they may organize material and identify missing setup information, but must not assert jurisdiction, venue, rule applicability, or deadline correctness. A human verifies legal conclusions and deadlines.

Automated validation checks YAML syntax, required structure, supported civil matter type, and required fields when marked verified. It does not verify the truth of case details, legal jurisdiction, applicable law, service, deadlines, or court procedures.
