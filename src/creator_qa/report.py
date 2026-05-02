"""Terminal and Markdown report rendering."""

from __future__ import annotations

from .models import GateResult


def failed_categories(result: GateResult) -> list[str]:
    return [check.name for check in result.checks if check.failed]


def render_terminal(result: GateResult) -> str:
    lines = [
        "Vidtoolz Creator QA Packaging Gate",
        f"Overall: {result.status}",
        f"Profile: {result.profile}",
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
        f"**Checked package:** {result.package_title}",
        f"**Overall result:** {result.status}",
        f"**Profile:** {result.profile}",
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


def render_hermes_report(result: GateResult) -> str:
    failed = failed_categories(result)
    lines = [
        "# Creator QA Memory Report",
        "",
        f"- Checked package title: {result.package_title}",
        f"- Overall result: {result.status}",
        f"- Profile: {result.profile}",
        f"- Total score: {result.total_score}/{result.max_score}",
        f"- Failed categories: {', '.join(failed) if failed else 'None'}",
        "",
        "## Top 3 Fixes",
    ]
    if result.top_fixes:
        lines.extend(f"{idx}. {item}" for idx, item in enumerate(result.top_fixes[:3], 1))
    else:
        lines.append("No fixes required.")

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

    next_action = "Ready for packaging handoff." if result.status == "PASS" else "Fix the top failed category, then rerun Creator QA."
    lines.extend(["", f"Recommended next action: {next_action}"])
    return "\n".join(lines) + "\n"


def render_linear_report(result: GateResult) -> str:
    failed = failed_categories(result)
    lines = [
        "## Summary",
        f"Creator QA checked `{result.package_title}` with profile `{result.profile}` and returned **{result.status}** with score **{result.total_score}/{result.max_score}**.",
        "",
        "## Result",
        f"- Overall result: {result.status}",
        f"- Profile: {result.profile}",
        f"- Score: {result.total_score}/{result.max_score}",
        f"- Failed categories: {', '.join(failed) if failed else 'None'}",
        "",
        "## Failed Checks",
    ]
    if result.failed_checks:
        lines.extend(f"- {item}" for item in result.failed_checks)
    else:
        lines.append("- None")

    lines.extend(["", "## Action Checklist"])
    if result.top_fixes:
        lines.extend(f"- [ ] {item}" for item in result.top_fixes)
    else:
        lines.append("- [ ] No QA fixes required.")

    lines.extend(["", "## QA Evidence"])
    lines.append(f"- Created at: {result.created_at}")
    lines.append(f"- Sections detected: {', '.join(result.input_sections_detected) if result.input_sections_detected else 'None'}")
    lines.append(f"- Risky factual claims: {len(result.risky_claims)}")
    lines.append(f"- Suspicious Resolve terms: {len(result.suspicious_terms)}")
    lines.append(f"- Finding IDs: {', '.join(sorted({finding.id for check in result.checks for finding in check.findings})) or 'None'}")
    return "\n".join(lines) + "\n"
