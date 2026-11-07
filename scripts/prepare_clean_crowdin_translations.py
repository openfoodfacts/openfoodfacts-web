#!/usr/bin/env python3
"""
Prepare and sanitize translation files before uploading translations to Crowdin.

Why this script exists:
1. Uploading raw HTML files (`upload_translations: true`) that contain untranslated
   English multi-sentence paragraphs causes Crowdin's SRX segmenter for CJK/Arabic/Thai
   to attach the entire multi-sentence English paragraph to Segment 1, creating an
   exponential sentence duplication loop on every sync (2,000+ file PRs).
2. Uploading contaminated strings (sister-project `Open Beauty Facts` / `Open Pet Food Facts`
   in OFF pages, leaked OpenAI API key errors, broken `[[...]]` includes, or translated
   Material Icons ligatures) pollutes Crowdin's Translation Memory (TM).

What this script does:
- Runs `fix_translation_issues.py` to repair all deterministic issues first.
- Scans `lang/<lc>/texts/**/*.html` against `lang/en/texts/**/*.html`.
- Strips any remaining contaminated or untranslated multi-sentence English segments
  from the working tree before `crowdin upload translations` runs, so ONLY clean,
  genuinely translated strings are uploaded to Crowdin.
- Deletes 100% untranslated files from the upload working tree so Crowdin does not
  mark English fallback text as translated.

Usage:
    # Dry-run audit of translated vs untranslated/contaminated segments
    python3 scripts/prepare_clean_crowdin_translations.py --check

    # Sanitize working tree in-place prior to `crowdin upload translations`
    python3 scripts/prepare_clean_crowdin_translations.py --strip-untranslated-for-upload
"""
import argparse
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from fix_translation_issues import (
    get_lang_code,
    process_file,
    _get_rel_and_en_path,
)

CONTAMINATED_RE = re.compile(
    r'Incorrect A(?:PI|pi) key provided|'
    r'platform\.\s*openai\.\s*com/account/api-keys|'
    r'sk-[A-Za-z0-9*]{20,}|'
    r'As an AI language model',
    re.IGNORECASE,
)

SISTER_PROJECT_RE = re.compile(
    r'Open Beauty Facts|Open Pet Food Facts|Open Products Facts|'
    r'openbeautyfacts\.org|openpetfoodfacts\.org|openproductsfacts\.org',
    re.IGNORECASE,
)

OFF_ONLY_PAGES = {
    'contribute.html',
    'contribuír.html',
    'discover.html',
    'open-food-hunt.html',
    'index.html',
}

BLOCK_RE = re.compile(
    r'(<(p|li|dd|dt|h[1-6]|blockquote)\b[^>]*>)(.*?)(</\2>)',
    flags=re.DOTALL | re.IGNORECASE,
)


def _normalize_for_comparison(text):
    """Normalize URLs, badges, and whitespace so localized links don't disguise untranslated English text."""
    s = re.sub(r'\s+', ' ', text).strip()
    s = re.sub(r'utm_campaign=(search_and_links_promo|discover_buttons)_[a-zA-Z_-]+', r'utm_campaign=\1_en', s)
    s = re.sub(r'utm_term=[a-zA-Z_-]+-text(-button)?-ecoscore-page', r'utm_term=en-text\1-ecoscore-page', s)
    s = re.sub(r'([?&]|&amp;)(l|hl)=[a-zA-Z_-]+', r'\1\2=en', s)
    s = re.sub(r'deed\.[a-zA-Z_-]+', 'deed.en', s)
    s = re.sub(r'/playstore/img/[a-zA-Z0-9_-]+_get\.svg', '/playstore/img/en_get.svg', s)
    s = re.sub(r'/appstore/black/appstore_[a-zA-Z0-9_]+\.svg', '/appstore/black/appstore_US.svg', s)
    s = re.sub(r'/f-droid/get-it-on-[a-zA-Z0-9_-]+\.png', '/f-droid/get-it-on-en.png', s)
    return s


