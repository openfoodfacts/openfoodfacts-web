#!/usr/bin/env python3
"""
Unit tests for scripts/add_scan_party.py
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

from scripts.add_scan_party import (
    slugify,
    clean_field_value,
    clean_dropdown,
    clean_url,
    parse_int_or_none,
    normalize_country,
    parse_issue_markdown,
    build_scan_party_dict,
    add_scan_party,
)
from scripts.compile_scan_parties import validate_scan_party, VALID_TYPES, VALID_STATUSES


class TestAddScanParty(unittest.TestCase):

    def setUp(self):
        self.test_dir = tempfile.mkdtemp(prefix="test_scan_parties_")

    def tearDown(self):
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)

    def test_slugify(self):
        self.assertEqual(slugify("Biomonde Rennes 2026"), "biomonde-rennes-2026")
        self.assertEqual(slugify("Scan Party à Lyon !"), "scan-party-a-lyon")
        self.assertEqual(slugify("What's in my Yogurt?"), "whats-in-my-yogurt")
        self.assertEqual(slugify(""), "")

    def test_clean_field_value(self):
        self.assertEqual(clean_field_value("  Hello World  "), "Hello World")
        self.assertEqual(clean_field_value("_No response_"), "")
        self.assertEqual(clean_field_value("<!-- comment -->Value"), "Value")
        self.assertEqual(clean_field_value(None), "")

    def test_clean_dropdown(self):
        self.assertEqual(clean_dropdown("upcoming (Upcoming Event)"), "upcoming")
        self.assertEqual(clean_dropdown("past (Past / Completed Event)"), "past")
        self.assertEqual(clean_dropdown("completed"), "completed")
        self.assertEqual(clean_dropdown("  Upcoming  "), "upcoming")

    def test_clean_url(self):
        self.assertEqual(clean_url("https://openfoodfacts.org"), "https://openfoodfacts.org")
        self.assertEqual(clean_url("[Link](https://blog.openfoodfacts.org)"), "https://blog.openfoodfacts.org")
        self.assertEqual(clean_url("<https://example.com>"), "https://example.com")
        self.assertIsNone(clean_url("invalid-url"))
        self.assertIsNone(clean_url("_No response_"))

    def test_parse_int_or_none(self):
        self.assertEqual(parse_int_or_none("250"), 250)
        self.assertEqual(parse_int_or_none("1,500"), 1500)
        self.assertEqual(parse_int_or_none("~40 participants"), 40)
        self.assertIsNone(parse_int_or_none(""))
        self.assertIsNone(parse_int_or_none("none"))

    def test_normalize_country(self):
        self.assertEqual(normalize_country("France"), "fra")
        self.assertEqual(normalize_country("United Kingdom"), "gbr")
        self.assertEqual(normalize_country("Spain"), "esp")
        self.assertEqual(normalize_country("Germany"), "deu")
        self.assertEqual(normalize_country("fra"), "fra")
        self.assertEqual(normalize_country(None, "Paris, France"), "fra")

    def test_parse_prefilled_url_markdown(self):
        md = """
### 🎉 Scan Party Title
<!-- Enter event title -->
Super U Lyon Scan Party

### 📅 Date & Time
- Date: 2026-10-15
- Start Time: 14:00

### 📍 Location & Venue
- Venue Name: Super U Lyon
- City: Lyon
- Country: France

### 👤 Organizer
- Organizer Name / Organization: OFF Auvergne-Rhone-Alpes
- Contact Email / Slack handle: contact@off.org

### 📝 Description
<!-- Describe the scan party, target store, or focus -->
Scanning regional yogurts and cheeses.

