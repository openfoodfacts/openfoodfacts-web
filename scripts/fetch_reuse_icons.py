#!/usr/bin/env python3
"""
Fetch and cache reuse application icons locally into html/images/reuses/icons/<id>.<ext>.

Resolution order:
1. Existing cached icon on disk (excluding known store placeholder hashes)
2. Explicit `icon_url`
3. Google Play Store (`play_store`) icon scraping + rating
4. Apple App Store (`app_store`) iTunes Lookup API + rating
5. Website `domain` / `website` favicon via DuckDuckGo ip3

Can be imported by `scripts/add_reuse.py` (via `ensure_reuse_icon`) or run as a CLI
to retro-download missing icons and update `data/reuses/*.yaml`.
"""

import argparse
import concurrent.futures
import glob
import hashlib
import json
import os
import re
import sys
import urllib.error
import urllib.parse
import urllib.request

SCRIPTS_DIR = os.path.dirname(os.path.abspath(__file__))
if SCRIPTS_DIR not in sys.path:
    sys.path.insert(0, SCRIPTS_DIR)

try:
    from i18n_utils import ensure_vendor_path
    ensure_vendor_path()
except ImportError:
    pass

import yaml
from add_reuse import (
    ICONS_DIR,
    REUSES_DIR,
    cache_reuse_icon,
    clean_url,
    extract_domain,
    find_cached_icon,
)

PLAY_PLACEHOLDER_HASH = "3b70337ef9bbfa68ccec79137a7c6f6f"
APPLE_PLACEHOLDER_HASH = "8bdf3cae80e6d1a97c0840b764d391df"
PLACEHOLDER_HASHES = {PLAY_PLACEHOLDER_HASH, APPLE_PLACEHOLDER_HASH}

USER_AGENT = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/122.0.0.0 Safari/537.36"
)

PLAY_REGIONS = [
    ("US", "en"),
    ("FR", "fr"),
    ("DE", "de"),
    ("GB", "en"),
    ("ES", "es"),
    ("IT", "it"),
    ("CA", "en"),
]

ITUNES_COUNTRIES = ["us", "fr", "de", "gb", "ca", "es", "it", "cn"]

EXCLUDED_FAVICON_DOMAINS = {
    "play.google.com",
    "apps.apple.com",
    "itunes.apple.com",
    "github.com",
    "gitlab.com",
    "f-droid.org",
}


def get_file_md5(path):
    """Return MD5 hex digest of a file, or None if it doesn't exist."""
    if not os.path.exists(path):
        return None
    with open(path, "rb") as f:
        return hashlib.md5(f.read()).hexdigest()


def is_valid_cached_icon(rel_icon_path, icons_dir=ICONS_DIR):
    """Check that a relative `/images/reuses/icons/<file>` exists, is non-trivial, and is not a placeholder."""
    if not rel_icon_path or not rel_icon_path.startswith("/images/reuses/icons/"):
        return False
    fname = os.path.basename(rel_icon_path)
    fpath = os.path.join(icons_dir, fname)
    if not os.path.isfile(fpath) or os.path.getsize(fpath) <= 100:
        return False
    return get_file_md5(fpath) not in PLACEHOLDER_HASHES


def extract_play_pkg(url):
    """Extract Android package ID from a Google Play Store URL."""
    if not url:
        return None
    m = re.search(r"id=([a-zA-Z0-9._]+)", url)
    if m:
        return m.group(1).split("&")[0]
    m = re.search(r"testing/([a-zA-Z0-9._]+)", url)
    if m:
        return m.group(1).split("&")[0]
    return None


def extract_apple_id(url):
    """Extract numeric Apple App Store ID from an App Store URL."""
    if not url:
        return None
    m = re.search(r"id(\d+)", url)
    return m.group(1) if m else None


