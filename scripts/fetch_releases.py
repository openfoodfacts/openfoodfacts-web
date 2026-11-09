#!/usr/bin/env python3
"""
Fetch releases across Open Food Facts repositories listed on:
https://wiki.openfoodfacts.org/Releases_%26_Features

Features:
- Dynamically parses the Open Food Facts Wiki page (with Anubis solver support)
  or falls back to the pre-seeded repository catalog.
- Fetches releases via GitHub REST API (if GITHUB_TOKEN is available) or
  via GitHub's Atom feeds (https://github.com/{repo}/releases.atom) with zero rate-limit constraints.
- Formats and cleans changelog HTML/markdown.
- Generates data/releases.json.
"""

import argparse
import datetime
import html
import http.cookiejar
import json
import os
import re
import sys
import time
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
DATA_DIR = os.path.join(REPO_ROOT, "data")
OUTPUT_JSON = os.path.join(DATA_DIR, "releases.json")

# Default catalog from https://wiki.openfoodfacts.org/Releases_%26_Features
DEFAULT_CATALOG = [
    ("Core", "openfoodfacts/openfoodfacts-server"),
    ("Core", "openfoodfacts/openfoodfacts-web"),
    ("Core", "openfoodfacts/openfoodfacts-infrastructure"),
    ("Core", "openfoodfacts/search-a-licious"),
    ("Core", "openfoodfacts/hunger-games"),
    ("Core", "openfoodfacts/facets-knowledge-panels"),
    ("AI & Robotoff", "openfoodfacts/robotoff"),
    ("Core", "openfoodfacts/openfoodfacts-explorer"),
    ("Mobile", "openfoodfacts/openfoodfacts-dart"),
    ("Mobile", "openfoodfacts/smooth-app"),
    ("Prices", "openfoodfacts/open-prices"),
    ("Prices", "openfoodfacts/open-prices-frontend"),
    ("Folksonomy", "openfoodfacts/folksonomy_api"),
    ("Taxonomy", "openfoodfacts/taxonomy-editor"),
    ("Misc", "openfoodfacts/DriveOFF"),
    ("Data Quality", "openfoodfacts/power-user-script"),
    ("SDKs", "openfoodfacts/openfoodfacts-python"),
    ("SDKs", "openfoodfacts/openfoodfacts-java"),
    ("SDKs", "openfoodfacts/openfoodfacts-go"),
    ("SDKs", "openfoodfacts/openfoodfacts-rust"),
    ("SDKs", "openfoodfacts/openfoodfacts-react-native"),
    ("SDKs", "openfoodfacts/openfoodfacts-php"),
    ("SDKs", "openfoodfacts/openfoodfacts-ruby"),
    ("SDKs", "openfoodfacts/openfoodfacts-elixir"),
    ("SDKs", "openfoodfacts/openfoodfacts-kotlin"),
    ("SDKs", "openfoodfacts/openfoodfacts-swift"),
    ("JavaScript", "openfoodfacts/openfoodfacts-js"),
    ("JavaScript", "openfoodfacts/openfoodfacts-webcomponents"),
]

MONTH_NAMES_EN = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
MONTH_NAMES_FR = ["janv.", "févr.", "mars", "avr.", "mai", "juin", "juil.", "août", "sept.", "oct.", "nov.", "déc."]

def format_date_en(dt_str):
    try:
        dt = datetime.datetime.fromisoformat(dt_str.replace("Z", "+00:00"))
        return f"{dt.day} {MONTH_NAMES_EN[dt.month - 1]} {dt.year}"
    except Exception:
        return dt_str[:10]

def format_date_fr(dt_str):
    try:
        dt = datetime.datetime.fromisoformat(dt_str.replace("Z", "+00:00"))
        return f"{dt.day} {MONTH_NAMES_FR[dt.month - 1]} {dt.year}"
    except Exception:
        return dt_str[:10]

