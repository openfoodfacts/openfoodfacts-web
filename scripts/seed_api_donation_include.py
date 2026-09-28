#!/usr/bin/env python3
"""
Script to distribute `api-donation-include.html` across all language directories
and insert `[[texts/api-donation-include.html]]` into all `data.html` pages
directly in the API section.
"""

import os
import re
import sys
import glob

INCLUDE_NAME = 'api-donation-include.html'
INCLUDE_TAG = f'[[texts/{INCLUDE_NAME}]]'

def main():
    root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    lang_root = os.path.join(root_dir, 'lang')
    en_include_path = os.path.join(lang_root, 'en', 'texts', INCLUDE_NAME)

    if not os.path.isfile(en_include_path):
        print(f"Error: English template not found at {en_include_path}", file=sys.stderr)
        sys.exit(1)

    with open(en_include_path, 'r', encoding='utf-8') as f:
        en_content = f.read()

    # Step 1: Collect all text directories
    texts_dirs = []
    for item in os.listdir(lang_root):
        item_path = os.path.join(lang_root, item)
        if not os.path.isdir(item_path):
            continue

        # Standard lang directories (e.g. lang/fr/texts)
        texts_dir = os.path.join(item_path, 'texts')
        if os.path.isdir(texts_dir):
            texts_dirs.append(texts_dir)

        # Flavor directories (e.g. lang/off/fr/texts, lang/obf/en/texts)
        if item in ('off', 'obf', 'opf', 'opff'):
            for sub in os.listdir(item_path):
                sub_texts = os.path.join(item_path, sub, 'texts')
                if os.path.isdir(sub_texts):
                    texts_dirs.append(sub_texts)

    fr_include_path = os.path.join(lang_root, 'fr', 'texts', INCLUDE_NAME)
    with open(fr_include_path, 'r', encoding='utf-8') as f:
        fr_content = f.read()

    # Step 2: Seed/sync api-donation-include.html to all texts directories
    synced = 0
    for td in texts_dirs:
        dest_include = os.path.join(td, INCLUDE_NAME)
        # Use French content for French directories, English for all others
        content_to_write = fr_content if ('/fr/' in td.replace('\\', '/') or td.endswith('/fr/texts')) else en_content
        with open(dest_include, 'w', encoding='utf-8') as f:
            f.write(content_to_write)
        synced += 1

    print(f"Synced {INCLUDE_NAME} to {synced} directories.")

    # Step 3: Update all data.html files
    data_files = glob.glob(os.path.join(lang_root, '**/texts/data.html'), recursive=True)

    api_btn_pattern = re.compile(
        r'(<a\s+href=["\']https://openfoodfacts\.github\.io/openfoodfacts-server/api/["\'][^>]*>.*?</a>)',
        re.DOTALL | re.IGNORECASE
    )

    # Next section pattern after API section (e.g. <h2>Android..., <h2>Wrappers..., <h2>SDK...)
    next_h2_pattern = re.compile(
        r'(<h2[^>]*>.*?(?:Android|Wrappers|SDK|Discussing|Contact).*?</h2>)',
        re.DOTALL | re.IGNORECASE
    )

    updated = 0
    already_had = 0
    fallback_updated = 0
    failed = 0

    for df in data_files:
        with open(df, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()

        if INCLUDE_TAG in content:
            already_had += 1
            continue

        # Try button match first
        match = api_btn_pattern.search(content)
        if match:
            new_content = (
                content[:match.end()] +
                f"\n\n{INCLUDE_TAG}\n" +
                content[match.end():]
            )
            with open(df, 'w', encoding='utf-8') as f:
                f.write(new_content)
            updated += 1
            continue

        # Try placing right before the next section after API
        api_h2 = re.search(r'<h2[^>]*>.*?(?:API|api).*?</h2>', content, re.IGNORECASE)
        if api_h2:
            next_h2 = next_h2_pattern.search(content, api_h2.end())
            if next_h2:
                new_content = (
                    content[:next_h2.start()] +
                    f"{INCLUDE_TAG}\n\n" +
                    content[next_h2.start():]
                )
                with open(df, 'w', encoding='utf-8') as f:
                    f.write(new_content)
                fallback_updated += 1
                continue
            else:
                # If no next h2, insert after api_h2 paragraph
                p_match = re.search(r'</p>', content[api_h2.end():])
                if p_match:
                    insert_pos = api_h2.end() + p_match.end()
                    new_content = (
                        content[:insert_pos] +
                        f"\n\n{INCLUDE_TAG}\n" +
                        content[insert_pos:]
                    )
                    with open(df, 'w', encoding='utf-8') as f:
                        f.write(new_content)
                    fallback_updated += 1
                    continue

        failed += 1

    print(f"data.html: {already_had} already had tag, {updated} updated via button, {fallback_updated} updated via fallback, {failed} unhandled.")

if __name__ == '__main__':
    main()
