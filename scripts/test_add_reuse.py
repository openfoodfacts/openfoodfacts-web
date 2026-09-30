#!/usr/bin/env python3
"""
Unit tests for scripts/add_reuse.py
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

try:
    from scripts.add_reuse import (
        slugify,
        clean_dropdown,
        clean_url,
        extract_domain,
        parse_bool,
        parse_issue_markdown,
        format_reuse_dict,
        add_reuse,
    )
    from scripts.compile_reuses import validate_reuse, VALID_THEMES, VALID_PROJECTS
except ImportError:
    from add_reuse import (
        slugify,
        clean_dropdown,
        clean_url,
        extract_domain,
        parse_bool,
        parse_issue_markdown,
        format_reuse_dict,
        add_reuse,
    )
    from compile_reuses import validate_reuse, VALID_THEMES, VALID_PROJECTS


class TestAddReuse(unittest.TestCase):

    def test_slugify(self):
        self.assertEqual(slugify("Open Prices!"), "open-prices")
        self.assertEqual(slugify("Scan & Eat 2026"), "scan-eat-2026")
        self.assertEqual(slugify("Yuka"), "yuka")
        self.assertEqual(slugify(""), "")

    def test_clean_dropdown(self):
        self.assertEqual(clean_dropdown("nutrition (Nutrition & General Health)"), "nutrition")
        self.assertEqual(clean_dropdown("openfoodfacts (Open Food Facts - Food & Beverages)"), "openfoodfacts")
        self.assertEqual(clean_dropdown("  environment  "), "environment")

    def test_clean_url(self):
        self.assertEqual(clean_url("https://example.com"), "https://example.com")
        self.assertEqual(clean_url("http://example.com/app"), "http://example.com/app")
        self.assertEqual(clean_url("[Website](https://example.com)"), "https://example.com")
        self.assertIsNone(clean_url("_No response_"))
        self.assertIsNone(clean_url("None"))
        self.assertIsNone(clean_url("not-a-url"))

    def test_extract_domain(self):
        self.assertEqual(extract_domain("https://www.example.com/path"), "example.com")
        self.assertEqual(extract_domain("https://sub.domain.org/foo/bar"), "sub.domain.org")
        self.assertIsNone(extract_domain(None))

    def test_parse_bool(self):
        self.assertTrue(parse_bool("Yes"))
        self.assertTrue(parse_bool("true"))
        self.assertTrue(parse_bool("[x]"))
        self.assertFalse(parse_bool("No"))
        self.assertFalse(parse_bool("false"))
        self.assertFalse(parse_bool("_No response_"))
        self.assertTrue(parse_bool("_No response_", default=True))

    def test_parse_issue_markdown_full(self):
        issue_body = """
### Application / Reuse Name

EcoFood Scanner

### Tagline / One-line Summary

Instant environmental and nutritional score scanner

### Detailed Description

EcoFood Scanner allows shoppers to scan grocery barcodes to view eco-score, carbon footprint, and recyclability. Powered by Open Food Facts.

### Primary Theme

environment (Environment & Eco-Score)

### Secondary Themes (optional)

nutrition, additives

### Open Food Facts Project

openfoodfacts (Open Food Facts - Food & Beverages)

### Website URL

https://ecofood.example.com

### Google Play Store URL (optional)

https://play.google.com/store/apps/details?id=com.ecofood.scanner

### Apple App Store URL (optional)

https://apps.apple.com/app/ecofood/id123456789

### F-Droid URL (optional)

_No response_

### Source Code / GitHub URL (optional)

https://github.com/ecofood/scanner

### Country Code (ISO 3-letter)

fra

### Country / Territory Label

France

### Is this project Open Source?

Yes (Open Source)

### License Name

GPLv3

### Does it contribute data back to Open Food Facts?

Yes

### Does it contribute product photos back?

Yes

### Is it ODbL compliant?

