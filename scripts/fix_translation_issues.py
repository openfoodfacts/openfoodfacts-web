#!/usr/bin/env python3
"""
Script to automatically fix common translation issues in lang files.
Can be used as part of a GitHub Action to repair Crowdin translations.

This script fixes:
1. UTM campaign parameters to use correct language code based on folder path
2. UTM term parameters with incorrect language prefixes
3. Apple App Store and Google Play URLs to use correct localized language codes (l=<lc>, hl=<lc>)
4. Protect brand names according to the official "No-Translate" list
5. Subdomain and locale URL consistency
6. French typographical quality (non-breaking spaces before : ; ? ! and within « »)
7. Common text repetition patterns (both known patterns and dynamic detection)

Usage:
    python fix_translation_issues.py [--base-dir DIR] [--fix-repetitions] [--fix-utm] [--fix-urls] [--fix-brands] [--fix-typography] [--verbose]
"""
import os
import re
import glob
import argparse
import sys

# CSS/HTML patterns to skip (false positives) - these are legitimate repeated CSS properties
CSS_SKIP_PATTERNS = [
    r'box-shadow:',
    r'animation:',
    r'transform:',
    r'transition:',
    r'and \(min-width:',
    r'\.mod-detail',
    r'rgba\(',
    r'scale\(',
    r'translate\(',
    r'gb__a',
]

