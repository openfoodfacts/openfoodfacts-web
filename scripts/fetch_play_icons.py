#!/usr/bin/env python3
"""
Fetch official high-resolution icons from Google Play Store.
Replaces generic Play Store triangle placeholders (and unresolved Apple placeholders)
with actual 128x128 RGBA PNG icons, with fallbacks to iTunes API and the clean
Open Food Facts default icon. Updates data/reuses.json.
"""

import concurrent.futures
import hashlib
import json
import os
import re
import subprocess
import time
import urllib.parse
import urllib.request

DATA_PATH = "data/reuses.json"
ICONS_DIR = "html/images/reuses/icons"
DEFAULT_ICON = "/images/reuses/default-app-icon.png"

PLAY_PLACEHOLDER_HASH = "3b70337ef9bbfa68ccec79137a7c6f6f"
APPLE_PLACEHOLDER_HASH = "8bdf3cae80e6d1a97c0840b764d391df"

USER_AGENT = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/122.0.0.0 Safari/537.36"
)

REGIONS = [
    ("US", "en"),
    ("FR", "fr"),
    ("DE", "de"),
    ("GB", "en"),
    ("ES", "es"),
    ("IT", "it"),
    ("CA", "en"),
]

ITUNES_COUNTRIES = ["us", "fr", "de", "gb", "ca", "es", "it", "cn"]


def get_file_md5(path):
    if not os.path.exists(path):
        return None
    with open(path, "rb") as f:
        return hashlib.md5(f.read()).hexdigest()


def extract_play_pkg(url):
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
    if not url:
        return None
    m = re.search(r"id(\d+)", url)
    return m.group(1) if m else None


def download_and_convert_icon(artwork_url, target_png):
    temp_file = target_png + ".tmp"
    try:
        req = urllib.request.Request(artwork_url, headers={"User-Agent": USER_AGENT})
        with urllib.request.urlopen(req, timeout=12) as resp:
            with open(temp_file, "wb") as f:
                f.write(resp.read())

        # Convert to 128x128 RGBA PNG using macOS sips
        conv = subprocess.run(
            ["sips", "-s", "format", "png", "-Z", "128", temp_file, "--out", target_png],
            capture_output=True,
            text=True,
        )
        if os.path.exists(temp_file):
            os.remove(temp_file)

        if conv.returncode == 0 and os.path.exists(target_png) and os.path.getsize(target_png) > 200:
            return True
    except Exception as e:
        if os.path.exists(temp_file):
            os.remove(temp_file)
    return False


def fetch_play_store_details(pkg):
    for gl, hl in REGIONS:
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

                # Extract icon URL
                m = re.search(
                    r'<meta\s+(?:property=[\"\']og:image[\"\']\s+content=[\"\']([^\"\']+)[\"\']|content=[\"\']([^\"\']+)[\"\']\s+property=[\"\']og:image[\"\'])',
                    html,
                )
                og_img = m.group(1) or m.group(2) if m else None

                if not og_img:
                    # Alternative regex for play-lh.googleusercontent.com
                    lh_matches = re.findall(
                        r"https://play-lh\.googleusercontent\.com/[a-zA-Z0-9_\-=]+", html
                    )
                    if lh_matches:
                        og_img = lh_matches[0]

                if og_img:
                    # Strip existing size params and request full 512x512
                    base_img = og_img.split("=")[0]
                    hi_res_url = base_img + "=s512"

                    # Rating
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

                    return {
                        "status": "ok",
                        "icon_url": hi_res_url,
                        "rating": rating,
                    }
        except urllib.error.HTTPError as e:
            if e.code == 404:
                continue
        except Exception:
            pass
    return {"status": "not_found"}


def fetch_itunes_icon(apple_id):
    for c in ITUNES_COUNTRIES:
        url = f"https://itunes.apple.com/lookup?id={apple_id}&country={c}&entity=software"
        req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
        try:
            with urllib.request.urlopen(req, timeout=8) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                if data.get("results"):
                    res = data["results"][0]
                    art = res.get("artworkUrl512") or res.get("artworkUrl100")
                    rating = res.get("averageUserRating")
                    return {
                        "status": "ok",
                        "icon_url": art,
                        "rating": round(float(rating), 1) if rating else None,
                    }
        except Exception:
            pass
    return {"status": "not_found"}


def fetch_domain_favicon(domain):
    if not domain or domain in ("play.google.com", "apps.apple.com", "itunes.apple.com"):
        return None
    url = f"https://icons.duckduckgo.com/ip3/{domain}.ico"
    return url


