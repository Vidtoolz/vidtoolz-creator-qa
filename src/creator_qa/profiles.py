"""QA profile definitions for Creator QA."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class QAProfile:
    """Deterministic tuning for a creator package content type."""

    name: str
    description: str
    required_sections: tuple[str, ...]
    title_max_length: int
    thumbnail_max_words: int
    thumbnail_required: bool
    structure_parts: tuple[str, ...]
    min_script_words: int
    factual_risk_sensitivity: str
    resolve_terminology: str
    min_pass_ratio: float = 0.85


ALL_STRUCTURE_PARTS = (
    "hook",
    "problem/context",
    "promised outcome",
    "steps or sections",
    "demonstration/proof",
    "recap or takeaway",
    "call to action",
)

PROFILES: dict[str, QAProfile] = {
    "resolve_tutorial": QAProfile(
        name="resolve_tutorial",
        description="Long-form DaVinci Resolve tutorial packaging.",
        required_sections=("title", "thumbnail", "hook", "script"),
        title_max_length=70,
        thumbnail_max_words=8,
        thumbnail_required=True,
        structure_parts=ALL_STRUCTURE_PARTS,
        min_script_words=75,
        factual_risk_sensitivity="strict",
        resolve_terminology="strict",
    ),
    "shorts": QAProfile(
        name="shorts",
        description="Short-form vertical video package.",
        required_sections=("title", "hook", "script"),
        title_max_length=55,
        thumbnail_max_words=6,
        thumbnail_required=False,
        structure_parts=("hook", "problem/context", "promised outcome", "steps or sections", "call to action"),
        min_script_words=30,
        factual_risk_sensitivity="standard",
        resolve_terminology="off",
    ),
    "ai_video_breakdown": QAProfile(
        name="ai_video_breakdown",
        description="AI video workflow analysis or breakdown.",
        required_sections=("title", "thumbnail", "hook", "script", "notes"),
        title_max_length=75,
        thumbnail_max_words=8,
        thumbnail_required=True,
        structure_parts=ALL_STRUCTURE_PARTS,
        min_script_words=80,
        factual_risk_sensitivity="strict",
        resolve_terminology="off",
    ),
    "kit_newsletter": QAProfile(
        name="kit_newsletter",
        description="Creator newsletter or Kit email package.",
        required_sections=("title", "hook", "script"),
        title_max_length=90,
        thumbnail_max_words=10,
        thumbnail_required=False,
        structure_parts=("hook", "problem/context", "promised outcome", "steps or sections", "call to action"),
        min_script_words=70,
        factual_risk_sensitivity="strict",
        resolve_terminology="off",
    ),
    "product_affiliate_page": QAProfile(
        name="product_affiliate_page",
        description="Product or affiliate recommendation page.",
        required_sections=("title", "thumbnail", "hook", "script", "notes"),
        title_max_length=80,
        thumbnail_max_words=10,
        thumbnail_required=True,
        structure_parts=("problem/context", "promised outcome", "steps or sections", "demonstration/proof", "call to action"),
        min_script_words=90,
        factual_risk_sensitivity="strict",
        resolve_terminology="off",
    ),
}

DEFAULT_PROFILE_NAME = "resolve_tutorial"


def get_profile(name: str | None = None) -> QAProfile:
    """Return a supported QA profile, using the default when omitted."""

    profile_name = name or DEFAULT_PROFILE_NAME
    try:
        return PROFILES[profile_name]
    except KeyError as exc:
        supported = ", ".join(sorted(PROFILES))
        raise ValueError(f"Unknown profile: {profile_name}. Supported profiles: {supported}") from exc