# Known repetition patterns to fix - (find, replace) pairs
KNOWN_REPETITIONS = [
    # Common English repetitions
    ("Open Food Facts is an essential data distribution channel. Open Food Facts is an essential data distribution channel.",
     "Open Food Facts is an essential data distribution channel."),
    ("Many publications use and cite Open Food Facts, both in nutrition and other research areas. Many publications use and cite Open Food Facts, both in nutrition and other research areas. Many publications use and cite Open Food Facts, both in nutrition and other research areas. Many publications use and cite Open Food Facts, both in nutrition and other research areas. Many publications use and cite Open Food Facts, both in nutrition and other research areas. Many publications use and cite Open Food Facts, both in nutrition and other research areas. Many publications use and cite Open Food Facts, both in nutrition and other research areas. Many publications use and cite Open Food Facts, both in nutrition and other research areas. Many publications use and cite Open Food Facts, both in nutrition and other research areas. Many publications use and cite Open Food Facts, both in nutrition and other research areas.",
     "Many publications use and cite Open Food Facts, both in nutrition and other research areas."),
    ("Our full list of communiques is coming soon. Future communiques will be listed here. Our full list of communiques is coming soon. Future communiques will be listed here. Future communiques will be listed here. Our full list of communiques is coming soon. Future communiques will be listed here. Future communiques will be listed here.",
     "Our full list of communiques is coming soon. Future communiques will be listed here."),
    ("Please direct additional questions at\u00a0<a href=\"mailto:reuse@openfoodfacts.org\"><u>reuse@openfoodfacts.org</u></a> Please direct additional questions at\u00a0<a href=\"mailto:reuse@openfoodfacts.org\"><u>reuse@openfoodfacts.org</u></a>",
     "Please direct additional questions at\u00a0<a href=\"mailto:reuse@openfoodfacts.org\"><u>reuse@openfoodfacts.org</u></a>"),
    ("In an ideal world, people shouldn't have to use a mobile app to understand their food. In an ideal world, people shouldn't have to use a mobile app to understand their food.",
     "In an ideal world, people shouldn't have to use a mobile app to understand their food."),
    ("Thank you ! Thank you ! Thank you ! Thank you !", "Thank you !"),
    ("Thank you! Thank you!", "Thank you!"),
    ("Thank you ! Thank you !", "Thank you !"),
    ("Daily delta exports are provided for the previous 14 days.\n Daily delta exports are provided for the previous 14 days.",
     "Daily delta exports are provided for the previous 14 days."),
    
    # French repetitions
    ("Open Food Facts est un canal de distribution de données essentiel. Open Food Facts est un canal de distribution de données essentiel.",
     "Open Food Facts est un canal de distribution de données essentiel."),
    (" null, null,", " null,"),
    
    # German repetitions
    ("Open Food Facts ist ein wichtiger Kanal für die Bereitstellung von Daten. Open Food Facts ist ein wichtiger Kanal für die Bereitstellung von Daten.",
     "Open Food Facts ist ein wichtiger Kanal für die Bereitstellung von Daten."),
    
    # Italian repetitions
    ("Open Food Facts è un canale di distribuzione dei dati essenziali. Open Food Facts è un canale di distribuzione dei dati essenziali.",
     "Open Food Facts è un canale di distribuzione dei dati essenziali."),
    
    # Japanese repetitions
    ("Open Food Facts は、重要なデータ配布チャネルです。 Open Food Facts は、重要なデータ配布チャネルです。",
     "Open Food Facts は、重要なデータ配布チャネルです。"),
    ("私たちは、すべての人のために作られたこの美しいプロジェクトにユニークな特徴を与える大規模な国際的な家族です!\n私たちは、すべての人のために作られたこの美しいプロジェクトにユニークな特徴を与える大規模な国際的な家族です!",
     "私たちは、すべての人のために作られたこの美しいプロジェクトにユニークな特徴を与える大規模な国際的な家族です!"),
    
    # Arabic repetitions
    ("Open Food Facts هو قناة توزيع بيانات أساسية. Open Food Facts هو قناة توزيع بيانات أساسية.",
     "Open Food Facts هو قناة توزيع بيانات أساسية."),
    
    # Spanish repetitions
    ("¿Preguntas o comentarios? ¿Preguntas o comentarios?",
     "¿Preguntas o comentarios?"),
    ("¡Muchas gracias por su interés en el proyecto! ¡Muchas gracias por su interés en el proyecto!",
     "¡Muchas gracias por su interés en el proyecto!"),
    
    # Thai repetitions
    ("ไม่มีสมาร์ทโฟนใช่ไหม ไม่มีสมาร์ทโฟนใช่ไหม ไม่มีสมาร์ทโฟนใช่ไหม", "ไม่มีสมาร์ทโฟนใช่ไหม"),
    ("ไม่มีสมาร์ทโฟนใช่ไหม ไม่มีสมาร์ทโฟนใช่ไหม", "ไม่มีสมาร์ทโฟนใช่ไหม"),
    
    # Portuguese repetitions
    ("Conhecimento é poder. Conhecimento é poder.", "Conhecimento é poder."),
    ("Talvez já tenha ideias? Talvez já tenha ideias?", "Talvez já tenha ideias?"),
    
    # Chinese repetitions
    ("(in French) (in French)", "(in French)"),
    ("That&amp;rsquo;s great ! That&amp;rsquo;s great !", "That&amp;rsquo;s great !"),
    ("Don't worry too much: Don't worry too much:", "Don't worry too much:"),
    ("你能猜出你的食物中含有的糖等于多少块方糖吗？ 你能猜出你的食物中含有的糖等于多少块方糖吗？", "你能猜出你的食物中含有的糖等于多少块方糖吗？"),
    ("You might like compote You might like compote", "You might like compote"),
    ("The Eco-Score is still young and can certainly be improved. The Eco-Score is still young and can certainly be improved.",
     "The Eco-Score is still young and can certainly be improved."),
    ("Curious about cosmetics? Curious about cosmetics?", "Curious about cosmetics?"),
    ("Tell others about it! Tell others about it!", "Tell others about it!"),
    ("And present it live! And present it live!", "And present it live!"),
    ("Are you one of them? Are you one of them?", "Are you one of them?"),
]

