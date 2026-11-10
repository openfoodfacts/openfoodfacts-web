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
        cls.file_contents = {}
        for root, dirs, files in os.walk(cls.base_dir):
            for f in files:
                full = os.path.join(root, f)
                if f.endswith('.html') and not os.path.islink(full):
                    cls.html_files.append(full)
                    try:
                        with open(full, 'r', encoding='utf-8', errors='ignore') as fh:
                            cls.file_contents[full] = fh.read()
                    except Exception:
                        cls.file_contents[full] = ''

    def test_no_conflict_markers(self):
        """Directive 2: Ensure no git conflict markers exist in files."""
        conflicts = []
        for path, content in self.file_contents.items():
            if '<<<<<<<' in content or '>>>>>>>' in content:
                conflicts.append(path)
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
            (r'\b[Ss]core [Vv]ert\b', 'French mistranslation of Green-Score'),
            (r'\bGrüner Score\b', 'German mistranslation of Green-Score'),
            (r'\bFatos Alimentares Abertos\b', 'Portuguese mistranslation of Open Food Facts'),
            (r'\bEco-Sscore\b', 'Typo/mistranslation of Eco-Score'),
            (r'\bNutri-Sscore\b', 'Typo/mistranslation of Nutri-Score'),
            (r'أوبن فوود فاكتس', 'Arabic transliteration of Open Food Facts'),
            (r'حقائق الطعام المفتوحة', 'Arabic mistranslation of Open Food Facts'),
            (r'حقائق الغذاء المفتوح', 'Arabic mistranslation of Open Food Facts'),
            (r'النوتري-النتيجة', 'Arabic mistranslation of Nutri-Score'),
            (r'Open Beauty Hunt', 'Sister project contamination of Open Food Hunt'),
        ]
        compiled_patterns = [(re.compile(p), r) for p, r in bad_brand_patterns]
        combined_re = re.compile('|'.join(f'(?:{p})' for p, _ in bad_brand_patterns))
        violations = []
        for path, content in self.file_contents.items():
            if 'AGENTS.md' in path or not combined_re.search(content):
                continue
            for pat, reason in compiled_patterns:
                if pat.search(content):
                    violations.append(f"{path}: {reason}")

        self.assertEqual(len(violations), 0, f"Found {len(violations)} brand protection violations:\n" + "\n".join(violations[:10]))

    def test_apple_store_urls_localized(self):
        """Directive 3: Apple App Store URLs in promo blocks must not have hardcoded l=en for non-English locales."""
        violations = []
        apple_re = re.compile(r'href="(https://apps\.apple\.com/app/open-food-facts/id588797948\?[^"]*)"')
        for path, content in self.file_contents.items():
            if 'apps.apple.com' not in content:
                continue
            lang_code = get_lang_code(path)
            if not lang_code or lang_code in ('en', 'en_GB', 'en_AU'):
                continue
            for m in apple_re.finditer(content):
                url = m.group(1)
                if 'utm_campaign=search_and_links_promo_' in url and ('l=en' in url or 'search_and_links_promo_en' in url):
                    violations.append(f"{path}: {url}")

        self.assertEqual(len(violations), 0, f"Found {len(violations)} hardcoded English App Store URLs in non-English locales:\n" + "\n".join(violations[:10]))

    def test_google_play_urls_localized(self):
        """Directive 3: Google Play URLs in promo blocks must use localized hl and campaign."""
        violations = []
        play_re = re.compile(r'href="(https://play\.google\.com/store/apps/details\?id=org\.openfoodfacts\.scanner[^"]*)"')
        for path, content in self.file_contents.items():
            if 'play.google.com' not in content:
                continue
            lang_code = get_lang_code(path)
            if not lang_code or lang_code in ('en', 'en_GB', 'en_AU'):
                continue
            for m in play_re.finditer(content):
                url = m.group(1)
                if 'utm_campaign=search_and_links_promo_' in url and ('hl=en' in url or 'search_and_links_promo_en' in url):
                    violations.append(f"{path}: {url}")

        self.assertEqual(len(violations), 0, f"Found {len(violations)} hardcoded English Google Play URLs in non-English locales:\n" + "\n".join(violations[:10]))

    def test_creative_commons_urls_localized(self):
        """Directive 3: Creative Commons deed URLs must match localized target code when supported."""
        from fix_translation_issues import CC_DEED_LANG_MAP
        violations = []
        cc_re = re.compile(r'href="(https?://creativecommons\.org/licenses/by-sa/3\.0/deed\.[a-zA-Z_-]+)"')
        for path, content in self.file_contents.items():
            if 'creativecommons.org/licenses/by-sa/3.0/deed.' not in content:
                continue
            lang_code = get_lang_code(path)
            if not lang_code:
                continue
            expected_deed = CC_DEED_LANG_MAP.get(lang_code, 'en')
            for m in cc_re.finditer(content):
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
        for path, content in self.file_contents.items():
            if '/images/misc/playstore/img/' not in content:
                continue
            lang_code = get_lang_code(path)
            if not lang_code or lang_code in ('en', 'en_GB', 'en_AU'):
                continue
            expected_badge = get_playstore_badge(lang_code)
            if not expected_badge or expected_badge == 'en':
                continue
            for m, badge in pattern.findall(content):
                if badge != expected_badge:
                    violations.append(f"{path}: found {badge}_get.svg, expected {expected_badge}_get.svg")

        self.assertEqual(len(violations), 0, f"Found {len(violations)} unlocalized Play Store badges in non-English locales:\n" + "\n".join(violations[:10]))

    def test_fdroid_badges_localized(self):
        """Directive 3: F-Droid badges must use localized badge PNG when available."""
        from fix_translation_issues import get_fdroid_badge
        violations = []
        pattern = re.compile(r'((?:https://static\.openfoodfacts\.org)?/images/misc/f-droid/get-it-on(?:-([a-zA-Z0-9_-]+))?\.png)')
        for path, content in self.file_contents.items():
            if '/images/misc/f-droid/get-it-on' not in content:
                continue
            lang_code = get_lang_code(path)
            if not lang_code or lang_code in ('en', 'en_GB', 'en_AU'):
                continue
            expected_badge = get_fdroid_badge(lang_code)
            if not expected_badge or expected_badge == 'en':
                continue
            for m, badge in pattern.findall(content):
                if badge != expected_badge:
                    violations.append(f"{path}: found get-it-on-{badge or 'en'}.png, expected get-it-on-{expected_badge}.png")

        self.assertEqual(len(violations), 0, f"Found {len(violations)} unlocalized F-Droid badges in non-English locales:\n" + "\n".join(violations[:10]))

    def test_facet_links_prefixed(self):
        """Directive 3: Multi-facet links must be prefixed with /facets/ and use plural facet names."""
        pattern = re.compile(r'href=[\'"](?:https?://[a-z0-9.-]*openfoodfacts\.org)?/(?:label/|category/[^/]+/origins|categories/[^/]+/environmental-score)')
        violations = []
        for path, content in self.file_contents.items():
            if '/label/' not in content and '/category/' not in content and '/categories/' not in content:
                continue
            for m in pattern.finditer(content):
                violations.append(f"{path}: {m.group(0)}")

        self.assertEqual(len(violations), 0, f"Found {len(violations)} un-prefixed facet links:\n" + "\n".join(violations[:10]))

    def test_food_revolution_assets_localized(self):
        """Directive 3: Food revolution image banner must use localized SVG when available."""
        from fix_translation_issues import get_food_revolution_asset
        violations = []
        pattern = re.compile(r'((?:https://static\.openfoodfacts\.org)?/images/misc/app-landing-page/join-the-food-revolution/join-the-food-revolution_([a-zA-Z_-]+)\.svg)')
        for path, content in self.file_contents.items():
            if 'join-the-food-revolution_' not in content:
                continue
            lang_code = get_lang_code(path)
            if not lang_code or lang_code in ('en', 'en_GB', 'en_AU'):
                continue
            expected_asset = get_food_revolution_asset(lang_code)
            if not expected_asset or expected_asset == 'en':
                continue
            content_clean = re.sub(r'<!--.*?-->', '', content, flags=re.DOTALL)
            for m, asset in pattern.findall(content_clean):
                if asset != expected_asset:
                    violations.append(f"{path}: found join-the-food-revolution_{asset}.svg, expected join-the-food-revolution_{expected_asset}.svg")

        self.assertEqual(len(violations), 0, f"Found {len(violations)} unlocalized food revolution assets:\n" + "\n".join(violations[:10]))

    def test_press_page_includes_valid(self):
        """Directive 5: All include directives [[...]] in press.html must resolve to an existing file."""
        violations = []
        root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        for path, content in self.file_contents.items():
            if not path.endswith('/texts/press.html'):
                continue
            lang_code = get_lang_code(path)
            for inc in re.findall(r'\[\[(.*?)\]\]', content):
                inc_clean = inc.strip()
                t_lang = os.path.join(root_dir, 'lang', lang_code, inc_clean)
                t_en = os.path.join(root_dir, 'lang', 'en', inc_clean)
                if not os.path.exists(t_lang) and not os.path.exists(t_en):
                    violations.append(f"{path}: include [[{inc_clean}]] not found")
        self.assertEqual(len(violations), 0, f"Found {len(violations)} broken includes in press pages:\n" + "\n".join(violations[:10]))

    def test_press_material_icons_ligatures(self):
        """Directive 5: Material icons inside press.html and all other pages must use untranslated ligature names."""
        from fix_translation_issues import VALID_MATERIAL_ICONS
        violations = []
        span_re = re.compile(r'<span class=[\'"]material-icons[^\'"]*[\'"][^>]*>([^<]*)</span>')
        for path, content in self.file_contents.items():
            if 'material-icons' not in content:
                continue
            for m in span_re.finditer(content):
                txt = m.group(1).strip()
                if path.endswith('/texts/press.html') and txt and txt != 'download':
                    violations.append(f"{path}: unexpected ligature '{txt}'")
                elif txt and (not re.match(r'^[a-z0-9_]+$', txt) or txt not in VALID_MATERIAL_ICONS):
                    violations.append(f"{path}: invalid/translated material-icons ligature '{txt}'")
        self.assertEqual(len(violations), 0, f"Found {len(violations)} translated material icons:\n" + "\n".join(violations[:10]))

    def test_all_template_includes_valid(self):
        """Directive 2 & 5: All [[...]] template includes across all HTML files must resolve to valid includes."""
        from fix_translation_issues import _is_valid_include
        violations = []
        for path, content in self.file_contents.items():
            if '[[' not in content:
                continue
            lang_code = get_lang_code(path)
            for inc in re.findall(r'\[\[(.*?)\]\]', content):
                if not _is_valid_include(inc, lang_code, self.base_dir):
                    violations.append(f"{path}: broken include [[{inc}]]")
        self.assertEqual(len(violations), 0, f"Found {len(violations)} broken [[...]] includes:\n" + "\n".join(violations[:10]))

    def test_no_api_key_or_ai_error_leaks(self):
        """Ensure no leaked OpenAI/MT API keys or error strings exist in any translation file."""
        leak_pattern = re.compile(
            r'Incorrect A(?:PI|pi) key provided|platform\.\s*openai\.\s*com/account/api-keys|sk-[A-Za-z0-9*]{20,}|As an AI language model',
            re.IGNORECASE
        )
        violations = []
        for path, content in self.file_contents.items():
            if 'Incorrect' not in content and 'openai' not in content and 'sk-' not in content and 'language model' not in content:
                continue
            m = leak_pattern.search(content)
            if m:
                violations.append(f"{path}: leaked error/key string '{m.group(0)}'")
        self.assertEqual(len(violations), 0, f"Found {len(violations)} leaked API/AI error strings:\n" + "\n".join(violations[:10]))

    def test_no_sister_project_contamination(self):
        """Ensure OFF pages whose English source does not mention sister projects do not contain OBF/OPFF/OPF strings."""
        target_basenames = {'contribute.html', 'contribuír.html', 'discover.html', 'open-food-hunt.html', 'index.html'}
        forbidden_re = re.compile(
            r'Open Beauty Facts|Open Pet Food Facts|Open Products Facts|openbeautyfacts\.org|openpetfoodfacts\.org|openproductsfacts\.org|'
            r'A cosmetics products database|Make better cosmetics choices|Curious about cosmetics\?|'
            r'O banco de dados de produtos cosméticos|Faça melhores escolhas de cosméticos|'
            r'База данных косметических продуктов|Tee parempia kosmetiikkavalintoja'
        )
        violations = []
        for path, content in self.file_contents.items():
            norm = path.replace('\\', '/')
            if '/obf/' in norm or '/opff/' in norm or '/opf/' in norm:
                continue
            if os.path.basename(norm) not in target_basenames:
                continue
            m = forbidden_re.search(content)
            if m:
                violations.append(f"{path}: contains sister-project contamination '{m.group(0)}'")
        self.assertEqual(len(violations), 0, f"Found {len(violations)} sister-project contaminations:\n" + "\n".join(violations[:10]))

    def test_press_no_obsolete_logo_includes(self):
        """Directive 5: Press page must not reference obsolete texts/logo.html."""
        violations = []
        for path, content in self.file_contents.items():
            if not path.endswith('/texts/press.html'):
                continue
            if 'texts/logo.html' in content or 'logo.html' in content:
                violations.append(f"{path}: references obsolete logo.html")
        self.assertEqual(len(violations), 0, f"Found {len(violations)} references to obsolete logo.html in press pages:\n" + "\n".join(violations[:10]))

    def test_edit_page_include_exists_in_en(self):
        """Verify edit-page-include.html exists in lang/en/texts."""
        root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        en_include = os.path.join(root_dir, 'lang', 'en', 'texts', 'edit-page-include.html')
        self.assertTrue(os.path.isfile(en_include), "edit-page-include.html does not exist in lang/en/texts/")

    def test_non_editable_pages_have_no_edit_include(self):
        """Verify non-editable pages (ToS, Code of Conduct, Legal, Privacy) do not contain edit-page-include."""
        forbidden_basenames = {
            'terms-of-use.html',
            'termos-de-uso.html',
            'termos-de-utilizacao.html',
            'nutzungsbedingungen.html',
            'condiciones-de-uso.html',
            'conditions-d-utilisation.html',
            'code-of-conduct.html',
            'codigo-de-conducta.html',
            'code-de-conduite.html',
            'verhaltenskodex.html',
            'legal.html',
            'informacao-legal.html',
            'gesetzliche-hinweise.html',
            'mentions-legales.html',
            'aviso-legal.html',
            'impressum.html',
            'privacy.html',
            'privacidade.html',
            'datenschutz.html',
            'politique-de-confidentialite.html',
        }
        violations = []
        for path, content in self.file_contents.items():
            filename = os.path.basename(path)
            if filename in forbidden_basenames:
                if 'edit-page-include.html' in content:
                    violations.append(path)
        self.assertEqual(len(violations), 0, f"Found edit-page-include in non-editable pages:\n" + "\n".join(violations[:10]))

    def test_data_page_has_api_donation_include(self):
        """Verify that the Data page includes the api-donation-include tag."""
        root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        for lang in ['en', 'fr']:
            page_path = os.path.join(root_dir, 'lang', lang, 'texts', 'data.html')
            content = self.file_contents.get(page_path, '')
            self.assertIn('[[texts/api-donation-include.html]]', content, f"lang/{lang}/texts/data.html is missing [[texts/api-donation-include.html]]")
            include_path = os.path.join(root_dir, 'lang', lang, 'texts', 'api-donation-include.html')
            self.assertTrue(os.path.isfile(include_path), f"Missing include file: {include_path}")

    def test_forbidden_strings_in_index_html(self):
        """Ensure Open Food Facts index.html files do not reference sister projects (check_strings.yml parity)."""
        forbidden_strings = ["Open Pet Food Facts", "Open Beauty Facts", "Open Products Facts"]
        violations = []
        for path, content in self.file_contents.items():
            if not path.endswith('/texts/index.html'):
                continue
            if '/obf/' in path or '/opff/' in path or '/opf/' in path:
                continue
            for s in forbidden_strings:
                if s in content:
                    violations.append(f"{path}: contains '{s}'")
        self.assertEqual(len(violations), 0, f"Found forbidden sister project strings in OFF index.html files:\n" + "\n".join(violations[:10]))

    def test_no_repeated_substring_loops(self):
        """Ensure translations do not contain repeated substrings or emoticon loops (e.g. &nbsp;:-)&nbsp;:-) or :-) :-) ...)."""
        emoticon_loop_pattern = re.compile(r'((?:&nbsp;|\s)*:[-~]?[)D(PpoO])(?:\s+|&nbsp;)*(?:\1)+')
        violations = []
        for path, content in self.file_contents.items():
            if ':-' not in content and ':)' not in content and ':D' not in content and ':P' not in content and ':p' not in content and ':(' not in content:
                continue
            clean = re.sub(r'<style[^>]*>.*?</style>', '', content, flags=re.DOTALL)
            clean = re.sub(r'<script[^>]*>.*?</script>', '', clean, flags=re.DOTALL)
            matches = [m.group(0).strip() for m in emoticon_loop_pattern.finditer(clean)]
            if matches:
                violations.append(f"{path}: looped substring '{matches[0]}'")
        self.assertEqual(len(violations), 0, f"Found repeated substring loops in translations:\n" + "\n".join(violations[:10]))

    def test_no_pseudo_xml_tags(self):
        """Ensure no pseudo-XML placeholder tags (<0>, </0>, <1/>, etc.) exist in translation files."""
        tag_re = re.compile(r"</?[0-9]+(?:/[0-9]*)?>|<[0-9]+/>")
        violations = []
        for path, content in self.file_contents.items():
            if not tag_re.search(content):
                continue
            matches = tag_re.findall(content)
            violations.append(f"{path}: found {matches[:5]}")
        self.assertEqual(len(violations), 0, f"Found {len(violations)} files with pseudo-XML tags:\n" + "\n".join(violations[:10]))

    def test_no_corrupted_css_js_entities(self):
        """Ensure no &nbsp; entities corrupt CSS or JS syntax inside <style> and <script> blocks."""
        style_script_re = re.compile(r"(<(style|script)\b[^>]*>)(.*?)(</\2>)", re.DOTALL | re.IGNORECASE)
        corrupt_re = re.compile(r"&nbsp;(!important|!==|!=|===|==|!\s*!|!\w)")
        violations = []
        for path, content in self.file_contents.items():
            if '&nbsp;' not in content:
                continue
            for m in style_script_re.finditer(content):
                body = m.group(3)
                cm = corrupt_re.findall(body)
                if cm:
                    violations.append(f"{path}: found {cm[:5]}")
                    break
        self.assertEqual(len(violations), 0, f"Found {len(violations)} files with corrupted CSS/JS operators in style/script:\n" + "\n".join(violations[:10]))

if __name__ == '__main__':
    unittest.main()


