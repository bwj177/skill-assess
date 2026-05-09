#!/usr/bin/env python3
"""Unified skill assessment entry point. Outputs structured JSON to stdout."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

# Add script dir to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from utils.parser import parse_frontmatter, extract_inline_commands, load_script_files, classify_directory
from checks import frontmatter, permissions, python_ast, shell_script, js_ts, prompt_injection, quality, supply_chain


def assess(skill_path: Path) -> dict:
    skill_md = skill_path / "SKILL.md"
    if not skill_md.exists():
        return {"error": f"SKILL.md not found in {skill_path}"}

    content = skill_md.read_text(encoding="utf-8")
    fm, body = parse_frontmatter(content)
    inline_commands = extract_inline_commands(body)
    script_files = load_script_files(skill_path)
    classification = classify_directory(skill_path)

    findings = []

    # Rule-based checks
    findings.extend(frontmatter.check(fm))
    findings.extend(permissions.check(fm, inline_commands, script_files))
    findings.extend(prompt_injection.check(body))
    findings.extend(quality.check(body, fm, inline_commands, classification))
    findings.extend(supply_chain.check(skill_path, classification))

    # AST analysis per script
    for sf in script_files:
        if sf["language"] == "python":
            findings.extend(python_ast.analyze(sf))
        elif sf["language"] == "shell":
            findings.extend(shell_script.analyze(sf))
        elif sf["language"] in ("javascript", "typescript"):
            findings.extend(js_ts.analyze(sf))

    # Compute score
    penalties = {"critical": 30, "high": 20, "medium": 10, "low": 5, "info": 1}
    total_penalty = sum(penalties.get(f.get("severity", "info"), 1) for f in findings)
    score = max(0, 100 - total_penalty)

    if score >= 90:
        grade = "PASS"
    elif score >= 60:
        grade = "WARN"
    else:
        grade = "FAIL"

    return {
        "skill_name": fm.get("name", skill_path.name),
        "skill_path": str(skill_path),
        "score": score,
        "grade": grade,
        "finding_count": len(findings),
        "findings": findings,
    }


def main():
    parser = argparse.ArgumentParser(description="Assess a Claude Code skill")
    parser.add_argument("skill_path", help="Path to skill directory")
    parser.add_argument("--checks", help="Comma-separated check names to run (default: all)")
    args = parser.parse_args()

    path = Path(args.skill_path).resolve()
    if not path.is_dir():
        print(json.dumps({"error": f"Not a directory: {path}"}))
        sys.exit(1)

    result = assess(path)
    print(json.dumps(result, indent=2, ensure_ascii=False))
    sys.exit(1 if result.get("grade") == "FAIL" else 0)


if __name__ == "__main__":
    main()