# Protected brand names rules (Directive 1)
BRAND_PROTECTION_RULES = [
    # Slovak translations of Open Food Facts
    (r'\bOtvorte Food Facts\b', 'Open Food Facts'),
    (r'\botvorte food facts\b', 'Open Food Facts'),
    # Norwegian translations of Open Food Facts
    (r'\bÅpne matfakta\b', 'Open Food Facts'),
    (r'\båpne matfakta\b', 'Open Food Facts'),
    (r'\bÅpne Matfakta\b', 'Open Food Facts'),
    (r'\båpen matfakta\b', 'Open Food Facts'),
    (r'\bÅpen matfakta\b', 'Open Food Facts'),
    (r'\bÅpne databasen over matfakta\b', 'Open Food Facts-databasen'),
    # French translations of Open Food Facts
    (r'\bInformations nutritionnelles ouvertes\b', 'Open Food Facts'),
    # Portuguese translations of Open Food Facts
    (r'\bAbra Food Facts\b', 'Open Food Facts'),
    (r'\babra food facts\b', 'Open Food Facts'),
    # Spanish translations of Open Food Facts
    (r'\babierto hechos de comida\b', 'Open Food Facts'),
    (r'\bAbierto Hechos de Comida\b', 'Open Food Facts'),
    # Occitan translations of Open Food Facts
    (r'\blos faches de l\'alimentacion dobèrta\b', 'Open Food Facts'),
    (r'\bfaches alimentaris dobèrts\b', 'Open Food Facts'),
    # Green-Score translations (Directive 1: Reject "Pontuação Verde", "Puntuación Verde")
    (r'\bLa [Pp]untuación [Vv]erde\b', 'El Green-Score'),
    (r'\bla [Pp]untuación [Vv]erde\b', 'el Green-Score'),
    (r'\b[Pp]untuación [Vv]erde\b', 'Green-Score'),
    (r'\bA [Pp]ontuação [Vv]erde\b', 'O Green-Score'),
    (r'\ba [Pp]ontuação [Vv]erde\b', 'o Green-Score'),
    (r'\b[Pp]ontuação [Vv]erde\b', 'Green-Score'),
]


def get_lang_code(filepath):
    """Extract language code from folder path like /lang/aa/ -> aa or /lang/obf/fr/ -> fr"""
    parts = filepath.replace('\\', '/').split('/')
    for i, part in enumerate(parts):
        if part in ('obf', 'opf', 'opff') and i + 1 < len(parts):
            return parts[i + 1]
        if part == 'lang' and i + 1 < len(parts) and parts[i + 1] not in ('obf', 'opf', 'opff', 'README.md'):
            return parts[i + 1]
    return None


def get_lang_val(lang_code):
    """Return lowercase hyphenated code suitable for web parameters (pt-br, zh-cn, etc.)."""
    return lang_code.lower().replace('_', '-')


def fix_utm_campaigns(content, lang_code):
    """
    Fix UTM parameter issues: wrong language codes, and misspelled parameter names.
    """
    fixes = 0
    patterns = [
        # UTM campaign patterns
        (r'utm_campaign=search_and_links_promo_[a-zA-Z_]+', f'utm_campaign=search_and_links_promo_{lang_code}'),
        (r'utm_campaign=discover_buttons_[a-zA-Z_]+', f'utm_campaign=discover_buttons_{lang_code}'),
        # UTM term patterns
        (r'utm_term=[a-zA-Z_]+-text-ecoscore-page', f'utm_term={lang_code}-text-ecoscore-page'),
        (r'utm_term=[a-zA-Z_]+-text-button-ecoscore-page', f'utm_term={lang_code}-text-button-ecoscore-page'),
        # Misspelled parameter name (language-independent)
        (r'utf_medium=', 'utm_medium='),
    ]
    
    for pattern, replacement in patterns:
        matches = len(re.findall(pattern, content))
        if matches:
            content = re.sub(pattern, replacement, content)
            fixes += matches
    
    return content, fixes


