"""Deterministic v0.1 rule checks for Creator QA."""

from __future__ import annotations

import json
import re
from pathlib import Path

from .models import CheckResult, GateResult, Package

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
RISK_PATTERNS = [
    r"\balways\b",
    r"\bnever\b",
    r"\bbest\b",
    r"\bfastest\b",
    r"\bfirst\b",
    r"\bonly\b",
    r"\bv?\d+\.\d+(?:\.\d+)?\b",
    r"\bversion\b",
    r"\$\s?\d+(?:\.\d{2})?\b",
    r"\b\d+(?:\.\d+)?\s?(?:usd|eur|gbp|dollars|euros)\b",
    r"\bcompatible with\b",
    r"\bworks with\b",
    r"\bsupports\b",
    r"\bresolve\b.*\b(feature|supports|requires|added|removed)\b",
    r"\b(codec|h\.?264|h\.?265|prores|dnx|gpu|cuda|metal|performance|render speed|fps)\b",
]
SOURCE_HINTS = ["source:", "sources:", "citation:", "verified:", "manual verification:", "needs source"]
WORD_RE = re.compile(r"[a-zA-Z0-9']+")


def words(text: str) -> list[str]:
    return [word.lower() for word in WORD_RE.findall(text)]


def score_from_issues(issue_count: int, max_score: int = 5) -> int:
    return max(0, max_score - issue_count)


def check_title(package: Package) -> CheckResult:
    title = package.get("title")
    failed: list[str] = []
    warnings: list[str] = []
    title_words = words(title)

    if not title:
        failed.append("Title section is missing.")
    if len(title) > 70:
        failed.append("Title is too long for clear YouTube packaging.")
    if len(title_words) < 4:
        failed.append("Title is too short to clearly identify topic and benefit.")
    if any(phrase in title.lower() for phrase in VAGUE_PHRASES):
        failed.append("Title uses vague packaging language.")
    if title_words and len(set(title_words) - GENERIC_TITLE_WORDS) < 3:
        failed.append("Title sounds generic and does not clearly identify the topic.")
    if not any(word in BENEFIT_WORDS for word in title_words):
        failed.append("Title does not state a clear viewer benefit.")
    if "resolve" not in title.lower() and "davinci" not in title.lower():
        warnings.append("Title may not identify the Resolve/video editing topic clearly.")

    return CheckResult("YouTube title clarity", score_from_issues(len(failed)), failed, warnings)


def check_thumbnail_alignment(package: Package) -> CheckResult:
    title = package.get("title")
    thumbnail = package.get("thumbnail")
    failed: list[str] = []
    warnings: list[str] = []
    title_words = set(words(title)) - GENERIC_TITLE_WORDS
    thumb_words = set(words(thumbnail)) - GENERIC_TITLE_WORDS
    overlap = title_words & thumb_words

    if not thumbnail:
        failed.append("Thumbnail section is missing.")
    if len(words(thumbnail)) > 8:
        failed.append("Thumbnail text is too long.")
    if title_words and thumb_words and not overlap:
        failed.append("Title and thumbnail text do not share a clear promise.")
    if not any(word in thumb_words for word in BENEFIT_WORDS | {"before", "after", "timeline", "nodes", "export", "grade"}):
        failed.append("Thumbnail has no concrete visual promise.")
    if len(thumb_words) <= 1:
        warnings.append("Thumbnail text may be too thin to carry a promise.")

    return CheckResult(
        "Thumbnail / title promise alignment",
        score_from_issues(len(failed)),
        failed,
        warnings,
        {"shared_terms": sorted(overlap)},
    )


def check_viewer_payoff(package: Package) -> CheckResult:
    combined = "\n".join([package.get("title"), package.get("thumbnail"), package.get("hook"), package.get("script")])
    lower = combined.lower()
    failed: list[str] = []
    warnings: list[str] = []

    has_payoff = any(re.search(pattern, lower, re.MULTILINE) for pattern in VIEWER_PAYOFF_PATTERNS)
    if not has_payoff:
        failed.append("Viewer payoff is missing or unclear.")
    if any(phrase in lower for phrase in CREATOR_CENTERED) and not has_payoff:
        failed.append("Payoff is creator-centered instead of viewer-centered.")
    elif any(phrase in lower for phrase in CREATOR_CENTERED):
        warnings.append("Some payoff language is creator-centered; keep the result viewer-centered.")

    return CheckResult("Viewer payoff", score_from_issues(len(failed) * 2), failed, warnings)


