"""Deterministic rule checks for Creator QA."""

from __future__ import annotations

import json
import re
from datetime import datetime, timezone
from pathlib import Path

from .models import CheckResult, Finding, GateResult, Package
from .profiles import QAProfile, get_profile

DATA_PATH = Path(__file__).resolve().parents[2] / "data" / "resolve_terms.json"

GENERIC_TITLE_WORDS = {
    "things",
    "stuff",
    "tips",
    "tricks",
    "guide",
    "tutorial",
    "video",
    "workflow",
    "better",
    "easy",
}
BENEFIT_WORDS = {
    "fix",
    "avoid",
    "build",
    "make",
    "create",
    "learn",
    "speed",
    "faster",
    "clean",
    "clear",
    "improve",
    "save",
    "export",
    "color",
    "edit",
    "deliver",
    "result",
    "without",
}
VAGUE_PHRASES = [
    "you need to know",
    "everything you need",
    "this changes everything",
    "game changer",
    "must watch",
    "ultimate guide",
    "secret trick",
]
VIEWER_PAYOFF_PATTERNS = [
    r"\byou('ll| will| can)?\b.*\b(get|learn|build|create|fix|avoid|understand|know|finish|make)\b",
    r"\bby the end\b",
    r"\bafter watching\b",
    r"\bso you can\b",
    r"\bwalk away with\b",
]
CREATOR_CENTERED = ["i show", "i explain", "my workflow", "my thoughts", "i talk about"]
STRUCTURE_PATTERNS = {
    "hook": [r"\bhook\b", r"\bwhat if\b", r"\bin this video\b"],
    "problem/context": [r"\bproblem\b", r"\bcontext\b", r"\bstruggle\b", r"\bcommon mistake\b", r"\bwhen you\b"],
    "promised outcome": [r"\bby the end\b", r"\byou will\b", r"\byou'll\b", r"\bso you can\b"],
    "steps or sections": [r"(^|\n)\s*(step\s+\d+|\d+\.|- )", r"\bfirst\b.*\bnext\b", r"\bsection\b"],
    "demonstration/proof": [r"\bdemo\b", r"\bdemonstrate\b", r"\bexample\b", r"\bbefore\b.*\bafter\b", r"\bproof\b", r"\bshow\b"],
    "recap or takeaway": [r"\brecap\b", r"\btakeaway\b", r"\bremember\b", r"\bin short\b", r"\bsummary\b"],
    "call to action": [r"\bsubscribe\b", r"\bcomment\b", r"\blike\b", r"\bdownload\b", r"\bgrab\b", r"\bwatch next\b"],
}
# Claim-shaped patterns only. We flag things that can be factually wrong and
# embarrassing (versions, prices, compatibility/support assertions, absolute
# claims, concrete performance specs) — NOT ordinary tutorial vocabulary.
# Bare superlatives ("best", "fastest", "first", "only") and topic words
# ("codec", "prores", "gpu", "fps") were removed: they are packaging/quality
# concerns handled elsewhere, not factual risks, and they made PASS unreachable.
RISK_PATTERNS = [
    r"\balways\b",
    r"\bnever\b",
    r"\bguarantee(?:d|s)?\b",
    r"\bv?\d+\.\d+(?:\.\d+)?\b",                       # version numbers: 18.6, v2.0.1
    r"\bversion\s+\d+\b",                              # "version 18"
    r"\$\s?\d+(?:\.\d{2})?\b",                         # prices
    r"\b\d+(?:\.\d+)?\s?(?:usd|eur|gbp|dollars|euros)\b",
    r"\bcompatible with\b",
    r"\bworks with\b",
    r"\bsupports\b",
    r"\brequires\b",
    r"\bresolve\b.*\b(feature|supports|requires|added|removed)\b",
    r"\b\d+(?:\.\d+)?\s?x\s+(?:faster|slower|smaller|bigger)\b",  # "2x faster"
    r"\b\d+\s?(?:fps|mbps|gb|tb)\b",                   # concrete specs: 60fps, 50mbps
]
STRICT_RISK_PATTERNS = [
    r"\b(?:19|20)\d{2}\b",                             # explicit years (not 1080/4000/720)
    r"\bnewly (?:added|released|introduced)\b",
    r"\b(?:released|introduced|added)\s+in\s+(?:19|20)\d{2}\b",
]
SOURCE_HINTS = ["source:", "sources:", "citation:", "verified:", "manual verification:", "needs source"]
WORD_RE = re.compile(r"[a-zA-Z0-9']+")