def fix_app_store_urls(content, lang_code):
    """
    Fix Apple App Store and Google Play URLs to use the proper language codes.
    Directive 3: URL & Domain Consistency.
    """
    fixes = 0
    lang_val = get_lang_val(lang_code)

    # 1. Apple Store links with existing ?l=... or in promo links
    # Match https://apps.apple.com/app/open-food-facts/id588797948?l=...
    def replace_apple_l(m):
        nonlocal fixes
        old = m.group(0)
        # replace l=en or any code with lang_val
        new = re.sub(r'(\?|&amp;|&)l=[a-zA-Z_-]+', r'\1l=' + lang_val, old)
        if new != old:
            fixes += 1
        return new

    content = re.sub(r'https://apps\.apple\.com/app/open-food-facts/id588797948\?[^"\'\s>]+', replace_apple_l, content)

    # 2. Apple Store links that have ?utm_source= without ?l=
    def add_apple_l(m):
        nonlocal fixes
        old = m.group(0)
        if '?l=' not in old and '&amp;l=' not in old and '&l=' not in old:
            # Add ?l= at the start of query string
            new = old.replace('id588797948?', f'id588797948?l={lang_val}&amp;')
            if new != old:
                fixes += 1
                return new
        return old

    content = re.sub(r'https://apps\.apple\.com/app/open-food-facts/id588797948\?[^"\'\s>]+', add_apple_l, content)

    # 3. Google Play links: update hl=...
    def replace_google_hl(m):
        nonlocal fixes
        old = m.group(0)
        new = re.sub(r'(\?|&amp;|&)hl=[a-zA-Z_-]+', r'\1hl=' + lang_val, old)
        if new != old:
            fixes += 1
        return new

    content = re.sub(r'https://play\.google\.com/store/apps/details\?id=org\.openfoodfacts\.scanner[^"\'\s>]+', replace_google_hl, content)

    # 4. In mobile app landing page: const defaultLang = "..."
    def replace_default_lang(m):
        nonlocal fixes
        old = m.group(0)
        new = f'const defaultLang = "{lang_val}";'
        if new != old:
            fixes += 1
        return new

    content = re.sub(r'const defaultLang = "[^"]*";', replace_default_lang, content)

    return content, fixes


# Play Store language badge aliases: maps folder lang_code to playstore SVG code prefix
PLAYSTORE_ALIASES = {
    "tl": "fil",
    "he": "iw",
    "yi": "iw",
    "uk": "ua",
    "nb": "no",
    "nn": "no",
    "zh": "zh-cn",
    "zh_CN": "zh-cn",
    "zh_TW": "zh-tw",
    "zh_HK": "zh-hk",
    "pt_BR": "pt-br",
    "es_419": "es-419",
}

# App Store badge aliases: maps folder lang_code to appstore SVG country suffix
APPSTORE_ALIASES = {
    "el": "GR",
    "en": "US",
    "en_US": "US",
    "en_GB": "UK",
    "en_AU": "US",
    "es": "ES",
    "es_419": "ES_MX",
    "fr": "FR",
    "fr_CA": "FR_CA",
    "pt": "PT_PT",
    "pt_PT": "PT_PT",
    "pt_BR": "PT_BR",
    "zh_CN": "CN_SC",
    "zh": "CN_SC",
    "zh_TW": "CN_TC",
    "zh_HK": "CN_TC",
    "he": "HB",
    "iw": "HB",
    "ja": "JP",
    "ko": "KR",
    "cs": "CZ",
    "da": "DK",
    "de": "DE",
    "et": "EE",
    "fi": "FI",
    "hu": "HU",
    "id": "ID",
    "it": "IT",
    "lt": "LT",
    "lv": "LV",
    "ms": "MY",
    "nl": "NL",
    "nl_BE": "NL",
    "nl_NL": "NL",
    "no": "NO",
    "nb": "NO",
    "nn": "NO",
    "pl": "PL",
    "ro": "RO",
    "ru": "RU",
    "sv": "SE",
    "sk": "SK",
    "sl": "SI",
    "th": "TH",
    "tr": "TR",
    "vi": "VN",
    "ar": "AR",
    "az": "AZ",
    "bg": "BG",
    "mt": "MT",
    "tl": "PH",
    "fil": "PH",
}

# Available badge sets (loaded dynamically if base dir exists, or cached defaults)
_PLAYSTORE_SVGS = None
_APPSTORE_SVGS = None

