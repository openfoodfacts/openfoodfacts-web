#!/usr/bin/env python3
"""
Add or update a Scan Party event in the Open Food Facts directory.

This script parses GitHub issue bodies submitted via `.github/ISSUE_TEMPLATE/new-scan-party.yml`
or markdown templates, validates fields against schema rules in compile_scan_parties.py,
writes the YAML file to `data/scan_parties/<id>.yaml`, and optionally recompiles
`data/scan_parties.json` and static HTML pages.

Usage:
    # From GitHub issue environment variables:
    python3 scripts/add_scan_party.py --from-env --compile --json --output-json result.json

    # From issue file:
    python3 scripts/add_scan_party.py --from-issue-file issue.md --compile

    # Directly via CLI flags:
    python3 scripts/add_scan_party.py \\
        --title "Scan Party Lyon" \\
        --type upcoming \\
        --date "November 2026" \\
        --start-date "2026-11-15" \\
        --venue "Biocoop Bellecour" \\
        --city "Lyon" \\
        --country "fra" \\
        --description "Scanning local products and organic drinks in Lyon." \\
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
SCAN_PARTIES_DIR = os.path.join(DATA_DIR, "scan_parties")

try:
    from compile_scan_parties import (
        compile_scan_parties,
        validate_scan_party,
        VALID_TYPES,
        VALID_STATUSES,
        SCAN_PARTIES_DIR as CSP_DIR,
    )
except ImportError:
    sys.path.insert(0, os.path.dirname(__file__))
    from compile_scan_parties import (
        compile_scan_parties,
        validate_scan_party,
        VALID_TYPES,
        VALID_STATUSES,
        SCAN_PARTIES_DIR as CSP_DIR,
    )

SP_KEY_ORDER = [
    "id",
    "title",
    "type",
    "status",
    "date",
    "start_date",
    "location",
    "city",
    "country",
    "venue",
    "organizer",
    "description",
    "image",
    "image_caption",
    "products_scanned",
    "participants_count",
    "link",
    "tags",
]

COUNTRY_MAP = {
    "france": "fra",
    "fr": "fra",
    "fra": "fra",
    "united kingdom": "gbr",
    "uk": "gbr",
    "great britain": "gbr",
    "gbr": "gbr",
    "spain": "esp",
    "españa": "esp",
    "espana": "esp",
    "es": "esp",
    "esp": "esp",
    "germany": "deu",
    "deutschland": "deu",
    "de": "deu",
    "deu": "deu",
    "united states": "usa",
    "usa": "usa",
    "us": "usa",
    "guyana": "guf",
    "french guiana": "guf",
    "guyane": "guf",
    "guf": "guf",
    "belgium": "bel",
    "belgique": "bel",
    "be": "bel",
    "bel": "bel",
    "switzerland": "che",
    "suisse": "che",
    "ch": "che",
    "che": "che",
    "italy": "ita",
    "italie": "ita",
    "it": "ita",
    "ita": "ita",
    "canada": "can",
    "ca": "can",
    "can": "can",
}


def slugify(text, max_len=50):
    """Normalize text into URL/ID friendly slug."""
    if not text:
        return ""
    text = unicodedata.normalize("NFKD", str(text)).encode("ascii", "ignore").decode("ascii")
    text = re.sub(r"[^\w\s-]", "", text.lower()).strip()
    slug = re.sub(r"[-\s]+", "-", text)
    return slug[:max_len].rstrip("-")


def clean_field_value(val):
    """Clean GitHub Issue field value removing markdown comments and '_No response_' placeholders."""
    if val is None:
        return ""
    val = re.sub(r"<!--.*?-->", "", str(val), flags=re.DOTALL).strip()
    if val.strip().lower() in ("_no response_", "none", "n/a", "null", ""):
        return ""
    return val.strip()


def clean_dropdown(val):
    """
    Extract key from dropdown options like:
    'upcoming (Upcoming Event)' -> 'upcoming'
    'past (Past / Completed Event)' -> 'past'
    """
    if not val:
        return ""
    val = clean_field_value(val)
    if "(" in val:
        val = val.split("(", 1)[0].strip()
    return val.strip().lower()


def clean_url(url):
    """Normalize and validate a URL."""
    if not url:
        return None
    url = clean_field_value(url)
    if not url:
        return None
    # Strip markdown link format [title](url) or angle brackets <url>
    md_match = re.search(r"\((https?://[^\s)]+)\)", url)
    if md_match:
        url = md_match.group(1).strip()
    url = url.strip("<>").strip()
    if not url.startswith("http://") and not url.startswith("https://"):
        return None
    return url


def parse_int_or_none(val):
    """Parse integer or return None."""
    if val is None:
        return None
    val = clean_field_value(val)
    if not val:
        return None
    try:
        m = re.search(r"(\d[\d,\s]*)", str(val))
        if m:
            clean_digits = re.sub(r"[^\d]", "", m.group(1))
            if clean_digits:
                return int(clean_digits)
    except Exception:
        pass
    return None


def normalize_country(country_val, location_val=None):
    """Normalize country code to 3-letter ISO or clean string."""
    if country_val:
        c_clean = clean_field_value(country_val).lower()
        if c_clean in COUNTRY_MAP:
            return COUNTRY_MAP[c_clean]
        if len(c_clean) == 3 and c_clean.isalpha():
            return c_clean

    if location_val:
        loc_lower = str(location_val).lower()
        for name, code in COUNTRY_MAP.items():
            if re.search(rf"\b{re.escape(name)}\b", loc_lower):
                return code

    return clean_field_value(country_val).lower() if country_val else None


def parse_issue_markdown(text):
    """
    Parses GitHub Issue Form or raw Markdown template body.
    Supports both GitHub Issue Form structure and pre-filled URL markdown format.
    """
    data = {}
    if not text:
        return data

    text = text.replace("\r\n", "\n")

    # Split into sections starting with '### '
    sections = re.split(r"(?m)^###\s+", "\n" + text)
    for sec in sections:
        sec = sec.strip()
        if not sec:
            continue
        lines = sec.splitlines()
        raw_header = lines[0].strip()
        # Strip emojis and punctuation from header
        clean_header = re.sub(r"[^\w\s/&-]", "", raw_header).strip().lower()
        content = "\n".join(lines[1:]).strip()
        content = re.sub(r"<!--.*?-->", "", content, flags=re.DOTALL).strip()
        if content.lower() in ("_no response_", "none", "n/a", "null"):
            content = ""

        # Check for bullet key-value pairs inside content
        bullet_dict = {}
        for line in lines[1:]:
            bullet_match = re.match(r"^\s*[-*]\s*([^:]+):\s*(.*)$", line)
            if bullet_match:
                b_key = bullet_match.group(1).strip().lower()
                b_val = bullet_match.group(2).strip()
                b_val = re.sub(r"<!--.*?-->", "", b_val, flags=re.DOTALL).strip()
                if b_val.lower() not in ("_no response_", "none", "n/a", "null", ""):
                    bullet_dict[b_key] = b_val

        # If this section contains bullet key-value pairs, populate directly
        if bullet_dict:
            for k in ["venue name", "venue", "lieu", "magasin"]:
                if k in bullet_dict:
                    data["venue"] = bullet_dict[k]
                    break
            if "city" in bullet_dict or "ville" in bullet_dict:
                data["city"] = bullet_dict.get("city") or bullet_dict.get("ville")
            if "country" in bullet_dict or "pays" in bullet_dict:
                data["country"] = bullet_dict.get("country") or bullet_dict.get("pays")
            if "location" in bullet_dict:
                data["location"] = bullet_dict["location"]
            if "date" in bullet_dict:
                data["date"] = bullet_dict["date"]
            if "start date" in bullet_dict:
                data["start_date"] = bullet_dict["start date"]
            if "start time" in bullet_dict:
                data["start_time"] = bullet_dict["start time"]
            for k in ["organizer name / organization", "organizer name", "organizer", "organization", "organisateur"]:
                if k in bullet_dict:
                    data["organizer"] = bullet_dict[k]
                    break
            for k in ["contact email / slack handle", "contact", "email", "slack"]:
                if k in bullet_dict:
                    data["contact"] = bullet_dict[k]
                    break
            for k in ["link", "registration", "recap link", "url"]:
                if k in bullet_dict:
                    data["link"] = bullet_dict[k]
                    break
            for k in ["products", "products scanned", "produits"]:
                if k in bullet_dict:
                    data["products_scanned"] = bullet_dict[k]
                    break
            for k in ["participants", "participants count"]:
                if k in bullet_dict:
                    data["participants_count"] = bullet_dict[k]
                    break

        # Map header keywords for non-bullet or explicit content
        if "title" in clean_header or clean_header.startswith("scan party"):
            data["title"] = content.splitlines()[0].strip() if content else ""
        elif "timing" in clean_header or clean_header == "type" or "event type" in clean_header:
            data["type"] = clean_dropdown(content)
        elif "status" in clean_header or "event status" in clean_header:
            data["status"] = clean_dropdown(content)
        elif "start date" in clean_header:
            data["start_date"] = clean_field_value(content.splitlines()[0] if content else "")
        elif "date" in clean_header:
            if content and not data.get("date"):
                data["date"] = content.splitlines()[0].strip()
        elif "venue" in clean_header and not data.get("venue"):
            if content:
                data["venue"] = content.splitlines()[0].strip()
        elif clean_header == "city" and not data.get("city"):
            data["city"] = content.splitlines()[0].strip() if content else ""
        elif clean_header == "country" and not data.get("country"):
            data["country"] = content.splitlines()[0].strip() if content else ""
        elif "location" in clean_header and not data.get("location"):
            if content and not bullet_dict:
                data["location"] = content.splitlines()[0].strip()
        elif "organizer" in clean_header and not data.get("organizer"):
            if content:
                data["organizer"] = content.splitlines()[0].strip()
        elif "description" in clean_header:
            data["description"] = content.strip()
        elif ("registration" in clean_header or "recap link" in clean_header or "link" in clean_header or "url" in clean_header) and not data.get("link"):
            if content:
                data["link"] = content.splitlines()[0].strip()
        elif "image url" in clean_header or clean_header == "image":
            data["image"] = content.splitlines()[0].strip() if content else ""
        elif "image caption" in clean_header or "caption" in clean_header:
            data["image_caption"] = content.splitlines()[0].strip() if content else ""
        elif "products" in clean_header and not data.get("products_scanned"):
            data["products_scanned"] = content.splitlines()[0].strip() if content else ""
        elif "participants" in clean_header and not data.get("participants_count"):
            data["participants_count"] = content.splitlines()[0].strip() if content else ""
        elif "tag" in clean_header or "keyword" in clean_header:
            data["tags"] = content.strip()

    return data


def build_scan_party_dict(
    title,
    event_type=None,
    status=None,
    date=None,
    start_date=None,
    location=None,
    venue=None,
    city=None,
    country=None,
    organizer=None,
    description=None,
    image=None,
    image_caption=None,
    products_scanned=None,
    participants_count=None,
    link=None,
    tags=None,
    custom_id=None,
    type=None,
    **kwargs,
):
    """Constructs standard scan party dictionary."""
    title = clean_field_value(title)
    if not title:
        raise ValueError("Title is required for scan party")

    # Clean dropdowns
    event_type = type or event_type or "upcoming"
    event_type = clean_dropdown(event_type) or "upcoming"
    if event_type not in VALID_TYPES:
        event_type = "upcoming"

    if status:
        status = clean_dropdown(status)
        if status not in VALID_STATUSES:
            status = "completed" if event_type == "past" else "upcoming"
    else:
        status = "completed" if event_type == "past" else "upcoming"

    # Dates
    date = clean_field_value(date)
    start_date = clean_field_value(start_date)

    if not date and start_date:
        date = start_date
    elif not start_date and date:
        # Check if date is in YYYY-MM-DD format
        m = re.search(r"\b(\d{4}-\d{2}-\d{2})\b", date)
        if m:
            start_date = m.group(1)
        else:
            # Check YYYY-MM
            m_ym = re.search(r"\b(\d{4})-(\d{2})\b", date)
            if m_ym:
                start_date = f"{m_ym.group(1)}-{m_ym.group(2)}-01"
            else:
                # Check Year
                m_y = re.search(r"\b(20\d{2})\b", date)
                if m_y:
                    start_date = f"{m_y.group(1)}-01-01"

    # Venue & Location
    venue = clean_field_value(venue)
    city = clean_field_value(city)
    location = clean_field_value(location)
    country = normalize_country(country, location)

    if not location:
        if city and country:
            country_display = country.upper()
            if country == "fra":
                country_display = "France"
            elif country == "gbr":
                country_display = "United Kingdom"
            elif country == "esp":
                country_display = "Spain"
            elif country == "deu":
                country_display = "Germany"
            elif country == "usa":
                country_display = "USA"
            elif country == "guf":
                country_display = "French Guiana"
            location = f"{city}, {country_display}"
        elif city:
            location = city
        elif venue:
            location = venue
        else:
            location = "Online / Global"

    if not venue:
        venue = location or "TBD"

    if not city and location and "," in location:
        city = location.split(",")[0].strip()

    description = clean_field_value(description)
    organizer = clean_field_value(organizer) or None

    # Image
    image = clean_url(image)
    image_caption = clean_field_value(image_caption) or None

    # Link
    link = clean_url(link)

    # Numbers
    products_scanned = parse_int_or_none(products_scanned)
    participants_count = parse_int_or_none(participants_count)

    # Tags
    tag_list = []
    if tags:
        if isinstance(tags, list):
            tag_list = [clean_field_value(t).lower() for t in tags if clean_field_value(t)]
        else:
            tag_tokens = re.split(r"[,;\n]+", str(tags))
            tag_list = [slugify(t) for t in tag_tokens if slugify(t)]

    # Add default tags if needed
    if event_type == "upcoming" and "upcoming" not in tag_list:
        tag_list.append("upcoming")
    if city and slugify(city) not in tag_list:
        tag_list.append(slugify(city))

    # Slug ID
    if custom_id:
        slug = slugify(custom_id)
    else:
        # Build nice slug from title and year/city if helpful
        base_slug = slugify(title)
        year_str = ""
        if start_date:
            year_str = start_date[:4]
        elif date:
            m_yr = re.search(r"\b(20\d{2})\b", date)
            if m_yr:
                year_str = m_yr.group(1)

        if year_str and year_str not in base_slug:
            slug = f"{base_slug}-{year_str}"
        else:
            slug = base_slug

    # Build ordered dictionary
    item = {
        "id": slug,
        "title": title,
        "type": event_type,
        "status": status,
        "date": date or "TBD",
        "start_date": start_date or None,
        "location": location,
        "city": city or None,
        "country": country or None,
        "venue": venue,
        "organizer": organizer,
        "description": description,
        "image": image,
        "image_caption": image_caption,
        "products_scanned": products_scanned,
        "participants_count": participants_count,
        "link": link,
        "tags": tag_list if tag_list else None,
    }

    # Ensure key order
    ordered_item = {k: item[k] for k in SP_KEY_ORDER if k in item}
    return ordered_item


def add_scan_party(
    title,
    event_type="upcoming",
    status=None,
    date=None,
    start_date=None,
    location=None,
    venue=None,
    city=None,
    country=None,
    organizer=None,
    description=None,
    image=None,
    image_caption=None,
    products_scanned=None,
    participants_count=None,
    link=None,
    tags=None,
    custom_id=None,
    directory=SCAN_PARTIES_DIR,
    dry_run=False,
    do_compile=False,
    overwrite=False,
    type=None,
    **kwargs,
):
    """Add a scan party item, validate it, write YAML, and optionally recompile."""
    item = build_scan_party_dict(
        title=title,
        event_type=event_type,
        status=status,
        date=date,
        start_date=start_date,
        location=location,
        venue=venue,
        city=city,
        country=country,
        organizer=organizer,
        description=description,
        image=image,
        image_caption=image_caption,
        products_scanned=products_scanned,
        participants_count=participants_count,
        link=link,
        tags=tags,
        custom_id=custom_id,
        type=type,
    )

    slug = item["id"]
    target_filename = f"{slug}.yaml"
    target_filepath = os.path.join(directory, target_filename)

    already_exists = os.path.exists(target_filepath)
    if already_exists and not overwrite and not dry_run:
        return {
            "success": False,
            "error": f"Scan party file '{target_filename}' already exists. Use --overwrite to replace it.",
            "file": os.path.relpath(target_filepath, REPO_ROOT),
        }

    # Validate against compile_scan_parties schema
    errors, warnings = validate_scan_party(item, target_filepath)
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
            "date": item["date"],
            "location": item["location"],
            "venue": item["venue"],
            "event_type": item["type"],
            "status": item["status"],
            "organizer": item.get("organizer"),
            "warnings": warnings,
            "yaml_preview": yaml.safe_dump(item, allow_unicode=True, sort_keys=False),
        }

    # Write file
    os.makedirs(directory, exist_ok=True)
    with open(target_filepath, "w", encoding="utf-8") as out:
        yaml.safe_dump(item, out, allow_unicode=True, sort_keys=False)

    # Recompile if requested
    if do_compile:
        try:
            with contextlib.redirect_stdout(sys.stderr):
                compile_success = compile_scan_parties(check_only=False, verbose=False)
            if not compile_success:
                return {
                    "success": False,
                    "error": "Failed to recompile scan parties dataset after adding event.",
                    "file": os.path.relpath(target_filepath, REPO_ROOT),
                }
        except Exception as e:
            print(f"[WARN] Scan parties compilation warning: {e}", file=sys.stderr)

    return {
        "success": True,
        "id": slug,
        "file": os.path.relpath(target_filepath, REPO_ROOT),
        "full_path": target_filepath,
        "title": item["title"],
        "date": item["date"],
        "location": item["location"],
        "venue": item["venue"],
        "event_type": item["type"],
        "status": item["status"],
        "organizer": item.get("organizer"),
        "warnings": warnings,
    }


def main():
    parser = argparse.ArgumentParser(description="Add or update a scan party in Open Food Facts.")
    parser.add_argument("--id", help="Explicit event ID (slug)")
    parser.add_argument("--title", help="Event title")
    parser.add_argument("--type", choices=["upcoming", "past"], default=None, help="Event timing type")
    parser.add_argument("--status", choices=["upcoming", "completed", "cancelled"], help="Event status")
    parser.add_argument("--date", help="Display date string")
    parser.add_argument("--start-date", help="Start date YYYY-MM-DD")
    parser.add_argument("--location", help="Location (e.g. 'Paris, France')")
    parser.add_argument("--venue", help="Venue / store name")
    parser.add_argument("--city", help="City name")
    parser.add_argument("--country", help="Country code or name")
    parser.add_argument("--organizer", help="Organizer or organization")
    parser.add_argument("--description", help="Description")
    parser.add_argument("--image", help="Image URL")
    parser.add_argument("--image-caption", help="Image caption")
    parser.add_argument("--products-scanned", help="Estimated/actual count of products scanned")
    parser.add_argument("--participants-count", help="Participant count")
    parser.add_argument("--link", help="Event link or registration URL")
    parser.add_argument("--tags", help="Comma-separated tags")

    parser.add_argument("--from-issue-file", help="Path to markdown issue file")
    parser.add_argument("--from-issue-text", help="Raw issue markdown text")
    parser.add_argument("--from-env", action="store_true", help="Read ISSUE_BODY from environment")
    parser.add_argument("--compile", action="store_true", help="Recompile data/scan_parties.json and HTML views")
    parser.add_argument("--overwrite", action="store_true", help="Allow overwriting existing scan party file")
    parser.add_argument("--dry-run", action="store_true", help="Validate without writing files")
    parser.add_argument("--json", action="store_true", help="Output result as JSON")
    parser.add_argument("--output-json", help="Path to write JSON result to")

    args = parser.parse_args()

    raw_data = {}

    raw_text = None
    if args.from_env:
        raw_text = os.environ.get("ISSUE_BODY", "")
    elif args.from_issue_file:
        with open(args.from_issue_file, "r", encoding="utf-8") as f:
            raw_text = f.read()
    elif args.from_issue_text:
        raw_text = args.from_issue_text
    elif not sys.stdin.isatty() and not args.title:
        raw_text = sys.stdin.read()

    if raw_text:
        raw_data = parse_issue_markdown(raw_text)

    # CLI arguments override parsed markdown
    if args.id:
        raw_data["id"] = args.id
    if args.title:
        raw_data["title"] = args.title
    if args.type:
        raw_data["type"] = args.type
    if args.status:
        raw_data["status"] = args.status
    if args.date:
        raw_data["date"] = args.date
    if args.start_date:
        raw_data["start_date"] = args.start_date
    if args.location:
        raw_data["location"] = args.location
    if args.venue:
        raw_data["venue"] = args.venue
    if args.city:
        raw_data["city"] = args.city
    if args.country:
        raw_data["country"] = args.country
    if args.organizer:
        raw_data["organizer"] = args.organizer
    if args.description:
        raw_data["description"] = args.description
    if args.image:
        raw_data["image"] = args.image
    if args.image_caption:
        raw_data["image_caption"] = args.image_caption
    if args.products_scanned:
        raw_data["products_scanned"] = args.products_scanned
    if args.participants_count:
        raw_data["participants_count"] = args.participants_count
    if args.link:
        raw_data["link"] = args.link
    if args.tags:
        raw_data["tags"] = args.tags

    if not raw_data.get("title"):
        res = {
            "success": False,
            "error": "Missing required field: title. Please provide an event title.",
        }
        if args.json or args.output_json:
            if args.output_json:
                with open(args.output_json, "w", encoding="utf-8") as out:
                    json.dump(res, out, indent=2)
            if args.json:
                print(json.dumps(res, indent=2))
        else:
            print(f"❌ Error: {res['error']}", file=sys.stderr)
        sys.exit(1)

    result = add_scan_party(
        title=raw_data.get("title"),
        event_type=raw_data.get("type", "upcoming"),
        status=raw_data.get("status"),
        date=raw_data.get("date"),
        start_date=raw_data.get("start_date"),
        location=raw_data.get("location"),
        venue=raw_data.get("venue"),
        city=raw_data.get("city"),
        country=raw_data.get("country"),
        organizer=raw_data.get("organizer"),
        description=raw_data.get("description"),
        image=raw_data.get("image"),
        image_caption=raw_data.get("image_caption"),
        products_scanned=raw_data.get("products_scanned"),
        participants_count=raw_data.get("participants_count"),
        link=raw_data.get("link"),
        tags=raw_data.get("tags"),
        custom_id=raw_data.get("id"),
        dry_run=args.dry_run,
        do_compile=args.compile,
        overwrite=args.overwrite,
    )

    if args.output_json:
        with open(args.output_json, "w", encoding="utf-8") as out:
            json.dump(result, out, indent=2)

    if args.json:
        print(json.dumps(result, indent=2))
    elif result["success"]:
        mode_str = "[DRY-RUN] Would create" if result.get("dry_run") else "Successfully created"
        print(f"✅ {mode_str} scan party YAML: {result['file']}")
    else:
        print(f"❌ Error: {result['error']}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
