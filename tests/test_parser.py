import tempfile
import unittest
from pathlib import Path

from creator_qa.parser import parse_markdown


class ParserTests(unittest.TestCase):
    def test_parse_known_sections(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            sample = Path(temp_dir) / "input.md"
            sample.write_text(
                "# Title\nA Clear Title\n\n# Thumbnail\nShort Text\n\n# Script\nBody\n",
                encoding="utf-8",
            )

            package = parse_markdown(sample)

        self.assertEqual(package.get("title"), "A Clear Title")
        self.assertEqual(package.get("thumbnail"), "Short Text")
        self.assertEqual(package.get("script"), "Body")

    def test_parse_preamble_as_notes(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            sample = Path(temp_dir) / "input.md"
            sample.write_text("Loose note\n\n# Title\nA title\n", encoding="utf-8")

            package = parse_markdown(sample)

        self.assertIn("Loose note", package.get("notes"))


if __name__ == "__main__":
    unittest.main()