def _get_available_badge_sets():
    global _PLAYSTORE_SVGS, _APPSTORE_SVGS
    if _PLAYSTORE_SVGS is None:
        root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        play_dir = os.path.join(root_dir, 'html', 'images', 'misc', 'playstore', 'img')
        app_dir = os.path.join(root_dir, 'html', 'images', 'misc', 'appstore', 'black')
        if os.path.isdir(play_dir):
            _PLAYSTORE_SVGS = {f.split('_get.svg')[0] for f in os.listdir(play_dir) if f.endswith('_get.svg')}
        else:
            _PLAYSTORE_SVGS = set()
        if os.path.isdir(app_dir):
            _APPSTORE_SVGS = {f.split('.svg')[0].replace('appstore_', '') for f in os.listdir(app_dir) if f.endswith('.svg')}
        else:
            _APPSTORE_SVGS = set()
    return _PLAYSTORE_SVGS, _APPSTORE_SVGS


def get_playstore_badge(lang_code):
    """Return the SVG badge prefix for Google Play Store for the given language code, or None."""
    if not lang_code:
        return None
    play_set, _ = _get_available_badge_sets()
    if lang_code in PLAYSTORE_ALIASES:
        target = PLAYSTORE_ALIASES[lang_code]
        if not play_set or target in play_set:
            return target
    val = lang_code.lower().replace('_', '-')
    if not play_set or val in play_set:
        return val
    base = lang_code.split('_')[0].split('-')[0].lower()
    if base in PLAYSTORE_ALIASES:
        target = PLAYSTORE_ALIASES[base]
        if not play_set or target in play_set:
            return target
    if not play_set or base in play_set:
        return base
    return None


def get_appstore_badge(lang_code):
    """Return the SVG badge country code for Apple App Store for the given language code, or None."""
    if not lang_code:
        return None
    _, app_set = _get_available_badge_sets()
    if lang_code in APPSTORE_ALIASES:
        target = APPSTORE_ALIASES[lang_code]
        if not app_set or target in app_set:
            return target
    upper = lang_code.upper()
    if not app_set or upper in app_set:
        return upper
    base = lang_code.split('_')[0].split('-')[0]
    if base in APPSTORE_ALIASES:
        target = APPSTORE_ALIASES[base]
        if not app_set or target in app_set:
            return target
    if not app_set or base.upper() in app_set:
        return base.upper()
    return None


def fix_store_badges(content, lang_code):
    """
    Fix Google Play Store and Apple App Store image badge paths to use the localized badge.
    E.g. /images/misc/playstore/img/en_get.svg -> /images/misc/playstore/img/el_get.svg
    and /images/misc/appstore/black/appstore_US.svg -> /images/misc/appstore/black/appstore_GR.svg
    """
    fixes = 0
    play_badge = get_playstore_badge(lang_code)
    if play_badge:
        def replace_play_badge(m):
            nonlocal fixes
            old = m.group(0)
            prefix = m.group(1) # e.g. "https://static.openfoodfacts.org" or ""
            current = m.group(2)
            if current != play_badge:
                fixes += 1
                return f'{prefix}/images/misc/playstore/img/{play_badge}_get.svg'
            return old

        content = re.sub(
            r'((?:https://static\.openfoodfacts\.org)?)/images/misc/playstore/img/([a-zA-Z0-9_-]+)_get\.svg',
            replace_play_badge,
            content
        )

    app_badge = get_appstore_badge(lang_code)
    if app_badge:
        def replace_app_badge(m):
            nonlocal fixes
            old = m.group(0)
            prefix = m.group(1) # e.g. "https://static.openfoodfacts.org" or ""
            current = m.group(2)
            if current != app_badge:
                fixes += 1
                return f'{prefix}/images/misc/appstore/black/appstore_{app_badge}.svg'
            return old

        content = re.sub(
            r'((?:https://static\.openfoodfacts\.org)?)/images/misc/appstore/black/appstore_([a-zA-Z0-9_]+)\.svg',
            replace_app_badge,
            content
        )

    return content, fixes


