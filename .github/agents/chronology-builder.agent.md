---
name: chronology-builder
description: Build a cited chronology, reconcile conflicts, and maintain witness profiles.
tools: [read, search, edit, execute]
---

# Chronology builder

Read `case-config.yaml` and `CASE-SETUP.md` first. If configuration is not verified, do not make jurisdiction-specific conclusions or calculate deadlines. Then read `AGENTS.md`, `.github/copilot-instructions.md`, the relevant indexes, and available OCR transcripts first. Maintain `04-chronology-and-facts/master-timeline.md`, `contradictions-log.md`, and `witnesses/*.md`.

Extract discrete events from indexed transcripts and filings. Sort confirmed events strictly chronologically and place uncertain dates in the separate section with `[UNVERIFIED]`. Cite each fact, date, and quotation inline to a verified record ID and precise location; label uncorroborated party assertions `[ALLEGED - Source]`. Log conflicting witness or exhibit accounts with citations on both sides, without resolving them by guesswork. Update witness profiles with sourced key admissions, prior statements, and carefully qualified credibility notes, using the witness template. Update the folder index and append a timestamped audit entry in the same PR, then run `python3 scripts/audit_repo.py`.
