#!/usr/bin/env python3
"""
Add scientific publications to Open Food Facts from GitHub issues, PR templates, or CLI.

This script parses GitHub issue bodies submitted via `.github/ISSUE_TEMPLATE/new-scientific-publication.yml`,
formats the publication into a standard YAML file under `data/scientific_publications/<id>.yaml`,
validates the result against schema rules, and optionally recompiles `data/scientific_publications.json`
and publication HTML views.

Usage:
    # From GitHub issue environment variables:
    python3 scripts/add_scientific_publication.py --from-env --compile --json --output-json result.json

    # Directly via CLI flags:
    python3 scripts/add_scientific_publication.py \
        --title "Nutri-Score: Evidence of the effectiveness of the French front-of-pack nutrition label" \
        --authors "Chantal Julia, Serge Hercberg" \
        --journal "Foods" \
        --year 2026 \
        --url "https://www.mdpi.com/..." \
        --doi "10.3390/foods15152651" \
        --theme nutrition \
        --excerpt "Evaluated 15,000 products from Open Food Facts..." \
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
import urllib.request
import yaml

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
DATA_DIR = os.path.join(REPO_ROOT, "data")
PUBLICATIONS_DIR = os.path.join(DATA_DIR, "scientific_publications")

try:
    from build_scientific_publications import (
        compile_publications,
        validate_publication,
        PUBLICATIONS_DIR,
    )
except ImportError:
    sys.path.insert(0, os.path.dirname(__file__))
    from build_scientific_publications import (
        compile_publications,
        validate_publication,
        PUBLICATIONS_DIR,
    )

PUB_KEY_ORDER = [
    "id",
    "title",
    "authors",
    "journal",
    "year",
    "doi",
    "url",
    "url_pdf",
    "num_citations",
    "usage_score",
    "themes",
    "type",
    "country",
    "excerpt",
    "featured",
]

KNOWN_THEMES = {
    "nutrition",
    "ultra_processed",
    "environment",
    "additives",
    "food_classification",
    "computer_science",
    "public_health",
    "mobile_apps",
    "consumer_empowerment",
    "food_waste",
    "allergies",
}


def slugify(text, max_words=6):
    """Normalize text into URL/ID friendly slug."""
    text = unicodedata.normalize("NFKD", str(text)).encode("ascii", "ignore").decode("ascii")
    text = re.sub(r"[^\w\s-]", "", text.lower()).strip()
    words = text.split()[:max_words]
    return "-".join(words)


def clean_field_value(val):
    """Clean GitHub Issue field value removing markdown comments and '_No response_' placeholders."""
    if not val:
        return ""
    val = re.sub(r"<!--.*?-->", "", str(val), flags=re.DOTALL).strip()
    if val.strip() in ("_No response_", "None", "N/A", "null"):
        return ""
    return val.strip()


def clean_doi(doi):
    """Normalize DOI identifier by removing URL prefixes or 'doi:' tags."""
    if not doi:
        return ""
    doi = str(doi).strip()
    doi = re.sub(r"^https?://(dx\.)?doi\.org/", "", doi)
    doi = re.sub(r"^doi:\s*", "", doi, flags=re.IGNORECASE)
    return doi.strip()


def parse_authors_input(authors_input):
    """Parses authors string into a clean list of author names."""
    if isinstance(authors_input, list):
        return [str(a).strip() for a in authors_input if str(a).strip()]
    
    text = clean_field_value(authors_input)
    if not text:
        return []

    # Replace newlines with commas
    text = text.replace("\n", ", ")
    
    # Split by semicolon, comma, or ' and '
    delimiters = [";", " and ", ","]
    authors = [text]
    for d in delimiters:
        new_authors = []
        for a in authors:
            for part in a.split(d):
                part = part.strip().rstrip(",")
                if part and part.lower() != "and":
                    new_authors.append(part)
        authors = new_authors

    return authors if authors else []


parse_authors = parse_authors_input


def get_first_author_surname(authors):
    """Extract surname of first author for ID generation."""
    if not authors or len(authors) == 0:
        return "author"
    first_author_full = authors[0]
    words = first_author_full.split()
    if not words:
        return "author"
    surname = words[-1].lower()
    surname = re.sub(r"[^a-z0-9]", "", surname)
    return surname or "author"


def fetch_doi_metadata(doi):
    """Fetch metadata from Crossref API if available."""
    if not doi:
        return None
    doi = doi.strip()
    if doi.startswith("http"):
        doi = re.sub(r"^https?://(dx\.)?doi\.org/", "", doi)
    
    url = f"https://api.crossref.org/works/{urllib.parse.quote(doi)}"
    req = urllib.request.Request(
        url,
        headers={"User-Agent": "OpenFoodFacts-PublicationImporter/1.0 (mailto:contact@openfoodfacts.org)"}
    )
    try:
        with urllib.request.urlopen(req, timeout=5) as response:
            data = json.loads(response.read().decode("utf-8"))
            msg = data.get("message", {})
            title = msg.get("title", [""])[0]
            authors = []
            for a in msg.get("author", []):
                name = f"{a.get('given', '')} {a.get('family', '')}".strip()
                if name:
                    authors.append(name)
            journal = msg.get("container-title", [""])[0]
            year = None
            date_parts = msg.get("published-print", {}).get("date-parts") or msg.get("published-online", {}).get("date-parts") or msg.get("created", {}).get("date-parts")
            if date_parts and len(date_parts[0]) > 0:
                year = date_parts[0][0]
            return {
                "title": title,
                "authors": authors,
                "journal": journal,
                "year": year,
                "doi": doi,
                "url": f"https://doi.org/{doi}"
            }
    except Exception:
        return None


def parse_issue_markdown(text):
    """
    Parses GitHub Issue Form body submitted via new-scientific-publication.yml.
    """
    data = {
        "title": "",
        "authors": [],
        "journal": "",
        "year": "",
        "doi": "",
        "url": "",
        "url_pdf": "",
        "theme": "",
        "themes": [],
        "excerpt": "",
    }

    if not text:
        return data

    text = text.replace("\r\n", "\n")
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

        if re.search(r"\b(title|titre)\b", header):
            data["title"] = content.splitlines()[0].strip().lstrip("#").strip()
        elif re.search(r"\b(authors|author|auteurs)\b", header):
            data["authors"] = parse_authors_input(content)
        elif re.search(r"\b(journal|conference|publisher|revue)\b", header):
            data["journal"] = content.splitlines()[0].strip()
        elif re.search(r"\b(year|annee)\b", header):
            year_match = re.search(r"\b(19\d{2}|20\d{2})\b", content)
            if year_match:
                data["year"] = int(year_match.group(1))
            else:
                data["year"] = content.splitlines()[0].strip()
        elif re.search(r"\bdoi\b", header):
            doi_match = re.search(r"\b10\.\d{4,9}/[-._;()/:A-Za-z0-9]+\b", content)
            if doi_match:
                data["doi"] = doi_match.group(0).rstrip(".,;")
            else:
                data["doi"] = content.splitlines()[0].strip()
        elif re.search(r"\b(pdf)\b", header):
            url_match = re.search(r"https?://\S+", content)
            if url_match:
                data["url_pdf"] = url_match.group(0).rstrip(")>].,\"'")
            else:
                data["url_pdf"] = content.splitlines()[0].strip()
        elif re.search(r"\b(url|link|lien)\b", header):
            url_match = re.search(r"https?://\S+", content)
            if url_match:
                data["url"] = url_match.group(0).rstrip(")>].,\"'")
            else:
                data["url"] = content.splitlines()[0].strip()
        elif re.search(r"\b(primary\s*theme|theme\s*principal)\b", header):
            raw_theme = content.splitlines()[0].strip()
            # E.g. "nutrition (Nutritional profiling...)" -> "nutrition"
            clean_t = re.sub(r"\(.*?\)", "", raw_theme).strip().lower()
            data["theme"] = clean_t
        elif re.search(r"\b(themes|keywords|mots-cles|topics)\b", header):
            extracted = []
            for line in content.splitlines():
                line = line.strip()
                if not line or re.match(r"^-\s*\[\s*\]", line):
                    continue
                chk_match = re.match(r"^-\s*\[[xX]\]\s*(.*)", line)
                if chk_match:
                    item_text = chk_match.group(1).lower()
                    for kt in KNOWN_THEMES:
                        if kt in item_text:
                            extracted.append(kt)
                else:
                    for token in re.split(r"[\s,]+", line.lower()):
                        token = token.strip()
                        if token in KNOWN_THEMES:
                            extracted.append(token)
            data["themes"] = sorted(list(set(extracted)))
        elif re.search(r"\b(excerpt|usage|findings|abstract|resume|conclusions)\b", header):
            data["excerpt"] = content

    return data


def generate_publication_id(year, authors, title, existing_ids=None):
    """
    Generates a unique publication ID:
    {year}-{first_author_slug}-{title_slug}
    """
    if existing_ids is None:
        existing_ids = set()

    year_str = str(year) if year else "2026"
    
    first_author = get_first_author_surname(authors)
    title_slug = slugify(title, max_words=6) or "paper"
    base_id = f"{year_str}-{first_author}-{title_slug}".strip("-")

    slug = base_id
    counter = 2
    while slug in existing_ids:
        slug = f"{base_id}-{counter}"
        counter += 1

    return slug


generate_pub_id = generate_publication_id


def get_existing_publication_ids(directory=PUBLICATIONS_DIR):
    """List of all existing YAML IDs in data/scientific_publications/."""
    ids = set()
    if not os.path.isdir(directory):
        return ids
    for fname in os.listdir(directory):
        if fname.endswith(".yaml") or fname.endswith(".yml"):
            stem = fname[:-5] if fname.endswith(".yaml") else fname[:-4]
            ids.add(stem)
    return ids


def build_publication_dict(
    title,
    authors,
    year,
    journal="",
    doi="",
    url="",
    url_pdf="",
    theme="",
    themes=None,
    excerpt="",
    custom_id=None,
    featured=False,
    directory=PUBLICATIONS_DIR,
):
    """Constructs a clean publication dictionary."""
    title = str(title).strip()
    
    if not authors:
        authors = ["Unknown Author"]
    elif isinstance(authors, str):
        authors = parse_authors_input(authors)

    try:
        year = int(year)
    except Exception:
        year = 2026

    journal = str(journal or "").strip()
    doi = clean_doi(doi)
    url = str(url or "").strip()
    url_pdf = str(url_pdf or "").strip()
    excerpt = str(excerpt or "").strip()

    # Compile themes
    all_themes = set()
    if theme:
        clean_primary = re.sub(r"\(.*?\)", "", theme).strip().lower()
        if clean_primary in KNOWN_THEMES:
            all_themes.add(clean_primary)
        elif clean_primary:
            all_themes.add(clean_primary)

    if themes:
        if isinstance(themes, str):
            themes = [t.strip() for t in re.split(r"[\s,]+", themes) if t.strip()]
        for t in themes:
            all_themes.add(t)

    if not all_themes:
        all_themes.add("nutrition")

    existing_ids = get_existing_publication_ids(directory)
    if custom_id:
        pub_id = slugify(custom_id, 80)
    else:
        pub_id = generate_publication_id(year, authors, title, existing_ids=existing_ids)

    doc = {
        "id": pub_id,
        "title": title,
        "authors": authors,
        "journal": journal,
        "year": year,
        "doi": doi,
        "url": url if url else (f"https://doi.org/{doi}" if doi else ""),
        "url_pdf": url_pdf,
        "num_citations": 0,
        "usage_score": 2,
        "themes": sorted(list(all_themes)),
        "type": "paper",
        "excerpt": excerpt,
        "featured": bool(featured),
    }

    # Clean out empty optional string fields
    if not doc["doi"]:
        doc.pop("doi", None)
    if not doc["url_pdf"]:
        doc.pop("url_pdf", None)

    ordered = {}
    for k in PUB_KEY_ORDER:
        if k in doc:
            ordered[k] = doc[k]
    for k, v in doc.items():
        if k not in ordered:
            ordered[k] = v

    return ordered


def add_scientific_publication_entry(
    title,
    authors,
    year,
    journal="",
    doi="",
    url="",
    url_pdf="",
    theme="",
    themes=None,
    excerpt="",
    custom_id=None,
    featured=False,
    dry_run=False,
    do_compile=False,
    directory=PUBLICATIONS_DIR,
):
    """
    Validates and writes a new scientific publication entry to data/scientific_publications/.
    """
    # Crossref metadata lookup if DOI provided and metadata missing
    if doi and (not journal or not authors or not title):
        doi_meta = fetch_doi_metadata(doi)
        if doi_meta:
            title = title or doi_meta.get("title", "")
            if not authors and doi_meta.get("authors"):
                authors = doi_meta["authors"]
            journal = journal or doi_meta.get("journal", "")
            year = year or doi_meta.get("year", 2026)
            url = url or doi_meta.get("url", "")

    doc = build_publication_dict(
        title=title,
        authors=authors,
        year=year,
        journal=journal,
        doi=doi,
        url=url,
        url_pdf=url_pdf,
        theme=theme,
        themes=themes,
        excerpt=excerpt,
        custom_id=custom_id,
        featured=featured,
        directory=directory,
    )

    slug = doc["id"]
    target_filepath = os.path.join(directory, f"{slug}.yaml")

    errors, warnings = validate_publication(doc, target_filepath)
    if errors:
        return {
            "success": False,
            "error": f"Validation failed: {'; '.join(errors)}",
            "warnings": warnings,
            "doc": doc,
        }

    rel_filepath = os.path.relpath(target_filepath, REPO_ROOT)

    if dry_run:
        return {
            "success": True,
            "dry_run": True,
            "id": slug,
            "title": doc["title"],
            "authors": ", ".join(doc["authors"]),
            "year": doc["year"],
            "journal": doc.get("journal", ""),
            "url": doc.get("url", ""),
            "file": rel_filepath,
            "warnings": warnings,
            "yaml_preview": yaml.safe_dump(doc, sort_keys=False, allow_unicode=True),
        }

    os.makedirs(directory, exist_ok=True)
    with open(target_filepath, "w", encoding="utf-8") as out:
        yaml.safe_dump(doc, out, sort_keys=False, allow_unicode=True)

    if do_compile:
        try:
            with contextlib.redirect_stdout(sys.stderr):
                compile_success = compile_publications(check_only=False, verbose=False)
            if not compile_success:
                return {
                    "success": False,
                    "error": "Failed to recompile scientific publications after adding entry.",
                    "file": rel_filepath,
                }
        except Exception as e:
            print(f"[WARN] Publications compilation warning: {e}", file=sys.stderr)

    return {
        "success": True,
        "id": slug,
        "title": doc["title"],
        "authors": ", ".join(doc["authors"]),
        "year": doc["year"],
        "journal": doc.get("journal", ""),
        "url": doc.get("url", ""),
        "file": rel_filepath,
        "warnings": warnings,
    }


def main():
    parser = argparse.ArgumentParser(description="Add scientific publication to Open Food Facts database.")
    parser.add_argument("--title", help="Paper title")
    parser.add_argument("--authors", help="Authors (comma-separated or list)")
    parser.add_argument("--year", help="Publication year (YYYY)")
    parser.add_argument("--journal", help="Journal, conference, or publisher name")
    parser.add_argument("--doi", help="DOI identifier")
    parser.add_argument("--url", help="Paper URL")
    parser.add_argument("--url-pdf", help="Open access PDF URL")
    parser.add_argument("--theme", help="Primary research theme")
    parser.add_argument("--themes", nargs="*", help="Additional keywords or themes")
    parser.add_argument("--excerpt", help="Summary of Open Food Facts usage & findings")
    parser.add_argument("--id", help="Explicit publication ID (slug)")

    parser.add_argument("--from-issue-file", help="Path to markdown issue file")
    parser.add_argument("--from-issue-text", help="Raw issue markdown text")
    parser.add_argument("--from-env", action="store_true", help="Read ISSUE_BODY from environment")
    parser.add_argument("--issue-number", help="GitHub issue number reference")

    parser.add_argument("--compile", action="store_true", help="Recompile publications aggregate and HTML")
    parser.add_argument("--dry-run", action="store_true", help="Validate without writing files")
    parser.add_argument("--json", action="store_true", help="Output result as JSON")
    parser.add_argument("--output-json", help="Path to write JSON result to")

    args = parser.parse_args()

    title = args.title
    authors = args.authors
    year = args.year
    journal = args.journal
    doi = args.doi
    url = args.url
    url_pdf = args.url_pdf
    theme = args.theme
    themes = args.themes
    excerpt = args.excerpt

    raw_text = None
    if args.from_env:
        raw_text = os.environ.get("ISSUE_BODY", "")
    elif args.from_issue_file:
        with open(args.from_issue_file, "r", encoding="utf-8") as f:
            raw_text = f.read()
    elif args.from_issue_text:
        raw_text = args.from_issue_text
    elif not sys.stdin.isatty() and not (title and authors and year):
        raw_text = sys.stdin.read()

    if raw_text:
        parsed = parse_issue_markdown(raw_text)
        title = parsed.get("title") or title
        authors = parsed.get("authors") or authors
        year = parsed.get("year") or year
        journal = parsed.get("journal") or journal
        doi = parsed.get("doi") or doi
        url = parsed.get("url") or url
        url_pdf = parsed.get("url_pdf") or url_pdf
        theme = parsed.get("theme") or theme
        themes = parsed.get("themes") or themes
        excerpt = parsed.get("excerpt") or excerpt

    missing = []
    if not title:
        missing.append("--title / Paper Title")
    if not authors:
        missing.append("--authors / Authors")
    if not year:
        missing.append("--year / Publication Year")
    if not url and not doi:
        missing.append("--url or --doi / Publication URL")

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

    result = add_scientific_publication_entry(
        title=title,
        authors=authors,
        year=year,
        journal=journal,
        doi=doi,
        url=url,
        url_pdf=url_pdf,
        theme=theme,
        themes=themes,
        excerpt=excerpt,
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
            print(f"✅ {action} publication entry:")
            print(f"   ID:      {result.get('id')}")
            print(f"   Title:   {result.get('title')}")
            print(f"   Authors: {result.get('authors')}")
            print(f"   Year:    {result.get('year')}")
            print(f"   File:    {result.get('file')}")
            if result.get("warnings"):
                for w in result["warnings"]:
                    print(f"   [WARN]   {w}")
        else:
            print(f"❌ Error adding publication: {result.get('error')}", file=sys.stderr)
            sys.exit(1)


if __name__ == "__main__":
    main()