def fetch_play_store_details(pkg):
    """Scrape Google Play Store for app icon URL and rating."""
    for gl, hl in PLAY_REGIONS:
        url = f"https://play.google.com/store/apps/details?id={pkg}&gl={gl}&hl={hl}"
        req = urllib.request.Request(
            url,
            headers={
                "User-Agent": USER_AGENT,
                "Accept-Language": f"{hl}-{gl},{hl};q=0.9",
            },
        )
        try:
            with urllib.request.urlopen(req, timeout=10) as resp:
                html = resp.read().decode("utf-8", errors="ignore")

                m = re.search(
                    r'<meta\s+(?:property=[\"\']og:image[\"\']\s+content=[\"\']([^\"\']+)[\"\']|'
                    r'content=[\"\']([^\"\']+)[\"\']\s+property=[\"\']og:image[\"\'])',
                    html,
                )
                og_img = (m.group(1) or m.group(2)) if m else None

                if not og_img:
                    lh_matches = re.findall(
                        r"https://play-lh\.googleusercontent\.com/[a-zA-Z0-9_\-=]+", html
                    )
                    if lh_matches:
                        og_img = lh_matches[0]

                if og_img:
                    base_img = og_img.split("=")[0]
                    hi_res_url = base_img + "=s512"

                    rating = None
                    m_rating = re.search(
                        r'aria-label=[\"\']Rated ([\d.]+) stars out of five stars[\"\']', html
                    )
                    if not m_rating:
                        m_rating = re.search(r'\"ratingValue\":\s*\"?([\d.]+)\"?', html)
                    if m_rating:
                        try:
                            rating = round(float(m_rating.group(1)), 1)
                        except ValueError:
                            pass

                    return {"status": "ok", "icon_url": hi_res_url, "rating": rating}
        except urllib.error.HTTPError as e:
            if e.code == 404:
                continue
        except Exception:
            pass
    return {"status": "not_found"}


def fetch_itunes_icon(apple_id):
    """Query Apple iTunes Lookup API for app icon URL and rating."""
    for country in ITUNES_COUNTRIES:
        url = f"https://itunes.apple.com/lookup?id={apple_id}&country={country}&entity=software"
        req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
        try:
            with urllib.request.urlopen(req, timeout=8) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                if data.get("results"):
                    res = data["results"][0]
                    art = res.get("artworkUrl512") or res.get("artworkUrl100")
                    rating = res.get("averageUserRating")
                    if art:
                        return {
                            "status": "ok",
                            "icon_url": art,
                            "rating": round(float(rating), 1) if rating else None,
                        }
        except Exception:
            pass
    return {"status": "not_found"}


def _try_cache(url, reuse_id, icons_dir):
    """Download via cache_reuse_icon and reject known store placeholder hashes."""
    rel_path = cache_reuse_icon(url, reuse_id, icons_dir=icons_dir)
    if not rel_path:
        return None
    if not is_valid_cached_icon(rel_path, icons_dir=icons_dir):
        fpath = os.path.join(icons_dir, os.path.basename(rel_path))
        if os.path.exists(fpath):
            os.remove(fpath)
        return None
    return rel_path


def ensure_reuse_icon(item, icons_dir=ICONS_DIR, force=False, include_domain_favicon=True):
    """
    Ensure a local icon exists for `item` under `icons_dir`.
    Updates `item["cached_icon"]` (and `item["rating"]` if missing and discovered).
    Returns a dict with `id`, `status`, `icon_path`, and optional `rating`.
    """
    r_id = item.get("id")
    if not r_id:
        return {"id": r_id, "status": "skipped_no_id", "icon_path": item.get("cached_icon")}

    existing = find_cached_icon(r_id, icons_dir=icons_dir)
    if existing:
        if not force and is_valid_cached_icon(existing, icons_dir=icons_dir):
            item["cached_icon"] = existing
            return {"id": r_id, "status": "existing", "icon_path": existing}
        # Remove stale/placeholder file
        stale_path = os.path.join(icons_dir, os.path.basename(existing))
        if os.path.exists(stale_path) and not is_valid_cached_icon(existing, icons_dir=icons_dir):
            os.remove(stale_path)

    # 1. Explicit icon_url
    icon_url = clean_url(item.get("icon_url"))
    if icon_url:
        cached = _try_cache(icon_url, r_id, icons_dir)
        if cached:
            item["cached_icon"] = cached
            return {"id": r_id, "status": "resolved_icon_url", "icon_path": cached}

    # 2. Google Play Store
    pkg = extract_play_pkg(item.get("play_store"))
    if pkg:
        play_data = fetch_play_store_details(pkg)
        if play_data["status"] == "ok":
            cached = _try_cache(play_data["icon_url"], r_id, icons_dir)
            if cached:
                item["cached_icon"] = cached
                if play_data.get("rating") and not item.get("rating"):
                    item["rating"] = play_data["rating"]
                return {
                    "id": r_id,
                    "status": "resolved_play",
                    "icon_path": cached,
                    "rating": play_data.get("rating"),
                }

    # 3. Apple App Store
    apple_id = extract_apple_id(item.get("app_store"))
    if apple_id:
        apple_data = fetch_itunes_icon(apple_id)
        if apple_data["status"] == "ok":
            cached = _try_cache(apple_data["icon_url"], r_id, icons_dir)
            if cached:
                item["cached_icon"] = cached
                if apple_data.get("rating") and not item.get("rating"):
                    item["rating"] = apple_data["rating"]
                return {
                    "id": r_id,
                    "status": "resolved_apple",
                    "icon_path": cached,
                    "rating": apple_data.get("rating"),
                }

    # 4. Website domain favicon
    if include_domain_favicon:
        domain = item.get("domain") or extract_domain(item.get("website"))
        if domain and domain not in EXCLUDED_FAVICON_DOMAINS:
            fav_url = f"https://icons.duckduckgo.com/ip3/{domain}.ico"
            cached = _try_cache(fav_url, r_id, icons_dir)
            if cached:
                item["cached_icon"] = cached
                return {"id": r_id, "status": "resolved_domain", "icon_path": cached}

    return {"id": r_id, "status": "not_resolved", "icon_path": item.get("cached_icon")}


