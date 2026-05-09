"""Content quality assessment."""

from __future__ import annotations


def check(body: str, fm: dict, inline_commands: list, classification: dict) -> list[dict]:
    findings = []

    body_lines = body.count("\n") + 1
    if body_lines > 500:
        findings.append({"rule_id": "QUAL-001", "severity": "low",
                         "message": f"SKILL.md body is {body_lines} lines (recommended < 500)"})

    desc = fm.get("description", "")
    if isinstance(desc, str) and len(desc) < 50:
        findings.append({"rule_id": "QUAL-002", "severity": "info",
                         "message": "Description is very short (< 50 chars)"})

    if not classification.get("scripts") and not inline_commands:
        findings.append({"rule_id": "QUAL-003", "severity": "info",
                         "message": "No scripts or inline commands found — skill may be purely instructional"})

    if not fm.get("allowed-tools") and inline_commands:
        findings.append({"rule_id": "QUAL-005", "severity": "medium",
                         "message": "Has inline shell commands but no allowed-tools declaration"})

    return findings
