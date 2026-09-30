#!/usr/bin/env python3
"""
Unit and integration tests for scripts/add_scientific_publication.py.
"""

import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
import yaml

from add_scientific_publication import (
    parse_authors,
    get_first_author_surname,
    clean_doi,
    clean_field_value,
    slugify,
    generate_pub_id,
    parse_issue_markdown,
    build_publication_dict,
    add_scientific_publication_entry,
)
from build_scientific_publications import validate_publication


class TestAddScientificPublication(unittest.TestCase):

    def test_parse_authors(self):
        # Comma-separated
        self.assertEqual(
            parse_authors("Chantal Julia, Serge Hercberg"),
            ["Chantal Julia", "Serge Hercberg"],
        )
        # With 'and'
        self.assertEqual(
            parse_authors("Jane Doe and John Smith"),
            ["Jane Doe", "John Smith"],
        )
        # Semicolon-separated
        self.assertEqual(
            parse_authors("A. Dupont; B. Martin; C. Durand"),
            ["A. Dupont", "B. Martin", "C. Durand"],
        )
        # List input
        self.assertEqual(
            parse_authors(["Alice Smith", "Bob Jones"]),
            ["Alice Smith", "Bob Jones"],
        )
        # Empty or placeholder
        self.assertEqual(parse_authors("_No response_"), [])
        self.assertEqual(parse_authors(""), [])

    def test_get_first_author_surname(self):
        self.assertEqual(get_first_author_surname(["Chantal Julia", "Serge Hercberg"]), "julia")
        self.assertEqual(get_first_author_surname(["John von Neumann"]), "neumann")
        self.assertEqual(get_first_author_surname(["Aristotle"]), "aristotle")
        self.assertEqual(get_first_author_surname([]), "author")

    def test_clean_doi(self):
        self.assertEqual(clean_doi("10.3390/foods15152651"), "10.3390/foods15152651")
        self.assertEqual(clean_doi("https://doi.org/10.3390/foods15152651"), "10.3390/foods15152651")
        self.assertEqual(clean_doi("http://dx.doi.org/10.1016/j.appet.2020.104983"), "10.1016/j.appet.2020.104983")
        self.assertEqual(clean_doi("doi: 10.3390/foods15152651"), "10.3390/foods15152651")
        self.assertEqual(clean_doi(""), "")

    def test_clean_field_value(self):
        self.assertEqual(clean_field_value("_No response_"), "")
        self.assertEqual(clean_field_value("None"), "")
        self.assertEqual(clean_field_value("<!-- comment -->Hello"), "Hello")
        self.assertEqual(clean_field_value("Valid text"), "Valid text")

    def test_slugify(self):
        self.assertEqual(slugify("Nutri-Score: Evaluation in France!"), "nutri-score-evaluation-in-france")
        self.assertEqual(slugify("A Very Long Title With More Than Six Words In It"), "a-very-long-title-with-more")

    def test_generate_pub_id(self):
        existing = {"2026-julia-nutri-score-effectiveness"}
        # Without collision
        new_id = generate_pub_id(
            2026,
            ["Chantal Julia"],
            "Front-of-pack Nutrition Label",
            existing_ids=existing,
        )
        self.assertEqual(new_id, "2026-julia-front-of-pack-nutrition-label")

        # With collision
        col_id = generate_pub_id(
            2026,
            ["Chantal Julia"],
            "Nutri Score Effectiveness",
            existing_ids=existing,
        )
        self.assertEqual(col_id, "2026-julia-nutri-score-effectiveness-2")

    def test_parse_issue_markdown_full(self):
        sample_markdown = """
### Paper Title

Nutri-Score: Evidence of the effectiveness of the French front-of-pack nutrition label

### Authors

Chantal Julia, Serge Hercberg

### Publication Year (YYYY)

2026

### Journal / Conference / Publisher

Foods

### DOI (Digital Object Identifier)

10.3390/foods15152651

### Paper URL / Link

https://www.mdpi.com/2304-8158/15/15/2651

### Open Access PDF URL

https://www.mdpi.com/2304-8158/15/15/2651/pdf

### Research Themes / Topics

- [X] nutrition (Nutrition & Diet Quality)
- [ ] ultra_processed (Ultra-processed foods & NOVA classification)
- [x] public_health (Public health policy & epidemiology)

### Open Food Facts Usage & Findings

This study used 15,000 products from Open Food Facts to evaluate the distribution of Nutri-Score grades across the French food market.
"""
        parsed = parse_issue_markdown(sample_markdown)
        self.assertEqual(
            parsed["title"],
            "Nutri-Score: Evidence of the effectiveness of the French front-of-pack nutrition label",
        )
        self.assertEqual(parsed["authors"], ["Chantal Julia", "Serge Hercberg"])
        self.assertEqual(parsed["year"], 2026)
        self.assertEqual(parsed["journal"], "Foods")
        self.assertEqual(parsed["doi"], "10.3390/foods15152651")
        self.assertEqual(parsed["url"], "https://www.mdpi.com/2304-8158/15/15/2651")
        self.assertEqual(parsed["url_pdf"], "https://www.mdpi.com/2304-8158/15/15/2651/pdf")
        self.assertIn("nutrition", parsed["themes"])
        self.assertIn("public_health", parsed["themes"])
        self.assertNotIn("ultra_processed", parsed["themes"])
        self.assertIn("15,000 products from Open Food Facts", parsed["excerpt"])

    def test_build_publication_dict(self):
        doc = build_publication_dict(
            custom_id="2026-julia-nutri-score-evidence",
            title="Nutri-Score: Evidence of the effectiveness",
            authors=["Chantal Julia", "Serge Hercberg"],
            year=2026,
            journal="Foods",
            doi="10.3390/foods15152651",
            url="https://doi.org/10.3390/foods15152651",
            url_pdf="https://www.mdpi.com/pdf",
            themes=["nutrition", "public_health"],
            excerpt="Evaluated 15,000 products.",
        )
        self.assertEqual(doc["id"], "2026-julia-nutri-score-evidence")
        self.assertEqual(doc["year"], 2026)
        self.assertEqual(doc["authors"], ["Chantal Julia", "Serge Hercberg"])
        self.assertEqual(doc["themes"], ["nutrition", "public_health"])
        self.assertEqual(doc["type"], "paper")
        self.assertFalse(doc["featured"])
        self.assertEqual(doc["usage_score"], 2)

    def test_add_publication_entry_and_validation(self):
        temp_dir = tempfile.mkdtemp()
        try:
            result = add_scientific_publication_entry(
                title="Analysis of Sodium Content in Bread Using Open Food Facts",
                authors="Jane Doe, John Smith",
                year=2026,
                journal="Journal of Nutritional Science",
                doi="10.1017/jns.2026.1",
                url="https://doi.org/10.1017/jns.2026.1",
                themes=["nutrition", "public_health"],
                excerpt="Assessed salt levels across 3,000 bread items using the Open Food Facts database.",
                directory=temp_dir,
                do_compile=False,
            )
            self.assertTrue(result["success"], result.get("error"))
            expected_file = os.path.join(temp_dir, f"{result['id']}.yaml")
            self.assertTrue(os.path.isfile(expected_file))

            with open(expected_file, "r", encoding="utf-8") as f:
                saved = yaml.safe_load(f)

            errs, warns = validate_publication(saved, expected_file)
            self.assertEqual(errs, [])
        finally:
            shutil.rmtree(temp_dir)

    def test_dry_run_and_output_json_cli(self):
        temp_out = tempfile.NamedTemporaryFile(suffix=".json", delete=False)
        temp_out.close()
        try:
            cmd = [
                sys.executable,
                os.path.join(os.path.dirname(__file__), "add_scientific_publication.py"),
                "--dry-run",
                "--json",
                "--output-json",
                temp_out.name,
                "--title",
                "Machine Learning for Nutri-Score Estimation",
                "--authors",
                "Alice Wonder, Bob Builder",
                "--year",
                "2026",
                "--journal",
                "IEEE Access",
                "--url",
                "https://ieeexplore.ieee.org/document/123456",
                "--theme",
                "computer_science",
            ]
            proc = subprocess.run(cmd, capture_output=True, text=True)
            self.assertEqual(proc.returncode, 0, f"CLI stderr: {proc.stderr}")

            # stdout must be valid JSON
            out_json = json.loads(proc.stdout)
            self.assertTrue(out_json["success"])
            self.assertTrue(out_json["dry_run"])
            self.assertEqual(out_json["year"], 2026)
            self.assertIn("Alice Wonder", out_json["authors"])

            # file output must also be valid JSON and identical
            with open(temp_out.name, "r", encoding="utf-8") as f:
                file_json = json.load(f)
            self.assertEqual(file_json["id"], out_json["id"])
            self.assertEqual(file_json["title"], out_json["title"])
        finally:
            if os.path.exists(temp_out.name):
                os.remove(temp_out.name)


if __name__ == "__main__":
    unittest.main()
