"""Supply chain verification."""

from __future__ import annotations

import json
import re
from pathlib import Path


def check(skill_path: Path, classification: dict) -> list[dict]:
    findings = []

    skillfish = skill_path / ".skillfish.json"
    if skillfish.exists():
        try:
            data = json.loads(skillfish.read_text(encoding="utf-8"))
            repo = data.get("repo", data.get("source", ""))
            if repo and not repo.startswith("https://"):
                findings.append({"rule_id": "SC-001", "severity": "medium",
                                 "message": f"Provenance URL is not HTTPS: {repo}"})
        except Exception:
            findings.append({"rule_id": "SC-002", "severity": "low",
                             "message": ".skillfish.json is not valid JSON"})
    else:
        findings.append({"rule_id": "SC-003", "severity": "info",
                         "message": "No .skillfish.json — no provenance information"})

    refs_dir = skill_path / "references"
    if refs_dir.is_dir():
        for ref_file in refs_dir.rglob("*.md"):
            try:
                content = ref_file.read_text(encoding="utf-8")
            except Exception:
                continue
            seen_urls: set[str] = set()
            for m in re.finditer(r"http://[^\s\)]+", content):
                url = m.group(0)
                if url in seen_urls:
                    continue
                seen_urls.add(url)
                findings.append({"rule_id": "SC-004", "severity": "medium",
                                 "message": f"Non-HTTPS URL in {ref_file.relative_to(skill_path)}: {url}",
                                 "file": str(ref_file.relative_to(skill_path))})

    return findings
