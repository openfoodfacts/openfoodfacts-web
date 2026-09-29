#!/usr/bin/env python3
"""
Add questions to the Open Food Facts FAQ from GitHub issues, PR templates, or CLI.

This script parses GitHub issue bodies submitted via `.github/ISSUE_TEMPLATE/new-faq-question.yml`
or markdown templates, formats the question and answer into standard Markdown with frontmatter,
appends it to the correct category file in `data/faq/<lang>/<category>.md`, validates the result,
and optionally recompiles the FAQ dataset.

Usage:
    # From GitHub issue markdown file or stdin:
    python3 scripts/add_faq_question.py --from-issue-file issue.md --compile
    python3 scripts/add_faq_question.py --from-env --compile

    # Directly via CLI flags:
    python3 scripts/add_faq_question.py \
        --lang en \
        --category nutri-score \
        --question "How does Nutri-Score score beverages?" \
        --answer "Beverages are evaluated using a specialized algorithm..." \
        --compile
"""

import argparse
import glob
import json
import os
import re
import sys
import yaml

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
DATA_DIR = os.path.join(REPO_ROOT, "data")
FAQ_DIR = os.path.join(DATA_DIR, "faq")

# Import compilation logic
try:
    from compile_faq import compile_faq, load_faq_for_lang, slugify, SUPPORTED_LANGS
except ImportError:
    sys.path.insert(0, os.path.dirname(__file__))
    from compile_faq import compile_faq, load_faq_for_lang, slugify, SUPPORTED_LANGS


def parse_issue_markdown(text):
    """
    Parses GitHub Issue Form / Markdown template body.
    Extracts language, category, question, answer, and sources.
    """
    data = {
        "lang": "en",
        "category": "",
        "question": "",
        "answer": "",
        "sources": ""
    }

    if not text:
        return data

    text = text.replace("\r\n", "\n")

    # Pattern for H3 sections: ### Section Title\n\nContent
    sections = re.split(r"(?m)^###\s+", "\n" + text)
    for sec in sections:
        sec = sec.strip()
        if not sec:
            continue
        lines = sec.splitlines()
        header = lines[0].strip().lower()
        content = "\n".join(lines[1:]).strip()

        # Remove HTML comments if any
        content = re.sub(r"<!--.*?-->", "", content, flags=re.DOTALL).strip()

        if "language" in header:
            lang_match = re.search(r"\b(en|fr|es|de|it)\b", content, re.IGNORECASE)
            if lang_match:
                data["lang"] = lang_match.group(1).lower()
        elif "category" in header:
            # Extract category name, removing parenthetical labels
            cleaned = content.splitlines()[0].strip()
            # E.g. "8-nutri-score (Nutri-Score)" -> "8-nutri-score" or "nutri-score"
            cleaned = re.sub(r"\(.*?\)", "", cleaned).strip()
            data["category"] = cleaned
        elif "question" in header:
            # Remove any leading markdown marks
            q_lines = [l for l in content.splitlines() if l.strip() and not l.startswith("<!--")]
            if q_lines:
                data["question"] = q_lines[0].strip().lstrip("#").strip()
        elif "answer" in header:
            data["answer"] = content.strip()
        elif "source" in header or "reference" in header:
            data["sources"] = content.strip()

    return data