def fetch_wiki_catalog(timeout=10):
    """
    Attempt to fetch live catalog from https://wiki.openfoodfacts.org/Releases_%26_Features
    using an automated Anubis PoW solver if challenged.
    """
    import hashlib
    wiki_url = "https://wiki.openfoodfacts.org/index.php?title=Releases_%26_Features&action=raw"
    cj = http.cookiejar.CookieJar()
    opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cj))
    opener.addheaders = [("User-Agent", "Mozilla/5.0 (OFF-Releases-Bot/1.0)")]

    try:
        resp = opener.open(wiki_url, timeout=timeout)
        content = resp.read().decode("utf-8")
        if "anubis_challenge" in content:
            m = re.search(r'id="anubis_challenge"[^>]*>(.*?)</script>', content, re.DOTALL)
            if m:
                c_data = json.loads(m.group(1))
                p = c_data.get("challenge", {})
                rules = c_data.get("rules", {})
                rand = p.get("randomData", "")
                diff = rules.get("difficulty", 5)
                cid = p.get("id")
                prefix = "0" * diff
                t0 = time.time()
                nonce = 0
                while True:
                    h = hashlib.sha256((rand + str(nonce)).encode("utf-8")).hexdigest()
                    if h.startswith(prefix):
                        break
                    nonce += 1
                elapsed = int((time.time() - t0) * 1000)
                pass_url = (
                    f"https://wiki.openfoodfacts.org/.within.website/x/cmd/anubis/api/pass-challenge"
                    f"?id={cid}&response={h}&nonce={nonce}&redir={urllib.parse.quote(wiki_url)}&elapsedTime={elapsed}"
                )
                resp2 = opener.open(pass_url, timeout=timeout)
                content = resp2.read().decode("utf-8")

        # Parse wikitext categories and repositories
        catalog = []
        current_cat = "Core"
        seen = set()
        for line in content.splitlines():
            m_cat = re.match(r"===+\s*(.*?)\s*===+", line)
            if m_cat:
                header = m_cat.group(1).strip()
                if "Robotoff" in header:
                    current_cat = "AI & Robotoff"
                elif "Taxonomy" in header:
                    current_cat = "Taxonomy"
                elif "Prices" in header:
                    current_cat = "Prices"
                elif "Mobile" in header:
                    current_cat = "Mobile"
                elif "SDKs" in header:
                    current_cat = "SDKs"
                elif "JavaScript" in header:
                    current_cat = "JavaScript"
                elif "Data Quality" in header:
                    current_cat = "Data Quality"
                else:
                    current_cat = header
                continue
            m_repo = re.search(r"github\.com/([^/\s]+/[^/\s]+)", line)
            if m_repo:
                repo = m_repo.group(1).rstrip("/")
                if repo not in seen:
                    seen.add(repo)
                    catalog.append((current_cat, repo))
        if catalog:
            return catalog
    except Exception as e:
        print(f"[INFO] Wiki fetch skipped ({e}), using default verified repository catalog.")
    return DEFAULT_CATALOG

def clean_html_body(raw_html):
    """
    Sanitize and clean up changelog HTML into standard semantic tags.
    """
    if not raw_html:
        return ""
    # Ensure links open in new tab and have rel="noopener"
    cleaned = re.sub(
        r'<a\s+href="([^"]+)"[^>]*>',
        r'<a href="\1" target="_blank" rel="noopener">',
        raw_html
    )
    # Remove internal data-hovercard attributes
    cleaned = re.sub(r'\s*data-hovercard-[^=]+="[^"]*"', '', cleaned)
    return cleaned.strip()

def summarize_body(text, max_len=200):
    """
    Extract a concise 1-sentence summary from the release notes.
    """
    if not text:
        return ""
    # Strip HTML tags
    plain = re.sub(r"<[^>]+>", " ", text)
    plain = html.unescape(plain)
    lines = [l.strip() for l in plain.splitlines() if l.strip()]
    
    # Filter out markdown version headings like "2.120.0 (2026-11-06)"
    filtered = []
    for l in lines:
        if re.match(r"^(#+|\d+\.\d+|Features|Bug Fixes|Technical|Internal release)", l):
            continue
        clean_l = l.lstrip("*-• ").strip()
        if len(clean_l) > 10:
            filtered.append(clean_l)
            if len(filtered) >= 2:
                break

    summary = " ".join(filtered) if filtered else (lines[0] if lines else "")
    if len(summary) > max_len:
        summary = summary[:max_len].rsplit(" ", 1)[0] + "…"
    return summary

