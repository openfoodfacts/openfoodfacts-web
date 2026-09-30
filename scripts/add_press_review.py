#!/usr/bin/env python3
"""
Add press review items to Open Food Facts from GitHub issues, PR templates, or CLI.

This script parses GitHub issue bodies submitted via `.github/ISSUE_TEMPLATE/new-press-review.yml`
or markdown templates, formats the entry into standard YAML adhering to the press review schema,
saves it to `data/press-review/<id>.yaml`, validates the result, and optionally recompiles
the press review dataset.

Usage:
    # From GitHub issue markdown file or stdin:
    python3 scripts/add_press_review.py --from-issue-file issue.md --compile
    python3 scripts/add_press_review.py --from-env --compile

    # Directly via CLI flags:
    python3 scripts/add_press_review.py \\
        --title "Open Food Facts: The Wikipedia of Food" \\
        --source "Le Monde" \\
        --date "2026-09-30" \\
        --link "https://www.lemonde.fr/..." \\
        --type article \\
        --media-scope national \\
        --lang fr \\
        --country fra \\
        --compile
"""

import argparse
import contextlib
import json
import os
import re
import sys
import unicodedata
import urllib.parse
import yaml

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
DATA_DIR = os.path.join(REPO_ROOT, "data")
PRESS_DIR = os.path.join(DATA_DIR, "press-review")

# Import validation and compilation logic
try:
    from compile_press_review import (
        compile_press_review,
        validate_press_item,
        VALID_TYPES,
        VALID_SCOPES,
    )
except ImportError:
    sys.path.insert(0, os.path.dirname(__file__))
    from compile_press_review import (
        compile_press_review,
        validate_press_item,
        VALID_TYPES,
        VALID_SCOPES,
    )

PRESS_KEY_ORDER = [
    "id",
    "date",
    "source",
    "title",
    "link",
    "domain",
    "type",
    "media_scope",
    "raw_type",
    "lang",
    "country",
    "author",
    "topic",
    "topics",
    "verbatim",
    "editorial_note",
    "dead_link",
    "selected",
    "origin",
]

KNOWN_TOPICS = {
    "nutriscore",
    "nova",
    "upf",
    "green-score",
    "open-data",
    "data-journalism",
    "additives",
    "seasonal",
}


def slugify(text, max_len=40):
    """Normalize text into URL/ID friendly slug."""
    text = unicodedata.normalize("NFKD", str(text)).encode("ascii", "ignore").decode("ascii")
    text = re.sub(r"[^\w\s-]", "", text.lower()).strip()
    slug = re.sub(r"[-\s]+", "-", text)
    return slug[:max_len].rstrip("-")


def extract_domain(url):
    """Extract clean domain name without www or port."""
    if not url:
        return ""
    try:
        parsed = urllib.parse.urlparse(str(url).strip())
        domain = parsed.netloc.lower()
        if not domain and not parsed.scheme:
            # Maybe url entered without protocol
            parsed = urllib.parse.urlparse("https://" + str(url).strip())
            domain = parsed.netloc.lower()
        if domain.startswith("www."):
            domain = domain[4:]
        domain = domain.split(":")[0]
        return domain
    except Exception:
        return ""


def clean_acronym_off(text):
    """Replace standalone acronym 'OFF' with 'Open Food Facts'."""
    if not text:
        return text
    return re.sub(r"\bOFF\b", "Open Food Facts", str(text))


def clean_field_value(val):
    """Clean GitHub Issue field value removing markdown comments and '_No response_' placeholders."""
    if not val:
        return ""
    val = re.sub(r"<!--.*?-->", "", str(val), flags=re.DOTALL).strip()
    if val.strip() in ("_No response_", "None", "N/A", "null"):
        return ""
    return val.strip()


