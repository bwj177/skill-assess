"""Shell script analysis."""

from __future__ import annotations

import re

RULES = [
    (r"\brm\s+(-[rRf]+\s+)*(/|~|\$HOME|\.\.)", "AST-SH-001", "high",
     "Recursive delete from root/home"),
    (r"\bcurl\b.*\|\s*(sh|bash)", "AST-SH-002", "critical",
     "Remote code execution: curl piped to shell"),
    (r"\bwget\b.*\|\s*(sh|bash)", "AST-SH-003", "critical",
     "Remote code execution: wget piped to shell"),
    (r"\bchmod\s+(777|666|\+s)", "AST-SH-006", "medium",
     "Overly permissive chmod or setuid"),
    (r"\bsudo\b", "AST-SH-008", "medium",
     "Privilege escalation via sudo"),
    (r"\beval\b\s+", "AST-SH-012", "high",
     "eval — dynamic code execution"),
    (r"/etc/(passwd|shadow|sudoers)", "AST-SH-013", "high",
     "Access to sensitive system file"),
    (r"\~/.ssh/", "AST-SH-014", "high",
     "Access to SSH directory"),
    (r"\bnc\b\s+-[elp]", "AST-SH-010", "high",
     "Netcat listener/backdoor"),
]


def analyze(script: dict) -> list[dict]:
    findings = []
    lines = script["content"].splitlines()
    for i, line in enumerate(lines, 1):
        if line.strip().startswith("#"):
            continue
        for pattern, rule_id, severity, msg in RULES:
            if re.search(pattern, line):
                findings.append({"rule_id": rule_id, "severity": severity,
                                 "message": msg, "file": script["relative_path"],
                                 "line": i, "evidence": line.strip()})
    return findings