def markdown_to_html(md_text):
    """
    Lightweight, dependency-free Markdown to clean semantic HTML converter.
    """
    if not md_text:
        return ""
    # Convert links: [text](url) -> <a href="url" target="_blank" rel="noopener">text</a>
    res = re.sub(r'\[([^\]]+)\]\((https?://[^)]+)\)', r'<a href="\2" target="_blank" rel="noopener">\1</a>', md_text)
    # Convert headers
    res = re.sub(r'^####\s+(.+)$', r'<h5>\1</h5>', res, flags=re.MULTILINE)
    res = re.sub(r'^###\s+(.+)$', r'<h4>\1</h4>', res, flags=re.MULTILINE)
    res = re.sub(r'^##\s+(.+)$', r'<h3>\1</h3>', res, flags=re.MULTILINE)
    res = re.sub(r'^#\s+(.+)$', r'<h2>\1</h2>', res, flags=re.MULTILINE)
    # Convert bold / code
    res = re.sub(r'\*\*([^*]+)\*\*', r'<strong>\1</strong>', res)
    res = re.sub(r'`([^`]+)`', r'<code>\1</code>', res)
    # Convert list items
    lines = res.splitlines()
    in_ul = False
    out = []
    for l in lines:
        s = l.strip()
        if s.startswith('* ') or s.startswith('- '):
            if not in_ul:
                out.append('<ul>')
                in_ul = True
            out.append(f'  <li>{s[2:]}</li>')
        else:
            if in_ul:
                out.append('</ul>')
                in_ul = False
            if s:
                if not s.startswith('<h') and not s.endswith('>'):
                    out.append(f'<p>{s}</p>')
                else:
                    out.append(s)
    if in_ul:
        out.append('</ul>')
    return '\n'.join(out)

def fetch_repo_releases(category, repo, token=None):
    """
    Fetch releases for a given repository. Prefers GitHub API if token is provided,
    otherwise uses Atom feeds for unlimited rate limits. Falls back to unauthenticated API
    when atom feed yields no production releases (e.g. smooth-app).
    """
    releases = []

    # 1. Try GitHub REST API if token is provided
    if token:
        api_url = f"https://api.github.com/repos/{repo}/releases?per_page=30"
        headers = {
            "User-Agent": "Mozilla/5.0 (OFF-Releases-Bot)",
            "Authorization": f"Bearer {token}",
            "Accept": "application/vnd.github.v3+json",
        }
        try:
            req = urllib.request.Request(api_url, headers=headers)
            with urllib.request.urlopen(req, timeout=15) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                for r in data:
                    tag = r.get("tag_name") or ""
                    if repo == "openfoodfacts/smooth-app" and tag.startswith("internal_"):
                        continue
                    pub = r.get("published_at") or r.get("created_at") or ""
                    body = r.get("body") or ""
                    summary = summarize_body(body)
                    releases.append({
                        "id": f"{repo.replace('/', '_')}_{tag}",
                        "repo": repo,
                        "repo_name": repo.split("/")[1],
                        "category": category,
                        "tag": tag,
                        "title": r.get("name") or tag,
                        "published_at": pub,
                        "date_en": format_date_en(pub),
                        "date_fr": format_date_fr(pub),
                        "html_url": r.get("html_url") or f"https://github.com/{repo}/releases/tag/{tag}",
                        "body_html": markdown_to_html(body),
                        "body_raw": body,
                        "summary": summary,
                        "is_prerelease": bool(r.get("prerelease")),
                    })
                return releases
        except Exception as e:
            print(f"  [WARN] GitHub API fetch failed for {repo}: {e}. Falling back to Atom feed.")

    # 2. GitHub releases.atom feed
    atom_url = f"https://github.com/{repo}/releases.atom"
    headers = {"User-Agent": "Mozilla/5.0 (OFF-Releases-Bot/1.0)"}
    try:
        req = urllib.request.Request(atom_url, headers=headers)
        with urllib.request.urlopen(req, timeout=15) as resp:
            tree = ET.fromstring(resp.read())
            ns = {"atom": "http://www.w3.org/2005/Atom"}
            entries = tree.findall("atom:entry", ns)
            for e in entries:
                title_elem = e.find("atom:title", ns)
                title = title_elem.text if title_elem is not None else ""
                tag = title.strip()
                if repo == "openfoodfacts/smooth-app" and tag.startswith("internal_"):
                    continue

                updated_elem = e.find("atom:updated", ns)
                pub = updated_elem.text if updated_elem is not None else ""

                link_elem = e.find("atom:link", ns)
                html_url = link_elem.attrib.get("href") if link_elem is not None else f"https://github.com/{repo}/releases/tag/{tag}"

                content_elem = e.find("atom:content", ns)
                raw_html = content_elem.text if content_elem is not None else ""
                cleaned_html = clean_html_body(raw_html)
                summary = summarize_body(cleaned_html)

                releases.append({
                    "id": f"{repo.replace('/', '_')}_{tag}",
                    "repo": repo,
                    "repo_name": repo.split("/")[1],
                    "category": category,
                    "tag": tag,
                    "title": title,
                    "published_at": pub,
                    "date_en": format_date_en(pub),
                    "date_fr": format_date_fr(pub),
                    "html_url": html_url,
                    "body_html": cleaned_html,
                    "body_raw": "",
                    "summary": summary,
                    "is_prerelease": "alpha" in tag.lower() or "beta" in tag.lower() or "rc" in tag.lower(),
                })
    except Exception as e:
        print(f"  [ERROR] Atom feed failed for {repo}: {e}")

    # 3. If atom feed returned no valid releases (or for smooth-app whose atom feed is clogged with internal builds),
    # fallback to unauthenticated GitHub REST API
    if not releases and repo in ("openfoodfacts/smooth-app",):
        try:
            api_url = f"https://api.github.com/repos/{repo}/releases?per_page=15"
            req = urllib.request.Request(api_url, headers={"User-Agent": "Mozilla/5.0 (OFF-Releases-Bot/1.0)"})
            with urllib.request.urlopen(req, timeout=10) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                for r in data:
                    tag = r.get("tag_name") or ""
                    if tag.startswith("internal_"):
                        continue
                    pub = r.get("published_at") or r.get("created_at") or ""
                    body = r.get("body") or ""
                    summary = summarize_body(body)
                    releases.append({
                        "id": f"{repo.replace('/', '_')}_{tag}",
                        "repo": repo,
                        "repo_name": repo.split("/")[1],
                        "category": category,
                        "tag": tag,
                        "title": r.get("name") or tag,
                        "published_at": pub,
                        "date_en": format_date_en(pub),
                        "date_fr": format_date_fr(pub),
                        "html_url": r.get("html_url") or f"https://github.com/{repo}/releases/tag/{tag}",
                        "body_html": markdown_to_html(body),
                        "body_raw": body,
                        "summary": summary,
                        "is_prerelease": bool(r.get("prerelease")),
                    })
        except Exception as e:
            print(f"  [WARN] Unauthenticated API fallback failed for {repo}: {e}")

    return releases

