import unittest

from creator_qa.models import Package
from creator_qa.rules import check_factual_risk, check_resolve_terms, run_checks


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


if __name__ == "__main__":
    unittest.main()