### 🔗 Registration / Recap Link
- Link: https://meetup.com/events/123
"""
        parsed = parse_issue_markdown(md)
        self.assertEqual(parsed["title"], "Super U Lyon Scan Party")
        self.assertEqual(parsed["date"], "2026-10-15")
        self.assertEqual(parsed["venue"], "Super U Lyon")
        self.assertEqual(parsed["city"], "Lyon")
        self.assertEqual(parsed["country"], "France")
        self.assertEqual(parsed["organizer"], "OFF Auvergne-Rhone-Alpes")
        self.assertEqual(parsed["link"], "https://meetup.com/events/123")
        self.assertEqual(parsed["description"], "Scanning regional yogurts and cheeses.")

    def test_parse_issue_form_markdown(self):
        md = """
### Event Title
Biomonde Rennes Scan Party

### Event Timing / Type
upcoming (Upcoming Event)

### Date (Display format)
November 2026

### Start Date (YYYY-MM-DD)
2026-11-23

### Venue / Location Details
Biomonde Organic Grocery

### City
Rennes

### Country
France

### Organizer / Community Group
Breton Food Data Enthusiasts

### Description
A collaborative Saturday workshop scanning organic Brittany products.

### Registration / Event URL / Recap Link
https://blog.openfoodfacts.org/event

### Tags / Keywords (comma-separated, optional)
organic, rennes, bio
"""
        parsed = parse_issue_markdown(md)
        self.assertEqual(parsed["title"], "Biomonde Rennes Scan Party")
        self.assertEqual(parsed["type"], "upcoming")
        self.assertEqual(parsed["date"], "November 2026")
        self.assertEqual(parsed["start_date"], "2026-11-23")
        self.assertEqual(parsed["venue"], "Biomonde Organic Grocery")
        self.assertEqual(parsed["city"], "Rennes")
        self.assertEqual(parsed["country"], "France")
        self.assertEqual(parsed["tags"], "organic, rennes, bio")

    def test_build_scan_party_dict_and_validation(self):
        item = build_scan_party_dict(
            title="Biomonde Rennes Scan Party",
            event_type="upcoming",
            date="November 2026",
            start_date="2026-11-23",
            venue="Biomonde Organic Grocery",
            city="Rennes",
            country="France",
            description="Collaborative workshop scanning organic items.",
            link="https://example.com/event",
            tags=["organic", "bio"],
        )
        self.assertEqual(item["id"], "biomonde-rennes-scan-party-2026")
        self.assertEqual(item["type"], "upcoming")
        self.assertEqual(item["status"], "upcoming")
        self.assertEqual(item["location"], "Rennes, France")
        self.assertEqual(item["country"], "fra")
        self.assertIn("upcoming", item["tags"])

        temp_path = os.path.join(self.test_dir, f"{item['id']}.yaml")
        errors, warnings = validate_scan_party(item, temp_path)
        self.assertEqual(errors, [])

    def test_add_scan_party_write_and_dry_run(self):
        # Dry run should not write file
        dry_result = add_scan_party(
            title="Paris Tech Scan Party",
            event_type="upcoming",
            date="2026-12-01",
            venue="La Cantine",
            city="Paris",
            country="fra",
            description="Tech community scanning food data.",
            directory=self.test_dir,
            dry_run=True,
        )
        self.assertTrue(dry_result["success"])
        self.assertTrue(dry_result["dry_run"])
        expected_file = os.path.join(self.test_dir, f"{dry_result['id']}.yaml")
        self.assertFalse(os.path.exists(expected_file))

        # Real run should write YAML file
        result = add_scan_party(
            title="Paris Tech Scan Party",
            event_type="upcoming",
            date="2026-12-01",
            venue="La Cantine",
            city="Paris",
            country="fra",
            description="Tech community scanning food data.",
            directory=self.test_dir,
            dry_run=False,
        )
        self.assertTrue(result["success"])
        self.assertTrue(os.path.exists(expected_file))

        # Read back YAML and validate
        with open(expected_file, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)
        self.assertEqual(data["title"], "Paris Tech Scan Party")
        self.assertEqual(data["venue"], "La Cantine")
        self.assertEqual(data["city"], "Paris")
        self.assertEqual(data["country"], "fra")

        errors, _ = validate_scan_party(data, expected_file)
        self.assertEqual(errors, [])


if __name__ == "__main__":
    unittest.main()
