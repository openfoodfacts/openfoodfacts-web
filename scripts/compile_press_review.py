#!/usr/bin/env python3
"""
Compilation and validation system for Open Food Facts Press Review.
Reads individual YAML files from data/press-review/*.yaml,
validates schemas, compiles data/press-review-merged.json, and generates press review HTML pages.
"""

import glob
import json
import os
import re
import sys
import yaml

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
DATA_DIR = os.path.join(REPO_ROOT, "data")
PRESS_DIR = os.path.join(DATA_DIR, "press-review")
COMPILED_JSON = os.path.join(DATA_DIR, "press-review-merged.json")

VALID_TYPES = {"article", "podcast", "video", "study"}

def validate_press_item(item, filepath):
    errors = []
    warnings = []
    filename = os.path.basename(filepath)
    stem = filename[:-5] if filename.endswith(".yaml") else filename[:-4]

    # Required: id
    p_id = item.get("id")
    if not p_id:
        errors.append(f"{filename}: missing required field 'id'")
    elif str(p_id) != stem:
        errors.append(f"{filename}: id '{p_id}' does not match filename stem '{stem}'")

    # Required: date (YYYY-MM-DD)
    date_val = str(item.get("date", "")).strip()
    if not date_val:
        errors.append(f"{filename}: missing required field 'date'")
    elif not re.match(r"^\d{4}-\d{2}-\d{2}$", date_val):
        errors.append(f"{filename}: invalid date format '{date_val}', must be YYYY-MM-DD")

    # Required: source
    source = item.get("source")
    if not source or not str(source).strip():
        errors.append(f"{filename}: missing or empty required field 'source'")

    # Required: title
    title = item.get("title")
    if not title or not str(title).strip():
        errors.append(f"{filename}: missing or empty required field 'title'")

    # Required: type
    m_type = item.get("type")
    if not m_type:
        errors.append(f"{filename}: missing required field 'type'")
    elif m_type not in VALID_TYPES:
        errors.append(f"{filename}: invalid type '{m_type}', must be one of {sorted(list(VALID_TYPES))}")

    # Check link
    link = item.get("link")
    if link and not str(link).startswith(("http://", "https://")):
        warnings.append(f"{filename}: link '{link}' does not start with http:// or https://")

    # Boolean field
    sel = item.get("selected")
    if sel is not None and not isinstance(sel, bool):
        errors.append(f"{filename}: 'selected' must be boolean")

    return errors, warnings

def load_press_items(directory=PRESS_DIR, validate=True):
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
            errs, warns = validate_press_item(data, fpath)
            all_errors.extend(errs)
            all_warnings.extend(warns)

        items.append(data)

    # Sort: newest first
    items.sort(key=lambda x: (str(x.get("date", "2000-01-01")), str(x.get("title", ""))), reverse=True)

    return items, all_errors, all_warnings

def compile_press_review(check_only=False, verbose=True):
    if verbose:
        print(f"Loading and validating press review from {PRESS_DIR}...")

    items, errors, warnings = load_press_items(PRESS_DIR, validate=True)

    if warnings and verbose:
        for w in warnings[:10]:
            print(f"  [WARN] {w}")
        if len(warnings) > 10:
            print(f"  ... and {len(warnings) - 10} more warnings.")

    if errors:
        print(f"\n❌ Found {len(errors)} validation error(s) in press review YAMLs:")
        for e in errors:
            print(f"  - {e}")
        return False

    if verbose:
        by_type = {}
        for it in items:
            t = it.get("type", "other")
            by_type[t] = by_type.get(t, 0) + 1
        type_str = ", ".join(f"{k}: {v}" for k, v in sorted(by_type.items()))
        print(f"✅ Validated {len(items)} press mentions ({type_str})")

    if check_only:
        return True

    # 1. Write compiled data/press-review-merged.json
    with open(COMPILED_JSON, "w", encoding="utf-8") as f:
        json.dump(items, f, ensure_ascii=False, indent=2)
    if verbose:
        print(f"Wrote compiled {COMPILED_JSON} ({len(items)} items)")

    # 2. Re-generate press review HTML pages
    sys.path.insert(0, os.path.dirname(__file__))
    import generate_press_review
    generate_press_review.main(items=items)

    return True

if __name__ == "__main__":
    check_mode = "--check" in sys.argv
    success = compile_press_review(check_only=check_mode, verbose=True)
    sys.exit(0 if success else 1)