def words(text: str) -> list[str]:
    return [word.lower() for word in WORD_RE.findall(text)]


def score_from_issues(issue_count: int, max_score: int = 5) -> int:
    return max(0, max_score - issue_count)


def finding(rule_id: str, severity: str, category: str, message: str, suggestion: str) -> Finding:
    return Finding(rule_id, severity, category, message, suggestion)


def check_expected_structure(package: Package, profile: QAProfile | None = None) -> CheckResult:
    profile = profile or get_profile()
    category = "Expected package structure"
    failed: list[str] = []
    findings: list[Finding] = []
    present = sorted(section for section in profile.required_sections if package.get(section))
    missing = [section for section in profile.required_sections if not package.get(section)]

    for section in missing:
        message = f"Required section is missing for {profile.name}: {section}."
        failed.append(message)
        findings.append(
            finding(
                f"structure.missing_{section.replace(' ', '_')}",
                "fail",
                category,
                message,
                f"Add a # {section.title()} section for the {profile.name} profile.",
            )
        )

    return CheckResult(
        category,
        score_from_issues(len(failed)),
        failed,
        [],
        {"profile": profile.name, "required_sections": list(profile.required_sections), "present": present},
        findings,
    )


def check_title(package: Package, profile: QAProfile | None = None) -> CheckResult:
    profile = profile or get_profile()
    category = "YouTube title clarity"
    title = package.get("title")
    failed: list[str] = []
    warnings: list[str] = []
    findings: list[Finding] = []
    title_words = words(title)

    if not title:
        message = "Title section is missing."
        failed.append(message)
        findings.append(finding("title.missing", "fail", category, message, "Add a # Title section with topic and viewer benefit."))
    if len(title) > profile.title_max_length:
        message = f"Title is too long for the {profile.name} profile."
        failed.append(message)
        findings.append(finding("title.too_long", "fail", category, message, f"Shorten the title to roughly {profile.title_max_length} characters or fewer."))
    if len(title_words) < 4:
        message = "Title is too short to clearly identify topic and benefit."
        failed.append(message)
        findings.append(finding("title.too_short", "fail", category, message, "Name the topic and the viewer outcome in the title."))
    if any(phrase in title.lower() for phrase in VAGUE_PHRASES):
        message = "Title uses vague packaging language."
        failed.append(message)
        findings.append(finding("title.vague", "fail", category, message, "Replace vague hype with the concrete problem or result."))
    if title_words and len(set(title_words) - GENERIC_TITLE_WORDS) < 3:
        message = "Title sounds generic and does not clearly identify the topic."
        failed.append(message)
        findings.append(finding("title.generic", "fail", category, message, "Add specific product, workflow, or problem terms."))
    if not any(word in BENEFIT_WORDS for word in title_words):
        message = "Title does not state a clear viewer benefit."
        failed.append(message)
        findings.append(finding("title.no_viewer_benefit", "fail", category, message, "State what the viewer can fix, make, avoid, save, or improve."))
    if profile.resolve_terminology != "off" and "resolve" not in title.lower() and "davinci" not in title.lower():
        message = "Title may not identify the Resolve/video editing topic clearly."
        warnings.append(message)
        findings.append(finding("title.topic_unclear", "warning", category, message, "Include Resolve, DaVinci Resolve, or a clear editing topic when relevant."))

    return CheckResult(category, score_from_issues(len(failed)), failed, warnings, findings=findings)


