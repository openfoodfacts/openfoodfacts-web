#!/usr/bin/env python3
"""
Unit tests for compile_releases.py and fetch_releases.py
"""

import json
import os
import sys
import unittest

SCRIPTS_DIR = os.path.dirname(os.path.abspath(__file__))
if SCRIPTS_DIR not in sys.path:
    sys.path.insert(0, SCRIPTS_DIR)

from compile_releases import (
    load_data,
    build_releases_html,
    generate_standalone_root_page,
    compile_releases,
    VALID_CATEGORIES,
)
from fetch_releases import (
    clean_html_body,
    summarize_body,
    format_date_en,
    format_date_fr,
    markdown_to_html,
)

class TestCompileReleases(unittest.TestCase):

    def test_load_data(self):
        releases, highlights, errors, warnings = load_data(validate=True)
        self.assertEqual(len(errors), 0, f"Encountered unexpected validation errors: {errors}")
        self.assertGreater(len(releases), 10, "Expected at least 10 releases in releases.json")
        self.assertGreater(len(highlights), 3, "Expected at least 3 curated highlights")

        # Verify highlights structure
        for h in highlights:
            self.assertIn("id", h)
            self.assertIn("title", h)
            self.assertIn("summary", h)
            self.assertIn("date", h)
            self.assertIn("category", h)
            self.assertTrue(h.get("rolling_year", False))

    def test_clean_html_body(self):
        raw = '<a href="https://github.com/pull/123" data-hovercard-type="pull_request">#123</a>'
        cleaned = clean_html_body(raw)
        self.assertIn('target="_blank"', cleaned)
        self.assertIn('rel="noopener"', cleaned)
        self.assertNotIn("data-hovercard", cleaned)

    def test_summarize_body(self):
        md = "## 2.120.0 (2026-11-06)\n\n### Features\n* add Matomo tracking for SignalConso link clicks\n* complete shared definitions"
        summary = summarize_body(md)
        self.assertIn("add Matomo tracking", summary)

    def test_markdown_to_html(self):
        md = "### Highlights\n* Add feature [docs](https://example.com)\n* Fix **critical** `bug`"
        html_out = markdown_to_html(md)
        self.assertIn("<h4>Highlights</h4>", html_out)
        self.assertIn('<li>Add feature <a href="https://example.com"', html_out)
        self.assertIn("<strong>critical</strong>", html_out)
        self.assertIn("<code>bug</code>", html_out)

    def test_date_formatting(self):
        iso_date = "2026-10-30T15:22:41Z"
        self.assertEqual(format_date_en(iso_date), "30 Oct 2026")
        self.assertEqual(format_date_fr(iso_date), "30 oct. 2026")

    def test_html_fragment_rules(self):
        releases, highlights, _, _ = load_data(validate=False)
        en_fragment = build_releases_html(releases, highlights, lang="en")
        fr_fragment = build_releases_html(releases, highlights, lang="fr")

        # Must NOT contain <html>, <head>, or <body> tags (AGENTS.md guideline for lang/*/texts/ fragments)
        self.assertNotIn("<html", en_fragment)
        self.assertNotIn("<body", en_fragment)
        self.assertNotIn("<html", fr_fragment)
        self.assertNotIn("<body", fr_fragment)

        # Must contain timeline structure and details
        self.assertIn("off-timeline", en_fragment)
        self.assertIn("off-timeline-dot", en_fragment)
        self.assertIn("off-rel-details", en_fragment)
        self.assertIn("off-highlights-grid", en_fragment)

        # Protected brand names check
        for protected in ["Open Food Facts", "Open Prices", "Nutri-Score", "Eco-Score"]:
            self.assertIn(protected, en_fragment)

    def test_standalone_page_structure(self):
        releases, highlights, _, _ = load_data(validate=False)
        en_fragment = build_releases_html(releases, highlights, lang="en")
        standalone = generate_standalone_root_page(en_fragment)

        self.assertTrue(standalone.startswith("<!DOCTYPE html>"))
        self.assertIn("<html lang=\"en\">", standalone)
        self.assertIn("<nav class=\"standalone-nav\">", standalone)
        self.assertIn("Open Food Facts — Ecosystem Releases & Features", standalone)

if __name__ == "__main__":
    unittest.main()
