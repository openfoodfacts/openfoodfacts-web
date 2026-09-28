#!/usr/bin/env python3
"""
Migrate monolithic reuses.json and press-review-merged.json into
one YAML file per entity in data/reuses/ and data/press-review/.
"""

import json
import os
import re
import unicodedata
import yaml

DATA_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "data"))
REUSES_JSON = os.path.join(DATA_DIR, "reuses.json")
PRESS_JSON = os.path.join(DATA_DIR, "press-review-merged.json")

REUSES_DIR = os.path.join(DATA_DIR, "reuses")
PRESS_DIR = os.path.join(DATA_DIR, "press-review")

REUSE_KEY_ORDER = [
    "id", "name", "tagline", "description",
    "theme", "themes", "project",
    "country", "country_label", "domain", "website",
    "play_store", "app_store", "fdroid", "github",
    "contributes_data", "contributes_photos",
    "odbl_compliant", "open_source", "license",
    "featured", "keywords",
    "icon_url", "cached_icon",
    "donates_to_ngo", "donation_note", "donation_note_fr", "special_badge",
    "installs", "installs_numeric", "rating"
]

PRESS_KEY_ORDER = [
    "id", "date", "source", "title", "link", "domain",
    "type", "raw_type", "lang", "country",
    "author", "topic", "verbatim",
    "selected", "origin"
]

def slugify(text, max_len=40):
    text = unicodedata.normalize("NFKD", str(text)).encode("ascii", "ignore").decode("ascii")
    text = re.sub(r"[^\w\s-]", "", text.lower()).strip()
    slug = re.sub(r"[-\s]+", "-", text)
    return slug[:max_len].rstrip("-")

def order_dict(d, key_order):
    ordered = {}
    for k in key_order:
        if k in d:
            ordered[k] = d[k]
    for k, v in d.items():
        if k not in ordered:
            ordered[k] = v
    return ordered

def migrate_reuses():
    os.makedirs(REUSES_DIR, exist_ok=True)
    with open(REUSES_JSON, "r", encoding="utf-8") as f:
        reuses = json.load(f)

    print(f"Exporting {len(reuses)} reuses to {REUSES_DIR}...")
    written = 0
    for r in reuses:
        r_id = r["id"].strip()
        ordered = order_dict(r, REUSE_KEY_ORDER)
        target_file = os.path.join(REUSES_DIR, f"{r_id}.yaml")
        with open(target_file, "w", encoding="utf-8") as out:
            yaml.dump(ordered, out, allow_unicode=True, sort_keys=False, width=120)
        written += 1

    print(f"Successfully wrote {written} reuse YAML files.")

def migrate_press():
    os.makedirs(PRESS_DIR, exist_ok=True)
    with open(PRESS_JSON, "r", encoding="utf-8") as f:
        press = json.load(f)

    print(f"Exporting {len(press)} press review items to {PRESS_DIR}...")
    used_slugs = set()
    written = 0

    for item in press:
        d = item.get("date", "2018-01-01").strip()
        s = slugify(item.get("source", "source"), 16) or "source"
        t = slugify(item.get("title", "mention"), 32) or "mention"
        base_slug = f"{d}-{s}-{t}".strip("-")
        
        slug = base_slug
        counter = 2
        while slug in used_slugs:
            slug = f"{base_slug}-{counter}"
            counter += 1
        used_slugs.add(slug)

        item_with_id = dict(item)
        item_with_id["id"] = slug
        ordered = order_dict(item_with_id, PRESS_KEY_ORDER)

        target_file = os.path.join(PRESS_DIR, f"{slug}.yaml")
        with open(target_file, "w", encoding="utf-8") as out:
            yaml.dump(ordered, out, allow_unicode=True, sort_keys=False, width=120)
        written += 1

    print(f"Successfully wrote {written} press review YAML files.")

if __name__ == "__main__":
    migrate_reuses()
    migrate_press()