def sanitize_file_for_crowdin_upload(filepath, base_dir, write_changes=False):
    """
    Compare `filepath` against its English source file in `lang/en/texts/`.
    Returns (translated_blocks, stripped_untranslated_blocks, stripped_contaminated_blocks, is_fully_untranslated).
    """
    lang_code = get_lang_code(filepath)
    if not lang_code or lang_code in ('en', 'en_GB', 'en_AU', 'en_US'):
        return (0, 0, 0, False)

    rel, en_path = _get_rel_and_en_path(filepath, base_dir)
    if not rel or not en_path or not os.path.isfile(en_path):
        return (0, 0, 0, False)

    try:
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
        with open(en_path, 'r', encoding='utf-8', errors='ignore') as f:
            en_content = f.read()
    except Exception:
        return (0, 0, 0, False)

    # Collect normalized English blocks
    en_blocks_norm = {
        _normalize_for_comparison(m.group(3))
        for m in BLOCK_RE.finditer(en_content)
        if len(m.group(3).strip()) > 0
    }

    norm_path = filepath.replace('\\', '/')
    is_off_page = not ('/obf/' in norm_path or '/opff/' in norm_path or '/opf/' in norm_path)
    check_sister = is_off_page and os.path.basename(norm_path) in OFF_ONLY_PAGES

    translated_count = 0
    untranslated_stripped = 0
    contaminated_stripped = 0

    def process_block(m):
        nonlocal translated_count, untranslated_stripped, contaminated_stripped
        open_tag, tag_name, inner, close_tag = m.group(1), m.group(2), m.group(3), m.group(4)
        stripped_inner = inner.strip()
        if not stripped_inner or stripped_inner.startswith('[['):
            return m.group(0)

        # Check contamination
        if CONTAMINATED_RE.search(stripped_inner) or (check_sister and SISTER_PROJECT_RE.search(stripped_inner)):
            contaminated_stripped += 1
            return f'{open_tag}{close_tag}'

        norm_inner = _normalize_for_comparison(stripped_inner)
        # Strip pure HTML tags to check if there is actual text
        text_only = re.sub(r'<[^>]+>', '', norm_inner).strip()
        if not text_only:
            return m.group(0)

        if norm_inner in en_blocks_norm and len(text_only) >= 15:
            # Untranslated English block! Strip its text for Crowdin upload so Crowdin
            # does not import English text as a target translation or duplicate multi-sentence segments.
            untranslated_stripped += 1
            return f'{open_tag}{close_tag}'

        translated_count += 1
        return m.group(0)

    sanitized_content = BLOCK_RE.sub(process_block, content)
    fully_untranslated = (translated_count == 0)

    if write_changes:
        if fully_untranslated:
            # Remove completely untranslated file from upload working tree so Crowdin skips it
            try:
                os.remove(filepath)
            except OSError:
                pass
        elif sanitized_content != content:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(sanitized_content)

    return (translated_count, untranslated_stripped, contaminated_stripped, fully_untranslated)


def main():
    parser = argparse.ArgumentParser(
        description='Sanitize and filter translation files before uploading to Crowdin.'
    )
    parser.add_argument('--base-dir', default='lang', help='Base lang directory (default: lang)')
    parser.add_argument('--check', action='store_true', help='Dry-run audit without modifying files for upload')
    parser.add_argument(
        '--strip-untranslated-for-upload',
        action='store_true',
        help='Run autofixes and strip untranslated/contaminated blocks in-place for Crowdin upload',
    )
    args = parser.parse_args()

    base_dir = os.path.abspath(args.base_dir)
    html_files = []
    for root, _, files in os.walk(base_dir):
        for fname in files:
            if fname.endswith('.html'):
                full = os.path.join(root, fname)
                if not os.path.islink(full):
                    html_files.append(full)

    if args.strip_untranslated_for_upload:
        print('Step 1/2: Running fix_translation_issues.py across all HTML files...')
        fixed_files = 0
        for fpath in html_files:
            if process_file(fpath) > 0:
                fixed_files += 1
        print(f'  -> Autofixed {fixed_files} files.')

    print('Step 2/2: Auditing translated vs untranslated/contaminated segments...')
    total_translated_blocks = 0
    total_untranslated_stripped = 0
    total_contaminated_stripped = 0
    fully_untranslated_files = 0

    for fpath in html_files:
        t_cnt, u_cnt, c_cnt, full_untrans = sanitize_file_for_crowdin_upload(
            fpath, base_dir, write_changes=args.strip_untranslated_for_upload
        )
        total_translated_blocks += t_cnt
        total_untranslated_stripped += u_cnt
        total_contaminated_stripped += c_cnt
        if full_untrans:
            fully_untranslated_files += 1

    print('=' * 60)
    print(f'Clean translated blocks ready for Crowdin : {total_translated_blocks}')
    print(f'Untranslated English blocks excluded      : {total_untranslated_stripped}')
    print(f'Contaminated blocks excluded              : {total_contaminated_stripped}')
    print(f'100% untranslated files skipped           : {fully_untranslated_files}')
    print('=' * 60)
    return 0


if __name__ == '__main__':
    sys.exit(main())