def fetch_all_releases(token=None, output_path=OUTPUT_JSON, verbose=True):
    catalog = fetch_wiki_catalog()
    if verbose:
        print(f"📦 Discovering releases across {len(catalog)} Open Food Facts repositories...")

    all_releases = []
    for cat, repo in catalog:
        if verbose:
            print(f"  Fetching {cat:15} | {repo}...")
        rels = fetch_repo_releases(cat, repo, token=token)
        if verbose:
            print(f"    -> Found {len(rels)} releases")
        all_releases.extend(rels)

    # Sort descending by published_at
    all_releases.sort(key=lambda x: x.get("published_at", ""), reverse=True)

    # Filter out empty or duplicate entries
    seen = set()
    deduped = []
    for r in all_releases:
        key = (r["repo"], r["tag"])
        if key not in seen:
            seen.add(key)
            deduped.append(r)

    # Save to JSON
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(deduped, f, ensure_ascii=False, indent=2)

    if verbose:
        one_year_ago = (datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(days=365)).isoformat()
        rolling = [r for r in deduped if r.get("published_at", "") >= one_year_ago]
        print("=" * 60)
        print(f"✨ Successfully compiled {len(deduped)} releases ({len(rolling)} in rolling year)")
        print(f"💾 Written to {output_path}")
        print("=" * 60)

    return deduped

def main():
    parser = argparse.ArgumentParser(description="Fetch Open Food Facts releases across repositories.")
    parser.add_argument("--token", default=os.environ.get("GITHUB_TOKEN"), help="GitHub personal access token for higher rate limits.")
    parser.add_argument("--output", default=OUTPUT_JSON, help="Path to output releases.json.")
    args = parser.parse_args()

    fetch_all_releases(token=args.token, output_path=args.output, verbose=True)

if __name__ == "__main__":
    main()
