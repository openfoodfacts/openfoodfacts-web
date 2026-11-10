#!/usr/bin/env python3
"""
Automated Route & Link Integrity Test Suite for Open Food Facts Web.

Validates:
1. Critical hub pages like 'scores.html' exist across all active language directories.
2. No raw French/English phrases or sentences mistakenly placed into href attributes.
3. No accented characters in static page slug routes (e.g. /reutilisations instead of /réutilisations).
4. No broken symlinks in lang/en/texts or lang/fr/texts.
5. Key localized symlinks exist in French (open-food-facts-et-le-nutriscore, nouveau-nutriscore, reutilisations, scores).
"""
import os
import re
import sys
import unittest

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

class TestLinksAndRoutes(unittest.TestCase):

    def test_scores_page_exists_in_all_locales(self):
        """Ensure /scores never 404s by checking scores.html exists across locales."""
        lang_dir = os.path.join(ROOT_DIR, "lang")
        missing_scores = []
        for entry in os.listdir(lang_dir):
            texts_path = os.path.join(lang_dir, entry, "texts")
            if os.path.isdir(texts_path) and entry not in ("obf", "opf", "opff", "prices"):
                scores_file = os.path.join(texts_path, "scores.html")
                if not (os.path.exists(scores_file) or os.path.islink(scores_file)):
                    missing_scores.append(entry)
        self.assertEqual(
            missing_scores,
            [],
            f"Missing scores.html in locales: {missing_scores}"
        )

    def test_no_sentence_as_href_in_core_locales(self):
        """Ensure no text or full sentence is mistakenly placed inside an href attribute in en and fr."""
        pattern = re.compile(r'href=[\"\']([^\"\']+)[\"\']')
        suspicious = []

        for lang in ("en", "fr"):
            base_dir = os.path.join(ROOT_DIR, "lang", lang, "texts")
            for root, _, files in os.walk(base_dir):
                for f in files:
                    if not f.endswith(".html"):
                        continue
                    fpath = os.path.join(root, f)
                    try:
                        with open(fpath, "r", encoding="utf-8", errors="ignore") as fp:
                            content = fp.read()
                    except Exception:
                        continue

                    for match in pattern.findall(content):
                        href = match.strip()
                        if href.startswith(("http://", "https://", "mailto:", "tel:", "#", "javascript:", "//")):
                            continue
                        # Strip query parameters and anchors
                        path = href.split("?")[0].split("#")[0]
                        # A path containing unencoded spaces or sentence words is a misplaced text string
                        if " " in path or "&quot;" in href or "<a href" in href:
                            suspicious.append((os.path.relpath(fpath, ROOT_DIR), href))

        self.assertEqual(
            suspicious,
            [],
            f"Found malformed href attributes containing sentences in en/fr: {suspicious}"
        )

    def test_no_accented_static_page_slugs(self):
        """Static html fragments must use ASCII slugs (e.g. /reutilisations, not /réutilisations)."""
        pattern = re.compile(r'href=[\"\'](/[^\"\'#? ]+)[\"\']')
        accented = []

        for lang in ("en", "fr"):
            base_dir = os.path.join(ROOT_DIR, "lang", lang, "texts")
            for root, _, files in os.walk(base_dir):
                for f in files:
                    if not f.endswith(".html"):
                        continue
                    fpath = os.path.join(root, f)
                    try:
                        with open(fpath, "r", encoding="utf-8", errors="ignore") as fp:
                            content = fp.read()
                    except Exception:
                        continue

                    for link in pattern.findall(content):
                        # Taxonomy and facet routes allow accents in Product Opener
                        if link.startswith(('/facets/', '/category/', '/categories/', '/label/', '/labels/', '/ingredient/', '/ingredients/')):
                            continue
                        if re.search(r'[éèêëàâäîïôöùûüçÉÈÊËÀÂÄÎÏÔÖÙÛÜÇ]', link):
                            accented.append((os.path.relpath(fpath, ROOT_DIR), link))

        self.assertEqual(
            accented,
            [],
            f"Found accented static page URLs which break route matching: {accented}"
        )

    def test_no_broken_symlinks_in_en_and_fr(self):
        """Ensure all symlinks in primary language directories resolve properly."""
        broken = []
        for lang_code in ("en", "fr"):
            base = os.path.join(ROOT_DIR, "lang", lang_code, "texts")
            for root, _, files in os.walk(base):
                for f in files:
                    p = os.path.join(root, f)
                    if os.path.islink(p) and not os.path.exists(p):
                        broken.append((p, os.readlink(p)))

        self.assertEqual(
            broken,
            [],
            f"Found broken symlinks: {broken}"
        )

    def test_french_key_symlinks_exist(self):
        """Verify that key French localized routes and aliases exist."""
        fr_texts = os.path.join(ROOT_DIR, "lang", "fr", "texts")
        required_aliases = [
            "open-food-facts-et-le-nutriscore.html",
            "nouveau-nutriscore.html",
            "reutilisations.html",
            "scores.html",
            "scores-et-methodologies.html",
        ]
        missing = [alias for alias in required_aliases if not os.path.exists(os.path.join(fr_texts, alias))]
        self.assertEqual(
            missing,
            [],
            f"Missing required French localized aliases: {missing}"
        )


if __name__ == "__main__":
    unittest.main()