def protect_brand_names(content):
    """
    Protect brand names according to Directive 1 (The "No-Translate" List).
    """
    fixes = 0
    for pattern, replacement in BRAND_PROTECTION_RULES:
        matches = len(re.findall(pattern, content))
        if matches:
            content = re.sub(pattern, replacement, content)
            fixes += matches
    return content, fixes


def fix_french_typography(content, lang_code):
    """
    Respect locale-specific typography for French (Directive 4):
    Non-breaking spaces (&nbsp;) before : ; ? ! and within « ».
    Applied only to text outside of HTML tags.
    """
    if lang_code != 'fr':
        return content, 0

    parts = re.split(r'(<[^>]+>)', content)
    fixes = 0
    for i in range(len(parts)):
        # Even indices are text outside HTML tags
        if i % 2 == 0:
            orig = parts[i]
            # Space before : ; ? !
            parts[i] = re.sub(r'([^\s&;])\s+([:;?!])', r'\1&nbsp;\2', parts[i])
            # Space inside guillemets
            parts[i] = re.sub(r'«\s+', '«&nbsp;', parts[i])
            parts[i] = re.sub(r'\s+»', '&nbsp;»', parts[i])
            if parts[i] != orig:
                fixes += 1

    return "".join(parts), fixes


def fix_known_repetitions(content):
    """
    Fix known text repetition patterns.
    """
    fixes = 0
    for find, replace in KNOWN_REPETITIONS:
        if find in content:
            content = content.replace(find, replace)
            fixes += 1
    return content, fixes


def is_css_pattern(text):
    """Check if the text is a CSS/style pattern that should be skipped."""
    for pattern in CSS_SKIP_PATTERNS:
        if re.search(pattern, text):
            return True
    return False


def fix_dynamic_repetitions(content, filepath):
    """
    Dynamically detect and fix text repetitions.
    """
    fixes = 0
    skip_files = ['landing-off.html', 'presse.html', 'revue-de-presse-fr.html']
    for skip_file in skip_files:
        if skip_file in filepath:
            return content, 0
    
    min_len = 20
    max_iterations = 50
    for _ in range(max_iterations):
        match = re.search(r'([^\n<>]{' + str(min_len) + r',}?)\s+\1', content, re.MULTILINE)
        if not match:
            break
        
        matched_text = match.group(1).strip()
        if is_css_pattern(matched_text):
            break
        if re.match(r'^[\s\n\r\t<>\/]+$', matched_text):
            break
        if re.match(r'^[a-z0-9_-]+$', matched_text, re.IGNORECASE):
            break
        if re.match(r'^["\'\(\)\[\]{}]+$', matched_text):
            break
        
        full_match = match.group(0)
        content = content.replace(full_match, matched_text, 1)
        fixes += 1
    
    return content, fixes


def process_file(filepath, fix_repetitions=True, fix_utm=True, fix_urls=True, fix_badges=True, fix_brands=True, fix_typography=True, verbose=False):
    """
    Process a single HTML file to fix translation issues.
    """
    lang_code = get_lang_code(filepath)
    if not lang_code or lang_code == 'README.md':
        return 0
    
    # Skip English folder for localized URL and campaign changes
    is_en = lang_code == 'en'
    
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception as e:
        if verbose:
            print(f"Error reading {filepath}: {e}", file=sys.stderr)
        return 0
    
    original = content
    total_fixes = 0
    fix_details = []
    
    if fix_repetitions:
        content, fixes = fix_known_repetitions(content)
        if fixes > 0:
            fix_details.append(f"{fixes} known repetitions")
        total_fixes += fixes
        
        content, fixes = fix_dynamic_repetitions(content, filepath)
        if fixes > 0:
            fix_details.append(f"{fixes} dynamic repetitions")
        total_fixes += fixes
    
    if fix_utm and not is_en:
        content, fixes = fix_utm_campaigns(content, lang_code)
        if fixes > 0:
            fix_details.append(f"{fixes} UTM params")
        total_fixes += fixes

    if fix_urls and not is_en:
        content, fixes = fix_app_store_urls(content, lang_code)
        if fixes > 0:
            fix_details.append(f"{fixes} app store URLs")
        total_fixes += fixes

    if fix_badges and not is_en:
        content, fixes = fix_store_badges(content, lang_code)
        if fixes > 0:
            fix_details.append(f"{fixes} store badges")
        total_fixes += fixes

    if fix_brands:
        content, fixes = protect_brand_names(content)
        if fixes > 0:
            fix_details.append(f"{fixes} protected brands")
        total_fixes += fixes

    if fix_typography:
        content, fixes = fix_french_typography(content, lang_code)
        if fixes > 0:
            fix_details.append(f"{fixes} typography spacing")
        total_fixes += fixes
    
    if content != original:
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            if verbose:
                print(f"Fixed {filepath}: {', '.join(fix_details)}")
            return total_fixes
        except Exception as e:
            print(f"Error writing {filepath}: {e}", file=sys.stderr)
            return 0
    
    return 0


