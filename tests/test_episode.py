import json
import tempfile
import unittest
from contextlib import redirect_stdout
from io import StringIO
from pathlib import Path

from creator_qa.cli import main
from creator_qa.episode import parse_episode_json, render_package_markdown_from_file
from creator_qa.rules import run_checks

ROOT = Path(__file__).resolve().parents[1]
GOOD = ROOT / "examples" / "episode-factory" / "resolve-episode-good.json"
WEAK = ROOT / "examples" / "episode-factory" / "resolve-episode-weak.json"


class EpisodeFactoryTests(unittest.TestCase):
    def test_check_episode_json_good_example_works(self) -> None:
        package = parse_episode_json(GOOD)
        result = run_checks(package, "resolve_tutorial")

        self.assertIn(result.status, {"PASS", "NEEDS WORK"})
        self.assertEqual(result.profile, "resolve_tutorial")
        self.assertGreaterEqual(result.total_score, 30)

    def test_check_episode_json_catches_weak_example(self) -> None:
        package = parse_episode_json(WEAK)
        result = run_checks(package, "resolve_tutorial")
        ids = {finding.id for check in result.checks for finding in check.findings}

        self.assertIn(result.status, {"FAIL", "NEEDS WORK"})
        self.assertIn("payoff.missing", ids)
        self.assertIn("factual.risky_claim", ids)

    def test_render_package_creates_expected_sections(self) -> None:
        markdown = render_package_markdown_from_file(GOOD)

        self.assertIn("# Title", markdown)
        self.assertIn("# Thumbnail", markdown)
        self.assertIn("# Hook", markdown)
        self.assertIn("# Viewer Payoff", markdown)
        self.assertIn("# Script", markdown)
        self.assertIn("# Notes", markdown)

    def test_render_package_cli_writes_markdown(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            output = Path(temp_dir) / "episode.md"

            exit_code = main(["render-package", str(GOOD), "--output", str(output)])

            self.assertEqual(exit_code, 0)
            self.assertIn("# Title", output.read_text(encoding="utf-8"))

    def test_missing_optional_json_fields_do_not_crash(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            sample = Path(temp_dir) / "minimal.json"
            sample.write_text(json.dumps({"title": "Fix Resolve Export Audio"}), encoding="utf-8")

            package = parse_episode_json(sample)
            result = run_checks(package, "resolve_tutorial")

            self.assertEqual(package.get("title"), "Fix Resolve Export Audio")
            self.assertGreaterEqual(result.total_score, 0)

    def test_check_episode_json_output_keeps_stable_fields(self) -> None:
        output = StringIO()

        with redirect_stdout(output):
            exit_code = main(["check-episode-json", str(WEAK), "--json"])

        self.assertEqual(exit_code, 1)
        payload = json.loads(output.getvalue())
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
            self.assertIn(key, payload)


if __name__ == "__main__":
    unittest.main()
