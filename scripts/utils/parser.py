"""SKILL.md parser: extract frontmatter, body, inline shell commands, script files."""

from __future__ import annotations

import re
from pathlib import Path

import yaml


def parse_frontmatter(content: str) -> tuple[dict, str]:
    """Extract YAML frontmatter and body from SKILL.md content."""
    if not content.startswith("---"):
        return {}, content
    match = re.match(r"^---\n(.*?)\n---", content, re.DOTALL)
    if not match:
        return {}, content
    try:
        fm = yaml.safe_load(match.group(1))
        if not isinstance(fm, dict):
            fm = {}
    except yaml.YAMLError:
        fm = {}
    body = content[match.end():]
    if body.startswith("\n"):
        body = body[1:]
    return fm, body


def extract_inline_commands(body: str) -> list[dict]:
    """Extract inline shell commands from SKILL.md body."""
    commands = []
    for m in re.finditer(r"```!\n(.*?)```", body, re.DOTALL):
        line = body[:m.start()].count("\n") + 1
        cmd = m.group(1).strip()
        if cmd:
            commands.append({"command": cmd, "line": line, "block": True})
    for m in re.finditer(r"!`([^`]+)`", body):
        line = body[:m.start()].count("\n") + 1
        cmd = m.group(1).strip()
        if cmd:
            commands.append({"command": cmd, "line": line, "block": False})
    return commands


def load_script_files(skill_path: Path) -> list[dict]:
    """Load all script files from the skill's scripts/ directory."""
    scripts_dir = skill_path / "scripts"
    if not scripts_dir.is_dir():
        return []

    ext_lang = {
        ".py": "python", ".sh": "shell", ".bash": "shell",
        ".js": "javascript", ".mjs": "javascript",
        ".ts": "typescript", ".tsx": "typescript",
    }

    files = []
    for f in sorted(scripts_dir.rglob("*")):
        if not f.is_file():
            continue
        lang = ext_lang.get(f.suffix.lower())
        if not lang:
            continue
        try:
            content = f.read_text(encoding="utf-8", errors="replace")
        except Exception:
            continue
        files.append({
            "path": str(f),
            "relative_path": str(f.relative_to(skill_path)),
            "language": lang,
            "content": content,
        })
    return files


def classify_directory(skill_path: Path) -> dict:
    """Classify files in skill directory."""
    result = {"scripts": [], "references": [], "assets": [], "other": []}
    if not skill_path.is_dir():
        return result
    for f in sorted(skill_path.rglob("*")):
        if not f.is_file():
            continue
        rel = str(f.relative_to(skill_path))
        top = rel.split("/")[0]
        if top == "scripts" and "/" in rel:
            result["scripts"].append(rel)
        elif top == "references" and "/" in rel:
            result["references"].append(rel)
        elif top == "assets" and "/" in rel:
            result["assets"].append(rel)
        elif top != "SKILL.md":
            result["other"].append(rel)
    return result
