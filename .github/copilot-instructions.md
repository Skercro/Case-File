# Universal repository standards

Read [AGENTS.md](../AGENTS.md) first. Preserve confidentiality and privilege; use only authorized sources and tools. These instructions do not replace qualified human legal judgment.

## Naming

Name new record files `YYYY-MM-DD_[DocType]_[Short-Kebab-Title].[ext]`; use `0000-00-00` when the record date is unknown, and prefix `DRAFT_` inside `drafts/`. Choose the final raw name before ingestion. The fixed scaffold names (`_index.md`, `master-timeline.md`, `privilege-log.md`, and similar governance files), `.gitkeep`, and the checksum manifest are exceptions. Use stable IDs in indexes; a filename is not itself proof of a record's contents or date.

## YAML frontmatter

The required keys are `doc_type`, `status`, `last_updated`, `updated_by`, and `verified_against_record`; include `privilege` as well. Use a YAML mapping between `---` delimiters on the first line and a later line, with one `key: value` scalar per line. The audit intentionally accepts only single-line plain, single-quoted, or unescaped double-quoted scalars, without inline comments, collections, anchors, tags, or block scalars; use full-line comments if needed. Unknown keys must also use this subset. Quote strings that would otherwise be ambiguous YAML values.

| Key | Allowed values / format |
| --- | --- |
| `doc_type` | `repository_guide`, `inbox_guide`, `folder_index`, `task_queue`, `case_summary`, `theory_of_case`, `procedural_history`, `audit_log`, `pleading_draft`, `legal_memo`, `exhibit_sheet`, `privilege_log`, `timeline`, `contradictions_log`, `witness` |
| `status` | `draft`, `in_review`, `verified`, `filed`, `superseded` |
| `privilege` | `none`, `attorney_client`, `work_product`, `confidential` |
| `last_updated` | Valid calendar date `YYYY-MM-DD` |
| `updated_by` | Nonempty identifying string |
| `verified_against_record` | Unquoted YAML boolean `true` or `false` |

The audit requires the five keys above and validates `privilege` when present. `verified_against_record: true` is a human-review assertion, not an automated finding. Update metadata when editing; apply privilege labels only after appropriate review.

## Legal writing and analysis

Use objective, precise, neutral, court-ready prose. Separate undisputed facts from contested allegations, and apply the inline citation and uncertainty rules in [AGENTS.md](../AGENTS.md). Distinguish evidence from attorney work product, source statements from findings, and requests from actual court orders. Confirm the controlling jurisdiction, procedural posture, governing law, and authority currency with counsel; do not invent facts, quotations, deadlines, or citations.

Before interpreting a binary, consult its index entry and available OCR transcript. Keep factual analysis and transcripts separate from immutable originals, and preserve the source ID and exact location. Update indexes and append the audit log in the same PR as any change within `01`–`05`; run both scripts as applicable.