Yes (Compliant with ODbL)

### App Icon or Logo URL (optional)

https://ecofood.example.com/logo.png

### Keywords / Search Tags (optional)

scanner, eco-score, carbon footprint, organic
"""
        data = parse_issue_markdown(issue_body)
        self.assertEqual(data["name"], "EcoFood Scanner")
        self.assertEqual(data["tagline"], "Instant environmental and nutritional score scanner")
        self.assertEqual(data["theme"], "environment")
        self.assertEqual(data["project"], "openfoodfacts")
        self.assertEqual(data["website"], "https://ecofood.example.com")
        self.assertEqual(data["play_store"], "https://play.google.com/store/apps/details?id=com.ecofood.scanner")
        self.assertEqual(data["app_store"], "https://apps.apple.com/app/ecofood/id123456789")
        self.assertIsNone(data.get("fdroid"))
        self.assertEqual(data["github"], "https://github.com/ecofood/scanner")
        self.assertEqual(data["country"], "fra")
        self.assertEqual(data["country_label"], "France")
        self.assertTrue(data["open_source"])
        self.assertEqual(data["license"], "GPLv3")
        self.assertTrue(data["contributes_data"])
        self.assertTrue(data["contributes_photos"])
        self.assertTrue(data["odbl_compliant"])

    def test_format_reuse_dict_and_validation(self):
        raw = {
            "name": "Quick Food App",
            "tagline": "A fast food analyzer",
            "description": "Analyzes food items with Open Food Facts data.",
            "theme": "nutrition",
            "secondary_themes": "allergies, vegan",
            "website": "https://quickfood.org",
            "country": "usa",
            "country_label": "United States",
            "open_source": True,
            "license": "MIT",
            "contributes_data": True,
            "contributes_photos": False,
            "odbl_compliant": True,
            "keywords": "scanner, quick",
        }
        item = format_reuse_dict(raw)
        self.assertEqual(item["id"], "quick-food-app")
        self.assertEqual(item["theme"], "nutrition")
        self.assertEqual(item["themes"], ["nutrition", "allergies", "vegan"])
        self.assertEqual(item["domain"], "quickfood.org")
        self.assertTrue(item["open_source"])
        self.assertTrue(item["contributes_data"])
        self.assertFalse(item["contributes_photos"])
        self.assertIn("quick-food-app", item["keywords"])
        self.assertIn("nutrition", item["keywords"])

        # Validate with compile_reuses.validate_reuse
        errors, warnings = validate_reuse(item, "data/reuses/quick-food-app.yaml")
        self.assertEqual(errors, [])

    def test_add_reuse_in_temp_dir(self):
        temp_dir = tempfile.mkdtemp()
        try:
            import scripts.add_reuse as add_reuse_module
            original_reuses_dir = add_reuse_module.REUSES_DIR
            add_reuse_module.REUSES_DIR = temp_dir

            raw = {
                "name": "Temp Test App",
                "tagline": "Temporary application for unit test",
                "description": "Tests adding reuse into folder.",
                "theme": "tools",
                "website": "https://temp-test.org",
            }
            res = add_reuse(raw, reuse_id="temp-test-app", dry_run=False, do_compile=False)
            self.assertTrue(res["success"])
            self.assertEqual(res["id"], "temp-test-app")

            target_file = os.path.join(temp_dir, "temp-test-app.yaml")
            self.assertTrue(os.path.exists(target_file))

            with open(target_file, "r", encoding="utf-8") as f:
                loaded = yaml.safe_load(f)
            self.assertEqual(loaded["name"], "Temp Test App")
            self.assertEqual(loaded["theme"], "tools")
            self.assertEqual(loaded["domain"], "temp-test.org")

            # Restore original
            add_reuse_module.REUSES_DIR = original_reuses_dir
        finally:
            shutil.rmtree(temp_dir)


if __name__ == "__main__":
    unittest.main()