def process_yaml_file(fpath, icons_dir=ICONS_DIR, force=False, dry_run=False, include_domain_favicon=True):
    """Load a reuse YAML file, ensure its icon is cached locally, and save if updated."""
    with open(fpath, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)

    if not isinstance(data, dict) or not data.get("id"):
        return {"id": os.path.basename(fpath), "status": "invalid_yaml"}

    old_cached = data.get("cached_icon")
    old_rating = data.get("rating")

    res = ensure_reuse_icon(
        data,
        icons_dir=icons_dir,
        force=force,
        include_domain_favicon=include_domain_favicon,
    )

    changed = (data.get("cached_icon") != old_cached) or (data.get("rating") != old_rating)
    if changed and not dry_run:
        with open(fpath, "w", encoding="utf-8") as f:
            yaml.safe_dump(data, f, sort_keys=False, allow_unicode=True)

    res["yaml_changed"] = changed
    return res


def main():
    parser = argparse.ArgumentParser(
        description="Retro-download missing reuse icons into html/images/reuses/icons/ and update YAML files."
    )
    parser.add_argument("--reuses-dir", default=REUSES_DIR, help="Path to data/reuses directory")
    parser.add_argument("--icons-dir", default=ICONS_DIR, help="Path to html/images/reuses/icons directory")
    parser.add_argument("--workers", type=int, default=12, help="Number of concurrent download workers")
    parser.add_argument("--force", action="store_true", help="Re-download even if icon already exists")
    parser.add_argument("--dry-run", action="store_true", help="Do not modify YAML files")
    parser.add_argument("--no-domain-favicon", action="store_true", help="Skip DuckDuckGo domain favicon fallback")
    parser.add_argument("--id", help="Only process a specific reuse ID")
    args = parser.parse_args()

    os.makedirs(args.icons_dir, exist_ok=True)
    yaml_files = sorted(glob.glob(os.path.join(args.reuses_dir, "*.yaml")))
    if args.id:
        yaml_files = [f for f in yaml_files if os.path.basename(f) == f"{args.id}.yaml"]

    if not yaml_files:
        print("No matching reuse YAML files found.")
        return

    candidates = []
    for fpath in yaml_files:
        with open(fpath, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)
        if not isinstance(data, dict) or not data.get("id"):
            continue
        r_id = data["id"]
        existing = find_cached_icon(r_id, icons_dir=args.icons_dir)
        valid_existing = existing and is_valid_cached_icon(existing, icons_dir=args.icons_dir)
        if args.force or not valid_existing or data.get("cached_icon") != existing:
            candidates.append(fpath)

    print(f"Scanning {len(yaml_files)} reuse YAMLs: {len(candidates)} need icon check/download.")

    stats = {}
    yaml_updates = 0
    with concurrent.futures.ThreadPoolExecutor(max_workers=args.workers) as executor:
        futures = {
            executor.submit(
                process_yaml_file,
                fpath,
                args.icons_dir,
                args.force,
                args.dry_run,
                not args.no_domain_favicon,
            ): fpath
            for fpath in candidates
        }
        for future in concurrent.futures.as_completed(futures):
            res = future.result()
            status = res["status"]
            stats[status] = stats.get(status, 0) + 1
            if res.get("yaml_changed"):
                yaml_updates += 1
            if status.startswith("resolved_"):
                print(f"  [+] {res['id']}: {status} -> {res['icon_path']}")

    print("\nSummary:")
    for k, v in sorted(stats.items()):
        print(f"  {k}: {v}")
    print(f"  YAML files updated: {yaml_updates}")


if __name__ == "__main__":
    main()
