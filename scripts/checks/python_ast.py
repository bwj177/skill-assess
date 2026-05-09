"""Python AST-based security analysis."""

from __future__ import annotations

import ast

DANGEROUS_IMPORTS = {"pickle", "shelve", "ctypes", "subprocess", "socket"}
NETWORK_MODULES = {"urllib", "requests", "httpx", "aiohttp", "http"}


class Visitor(ast.NodeVisitor):
    def __init__(self, lines: list[str]):
        self.findings = []
        self._lines = lines

    def _line(self, n):
        return self._lines[n - 1].strip() if 0 < n <= len(self._lines) else ""

    def visit_Call(self, node):
        func = node.func

        # os.system()
        if isinstance(func, ast.Attribute) and func.attr == "system":
            if isinstance(func.value, ast.Name) and func.value.id == "os":
                self.findings.append({"rule_id": "AST-PY-001", "severity": "high",
                                      "message": "os.system() call",
                                      "line": node.lineno, "evidence": self._line(node.lineno)})

        # subprocess.*
        if isinstance(func, ast.Attribute) and func.attr in ("Popen", "call", "run", "check_call", "check_output"):
            is_sub = False
            if isinstance(func.value, ast.Name) and func.value.id == "subprocess":
                is_sub = True
            elif isinstance(func.value, ast.Attribute) and isinstance(func.value.value, ast.Name) and func.value.value.id == "subprocess":
                is_sub = True
            if is_sub:
                has_shell = any(kw.arg == "shell" and isinstance(kw.value, ast.Constant) and kw.value.value is True for kw in node.keywords)
                sev = "high" if has_shell else "medium"
                msg = f"subprocess.{func.attr}() with shell=True" if has_shell else f"subprocess.{func.attr}() call"
                self.findings.append({"rule_id": "AST-PY-002" if has_shell else "AST-PY-003",
                                      "severity": sev, "message": msg,
                                      "line": node.lineno, "evidence": self._line(node.lineno)})

        # eval/exec
        if isinstance(func, ast.Name) and func.id in ("eval", "exec"):
            self.findings.append({"rule_id": "AST-PY-004", "severity": "high",
                                  "message": f"{func.id}() — dynamic code execution",
                                  "line": node.lineno, "evidence": self._line(node.lineno)})

        # pickle.load/loads
        if isinstance(func, ast.Attribute) and func.attr in ("load", "loads"):
            if isinstance(func.value, ast.Name) and func.value.id == "pickle":
                self.findings.append({"rule_id": "AST-PY-006", "severity": "high",
                                      "message": f"pickle.{func.attr}() — deserializing untrusted data",
                                      "line": node.lineno, "evidence": self._line(node.lineno)})

        # network
        if isinstance(func, ast.Attribute) and func.attr in ("get", "post", "put", "delete", "urlopen", "request"):
            if isinstance(func.value, ast.Name) and func.value.id in NETWORK_MODULES:
                self.findings.append({"rule_id": "AST-PY-007", "severity": "medium",
                                      "message": f"Network request: {func.value.id}.{func.attr}()",
                                      "line": node.lineno, "evidence": self._line(node.lineno)})

        self.generic_visit(node)

    def visit_Import(self, node):
        for alias in node.names:
            if alias.name in DANGEROUS_IMPORTS:
                self.findings.append({"rule_id": "AST-PY-009", "severity": "medium",
                                      "message": f"Import of dangerous module: {alias.name}",
                                      "line": node.lineno, "evidence": self._line(node.lineno)})
        self.generic_visit(node)

    def visit_ImportFrom(self, node):
        if node.module and node.module in DANGEROUS_IMPORTS:
            self.findings.append({"rule_id": "AST-PY-009", "severity": "medium",
                                  "message": f"Import from dangerous module: {node.module}",
                                  "line": node.lineno, "evidence": self._line(node.lineno)})
        self.generic_visit(node)


def analyze(script: dict) -> list[dict]:
    try:
        tree = ast.parse(script["content"], filename=script["relative_path"])
    except SyntaxError:
        return [{"rule_id": "AST-PY-SYN", "severity": "low",
                 "message": "Syntax error — cannot parse", "file": script["relative_path"]}]

    v = Visitor(script["content"].splitlines())
    v.visit(tree)
    for f in v.findings:
        f["file"] = script["relative_path"]
    return v.findings
