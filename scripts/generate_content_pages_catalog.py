#!/usr/bin/env python3
"""Generate a machine-readable catalog of translated content pages."""

from __future__ import annotations

import json
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
LANG_DIR = REPO_ROOT / "lang"
OUTPUT_FILE = LANG_DIR / "content-pages.json"
METADATA_FILE = LANG_DIR / "content-pages-metadata.json"
EDIT_URL_BASE = "https://github.com/openfoodfacts/openfoodfacts-web/edit/main"


def load_metadata() -> dict[str, dict]:
    if not METADATA_FILE.exists():
        return {}

    with METADATA_FILE.open("r", encoding="utf-8") as file_obj:
        metadata = json.load(file_obj)

    pages = metadata.get("pages", {})
    if not isinstance(pages, dict):
        raise ValueError("`pages` must be an object in content-pages-metadata.json")

    return pages


def list_language_folders() -> list[Path]:
    return sorted(
        path
        for path in LANG_DIR.iterdir()
        if path.is_dir() and (path / "texts").is_dir()
    )


def build_catalog() -> dict:
    metadata_by_page = load_metadata()
    pages_index: dict[str, dict] = {}

    for language_dir in list_language_folders():
        language_code = language_dir.name
        texts_dir = language_dir / "texts"

        for file_path in sorted(texts_dir.rglob("*.html")):
            relative_page_path = file_path.relative_to(texts_dir).as_posix()
            language_relative_path = file_path.relative_to(REPO_ROOT).as_posix()

            page_entry = pages_index.setdefault(
                relative_page_path,
                {
                    "path": relative_page_path,
                    "languages": [],
                    "edit_links": [],
                },
            )

            page_entry["languages"].append(language_code)
            page_entry["edit_links"].append(
                {
                    "language": language_code,
                    "url": f"{EDIT_URL_BASE}/{language_relative_path}",
                }
            )

    pages = []
    for page_path in sorted(pages_index):
        page_entry = pages_index[page_path]
        page_entry["languages"] = sorted(page_entry["languages"])
        page_entry["edit_links"] = sorted(
            page_entry["edit_links"], key=lambda link: link["language"]
        )

        metadata = metadata_by_page.get(page_path, {})
        page_entry["description"] = metadata.get("description")
        page_entry["thumbnail_image"] = metadata.get("thumbnail_image")
        page_entry["metadata"] = metadata.get("metadata", {})
        page_entry["background_color"] = metadata.get("background_color")

        pages.append(page_entry)

    return {
        "schema_version": 1,
        "metadata_file": "lang/content-pages-metadata.json",
        "pages": pages,
    }


def write_catalog(catalog: dict) -> None:
    with OUTPUT_FILE.open("w", encoding="utf-8") as file_obj:
        json.dump(catalog, file_obj, ensure_ascii=False, indent=2)
        file_obj.write("\n")


def main() -> int:
    catalog = build_catalog()
    write_catalog(catalog)
    print(f"Generated {OUTPUT_FILE.relative_to(REPO_ROOT)} with {len(catalog['pages'])} pages")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
