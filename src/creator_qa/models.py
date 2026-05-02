"""Data models for Creator QA."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class Package:
    """Parsed Markdown creator package."""

    path: str
    sections: dict[str, str]

    def get(self, name: str) -> str:
        return self.sections.get(name.lower(), "").strip()

    @property
    def combined_text(self) -> str:
        return "\n\n".join(value for value in self.sections.values() if value.strip())


@dataclass(frozen=True)
class Finding:
    """Stable machine-readable QA finding."""

    id: str
    severity: str
    category: str
    message: str
    suggestion: str

    def to_dict(self) -> dict[str, str]:
        return {
            "id": self.id,
            "severity": self.severity,
            "category": self.category,
            "message": self.message,
            "suggestion": self.suggestion,
        }


@dataclass
class CheckResult:
    """Result for a single check category."""

    name: str
    score: int
    failed: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    details: dict[str, Any] = field(default_factory=dict)
    findings: list[Finding] = field(default_factory=list)

    @property
    def passed(self) -> bool:
        return not self.failed


@dataclass
class GateResult:
    """Overall packaging gate result."""

    package_title: str
    profile: str
    input_sections_detected: list[str]
    created_at: str
    status: str
    total_score: int
    max_score: int
    checks: list[CheckResult]
    failed_checks: list[str]
    warnings: list[str]
    risky_claims: list[str]
    suspicious_terms: list[str]
    top_fixes: list[str]

    def to_dict(self) -> dict[str, Any]:
        return {
            "overall_result": self.status,
            "profile": self.profile,
            "total_score": self.total_score,
            "max_score": self.max_score,
            "category_scores": {check.name: check.score for check in self.checks},
            "findings": [finding.to_dict() for check in self.checks for finding in check.findings],
            "failed_checks": self.failed_checks,
            "warnings": self.warnings,
            "risky_claims": self.risky_claims,
            "suspicious_terms": self.suspicious_terms,
            "top_fixes": self.top_fixes,
            "input_sections_detected": self.input_sections_detected,
            "created_at": self.created_at,
            "package_title": self.package_title,
            "risky_factual_claims": self.risky_claims,
            "suspicious_resolve_terms": self.suspicious_terms,
            "top_3_recommended_fixes": self.top_fixes,
            "checks": [
                {
                    "name": check.name,
                    "score": check.score,
                    "failed": check.failed,
                    "warnings": check.warnings,
                    "findings": [finding.to_dict() for finding in check.findings],
                    "details": check.details,
                }
                for check in self.checks
            ],
        }
