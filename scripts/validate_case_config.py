#!/usr/bin/env python3
"""Validate the structured civil case configuration; this is not legal verification."""
from datetime import date
from pathlib import Path
import re
import sys

try:
    import yaml
except ImportError:
    print("ERROR: PyYAML is required. Install with: python3 -m pip install -r requirements-dev.txt", file=sys.stderr)
    raise SystemExit(2)

ROOT = Path(__file__).resolve().parent.parent
PATH = ROOT / "case-config.yaml"
ALLOWED_STATUS = {"unconfigured", "in_progress", "verified"}


class UniqueKeyLoader(yaml.SafeLoader):
    def construct_mapping(self, node, deep=False):
        self.flatten_mapping(node)
        seen = set()
        for key_node, _ in node.value:
            key = self.construct_object(key_node, deep=deep)
            try:
                duplicate = key in seen
                seen.add(key)
            except TypeError as exc:
                raise yaml.constructor.ConstructorError(
                    "while constructing a mapping", node.start_mark,
                    "unhashable mapping key", key_node.start_mark,
                ) from exc
            if duplicate:
                raise yaml.constructor.ConstructorError(
                    "while constructing a mapping", node.start_mark,
                    f"duplicate key: {key!r}", key_node.start_mark,
                )
        return super().construct_mapping(node, deep=deep)


def main():
    if PATH.is_symlink() or not PATH.is_file():
        print("ERROR: case-config.yaml is missing or is not a regular file", file=sys.stderr)
        return 1
    try:
        data = yaml.load(PATH.read_text(encoding="utf-8"), Loader=UniqueKeyLoader)
    except (OSError, UnicodeError, ValueError, yaml.YAMLError) as exc:
        print(f"ERROR: invalid case-config.yaml: {exc}", file=sys.stderr)
        return 1
    errors = []
    def mapping(parent, key, label):
        value = parent.get(key) if isinstance(parent, dict) else None
        if not isinstance(value, dict):
            errors.append(f"{label} must be a mapping")
            return {}
        return value
    def string_list(parent, key, label):
        value = parent.get(key) if isinstance(parent, dict) else None
        if not isinstance(value, list) or any(not isinstance(item, str) for item in value):
            errors.append(f"{label} must be a list of strings")

    if not isinstance(data, dict):
        errors.append("top level must be a mapping")
        data = {}
    if data.get("schema_version") != "1.0":
        errors.append("schema_version must be '1.0'")
    status = data.get("configuration_status")
    if not isinstance(status, str) or status not in ALLOWED_STATUS:
        errors.append("configuration_status must be unconfigured, in_progress, or verified")
    case = mapping(data, "case", "case")
    if case.get("matter_type") != "civil":
        errors.append("case.matter_type must be 'civil' (this framework supports civil litigation)")
    scope = mapping(data, "case_scope", "case_scope")
    for key in ("claims", "defenses", "requested_relief"):
        string_list(scope, key, f"case_scope.{key}")
    jurisdiction = mapping(data, "jurisdiction", "jurisdiction")
    court = mapping(jurisdiction, "court", "jurisdiction.court")
    laws = mapping(jurisdiction, "governing_law", "jurisdiction.governing_law")
    for key in ("federal", "state", "local_rules", "standing_orders"):
        string_list(laws, key, f"jurisdiction.governing_law.{key}")
    parties = data.get("parties")
    if not isinstance(parties, list):
        errors.append("parties must be a list")
    else:
        ids = set()
        for i, party in enumerate(parties):
            if not isinstance(party, dict) or not isinstance(party.get("id"), str) or not party["id"].strip():
                errors.append(f"parties[{i}] must be a mapping with a non-empty id")
            elif party["id"] in ids:
                errors.append(f"duplicate party id: {party['id']}")
            else:
                ids.add(party["id"])
    proceedings = mapping(data, "proceedings", "proceedings")
    for key in ("pending_motions", "hearings", "known_deadlines", "orders"):
        if not isinstance(proceedings.get(key), list):
            errors.append(f"proceedings.{key} must be a list")
    controls = mapping(data, "operating_controls", "operating_controls")
    for key in ("privilege_review_required", "human_review_required",
                "filing_approval_required", "deadline_calculation_requires_human_verification"):
        value = controls.get(key)
        if not isinstance(value, bool):
            errors.append(f"operating_controls.{key} must be a boolean")
        elif not value:
            print(f"WARNING: operating_controls.{key} is disabled; confirm that this is authorized for the matter.", file=sys.stderr)
    for key in ("permitted_ai_data_sources", "prohibited_ai_actions"):
        string_list(controls, key, f"operating_controls.{key}")
    verification = mapping(data, "verification", "verification")
    if not isinstance(verification.get("unresolved_items"), list):
        errors.append("verification.unresolved_items must be a list")
    review_status = verification.get("status")
    if not isinstance(review_status, str) or review_status not in {"not_reviewed", "in_review", "verified"}:
        errors.append("verification.status must be not_reviewed, in_review, or verified")
    if status == "verified":
        required = {
            "case.title": case.get("title"),
            "case.case_number": case.get("case_number"),
            "jurisdiction.country": jurisdiction.get("country"),
            "jurisdiction.state_or_province": jurisdiction.get("state_or_province"),
            "jurisdiction.county_or_district": jurisdiction.get("county_or_district"),
            "jurisdiction.court.name": court.get("name"),
            "verification.reviewed_by": verification.get("reviewed_by"),
        }
        for label, value in required.items():
            if not isinstance(value, str) or not value.strip():
                errors.append(f"{label} is required when configuration_status is verified")
        reviewed = verification.get("last_reviewed")
        if isinstance(reviewed, str):
            try:
                if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", reviewed):
                    raise ValueError("not an ISO calendar date")
                date.fromisoformat(reviewed)
            except ValueError:
                errors.append("verification.last_reviewed must be a valid ISO date when configuration_status is verified")
        elif not isinstance(reviewed, date):
            errors.append("verification.last_reviewed must be a valid ISO date when configuration_status is verified")
        if verification.get("status") != "verified":
            errors.append("verification.status must be 'verified' when configuration_status is verified")
        if verification.get("unresolved_items"):
            errors.append("verification.unresolved_items must be empty before marking verified")
    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        return 1
    print(f"Case configuration structure valid (status: {status}). Legal jurisdiction and deadlines are not verified by this script.")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
