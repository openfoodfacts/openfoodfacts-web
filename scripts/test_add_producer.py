#!/usr/bin/env python3
"""
Unit tests for scripts/add_producer.py and scripts/compile_producers.py
"""

import os
import shutil
import sys
import tempfile
import unittest
import yaml

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)
if os.path.dirname(__file__) not in sys.path:
    sys.path.insert(0, os.path.dirname(__file__))

from add_producer import (
    slugify,
    clean_url,
    parse_issue_markdown,
    add_producer,
)
from compile_producers import validate_producer, VALID_CATEGORIES, VALID_COUNTRIES


class TestAddProducer(unittest.TestCase):

    def test_slugify(self):
        self.assertEqual(slugify("Carrefour Bio"), "carrefour-bio")
        self.assertEqual(slugify("Fleury Michon!"), "fleury-michon")
        self.assertEqual(slugify("Ben & Jerry's"), "ben-jerry-s")
        self.assertEqual(slugify(""), "")

    def test_clean_url(self):
        self.assertEqual(clean_url("https://example.com"), "https://example.com")
        self.assertEqual(clean_url("[Website](https://example.com)"), "https://example.com")
        self.assertEqual(clean_url("<https://example.com>"), "https://example.com")
        self.assertIsNone(clean_url("none"))
        self.assertIsNone(clean_url("not-a-url"))

    def test_parse_issue_markdown(self):
        markdown = """
### Brand or Producer Name
BioVillage

### Parent Company / Owner
E.Leclerc / Scamark

### Primary Category
Organic & Local

### Country Code (ISO 3-letter)
fra

### Country Label
France

### Data Source ID
producer-scamark

### Official Website URL
https://www.e.leclerc

### Logo URL
https://example.com/logo.svg

### Products Contributed Count
5300

### Summary Description
Marque bio repère de l'enseigne E.Leclerc
"""
        parsed = parse_issue_markdown(markdown)
        self.assertEqual(parsed.get("name"), "BioVillage")
        self.assertEqual(parsed.get("owner"), "E.Leclerc / Scamark")
        self.assertEqual(parsed.get("category"), "Organic & Local")
        self.assertEqual(parsed.get("country"), "fra")
        self.assertEqual(parsed.get("country_label"), "France")
        self.assertEqual(parsed.get("producer_id"), "producer-scamark")
        self.assertEqual(parsed.get("website"), "https://www.e.leclerc")
        self.assertEqual(parsed.get("products_count"), 5300)

    def test_parse_issue_markdown_with_update_and_shared_data(self):
        markdown = """
### Brand or Producer Name
Danone Transparency

### Parent Company / Owner
Danone Group

### Primary Category
Dairy & Cheese

### Country Code (ISO 3-letter)
fra

### Data Source ID
producer-danone-france

### Last Update Date
2026-10-08

### Data Shared with Open Food Facts
- [x] basic_data (Product name, brand, barcode)
- [x] nutrition (Nutritional values)
- [x] ingredients (Ingredients and allergens)
- [ ] front_photo (Front package photo)
- [x] packaging_data (Packaging components)

### Summary Description
Exemplary dairy brand sharing full nutrition, ingredients and packaging specs.
"""
        parsed = parse_issue_markdown(markdown)
        self.assertEqual(parsed.get("name"), "Danone Transparency")
        self.assertEqual(parsed.get("last_update"), "2026-10-08")
        self.assertIn("basic_data", parsed.get("data_shared", []))
        self.assertIn("nutrition", parsed.get("data_shared", []))
        self.assertIn("ingredients", parsed.get("data_shared", []))
        self.assertIn("packaging_data", parsed.get("data_shared", []))
        self.assertNotIn("front_photo", parsed.get("data_shared", []))

    def test_validate_producer_valid(self):
        valid = {
            "id": "test-brand",
            "name": "Test Brand",
            "owner": "Test Group",
            "category": "Dairy & Cheese",
            "country": "fra",
            "producer_id": "producer-test-brand",
            "products_count": 120,
            "featured": False,
            "last_update": "2026-10-08",
            "data_shared": ["nutrition", "ingredients", "basic_data"]
        }
        errors, warnings = validate_producer(valid, "/tmp/test-brand.yaml")
        self.assertEqual(errors, [])
        self.assertEqual(warnings, [])

    def test_validate_producer_invalid(self):
        invalid = {
            "id": "wrong-id",
            "name": "",
            "category": "Dairy & Cheese",
            "data_shared": "not-a-list"
        }
        errors, warnings = validate_producer(invalid, "/tmp/test-brand.yaml")
        self.assertTrue(len(errors) > 0)
        # Missing owner, name empty, id doesn't match stem, data_shared not a list

    def test_add_producer_dry_run(self):
        class MockArgs:
            id = "mock-brand"
            name = "Mock Brand"
            owner = "Mock Owner"
            category = "Beverages"
            country = "fra"
            country_label = "France"
            producer_id = "producer-mock-brand"
            off_url = "https://world.openfoodfacts.org/facets/data-sources/producer-mock-brand"
            website = "https://mock.example.com"
            logo_url = "https://mock.example.com/logo.png"
            description = "A mock beverage producer"
            products_count = 50
            featured = False
            last_update = "2026-10-08"
            data_shared = "nutrition, ingredients, basic_data"
            dry_run = True
            compile = False
            from_env = False
            from_issue_file = None

        res = add_producer(MockArgs())
        self.assertTrue(res.get("success"))
        self.assertEqual(res.get("id"), "mock-brand")
        self.assertEqual(res.get("name"), "Mock Brand")
        self.assertEqual(res.get("data", {}).get("last_update"), "2026-10-08")
        self.assertEqual(res.get("data", {}).get("data_shared"), ["nutrition", "ingredients", "basic_data"])


if __name__ == "__main__":
    unittest.main()
