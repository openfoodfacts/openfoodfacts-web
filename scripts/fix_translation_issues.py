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
    # Green-Score translations (Directive 1: Reject "Pontuação Verde", "Puntuación Verde", "Score Vert", "Grüner Score")
    (r'\bLa [Pp]untuación [Vv]erde\b', 'El Green-Score'),
    (r'\bla [Pp]untuación [Vv]erde\b', 'el Green-Score'),
    (r'\b[Pp]untuación [Vv]erde\b', 'Green-Score'),
    (r'\bA [Pp]ontuação [Vv]erde\b', 'O Green-Score'),
    (r'\ba [Pp]ontuação [Vv]erde\b', 'o Green-Score'),
    (r'\b[Pp]ontuação [Vv]erde\b', 'Green-Score'),
    (r'\b[Ss]core [Vv]ert\b', 'Green-Score'),
    (r'\bGrüner Score\b', 'Green-Score'),
    (r'\bFatos Alimentares Abertos\b', 'Open Food Facts'),
    (r'\bEco-Sscore\b', 'Eco-Score'),
    (r'\bNutri-Sscore\b', 'Nutri-Score'),
    (r'أوبن فوود فاكتس', 'Open Food Facts'),
    (r'حقائق الطعام المفتوحة', 'Open Food Facts'),
    (r'حقائق الغذاء المفتوح', 'Open Food Facts'),
    (r'النوتري-النتيجة', 'Nutri-Score'),
    (r'Open Beauty Hunt', 'Open Food Hunt'),
    (r'Open Beauty 探索者', 'Open Food 探索者'),
    (r'Open Beauty 大使', 'Open Food 大使'),
    (r'contact@openbeautyfacts\.\s*org', 'contact@openfoodfacts.org'),
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


# Supported language codes for Creative Commons BY-SA 3.0 deeds
CC_DEED_LANG_MAP = {
    'an': 'an',
    'ar': 'ar',
    'az': 'az',
    'be': 'be',
    'bg': 'bg',
    'bn': 'bn',
    'ca': 'ca',
    'cs': 'cs',
    'da': 'da',
    'de': 'de',
    'el': 'el',
    'en': 'en',
    'en_AU': 'en',
    'en_GB': 'en',
    'eo': 'eo',
    'es': 'es',
    'et': 'et',
    'eu': 'eu',
    'fa': 'fa',
    'fi': 'fi',
    'fr': 'fr',
    'fy': 'fy',
    'ga': 'ga',
    'gl': 'gl',
    'hi': 'hi',
    'hr': 'hr',
    'hu': 'hu',
    'id': 'id',
    'is': 'is',
    'it': 'it',
    'ja': 'ja',
    'ko': 'ko',
    'lt': 'lt',
    'lv': 'lv',
    'ms': 'ms',
    'nb': 'no',
    'nl': 'nl',
    'nl_BE': 'nl',
    'nl_NL': 'nl',
    'nn': 'no',
    'no': 'no',
    'pl': 'pl',
    'pt': 'pt',
    'pt_PT': 'pt',
    'pt_BR': 'pt-br',
    'ro': 'ro',
    'ru': 'ru',
    'sk': 'sk',
    'sl': 'sl',
    'sr': 'sr-latn',
    'sr_CS': 'sr-latn',
    'sr_RS': 'sr-latn',
    'sv': 'sv',
    'tr': 'tr',
    'uk': 'uk',
    'zh': 'zh-hans',
    'zh_CN': 'zh-hans',
    'zh_HK': 'zh-hant',
    'zh_TW': 'zh-hant',
}


def fix_creative_commons_urls(content, lang_code):
    """
    Fix Creative Commons deed URLs based on the target language code.
    Directive 3: URL & Domain Consistency.
    Adapts https://creativecommons.org/licenses/by-sa/3.0/deed.en to deed.<lang>.
    Falls back to deed.en if CC doesn't support the language.
    """
    fixes = 0
    target_deed = CC_DEED_LANG_MAP.get(lang_code, 'en')

    def replace_cc_url(m):
        nonlocal fixes
        old = m.group(0)
        new = f'https://creativecommons.org/licenses/by-sa/3.0/deed.{target_deed}'
        if new != old:
            fixes += 1
            return new
        return old

    content = re.sub(r'https?://creativecommons\.org/licenses/by-sa/3\.0/deed\.[a-zA-Z_-]+', replace_cc_url, content)
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

# F-Droid badge language aliases: maps folder lang_code to F-Droid PNG code suffix
FDROID_ALIASES = {
    "tl": "fil",
    "he": "he",
    "iw": "he",
    "yi": "he",
    "uk": "ua",
    "nb": "no",
    "no": "no",
    "nn": "nn",
    "zh": "zh-cn",
    "zh_CN": "zh-cn",
    "zh_TW": "zh-tw",
    "zh_HK": "zh-hk",
    "pt_BR": "pt-br",
    "pt_PT": "pt-pt",
    "es_419": "es-419",
    "en_AU": "en-au",
    "en_GB": "en-gb",
    "en_CA": "en-ca",
    "en_US": "en-us",
    "fr_CA": "fr-ca",
    "fr_FR": "fr-fr",
    "nl_BE": "nl",
    "nl_NL": "nl",
    "sr_RS": "sr",
    "sr_CS": "sr",
}

# F-Droid badges available on openfoodfacts-server (/images/misc/f-droid/get-it-on-<lang>.png)
FDROID_BADGES = {
    "af", "am", "ar", "az", "be", "bg", "bn", "bs", "ca", "cs", "cy", "da", "de",
    "el", "en", "en-au", "en-ca", "en-gb", "en-us", "eo", "es", "es-419", "es-ar",
    "es-es", "es-mx", "et", "eu", "fa", "fi", "fil", "fr", "fr-ca", "fr-fr", "fy",
    "ga", "gd", "gl", "gu", "he", "hi", "hr", "hu", "hy", "id", "is", "it", "iw",
    "ja", "jp", "ka", "kk", "km", "kn", "ko", "ky", "lb", "lo", "lt", "lv", "mk",
    "ml", "mn", "mr", "ms", "my", "ne", "nl", "nn", "no", "pa", "pl", "pt",
    "pt-br", "pt-pt", "ro", "ru", "si", "sk", "sl", "sq", "sr", "sv", "sw", "ta",
    "te", "th", "tr", "ua", "ur", "uz", "vi", "zh-cn", "zh-hans", "zh-hant",
    "zh-hk", "zh-tw", "zu"
}

