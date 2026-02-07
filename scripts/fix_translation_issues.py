#!/usr/bin/env python3
"""
Script to automatically fix common translation issues in lang files.
Can be used as part of a GitHub Action to repair Crowdin translations.

This script fixes:
1. UTM campaign parameters to use correct language code based on folder path
2. UTM term parameters with incorrect language prefixes
3. Common text repetition patterns (both known patterns and dynamic detection)

Usage:
    python fix_translation_issues.py [--base-dir DIR] [--fix-repetitions] [--fix-utm] [--verbose]

Examples:
    # Fix all issues in lang directory
    python fix_translation_issues.py --base-dir lang
    
    # Fix only UTM parameters
    python fix_translation_issues.py --fix-utm --no-repetitions
    
    # Verbose output
    python fix_translation_issues.py -v
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


def get_lang_code(filepath):
    """Extract language code from folder path like /lang/aa/ -> aa"""
    parts = filepath.split(os.sep)
    for i, part in enumerate(parts):
        if part == 'lang' and i + 1 < len(parts):
            return parts[i + 1]
    return None


def fix_utm_campaigns(content, lang_code):
    """
    Fix UTM campaign parameters to use correct language code.
    
    Args:
        content: File content
        lang_code: Language code from folder path
    
    Returns:
        (fixed_content, number_of_fixes)
    """
    fixes = 0
    
    patterns = [
        # UTM campaign patterns
        (r'utm_campaign=search_and_links_promo_[a-zA-Z_]+', f'utm_campaign=search_and_links_promo_{lang_code}'),
        (r'utm_campaign=discover_buttons_[a-zA-Z_]+', f'utm_campaign=discover_buttons_{lang_code}'),
        # UTM term patterns
        (r'utm_term=[a-zA-Z_]+-text-ecoscore-page', f'utm_term={lang_code}-text-ecoscore-page'),
        (r'utm_term=[a-zA-Z_]+-text-button-ecoscore-page', f'utm_term={lang_code}-text-button-ecoscore-page'),
    ]
    
    for pattern, replacement in patterns:
        matches = len(re.findall(pattern, content))
        if matches:
            content = re.sub(pattern, replacement, content)
            fixes += matches
    
    return content, fixes


def fix_known_repetitions(content):
    """
    Fix known text repetition patterns.
    
    Args:
        content: File content
    
    Returns:
        (fixed_content, number_of_fixes)
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
    Dynamically detect and fix text repetitions similar to the Perl script.
    Looks for substantial text (20+ chars) that appears consecutively.
    
    Args:
        content: File content
        filepath: Path to file (for skip logic)
    
    Returns:
        (fixed_content, number_of_fixes)
    """
    fixes = 0
    
    # Skip certain files known to have false positives (CSS-heavy files)
    skip_files = ['landing-off.html', 'presse.html', 'revue-de-presse-fr.html']
    for skip_file in skip_files:
        if skip_file in filepath:
            return content, 0
    
    # Pattern to find consecutive duplicate text (min 20 chars)
    # Match text that doesn't contain < or > (to avoid HTML tags)
    min_len = 20
    
    # Use a loop to find and fix repetitions
    max_iterations = 50  # Increased to handle severe repetitions
    for _ in range(max_iterations):
        # Find pattern: text followed by whitespace (including newlines) followed by same text
        match = re.search(r'([^\n<>]{' + str(min_len) + r',}?)\s+\1', content, re.MULTILINE)
        if not match:
            break
        
        matched_text = match.group(1).strip()
        
        # Skip if it's a CSS pattern
        if is_css_pattern(matched_text):
            # Can't skip easily in regex, so just break
            break
        
        # Skip pure structural/technical patterns
        if re.match(r'^[\s\n\r\t<>\/]+$', matched_text):
            break
        if re.match(r'^[a-z0-9_-]+$', matched_text, re.IGNORECASE):
            break
        if re.match(r'^["\'\(\)\[\]{}]+$', matched_text):
            break
        
        # Fix the repetition - replace "text text" with "text"
        full_match = match.group(0)
        content = content.replace(full_match, matched_text, 1)
        fixes += 1
    
    return content, fixes


def process_file(filepath, fix_repetitions=True, fix_utm=True, verbose=False):
    """
    Process a single HTML file to fix translation issues.
    
    Args:
        filepath: Path to HTML file
        fix_repetitions: Whether to fix text repetitions
        fix_utm: Whether to fix UTM parameters
        verbose: Whether to print detailed output
    
    Returns:
        Number of fixes made
    """
    lang_code = get_lang_code(filepath)
    if not lang_code or lang_code == 'README.md':
        return 0
    
    # Skip English folder for UTM changes (English is the source)
    skip_utm = lang_code == 'en'
    
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
        
        # Also try dynamic repetition detection
        content, fixes = fix_dynamic_repetitions(content, filepath)
        if fixes > 0:
            fix_details.append(f"{fixes} dynamic repetitions")
        total_fixes += fixes
    
    if fix_utm and not skip_utm:
        content, fixes = fix_utm_campaigns(content, lang_code)
        if fixes > 0:
            fix_details.append(f"{fixes} UTM params")
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
        epilog="""
Examples:
    # Fix all issues
    %(prog)s --base-dir lang
    
    # Fix only UTM parameters  
    %(prog)s --fix-utm --no-repetitions
    
    # Verbose output
    %(prog)s -v
"""
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
    parser.add_argument('--verbose', '-v', action='store_true',
                        help='Verbose output')
    parser.add_argument('files', nargs='*',
                        help='Specific files to process (optional)')
    args = parser.parse_args()
    
    # Handle negation flags
    fix_repetitions = args.fix_repetitions and not args.no_repetitions
    fix_utm = args.fix_utm and not args.no_utm
    
    base_dir = args.base_dir
    if not os.path.isabs(base_dir):
        base_dir = os.path.join(os.getcwd(), base_dir)
    
    total_fixes = 0
    total_files = 0
    
    # If specific files provided, process only those
    if args.files:
        files = args.files
    else:
        files = []
        for lang_dir in os.listdir(base_dir):
            lang_path = os.path.join(base_dir, lang_dir)
            if not os.path.isdir(lang_path):
                continue
            
            files.extend(glob.glob(os.path.join(lang_path, '**/*.html'), recursive=True))
    
    for html_file in files:
        fixes = process_file(html_file, fix_repetitions, fix_utm, args.verbose)
        if fixes > 0:
            total_files += 1
            total_fixes += fixes
    
    print(f"\n{'='*60}")
    print(f"📊 Summary: {total_fixes} fixes across {total_files} files")
    print(f"{'='*60}")
    
    # Always return success - this script is a repair tool
    return 0


if __name__ == '__main__':
    sys.exit(main())