def find_category_file(lang, category_hint):
    """
    Finds the matching category file in data/faq/<lang>/.
    Returns (filepath, relative_path, frontmatter_dict) or (None, None, None).
    """
    lang_dir = os.path.join(FAQ_DIR, lang)
    if not os.path.isdir(lang_dir):
        return None, None, None

    md_files = sorted(glob.glob(f"{lang_dir}/**/*.md", recursive=True))

    hint_slug = slugify(category_hint)
    hint_clean = re.sub(r"^\d+-", "", hint_slug)
    num_match = re.match(r"^(\d+)", hint_slug)
    hint_num = int(num_match.group(1)) if num_match else None

    # 1. Exact match on filename without extension or number
    for fpath in md_files:
        if os.path.basename(fpath) == "index.md":
            continue
        basename = os.path.basename(fpath)
        base_no_ext = os.path.splitext(basename)[0]
        base_clean = re.sub(r"^\d+-", "", base_no_ext)

        if hint_slug in (slugify(base_no_ext), slugify(base_clean)) or hint_clean in (slugify(base_clean), slugify(base_no_ext)):
            with open(fpath, "r", encoding="utf-8") as f:
                content = f.read()
            fm = {}
            if content.startswith("---"):
                parts = content.split("---", 2)
                if len(parts) >= 3:
                    try:
                        fm = yaml.safe_load(parts[1]) or {}
                    except Exception:
                        pass
            return fpath, os.path.relpath(fpath, lang_dir), fm

    # 2. Match on frontmatter id, title, or order
    for fpath in md_files:
        if os.path.basename(fpath) == "index.md":
            continue
        try:
            with open(fpath, "r", encoding="utf-8") as f:
                content = f.read()
        except Exception:
            continue

        if not content.startswith("---"):
            continue
        parts = content.split("---", 2)
        if len(parts) < 3:
            continue
        try:
            fm = yaml.safe_load(parts[1]) or {}
        except Exception:
            continue

        fm_id = slugify(fm.get("id", ""))
        fm_title = slugify(fm.get("title", ""))
        fm_order = fm.get("order")

        if hint_clean and (hint_clean == fm_id or hint_clean in fm_id or hint_clean in fm_title):
            return fpath, os.path.relpath(fpath, lang_dir), fm

        if hint_num is not None and fm_order == hint_num:
            return fpath, os.path.relpath(fpath, lang_dir), fm

    return None, None, None


def append_question_to_file(filepath, question, answer, sources=None):
    """
    Appends the question and answer to the Markdown category file.
    Ensures clean separator and formatting.
    """
    with open(filepath, "r", encoding="utf-8") as f:
        existing = f.read()

    existing_stripped = existing.rstrip()

    new_block = []
    # If the file does not end with a divider '---', add one
    if not existing_stripped.endswith("---"):
        new_block.append("\n---")

    new_block.append(f"\n## {question}\n")
    new_block.append(answer.strip())

    if sources and sources.strip():
        new_block.append("\n\n*Sources:* " + sources.strip())

    new_block.append("\n---\n")

    updated_content = existing_stripped + "\n" + "\n".join(new_block)

    with open(filepath, "w", encoding="utf-8") as f:
        f.write(updated_content)

    return True


def create_new_category_file(lang, category_name, question, answer, sources=None):
    """
    Creates a new category file in data/faq/<lang>/ if it doesn't already exist.
    """
    lang_dir = os.path.join(FAQ_DIR, lang)
    os.makedirs(lang_dir, exist_ok=True)

    cat_slug = slugify(category_name) or "general"
    filename = f"99-{cat_slug}.md"
    filepath = os.path.join(lang_dir, filename)

    frontmatter = {
        "id": cat_slug,
        "title": category_name.title(),
        "icon": "❓",
        "order": 99,
        "lang": lang
    }

    content_parts = [
        "---",
        yaml.safe_dump(frontmatter, sort_keys=False).strip(),
        "---\n",
        f"## {question}\n",
        answer.strip()
    ]

    if sources and sources.strip():
        content_parts.append("\n\n*Sources:* " + sources.strip())

    content_parts.append("\n---\n")

    with open(filepath, "w", encoding="utf-8") as f:
        f.write("\n".join(content_parts))

    return filepath, os.path.relpath(filepath, lang_dir)


