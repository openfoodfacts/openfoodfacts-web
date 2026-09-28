#!/usr/bin/env python3
"""
Import or create a publication YAML file for Open Food Facts scientific publications,
with support for Google Scholar 'Quick Read' summaries and ultra-processed food metadata.

Usage:
  # Interactive mode:
  python3 scripts/import_scholar_publication.py

  # With arguments:
  python3 scripts/import_scholar_publication.py \
    --doi "10.3390/foods15152651" \
    --title "Are All Ultra-Processed Foods Created Equal?" \
    --authors "Melvin Bernardino, Julia Theresa Regalado" \
    --journal "Foods" \
    --year 2026 \
    --quick-read "The authors extracted 13,025 products from Open Food Facts..."
"""

import argparse
import json
import os
import re
import sys
import urllib.parse
import urllib.request
import yaml

PUBLICATIONS_DIR = "data/scientific_publications"

def slugify(text, max_words=6):
    text = text.lower()
    text = re.sub(r'[^a-z0-9\s-]', '', text)
    words = text.split()[:max_words]
    return "-".join(words)

def clean_author_name(author_str):
    author_str = author_str.strip().rstrip(',')
    # Remove trailing affiliations or email
    author_str = re.sub(r'\s*\([^)]*\)', '', author_str)
    return author_str

def parse_authors(authors_input):
    if isinstance(authors_input, list):
        return [clean_author_name(a) for a in authors_input if a]
    
    # Split by comma, semicolon, or 'and'
    delimiters = [';', ' and ', ',']
    for d in delimiters:
        if d in authors_input:
            parts = [clean_author_name(p) for p in authors_input.split(d) if clean_author_name(p)]
            if len(parts) > 1:
                return parts
    return [clean_author_name(authors_input)] if authors_input else ["Unknown Author"]

def fetch_doi_metadata(doi):
    """Fetch metadata from Crossref API if available."""
    doi = doi.strip()
    if doi.startswith("http"):
        doi = re.sub(r'^https?://(dx\.)?doi\.org/', '', doi)
    
    url = f"https://api.crossref.org/works/{urllib.parse.quote(doi)}"
    req = urllib.request.Request(
        url,
        headers={"User-Agent": "OpenFoodFacts-ScholarImporter/1.0 (mailto:contact@openfoodfacts.org)"}
    )
    try:
        with urllib.request.urlopen(req, timeout=6) as response:
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
            volume = msg.get("volume")
            return {
                "title": title,
                "authors": authors,
                "journal": journal,
                "year": year,
                "volume": str(volume) if volume else None,
                "doi": doi,
                "url": f"https://doi.org/{doi}"
            }
    except Exception as e:
        return None

def parse_quick_read(text):
    """
    Parses Google Scholar Quick Read sections:
    - Answers / Findings
    - Approach / Methodology
    - Considerations / Caveats
    """
    if not text:
        return "", {}
    
    # Check if text contains structured sections
    sections = {}
    current_key = "answers"
    lines = text.strip().splitlines()
    buffer = []
    
    for line in lines:
        line_clean = line.strip()
        lower = line_clean.lower()
        if lower.startswith("answers") or lower.startswith("key answers") or lower.startswith("summary"):
            if buffer:
                sections[current_key] = " ".join(buffer).strip()
                buffer = []
            current_key = "answers"
        elif lower.startswith("approach") or lower.startswith("methodology") or lower.startswith("methods"):
            if buffer:
                sections[current_key] = " ".join(buffer).strip()
                buffer = []
            current_key = "approach"
        elif lower.startswith("considerations") or lower.startswith("limitations") or lower.startswith("caveats"):
            if buffer:
                sections[current_key] = " ".join(buffer).strip()
                buffer = []
            current_key = "considerations"
        else:
            buffer.append(line_clean)
            
    if buffer:
        sections[current_key] = " ".join(buffer).strip()
    
    # Formulate unified excerpt for the website
    excerpt_parts = []
    if "answers" in sections:
        excerpt_parts.append(sections["answers"])
    if "approach" in sections:
        excerpt_parts.append(sections["approach"])
        
    excerpt = " ".join(excerpt_parts) if excerpt_parts else text.strip()
    return excerpt, sections

