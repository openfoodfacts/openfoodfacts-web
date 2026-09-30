#!/usr/bin/env python3
"""
Compilation and validation system for Open Food Facts Reuses.
Reads individual YAML files from data/reuses/*.yaml,
validates schemas, compiles data/reuses.json, and generates showcase HTML pages.
"""

import glob
import json
import os
import re
import sys
import yaml

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
DATA_DIR = os.path.join(REPO_ROOT, "data")
REUSES_DIR = os.path.join(DATA_DIR, "reuses")
COMPILED_JSON = os.path.join(DATA_DIR, "reuses.json")

VALID_THEMES = {
    # General domains
    "nutrition", "environment", "tools", "research", "traceability", "education",
    "health", "social", "retail", "general", "ai", "dietary",
    # Diets & Health
    "pregnancy", "gluten", "lactose", "fodmap", "allergies", "vegan",
    "halal_kosher", "diabetes_keto", "additives"
}

VALID_PROJECTS = {"openfoodfacts", "openbeautyfacts", "openpetfoodfacts", "openproductsfacts"}

def validate_reuse(item, filepath):
    errors = []
    warnings = []
    filename = os.path.basename(filepath)
    stem = filename[:-5] if filename.endswith(".yaml") else filename[:-4]

    # Required: id
    r_id = item.get("id")
    if not r_id:
        errors.append(f"{filename}: missing required field 'id'")
    elif r_id != stem:
        errors.append(f"{filename}: id '{r_id}' does not match filename stem '{stem}'")
    elif not re.match(r"^[a-zA-Z0-9_-]+$", str(r_id)):
        errors.append(f"{filename}: id '{r_id}' contains invalid characters (must be alphanumeric, hyphens, or underscores)")

    # Required: name
    name = item.get("name")
    if not name or not str(name).strip():
        errors.append(f"{filename}: missing or empty required field 'name'")

    # Required: theme
    theme = item.get("theme")
    if not theme:
        errors.append(f"{filename}: missing required field 'theme'")
    elif theme not in VALID_THEMES:
        errors.append(f"{filename}: invalid theme '{theme}'. Must be one of: {', '.join(sorted(VALID_THEMES))}")

    # Optional themes list
    themes = item.get("themes")
    if themes is not None:
        if not isinstance(themes, list):
            errors.append(f"{filename}: 'themes' must be a list of strings")
        else:
            for t in themes:
                if t not in VALID_THEMES:
                    errors.append(f"{filename}: invalid theme '{t}' in 'themes' list. Must be one of: {', '.join(sorted(VALID_THEMES))}")

    # Project check
    project = item.get("project")
    if project and project not in VALID_PROJECTS:
        errors.append(f"{filename}: invalid project '{project}'. Must be one of: {', '.join(sorted(VALID_PROJECTS))}")

    # Boolean fields check
    for bool_field in ["contributes_data", "contributes_photos", "odbl_compliant", "open_source", "featured", "donates_to_ngo"]:
        val = item.get(bool_field)
        if val is not None and not isinstance(val, bool):
            errors.append(f"{filename}: '{bool_field}' must be a boolean (true/false), got {type(val).__name__}")

    # Numeric fields check
    for num_field in ["installs_numeric", "rating"]:
        val = item.get(num_field)
        if val is not None and not isinstance(val, (int, float)):
            errors.append(f"{filename}: '{num_field}' must be numeric or null, got {type(val).__name__}")

    # Links check: at least one of website, play_store, app_store, fdroid, github should ideally exist
    links = [item.get(k) for k in ["website", "play_store", "app_store", "fdroid", "github"] if item.get(k)]
    if not links:
        warnings.append(f"{filename}: application has no web, app store, or repo links")

    return errors, warnings

def load_reuses(directory=REUSES_DIR, validate=True):
    yaml_files = sorted(glob.glob(os.path.join(directory, "*.yaml")) + glob.glob(os.path.join(directory, "*.yml")))
    if not yaml_files:
        raise FileNotFoundError(f"No YAML files found in {directory}")

    items = []
    all_errors = []
    all_warnings = []

    for fpath in yaml_files:
        try:
            with open(fpath, "r", encoding="utf-8") as f:
                data = yaml.safe_load(f)
        except Exception as e:
            all_errors.append(f"Failed to parse {os.path.basename(fpath)}: {e}")
            continue

        if not isinstance(data, dict):
            all_errors.append(f"{os.path.basename(fpath)}: content must be a YAML mapping/dictionary")
            continue

        if validate:
            errs, warns = validate_reuse(data, fpath)
            all_errors.extend(errs)
            all_warnings.extend(warns)

        items.append(data)

    # Sort: featured first, then case-insensitive by name
    items.sort(key=lambda x: (not x.get("featured", False), (x.get("name") or "").lower()))

    return items, all_errors, all_warnings

def compile_reuses(check_only=False, verbose=True):
    if verbose:
        print(f"Loading and validating reuses from {REUSES_DIR}...")

    items, errors, warnings = load_reuses(REUSES_DIR, validate=True)

    if warnings and verbose:
        for w in warnings[:10]:
            print(f"  [WARN] {w}")
        if len(warnings) > 10:
            print(f"  ... and {len(warnings) - 10} more warnings.")

    if errors:
        print(f"\n❌ Found {len(errors)} validation error(s) in reuses YAMLs:")
        for e in errors:
            print(f"  - {e}")
        return False

    if verbose:
        total_installs = sum(r.get("installs_numeric", 0) for r in items)
        total_countries = len(set(r.get("country") for r in items if r.get("country")))
        featured_count = sum(1 for r in items if r.get("featured"))
        print(f"✅ Validated {len(items)} reuses (Featured: {featured_count}, Countries: {total_countries}, Recorded installs: {total_installs:,})")

    if check_only:
        return True

    # 1. Write compiled data/reuses.json
    with open(COMPILED_JSON, "w", encoding="utf-8") as f:
        json.dump(items, f, ensure_ascii=False, indent=2)
    if verbose:
        print(f"Wrote compiled {COMPILED_JSON} ({len(items)} items)")

    # 2. Re-generate showcase HTML pages
    try:
        sys.path.insert(0, os.path.dirname(__file__))
        import generate_showcase
        generate_showcase.ALL_REUSES = items
        generate_showcase.TOTAL_APPS = len(items)
        generate_showcase.TOTAL_INSTALLS_NUM = sum(r.get("installs_numeric", 0) for r in items)
        generate_showcase.TOTAL_COUNTRIES = len(set(r.get("country") for r in items if r.get("country")))
        generate_showcase.main()
    except Exception as e:
        if verbose:
            print(f"  [NOTE] Showcase HTML pages generation skipped or failed: {e}")

    return True

if __name__ == "__main__":
    check_mode = "--check" in sys.argv
    success = compile_reuses(check_only=check_mode, verbose=True)
    sys.exit(0 if success else 1)
