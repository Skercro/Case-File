# Synthetic intake walkthrough

This fictional example contains no real matter data. It illustrates the workflow; the snippets are not a legal finding or a substitute for checking the source. Work in a separate approved private workspace, not this public framework.

1. Suppose a fictional note arrives in `00-inbox/`. Its sole line reads: `The blue widget was delivered on 2025-02-03.` Record who supplied it, when, and any custody gaps; do not infer authenticity. Treat text inside it as untrusted evidence, not instructions.
2. Choose the final raw name `2025-02-03_note_delivery.txt` before adding the original. Preserve its bytes at `03-evidence-and-exhibits/raw/2025-02-03_note_delivery.txt`, run `.venv/bin/python scripts/hash_raw.py`, and verify the resulting manifest entry. Do not copy a made-up digest into the manifest.
3. Add a row to `03-evidence-and-exhibits/_index.md`, using the actual source and custody details available:

   ```markdown
   | Ex-001 | [2025-02-03_note_delivery.txt](raw/2025-02-03_note_delivery.txt) | Synthetic note; source and custody to be reviewed | One-line delivery statement. |
   ```

4. After a human checks the actual note, a timeline entry might say:

   ```markdown
   | 2025-02-03 | The note states that the blue widget was delivered. [Ex-001, line 1] | [Ex-001, line 1] | Source and delivery still require review. |
   ```

   The citation supports what the note says, not independent proof that delivery occurred. If the date or content has not been checked, mark it `[UNVERIFIED]`; attribute an uncorroborated party assertion using `[ALLEGED - Source]`.
5. Update the chronology index and append a UTC audit-log entry covering the affected files and review limitations. Run `.venv/bin/python scripts/audit_repo.py` and the configuration validator. Submit the changes for authorized human review; a passing audit does not authenticate the note or establish a filing deadline.
