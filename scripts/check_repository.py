#!/usr/bin/env python3
"""Dependency-free structural checks for the repository harness."""

from __future__ import annotations

import re
import sys
from pathlib import Path
from urllib.parse import unquote


ROOT = Path(__file__).resolve().parents[1]

EXPECTED_AGENTS = (
    Path("AGENTS.md"),
    Path("firmware/AGENTS.md"),
    Path("app/AGENTS.md"),
    Path("server/AGENTS.md"),
    Path("remote/code/AGENTS.md"),
    Path("openspec/AGENTS.md"),
    Path(".github/AGENTS.md"),
)

REQUIRED_PATHS = EXPECTED_AGENTS + (
    Path("CONTRIBUTING.md"),
    Path("docs/README.md"),
    Path("docs/knowledge-sources.md"),
    Path("docs/workflows.md"),
    Path("docs/validation.md"),
    Path("scripts/repo-harness"),
    Path(".github/workflows/repo-harness.yml"),
    Path("openspec/config.yaml"),
)

MARKDOWN_LINK_RE = re.compile(r"!?\[[^\]]*\]\(([^)]+)\)")
ACTION_RE = re.compile(r"^\s*-\s+uses:\s+([^@\s]+)@([^\s#]+)")
FULL_SHA_RE = re.compile(r"^[0-9a-f]{40}$")
PRIVATE_PATH_RE = re.compile(r"(?:/Users/[^/\s]+|[A-Za-z]:\\Users\\[^\\\s]+)")


def harness_markdown_files() -> list[Path]:
    files = [
        ROOT / "README.md",
        ROOT / "CONTRIBUTING.md",
        *(ROOT / path for path in EXPECTED_AGENTS),
    ]
    files.extend(sorted((ROOT / "docs").rglob("*.md")))
    return files


def content_without_fenced_code(path: Path) -> str:
    output: list[str] = []
    in_fence = False
    fence_marker = ""

    for line in path.read_text(encoding="utf-8").splitlines():
        stripped = line.lstrip()
        marker = stripped[:3]
        if marker in {"```", "~~~"}:
            if not in_fence:
                in_fence = True
                fence_marker = marker
            elif marker == fence_marker:
                in_fence = False
                fence_marker = ""
            continue
        if not in_fence:
            output.append(line)

    return "\n".join(output)


def normalized_link_target(raw_target: str) -> str:
    target = raw_target.strip()
    if target.startswith("<") and ">" in target:
        return target[1 : target.index(">")]

    title_match = re.match(r"""^(.+?)\s+["'][^"']*["']\s*$""", target)
    if title_match:
        target = title_match.group(1)
    return target


def check_local_links(path: Path, errors: list[str]) -> None:
    content = content_without_fenced_code(path)
    for match in MARKDOWN_LINK_RE.finditer(content):
        target = normalized_link_target(match.group(1))
        if (
            not target
            or target.startswith("#")
            or "://" in target
            or target.startswith(("mailto:", "data:", "javascript:"))
        ):
            continue

        target_path = unquote(target.split("#", 1)[0].split("?", 1)[0])
        if not target_path:
            continue

        if target_path.startswith("/"):
            resolved = ROOT / target_path.lstrip("/")
        else:
            resolved = path.parent / target_path
        resolved = resolved.resolve()

        try:
            resolved.relative_to(ROOT)
        except ValueError:
            errors.append(f"{path.relative_to(ROOT)}: link escapes repository: {target}")
            continue

        if not resolved.exists():
            errors.append(f"{path.relative_to(ROOT)}: broken local link: {target}")


def check_workflow_action_pins(errors: list[str]) -> None:
    workflow_dir = ROOT / ".github" / "workflows"
    for path in sorted((*workflow_dir.glob("*.yml"), *workflow_dir.glob("*.yaml"))):
        for line_number, line in enumerate(
            path.read_text(encoding="utf-8").splitlines(), start=1
        ):
            match = ACTION_RE.match(line)
            if not match:
                continue
            action, ref = match.groups()
            if action.startswith("./"):
                continue
            if not FULL_SHA_RE.fullmatch(ref):
                errors.append(
                    f"{path.relative_to(ROOT)}:{line_number}: "
                    f"Action {action} must use a full commit SHA"
                )


def main() -> int:
    errors: list[str] = []

    for relative_path in REQUIRED_PATHS:
        if not (ROOT / relative_path).exists():
            errors.append(f"missing required harness path: {relative_path}")

    harness = ROOT / "scripts" / "repo-harness"
    if harness.exists() and not harness.stat().st_mode & 0o111:
        errors.append("scripts/repo-harness is not executable")

    for path in harness_markdown_files():
        if not path.exists():
            continue
        check_local_links(path, errors)
        content = content_without_fenced_code(path)
        if PRIVATE_PATH_RE.search(content):
            errors.append(
                f"{path.relative_to(ROOT)}: contains a user-specific absolute path"
            )

    root_agents = ROOT / "AGENTS.md"
    if root_agents.exists():
        line_count = len(root_agents.read_text(encoding="utf-8").splitlines())
        if line_count > 140:
            errors.append(
                f"AGENTS.md has {line_count} lines; keep the root router at or below 140"
            )

    check_workflow_action_pins(errors)

    if errors:
        print("Repository harness checks failed:", file=sys.stderr)
        for error in errors:
            print(f"  - {error}", file=sys.stderr)
        return 1

    print("Repository harness checks passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
