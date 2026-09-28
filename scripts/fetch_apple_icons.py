#!/usr/bin/env python3
"""
Fetch official high-resolution icons from Apple App Store via iTunes Lookup API.
Downloads artworkUrl512, converts to 128x128 PNG via sips, and updates data/reuses.json.
"""

import json
import os
import re
import subprocess
import urllib.request
import time

DATA_PATH = "data/reuses.json"
ICONS_DIR = "html/images/reuses/icons"
USER_AGENT = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"

# Specific overrides/fixes for Apple IDs
KNOWN_APPLE_IDS = {
    "macrofactor": "1553503471",
    "foodvisor": "1064020872",
    "yuka": "1092799236",
    "open-food-facts-smooth-app": "588797948",
    "open-beauty-facts-app": "1125923483",
    "mylabel": "1316896135",
    "quelproduit": "1509421160",
    "el-coco": "1446005742",
    "pantrist": "1531156635",
    "date-limite": "504520670",
    "hophopfood": "1358327914",
    "opennutritracker": "6451490901"
}

def extract_apple_id(url):
    if not url: return None
    m = re.search(r'id(\d+)', url)
    return m.group(1) if m else None

def lookup_itunes_batch(apple_ids, country=None):
    ids_str = ",".join(apple_ids)
    url = f"https://itunes.apple.com/lookup?id={ids_str}&entity=software"
    if country:
        url += f"&country={country}"
    try:
        req = urllib.request.Request(url, headers={'User-Agent': USER_AGENT})
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read().decode('utf-8'))
            results = {}
            for res in data.get('results', []):
                t_id = str(res.get('trackId'))
                results[t_id] = res
            return results
    except Exception as e:
        print(f"Error querying iTunes batch ({country}): {e}")
        return {}

def download_and_convert_icon(artwork_url, target_png):
    try:
        temp_file = target_png + ".tmp"
        req = urllib.request.Request(artwork_url, headers={'User-Agent': USER_AGENT})
        with urllib.request.urlopen(req, timeout=10) as resp:
            with open(temp_file, "wb") as f:
                f.write(resp.read())

        # Convert to 128x128 RGBA PNG with sips
        conv = subprocess.run(
            ["sips", "-s", "format", "png", "-Z", "128", temp_file, "--out", target_png],
            capture_output=True,
            text=True
        )
        if os.path.exists(temp_file):
            os.remove(temp_file)

        if conv.returncode == 0 and os.path.exists(target_png) and os.path.getsize(target_png) > 200:
            return True
        return False
    except Exception as e:
        print(f"Error downloading {artwork_url}: {e}")
        return False

def main():
    os.makedirs(ICONS_DIR, exist_ok=True)
    with open(DATA_PATH, "r", encoding="utf-8") as f:
        reuses = json.load(f)

    # Collect apps with Apple Store IDs
    id_to_app = {}
    for r in reuses:
        app_id = r["id"]
        apple_id = KNOWN_APPLE_IDS.get(app_id) or extract_apple_id(r.get("app_store"))
        if apple_id:
            id_to_app[apple_id] = r

    print(f"Found {len(id_to_app)} apps with Apple Store ID.")

    all_apple_ids = list(id_to_app.keys())
    batch_size = 80
    resolved_results = {}

    # Query storefronts: US, FR, DE, ES, IT, GB
    countries = [None, "fr", "us", "de", "es", "gb"]

    for country in countries:
        unresolved_ids = [aid for aid in all_apple_ids if aid not in resolved_results]
        if not unresolved_ids:
            break
        print(f"Looking up {len(unresolved_ids)} unresolved IDs in storefront: {country or 'default'}...")
        for i in range(0, len(unresolved_ids), batch_size):
            chunk = unresolved_ids[i:i + batch_size]
            batch_res = lookup_itunes_batch(chunk, country)
            resolved_results.update(batch_res)
            time.sleep(0.3)

    print(f"Successfully resolved iTunes data for {len(resolved_results)} apps!")

    # Download and update icons
    updated_icons = 0
    for apple_id, res in resolved_results.items():
        app = id_to_app.get(apple_id)
        if not app:
            continue

        art_url = res.get("artworkUrl512") or res.get("artworkUrl100")
        if not art_url:
            continue

        target_png = os.path.join(ICONS_DIR, f"{app['id']}.png")
        success = download_and_convert_icon(art_url, target_png)
        if success:
            app["cached_icon"] = f"/images/reuses/icons/{app['id']}.png"
            updated_icons += 1

        # Also capture store rating if available
        rating = res.get("averageUserRating")
        if rating and not app.get("rating"):
            app["rating"] = round(float(rating), 1)

    print(f"Updated {updated_icons} official Apple App Store icons!")

    with open(DATA_PATH, "w", encoding="utf-8") as f:
        json.dump(reuses, f, indent=2, ensure_ascii=False)

    print("Updated data/reuses.json with fresh store icons and ratings.")

if __name__ == "__main__":
    main()
