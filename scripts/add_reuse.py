#!/usr/bin/env python3
"""
Add or update a reuse in the Open Food Facts ecosystem database.

This script parses GitHub issue bodies submitted via `.github/ISSUE_TEMPLATE/new-reuse.yml`
or markdown templates, validates the fields against the schema, writes the YAML file to
`data/reuses/<id>.yaml`, and optionally recompiles `data/reuses.json` and showcase pages.

Usage:
    # From GitHub issue environment variables:
    python3 scripts/add_reuse.py --from-env --compile --json

    # From issue file or text:
    python3 scripts/add_reuse.py --from-issue-file issue.md --compile

    # Directly via CLI flags:
    python3 scripts/add_reuse.py \
        --name "FoodScanner" \
        --tagline "Instant nutrition scanner" \
        --description "Scan barcodes to analyze nutrition..." \
        --theme nutrition \
        --website "https://foodscanner.example.com" \
        --compile
"""

import argparse
import json
import os
import re
import sys
import urllib.parse
import yaml

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
DATA_DIR = os.path.join(REPO_ROOT, "data")
REUSES_DIR = os.path.join(DATA_DIR, "reuses")

# Import compilation and validation logic
try:
    from compile_reuses import compile_reuses, validate_reuse, VALID_THEMES, VALID_PROJECTS
except ImportError:
    sys.path.insert(0, os.path.dirname(__file__))
    from compile_reuses import compile_reuses, validate_reuse, VALID_THEMES, VALID_PROJECTS


def slugify(text):
    """Convert text into a clean alphanumeric slug with hyphens."""
    if not text:
        return ""
    text = text.lower().strip()
    # Replace non-alphanumeric with hyphens
    text = re.sub(r"[^a-z0-9_-]+", "-", text)
    text = re.sub(r"-+", "-", text)
    return text.strip("-")


def clean_dropdown(val):
    """
    Extract key from dropdown options like:
    'nutrition (Nutrition & General Health)' -> 'nutrition'
    'openfoodfacts (Open Food Facts)' -> 'openfoodfacts'
    """
    if not val:
        return ""
    val = val.strip()
    if "(" in val:
        val = val.split("(", 1)[0].strip()
    return val.strip().lower()


def parse_bool(val, default=False):
    """Parse string representation of boolean."""
    if val is None:
        return default
    if isinstance(val, bool):
        return val
    s = str(val).strip().lower()
    if s in ("_no response_", "none", "n/a", "null", ""):
        return default
    if any(pos in s for pos in ("yes", "true", "1", "oui", "si", "ja", "[x]")):
        return True
    if any(neg in s for neg in ("no", "false", "0", "non", "nein")):
        return False
    return default


def clean_url(url):
    """Normalize and validate a URL."""
    if not url:
        return None
    url = str(url).strip()
    if url.lower() in ("_no response_", "none", "n/a", "null", ""):
        return None
    # Strip markdown link format [title](url) or angle brackets <url>
    md_match = re.search(r"\((https?://[^\s)]+)\)", url)
    if md_match:
        url = md_match.group(1).strip()
    url = url.strip("<>").strip()
    if not url.startswith("http://") and not url.startswith("https://"):
        return None
    return url


def extract_domain(url):
    """Extract domain from a website URL."""
    if not url:
        return None
    try:
        parsed = urllib.parse.urlparse(url)
        netloc = parsed.netloc.lower()
        if netloc.startswith("www."):
            netloc = netloc[4:]
        return netloc or None
    except Exception:
        return None