def add_faq_question(lang, category, question, answer, sources=None, dry_run=False, do_compile=False):
    """
    Main function to validate and add a new question to the FAQ.
    """
    if lang not in SUPPORTED_LANGS:
        return {
            "success": False,
            "error": f"Unsupported language '{lang}'. Must be one of {SUPPORTED_LANGS}"
        }

    question = question.strip().lstrip("#").strip()
    if not question:
        return {"success": False, "error": "Question title cannot be empty."}

    answer = answer.strip()
    if not answer:
        return {"success": False, "error": "Answer cannot be empty."}

    # Locate category file
    fpath, rel_path, fm = find_category_file(lang, category)
    is_new_category = False

    if not fpath:
        is_new_category = True
        target_name = category or "General"
        if dry_run:
            print(f"[Dry Run] Would create new category file for '{target_name}' in lang/{lang}")
            return {"success": True, "question": question, "lang": lang, "dry_run": True}
        fpath, rel_path = create_new_category_file(lang, target_name, question, answer, sources)
    else:
        if dry_run:
            print(f"[Dry Run] Would append to existing file {fpath}")
            return {"success": True, "question": question, "lang": lang, "dry_run": True}
        append_question_to_file(fpath, question, answer, sources)

    # Validate with compile_faq
    categories, errors, warnings = load_faq_for_lang(lang)
    if errors:
        return {
            "success": False,
            "error": f"Validation failed after adding question: {'; '.join(errors)}",
            "file": fpath
        }

    q_slug = slugify(question)

    # Optionally recompile
    if do_compile:
        compile_success = compile_faq(check_only=False, verbose=False)
        if not compile_success:
            return {
                "success": False,
                "error": "Failed to recompile FAQ after adding question.",
                "file": fpath
            }

    return {
        "success": True,
        "lang": lang,
        "question": question,
        "id": q_slug,
        "file": rel_path,
        "full_path": fpath,
        "is_new_category": is_new_category
    }


def main():
    parser = argparse.ArgumentParser(description="Add questions to the Open Food Facts FAQ.")
    parser.add_argument("--lang", choices=SUPPORTED_LANGS, default="en", help="Language code")
    parser.add_argument("--category", help="Category name or ID (e.g. nutri-score, mobile-app)")
    parser.add_argument("--question", help="Question title")
    parser.add_argument("--answer", help="Answer in Markdown")
    parser.add_argument("--sources", help="Optional sources / references")
    parser.add_argument("--from-issue-file", help="Path to markdown issue file")
    parser.add_argument("--from-issue-text", help="Raw issue text")
    parser.add_argument("--from-env", action="store_true", help="Read ISSUE_BODY and ISSUE_NUMBER from environment")
    parser.add_argument("--issue-number", help="GitHub issue number reference")
    parser.add_argument("--compile", action="store_true", help="Recompile data/faq.json and lang/*/texts/faq.html")
    parser.add_argument("--dry-run", action="store_true", help="Validate without writing changes")
    parser.add_argument("--json", action="store_true", help="Output result as JSON")

    args = parser.parse_args()

    # Determine input source
    lang = args.lang
    category = args.category
    question = args.question
    answer = args.answer
    sources = args.sources

    raw_text = None
    if args.from_env:
        raw_text = os.environ.get("ISSUE_BODY", "")
    elif args.from_issue_file:
        with open(args.from_issue_file, "r", encoding="utf-8") as f:
            raw_text = f.read()
    elif args.from_issue_text:
        raw_text = args.from_issue_text
    elif not sys.stdin.isatty() and not (question and answer):
        raw_text = sys.stdin.read()

    if raw_text:
        parsed = parse_issue_markdown(raw_text)
        lang = parsed.get("lang") or lang
        category = parsed.get("category") or category
        question = parsed.get("question") or question
        answer = parsed.get("answer") or answer
        sources = parsed.get("sources") or sources

    if not question or not answer:
        print("Error: Both --question and --answer must be provided or parsed from issue body.", file=sys.stderr)
        sys.exit(1)

    result = add_faq_question(
        lang=lang,
        category=category,
        question=question,
        answer=answer,
        sources=sources,
        dry_run=args.dry_run,
        do_compile=args.compile
    )

    if args.json:
        print(json.dumps(result, indent=2))
    else:
        if result.get("success"):
            print(f"✅ Successfully added FAQ question to {result.get('file')}")
            print(f"   ID: {result.get('id')}")
            print(f"   Question: {result.get('question')}")
            print(f"   Language: {result.get('lang')}")
        else:
            print(f"❌ Error adding FAQ question: {result.get('error')}", file=sys.stderr)
            sys.exit(1)


if __name__ == "__main__":
    main()