def process_app(app):
    app_id = app["id"]
    target_png = os.path.join(ICONS_DIR, f"{app_id}.png")

    # 1. Try Google Play
    pkg = extract_play_pkg(app.get("play_store"))
    if pkg:
        play_data = fetch_play_store_details(pkg)
        if play_data["status"] == "ok":
            success = download_and_convert_icon(play_data["icon_url"], target_png)
            if success:
                return {
                    "id": app_id,
                    "status": "resolved_play",
                    "icon_path": f"/images/reuses/icons/{app_id}.png",
                    "rating": play_data.get("rating"),
                }

    # 2. Try Apple App Store fallback
    apple_id = extract_apple_id(app.get("app_store"))
    if apple_id:
        apple_data = fetch_itunes_icon(apple_id)
        if apple_data["status"] == "ok":
            success = download_and_convert_icon(apple_data["icon_url"], target_png)
            if success:
                return {
                    "id": app_id,
                    "status": "resolved_apple",
                    "icon_path": f"/images/reuses/icons/{app_id}.png",
                    "rating": apple_data.get("rating"),
                }

    # 3. Try custom domain favicon if website is available
    domain = app.get("domain")
    if not domain and app.get("website"):
        try:
            domain = urllib.parse.urlparse(app["website"]).netloc.lower().replace("www.", "")
        except Exception:
            pass

    if domain and domain not in ("play.google.com", "apps.apple.com", "itunes.apple.com"):
        fav_url = fetch_domain_favicon(domain)
        if fav_url:
            success = download_and_convert_icon(fav_url, target_png)
            if success:
                return {
                    "id": app_id,
                    "status": "resolved_domain",
                    "icon_path": f"/images/reuses/icons/{app_id}.png",
                    "rating": None,
                }

    # 4. Fallback: Clean Open Food Facts default icon
    return {
        "id": app_id,
        "status": "fallback_default",
        "icon_path": DEFAULT_ICON,
        "rating": None,
    }


def main():
    os.makedirs(ICONS_DIR, exist_ok=True)

    with open(DATA_PATH, "r", encoding="utf-8") as f:
        reuses = json.load(f)

    print(f"Loaded {len(reuses)} reuses from {DATA_PATH}.")

    # Identify apps that need processing:
    # - Those whose current cached icon is the Play Store placeholder
    # - Those whose current cached icon is the Apple Store placeholder
    # - Those with play_store that currently have default-app-icon.png (upgrade opportunity)
    candidates = []
    for r in reuses:
        icon_path = r.get("cached_icon")
        if not icon_path:
            candidates.append(r)
            continue

        full_path = os.path.join("html", icon_path.lstrip("/"))
        file_hash = get_file_md5(full_path) if os.path.exists(full_path) else None

        if file_hash in (PLAY_PLACEHOLDER_HASH, APPLE_PLACEHOLDER_HASH):
            candidates.append(r)
        elif icon_path == DEFAULT_ICON and r.get("play_store"):
            candidates.append(r)

    print(f"Found {len(candidates)} apps to process (placeholders or upgrade candidates).")

    resolved_count = 0
    fallback_count = 0
    results_by_id = {}

    with concurrent.futures.ThreadPoolExecutor(max_workers=12) as executor:
        futures = {executor.submit(process_app, app): app for app in candidates}
        for future in concurrent.futures.as_completed(futures):
            res = future.result()
            results_by_id[res["id"]] = res
            if res["status"].startswith("resolved_"):
                resolved_count += 1
                print(f"  [+] {res['id']}: {res['status']} -> {res['icon_path']}")
            else:
                fallback_count += 1
                print(f"  [-] {res['id']}: {res['status']} -> {res['icon_path']}")

    print(f"\nProcessing complete: {resolved_count} newly resolved, {fallback_count} set to clean default icon.")

    # Update data/reuses.json
    updated_apps = 0
    for r in reuses:
        app_id = r["id"]
        if app_id in results_by_id:
            res = results_by_id[app_id]
            r["cached_icon"] = res["icon_path"]
            if res.get("rating") and not r.get("rating"):
                r["rating"] = res["rating"]
            updated_apps += 1

    with open(DATA_PATH, "w", encoding="utf-8") as f:
        json.dump(reuses, f, indent=2, ensure_ascii=False)

    print(f"Updated {updated_apps} apps in {DATA_PATH}.")

    # Clean up any leftover placeholder files on disk matching the placeholder MD5 hashes
    cleaned_files = 0
    for fname in os.listdir(ICONS_DIR):
        fpath = os.path.join(ICONS_DIR, fname)
        if os.path.isfile(fpath):
            h = get_file_md5(fpath)
            if h in (PLAY_PLACEHOLDER_HASH, APPLE_PLACEHOLDER_HASH):
                os.remove(fpath)
                cleaned_files += 1

    print(f"Removed {cleaned_files} lingering placeholder icon files from disk.")


if __name__ == "__main__":
    main()