def parse_issue_markdown(text):
    """
    Parses GitHub Issue Form / Markdown body submitted via new-reuse.yml.
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
        header = lines[0].strip().lower()
        content = "\n".join(lines[1:]).strip()

        # Remove HTML comments if any
        content = re.sub(r"<!--.*?-->", "", content, flags=re.DOTALL).strip()
        if content.lower() in ("_no response_", "none", "n/a", "null"):
            content = ""

        # Map header keywords to keys (check specific/compound matches first)
        if "open source" in header:
            data["open_source"] = parse_bool(content, default=False)
        elif "contribute data" in header or "contributes data" in header:
            data["contributes_data"] = parse_bool(content, default=False)
        elif "photo" in header:
            data["contributes_photos"] = parse_bool(content, default=False)
        elif "odbl" in header:
            data["odbl_compliant"] = parse_bool(content, default=True)
        elif "license" in header:
            data["license"] = content.splitlines()[0].strip() if content else ""
        elif "country code" in header:
            data["country"] = content.splitlines()[0].strip().lower() if content else ""
        elif "country" in header or "territory" in header:
            data["country_label"] = content.splitlines()[0].strip() if content else ""
        elif "application" in header or "reuse name" in header or "app name" in header or header.startswith("name"):
            data["name"] = content.splitlines()[0].strip() if content else ""
        elif "tagline" in header or "summary" in header:
            data["tagline"] = content.splitlines()[0].strip() if content else ""
        elif "description" in header:
            data["description"] = content.strip()
        elif "primary theme" in header or "main theme" in header or header == "theme":
            data["theme"] = clean_dropdown(content)
        elif "secondary theme" in header or "other theme" in header:
            data["secondary_themes"] = content
        elif "project" in header:
            data["project"] = clean_dropdown(content)
        elif "play store" in header or "google play" in header:
            data["play_store"] = clean_url(content)
        elif "app store" in header or "apple app" in header or "ios" in header:
            data["app_store"] = clean_url(content)
        elif "f-droid" in header or "fdroid" in header:
            data["fdroid"] = clean_url(content)
        elif "source code" in header or "github" in header or "repository" in header:
            data["github"] = clean_url(content)
        elif "website" in header or "landing page" in header or header == "url":
            data["website"] = clean_url(content)
        elif "icon" in header or "logo" in header:
            data["icon_url"] = clean_url(content)
        elif "keyword" in header or "tag" in header:
            data["keywords"] = content.strip()
        elif "check" in header or "confirm" in header:
            pass

    return data


def format_reuse_dict(raw_data, reuse_id=None):
    """
    Constructs the canonical dictionary structure matching data/reuses/*.yaml
    """
    name = (raw_data.get("name") or "").strip()
    r_id = reuse_id or raw_data.get("id") or slugify(name)

    tagline = (raw_data.get("tagline") or "").strip()
    description = (raw_data.get("description") or "").strip()

    # Theme normalization
    theme = clean_dropdown(raw_data.get("theme") or "nutrition")
    if theme not in VALID_THEMES:
        # Fallback to closest or default
        theme = "nutrition"

    # Themes list
    themes = [theme]
    secondary_raw = raw_data.get("secondary_themes") or ""
    if secondary_raw:
        sec_list = [clean_dropdown(s) for s in re.split(r"[,;\n]+", secondary_raw)]
        for s in sec_list:
            if s and s in VALID_THEMES and s not in themes:
                themes.append(s)

    # Project normalization
    project = clean_dropdown(raw_data.get("project") or "openfoodfacts")
    if project not in VALID_PROJECTS:
        project = "openfoodfacts"

    # Country normalization
    country = (raw_data.get("country") or "global").strip().lower()
    if len(country) > 3 and country != "global":
        country = country[:3]
    country_label = (raw_data.get("country_label") or ("Worldwide" if country == "global" else country.upper())).strip()

    # Links
    website = clean_url(raw_data.get("website"))
    play_store = clean_url(raw_data.get("play_store"))
    app_store = clean_url(raw_data.get("app_store"))
    fdroid = clean_url(raw_data.get("fdroid"))
    github = clean_url(raw_data.get("github"))

    domain = extract_domain(website) or extract_domain(github)

    # Booleans
    contributes_data = parse_bool(raw_data.get("contributes_data"), default=False)
    contributes_photos = parse_bool(raw_data.get("contributes_photos"), default=False)
    odbl_compliant = parse_bool(raw_data.get("odbl_compliant"), default=True)
    open_source = parse_bool(raw_data.get("open_source"), default=False)
    featured = parse_bool(raw_data.get("featured"), default=False)
    donates_to_ngo = parse_bool(raw_data.get("donates_to_ngo"), default=False)

    license_name = raw_data.get("license") or ("Open Source" if open_source else "Proprietary")

    # Keywords
    user_keywords = raw_data.get("keywords") or ""
    kw_tokens = [t.lower().strip() for t in re.split(r"[,;\s]+", user_keywords) if t.strip()]
    # Enrich with default tokens
    for token in [r_id, slugify(name), theme, country]:
        if token and token not in kw_tokens:
            kw_tokens.append(token)
    keywords_str = " ".join(kw_tokens)

    # Cached icon check
    cached_icon = None
    icon_rel_path = f"/images/reuses/icons/{r_id}.png"
    icon_abs_path = os.path.join(REPO_ROOT, "html", "images", "reuses", "icons", f"{r_id}.png")
    if os.path.exists(icon_abs_path):
        cached_icon = icon_rel_path

    icon_url = clean_url(raw_data.get("icon_url"))

    item = {
        "id": r_id,
        "name": name,
        "tagline": tagline,
        "description": description,
        "theme": theme,
        "themes": themes,
        "project": project,
        "country": country,
        "country_label": country_label,
        "domain": domain,
        "website": website,
        "play_store": play_store,
        "app_store": app_store,
        "fdroid": fdroid,
        "github": github,
        "contributes_data": contributes_data,
        "contributes_photos": contributes_photos,
        "odbl_compliant": odbl_compliant,
        "open_source": open_source,
        "license": license_name,
        "featured": featured,
        "keywords": keywords_str,
        "cached_icon": cached_icon,
        "donates_to_ngo": donates_to_ngo,
    }

    if icon_url:
        item["icon_url"] = icon_url

    # Preserve numeric stats if provided
    if raw_data.get("installs"):
        item["installs"] = str(raw_data.get("installs"))
    if raw_data.get("installs_numeric") is not None:
        try:
            item["installs_numeric"] = int(raw_data.get("installs_numeric"))
        except (ValueError, TypeError):
            pass
    if raw_data.get("rating") is not None:
        try:
            item["rating"] = float(raw_data.get("rating"))
        except (ValueError, TypeError):
            pass

    return item


def add_reuse(raw_data, reuse_id=None, overwrite=False, dry_run=False, do_compile=False):
    """
    Validates and writes a reuse YAML file in data/reuses/<id>.yaml.
    """
    item = format_reuse_dict(raw_data, reuse_id=reuse_id)
    r_id = item["id"]

    if not r_id:
        return {"success": False, "error": "Application name or id cannot be empty."}
    if not item["name"]:
        return {"success": False, "error": "Application name cannot be empty."}
    if not item["tagline"]:
        return {"success": False, "error": "Application tagline cannot be empty."}

    os.makedirs(REUSES_DIR, exist_ok=True)
    target_filename = f"{r_id}.yaml"
    target_filepath = os.path.join(REUSES_DIR, target_filename)
    rel_filepath = os.path.relpath(target_filepath, REPO_ROOT)

    already_exists = os.path.exists(target_filepath)
    if already_exists and not overwrite:
        # Load existing item to preserve fields if partial update
        try:
            with open(target_filepath, "r", encoding="utf-8") as f:
                existing_item = yaml.safe_load(f)
                if isinstance(existing_item, dict):
                    # Merge existing fields with new values
                    for k, v in existing_item.items():
                        if k not in item or item[k] is None:
                            item[k] = v
        except Exception:
            pass

    # Validate item
    errors, warnings = validate_reuse(item, target_filepath)
    if errors:
        return {
            "success": False,
            "error": f"Validation errors: {'; '.join(errors)}",
            "warnings": warnings,
            "file": rel_filepath
        }

    if dry_run:
        return {
            "success": True,
            "id": r_id,
            "name": item["name"],
            "theme": item["theme"],
            "file": rel_filepath,
            "is_update": already_exists,
            "dry_run": True,
            "warnings": warnings
        }

    # Write YAML file
    with open(target_filepath, "w", encoding="utf-8") as f:
        yaml.safe_dump(item, f, sort_keys=False, allow_unicode=True)

    # Optionally recompile
    if do_compile:
        compile_success = compile_reuses(check_only=False, verbose=False)
        if not compile_success:
            return {
                "success": False,
                "error": "Failed to recompile reuses after adding YAML.",
                "file": rel_filepath
            }

    return {
        "success": True,
        "id": r_id,
        "name": item["name"],
        "tagline": item["tagline"],
        "theme": item["theme"],
        "project": item["project"],
        "website": item.get("website") or item.get("github") or item.get("play_store") or item.get("app_store"),
        "file": rel_filepath,
        "is_update": already_exists,
        "warnings": warnings
    }


def main():
    parser = argparse.ArgumentParser(description="Add or update a reuse in the Open Food Facts database.")
    parser.add_argument("--id", help="Explicit reuse ID (slug)")
    parser.add_argument("--name", help="Application / reuse name")
    parser.add_argument("--tagline", help="Tagline / one-line summary")
    parser.add_argument("--description", help="Detailed description")
    parser.add_argument("--theme", help="Primary theme (e.g. nutrition, environment, allergies)")
    parser.add_argument("--secondary-themes", help="Secondary themes (comma-separated)")
    parser.add_argument("--project", default="openfoodfacts", help="Open Food Facts project")
    parser.add_argument("--website", help="Website URL")
    parser.add_argument("--play-store", help="Google Play Store URL")
    parser.add_argument("--app-store", help="Apple App Store URL")
    parser.add_argument("--fdroid", help="F-Droid URL")
    parser.add_argument("--github", help="GitHub / Source code URL")
    parser.add_argument("--country", help="Country ISO code (3 letters or 'global')")
    parser.add_argument("--country-label", help="Country / territory label (e.g. France, Worldwide)")
    parser.add_argument("--license", help="License name (e.g. Proprietary, GPLv3, MIT)")
    parser.add_argument("--open-source", action="store_true", help="Flag as Open Source")
    parser.add_argument("--contributes-data", action="store_true", help="Flag as contributing data back")
    parser.add_argument("--contributes-photos", action="store_true", help="Flag as contributing photos back")
    parser.add_argument("--odbl-compliant", action="store_true", default=True, help="Flag as ODbL compliant")
    parser.add_argument("--icon-url", help="App icon or logo URL")
    parser.add_argument("--keywords", help="Keywords / search tags")
    parser.add_argument("--from-issue-file", help="Path to markdown issue file")
    parser.add_argument("--from-issue-text", help="Raw issue markdown text")
    parser.add_argument("--from-env", action="store_true", help="Read ISSUE_BODY from environment")
    parser.add_argument("--compile", action="store_true", help="Recompile data/reuses.json and showcase pages")
    parser.add_argument("--overwrite", action="store_true", help="Allow overwriting existing reuse file")
    parser.add_argument("--dry-run", action="store_true", help="Validate without writing files")
    parser.add_argument("--json", action="store_true", help="Output result as JSON")

    args = parser.parse_args()

    raw_data = {}

    # Check input source
    raw_text = None
    if args.from_env:
        raw_text = os.environ.get("ISSUE_BODY", "")
    elif args.from_issue_file:
        with open(args.from_issue_file, "r", encoding="utf-8") as f:
            raw_text = f.read()
    elif args.from_issue_text:
        raw_text = args.from_issue_text
    elif not sys.stdin.isatty() and not args.name:
        raw_text = sys.stdin.read()

    if raw_text:
        raw_data = parse_issue_markdown(raw_text)

    # CLI arguments override parsed markdown
    if args.id:
        raw_data["id"] = args.id
    if args.name:
        raw_data["name"] = args.name
    if args.tagline:
        raw_data["tagline"] = args.tagline
    if args.description:
        raw_data["description"] = args.description
    if args.theme:
        raw_data["theme"] = args.theme
    if args.secondary_themes:
        raw_data["secondary_themes"] = args.secondary_themes
    if args.project:
        raw_data["project"] = args.project
    if args.website:
        raw_data["website"] = args.website
    if args.play_store:
        raw_data["play_store"] = args.play_store
    if args.app_store:
        raw_data["app_store"] = args.app_store
    if args.fdroid:
        raw_data["fdroid"] = args.fdroid
    if args.github:
        raw_data["github"] = args.github
    if args.country:
        raw_data["country"] = args.country
    if args.country_label:
        raw_data["country_label"] = args.country_label
    if args.license:
        raw_data["license"] = args.license
    if args.open_source:
        raw_data["open_source"] = True
    if args.contributes_data:
        raw_data["contributes_data"] = True
    if args.contributes_photos:
        raw_data["contributes_photos"] = True
    if args.icon_url:
        raw_data["icon_url"] = args.icon_url
    if args.keywords:
        raw_data["keywords"] = args.keywords

    if not raw_data.get("name"):
        err_msg = "Error: Application name must be provided via issue body or --name."
        if args.json:
            print(json.dumps({"success": False, "error": err_msg}, indent=2))
        else:
            print(err_msg, file=sys.stderr)
        sys.exit(1)

    result = add_reuse(
        raw_data=raw_data,
        reuse_id=args.id,
        overwrite=args.overwrite,
        dry_run=args.dry_run,
        do_compile=args.compile
    )

    if args.json:
        print(json.dumps(result, indent=2))
    else:
        if result.get("success"):
            action = "Updated" if result.get("is_update") else "Added"
            print(f"✅ Successfully {action} reuse in {result.get('file')}")
            print(f"   ID: {result.get('id')}")
            print(f"   Name: {result.get('name')}")
            print(f"   Theme: {result.get('theme')}")
            print(f"   Project: {result.get('project')}")
        else:
            print(f"❌ Error adding reuse: {result.get('error')}", file=sys.stderr)
            sys.exit(1)


if __name__ == "__main__":
    main()
