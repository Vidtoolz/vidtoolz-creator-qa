"""Episode Factory JSON adapter."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .models import Package


def load_episode_json(path: str | Path) -> dict[str, Any]:
    """Load an Episode Factory export or simplified episode object."""

    file_path = Path(path)
    data = json.loads(file_path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError("Episode JSON input must be an object.")
    return data


def stringify(value: Any) -> str:
    """Convert tolerant Episode Factory values into readable Markdown text."""

    if value is None:
        return ""
    if isinstance(value, str):
        return value.strip()
    if isinstance(value, (bool, int, float)):
        return str(value)
    if isinstance(value, list):
        lines: list[str] = []
        for item in value:
            text = stringify(item)
            if text:
                if "\n" in text:
                    lines.append(text)
                else:
                    lines.append(f"- {text}")
        return "\n".join(lines).strip()
    if isinstance(value, dict):
        lines = []
        for key, item in value.items():
            text = stringify(item)
            if text:
                label = split_camel_case(str(key)).title()
                lines.append(f"{label}: {text}")
        return "\n".join(lines).strip()
    return str(value).strip()


def first_text(data: dict[str, Any], *keys: str) -> str:
    for key in keys:
        text = stringify(data.get(key))
        if text:
            return text
    return ""


def split_camel_case(value: str) -> str:
    chars: list[str] = []
    for index, char in enumerate(value):
        if index and char.isupper() and value[index - 1].islower():
            chars.append(" ")
        chars.append(char)
    return "".join(chars).replace("_", " ").replace("-", " ")


def render_script(data: dict[str, Any]) -> str:
    script = stringify(data.get("script"))
    outline = stringify(data.get("scriptOutline"))
    if script and outline:
        return f"{outline}\n\n{script}".strip()
    return script or outline


def render_notes(data: dict[str, Any]) -> str:
    note_parts: list[tuple[str, str]] = [
        ("Notes", stringify(data.get("notes"))),
        ("Factual Claims Needing Source Notes", stringify(data.get("factualClaims"))),
        ("Sources / manual verification", stringify(data.get("sourceNotes"))),
        ("Status", stringify(data.get("status"))),
        ("Packaging Gate", stringify(data.get("packagingGate"))),
        ("Checklist", stringify(data.get("checklist"))),
        ("Shorts Ideas", stringify(data.get("shortsIdeas"))),
        ("Next Action", stringify(data.get("nextAction"))),
    ]
    sections: list[str] = []
    for heading, body in note_parts:
        if body:
            sections.append(f"{heading}:\n{body}")
    return "\n\n".join(sections).strip()


def episode_to_sections(data: dict[str, Any]) -> dict[str, str]:
    """Map Episode Factory JSON fields into Creator QA package sections."""

    sections = {
        "title": first_text(data, "title"),
        "thumbnail": first_text(data, "thumbnailText", "thumbnailConcept"),
        "hook": first_text(data, "hook"),
        "viewer payoff": first_text(data, "viewerPayoff", "promise"),
        "script": render_script(data),
        "notes": render_notes(data),
    }
    return {key: value for key, value in sections.items() if value}


def parse_episode_json(path: str | Path) -> Package:
    file_path = Path(path)
    return Package(path=str(file_path), sections=episode_to_sections(load_episode_json(file_path)))


def render_package_markdown(data: dict[str, Any]) -> str:
    sections = episode_to_sections(data)
    ordered = [
        ("Title", sections.get("title", "")),
        ("Thumbnail", sections.get("thumbnail", "")),
        ("Hook", sections.get("hook", "")),
        ("Viewer Payoff", sections.get("viewer payoff", "")),
        ("Script", sections.get("script", "")),
        ("Notes", sections.get("notes", "")),
    ]
    chunks = [f"# {heading}\n{body.strip()}" for heading, body in ordered if body.strip()]
    return "\n\n".join(chunks).strip() + "\n"


def render_package_markdown_from_file(path: str | Path) -> str:
    return render_package_markdown(load_episode_json(path))
