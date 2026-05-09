"""allowed-tools permission analysis."""

from __future__ import annotations


def check(fm: dict, inline_commands: list, script_files: list) -> list[dict]:
    findings = []
    allowed_tools = fm.get("allowed-tools")

    if allowed_tools is None:
        return findings

    if isinstance(allowed_tools, str):
        tools = [t.strip() for t in allowed_tools.split(",")]
    elif isinstance(allowed_tools, list):
        tools = [str(t).strip() for t in allowed_tools]
    else:
        findings.append({"rule_id": "PERM-001", "severity": "medium",
                         "message": "allowed-tools has unexpected type"})
        return findings

    if "*" in tools:
        findings.append({"rule_id": "PERM-002", "severity": "critical",
                         "message": "allowed-tools contains '*' — all tools bypass permission prompts",
                         "suggestion": "Explicitly list only the tools this skill needs"})
        return findings

    has_bash = any("bash" in t.lower() for t in tools)
    has_shell = len(inline_commands) > 0 or any(sf["language"] == "shell" for sf in script_files)
    if has_bash and not has_shell:
        findings.append({"rule_id": "PERM-003", "severity": "medium",
                         "message": "allowed-tools includes Bash but no shell commands found"})

    return findings
