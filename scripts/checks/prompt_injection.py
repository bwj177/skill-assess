"""Prompt injection pattern detection."""

from __future__ import annotations

import re

PATTERNS = [
    (r"ignore\s+(all\s+)?previous\s+(instructions|prompts|rules)", "INJ-001", "critical",
     "Attempt to override previous instructions"),
    (r"you\s+are\s+now\s+", "INJ-002", "high",
     "Attempt to redefine model identity"),
    (r"(system\s+prompt|system\s+message)\s*(override|replace|ignore)", "INJ-003", "critical",
     "Attempt to override system prompt"),
    (r"forget\s+(everything|all|your\s+instructions)", "INJ-004", "high",
     "Attempt to clear model context"),
    (r"(reveal|show|print|output)\s+(the\s+)?(system\s+prompt|instructions)", "INJ-005", "high",
     "Attempt to extract system prompt"),
    (r"do\s+not\s+(mention|reveal|disclose)\s+(this|these)", "INJ-006", "medium",
     "Covert instruction to hide actions"),
]


def check(body: str) -> list[dict]:
    findings = []
    lines = body.splitlines()
    for i, line in enumerate(lines, 1):
        stripped = line.strip()
        if stripped.startswith("#") or stripped.startswith("```"):
            continue
        for pattern, rule_id, severity, msg in PATTERNS:
            if re.search(pattern, line, re.IGNORECASE):
                findings.append({"rule_id": rule_id, "severity": severity,
                                 "message": msg, "line": i,
                                 "evidence": stripped[:120]})
    return findings
