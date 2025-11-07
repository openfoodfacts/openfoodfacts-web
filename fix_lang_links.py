#!/usr/bin/env python3
"""
Script to fix language codes in HTML files across all language folders.

This script:
1. Fixes Google Play Store links: changes &hl=en to &hl=<langcode>
2. Fixes domain links: changes world-en. to world-<langcode>. for various domains
"""

import os
import re
from pathlib import Path

# Mapping for special language codes (with underscores) to their base codes
# Some languages with regional variants may need special handling
LANG_CODE_MAP = {
    'en_AU': 'en',
    'en_GB': 'en',
    'kmr_TR': 'kmr',
    'nl_BE': 'nl',
    'nl_NL': 'nl',
    'pt_BR': 'pt',
    'pt_PT': 'pt',
    'sr_CS': 'sr',
    'sr_RS': 'sr',
    'zh_CN': 'zh',
    'zh_HK': 'zh',
    'zh_TW': 'zh',
}

def get_lang_code_for_links(folder_name):
    """
    Get the language code to use in links for a given folder name.
    For folders with underscores, use the mapped base code.
    """
    return LANG_CODE_MAP.get(folder_name, folder_name)

def fix_google_play_links(content, lang_code):
    """
    Fix Google Play Store links by replacing &hl=en with &hl=<lang_code>
    Also handles cases like &hl=fr or other existing language codes.
    """
    # Pattern to match &hl=XX where XX is any language code (2-3 letters)
    pattern = r'(&hl=)[a-z]{2,3}([&"\'])'
    replacement = rf'\1{lang_code}\2'
    return re.sub(pattern, replacement, content)

def fix_domain_links(content, lang_code):
    """
    Fix domain links by replacing world-XX. with world-<lang_code>.
    for openfoodfacts, openpetfoodfacts, openbeautyfacts, and openproductsfacts domains.
    """
    # List of domains to fix
    domains = [
        'openfoodfacts.org',
        'openpetfoodfacts.org',
        'openbeautyfacts.org',
        'openproductsfacts.org'
    ]
    
    for domain in domains:
        # Pattern to match world-XX.domain where XX is any language code
        pattern = rf'(world-)[a-z_]{{2,7}}(\.{re.escape(domain)})'
        replacement = rf'\1{lang_code}\2'
        content = re.sub(pattern, replacement, content)
    
    return content

def fix_html_file(file_path, lang_code):
    """
    Fix all language-specific links in a single HTML file.
    Returns True if changes were made, False otherwise.
    """
    # Skip symlinks - they point to the actual file which will be processed
    if file_path.is_symlink():
        return False
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            original_content = f.read()
        
        # Apply fixes
        content = fix_google_play_links(original_content, lang_code)
        content = fix_domain_links(content, lang_code)
        
        # Only write if changes were made
        if content != original_content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            return True
        return False
    except Exception as e:
        print(f"Error processing {file_path}: {e}")
        return False

def main():
    """Main function to process all HTML files in language folders."""
    lang_dir = Path(__file__).parent / 'lang'
    
    if not lang_dir.exists():
        print(f"Error: {lang_dir} does not exist")
        return
    
    total_files = 0
    modified_files = 0
    
    # Process each language folder
    for lang_folder in sorted(lang_dir.iterdir()):
        if not lang_folder.is_dir():
            continue
        
        folder_name = lang_folder.name
        lang_code = get_lang_code_for_links(folder_name)
        
        print(f"Processing {folder_name} (using lang code: {lang_code})...")
        
        # Find all HTML files in this language folder
        html_files = list(lang_folder.rglob('*.html'))
        
        for html_file in html_files:
            total_files += 1
            if fix_html_file(html_file, lang_code):
                modified_files += 1
    
    print(f"\nComplete!")
    print(f"Total files processed: {total_files}")
    print(f"Files modified: {modified_files}")

if __name__ == '__main__':
    main()
