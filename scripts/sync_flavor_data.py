#!/usr/bin/env python3
"""
Sync shared sections from Open Food Facts data.html to flavor-specific versions:
- Open Beauty Facts (lang/obf/en/texts/data.html)
- Open Pet Food Facts (lang/opff/en/texts/data.html)
- Open Products Facts (lang/opf/en/texts/data.html)

Synchronizes:
1. Conditions for reuse (including simplified ODbL summary & technical compliance guide)
2. SDK table, filter UI, and JavaScript filter/sorting logic
3. Discussing data & API section

Usage:
    python3 scripts/sync_flavor_data.py [--check] [--verbose]
"""

import os
import re
import sys
import argparse

FLAVORS = {
    'obf': {
        'name': 'Open Beauty Facts',
        'domain': 'openbeautyfacts.org',
        'file': 'lang/obf/en/texts/data.html',
    },
    'opff': {
        'name': 'Open Pet Food Facts',
        'domain': 'openpetfoodfacts.org',
        'file': 'lang/opff/en/texts/data.html',
    },
    'opf': {
        'name': 'Open Products Facts',
        'domain': 'openproductsfacts.org',
        'file': 'lang/opf/en/texts/data.html',
    },
}

def extract_conditions_section(content):
    """Extract the Conditions for reuse section up to 'Tell us about your reuse'."""
    m = re.search(r'(<h2 class="emphasized-title">Conditions for reuse</h2>.*?)(?=\s*<h2 class="emphasized-title">Tell us about your reuse</h2>)', content, re.DOTALL)
    if not m:
        raise ValueError("Could not find 'Conditions for reuse' section in data.html")
    return m.group(1).strip()

def extract_sdk_section(content):
    """Extract the complete SDK section from <h3>SDKs</h3> up to Discussing data."""
    m = re.search(r'(<h3>SDKs</h3>.*?)(?=\s*<h2 class="emphasized-title">Discussing data)', content, re.DOTALL)
    if not m:
        raise ValueError("Could not find SDK section in data.html")
    return m.group(1).strip()

def adapt_conditions_for_flavor(conditions_html, flavor_key):
    info = FLAVORS[flavor_key]
    flavor_name = info['name']
    flavor_domain = info['domain']

    res = conditions_html
    res = re.sub(r'The Open Food Facts database is available under', f'The {flavor_name} database is available under', res)
    res = re.sub(r'https://world\.openfoodfacts\.org/terms-of-use', f'https://world.{flavor_domain}/terms-of-use', res)
    res = re.sub(r'Contains data from Open Food Facts', f'Contains data from {flavor_name}', res)
    res = re.sub(r'send those contributions back to Open Food Facts', f'send those contributions back to {flavor_name}', res)
    res = re.sub(r'Clearly attribute Open Food Facts', f'Clearly attribute {flavor_name}', res)
    res = re.sub(r'links back to Open Food Facts and the ODbL', f'links back to {flavor_name} and the ODbL', res)

    return res

def sync_flavor_file(base_dir, flavor_key, off_conditions, off_sdk_block, check_only=False, verbose=False):
    info = FLAVORS[flavor_key]
    file_path = os.path.join(base_dir, info['file'])

    if not os.path.exists(file_path):
        print(f"Error: {file_path} not found", file=sys.stderr)
        return False

    with open(file_path, 'r', encoding='utf-8') as f:
        original = f.read()

    updated = original

    # 1. Update Conditions for reuse
    flavor_conditions = adapt_conditions_for_flavor(off_conditions, flavor_key)
    cond_pattern = re.compile(r'<h2 class="emphasized-title">Conditions for reuse</h2>.*?(?=\s*<h2 class="emphasized-title">Tell us about your reuse</h2>)', re.DOTALL)
    if cond_pattern.search(updated):
        updated = cond_pattern.sub(flavor_conditions + '\n\n\n', updated)
    else:
        print(f"Warning: Could not match Conditions for reuse in {file_path}", file=sys.stderr)

    # 2. Update SDK section
    sdk_pattern = re.compile(r'<h3>SDKs</h3>.*?(?=\s*<h2 class="emphasized-title">Discussing data)', re.DOTALL)
    if sdk_pattern.search(updated):
        updated = sdk_pattern.sub(off_sdk_block + '\n\n', updated)
    else:
        print(f"Warning: Could not match SDK section in {file_path}", file=sys.stderr)

    # Clean up any potential triple/quadruple blank lines
    updated = re.sub(r'\n{4,}', '\n\n\n', updated)

    changed = (updated != original)

    if changed:
        if check_only:
            if verbose:
                print(f"[OUT OF SYNC] {info['file']}")
            return False
        else:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(updated)
            if verbose:
                print(f"[UPDATED] {info['file']}")
            return True
    else:
        if verbose:
            print(f"[IN SYNC] {info['file']}")
        return True

def main():
    parser = argparse.ArgumentParser(description="Sync shared content from OFF data.html to flavor-specific versions.")
    parser.add_argument('--base-dir', default='.', help="Repository root directory")
    parser.add_argument('--check', action='store_true', help="Check whether flavor files are in sync without writing")
    parser.add_argument('--verbose', '-v', action='store_true', help="Verbose output")
    args = parser.parse_args()

    off_data_path = os.path.join(args.base_dir, 'lang/en/texts/data.html')
    if not os.path.exists(off_data_path):
        print(f"Error: {off_data_path} does not exist", file=sys.stderr)
        sys.exit(1)

    with open(off_data_path, 'r', encoding='utf-8') as f:
        off_content = f.read()

    off_conditions = extract_conditions_section(off_content)
    off_sdk_block = extract_sdk_section(off_content)

    all_in_sync = True
    for flavor_key in FLAVORS:
        ok = sync_flavor_file(args.base_dir, flavor_key, off_conditions, off_sdk_block, check_only=args.check, verbose=args.verbose)
        if not ok:
            all_in_sync = False

    if args.check and not all_in_sync:
        sys.exit(1)

if __name__ == '__main__':
    main()