def check_thumbnail_alignment(package: Package, profile: QAProfile | None = None) -> CheckResult:
    profile = profile or get_profile()
    category = "Thumbnail / title promise alignment"
    title = package.get("title")
    thumbnail = package.get("thumbnail")
    failed: list[str] = []
    warnings: list[str] = []
    findings: list[Finding] = []
    title_words = set(words(title)) - GENERIC_TITLE_WORDS
    thumb_words = set(words(thumbnail)) - GENERIC_TITLE_WORDS
    overlap = title_words & thumb_words

    if not thumbnail and profile.thumbnail_required:
        message = "Thumbnail section is missing."
        failed.append(message)
        findings.append(finding("thumbnail.missing", "fail", category, message, "Add a # Thumbnail section with short visual promise text."))
    elif not thumbnail:
        message = "Thumbnail is optional for this profile, but packaging may be harder to evaluate."
        warnings.append(message)
        findings.append(finding("thumbnail.optional_missing", "warning", category, message, "Add thumbnail text when this package will be used for a video surface."))
    if len(words(thumbnail)) > profile.thumbnail_max_words:
        message = f"Thumbnail text is too long for the {profile.name} profile."
        failed.append(message)
        findings.append(finding("thumbnail.too_much_text", "fail", category, message, f"Cut thumbnail text to roughly {profile.thumbnail_max_words} words or fewer."))
    if title_words and thumb_words and not overlap:
        message = "Title and thumbnail text do not share a clear promise."
        failed.append(message)
        findings.append(finding("thumbnail.promise_mismatch", "fail", category, message, "Make the thumbnail reinforce the same promise as the title."))
    if not any(word in thumb_words for word in BENEFIT_WORDS | {"before", "after", "timeline", "nodes", "export", "grade"}):
        message = "Thumbnail has no concrete visual promise."
        failed.append(message)
        findings.append(finding("thumbnail.no_visual_promise", "fail", category, message, "Use concrete result language such as fix, export, timeline, nodes, grade, before, or after."))
    if len(thumb_words) <= 1:
        message = "Thumbnail text may be too thin to carry a promise."
        warnings.append(message)
        findings.append(finding("thumbnail.too_thin", "warning", category, message, "Use enough thumbnail wording to imply the specific result."))

    return CheckResult(
        category,
        score_from_issues(len(failed)),
        failed,
        warnings,
        {"shared_terms": sorted(overlap)},
        findings,
    )


def check_viewer_payoff(package: Package) -> CheckResult:
    category = "Viewer payoff"
    combined = "\n".join(
        [
            package.get("title"),
            package.get("thumbnail"),
            package.get("hook"),
            package.get("viewer payoff"),
            package.get("script"),
        ]
    )
    lower = combined.lower()
    failed: list[str] = []
    warnings: list[str] = []
    findings: list[Finding] = []

    has_payoff = any(re.search(pattern, lower, re.MULTILINE) for pattern in VIEWER_PAYOFF_PATTERNS)
    if not has_payoff:
        message = "Viewer payoff is missing or unclear."
        failed.append(message)
        findings.append(finding("payoff.missing", "fail", category, message, "State what the viewer will get, fix, understand, or finish by the end."))
    if any(phrase in lower for phrase in CREATOR_CENTERED) and not has_payoff:
        message = "Payoff is creator-centered instead of viewer-centered."
        failed.append(message)
        findings.append(finding("payoff.weak", "fail", category, message, "Rewrite creator-centered language into a viewer-centered outcome."))
    elif any(phrase in lower for phrase in CREATOR_CENTERED):
        message = "Some payoff language is creator-centered; keep the result viewer-centered."
        warnings.append(message)
        findings.append(finding("payoff.weak", "warning", category, message, "Keep the promise focused on the viewer's result."))

    return CheckResult(category, score_from_issues(len(failed) * 2), failed, warnings, findings=findings)