def parse_issue_markdown(text):
    """
    Parses GitHub Issue Form / Markdown template body.
    Extracts title, source, date, link, type, media_scope, lang, country, author, topics, verbatim, editorial_note.
    """
    data = {
        "title": "",
        "source": "",
        "date": "",
        "link": "",
        "type": "article",
        "media_scope": "national",
        "lang": "fr",
        "country": "fra",
        "author": "",
        "topics": [],
        "verbatim": "",
        "editorial_note": "",
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
        content = clean_field_value(content)

        if not content:
            continue

        if re.search(r"\b(title|titre|headline)\b", header):
            data["title"] = content.splitlines()[0].strip().lstrip("#").strip()
        elif re.search(r"\bdate\b", header):
            date_match = re.search(r"\b(\d{4}[-/]\d{1,2}[-/]\d{1,2})\b", content)
            if date_match:
                raw_d = date_match.group(1).replace("/", "-")
                parts = raw_d.split("-")
                data["date"] = f"{int(parts[0]):04d}-{int(parts[1]):02d}-{int(parts[2]):02d}"
            else:
                data["date"] = content.splitlines()[0].strip()
        elif re.search(r"\b(scope|portee)\b", header):
            raw_scope = content.splitlines()[0].strip().lower()
            for s in VALID_SCOPES:
                if s in raw_scope:
                    data["media_scope"] = s
                    break
        elif re.search(r"\b(type|format)\b", header):
            raw_type = content.splitlines()[0].strip().lower()
            # E.g. "article (Written article / news story)" -> "article"
            for t in VALID_TYPES:
                if t in raw_type:
                    data["type"] = t
                    break
        elif re.search(r"\b(source|outlet|journal|publisher|newspaper|magazine)\b", header) or header.strip() in ("media", "media name"):
            data["source"] = content.splitlines()[0].strip()
        elif re.search(r"\b(link|url|lien|website)\b", header):
            # Extract first URL found or raw line
            url_match = re.search(r"https?://\S+", content)
            if url_match:
                data["link"] = url_match.group(0).rstrip(")>].,\"'")
            else:
                data["link"] = content.splitlines()[0].strip()
        elif re.search(r"\b(lang|language|langue)\b", header):
            lang_match = re.search(r"\b([a-z]{2})\b", content, re.IGNORECASE)
            if lang_match:
                data["lang"] = lang_match.group(1).lower()
        elif re.search(r"\b(country|pays)\b", header):
            country_match = re.search(r"\b([a-z]{3}|eu)\b", content, re.IGNORECASE)
            if country_match:
                data["country"] = country_match.group(1).lower()
        elif re.search(r"\b(author|journalist|auteur|journaliste)\b", header):
            data["author"] = content.splitlines()[0].strip()
        elif re.search(r"\b(topic|topics|sujet|sujets|tag|tags)\b", header):
            # Parse checkbox lines or tokens
            extracted_topics = []
            for line in content.splitlines():
                line = line.strip()
                if not line:
                    continue
                # Unchecked checkbox: skip
                if re.match(r"^-\s*\[\s*\]", line):
                    continue
                # Checked checkbox: extract
                chk_match = re.match(r"^-\s*\[[xX]\]\s*(.*)", line)
                if chk_match:
                    topic_text = chk_match.group(1).lower()
                    for kt in KNOWN_TOPICS:
                        if kt in topic_text:
                            extracted_topics.append(kt)
                else:
                    # Comma-separated or single words
                    for word in re.split(r"[\s,]+", line.lower()):
                        word = word.strip()
                        if word in KNOWN_TOPICS and word not in extracted_topics:
                            extracted_topics.append(word)
            if extracted_topics:
                data["topics"] = sorted(list(set(extracted_topics)))
        elif re.search(r"\b(verbatim|quote|citation|excerpt|extrait)\b", header):
            data["verbatim"] = content
        elif re.search(r"\b(editorial|internal|note)\b", header):
            data["editorial_note"] = content

    return data


def generate_item_id(date_str, source_str, title_str, existing_ids=None):
    """
    Generates a unique item id following OFF press-review conventions:
    {date}-{source_slug}-{title_slug}
    """
    if existing_ids is None:
        existing_ids = set()

    s = slugify(source_str, 16) or "source"
    t = slugify(title_str, 32) or "mention"
    base_slug = f"{date_str}-{s}-{t}".strip("-")

    slug = base_slug
    counter = 2
    while slug in existing_ids:
        slug = f"{base_slug}-{counter}"
        counter += 1

    return slug


def get_existing_ids(directory=PRESS_DIR):
    """List of all existing YAML ids in data/press-review/."""
    ids = set()
    if not os.path.isdir(directory):
        return ids
    for fname in os.listdir(directory):
        if fname.endswith(".yaml") or fname.endswith(".yml"):
            stem = fname[:-5] if fname.endswith(".yaml") else fname[:-4]
            ids.add(stem)
    return ids


def build_press_item_dict(
    title,
    source,
    date,
    link,
    media_type="article",
    media_scope="national",
    lang="fr",
    country="fra",
    author="",
    topics=None,
    verbatim="",
    editorial_note="",
    selected=False,
    dead_link=False,
    origin="github-issue",
    custom_id=None,
    directory=PRESS_DIR,
):
    """
    Constructs and cleans a complete press review item dict.
    """
    title = clean_acronym_off(str(title).strip())
    source = clean_acronym_off(str(source).strip())
    date = str(date).strip()
    link = str(link).strip()
    author = str(author or "").strip()
    verbatim = clean_acronym_off(str(verbatim or "").strip())
    editorial_note = clean_acronym_off(str(editorial_note or "").strip())

    if topics is None:
        topics = []
    elif isinstance(topics, str):
        topics = [t.strip() for t in re.split(r"[\s,]+", topics) if t.strip()]

    # Clean domain
    domain = extract_domain(link)

    # Validate type and media_scope
    media_type = str(media_type).lower().strip()
    if media_type not in VALID_TYPES:
        media_type = "article"

    media_scope = str(media_scope).lower().strip()
    if media_scope not in VALID_SCOPES:
        media_scope = "national"

    raw_type = media_type.capitalize()

    # Generate unique ID
    existing = get_existing_ids(directory)
    if custom_id:
        p_id = slugify(custom_id, 80)
    else:
        p_id = generate_item_id(date, source, title, existing_ids=existing)

    item = {
        "id": p_id,
        "date": date,
        "source": source,
        "title": title,
        "link": link,
        "domain": domain,
        "type": media_type,
        "media_scope": media_scope,
        "raw_type": raw_type,
        "lang": str(lang).lower().strip() or "fr",
        "country": str(country).lower().strip() or "fra",
        "author": author,
        "topic": "",
        "topics": sorted(list(set(topics))),
        "verbatim": verbatim,
        "dead_link": bool(dead_link),
        "selected": bool(selected),
        "origin": str(origin).strip() or "github-issue",
    }

    if editorial_note:
        item["editorial_note"] = editorial_note

    # Order keys
    ordered = {}
    for k in PRESS_KEY_ORDER:
        if k in item:
            ordered[k] = item[k]
    for k, v in item.items():
        if k not in ordered:
            ordered[k] = v

    return ordered


def add_press_review_entry(
    title,
    source,
    date,
    link,
    media_type="article",
    media_scope="national",
    lang="fr",
    country="fra",
    author="",
    topics=None,
    verbatim="",
    editorial_note="",
    selected=False,
    dead_link=False,
    origin="github-issue",
    custom_id=None,
    dry_run=False,
    do_compile=False,
    directory=PRESS_DIR,
):
    """
    Main function to validate and add a new entry to data/press-review/.
    """
    item = build_press_item_dict(
        title=title,
        source=source,
        date=date,
        link=link,
        media_type=media_type,
        media_scope=media_scope,
        lang=lang,
        country=country,
        author=author,
        topics=topics,
        verbatim=verbatim,
        editorial_note=editorial_note,
        selected=selected,
        dead_link=dead_link,
        origin=origin,
        custom_id=custom_id,
        directory=directory,
    )

    slug = item["id"]
    target_filename = f"{slug}.yaml"
    target_filepath = os.path.join(directory, target_filename)

    # Validate against compile_press_review schema
    errors, warnings = validate_press_item(item, target_filepath)
    if errors:
        return {
            "success": False,
            "error": f"Validation failed: {'; '.join(errors)}",
            "warnings": warnings,
            "item": item,
        }

    if dry_run:
        return {
            "success": True,
            "dry_run": True,
            "id": slug,
            "file": os.path.relpath(target_filepath, REPO_ROOT),
            "full_path": target_filepath,
            "title": item["title"],
            "source": item["source"],
            "date": item["date"],
            "link": item["link"],
            "type": item["type"],
            "warnings": warnings,
            "yaml_preview": yaml.dump(item, allow_unicode=True, sort_keys=False, width=120),
        }

    # Write file
    os.makedirs(directory, exist_ok=True)
    with open(target_filepath, "w", encoding="utf-8") as out:
        yaml.dump(item, out, allow_unicode=True, sort_keys=False, width=120)

    # Recompile if requested
    if do_compile:
        try:
            with contextlib.redirect_stdout(sys.stderr):
                compile_success = compile_press_review(check_only=False, verbose=False)
            if not compile_success:
                return {
                    "success": False,
                    "error": "Failed to recompile press review dataset after adding entry.",
                    "file": os.path.relpath(target_filepath, REPO_ROOT),
                }
        except Exception as e:
            # Handle possible OS-level permission restrictions gracefully in local dev
            print(f"[WARN] HTML compilation warning: {e}", file=sys.stderr)

    return {
        "success": True,
        "id": slug,
        "file": os.path.relpath(target_filepath, REPO_ROOT),
        "full_path": target_filepath,
        "title": item["title"],
        "source": item["source"],
        "date": item["date"],
        "link": item["link"],
        "type": item["type"],
        "media_scope": item["media_scope"],
        "lang": item["lang"],
        "country": item["country"],
        "warnings": warnings,
    }


def main():
    parser = argparse.ArgumentParser(description="Add entries to the Open Food Facts Press Review.")
    parser.add_argument("--title", help="Title of the article, segment, or study")
    parser.add_argument("--source", help="Media source / publication name")
    parser.add_argument("--date", help="Publication date (YYYY-MM-DD)")
    parser.add_argument("--link", help="Direct URL to the mention")
    parser.add_argument("--type", choices=list(VALID_TYPES), default="article", help="Media type")
    parser.add_argument("--media-scope", choices=list(VALID_SCOPES), default="national", help="Media scope")
    parser.add_argument("--lang", default="fr", help="Language code (e.g. fr, en, es, de, it)")
    parser.add_argument("--country", default="fra", help="Country code (e.g. fra, deu, esp, ita, eu)")
    parser.add_argument("--author", default="", help="Author or journalist name")
    parser.add_argument("--topics", nargs="*", help="Topics covered")
    parser.add_argument("--verbatim", default="", help="Key quote or excerpt mentioning Open Food Facts")
    parser.add_argument("--editorial-note", default="", help="Internal note for editors")
    parser.add_argument("--selected", action="store_true", help="Highlight as featured entry")
    parser.add_argument("--dead-link", action="store_true", help="Mark link as archived/broken")
    parser.add_argument("--id", help="Explicit ID/slug to use")

    # Inputs
    parser.add_argument("--from-issue-file", help="Path to markdown issue file")
    parser.add_argument("--from-issue-text", help="Raw issue text")
    parser.add_argument("--from-env", action="store_true", help="Read ISSUE_BODY from environment")
    parser.add_argument("--issue-number", help="GitHub issue number reference")

    # Actions
    parser.add_argument("--compile", action="store_true", help="Recompile data/press-review-merged.json and HTML pages")
    parser.add_argument("--dry-run", action="store_true", help="Validate without writing changes")
    parser.add_argument("--json", action="store_true", help="Output result as JSON")
    parser.add_argument("--output-json", help="Path to write JSON result to")

    args = parser.parse_args()

    title = args.title
    source = args.source
    date = args.date
    link = args.link
    media_type = args.type
    media_scope = args.media_scope
    lang = args.lang
    country = args.country
    author = args.author
    topics = args.topics
    verbatim = args.verbatim
    editorial_note = args.editorial_note

    raw_text = None
    if args.from_env:
        raw_text = os.environ.get("ISSUE_BODY", "")
    elif args.from_issue_file:
        with open(args.from_issue_file, "r", encoding="utf-8") as f:
            raw_text = f.read()
    elif args.from_issue_text:
        raw_text = args.from_issue_text
    elif not sys.stdin.isatty() and not (title and source and date and link):
        raw_text = sys.stdin.read()

    if raw_text:
        parsed = parse_issue_markdown(raw_text)
        title = parsed.get("title") or title
        source = parsed.get("source") or source
        date = parsed.get("date") or date
        link = parsed.get("link") or link
        media_type = parsed.get("type") or media_type
        media_scope = parsed.get("media_scope") or media_scope
        lang = parsed.get("lang") or lang
        country = parsed.get("country") or country
        author = parsed.get("author") or author
        topics = parsed.get("topics") or topics
        verbatim = parsed.get("verbatim") or verbatim
        editorial_note = parsed.get("editorial_note") or editorial_note

    missing = []
    if not title:
        missing.append("--title / Article Title")
    if not source:
        missing.append("--source / Media Source")
    if not date:
        missing.append("--date / Publication Date (YYYY-MM-DD)")
    if not link:
        missing.append("--link / URL")

    if missing:
        err_msg = f"Missing required fields: {', '.join(missing)}"
        err_dict = {"success": False, "error": err_msg}
        if args.output_json:
            with open(args.output_json, "w", encoding="utf-8") as f:
                json.dump(err_dict, f, indent=2)
        if args.json:
            print(json.dumps(err_dict, indent=2))
        else:
            print(f"❌ Error: {err_msg}", file=sys.stderr)
        sys.exit(1)

    result = add_press_review_entry(
        title=title,
        source=source,
        date=date,
        link=link,
        media_type=media_type,
        media_scope=media_scope,
        lang=lang,
        country=country,
        author=author,
        topics=topics,
        verbatim=verbatim,
        editorial_note=editorial_note,
        selected=args.selected,
        dead_link=args.dead_link,
        origin=f"github-issue-#{args.issue_number}" if args.issue_number else "github-issue",
        custom_id=args.id,
        dry_run=args.dry_run,
        do_compile=args.compile,
    )

    if args.output_json:
        with open(args.output_json, "w", encoding="utf-8") as f:
            json.dump(result, f, indent=2)

    if args.json:
        print(json.dumps(result, indent=2))
    else:
        if result.get("success"):
            action = "[Dry Run] Validated" if result.get("dry_run") else "Successfully added"
            print(f"✅ {action} press review entry:")
            print(f"   ID:     {result.get('id')}")
            print(f"   Source: {result.get('source')}")
            print(f"   Date:   {result.get('date')}")
            print(f"   Title:  {result.get('title')}")
            print(f"   File:   {result.get('file')}")
            if result.get("warnings"):
                for w in result["warnings"]:
                    print(f"   [WARN]  {w}")
        else:
            print(f"❌ Error adding press review entry: {result.get('error')}", file=sys.stderr)
            sys.exit(1)


if __name__ == "__main__":
    main()
