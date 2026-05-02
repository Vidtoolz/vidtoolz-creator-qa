import unittest

from creator_qa.models import Package
from creator_qa.report import render_hermes_report, render_linear_report
from creator_qa.rules import run_checks


class ReportTests(unittest.TestCase):
    def test_hermes_report_generation(self) -> None:
        package = Package(
            path="sample.md",
            sections={
                "title": "Best Tips",
                "thumbnail": "Everything You Need To Know About The Best Export Settings",
                "script": "This is always the fastest workflow in the render page.",
            },
        )

        report = render_hermes_report(run_checks(package))

        self.assertIn("# Creator QA Memory Report", report)
        self.assertIn("Checked package title: Best Tips", report)
        self.assertIn("Failed categories:", report)
        self.assertIn("Risky Factual Claims", report)
        self.assertIn("Suspicious Resolve Terms", report)
        self.assertIn("Recommended next action:", report)

    def test_linear_report_generation(self) -> None:
        package = Package(
            path="sample.md",
            sections={
                "title": "Best Tips",
                "thumbnail": "Everything You Need To Know About The Best Export Settings",
                "script": "This is always the fastest workflow in the render page.",
            },
        )

        report = render_linear_report(run_checks(package))

        self.assertIn("## Summary", report)
        self.assertIn("## Result", report)
        self.assertIn("## Failed Checks", report)
        self.assertIn("## Action Checklist", report)
        self.assertIn("## QA Evidence", report)
        self.assertIn("Finding IDs:", report)


if __name__ == "__main__":
    unittest.main()
