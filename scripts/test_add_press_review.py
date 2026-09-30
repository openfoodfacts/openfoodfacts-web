#!/usr/bin/env python3
"""
Unit and integration tests for scripts/add_press_review.py.
"""

import os
import shutil
import tempfile
import unittest
import yaml

from add_press_review import (
    parse_issue_markdown,
    extract_domain,
    clean_acronym_off,
    clean_field_value,
    generate_item_id,
    build_press_item_dict,
    add_press_review_entry,
    VALID_TYPES,
    VALID_SCOPES,
)
from compile_press_review import validate_press_item


class TestAddPressReview(unittest.TestCase):

    def test_extract_domain(self):
        self.assertEqual(extract_domain("https://www.lemonde.fr/article/123"), "lemonde.fr")
        self.assertEqual(extract_domain("http://bbc.co.uk/news"), "bbc.co.uk")
        self.assertEqual(extract_domain("https://radiofrance.fr:443/podcast"), "radiofrance.fr")
        self.assertEqual(extract_domain("sub.domain.com/path"), "sub.domain.com")
        self.assertEqual(extract_domain(""), "")

    def test_clean_acronym_off(self):
        self.assertEqual(clean_acronym_off("Le projet OFF et la santé"), "Le projet Open Food Facts et la santé")
        self.assertEqual(clean_acronym_off("OFFLINE is unaffected"), "OFFLINE is unaffected")
        self.assertEqual(clean_acronym_off("Turn off the lights"), "Turn off the lights")
        self.assertEqual(clean_acronym_off("OFF"), "Open Food Facts")

    def test_clean_field_value(self):
        self.assertEqual(clean_field_value("_No response_"), "")
        self.assertEqual(clean_field_value("None"), "")
        self.assertEqual(clean_field_value("<!-- comment -->Hello"), "Hello")
        self.assertEqual(clean_field_value("Valid text"), "Valid text")

    def test_generate_item_id(self):
        existing = {"2026-09-30-le-monde-nutri-score-et-transparence"}
        # Without collision
        new_id = generate_item_id("2026-09-30", "Le Monde", "Un nouvel article", existing_ids=existing)
        self.assertEqual(new_id, "2026-09-30-le-monde-un-nouvel-article")

        # With collision
        collision_id = generate_item_id("2026-09-30", "Le Monde", "Nutri-Score et transparence", existing_ids=existing)
        self.assertEqual(collision_id, "2026-09-30-le-monde-nutri-score-et-transparence-2")

    def test_parse_issue_markdown_full(self):
        sample_markdown = """
### Article / Segment Title

Des super-pouvoirs dans l'assiette avec OFF

### Media Source

France Inter

### Publication Date (YYYY-MM-DD)

2026-05-18

### URL / Web Link

https://www.radiofrance.fr/franceinter/podcasts/grand-bien-vous-fasse/super-pouvoirs-123

### Media Type

podcast (Podcast / Radio episode / Audio)

### Media Scope

national (National media & mainstream press)

### Language

fr (Français)

### Country

fra (France)

### Author / Journalist

Ali Rebeihi

### Topics Covered

- [X] nutriscore (Nutri-Score)
- [ ] upf (Ultra-processed foods / aliments ultra-transformés)
- [x] open-data (Open data & digital commons)

### Verbatim / Key Quote (optional)

« Open Food Facts révolutionne l'information sur les produits. »

### Editorial Note (optional)

Diffusé à 10h sur France Inter.
"""
        parsed = parse_issue_markdown(sample_markdown)
        self.assertEqual(parsed["title"], "Des super-pouvoirs dans l'assiette avec OFF")
        self.assertEqual(parsed["source"], "France Inter")
        self.assertEqual(parsed["date"], "2026-05-18")
        self.assertEqual(parsed["link"], "https://www.radiofrance.fr/franceinter/podcasts/grand-bien-vous-fasse/super-pouvoirs-123")
        self.assertEqual(parsed["type"], "podcast")
        self.assertEqual(parsed["media_scope"], "national")
        self.assertEqual(parsed["lang"], "fr")
        self.assertEqual(parsed["country"], "fra")
        self.assertEqual(parsed["author"], "Ali Rebeihi")
        self.assertEqual(parsed["topics"], ["nutriscore", "open-data"])
        self.assertEqual(parsed["verbatim"], "« Open Food Facts révolutionne l'information sur les produits. »")
        self.assertEqual(parsed["editorial_note"], "Diffusé à 10h sur France Inter.")

    def test_build_press_item_dict(self):
        item = build_press_item_dict(
            title="Interview du fondateur de OFF",
            source="Le Monde",
            date="2026-08-01",
            link="https://www.lemonde.fr/economie/article/2026/08/01/off.html",
            media_type="article",
            media_scope="national",
            topics=["nutriscore", "open-data"],
            verbatim="OFF a permis d'éclairer le débat.",
            editorial_note="Accessible aux abonnés.",
        )
        self.assertEqual(item["title"], "Interview du fondateur de Open Food Facts")
        self.assertEqual(item["source"], "Le Monde")
        self.assertEqual(item["domain"], "lemonde.fr")
        self.assertEqual(item["raw_type"], "Article")
        self.assertEqual(item["verbatim"], "Open Food Facts a permis d'éclairer le débat.")
        self.assertEqual(item["editorial_note"], "Accessible aux abonnés.")
        self.assertFalse(item["selected"])
        self.assertFalse(item["dead_link"])

    def test_add_press_review_entry_and_validation(self):
        temp_dir = tempfile.mkdtemp()
        try:
            result = add_press_review_entry(
                title="Test Article Title",
                source="Tech Media",
                date="2026-09-30",
                link="https://techmedia.example.com/open-food-facts",
                media_type="article",
                media_scope="specialized",
                lang="en",
                country="gbr",
                topics=["open-data"],
                directory=temp_dir,
            )
            self.assertTrue(result["success"])
            expected_file = os.path.join(temp_dir, f"{result['id']}.yaml")
            self.assertTrue(os.path.isfile(expected_file))

            # Validate against compile_press_review
            with open(expected_file, "r", encoding="utf-8") as f:
                saved = yaml.safe_load(f)
            errs, warns = validate_press_item(saved, expected_file)
            self.assertEqual(errs, [])
        finally:
            shutil.rmtree(temp_dir)


if __name__ == "__main__":
    unittest.main()
