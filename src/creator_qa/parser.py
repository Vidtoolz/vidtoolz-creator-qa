"""Markdown package parser."""

from __future__ import annotations

from pathlib import Path

from .models import Package


KNOWN_SECTIONS = {"title", "thumbnail", "hook", "script", "notes"}


def normalize_heading(value: str) -> str:
    return " ".join(value.strip().lower().split())


def parse_markdown(path: str | Path) -> Package:
    """Parse a simple Markdown package into top-level sections."""

    file_path = Path(path)
    text = file_path.read_text(encoding="utf-8")
    sections: dict[str, list[str]] = {}
    current: str | None = None
    preamble: list[str] = []

    for raw_line in text.splitlines():
        stripped = raw_line.strip()
        if stripped.startswith("# ") and not stripped.startswith("##"):
            heading_text = stripped.lstrip("#").strip()
            heading = normalize_heading(heading_text)
            if heading:
                current = heading
                sections.setdefault(current, [])
                continue

        if current is None:
            preamble.append(raw_line)
        else:
            sections.setdefault(current, []).append(raw_line)

    parsed = {key: "\n".join(lines).strip() for key, lines in sections.items()}
    if preamble and any(line.strip() for line in preamble):
        parsed.setdefault("notes", "\n".join(preamble).strip())

    return Package(path=str(file_path), sections=parsed)
