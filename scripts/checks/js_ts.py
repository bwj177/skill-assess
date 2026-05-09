"""JavaScript/TypeScript analysis."""

from __future__ import annotations

import re

RULES = [
    (r"child_process\.(exec|execSync|spawn)\b", "AST-JS-001", "high",
     "Process spawning via child_process"),
    (r"\beval\s*\(", "AST-JS-002", "high",
     "eval() — dynamic code execution"),
    (r"\bFunction\s*\(", "AST-JS-003", "high",
     "Function() constructor — dynamic code execution"),
    (r"require\s*\(\s*['\"]child_process['\"]", "AST-JS-005", "medium",
     "Import of child_process module"),
    (r"\bprocess\.env\b", "AST-JS-007", "low",
     "Environment variable access"),
    (r"\bfetch\s*\(", "AST-JS-008", "low",
     "Network request via fetch()"),
]


def analyze(script: dict) -> list[dict]:
    findings = []
    lines = script["content"].splitlines()
    for i, line in enumerate(lines, 1):
        if line.strip().startswith("//"):
            continue
        for pattern, rule_id, severity, msg in RULES:
            if re.search(pattern, line):
                findings.append({"rule_id": rule_id, "severity": severity,
                                 "message": msg, "file": script["relative_path"],
                                 "line": i, "evidence": line.strip()})
    return findings
