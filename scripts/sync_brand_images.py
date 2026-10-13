#!/usr/bin/env python3
"""
Sync logos from the official openfoodfacts/brand-images repository
(https://github.com/openfoodfacts/brand-images) and save local versions in:
html/images/producers/brands/

Matches producer and brand entries in data/producers/*.yaml and updates
their logo_url fields to use the local committed image or CDN fallback.
"""

import glob
import json
import os
import re
import urllib.request
import yaml

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
DATA_PRODUCERS_DIR = os.path.join(REPO_ROOT, "data", "producers")
BRANDS_IMG_DIR = os.path.join(REPO_ROOT, "html", "images", "producers", "brands")
INDEX_CACHE_PATH = os.path.join(REPO_ROOT, "scratch", "brand_images_index.json")

GITHUB_RAW_BASE = "https://raw.githubusercontent.com/openfoodfacts/brand-images/main"
JSDELIVR_BASE = "https://cdn.jsdelivr.net/gh/openfoodfacts/brand-images@main"


def fetch_brand_images_index():
    """Fetch or load the tree index of openfoodfacts/brand-images."""
    if os.path.exists(INDEX_CACHE_PATH):
        with open(INDEX_CACHE_PATH, "r", encoding="utf-8") as f:
            return json.load(f)

    print("Fetching repository tree from GitHub API...")
    req = urllib.request.Request(
        "https://api.github.com/repos/openfoodfacts/brand-images/git/trees/main?recursive=1",
        headers={"User-Agent": "OFF-Web-Compiler"}
    )
    with urllib.request.urlopen(req) as resp:
        data = json.loads(resp.read().decode("utf-8"))

    brands = []
    stores = []
    for item in data.get("tree", []):
        path = item.get("path", "")
        if path.startswith("xx/brands/") and not path.endswith("/"):
            brands.append(os.path.basename(path))
        elif path.startswith("xx/stores/") and not path.endswith("/"):
            stores.append(os.path.basename(path))

    os.makedirs(os.path.dirname(INDEX_CACHE_PATH), exist_ok=True)
    with open(INDEX_CACHE_PATH, "w", encoding="utf-8") as f:
        json.dump({"brands": brands, "stores": stores}, f)

    return {"brands": brands, "stores": stores}


def normalize(name):
    if not name:
        return ""
    s = name.lower()
    s = re.sub(r"\.(svg|png|jpg|jpeg|webp)$", "", s)
    s = re.sub(r"[^a-z0-9]+", "", s)
    return s


def build_lookup_table(index):
    """Build normalized lookup table favoring SVG, then PNG, then JPG."""
    table = {}

    def add_files(file_list, category):
        for f in file_list:
            norm = normalize(f)
            ext = os.path.splitext(f)[1].lower()
            score = 3 if ext == ".svg" else (2 if ext == ".png" else 1)
            # Give slight bonus to exact / non-candidate files
            if "candidate" in f.lower():
                score -= 0.5
            if norm not in table or score > table[norm]["score"]:
                table[norm] = {
                    "score": score,
                    "filename": f,
                    "category": category,
                    "ext": ext
                }

    # Add stores first, then brands (brands take precedence unless stores has SVG)
    add_files(index.get("stores", []), "stores")
    add_files(index.get("brands", []), "brands")
    return table


def find_best_match(producer_data, lookup_table):
    pid = producer_data.get("id", "")
    name = producer_data.get("name", "")
    owner = producer_data.get("owner", "")

    # Clean candidates
    cands = []
    if name:
        cands.append(name)
    if pid:
        cands.append(pid)

    # Common brand name variations
    for base in [name, pid]:
        if not base:
            continue
        cleaned = re.sub(
            r"\b(france|deutschland|espana|belgique|germany|suisse|osterreich|ag|gmbh|sas|sa|srl|spa|sl|ltd|co|corp|groupe|group)\b",
            "", base, flags=re.I
        ).strip("- ").strip()
        if cleaned and cleaned not in cands:
            cands.append(cleaned)
        parts = base.split("-")
        if len(parts) > 1 and parts[0] not in cands:
            cands.append(parts[0])

    # Check candidates against lookup table
    for c in cands:
        norm = normalize(c)
        if norm in lookup_table:
            return lookup_table[norm]

    # Fallback to owner if group/parent
    if owner:
        norm_owner = normalize(owner)
        if norm_owner in lookup_table:
            return lookup_table[norm_owner]

    return None


def download_brand_image(entry, target_filename):
    """Download image from GitHub raw / jsDelivr to local target path."""
    os.makedirs(BRANDS_IMG_DIR, exist_ok=True)
    target_path = os.path.join(BRANDS_IMG_DIR, target_filename)
    if os.path.exists(target_path) and os.path.getsize(target_path) > 0:
        return target_path

    cat = entry["category"]
    fname = entry["filename"]
    # URL encode filename
    url_fname = urllib.parse.quote(fname)
    url = f"{GITHUB_RAW_BASE}/xx/{cat}/{url_fname}"

    try:
        req = urllib.request.Request(url, headers={"User-Agent": "OFF-Web-Compiler"})
        with urllib.request.urlopen(req, timeout=10) as resp:
            content = resp.read()
            with open(target_path, "wb") as f:
                f.write(content)
        return target_path
    except Exception as e:
        # Fallback to jsdelivr
        try:
            cdn_url = f"{JSDELIVR_BASE}/xx/{cat}/{url_fname}"
            req2 = urllib.request.Request(cdn_url, headers={"User-Agent": "OFF-Web-Compiler"})
            with urllib.request.urlopen(req2, timeout=10) as resp2:
                content = resp2.read()
                with open(target_path, "wb") as f:
                    f.write(content)
            return target_path
        except Exception as e2:
            print(f"  Warning: failed downloading {fname}: {e} / {e2}")
            return None


def sync_all_brands(dry_run=False):
    index = fetch_brand_images_index()
    lookup = build_lookup_table(index)

    # Check local existing files in BRANDS_IMG_DIR
    local_existing = {}
    if os.path.exists(BRANDS_IMG_DIR):
        for f in os.listdir(BRANDS_IMG_DIR):
            norm = normalize(f)
            local_existing[norm] = f

    yaml_files = sorted(glob.glob(os.path.join(DATA_PRODUCERS_DIR, "*.yaml")))
    updated_count = 0
    downloaded_count = 0

    for yfile in yaml_files:
        with open(yfile, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f) or {}

        pid = data.get("id")
        current_logo = data.get("logo_url")

        # 1. Check if already has a dedicated local logo
        match = find_best_match(data, lookup)
        if not match:
            continue

        ext = match["ext"]
        clean_slug = re.sub(r"[^a-z0-9_-]+", "-", pid.lower()).strip("-")
        local_filename = f"{clean_slug}{ext}"
        local_web_path = f"/images/producers/brands/{local_filename}"

        if not dry_run:
            downloaded = download_brand_image(match, local_filename)
            if downloaded:
                downloaded_count += 1
                if current_logo != local_web_path:
                    data["logo_url"] = local_web_path
                    with open(yfile, "w", encoding="utf-8") as f:
                        yaml.dump(data, f, allow_unicode=True, sort_keys=False, default_flow_style=False)
                    updated_count += 1
        else:
            updated_count += 1

    print(f"✅ Brand Images Sync Complete!")
    print(f"   Matched & processed: {updated_count} producers")
    print(f"   Total local brand images in {BRANDS_IMG_DIR}: {len(os.listdir(BRANDS_IMG_DIR))}")


if __name__ == "__main__":
    sync_all_brands()