def check_script_structure(package: Package, profile: QAProfile | None = None) -> CheckResult:
    profile = profile or get_profile()
    category = "Script structure"
    script = "\n".join([package.get("hook"), package.get("script")]).lower()
    failed: list[str] = []
    warnings: list[str] = []
    findings: list[Finding] = []
    present: list[str] = []
    script_words = words(script)

    if not script.strip():
        message = "Hook and Script sections are missing."
        failed.append(message)
        findings.append(finding("script.missing", "fail", category, message, "Add # Hook and # Script sections before running QA."))
    elif len(script_words) < profile.min_script_words:
        message = f"Script is too thin for the {profile.name} profile."
        failed.append(message)
        findings.append(finding("script.too_thin", "fail", category, message, f"Expand the script to at least {profile.min_script_words} purposeful words with clear beats."))
    for part in profile.structure_parts:
        patterns = STRUCTURE_PATTERNS[part]
        if any(re.search(pattern, script, re.MULTILINE | re.DOTALL) for pattern in patterns):
            present.append(part)
        else:
            message = f"Missing script structure part: {part}."
            failed.append(message)
            rule_id = {
                "hook": "script.no_hook",
                "problem/context": "script.no_context",
                "promised outcome": "script.no_promised_outcome",
                "steps or sections": "script.no_steps",
                "demonstration/proof": "script.no_demo_or_proof",
                "recap or takeaway": "script.no_recap",
                "call to action": "script.no_cta",
            }[part]
            findings.append(finding(rule_id, "fail", category, message, f"Add a clear {part} beat to the script."))

    missing_count = len(profile.structure_parts) - len(present)
    score = 0 if not script.strip() else max(0, 5 - missing_count)
    if script.strip() and missing_count and missing_count <= 2:
        warnings.append("Script has partial structure problems.")
    return CheckResult(
        category,
        min(score, score_from_issues(1) if len(script_words) < profile.min_script_words else 5),
        failed,
        warnings,
        {"present": present, "expected": list(profile.structure_parts), "word_count": len(script_words)},
        findings,
    )


def has_source_notes(package: Package) -> bool:
    notes = package.get("notes").lower()
    return any(hint in notes for hint in SOURCE_HINTS)


def find_risky_claims(text: str, sensitivity: str = "strict") -> list[str]:
    patterns = RISK_PATTERNS + (STRICT_RISK_PATTERNS if sensitivity == "strict" else [])
    claims: list[str] = []
    for line in text.splitlines():
        stripped = line.strip()
        if not stripped:
            continue
        stripped = re.sub(r"^[-*]\s+", "", stripped)
        lower = stripped.lower()
        if any(re.search(pattern, lower) for pattern in patterns):
            claims.append(stripped)
    return claims


def check_factual_risk(package: Package, profile: QAProfile | None = None) -> CheckResult:
    profile = profile or get_profile()
    category = "Factual-claim risk"
    claims = find_risky_claims(package.combined_text, profile.factual_risk_sensitivity)
    sourced = has_source_notes(package)
    failed: list[str] = []
    warnings: list[str] = []
    findings: list[Finding] = []
    if claims and not sourced:
        message = "Risky factual claims need source notes or manual verification."
        failed.append(message)
        findings.append(finding("factual.risky_claim", "fail", category, message, "Add source notes or manual verification for version, price, compatibility, performance, or absolute claims."))
    elif claims:
        message = "Risky factual claims detected; source notes are present."
        warnings.append(message)
        findings.append(finding("factual.risky_claim", "warning", category, message, "Confirm the source notes are current before publishing."))
    risk_score = max(0, 5 - min(5, len(claims)))
    return CheckResult(
        category,
        risk_score,
        failed,
        warnings,
        {"needs_source_manual_verification": claims},
        findings,
    )


def load_resolve_lexicon(path: Path = DATA_PATH) -> dict[str, object]:
    return json.loads(path.read_text(encoding="utf-8"))


def check_resolve_terms(package: Package, profile: QAProfile | None = None) -> CheckResult:
    profile = profile or get_profile()
    category = "Resolve terminology accuracy"
    if profile.resolve_terminology == "off":
        return CheckResult(category, 5, [], [], {"suspicious_terms": [], "profile": profile.name}, [])
    lexicon = load_resolve_lexicon()
    suspicious_map: dict[str, str] = lexicon.get("suspicious_terms", {})  # type: ignore[assignment]
    text = package.combined_text.lower()
    suspicious: list[str] = []
    for bad_term, suggestion in suspicious_map.items():
        if re.search(rf"\b{re.escape(bad_term.lower())}\b", text):
            suspicious.append(f"{bad_term} -> {suggestion}")

    failed = [f"Suspicious Resolve term: {item}" for item in suspicious]
    findings = [
        finding(
            "resolve.suspicious_term",
            "fail" if profile.resolve_terminology == "strict" else "warning",
            category,
            f"Suspicious Resolve term: {item}",
            "Replace the suspicious wording with the suggested Resolve terminology.",
        )
        for item in suspicious
    ]
    warnings: list[str] = []
    if profile.resolve_terminology != "strict":
        warnings = failed
        failed = []
    score = score_from_issues(len(failed))
    return CheckResult(category, score, failed, warnings, {"suspicious_terms": suspicious, "profile": profile.name}, findings)


