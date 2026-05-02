import unittest
from contextlib import redirect_stdout
from io import StringIO
from pathlib import Path

from creator_qa.cli import main
from creator_qa.models import Package
from creator_qa.parser import parse_markdown
from creator_qa.rules import check_factual_risk, check_resolve_terms, run_checks

ROOT = Path(__file__).resolve().parents[1]


def fixture_result(name: str, profile: str | None = "resolve_tutorial"):
    package = parse_markdown(ROOT / "examples" / "failures" / name)
    return run_checks(package, profile)


def finding_ids(result) -> set[str]:
    return {finding.id for check in result.checks for finding in check.findings}


class RulesTests(unittest.TestCase):
    def test_gate_passes_structured_sourced_package(self) -> None:
        package = Package(
            path="sample.md",
            sections={
                "title": "Fix Flat DaVinci Resolve Exports with Color Management",
                "thumbnail": "Fix Flat Exports",
                "hook": "By the end, you will know the setting to check so you can export cleaner footage.",
                "script": """
## Hook
In this video you will fix flat exports.
## Problem / Context
When your timeline and export settings do not match, the image can look wrong.
## Promised Outcome
By the end, you will know what to inspect.
## Steps
1. Open Project Settings.
2. Check Color Management.
## Demonstration / Proof
Show a before and after export.
## Recap / Takeaway
The takeaway is to check the pipeline first.
## Call To Action
Comment with your format.
""",
                "notes": "Sources / manual verification: Resolve version should be checked.",
            },
        )

        result = run_checks(package)

        self.assertIn(result.status, {"PASS", "NEEDS WORK"})
        self.assertGreaterEqual(result.total_score, 24)

    def test_factual_risk_requires_source_notes(self) -> None:
        package = Package(
            path="sample.md",
            sections={
                "title": "Best Resolve Export Settings",
                "script": "This is always the fastest GPU render workflow in Resolve 20.",
            },
        )

        result = check_factual_risk(package)

        self.assertTrue(result.failed)
        self.assertTrue(result.details["needs_source_manual_verification"])

    def test_resolve_suspicious_terms_are_flagged(self) -> None:
        package = Package(
            path="sample.md",
            sections={"script": "Open the render page and then the sound page."},
        )

        result = check_resolve_terms(package)

        self.assertTrue(result.failed)
        self.assertIn("render page", result.details["suspicious_terms"][0])

    def test_gate_json_shape_includes_v02_fields(self) -> None:
        package = Package(
            path="sample.md",
            sections={
                "title": "Best Tips",
                "thumbnail": "Best Export Settings For Fast Renders In Resolve Timeline",
                "script": "This is always the fastest workflow in the render page.",
            },
        )

        output = run_checks(package).to_dict()

        for key in [
            "overall_result",
            "profile",
            "total_score",
            "max_score",
            "category_scores",
            "findings",
            "warnings",
            "risky_claims",
            "suspicious_terms",
            "top_fixes",
            "input_sections_detected",
            "created_at",
        ]:
            self.assertIn(key, output)
        self.assertTrue(output["findings"])
        self.assertIn("id", output["findings"][0])
        self.assertIn("severity", output["findings"][0])
        self.assertIn("category", output["findings"][0])
        self.assertIn("message", output["findings"][0])
        self.assertIn("suggestion", output["findings"][0])

    def test_stable_rule_ids_are_emitted(self) -> None:
        package = Package(
            path="sample.md",
            sections={
                "title": "Best Tips",
                "thumbnail": "Best Export Settings For Fast Renders In Resolve Timeline",
                "script": "This is always the fastest workflow in the render page.",
            },
        )

        result = run_checks(package)
        ids = {finding.id for check in result.checks for finding in check.findings}

        self.assertIn("title.no_viewer_benefit", ids)
        self.assertIn("thumbnail.too_much_text", ids)
        self.assertIn("payoff.missing", ids)
        self.assertIn("script.no_hook", ids)
        self.assertIn("script.no_steps", ids)
        self.assertIn("script.no_demo_or_proof", ids)
        self.assertIn("factual.risky_claim", ids)
        self.assertIn("resolve.suspicious_term", ids)

    def test_bad_title_fixture_produces_title_finding(self) -> None:
        result = fixture_result("bad-title-sample.md")

        self.assertIn("title.vague", finding_ids(result))
        self.assertIn(result.status, {"FAIL", "NEEDS WORK"})

    def test_thumbnail_mismatch_fixture_produces_mismatch_finding(self) -> None:
        result = fixture_result("thumbnail-mismatch-sample.md")

        self.assertIn("thumbnail.promise_mismatch", finding_ids(result))
        self.assertEqual(result.status, "FAIL")

    def test_missing_payoff_fixture_fails_or_needs_work(self) -> None:
        result = fixture_result("missing-viewer-payoff-sample.md")

        self.assertIn("payoff.missing", finding_ids(result))
        self.assertIn(result.status, {"FAIL", "NEEDS WORK"})

    def test_weak_script_structure_fixture_is_caught(self) -> None:
        result = fixture_result("weak-script-structure-sample.md")
        ids = finding_ids(result)

        self.assertIn("script.too_thin", ids)
        self.assertIn("script.no_steps", ids)
        self.assertEqual(result.status, "FAIL")

    def test_risky_resolve_claims_fixture_lists_claims(self) -> None:
        result = fixture_result("resolve-risky-claims-sample.md")

        self.assertIn("factual.risky_claim", finding_ids(result))
        self.assertTrue(result.risky_claims)
        self.assertEqual(result.status, "FAIL")

    def test_suspicious_resolve_terms_fixture_lists_terms(self) -> None:
        result = fixture_result("suspicious-resolve-terms-sample.md")

        self.assertIn("resolve.suspicious_term", finding_ids(result))
        self.assertTrue(result.suspicious_terms)
        self.assertEqual(result.status, "FAIL")

    def test_resolve_tutorial_profile_works(self) -> None:
        output = StringIO()
        input_path = ROOT / "examples" / "failures" / "bad-title-sample.md"

        with redirect_stdout(output):
            exit_code = main(["check", str(input_path), "--profile", "resolve_tutorial", "--json"])

        self.assertEqual(exit_code, 1)
        self.assertIn('"profile": "resolve_tutorial"', output.getvalue())

        result = fixture_result("bad-title-sample.md", "resolve_tutorial")
        self.assertEqual(result.profile, "resolve_tutorial")
        self.assertIn("Expected package structure", [check.name for check in result.checks])

    def test_default_profile_still_works(self) -> None:
        package = parse_markdown(ROOT / "examples" / "resolve-tutorial-sample.md")
        result = run_checks(package)

        self.assertEqual(result.profile, "resolve_tutorial")
        self.assertGreater(result.total_score, 0)

    def test_profile_required_section_failure_is_caught(self) -> None:
        package = Package(
            path="sample.md",
            sections={
                "title": "Fix DaVinci Resolve Exports Fast",
                "thumbnail": "Fix Exports",
                "hook": "By the end, you will know what to check.",
            },
        )

        result = run_checks(package, "resolve_tutorial")

        self.assertIn("structure.missing_script", finding_ids(result))
        self.assertEqual(result.status, "FAIL")


if __name__ == "__main__":
    unittest.main()
