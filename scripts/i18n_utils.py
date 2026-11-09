#!/usr/bin/env python3
"""
Internationalization (i18n) and Localization (l10n) utilities for Open Food Facts Web data.
Provides consistent field-level translation resolution and validation across all
YAML-based compilation pipelines (queries, reuses, scan parties, missions, publications).
"""

import os
import sys

DEFAULT_LANG = "en"
SUPPORTED_LANGUAGES = [
    "en", "fr", "es", "de", "it",
    "nl", "pt", "pl", "ru", "ca",
    "ro", "cs", "sv", "da", "fi",
    "el", "hu", "ja", "zh", "ar",
    "uk", "tr", "id", "ko", "no", "he"
]

def get_localized_field(item, field, lang="en", default_lang=DEFAULT_LANG):
    """
    Retrieve a localized string from an item for a given field and language.
    
    Supports:
    1. Multilingual mapping dictionary:
       item[field] = {"en": "Text", "fr": "Texte"}
    2. Language suffix keys (legacy / flat format):
       item[f"{field}_{lang}"] (e.g. title_fr, tagline_en)
    3. Plain string fallback:
       item[field] = "Text" (used as default_lang)
    4. Default language fallback (if requested translation is missing)
    5. First available non-empty translation
    """
    if not isinstance(item, dict):
        return ""

    val = item.get(field)

    # 1. Dictionary format: { "en": "...", "fr": "..." }
    if isinstance(val, dict):
        # Explicit target language requested
        if lang in val and str(val[lang]).strip():
            return str(val[lang]).strip()
        # Fallback to default language
        if default_lang in val and str(val[default_lang]).strip():
            return str(val[default_lang]).strip()
        # Fallback to first non-empty string in dict
        for k, v in val.items():
            if str(v).strip():
                return str(v).strip()
        return ""

    # 2. Suffixed key format for target lang (e.g. title_fr, tagline_es)
    suffixed_target = item.get(f"{field}_{lang}")
    if suffixed_target is not None and str(suffixed_target).strip():
        return str(suffixed_target).strip()

    # 3. Base field is string and target is default_lang
    if lang == default_lang and isinstance(val, str) and val.strip():
        return val.strip()

    # 4. Suffixed key for default_lang (e.g. title_en)
    suffixed_default = item.get(f"{field}_{default_lang}")
    if suffixed_default is not None and str(suffixed_default).strip():
        return str(suffixed_default).strip()

    # 5. Fallback to base field as string
    if isinstance(val, str) and val.strip():
        return val.strip()

    return ""


def validate_localized_field(item, field, filename, required=True, allowed_langs=None):
    """
    Validate that a localized field in a YAML entity is well-formed.
    Accepts:
    - Non-empty string
    - Mapping dictionary of lang_code -> string with at least one non-empty value
    - One or more suffixed keys (e.g. field_en, field_fr)
    
    Returns a list of error strings (empty if valid).
    """
    errors = []
    val = item.get(field)

    if val is None:
        # Check if any suffixed key exists (e.g. field_en, field_fr)
        suffixed = [
            k for k in item.keys()
            if k.startswith(f"{field}_") and str(item[k]).strip()
        ]
        if not suffixed:
            if required:
                errors.append(f"{filename}: missing required field '{field}'")
        return errors

    if isinstance(val, dict):
        has_valid_text = False
        for lang_code, text in val.items():
            if not isinstance(lang_code, str) or not lang_code.strip():
                errors.append(f"{filename}: field '{field}' has invalid language key '{lang_code}'")
            elif allowed_langs and lang_code not in allowed_langs:
                errors.append(f"{filename}: field '{field}' has unsupported language code '{lang_code}'")
            if text and str(text).strip():
                has_valid_text = True
        if required and not has_valid_text:
            errors.append(f"{filename}: field '{field}' translation dictionary has no non-empty values")
    elif isinstance(val, str):
        if required and not val.strip():
            errors.append(f"{filename}: missing or empty required field '{field}'")
    else:
        errors.append(f"{filename}: field '{field}' must be a string or language mapping dictionary, got {type(val).__name__}")

    return errors


def ensure_vendor_path():
    """Ensure repository-local vendor directory is on sys.path if present."""
    repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    vendor_dir = os.path.join(repo_root, "vendor")
    if os.path.isdir(vendor_dir) and vendor_dir not in sys.path:
        sys.path.insert(0, vendor_dir)