def main():
    parser = argparse.ArgumentParser(
        description='Fix common translation issues in lang files',
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument('--base-dir', default='lang',
                        help='Base directory for language files (default: lang)')
    parser.add_argument('--fix-repetitions', action='store_true', default=True,
                        help='Fix repeated text (default: True)')
    parser.add_argument('--no-repetitions', action='store_true',
                        help='Skip fixing repetitions')
    parser.add_argument('--fix-utm', action='store_true', default=True,
                        help='Fix UTM parameters (default: True)')
    parser.add_argument('--no-utm', action='store_true',
                        help='Skip fixing UTM parameters')
    parser.add_argument('--fix-urls', action='store_true', default=True,
                        help='Fix App Store and Google Play URLs (default: True)')
    parser.add_argument('--no-urls', action='store_true',
                        help='Skip fixing URLs')
    parser.add_argument('--fix-badges', action='store_true', default=True,
                        help='Fix Play Store and App Store image badges (default: True)')
    parser.add_argument('--no-badges', action='store_true',
                        help='Skip fixing badges')
    parser.add_argument('--fix-brands', action='store_true', default=True,
                        help='Protect brand names from translation (default: True)')
    parser.add_argument('--no-brands', action='store_true',
                        help='Skip brand name protection')
    parser.add_argument('--fix-typography', action='store_true', default=True,
                        help='Fix locale typography spacing (default: True)')
    parser.add_argument('--no-typography', action='store_true',
                        help='Skip typography fixes')
    parser.add_argument('--verbose', '-v', action='store_true',
                        help='Verbose output')
    parser.add_argument('files', nargs='*',
                        help='Specific files to process (optional)')
    args = parser.parse_args()
    
    fix_repetitions = args.fix_repetitions and not args.no_repetitions
    fix_utm = args.fix_utm and not args.no_utm
    fix_urls = args.fix_urls and not args.no_urls
    fix_badges = args.fix_badges and not args.no_badges
    fix_brands = args.fix_brands and not args.no_brands
    fix_typography = args.fix_typography and not args.no_typography
    
    base_dir = args.base_dir
    if not os.path.isabs(base_dir):
        base_dir = os.path.join(os.getcwd(), base_dir)
    
    total_fixes = 0
    total_files = 0
    
    if args.files:
        files = args.files
    else:
        files = []
        for root, dirs, fnames in os.walk(base_dir):
            for fname in fnames:
                if fname.endswith('.html'):
                    files.append(os.path.join(root, fname))
    
    for html_file in files:
        fixes = process_file(
            html_file,
            fix_repetitions=fix_repetitions,
            fix_utm=fix_utm,
            fix_urls=fix_urls,
            fix_badges=fix_badges,
            fix_brands=fix_brands,
            fix_typography=fix_typography,
            verbose=args.verbose
        )
        if fixes > 0:
            total_files += 1
            total_fixes += fixes
    
    print(f"\n{'='*60}")
    print(f"📊 Summary: {total_fixes} fixes across {total_files} files")
    print(f"{'='*60}")
    
    return 0


if __name__ == '__main__':
    sys.exit(main())
