"""Frontmatter structure compliance checks."""

from __future__ import annotations

import re

ALLOWED_FIELDS = {
    "name", "description", "license", "allowed-tools", "metadata", "compatibility",
    "argument-hint", "arguments", "when_to_use", "version", "model",
    "disable-model-invocation", "user-invocable", "hooks", "context",
    "agent", "effort", "paths", "shell", "tags",
}


def check(fm: dict) -> list[dict]:
    findings = []

    if not fm:
        findings.append({"rule_id": "STR-001", "severity": "critical",
                         "message": "No YAML frontmatter found"})
        return findings

    if "name" not in fm:
        findings.append({"rule_id": "STR-002", "severity": "critical",
                         "message": "Required field 'name' is missing"})
    if "description" not in fm:
        findings.append({"rule_id": "STR-003", "severity": "critical",
                         "message": "Required field 'description' is missing"})

    unknown = set(fm.keys()) - ALLOWED_FIELDS
    if unknown:
        findings.append({"rule_id": "STR-004", "severity": "medium",
                         "message": f"Unknown frontmatter fields: {', '.join(sorted(unknown))}"})

    name = fm.get("name")
    if isinstance(name, str):
        name = name.strip()
        if not re.match(r"^[a-z0-9-]+$", name):
            findings.append({"rule_id": "STR-005", "severity": "high",
                             "message": f"Name '{name}' is not kebab-case"})
        if name.startswith("-") or name.endswith("-"):
            findings.append({"rule_id": "STR-006", "severity": "medium",
                             "message": "Name cannot start/end with hyphen"})
        if "--" in name:
            findings.append({"rule_id": "STR-007", "severity": "medium",
                             "message": "Name contains consecutive hyphens"})
        if len(name) > 64:
            findings.append({"rule_id": "STR-008", "severity": "medium",
                             "message": f"Name is {len(name)} chars (max 64)"})
    elif name is not None:
        findings.append({"rule_id": "STR-009", "severity": "high",
                         "message": "Name must be a string"})

    desc = fm.get("description")
    if isinstance(desc, str):
        if "<" in desc or ">" in desc:
            findings.append({"rule_id": "STR-010", "severity": "medium",
                             "message": "Description contains angle brackets"})
        if len(desc) > 1024:
            findings.append({"rule_id": "STR-011", "severity": "medium",
                             "message": f"Description is {len(desc)} chars (max 1024)"})

    return findings
