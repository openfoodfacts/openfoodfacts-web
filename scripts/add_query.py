#!/usr/bin/env python3
"""
Add or update a query/graph in the Open Food Facts Useful Queries directory.

This script parses GitHub issue bodies submitted via `.github/ISSUE_TEMPLATE/new-graph-query.yml`
or markdown templates, validates the fields against the schema, writes the YAML file to
`data/queries/<id>.yaml`, and optionally recompiles `data/queries.json` and HTML pages.

Usage:
    # From GitHub issue environment variables:
    python3 scripts/add_query.py --from-env --compile --json

    # From issue file:
    python3 scripts/add_query.py --from-issue-file issue.md --compile

    # Directly via CLI flags:
    python3 scripts/add_query.py \
        --title "Sugars vs Additives in Yogurts" \
        --url "https://world.openfoodfacts.org/cgi/search.pl?action=process&tagtype_0=categories&tag_contains_0=contains&tag_0=yogurts&axis_x=sugars&axis_y=additives_n&generate_graph_scatter_plot=1" \
        --description "Scatter plot showing sugar content vs additives in yogurts" \
        --topic "dairy" \
        --query-type "scatter_plot" \
        --geography "world" \
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
QUERIES_DIR = os.path.join(DATA_DIR, "queries")

try:
    from compile_queries import compile_queries, validate_query, VALID_TOPICS, VALID_QUERY_TYPES, GEO_NAMES
except ImportError:
    sys.path.insert(0, os.path.dirname(__file__))
    from compile_queries import compile_queries, validate_query, VALID_TOPICS, VALID_QUERY_TYPES, GEO_NAMES


def slugify(text, max_len=60):
    """Convert text into a clean alphanumeric slug with hyphens."""
    if not text:
        return ""
    text = text.lower().strip()
    text = text.replace("'", "").replace("’", "")
    text = re.sub(r"[^a-z0-9_-]+", "-", text)
    text = re.sub(r"-+", "-", text)
    slug = text.strip("-")
    return slug[:max_len].rstrip("-")


def clean_field_value(val):
    """Normalize and clean an issue form string."""
    if val is None:
        return ""
    s = str(val).strip()
    if s.lower() in ("_no response_", "none", "n/a", "null"):
        return ""
    s = re.sub(r"<!--.*?-->", "", s, flags=re.DOTALL).strip()
    return s


def clean_dropdown(val):
    """Extract code from dropdown label like 'beverages (🥤 Beverages / Boissons)' -> 'beverages'."""
    val = clean_field_value(val)
    if not val:
        return ""
    if " " in val:
        val = val.split(" ")[0].strip()
    return val.lower()


def clean_url(url):
    """Normalize and clean a URL."""
    url = clean_field_value(url)
    if not url:
        return ""
    md_match = re.search(r"\((https?://[^\s)]+)\)", url)
    if md_match:
        url = md_match.group(1).strip()
    url = url.strip("<>").strip()
    return url


def parse_query_params_from_url(url_str):
    """
    Extract query parameters, axis_x, axis_y, and tags from an Open Food Facts query URL.
    """
    params = {}
    axis_x = None
    axis_y = None
    tags_combined = []

    try:
        parsed = urllib.parse.urlparse(url_str)
        qs = urllib.parse.parse_qs(parsed.query, keep_blank_values=False)
        for k, vals in qs.items():
            if not vals:
                continue
            val = vals[0]
            params[k] = val
            if k == "axis_x":
                axis_x = val
                tags_combined.append(f"axis_x:{val}")
            elif k == "axis_y":
                axis_y = val
                tags_combined.append(f"axis_y:{val}")

        # Check tagtype_0 / tag_0
        idx = 0
        while True:
            tt_key = f"tagtype_{idx}"
            t_key = f"tag_{idx}"
            if t_key in params:
                tt = params.get(tt_key, "tag")
                if tt == "categories": tt = "category"
                elif tt == "labels": tt = "label"
                elif tt == "ingredients": tt = "ingredient"
                elif tt == "origins": tt = "origin"
                t_val = params[t_key]
                tags_combined.append(f"{tt}:{t_val}")
                idx += 1
            else:
                break

        # Check series switches
        for k in params:
            if k.startswith("series_") and params[k] in ("on", "1", "true"):
                series_name = k[len("series_"):]
                tags_combined.append(f"series:{series_name}")
    except Exception:
        pass

    return params, axis_x, axis_y, tags_combined


def parse_issue_markdown(text):
    """
    Parses GitHub Issue Form body submitted via new-graph-query.yml.
    """
    data = {}
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

        if "title" in header or "query / graph title" in header:
            data["title"] = content.splitlines()[0].strip() if content else ""
        elif "url" in header or "query url" in header:
            data["url"] = clean_url(content.splitlines()[0].strip()) if content else ""
        elif "description" in header or "insights" in header:
            data["description"] = content
        elif "topic" in header or "food topic" in header:
            data["topic"] = clean_dropdown(content)
        elif "query_type" in header or "visualization" in header or "format" in header:
            data["query_type"] = clean_dropdown(content)
        elif "geography" in header or "geographic scope" in header or "country" in header:
            data["geography"] = clean_dropdown(content)
        elif "author" in header or "contributor" in header:
            data["author"] = content.splitlines()[0].strip() if content else ""
        elif "axis_x" in header or "x-axis" in header:
            data["axis_x"] = content.splitlines()[0].strip() if content else ""
        elif "axis_y" in header or "y-axis" in header:
            data["axis_y"] = content.splitlines()[0].strip() if content else ""
        elif "keywords" in header or "tags" in header:
            data["keywords"] = [k.strip() for k in content.split(",") if k.strip()]

    return data


def build_query_dict(parsed_data, custom_id=None):
    """
    Constructs a clean dictionary ready for YAML output.
    """
    title = clean_field_value(parsed_data.get("title", ""))
    url = clean_url(parsed_data.get("url", ""))
    desc = clean_field_value(parsed_data.get("description", ""))
    topic = clean_dropdown(parsed_data.get("topic", "nutrition"))
    q_type = clean_dropdown(parsed_data.get("query_type", "scatter_plot"))

    geo = clean_dropdown(parsed_data.get("geography", "world"))
    if not geo:
        geo = "world"
    geographies = parsed_data.get("geographies")
    if not geographies:
        geographies = [geo]
    elif isinstance(geographies, str):
        geographies = [clean_dropdown(g) for g in geographies.split(",") if clean_dropdown(g)]

    author = clean_field_value(parsed_data.get("author", ""))
    if not author:
        author = "Open Food Facts Community"

    qid = custom_id or slugify(title)
    if not qid:
        qid = "custom-query"

    # Extract URL params and tags
    url_params, detected_x, detected_y, detected_tags = parse_query_params_from_url(url)

    axis_x = clean_field_value(parsed_data.get("axis_x", "")) or detected_x
    axis_y = clean_field_value(parsed_data.get("axis_y", "")) or detected_y

    keywords = parsed_data.get("keywords", [])
    if isinstance(keywords, str):
        keywords = [k.strip() for k in keywords.split(",") if k.strip()]

    tags_combined = parsed_data.get("tags_combined", [])
    if not tags_combined:
        tags_combined = detected_tags

    query_dict = {
        "id": qid,
        "title": title,
        "description": desc,
        "author": author,
        "topic": topic,
        "geographies": geographies,
        "query_type": q_type,
    }

    if axis_x:
        query_dict["axis_x"] = axis_x
    if axis_y:
        query_dict["axis_y"] = axis_y

    if tags_combined:
        query_dict["tags_combined"] = tags_combined

    if url_params:
        query_dict["parameters"] = url_params

    query_dict["url"] = url
    query_dict["featured"] = bool(parsed_data.get("featured", False))

    if keywords:
        query_dict["keywords"] = keywords

    return query_dict


def add_query(query_dict, queries_dir=QUERIES_DIR, dry_run=False):
    """
    Validates and writes query dictionary to YAML file.
    """
    qid = query_dict.get("id")
    if not qid:
        return False, ["Missing query id"], None

    filename = f"{qid}.yaml"
    filepath = os.path.join(queries_dir, filename)

    errors, warnings = validate_query(query_dict, filepath)
    if errors:
        return False, errors, None

    if dry_run:
        return True, warnings, filepath

    os.makedirs(queries_dir, exist_ok=True)
    with open(filepath, "w", encoding="utf-8") as f:
        yaml.dump(query_dict, f, default_flow_style=False, sort_keys=False, allow_unicode=True)

    return True, warnings, filepath


def main():
    parser = argparse.ArgumentParser(description="Add or update an Open Food Facts graph/query.")
    parser.add_argument("--from-env", action="store_true", help="Parse from ISSUE_BODY env var")
    parser.add_argument("--from-issue-file", help="Path to markdown issue body file")
    parser.add_argument("--id", help="Explicit query id/slug")
    parser.add_argument("--title", help="Query or graph title")
    parser.add_argument("--url", help="Open Food Facts search/graph URL")
    parser.add_argument("--description", help="Description of the query")
    parser.add_argument("--topic", help="Food topic (beverages, dairy, etc.)")
    parser.add_argument("--query-type", help="query_type (scatter_plot, bar_chart, etc.)")
    parser.add_argument("--geography", help="Primary geographic scope (world, fr, etc.)")
    parser.add_argument("--author", help="Author name")
    parser.add_argument("--axis-x", help="X-axis metric")
    parser.add_argument("--axis-y", help="Y-axis metric")
    parser.add_argument("--keywords", help="Comma-separated keywords")
    parser.add_argument("--featured", action="store_true", help="Mark as featured")
    parser.add_argument("--compile", action="store_true", help="Recompile dataset & HTML after adding")
    parser.add_argument("--dry-run", action="store_true", help="Validate without writing file")
    parser.add_argument("--json", action="store_true", help="Output JSON result")
    parser.add_argument("--output-json", help="Write JSON result to file")

    args = parser.parse_args()

    parsed_data = {}
    if args.from_env:
        issue_body = os.environ.get("ISSUE_BODY", "")
        parsed_data = parse_issue_markdown(issue_body)
    elif args.from_issue_file:
        with open(args.from_issue_file, "r", encoding="utf-8") as f:
            parsed_data = parse_issue_markdown(f.read())

    # Override from CLI flags if specified
    if args.title: parsed_data["title"] = args.title
    if args.url: parsed_data["url"] = args.url
    if args.description: parsed_data["description"] = args.description
    if args.topic: parsed_data["topic"] = args.topic
    if args.query_type: parsed_data["query_type"] = args.query_type
    if args.geography: parsed_data["geography"] = args.geography
    if args.author: parsed_data["author"] = args.author
    if args.axis_x: parsed_data["axis_x"] = args.axis_x
    if args.axis_y: parsed_data["axis_y"] = args.axis_y
    if args.keywords: parsed_data["keywords"] = [k.strip() for k in args.keywords.split(",") if k.strip()]
    if args.featured: parsed_data["featured"] = True

    query_dict = build_query_dict(parsed_data, custom_id=args.id)

    success, issues, target_path = add_query(query_dict, QUERIES_DIR, dry_run=args.dry_run)

    res = {
        "success": success,
        "id": query_dict.get("id"),
        "title": query_dict.get("title"),
        "topic": query_dict.get("topic"),
        "query_type": query_dict.get("query_type"),
        "file": os.path.relpath(target_path, REPO_ROOT) if target_path else None,
        "issues": issues,
    }

    if success and args.compile and not args.dry_run:
        compile_success = compile_queries(check_only=False, verbose=False)
        res["compiled"] = compile_success

    if args.output_json:
        with open(args.output_json, "w", encoding="utf-8") as f:
            json.dump(res, f, indent=2)

    if args.json:
        print(json.dumps(res, indent=2))
    else:
        if success:
            print(f"✅ Successfully {'validated' if args.dry_run else 'saved'} query: {query_dict.get('id')}")
            if target_path and not args.dry_run:
                print(f"   File: {target_path}")
        else:
            print(f"❌ Failed to add query: {issues}", file=sys.stderr)

    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