def check_script_structure(package: Package) -> CheckResult:
    script = "\n".join([package.get("hook"), package.get("script")]).lower()
    failed: list[str] = []
    present: list[str] = []

    if not script.strip():
        failed.append("Hook and Script sections are missing.")
    for part, patterns in STRUCTURE_PATTERNS.items():
        if any(re.search(pattern, script, re.MULTILINE | re.DOTALL) for pattern in patterns):
            present.append(part)
        else:
            failed.append(f"Missing script structure part: {part}.")

    missing_count = len(STRUCTURE_PATTERNS) - len(present)
    score = 0 if not script.strip() else max(0, 5 - missing_count)
    return CheckResult("Script structure", score, failed, [], {"present": present})


def has_source_notes(package: Package) -> bool:
    notes = package.get("notes").lower()
    return any(hint in notes for hint in SOURCE_HINTS)


def find_risky_claims(text: str) -> list[str]:
    claims: list[str] = []
    for line in text.splitlines():
        stripped = line.strip()
        if not stripped:
            continue
        stripped = re.sub(r"^[-*]\s+", "", stripped)
        lower = stripped.lower()
        if any(re.search(pattern, lower) for pattern in RISK_PATTERNS):
            claims.append(stripped)
    return claims


def check_factual_risk(package: Package) -> CheckResult:
    claims = find_risky_claims(package.combined_text)
    sourced = has_source_notes(package)
    failed: list[str] = []
    warnings: list[str] = []
    if claims and not sourced:
        failed.append("Risky factual claims need source notes or manual verification.")
    elif claims:
        warnings.append("Risky factual claims detected; source notes are present.")
    risk_score = max(0, 5 - min(5, len(claims)))
    return CheckResult(
        "Factual-claim risk",
        risk_score,
        failed,
        warnings,
        {"needs_source_manual_verification": claims},
    )


def load_resolve_lexicon(path: Path = DATA_PATH) -> dict[str, object]:
    return json.loads(path.read_text(encoding="utf-8"))


def check_resolve_terms(package: Package) -> CheckResult:
    lexicon = load_resolve_lexicon()
    suspicious_map: dict[str, str] = lexicon.get("suspicious_terms", {})  # type: ignore[assignment]
    text = package.combined_text.lower()
    suspicious: list[str] = []
    for bad_term, suggestion in suspicious_map.items():
        if re.search(rf"\b{re.escape(bad_term.lower())}\b", text):
            suspicious.append(f"{bad_term} -> {suggestion}")

    failed = [f"Suspicious Resolve term: {item}" for item in suspicious]
    score = score_from_issues(len(failed))
    return CheckResult("Resolve terminology accuracy", score, failed, [], {"suspicious_terms": suspicious})


def top_fixes(checks: list[CheckResult]) -> list[str]:
    fixes: list[str] = []
    priority = [
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


def run_checks(package: Package) -> GateResult:
    checks = [
        check_title(package),
        check_thumbnail_alignment(package),
        check_viewer_payoff(package),
        check_script_structure(package),
        check_factual_risk(package),
        check_resolve_terms(package),
    ]
    total_score = sum(check.score for check in checks)
    max_score = len(checks) * 5
    failed_checks = [failure for check in checks for failure in check.failed]
    warnings = [warning for check in checks for warning in check.warnings]
    risky_claims = checks[4].details.get("needs_source_manual_verification", [])
    suspicious_terms = checks[5].details.get("suspicious_terms", [])

    hard_fail = (
        bool(checks[2].failed)
        or checks[3].score <= 1
        or bool(checks[4].failed)
    )
    if hard_fail or total_score < 18:
        status = "FAIL"
    elif failed_checks or total_score < 24:
        status = "NEEDS WORK"
    else:
        status = "PASS"

    return GateResult(
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