def create_publication(
    title,
    authors,
    journal,
    year,
    doi=None,
    url=None,
    num_citations=0,
    excerpt="",
    themes=None,
    pub_type="paper",
    usage_score=3,
    featured=True,
    quick_read_sections=None
):
    if not authors:
        authors = ["Unknown Author"]
    first_author = authors[0].split()[-1].lower() if authors[0] else "author"
    first_author = re.sub(r'[^a-z0-9]', '', first_author)
    
    year_str = str(year) if year else "2026"
    slug = slugify(title)
    pub_id = f"{year_str}-{first_author}-{slug}"
    
    if themes is None:
        themes = ["nutrition", "ultra_processed"]
    elif "ultra_processed" not in themes:
        themes.append("ultra_processed")
        
    doc = {
        "id": pub_id,
        "title": title.strip(),
        "authors": authors,
        "journal": journal.strip() if journal else "",
        "year": int(year) if year else 2026,
    }
    
    if doi:
        doc["doi"] = doi.strip()
    if url:
        doc["url"] = url.strip()
    elif doi:
        doc["url"] = f"https://doi.org/{doi.strip()}"
        
    if num_citations:
        doc["num_citations"] = int(num_citations)
        
    doc["themes"] = themes
    doc["type"] = pub_type
    doc["usage_score"] = int(usage_score)
    doc["excerpt"] = excerpt.strip()
    doc["featured"] = featured
    
    if quick_read_sections and len(quick_read_sections) > 1:
        doc["quick_read"] = quick_read_sections

    os.makedirs(PUBLICATIONS_DIR, exist_ok=True)
    out_path = os.path.join(PUBLICATIONS_DIR, f"{pub_id}.yaml")
    
    with open(out_path, "w", encoding="utf-8") as f:
        yaml.dump(doc, f, allow_unicode=True, sort_keys=False, default_flow_style=False)
        
    print(f"✅ Successfully created: {out_path}")
    return out_path

def main():
    parser = argparse.ArgumentParser(description="Import scientific publication into Open Food Facts YAML.")
    parser.add_argument("--doi", help="DOI of the paper")
    parser.add_argument("--title", help="Paper title")
    parser.add_argument("--authors", help="Comma or semicolon-separated authors")
    parser.add_argument("--journal", help="Journal or conference name")
    parser.add_argument("--year", type=int, help="Publication year")
    parser.add_argument("--url", help="Paper URL")
    parser.add_argument("--citations", type=int, default=0, help="Citation count")
    parser.add_argument("--excerpt", help="Excerpt or quote regarding Open Food Facts")
    parser.add_argument("--quick-read", help="Google Scholar Quick Read summary text")
    parser.add_argument("--usage-score", type=int, default=3, help="Usage score (0-5)")
    parser.add_argument("--themes", help="Comma-separated themes (default: nutrition,ultra_processed)")
    
    args = parser.parse_args()
    
    metadata = {}
    if args.doi:
        fetched = fetch_doi_metadata(args.doi)
        if fetched:
            print(f"ℹ️ Retrieved metadata for DOI {args.doi} via Crossref")
            metadata.update(fetched)
            
    title = args.title or metadata.get("title")
    authors = parse_authors(args.authors) if args.authors else metadata.get("authors", [])
    journal = args.journal or metadata.get("journal", "")
    year = args.year or metadata.get("year", 2026)
    url = args.url or metadata.get("url")
    doi = args.doi or metadata.get("doi")
    
    quick_read_raw = args.quick_read or ""
    excerpt_text, quick_read_dict = parse_quick_read(quick_read_raw)
    if args.excerpt:
        excerpt_text = args.excerpt
        
    themes = [t.strip() for t in args.themes.split(",")] if args.themes else ["nutrition", "ultra_processed"]
    
    if not title:
        print("Error: Paper title is required. Provide --title or a valid --doi.")
        sys.exit(1)
        
    create_publication(
        title=title,
        authors=authors,
        journal=journal,
        year=year,
        doi=doi,
        url=url,
        num_citations=args.citations,
        excerpt=excerpt_text,
        themes=themes,
        usage_score=args.usage_score,
        featured=True,
        quick_read_sections=quick_read_dict
    )

if __name__ == "__main__":
    main()
