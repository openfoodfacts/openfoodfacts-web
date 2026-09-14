#!/usr/bin/env python3
"""
Automated Translation QA test suite for Open Food Facts web translations.
Validates:
1. No merge conflict markers exist in any translation file.
2. Protected brand names (Directive 1) remain untranslated.
3. App Store and Google Play URLs use localized language codes (Directive 3).
4. UTM campaigns match folder language codes (Directive 3).
"""
import os
import re
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def get_lang_code(filepath):
    parts = filepath.replace('\\', '/').split('/')
    for i, part in enumerate(parts):
        if part in ('obf', 'opf', 'opff') and i + 1 < len(parts):
            return parts[i+1]
        if part == 'lang' and i + 1 < len(parts) and parts[i+1] not in ('obf', 'opf', 'opff', 'README.md'):
            return parts[i+1]
    return None

class TestTranslationQA(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.base_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'lang')
        cls.html_files = []
        for root, dirs, files in os.walk(cls.base_dir):
            for f in files:
                if f.endswith('.html') and not os.path.islink(os.path.join(root, f)):
                    cls.html_files.append(os.path.join(root, f))

    def test_no_conflict_markers(self):
        """Directive 2: Ensure no git conflict markers exist in files."""
        conflicts = []
        for path in self.html_files:
            try:
                with open(path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                    if '<<<<<<<' in content or '>>>>>>>' in content:
                        conflicts.append(path)
            except Exception:
                pass
        self.assertEqual(len(conflicts), 0, f"Found merge conflict markers in: {conflicts[:5]}")

    def test_brand_protection(self):
        """Directive 1: Brand names must not be translated."""
        bad_brand_patterns = [
            (r'\bOtvorte Food Facts\b', 'Slovak mistranslation of Open Food Facts'),
            (r'\bÅpne [Mm]atfakta\b', 'Norwegian mistranslation of Open Food Facts'),
            (r'\b[åÅ]pen matfakta\b', 'Norwegian mistranslation of Open Food Facts'),
            (r'\bInformations nutritionnelles ouvertes\b', 'French mistranslation of Open Food Facts'),
            (r'\bAbra Food Facts\b', 'Portuguese mistranslation of Open Food Facts'),
            (r'\b[Ff]aches alimentaris dobèrts\b', 'Occitan mistranslation of Open Food Facts'),
            (r'\b[Pp]untuación [Vv]erde\b', 'Spanish mistranslation of Green-Score'),
            (r'\b[Pp]ontuação [Vv]erde\b', 'Portuguese mistranslation of Green-Score'),
        ]
        violations = []
        for path in self.html_files:
            # Skip the AGENTS.md / documentation if scanned
            if 'AGENTS.md' in path:
                continue
            with open(path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            for pattern, reason in bad_brand_patterns:
                if re.search(pattern, content):
                    violations.append(f"{path}: {reason}")

        self.assertEqual(len(violations), 0, f"Found {len(violations)} brand protection violations:\n" + "\n".join(violations[:10]))

    def test_apple_store_urls_localized(self):
        """Directive 3: Apple App Store URLs in promo blocks must not have hardcoded l=en for non-English locales."""
        violations = []
        for path in self.html_files:
            lang_code = get_lang_code(path)
            if not lang_code or lang_code in ('en', 'en_GB', 'en_AU'):
                continue
            with open(path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            # In search_and_links_promo links
            for m in re.finditer(r'href="(https://apps\.apple\.com/app/open-food-facts/id588797948\?[^"]*)"', content):
                url = m.group(1)
                if 'utm_campaign=search_and_links_promo_' in url and ('l=en' in url or 'search_and_links_promo_en' in url):
                    violations.append(f"{path}: {url}")

        self.assertEqual(len(violations), 0, f"Found {len(violations)} hardcoded English App Store URLs in non-English locales:\n" + "\n".join(violations[:10]))

    def test_google_play_urls_localized(self):
        """Directive 3: Google Play URLs in promo blocks must use localized hl and campaign."""
        violations = []
        for path in self.html_files:
            lang_code = get_lang_code(path)
            if not lang_code or lang_code in ('en', 'en_GB', 'en_AU'):
                continue
            with open(path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            for m in re.finditer(r'href="(https://play\.google\.com/store/apps/details\?id=org\.openfoodfacts\.scanner[^"]*)"', content):
                url = m.group(1)
                if 'utm_campaign=search_and_links_promo_' in url and ('hl=en' in url or 'search_and_links_promo_en' in url):
                    violations.append(f"{path}: {url}")

        self.assertEqual(len(violations), 0, f"Found {len(violations)} hardcoded English Google Play URLs in non-English locales:\n" + "\n".join(violations[:10]))

    def test_creative_commons_urls_localized(self):
        """Directive 3: Creative Commons deed URLs must match localized target code when supported."""
        from fix_translation_issues import CC_DEED_LANG_MAP
        violations = []
        for path in self.html_files:
            lang_code = get_lang_code(path)
            if not lang_code:
                continue
            expected_deed = CC_DEED_LANG_MAP.get(lang_code, 'en')
            with open(path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            for m in re.finditer(r'href="(https?://creativecommons\.org/licenses/by-sa/3\.0/deed\.[a-zA-Z_-]+)"', content):
                url = m.group(1)
                actual_deed = url.split('.')[-1]
                if actual_deed != expected_deed:
                    violations.append(f"{path}: got {actual_deed}, expected {expected_deed} ({url})")

        self.assertEqual(len(violations), 0, f"Found {len(violations)} mismatched Creative Commons deed URLs:\n" + "\n".join(violations[:10]))

    def test_playstore_badges_localized(self):
        """Directive 3: Play Store badges must use localized badge SVG when available."""
        from fix_translation_issues import get_playstore_badge
        violations = []
        pattern = re.compile(r'((?:https://static\.openfoodfacts\.org)?/images/misc/playstore/img/([a-zA-Z0-9_-]+)_get\.svg)')
        for path in self.html_files:
            lang_code = get_lang_code(path)
            if not lang_code or lang_code in ('en', 'en_GB', 'en_AU'):
                continue
            expected_badge = get_playstore_badge(lang_code)
            if not expected_badge or expected_badge == 'en':
                continue
            with open(path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            for m, badge in pattern.findall(content):
                if badge != expected_badge:
                    violations.append(f"{path}: found {badge}_get.svg, expected {expected_badge}_get.svg")

        self.assertEqual(len(violations), 0, f"Found {len(violations)} unlocalized Play Store badges in non-English locales:\n" + "\n".join(violations[:10]))

    def test_fdroid_badges_localized(self):
        """Directive 3: F-Droid badges must use localized badge PNG when available."""
        from fix_translation_issues import get_fdroid_badge
        violations = []
        pattern = re.compile(r'((?:https://static\.openfoodfacts\.org)?/images/misc/f-droid/get-it-on(?:-([a-zA-Z0-9_-]+))?\.png)')
        for path in self.html_files:
            lang_code = get_lang_code(path)
            if not lang_code or lang_code in ('en', 'en_GB', 'en_AU'):
                continue
            expected_badge = get_fdroid_badge(lang_code)
            if not expected_badge or expected_badge == 'en':
                continue
            with open(path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            for m, badge in pattern.findall(content):
                if badge != expected_badge:
                    violations.append(f"{path}: found get-it-on-{badge or 'en'}.png, expected get-it-on-{expected_badge}.png")

        self.assertEqual(len(violations), 0, f"Found {len(violations)} unlocalized F-Droid badges in non-English locales:\n" + "\n".join(violations[:10]))

    def test_facet_links_prefixed(self):
        """Directive 3: Multi-facet links must be prefixed with /facets/ and use plural facet names."""
        pattern = re.compile(r'href=[\'"](?:https?://[a-z0-9.-]*openfoodfacts\.org)?/(?:label/|category/[^/]+/origins|categories/[^/]+/environmental-score)')
        violations = []
        for path in self.html_files:
            with open(path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            for m in pattern.finditer(content):
                violations.append(f"{path}: {m.group(0)}")

        self.assertEqual(len(violations), 0, f"Found {len(violations)} un-prefixed facet links:\n" + "\n".join(violations[:10]))

    def test_food_revolution_assets_localized(self):
        """Directive 3: Food revolution image banner must use localized SVG when available."""
        from fix_translation_issues import get_food_revolution_asset
        violations = []
        pattern = re.compile(r'((?:https://static\.openfoodfacts\.org)?/images/misc/app-landing-page/join-the-food-revolution/join-the-food-revolution_([a-zA-Z_-]+)\.svg)')
        for path in self.html_files:
            lang_code = get_lang_code(path)
            if not lang_code or lang_code in ('en', 'en_GB', 'en_AU'):
                continue
            expected_asset = get_food_revolution_asset(lang_code)
            if not expected_asset or expected_asset == 'en':
                continue
            with open(path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            # Strip comments to ignore commented-out templates (like in OBF)
            content_clean = re.sub(r'<!--.*?-->', '', content, flags=re.DOTALL)
            for m, asset in pattern.findall(content_clean):
                if asset != expected_asset:
                    violations.append(f"{path}: found join-the-food-revolution_{asset}.svg, expected join-the-food-revolution_{expected_asset}.svg")

    def test_press_page_includes_valid(self):
        """Directive 5: All include directives [[...]] in press.html must resolve to an existing file."""
        violations = []
        root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        for path in self.html_files:
            if not path.endswith('/texts/press.html'):
                continue
            lang_code = get_lang_code(path)
            with open(path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            for inc in re.findall(r'\[\[(.*?)\]\]', content):
                inc_clean = inc.strip()
                t_lang = os.path.join(root_dir, 'lang', lang_code, inc_clean)
                t_en = os.path.join(root_dir, 'lang', 'en', inc_clean)
                if not os.path.exists(t_lang) and not os.path.exists(t_en):
                    violations.append(f"{path}: include [[{inc_clean}]] not found")
        self.assertEqual(len(violations), 0, f"Found {len(violations)} broken includes in press pages:\n" + "\n".join(violations[:10]))

    def test_press_material_icons_ligatures(self):
        """Directive 5: Material icons inside press.html must use untranslated ligature names."""
        violations = []
        for path in self.html_files:
            if not path.endswith('/texts/press.html'):
                continue
            with open(path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            for m in re.finditer(r'<span class=[\'"]material-icons[\'"]>([^<]*)</span>', content):
                txt = m.group(1).strip()
                if txt and txt != 'download':
                    violations.append(f"{path}: unexpected ligature '{txt}'")
        self.assertEqual(len(violations), 0, f"Found {len(violations)} translated material icons in press pages:\n" + "\n".join(violations[:10]))

    def test_press_no_obsolete_logo_includes(self):
        """Directive 5: Press page must not reference obsolete texts/logo.html."""
        violations = []
        for path in self.html_files:
            if not path.endswith('/texts/press.html'):
                continue
            with open(path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            if 'texts/logo.html' in content or 'logo.html' in content:
                violations.append(f"{path}: references obsolete logo.html")
        self.assertEqual(len(violations), 0, f"Found {len(violations)} references to obsolete logo.html in press pages:\n" + "\n".join(violations[:10]))

if __name__ == '__main__':
    unittest.main()