# Available badge sets (loaded dynamically if base dir exists, or cached defaults)
_PLAYSTORE_SVGS = None
_APPSTORE_SVGS = None
_FDROID_PNGS = None

def _get_available_badge_sets():
    global _PLAYSTORE_SVGS, _APPSTORE_SVGS, _FDROID_PNGS
    if _PLAYSTORE_SVGS is None:
        root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        play_dir = os.path.join(root_dir, 'html', 'images', 'misc', 'playstore', 'img')
        app_dir = os.path.join(root_dir, 'html', 'images', 'misc', 'appstore', 'black')
        fdroid_dir = os.path.join(root_dir, 'html', 'images', 'misc', 'f-droid')
        if os.path.isdir(play_dir):
            _PLAYSTORE_SVGS = {f.split('_get.svg')[0] for f in os.listdir(play_dir) if f.endswith('_get.svg')}
        else:
            _PLAYSTORE_SVGS = set()
        if os.path.isdir(app_dir):
            _APPSTORE_SVGS = {f.split('.svg')[0].replace('appstore_', '') for f in os.listdir(app_dir) if f.endswith('.svg')}
        else:
            _APPSTORE_SVGS = set()
        if os.path.isdir(fdroid_dir):
            _FDROID_PNGS = {f.replace('get-it-on-', '').replace('.png', '') for f in os.listdir(fdroid_dir) if f.startswith('get-it-on-') and f.endswith('.png')}
        else:
            _FDROID_PNGS = FDROID_BADGES
    return _PLAYSTORE_SVGS, _APPSTORE_SVGS, _FDROID_PNGS


def get_playstore_badge(lang_code):
    """Return the SVG badge prefix for Google Play Store for the given language code, or None."""
    if not lang_code:
        return None
    play_set, _, _ = _get_available_badge_sets()
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
    _, app_set, _ = _get_available_badge_sets()
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


def get_fdroid_badge(lang_code):
    """Return the PNG badge suffix for F-Droid for the given language code, or None."""
    if not lang_code:
        return None
    _, _, fdroid_set = _get_available_badge_sets()
    if lang_code in FDROID_ALIASES:
        target = FDROID_ALIASES[lang_code]
        if not fdroid_set or target in fdroid_set:
            return target
    val = lang_code.lower().replace('_', '-')
    if not fdroid_set or val in fdroid_set:
        return val
    base = lang_code.split('_')[0].split('-')[0].lower()
    if base in FDROID_ALIASES:
        target = FDROID_ALIASES[base]
        if not fdroid_set or target in fdroid_set:
            return target
    if not fdroid_set or base in fdroid_set:
        return base
    return None


