#!/usr/bin/env python3
"""
Migrate and clean FAQ content from cms-test to openfoodfacts-web.
Standardizes frontmatter, strips Quarto shortcodes, and organizes
by 2-letter language codes in data/faq/<lang>/.
"""

import glob
import os
import re
import yaml

CMS_FAQ_DIR = "/Users/pierre/development/cms-test/faq"
TARGET_FAQ_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "data", "faq"))

LANG_MAP = {
    "en-gb": "en",
    "fr-fr": "fr",
    "es-es": "es",
    "de-de": "de",
    "it-it": "it"
}

CATEGORY_MAP = {
    "1": "account",
    "2": "mobile-app",
    "4": "product-questions",
    "5": "eco-score",
    "6": "nova",
    "7": "data-download",
    "8": "nutri-score",
    "9": "open-food-facts",
    "10": "open-pet-food-facts",
    "11": "open-beauty-facts",
    "12": "api-data-reuse",
    "13": "volunteering",
    "14": "press-media",
    "15": "international",
    "16": "technical-faq",
    "17": "producers-about",
    "19": "producers-scores",
    "20": "producers-account",
    "21": "producers-products",
    "22": "producers-portfolio",
    "23": "labels",
    "24": "producers-packaging",
    "26": "school-projects",
    "28": "open-products-facts",
    "29": "open-prices",
    "31": "folksonomy",
}

ICON_MAP = {
    "book": "📖",
    "bookmark": "🏷️",
    "box": "📦",
    "brands github": "🛠️",
    "chart-bar": "📊",
    "chart-line": "📈",
    "cloud-download": "📥",
    "cube": "📦",
    "dollar": "💶",
    "edit": "🤝",
    "file-o": "🎓",
    "flask": "🧪",
    "globe": "🌐",
    "heartbeat": "🥗",
    "industry": "🏭",
    "info-circle": "ℹ️",
    "key": "🔑",
    "mobile": "📱",
    "newspaper": "📰",
    "paw": "🐾",
    "question-circle": "❓",
    "shopping-basket": "🛒",
    "tags": "💄",
    "user": "👤",
    "user-circle": "👤",
    "user-plus": "🌿",
    "wrench": "💻",
}

def clean_quarto_tags(text):
    return re.sub(r"\{\{<\s*fa\s+[^>]*\s*>\}\}", "", text).strip()

def extract_prefix(filename):
    basename = os.path.basename(filename)
    match = re.match(r"^(\d+)", basename)
    return match.group(1) if match else None

def migrate():
    os.makedirs(TARGET_FAQ_DIR, exist_ok=True)
    total_files = 0
    total_questions = 0

    for cms_lang, target_lang in LANG_MAP.items():
        src_lang_dir = os.path.join(CMS_FAQ_DIR, cms_lang)
        dst_lang_dir = os.path.join(TARGET_FAQ_DIR, target_lang)
        os.makedirs(dst_lang_dir, exist_ok=True)

        if not os.path.isdir(src_lang_dir):
            print(f"Directory not found: {src_lang_dir}")
            continue

        md_files = sorted(glob.glob(f"{src_lang_dir}/**/*.md", recursive=True))

        for src_path in md_files:
            if os.path.basename(src_path) == "index.md":
                continue

            rel_path = os.path.relpath(src_path, src_lang_dir)
            dst_path = os.path.join(dst_lang_dir, rel_path)
            os.makedirs(os.path.dirname(dst_path), exist_ok=True)

            with open(src_path, "r", encoding="utf-8") as f:
                content = f.read()

            fm = {}
            body = content
            if content.startswith("---"):
                parts = content.split("---", 2)
                if len(parts) >= 3:
                    try:
                        fm = yaml.safe_load(parts[1]) or {}
                    except Exception as e:
                        print(f"Error parsing frontmatter in {src_path}: {e}")
                    body = parts[2]

            prefix = extract_prefix(src_path)
            category_slug = CATEGORY_MAP.get(prefix, f"cat-{prefix}")

            title = fm.get("title", "")
            title_clean = clean_quarto_tags(title)
            raw_icon = str(fm.get("icon", "")).strip()
            emoji_icon = ICON_MAP.get(raw_icon, "❓")
            order = fm.get("order", int(prefix) if prefix and prefix.isdigit() else 99)

            body_clean = clean_quarto_tags(body).strip()

            questions = re.findall(r"^##\s+(.+)$", body_clean, flags=re.MULTILINE)
            total_questions += len(questions)
            total_files += 1

            new_frontmatter = {
                "id": category_slug,
                "title": title_clean,
                "icon": emoji_icon,
                "icon_name": raw_icon,
                "order": order,
                "lang": target_lang
            }

            out_content = "---\n"
            out_content += yaml.dump(new_frontmatter, allow_unicode=True, sort_keys=False)
            out_content += "---\n\n"
            out_content += body_clean + "\n"

            with open(dst_path, "w", encoding="utf-8") as f:
                f.write(out_content)

        file_count = len([f for f in md_files if not f.endswith("index.md")])
        print(f"Migrated {file_count} files to data/faq/{target_lang}/")

    print(f"\nMigration complete: {total_files} files, {total_questions} total questions migrated.")

if __name__ == "__main__":
    migrate()
