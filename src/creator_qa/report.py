"""Terminal and Markdown report rendering."""

from __future__ import annotations

from .models import GateResult


def render_terminal(result: GateResult) -> str:
    lines = [
        "Vidtoolz Creator QA Packaging Gate",
        f"Overall: {result.status}",
        f"Score: {result.total_score}/{result.max_score}",
        "",
        "Category scores:",
    ]
    for check in result.checks:
        lines.append(f"- {check.name}: {check.score}/5")

    if result.failed_checks:
        lines.extend(["", "Failed checks:"])
        lines.extend(f"- {item}" for item in result.failed_checks)
    if result.warnings:
        lines.extend(["", "Warnings:"])
        lines.extend(f"- {item}" for item in result.warnings)
    if result.risky_claims:
        lines.extend(["", "Risky factual claims needing source / manual verification:"])
        lines.extend(f"- {item}" for item in result.risky_claims)
    if result.suspicious_terms:
        lines.extend(["", "Suspicious Resolve terms:"])
        lines.extend(f"- {item}" for item in result.suspicious_terms)
    if result.top_fixes:
        lines.extend(["", "Top 3 fixes:"])
        lines.extend(f"{idx}. {item}" for idx, item in enumerate(result.top_fixes, 1))
    return "\n".join(lines)


def render_markdown(result: GateResult) -> str:
    lines = [
        "# Vidtoolz Creator QA Report",
        "",
        f"**Overall result:** {result.status}",
        f"**Score:** {result.total_score}/{result.max_score}",
        "",
        "## Category Scores",
    ]
    for check in result.checks:
        lines.append(f"- **{check.name}:** {check.score}/5")

    lines.extend(["", "## Failed Checks"])
    if result.failed_checks:
        lines.extend(f"- {item}" for item in result.failed_checks)
    else:
        lines.append("- None")

    lines.extend(["", "## Warnings"])
    if result.warnings:
        lines.extend(f"- {item}" for item in result.warnings)
    else:
        lines.append("- None")

    lines.extend(["", "## Risky Factual Claims"])
    if result.risky_claims:
        lines.extend(f"- {item}" for item in result.risky_claims)
    else:
        lines.append("- None")

    lines.extend(["", "## Suspicious Resolve Terms"])
    if result.suspicious_terms:
        lines.extend(f"- {item}" for item in result.suspicious_terms)
    else:
        lines.append("- None")

    lines.extend(["", "## Top 3 Recommended Fixes"])
    if result.top_fixes:
        lines.extend(f"{idx}. {item}" for idx, item in enumerate(result.top_fixes, 1))
    else:
        lines.append("No fixes required.")

    return "\n".join(lines) + "\n"