def fix_store_badges(content, lang_code):
    """
    Fix Google Play Store, Apple App Store, and F-Droid image badge paths to use the localized badge.
    E.g. /images/misc/playstore/img/en_get.svg -> /images/misc/playstore/img/el_get.svg,
    /images/misc/appstore/black/appstore_US.svg -> /images/misc/appstore/black/appstore_GR.svg,
    and /images/misc/f-droid/get-it-on-en.png -> /images/misc/f-droid/get-it-on-de.png
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

    fdroid_badge = get_fdroid_badge(lang_code)
    if fdroid_badge:
        def replace_fdroid_badge(m):
            nonlocal fixes
            old = m.group(0)
            prefix = m.group(1) # e.g. "https://static.openfoodfacts.org" or ""
            current = m.group(2)
            if current != fdroid_badge:
                fixes += 1
                return f'{prefix}/images/misc/f-droid/get-it-on-{fdroid_badge}.png'
            return old

        content = re.sub(
            r'((?:https://static\.openfoodfacts\.org)?)/images/misc/f-droid/get-it-on(?:-([a-zA-Z0-9_-]+))?\.png',
            replace_fdroid_badge,
            content
        )

    return content, fixes


# Food revolution image translated assets available in openfoodfacts-server
FOOD_REVOLUTION_SVGS = {
    "ca", "cs", "da", "de", "en", "eo", "es", "eu", "fi", "fr",
    "gl", "hu", "id", "it", "nl", "no", "pl", "pt", "ro", "ru",
    "sv", "tr", "uk", "vi"
}

FOOD_REVOLUTION_ALIASES = {
    "nb": "no",
    "nn": "no",
    "nl_BE": "nl",
    "nl_NL": "nl",
    "pt_BR": "pt",
    "pt_PT": "pt",
}


def get_food_revolution_asset(lang_code):
    """Return the language code for join-the-food-revolution SVG, or None if not available."""
    if not lang_code:
        return None
    if lang_code in FOOD_REVOLUTION_ALIASES:
        target = FOOD_REVOLUTION_ALIASES[lang_code]
        if target in FOOD_REVOLUTION_SVGS:
            return target
    if lang_code in FOOD_REVOLUTION_SVGS:
        return lang_code
    base = lang_code.split('_')[0].split('-')[0].lower()
    if base in FOOD_REVOLUTION_ALIASES:
        target = FOOD_REVOLUTION_ALIASES[base]
        if target in FOOD_REVOLUTION_SVGS:
            return target
    if base in FOOD_REVOLUTION_SVGS:
        return base
    return None


def fix_food_revolution_assets(content, lang_code):
    """
    Fix join-the-food-revolution SVG path to use the localized asset when available.
    E.g. /images/misc/app-landing-page/join-the-food-revolution/join-the-food-revolution_en.svg -> _de.svg
    """
    target = get_food_revolution_asset(lang_code)
    if not target:
        return content, 0
    fixes = 0

    def replace_svg(m):
        nonlocal fixes
        prefix = m.group(1)
        current = m.group(2)
        if current != target:
            fixes += 1
            return f'{prefix}/images/misc/app-landing-page/join-the-food-revolution/join-the-food-revolution_{target}.svg'
        return m.group(0)

    content = re.sub(
        r'((?:https://static\.openfoodfacts\.org)?)/images/misc/app-landing-page/join-the-food-revolution/join-the-food-revolution_([a-zA-Z_-]+)\.svg',
        replace_svg,
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


def fix_facet_links(content):
    """
    Fix legacy facet links not prefixed with /facets/ and ensure plural form.
    E.g.:
      /label/fair-trade/origins -> /facets/labels/fair-trade/origins
      /label/commerce-equitable/origines -> /facets/labels/commerce-equitable/origines
      https://world.openfoodfacts.org/label/nutriscore/categories -> https://world.openfoodfacts.org/facets/labels/nutriscore/categories
      https://*.openfoodfacts.org/label/nutriscore/brands -> https://*.openfoodfacts.org/facets/labels/nutriscore/brands
      /categories/meals/environmental-score -> /facets/categories/meals/environmental-score
      /category/perfumes/origins -> /facets/categories/perfumes/origins
    """
    fixes = 0

    def replace_label(m):
        nonlocal fixes
        fixes += 1
        quote = m.group(1)
        domain = m.group(2) or ""
        tag = m.group(3)
        subfacet = m.group(4)
        return f'href={quote}{domain}/facets/labels/{tag}/{subfacet}{quote}'

    content, n1 = re.subn(
        r'href=([\'"])(https?://[a-z0-9.-]*openfoodfacts\.org)?/label/([a-zA-Z0-9_:-]+)/(origins|categories|brands|marques|origines|oorsprong)\1',
        replace_label,
        content
    )

    def replace_category(m):
        nonlocal fixes
        fixes += 1
        quote = m.group(1)
        domain = m.group(2) or ""
        tag = m.group(3)
        subfacet = m.group(4)
        return f'href={quote}{domain}/facets/categories/{tag}/{subfacet}{quote}'

    content, n2 = re.subn(
        r'href=([\'"])(https?://[a-z0-9.-]*openfoodfacts\.org)?/(?:category|categories)/([a-zA-Z0-9_:-]+)/(eco-score|environmental-score|origins)\1',
        replace_category,
        content
    )

    def replace_green_categories(m):
        nonlocal fixes
        fixes += 1
        quote = m.group(1)
        tag1 = m.group(2)
        tag2 = m.group(3)
        return f'href={quote}/facets/categories/{tag1}/{tag2}{quote}'

    content, n3 = re.subn(
        r'href=([\'"])/categories/(aduan|dumuni|meals|swakudya)/(nne|lamini-jateb|anviw|puntuaci|xikoro-xa-mbango)\1',
        replace_green_categories,
        content
    )

    return content, fixes


def clean_css(css_text):
    """Clean corrupted non-breaking spaces from CSS inside style tags."""
    return css_text.replace("&nbsp;", " ")


def clean_js(js_text):
    """Scanner for JS that replaces corrupted &nbsp; with a space when not inside string literals."""
    res = []
    i = 0
    n = len(js_text)
    state_stack = ["CODE"]
    template_brace_depth = []

    while i < n:
        state = state_stack[-1]
        c = js_text[i]
        c2 = js_text[i:i+2]

        if state == "CODE":
            if c2 == "//":
                res.append(c2)
                i += 2
                state_stack.append("COMMENT_LINE")
                continue
            elif c2 == "/*":
                res.append(c2)
                i += 2
                state_stack.append("COMMENT_BLOCK")
                continue
            elif c == "'":
                res.append(c)
                i += 1
                state_stack.append("SINGLE")
                continue
            elif c == '"':
                res.append(c)
                i += 1
                state_stack.append("DOUBLE")
                continue
            elif c == '`':
                res.append(c)
                i += 1
                state_stack.append("TEMPLATE")
                template_brace_depth.append(0)
                continue
            elif js_text[i:i+6] == "&nbsp;":
                res.append(" ")
                i += 6
                continue
            else:
                res.append(c)
                i += 1
                continue

        elif state == "COMMENT_LINE":
            res.append(c)
            i += 1
            if c == "\n":
                state_stack.pop()
            continue

        elif state == "COMMENT_BLOCK":
            if c2 == "*/":
                res.append(c2)
                i += 2
                state_stack.pop()
            else:
                res.append(c)
                i += 1
            continue

        elif state == "SINGLE":
            if c == "\n":
                state_stack.pop()
                res.append(c)
                i += 1
                continue
            if c == "\\":
                res.append(js_text[i:i+2])
                i += 2
                continue
            res.append(c)
            i += 1
            if c == "'":
                state_stack.pop()
            continue

        elif state == "DOUBLE":
            if c == "\n":
                state_stack.pop()
                res.append(c)
                i += 1
                continue
            if c == "\\":
                res.append(js_text[i:i+2])
                i += 2
                continue
            res.append(c)
            i += 1
            if c == '"':
                state_stack.pop()
            continue

        elif state == "TEMPLATE":
            if c == "\\":
                res.append(js_text[i:i+2])
                i += 2
                continue
            if c2 == "${":
                res.append(c2)
                i += 2
                state_stack.append("TEMPLATE_EXPR")
                template_brace_depth[-1] = 1
                continue
            res.append(c)
            i += 1
            if c == '`':
                state_stack.pop()
                template_brace_depth.pop()
            continue

        elif state == "TEMPLATE_EXPR":
            if c2 == "//":
                res.append(c2)
                i += 2
                state_stack.append("COMMENT_LINE")
                continue
            elif c2 == "/*":
                res.append(c2)
                i += 2
                state_stack.append("COMMENT_BLOCK")
                continue
            elif c == "'":
                res.append(c)
                i += 1
                state_stack.append("SINGLE")
                continue
            elif c == '"':
                res.append(c)
                i += 1
                state_stack.append("DOUBLE")
                continue
            elif c == '`':
                res.append(c)
                i += 1
                state_stack.append("TEMPLATE")
                template_brace_depth.append(0)
                continue
            elif c == "{":
                res.append(c)
                i += 1
                template_brace_depth[-1] += 1
                continue
            elif c == "}":
                res.append(c)
                i += 1
                template_brace_depth[-1] -= 1
                if template_brace_depth[-1] == 0:
                    state_stack.pop()
                continue
            elif js_text[i:i+6] == "&nbsp;":
                res.append(" ")
                i += 6
                continue
            else:
                res.append(c)
                i += 1
                continue

    return "".join(res)


def fix_corrupted_css_js(content):
    """
    Repair corrupted CSS and JS entities (e.g. &nbsp;!important, &nbsp;!==, &nbsp;?)
    inside <style> and <script> blocks.
    """
    fixes = 0

    def replace_style(m):
        nonlocal fixes
        open_tag, body, close_tag = m.group(1), m.group(2), m.group(3)
        cleaned = clean_css(body)
        if cleaned != body:
            fixes += 1
            return f"{open_tag}{cleaned}{close_tag}"
        return m.group(0)

    content = re.sub(r'(<style\b[^>]*>)(.*?)(</style>)', replace_style, content, flags=re.DOTALL | re.IGNORECASE)

    def replace_script(m):
        nonlocal fixes
        open_tag, body, close_tag = m.group(1), m.group(2), m.group(3)
        cleaned = clean_js(body)
        if cleaned != body:
            fixes += 1
            return f"{open_tag}{cleaned}{close_tag}"
        return m.group(0)

    content = re.sub(r'(<script\b[^>]*>)(.*?)(</script>)', replace_script, content, flags=re.DOTALL | re.IGNORECASE)

    return content, fixes


def fix_pseudo_xml_tags(content):
    """
    Remove or fix pseudo-XML tags (<0>, </0>, <1/>, etc.) that leaked from translation systems.
    """
    fixes = 0

    replacements = [
        # Material Icons: <0>add_task</0> -> <span class="material-icons" translate="no">add_task</span>
        (r'<0>add_task</0>', '<span class="material-icons" translate="no">add_task</span>'),
        # SDK filter label in data.html: <0>Фильтр по имени:</0> -> <label for="sdkFilter">Фильтр по имени:</label>
        (r'<0>(Фильтр по имени:)</0>', r'<label for="sdkFilter">\1</label>'),
        # Wiki links in data.html: у <0>Wiki</0> -> у <a href="https://wiki.openfoodfacts.org/">Wiki</a>
        (r'<0>Wiki</0>', '<a href="https://wiki.openfoodfacts.org/">Wiki</a>'),
        # Search form in opf data.html: geavanceerde zoekformulier <0>. -> geavanceerde zoekformulier</a>.
        (r'geavanceerde zoekformulier\s*<0>\.', 'geavanceerde zoekformulier</a>.'),
        # Mobile app highlight spans:
        (r'hele beeld<0>', 'hele beeld</span>'),
        (r'<0>economia circular</0>', '<span class="highlight-label green rotate-left">economia circular</span>'),
        (r'<0>повну картину</0>', '<span class="highlight-label orange rotate-left">повну картину</span>'),
        (r'<0>планету</0>', '<span class="highlight-label green rotate-left">планету</span>'),
        # Green-score Wikipedia link:
        (r'A análise do ciclo de vida<0>', 'A análise do ciclo de vida</a>'),
        # Press release:
        (r'に変身します<0>。', 'に変身します</strong>。'),
        (r'</0></0></0>\.', '.'),
        (r'참가하신다면</0>\(', '참가하신다면('),
        (r'எப்படி என்பதைப் பற்றி மேலும் அறிய</a>\s*</0>பார்க்கவும்', 'எப்படி என்பதைப் பற்றி மேலும் அறிய</a> பார்க்கவும்'),
        (r'<a href="https://slack\.openfoodfacts\.org"></0></a>', '<a href="https://slack.openfoodfacts.org">Slack</a>'),
        (r'или <0>о калориях</strong>', 'или <strong>о калориях</strong>'),
        (r'увеличивается значимость <0>более отзывчивого</strong>', 'увеличивается значимость <strong>более отзывчивого</strong>'),
        (r'\s*По случаю празднования десятой годовщины, эта <0>новая версия позволит нам в дальнейшем увеличить наше влияние по всему миру\.', ''),
        (r'отримати<0> Nutri-Score і визначити<0>,', 'отримати <strong>Nutri-Score</strong> і визначити,'),
    ]

    for pattern, replacement in replacements:
        matches = len(re.findall(pattern, content))
        if matches:
            content = re.sub(pattern, replacement, content)
            fixes += matches

    return content, fixes


def fix_french_typography(content, lang_code):
    """
    Respect locale-specific typography for French (Directive 4):
    Non-breaking spaces (&nbsp;) before : ; ? ! and within « ».
    Applied only to text outside of HTML tags and protected code/style blocks.
    """
    if lang_code != 'fr':
        return content, 0

    # Mask protected blocks: <script>...</script>, <style>...</style>,
    # <code>...</code>, <pre>...</pre>, <!--...-->, and [[...]] includes
    protected_blocks = []
    def mask_block(m):
        protected_blocks.append(m.group(0))
        return f"___OFF_PROTECTED_BLOCK_{len(protected_blocks) - 1}___"

    pattern = re.compile(
        r'(<script\b[^>]*>.*?</script>|<style\b[^>]*>.*?</style>|<code\b[^>]*>.*?</code>|<pre\b[^>]*>.*?</pre>|<!--.*?-->|\[\[.*?\]\])',
        re.DOTALL | re.IGNORECASE
    )
    masked_content = pattern.sub(mask_block, content)

    parts = re.split(r'(<[^>]+>)', masked_content)
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

    result = "".join(parts)
    # Unmask protected blocks
    for idx, block in enumerate(protected_blocks):
        result = result.replace(f"___OFF_PROTECTED_BLOCK_{idx}___", block)

    return result, fixes


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


def fix_api_error_leaks(content):
    """
    Strip leaked machine-translation / LLM API key errors or refusal strings.
    E.g., 'Incorrect Api key provided: sk-dCEE0***************************************OfZI. You can find your Api key at https://platform. openai. com/account/api-keys.'
    """
    fixes = 0
    # Remove full paragraphs containing only an API key error
    content, n1 = re.subn(
        r'<p[^>]*>\s*Incorrect A(?:PI|pi) key provided:\s*sk-[A-Za-z0-9*]+\.\s*You can find your A(?:PI|pi) key at https?://platform\.\s*openai\.\s*com/account/api-keys\.?\s*</p>\s*',
        '',
        content
    )
    fixes += n1
    # Remove inline leaked API key error strings
    content, n2 = re.subn(
        r'\s*Incorrect A(?:PI|pi) key provided:\s*sk-[A-Za-z0-9*]+\.\s*You can find your A(?:PI|pi) key at https?://platform\.\s*openai\.\s*com/account/api-keys\.?',
        '',
        content
    )
    fixes += n2
    return content, fixes


LOCALIZED_PRESS_FILENAMES = {
    'premsa.html': 'press.html',
    'presse.html': 'press.html',
    'prentsa.html': 'press.html',
    'prensa.html': 'press.html',
    'prasa.html': 'press.html',
}

LOCALIZED_CONTRIBUTE_FILENAMES = {
    'contribuír.html': 'contribute.html',
}


def _get_rel_and_en_path(filepath, base_dir):
    norm = filepath.replace('\\', '/')
    m = re.search(r'/lang/(?:(?:obf|opff|opf)/)?([^/]+)/texts/(.+)$', norm)
    if not m:
        m = re.match(r'^lang/(?:(?:obf|opff|opf)/)?([^/]+)/texts/(.+)$', norm)
    if not m:
        return None, None
    rel = m.group(2)
    mapped_rel = LOCALIZED_PRESS_FILENAMES.get(rel, LOCALIZED_CONTRIBUTE_FILENAMES.get(rel, rel))
    en_path = os.path.join(base_dir, 'en', 'texts', mapped_rel)
    return mapped_rel, en_path


def _is_valid_include(inc, lang_code, base_dir):
    clean = inc.strip()
    if clean.startswith('query:'):
        return True
    if clean.startswith('texts/'):
        clean = clean[6:]
    if clean in ('products_stats_<cc>.html', 'missions_list.html', 'iphone-de.html', 'android-de.html'):
        return True
    if clean.startswith('cop26/blocks/'):
        return True
    if os.path.isfile(os.path.join(base_dir, 'en', 'texts', clean)):
        return True
    if lang_code and os.path.isfile(os.path.join(base_dir, lang_code, 'texts', clean)):
        return True
    return False


_EN_INCS_CACHE = {}
_EN_ICONS_CACHE = {}


def _get_en_incs(en_path):
    if not en_path:
        return []
    if en_path not in _EN_INCS_CACHE:
        if os.path.isfile(en_path):
            try:
                with open(en_path, 'r', encoding='utf-8', errors='ignore') as f:
                    _EN_INCS_CACHE[en_path] = re.findall(r'\[\[(.*?)\]\]', f.read())
            except Exception:
                _EN_INCS_CACHE[en_path] = []
        else:
            _EN_INCS_CACHE[en_path] = []
    return _EN_INCS_CACHE[en_path]


def _get_en_icons(en_path):
    if not en_path:
        return []
    if en_path not in _EN_ICONS_CACHE:
        if os.path.isfile(en_path):
            try:
                with open(en_path, 'r', encoding='utf-8', errors='ignore') as f:
                    _EN_ICONS_CACHE[en_path] = [
                        m.group(1).strip()
                        for m in re.finditer(r'<span class=[\'"]material-icons[^\'"]*[\'"][^>]*>([^<]*)</span>', f.read())
                    ]
            except Exception:
                _EN_ICONS_CACHE[en_path] = []
        else:
            _EN_ICONS_CACHE[en_path] = []
    return _EN_ICONS_CACHE[en_path]


def fix_template_includes(content, lang_code, filepath, base_dir):
    """
    Validate and repair broken/translated [[...]] template includes in translated HTML files
    against the corresponding English source file in lang/en/texts/.
    """
    if lang_code == 'en' or '[[' not in content:
        return content, 0

    rel, en_path = _get_rel_and_en_path(filepath, base_dir)
    if not rel:
        return content, 0

    matches = list(re.finditer(r'\[\[(.*?)\]\]', content))
    if not matches:
        return content, 0

    en_incs = _get_en_incs(en_path)

    fixes = 0
    # Special check for nova.html where ro duplicated group-3-ingredients instead of group-4-ingredients
    if rel == 'nova.html' and len(matches) == len(en_incs):
        curr_incs = [m.group(1) for m in matches]
        if curr_incs != en_incs:
            new_content = content
            for m_obj, en_inc in zip(reversed(matches), reversed(en_incs)):
                if m_obj.group(1) != en_inc:
                    s, e = m_obj.span()
                    new_content = new_content[:s] + f'[[{en_inc}]]' + new_content[e:]
                    fixes += 1
            return new_content, fixes

    new_content = content
    for idx in range(len(matches) - 1, -1, -1):
        m_obj = matches[idx]
        inc = m_obj.group(1)
        if _is_valid_include(inc, lang_code, base_dir):
            continue

        replacement = None
        if len(matches) == len(en_incs):
            replacement = en_incs[idx]
        elif rel == 'press.html':
            if idx == 0 or 'rss' in inc.lower() or idx < len(matches) - 1:
                replacement = 'texts/presskit-rss.html'
            else:
                replacement = 'texts/sendinblue.html'
        elif rel == 'nova.html':
            # Match group number 1..4
            num_m = re.search(r'[1-4]', inc)
            if num_m:
                g_num = num_m.group(0)
                if idx >= 4:
                    replacement = f'processing/group-{g_num}-ingredients.html'
                else:
                    replacement = f'processing/group-{g_num}-description.html'
        elif rel == 'development.html':
            if 'general' in inc or idx == 0:
                replacement = 'texts/dev-general.html'
            elif 'server' in inc or idx >= len(matches) - 2:
                replacement = 'texts/dev-server.html'
        else:
            # Try matching by basename suffix in en_incs
            inc_nospace = inc.replace(' ', '')
            for cand in en_incs:
                cand_base = cand.split('/')[-1]
                if inc_nospace.endswith(cand_base) or cand_base in inc_nospace:
                    replacement = cand
                    break
            if not replacement and len(en_incs) == 1:
                replacement = en_incs[0]

        if replacement and replacement != inc:
            s, e = m_obj.span()
            new_content = new_content[:s] + f'[[{replacement}]]' + new_content[e:]
            fixes += 1

    return new_content, fixes


VALID_MATERIAL_ICONS = {
    'add_circle', 'add_task', 'arrow_back', 'arrow_forward', 'assignment',
    'auto_stories', 'biotech', 'check', 'check_circle', 'close',
    'cloud_download', 'code', 'content_copy', 'dataset', 'delete',
    'description', 'download', 'eco', 'edit', 'edit_note', 'email', 'event',
    'expand_less', 'expand_more', 'explore', 'extension', 'favorite',
    'filter_list', 'folder', 'folder_open', 'format_quote', 'forum', 'globe',
    'group', 'GROUPS', 'groups', 'handshake', 'help', 'help_outline',
    'history', 'home', 'hub', 'image', 'info', 'insights', 'inventory_2',
    'language', 'launch', 'leaderboard', 'lightbulb', 'link', 'Linked_camera',
    'list', 'local_offer', 'lock', 'login', 'map', 'menu', 'menu_book',
    'military_tech', 'more_vert', 'newspaper', 'notifications', 'open_in_new',
    'palette', 'people', 'person', 'photo_camera', 'picture_as_pdf', 'place',
    'play_arrow', 'play_circle', 'podcasts', 'public', 'publish', 'qr_code',
    'qr_code_scanner', 'query_stats', 'quiz', 'receipt_long', 'Refresh',
    'refresh', 'restaurant', 'rocket_launch', 'rss_feed', 'rule', 'savings',
    'scale', 'scanner', 'schema', 'school', 'science', 'search', 'security',
    'sell', 'send', 'settings', 'share', 'shield', 'shopping_bag',
    'shopping_cart', 'smart_toy', 'smartphone', 'sort', 'source',
    'Auto_awesome', 'auto_awesome', 'star', 'store', 'storage', 'support',
    'sync', 'table_chart', 'tag', 'terminal', 'thumb_up', 'timeline',
    'tips_and_updates', 'translate', 'trending_up', 'tune', 'update', 'upload',
    'verified', 'videocam', 'video_library', 'view_in_ar', 'view_list',
    'visibility', 'volunteer_activism', 'warning', 'web', 'widgets', 'work',
    'workspace_premium',
}


def fix_material_icons(content, lang_code, filepath, base_dir):
    """
    Restore translated or corrupted Material Icons ligatures (<span class="material-icons">...</span>)
    using the corresponding English source file.
    """
    if 'material-icons' not in content:
        return content, 0

    fixes = 0
    # Fix merged ligature + text in lang/obf/hr/texts/index.html: <span class="material-icons">auto_storiesSaznajte
    content, n_merged = re.subn(
        r'(<span class=[\'"]material-icons[^\'"]*[\'"][^>]*>)\s*(auto_stories|add_task)([^\s<][^<]*)(</span>)',
        r'\1\2\4\3',
        content
    )
    fixes += n_merged

    rel, en_path = _get_rel_and_en_path(filepath, base_dir)
    en_icons = _get_en_icons(en_path)

    span_re = re.compile(r'(<span class=[\'"]material-icons[^\'"]*[\'"][^>]*>)([^<]*)(</span>)')
    matches = list(span_re.finditer(content))
    if not matches:
        return content, fixes

    new_content = content
    for idx in range(len(matches) - 1, -1, -1):
        m_obj = matches[idx]
        lig = m_obj.group(2).strip()
        if not lig or re.match(r'^[a-z0-9_]+$', lig) and lig in VALID_MATERIAL_ICONS:
            continue

        # Determine replacement
        replacement = None
        if len(matches) == len(en_icons):
            replacement = en_icons[idx]
        elif lig.lower() in VALID_MATERIAL_ICONS:
            replacement = lig.lower()
        elif rel == 'index.html':
            replacement = 'auto_stories' if idx == 0 else 'add_task'
        elif rel == 'press.html':
            replacement = 'download'
        elif lig == 'datasæt':
            replacement = 'dataset'
        elif lig == 'videokamera':
            replacement = 'videocam'

        if replacement and replacement != m_obj.group(2):
            s, e = m_obj.span()
            new_content = new_content[:s] + f'{m_obj.group(1)}{replacement}{m_obj.group(3)}' + new_content[e:]
            fixes += 1

    return new_content, fixes


def fix_sister_project_contamination(content, lang_code, filepath, base_dir):
    """
    Fix sister-project contamination (Open Beauty Facts / Open Pet Food Facts / cosmetics text)
    leaking into Open Food Facts pages from shared Crowdin Translation Memory.
    """
    norm = filepath.replace('\\', '/')
    if re.search(r'/lang/(?:obf|opff|opf)/', norm) or re.match(r'^lang/(?:obf|opff|opf)/', norm):
        return content, 0

    rel, en_path = _get_rel_and_en_path(filepath, base_dir)
    if not rel:
        return content, 0

    fixes = 0
    # 1. Fix translated Google Scholar query URLs in scientific-publications.html
    if rel == 'scientific-publications.html':
        def fix_scholar_links(m):
            nonlocal fixes
            full = m.group(0)
            # Check if q= has non-ASCII or corrupted query
            fixed = re.sub(r'хттпс://сцхолар\.гоогле\.цом/сцхолар\?хл=ен&ас_сдт=0%2C5&q=%22[^"&]+%22&бтнГ=',
                           'https://scholar.google.com/scholar?hl=en&as_sdt=0%2C5&q=%22openbeautyfacts%22&btnG=', full)
            if fixed != full:
                fixes += 1
                return fixed
            if 'OpenBeautyFacts' in full and 'q=%22openbeautyfacts%22' not in full:
                fixed = re.sub(r'as_sdt=0%2C[^&]+&q=%22[^"&]+%22', 'as_sdt=0%2C5&q=%22openbeautyfacts%22', full)
                if fixed != full:
                    fixes += 1
                    return fixed
            return full

        content = re.sub(r'<li><a href="[^"]*scholar[^"]*"[^>]*>.*?</a></li>', fix_scholar_links, content)

        # Also fix line 41 (4-term OR query in Google Scholar) if translated
        def fix_scholar_or_query(m):
            nonlocal fixes
            old_q = m.group(1)
            target_q = '%22open+food+facts%22+OR+%22openfoodfacts%22+OR+%22open+beauty+facts%22+OR+%22openbeautyfacts%22'
            if old_q != target_q and ('openfoodfacts' in old_q or 'open' in old_q):
                fixes += 1
                return f'https://scholar.google.com/scholar?hl=en&as_sdt=0%2C5&q={target_q}&btnG='
            return m.group(0)

        content = re.sub(
            r'https://scholar\.google\.com/scholar\?hl=en&as_sdt=0%2C5&q=(%22[^"&]+)&btnG=',
            lambda m: fix_scholar_or_query(m) if m.group(1).count('%22') >= 6 else m.group(0),
            content
        )
        # Fix line 39 if "open+beauty+facts" was translated in mg
        content, n_mg = re.subn(
            r'q=%22open\+hatsaran-tarehy\+zava-misy%22',
            'q=%22open+beauty+facts%22',
            content
        )
        fixes += n_mg
        return content, fixes

    # 2. In data.html: fix specific Slack and mobile app code contaminations
    if rel == 'data.html':
        content, n1 = re.subn(r'Open Beauty Facts Slack', 'Open Food Facts Slack', content)
        content, n2 = re.subn(
            r'Код мобильного приложения Open Pet Food Facts',
            'Код мобильного приложения Open Food Facts',
            content
        )
        fixes += n1 + n2
        return content, fixes

    # 3. For pages whose English source does NOT mention sister projects (contribute.html, discover.html, open-food-hunt.html, index.html)
    if rel in ('contribute.html', 'discover.html', 'open-food-hunt.html', 'index.html'):
        content, n1 = re.subn(r'Open Beauty Facts|Open Pet Food Facts|Open Products Facts', 'Open Food Facts', content)
        content, n2 = re.subn(r'openbeautyfacts\.org|openpetfoodfacts\.org|openproductsfacts\.org', 'openfoodfacts.org', content)
        content, n3 = re.subn(r'#openbeautyfacts', '#general', content)
        fixes += n1 + n2 + n3

    # 4. Specific cosmetics/beauty TM contamination in discover.html (pl, pt_BR, ru, fi)
    if rel == 'discover.html':
        discover_replacements = [
            # Polish
            ('Open your cosmetics and know what you use on your body', 'Otwórz swoje jedzenie i dowiedz się, co jesz'),
            ('A cosmetics products database', 'Baza danych produktów spożywczych'),
            ('Data about cosmetics is of public interest and has to be open.', 'Dane o żywności leżą w interesie publicznym i muszą być otwarte.'),
            ('Make better cosmetics choices', 'Dokonuj lepszych wyborów żywieniowych'),
            ('Cosmetics knowledge is power to pamper yourself better!', 'Wiedza o jedzeniu daje siłę do lepszego odżywiania!'),
            ('Do you know which shampoos have the less chemicals?', 'Czy wiesz, które płatki śniadaniowe mają najmniej tłuszczu i cukru?'),
            ('Origins of ingredients of Perfumes', 'Pochodzenie składników produktów Fair Trade'),
            ('Curious about cosmetics?', 'Ciekawi Cię jedzenie?'),
            ('Cosmetics, for innovation and science', 'Żywność dla innowacji i nauki'),
            ('How many cosmetics commercials have you seen in your life?', 'Ile reklam jedzenia widziałeś w swoim życiu?'),
            # Portuguese (pt_BR)
            ('O banco de dados de produtos cosméticos', 'O banco de dados de produtos alimentícios'),
            ('Os dados sobre cosmeticos são de interesse público', 'Os dados sobre alimentos são de interesse público'),
            ('Faça melhores escolhas de cosméticos', 'Faça melhores escolhas alimentares'),
            ('Você sabe quais champôs têm menos produtos químicos?', 'Você sabe quais cereais matinais têm menos gordura e açúcar?'),
            ('Origens de ingredientes de perfumes', 'Origens dos ingredientes de produtos de comércio justo'),
            ('Cosméticos, para inovação e ciência', 'Alimentos, para inovação e ciência'),
            ('Quantos comerciais de cosméticos viu na sua vida?', 'Quantos comerciais de alimentos viu na sua vida?'),
            # Russian (ru)
            ('База данных косметических продуктов', 'База данных продуктов питания'),
            ('Происхождение ингредиентов парфюмерии', 'Происхождение ингредиентов продуктов справедливой торговли'),
            ('Сколько рекламных роликов косметики вы видели в своей жизни?', 'Сколько рекламных роликов еды вы видели в своей жизни?'),
            # Finnish (fi)
            ('Tee parempia kosmetiikkavalintoja', 'Tee parempia ruokavalintoja'),
            ('Kosmetiikkaa, innovaatiolle ja tieteelle', 'Ruokaa innovaatiolle ja tieteelle'),
        ]
        for old_str, new_str in discover_replacements:
            if old_str in content:
                content = content.replace(old_str, new_str)
                fixes += 1

    return content, fixes


def _dedup_block_inner_html(inner):
    """
    Deduplicate consecutive repeated sentences or clauses inside an HTML text block (<p>, <li>, <dd>, <h1-6>)
    in strictly linear O(N) time without regex backreferences.
    Supports inline HTML tags (<a ...>...</a>, <strong>, <b>, <em>) and multi-line paragraphs,
    as well as CJK/Arabic/Latin sentence punctuation and ABAB sentence loops.
    """
    if len(inner) < 20 or len(inner) > 4000 or '<div' in inner or '<table' in inner or '<ul' in inner or '<ol' in inner or '<script' in inner or '<style' in inner:
        return inner, 0

    fixes = 0
    cur = inner

    # 1. Exact half-string duplication in O(N) using word/line splitting (no regex backreference)
    stripped = cur.strip()
    words = stripped.split()
    if len(words) >= 6 and len(words) % 2 == 0:
        half = len(words) // 2
        if words[:half] == words[half:]:
            # Find the midpoint in stripped where the second half starts
            first_half_str = " ".join(words[:half])
            if len(first_half_str) >= 15 and not is_css_pattern(first_half_str):
                # Slice stripped up to the second occurrence of words[0] near the middle
                mid_pos = len(stripped) // 2
                # Find whitespace around mid_pos
                ws_match = re.search(r'\s+', stripped[max(0, mid_pos - 10):mid_pos + 10])
                if ws_match:
                    cut = max(0, mid_pos - 10) + ws_match.start()
                    if stripped[:cut].split() == words[:half]:
                        lead = cur[:len(cur) - len(cur.lstrip())]
                        trail = cur[len(cur.rstrip()):]
                        return lead + stripped[:cut] + trail, 1

    # 2. Split into sentences keeping delimiters (. ! ? 。 ！ ？ ؟) in O(N)
    parts = re.split(r'([.!?。！？؟]+(?:\s+|&nbsp;)*)', cur)
    sentences = []
    idx_p = 0
    while idx_p < len(parts):
        seg = parts[idx_p]
        if idx_p + 1 < len(parts):
            seg += parts[idx_p + 1]
            idx_p += 2
        else:
            idx_p += 1
        if seg:
            sentences.append(seg)

    if len(sentences) >= 2:
        def norm_sent(s):
            return re.sub(r'(?:\s+|&nbsp;)+', ' ', s).strip()

        norms = [norm_sent(s) for s in sentences]
        changed = True
        while changed:
            changed = False
            # Check consecutive identical sentences (AA -> A)
            i = 0
            new_sents = []
            new_norms = []
            while i < len(sentences):
                norm_i = norms[i]
                if i + 1 < len(sentences) and len(norm_i) >= 12 and norm_i == norms[i + 1]:
                    new_sents.append(sentences[i])
                    new_norms.append(norm_i)
                    i += 2
                    fixes += 1
                    changed = True
                    while i < len(sentences) and norms[i] == norm_i:
                        i += 1
                elif (
                    i + 1 < len(sentences)
                    and len(norm_i) >= 20
                    and norm_i.replace('/label/', '/facets/labels/') == norms[i + 1].replace('/label/', '/facets/labels/')
                ):
                    pick_idx = i + 1 if '/facets/labels/' in sentences[i + 1] else i
                    new_sents.append(sentences[pick_idx])
                    new_norms.append(norms[pick_idx])
                    i += 2
                    fixes += 1
                    changed = True
                else:
                    new_sents.append(sentences[i])
                    new_norms.append(norm_i)
                    i += 1
            sentences, norms = new_sents, new_norms

            # Check ABAB sentence loops (Sentence 1 + Sentence 2 + Sentence 1 + Sentence 2)
            i = 0
            new_sents = []
            new_norms = []
            while i < len(sentences):
                if (
                    i + 3 < len(sentences)
                    and len(norms[i]) + len(norms[i + 1]) >= 20
                    and norms[i] == norms[i + 2]
                    and norms[i + 1] == norms[i + 3]
                ):
                    new_sents.extend([sentences[i], sentences[i + 1]])
                    new_norms.extend([norms[i], norms[i + 1]])
                    i += 4
                    fixes += 1
                    changed = True
                elif (
                    i + 2 < len(sentences)
                    and len(norms[i]) >= 25
                    and norms[i] == norms[i + 2]
                ):
                    new_sents.extend([sentences[i], sentences[i + 1]])
                    new_norms.extend([norms[i], norms[i + 1]])
                    i += 3
                    fixes += 1
                    changed = True
                else:
                    new_sents.append(sentences[i])
                    new_norms.append(norms[i])
                    i += 1
            sentences, norms = new_sents, new_norms

        if fixes > 0:
            cur = "".join(sentences)

    return cur, fixes


def fix_dynamic_repetitions(content, filepath):
    """
    Dynamically detect and fix text repetitions outside of <style>, <script>, <svg>, and HTML comments
    in strictly linear O(N) time.
    """
    fixes = 0
    skip_files = ['landing-off.html', 'presse.html', 'revue-de-presse-fr.html']
    for skip_file in skip_files:
        if skip_file in filepath:
            return content, 0

    protected_re = re.compile(
        r'(<style[^>]*>.*?</style>|<script[^>]*>.*?</script>|<svg[^>]*>.*?</svg>|<!--.*?-->)',
        flags=re.DOTALL | re.IGNORECASE
    )
    chunks = protected_re.split(content)

    block_re = re.compile(r'(<(p|li|dd|dt|h[1-6]|blockquote)\b[^>]*>)(.*?)(</\2>)', flags=re.DOTALL | re.IGNORECASE)

    for idx in range(0, len(chunks), 2):
        chunk = chunks[idx]

        def replace_block(m):
            nonlocal fixes
            open_tag, tag_name, inner, close_tag = m.group(1), m.group(2), m.group(3), m.group(4)
            new_inner, f_cnt = _dedup_block_inner_html(inner)
            if f_cnt > 0:
                fixes += f_cnt
                return open_tag + new_inner + close_tag
            return m.group(0)

        chunks[idx] = block_re.sub(replace_block, chunk)

    return "".join(chunks), fixes


def fix_repeated_substring_loops(content):
    """
    Fix repeated emoticons and token loops introduced by Crowdin translation memory.
    e.g. '&nbsp;:-)&nbsp;:-)' -> '&nbsp;:-)'
    or ' :-) :-) :-) ...' -> ' :-)'
    """
    pattern = re.compile(r'((?:&nbsp;|\s)*:[-~]?[)D(PpoO])(?:\s+|&nbsp;)*(?:\1)+')
    new_content, count = pattern.subn(
        lambda m: ('&nbsp;' if '&nbsp;' in m.group(1) else ' ') + m.group(1).strip().replace('&nbsp;', ''),
        content
    )
    return new_content, count


def process_file(filepath, fix_repetitions=True, fix_utm=True, fix_urls=True, fix_badges=True, fix_brands=True, fix_typography=True, fix_facets=True, verbose=False):
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
    root_lang_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'lang')
    
    content, fixes = fix_api_error_leaks(content)
    if fixes > 0:
        fix_details.append(f"{fixes} leaked API error strings")
    total_fixes += fixes

    if not is_en:
        content, fixes = fix_template_includes(content, lang_code, filepath, root_lang_dir)
        if fixes > 0:
            fix_details.append(f"{fixes} template includes")
        total_fixes += fixes

        content, fixes = fix_material_icons(content, lang_code, filepath, root_lang_dir)
        if fixes > 0:
            fix_details.append(f"{fixes} material icons")
        total_fixes += fixes

        content, fixes = fix_sister_project_contamination(content, lang_code, filepath, root_lang_dir)
        if fixes > 0:
            fix_details.append(f"{fixes} sister project contaminations")
        total_fixes += fixes

    if fix_facets:
        content, fixes = fix_facet_links(content)
        if fixes > 0:
            fix_details.append(f"{fixes} facet links")
        total_fixes += fixes

    if fix_repetitions:
        content, fixes = fix_repeated_substring_loops(content)
        if fixes > 0:
            fix_details.append(f"{fixes} emoticon/token loops")
        total_fixes += fixes

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

    if fix_creative_commons_urls and not is_en:
        content, fixes = fix_creative_commons_urls(content, lang_code)
        if fixes > 0:
            fix_details.append(f"{fixes} Creative Commons URLs")
        total_fixes += fixes

    if fix_badges and not is_en:
        content, fixes = fix_store_badges(content, lang_code)
        if fixes > 0:
            fix_details.append(f"{fixes} store badges")
        total_fixes += fixes

        content, fixes = fix_food_revolution_assets(content, lang_code)
        if fixes > 0:
            fix_details.append(f"{fixes} food revolution assets")
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

    content, fixes = fix_corrupted_css_js(content)
    if fixes > 0:
        fix_details.append(f"{fixes} corrupted CSS/JS entities")
    total_fixes += fixes

    content, fixes = fix_pseudo_xml_tags(content)
    if fixes > 0:
        fix_details.append(f"{fixes} pseudo-XML tags")
    total_fixes += fixes

    if filepath.endswith('/texts/press.html') and not is_en:
        try:
            from fix_press_pages import fix_standard_press_file
            new_content = fix_standard_press_file(content, lang_code)
            if new_content != content:
                content = new_content
                fix_details.append("press page structure & includes")
                total_fixes += 1
        except Exception as e:
            if verbose:
                print(f"Error fixing press page in {filepath}: {e}", file=sys.stderr)
    
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
    parser.add_argument('--fix-facets', action='store_true', default=True,
                        help='Fix legacy facet links (default: True)')
    parser.add_argument('--no-facets', action='store_true',
                        help='Skip fixing legacy facet links')
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
                        help='Fix Play Store, App Store, and F-Droid image badges (default: True)')
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
    
    fix_facets = args.fix_facets and not args.no_facets
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
                    full_path = os.path.join(root, fname)
                    if not os.path.islink(full_path):
                        files.append(full_path)
    
    for html_file in files:
        fixes = process_file(
            html_file,
            fix_repetitions=fix_repetitions,
            fix_utm=fix_utm,
            fix_urls=fix_urls,
            fix_badges=fix_badges,
            fix_brands=fix_brands,
            fix_typography=fix_typography,
            fix_facets=fix_facets,
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