def top_fixes(checks: list[CheckResult]) -> list[str]:
    fixes: list[str] = []
    priority = [
        ("Expected package structure", "Add the sections required by the selected QA profile."),
        ("Viewer payoff", "Rewrite the title/hook to state what the viewer gets by the end."),
        ("Script structure", "Add missing script beats: hook, context, outcome, steps, proof, recap, and CTA."),
        ("Factual-claim risk", "Add source notes or manual verification for risky factual claims."),
        ("YouTube title clarity", "Make the title specific: topic plus viewer benefit."),
        ("Thumbnail / title promise alignment", "Align thumbnail text with the same promise as the title."),
        ("Resolve terminology accuracy", "Replace suspicious Resolve terms with official/local lexicon terms."),
    ]
    by_name = {check.name: check for check in checks}
    for name, fix in priority:
        check = by_name.get(name)
        if check and check.failed:
            fixes.append(fix)
        if len(fixes) == 3:
            return fixes
    for check in checks:
        if check.warnings and len(fixes) < 3:
            fixes.append(f"Review warning in {check.name}.")
    return fixes[:3]


# A critical finding forces a hard FAIL. An unsourced risky factual claim is a
# real problem but should be a NEEDS WORK (fail-severity, non-critical), not a
# hard FAIL — it is fixable by adding a source note, and treating it as critical
# made realistic packages un-passable. So `factual.risky_claim` is intentionally
# NOT in this set; it still blocks PASS via the fail-finding check below.
CRITICAL_FINDING_IDS = {
    "structure.missing_title",
    "structure.missing_script",
    "title.missing",
    "payoff.missing",
    "payoff.weak",
    "script.missing",
    "script.too_thin",
    "thumbnail.promise_mismatch",
    "resolve.suspicious_term",
}


def is_critical_finding(finding_item: Finding, profile: QAProfile) -> bool:
    if finding_item.id == "resolve.suspicious_term" and profile.resolve_terminology != "strict":
        return False
    return finding_item.severity == "fail" and finding_item.id in CRITICAL_FINDING_IDS


def run_checks(package: Package, profile_name: str | None = None) -> GateResult:
    profile = get_profile(profile_name)
    checks = [
        check_expected_structure(package, profile),
        check_title(package, profile),
        check_thumbnail_alignment(package, profile),
        check_viewer_payoff(package),
        check_script_structure(package, profile),
        check_factual_risk(package, profile),
        check_resolve_terms(package, profile),
    ]
    total_score = sum(check.score for check in checks)
    max_score = len(checks) * 5
    failed_checks = [failure for check in checks for failure in check.failed]
    warnings = [warning for check in checks for warning in check.warnings]
    risky_claims = checks[5].details.get("needs_source_manual_verification", [])
    suspicious_terms = checks[6].details.get("suspicious_terms", [])
    findings = [finding_item for check in checks for finding_item in check.findings]
    fail_findings = [finding_item for finding_item in findings if finding_item.severity == "fail"]
    critical_findings = [finding_item for finding_item in findings if is_critical_finding(finding_item, profile)]
    min_pass_score = int(max_score * profile.min_pass_ratio)

    # Warnings are advisory and must NOT block PASS (they still surface in the
    # report for the human). Only critical findings (FAIL), any fail-severity
    # finding, or an under-threshold score gate the result.
    if critical_findings:
        status = "FAIL"
    elif fail_findings or total_score < min_pass_score:
        status = "NEEDS WORK"
    else:
        status = "PASS"

    return GateResult(
        package_title=package.get("title") or "(untitled package)",
        profile=profile.name,
        input_sections_detected=sorted(package.sections),
        created_at=datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
        status=status,
        total_score=total_score,
        max_score=max_score,
        checks=checks,
        failed_checks=failed_checks,
        warnings=warnings,
        risky_claims=risky_claims,
        suspicious_terms=suspicious_terms,
        top_fixes=top_fixes(checks),
    )
