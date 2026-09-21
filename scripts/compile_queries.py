#!/usr/bin/env python3
"""
Compilation and validation system for Open Food Facts Useful Queries.
Reads individual YAML files from data/queries/*.yaml,
validates schemas, compiles data/queries.json, and generates modernized
interactive tutorial and showcase HTML pages in:
- lang/en/texts/graphs-in-3-clicks.html
- lang/fr/texts/graphs-in-3-clicks.html

Usage:
    python3 scripts/compile_queries.py          # Validate and compile
    python3 scripts/compile_queries.py --check  # Validate only (CI friendly)
"""

import glob
import html
import json
import os
import re
import sys
import yaml

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
DATA_DIR = os.path.join(REPO_ROOT, "data")
QUERIES_DIR = os.path.join(DATA_DIR, "queries")
COMPILED_JSON = os.path.join(DATA_DIR, "queries.json")

VALID_TOPICS = {
    "beverages": {"en": "Beverages", "fr": "Boissons", "icon": "🥤"},
    "dairy": {"en": "Dairy & Cheeses", "fr": "Produits laitiers & Fromages", "icon": "🧀"},
    "breakfast": {"en": "Breakfast & Cereals", "fr": "Petit-déjeuner & Céréales", "icon": "🥣"},
    "sweets": {"en": "Sweets & Spreads", "fr": "Douceurs & Pâtes à tartiner", "icon": "🍫"},
    "meat": {"en": "Meat & Charcuterie", "fr": "Viandes & Charcuterie", "icon": "🥩"},
    "meals": {"en": "Ready Meals & Prepared", "fr": "Plats préparés", "icon": "🍲"},
    "nutrition": {"en": "Nutrition & Scores", "fr": "Nutrition & Scores", "icon": "🥗"},
    "quality": {"en": "Data Quality & Contributor Tools", "fr": "Qualité des données & Outils", "icon": "🛠️"},
}

VALID_QUERY_TYPES = {
    "scatter_plot": {"en": "Scatter Plot", "fr": "Nuage de points", "icon": "📈"},
    "bar_chart": {"en": "Bar Chart", "fr": "Histogramme", "icon": "📊"},
    "map": {"en": "Origins Map", "fr": "Carte d'origines", "icon": "🗺️"},
    "list": {"en": "Product List", "fr": "Liste de produits", "icon": "📋"},
    "facet": {"en": "Taxonomy Facet", "fr": "Facette taxonomique", "icon": "🔍"},
}

GEO_NAMES = {
    "world": {"en": "Worldwide", "fr": "Monde", "flag": "🌍"},
    "fr": {"en": "France", "fr": "France", "flag": "🇫🇷"},
    "uk": {"en": "United Kingdom", "fr": "Royaume-Uni", "flag": "🇬🇧"},
    "be": {"en": "Belgium", "fr": "Belgique", "flag": "🇧🇪"},
    "de": {"en": "Germany", "fr": "Allemagne", "flag": "🇩🇪"},
    "es": {"en": "Spain", "fr": "Espagne", "flag": "🇪🇸"},
    "us": {"en": "United States", "fr": "États-Unis", "flag": "🇺🇸"},
}

def validate_query(item, filepath):
    errors = []
    warnings = []
    filename = os.path.basename(filepath)
    stem = filename[:-5] if filename.endswith(".yaml") else filename[:-4]

    # Required: id
    q_id = item.get("id")
    if not q_id:
        errors.append(f"{filename}: missing required field 'id'")
    elif q_id != stem:
        errors.append(f"{filename}: id '{q_id}' does not match filename stem '{stem}'")
    elif not re.match(r"^[a-zA-Z0-9_-]+$", str(q_id)):
        errors.append(f"{filename}: id '{q_id}' contains invalid characters (must be alphanumeric, hyphens, or underscores)")

    # Required: title
    title = item.get("title")
    if not title or not str(title).strip():
        errors.append(f"{filename}: missing or empty required field 'title'")

    # Required: description
    desc = item.get("description")
    if not desc or not str(desc).strip():
        errors.append(f"{filename}: missing or empty required field 'description'")

    # Required: topic
    topic = item.get("topic")
    if not topic:
        errors.append(f"{filename}: missing required field 'topic'")
    elif topic not in VALID_TOPICS:
        errors.append(f"{filename}: invalid topic '{topic}', must be one of {sorted(list(VALID_TOPICS.keys()))}")

    # Required: query_type
    q_type = item.get("query_type")
    if not q_type:
        errors.append(f"{filename}: missing required field 'query_type'")
    elif q_type not in VALID_QUERY_TYPES:
        errors.append(f"{filename}: invalid query_type '{q_type}', must be one of {sorted(list(VALID_QUERY_TYPES.keys()))}")

    # Required: geographies
    geos = item.get("geographies")
    if not geos or not isinstance(geos, list):
        errors.append(f"{filename}: 'geographies' must be a non-empty list of country codes (e.g. ['world', 'fr'])")

    # Required: url
    url = item.get("url")
    if not url or not str(url).strip():
        errors.append(f"{filename}: missing required field 'url'")
    elif not (url.startswith("http://") or url.startswith("https://") or url.startswith("/")):
        errors.append(f"{filename}: url must start with http://, https://, or /")

    # Optional: tags_combined
    tags_combined = item.get("tags_combined")
    if tags_combined is not None and not isinstance(tags_combined, list):
        errors.append(f"{filename}: 'tags_combined' must be a list of strings")

    # Optional: featured
    featured = item.get("featured")
    if featured is not None and not isinstance(featured, bool):
        errors.append(f"{filename}: 'featured' must be a boolean (true/false)")

    return errors, warnings

def load_queries(directory=QUERIES_DIR, validate=True):
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
            errs, warns = validate_query(data, fpath)
            all_errors.extend(errs)
            all_warnings.extend(warns)

        items.append(data)

    # Sort: featured first, then case-insensitive by title
    items.sort(key=lambda x: (not x.get("featured", False), (x.get("title") or "").lower()))

    return items, all_errors, all_warnings

def generate_css():
    return """
<style>
/* ==========================================================================
   Open Food Facts: Graphs in 3 Clicks & Useful Queries Modern Showcase
   ========================================================================== */

:root {
  --off-green-900: #064e3b;
  --off-green-800: #065f46;
  --off-green-700: #047857;
  --off-green-600: #059669;
  --off-green-500: #10b981;
  --off-green-100: #d1fae5;
  --off-green-50: #ecfdf5;
  --off-surface: #ffffff;
  --off-bg: #f8fafc;
  --off-border: #e2e8f0;
  --off-border-hover: #cbd5e1;
  --off-text-primary: #0f172a;
  --off-text-secondary: #475569;
  --off-text-muted: #64748b;
  --off-accent: #2563eb;
  --off-accent-bg: #eff6ff;
  --off-warn-bg: #fffbeb;
  --off-warn-border: #fde68a;
  --off-warn-text: #92400e;
  --off-shadow-sm: 0 1px 3px rgba(0,0,0,0.05);
  --off-shadow-md: 0 4px 14px rgba(0,0,0,0.06);
  --off-shadow-hover: 0 10px 25px rgba(4, 120, 87, 0.10);
  --off-radius-card: 16px;
  --off-radius-pill: 9999px;
  --off-radius-sm: 8px;
}

.g3c-container {
  max-width: 1140px;
  margin: 0 auto;
  padding: 1.5rem 1rem 4rem;
  color: var(--off-text-primary);
  font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Oxygen, Ubuntu, Cantarell, "Open Sans", "Helvetica Neue", sans-serif;
  line-height: 1.6;
}

/* Hero Section */
.g3c-hero {
  text-align: center;
  padding: 2.5rem 1.5rem 2rem;
  background: linear-gradient(135deg, var(--off-green-50) 0%, #ffffff 100%);
  border: 1px solid var(--off-border);
  border-radius: var(--off-radius-card);
  margin-bottom: 2.5rem;
  box-shadow: var(--off-shadow-sm);
}

.g3c-badge {
  display: inline-flex;
  align-items: center;
  gap: 0.35rem;
  background: var(--off-green-100);
  color: var(--off-green-900);
  font-size: 0.85rem;
  font-weight: 700;
  padding: 0.35rem 0.85rem;
  border-radius: var(--off-radius-pill);
  margin-bottom: 1rem;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.g3c-hero-title {
  font-size: 2.5rem;
  font-weight: 800;
  color: var(--off-green-900);
  margin: 0 0 0.75rem;
  line-height: 1.2;
  letter-spacing: -0.025em;
}

.g3c-hero-subtitle {
  font-size: 1.2rem;
  color: var(--off-text-secondary);
  max-width: 760px;
  margin: 0 auto 1.5rem;
}

.g3c-quote-card {
  display: inline-block;
  background: var(--off-surface);
  border-left: 4px solid var(--off-green-600);
  padding: 0.75rem 1.25rem;
  border-radius: 0 var(--off-radius-sm) var(--off-radius-sm) 0;
  font-style: italic;
  color: var(--off-green-800);
  font-weight: 500;
  box-shadow: var(--off-shadow-sm);
  margin-bottom: 1.75rem;
}

.g3c-hero-actions {
  display: flex;
  flex-wrap: wrap;
  gap: 0.75rem;
  justify-content: center;
  align-items: center;
}

.g3c-btn {
  display: inline-flex;
  align-items: center;
  gap: 0.45rem;
  padding: 0.75rem 1.35rem;
  border-radius: var(--off-radius-pill);
  font-weight: 600;
  font-size: 0.95rem;
  text-decoration: none;
  cursor: pointer;
  transition: all 0.2s ease;
  border: 1px solid transparent;
}

.g3c-btn-primary {
  background: var(--off-green-700);
  color: #ffffff !important;
  box-shadow: 0 2px 6px rgba(4, 120, 87, 0.25);
}
.g3c-btn-primary:hover {
  background: var(--off-green-800);
  transform: translateY(-1px);
  box-shadow: 0 4px 10px rgba(4, 120, 87, 0.35);
}

.g3c-btn-secondary {
  background: var(--off-surface);
  color: var(--off-green-800) !important;
  border-color: var(--off-border);
}
.g3c-btn-secondary:hover {
  border-color: var(--off-green-600);
  background: var(--off-green-50);
}

/* 3 Clicks Visual Workflow */
.g3c-workflow {
  margin-bottom: 3.5rem;
}

.g3c-section-header {
  text-align: center;
  margin-bottom: 2rem;
}

.g3c-section-title {
  font-size: 1.85rem;
  font-weight: 800;
  color: var(--off-green-900);
  margin: 0 0 0.5rem;
}

.g3c-section-subtitle {
  color: var(--off-text-secondary);
  font-size: 1.05rem;
  max-width: 680px;
  margin: 0 auto;
}

.g3c-steps-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 1.5rem;
  margin-bottom: 2rem;
}

.g3c-step-card {
  background: var(--off-surface);
  border: 1px solid var(--off-border);
  border-radius: var(--off-radius-card);
  padding: 1.75rem 1.5rem;
  box-shadow: var(--off-shadow-sm);
  transition: all 0.25s ease;
  position: relative;
  display: flex;
  flex-direction: column;
}

.g3c-step-card:hover {
  border-color: var(--off-green-600);
  box-shadow: var(--off-shadow-hover);
  transform: translateY(-2px);
}

.g3c-step-number {
  position: absolute;
  top: 1rem;
  right: 1.25rem;
  font-size: 2.2rem;
  font-weight: 900;
  color: var(--off-green-100);
  line-height: 1;
}

.g3c-step-icon {
  font-size: 2rem;
  margin-bottom: 0.75rem;
}

.g3c-step-title {
  font-size: 1.25rem;
  font-weight: 700;
  color: var(--off-green-900);
  margin: 0 0 0.65rem;
}

.g3c-step-desc {
  color: var(--off-text-secondary);
  font-size: 0.95rem;
  margin: 0 0 1rem;
  flex-grow: 1;
}

.g3c-step-features {
  list-style: none;
  padding: 0;
  margin: 0;
  font-size: 0.88rem;
  color: var(--off-text-muted);
}

.g3c-step-features li {
  margin-bottom: 0.4rem;
  display: flex;
  align-items: center;
  gap: 0.4rem;
}

/* Callout Box */
.g3c-callout {
  background: var(--off-warn-bg);
  border: 1px solid var(--off-warn-border);
  border-radius: var(--off-radius-card);
  padding: 1.25rem 1.5rem;
  margin-bottom: 2.5rem;
  display: flex;
  gap: 1rem;
  align-items: flex-start;
}

.g3c-callout-icon {
  font-size: 1.5rem;
  line-height: 1;
}

.g3c-callout-body h4 {
  margin: 0 0 0.35rem;
  color: var(--off-warn-text);
  font-size: 1.05rem;
}

.g3c-callout-body p {
  margin: 0;
  color: #78350f;
  font-size: 0.92rem;
  line-height: 1.5;
}

/* Showcase & Filters Section */
.g3c-showcase-section {
  background: var(--off-surface);
  border: 1px solid var(--off-border);
  border-radius: var(--off-radius-card);
  padding: 2rem 1.5rem;
  box-shadow: var(--off-shadow-sm);
  margin-bottom: 3rem;
}

.g3c-controls-wrap {
  background: var(--off-bg);
  border: 1px solid var(--off-border);
  border-radius: var(--off-radius-card);
  padding: 1.5rem;
  margin-bottom: 2rem;
}

.g3c-search-bar {
  position: relative;
  margin-bottom: 1.25rem;
}

.g3c-search-input {
  width: 100%;
  box-sizing: border-box;
  padding: 0.85rem 1rem 0.85rem 2.75rem;
  font-size: 1rem;
  border: 1px solid var(--off-border);
  border-radius: var(--off-radius-pill);
  background: var(--off-surface);
  color: var(--off-text-primary);
  outline: none;
  transition: all 0.2s ease;
}

.g3c-search-input:focus {
  border-color: var(--off-green-600);
  box-shadow: 0 0 0 3px rgba(16, 185, 129, 0.2);
}

.g3c-search-icon {
  position: absolute;
  left: 1rem;
  top: 50%;
  transform: translateY(-50%);
  color: var(--off-text-muted);
  font-size: 1.1rem;
  pointer-events: none;
}

/* Filter Groups */
.g3c-filter-group {
  margin-bottom: 1rem;
}

.g3c-filter-group:last-child {
  margin-bottom: 0;
}

.g3c-filter-label {
  display: block;
  font-size: 0.82rem;
  font-weight: 700;
  color: var(--off-text-muted);
  text-transform: uppercase;
  letter-spacing: 0.04em;
  margin-bottom: 0.5rem;
}

.g3c-pills-row {
  display: flex;
  flex-wrap: wrap;
  gap: 0.4rem;
}

.g3c-pill-btn {
  background: var(--off-surface);
  border: 1px solid var(--off-border);
  border-radius: var(--off-radius-pill);
  padding: 0.35rem 0.75rem;
  font-size: 0.85rem;
  color: var(--off-text-secondary);
  cursor: pointer;
  transition: all 0.15s ease;
  display: inline-flex;
  align-items: center;
  gap: 0.3rem;
  user-select: none;
}

.g3c-pill-btn:hover {
  border-color: var(--off-green-600);
  color: var(--off-green-900);
}

.g3c-pill-btn.active {
  background: var(--off-green-700);
  border-color: var(--off-green-700);
  color: #ffffff;
  font-weight: 600;
}

/* Secondary Filters Row */
.g3c-secondary-filters {
  display: flex;
  flex-wrap: wrap;
  gap: 1rem;
  margin-top: 1rem;
  padding-top: 1rem;
  border-top: 1px dashed var(--off-border);
  align-items: center;
  justify-content: space-between;
}

.g3c-select-wrap {
  display: flex;
  flex-wrap: wrap;
  gap: 0.75rem;
  align-items: center;
}

.g3c-select {
  padding: 0.45rem 0.85rem;
  border-radius: var(--off-radius-sm);
  border: 1px solid var(--off-border);
  background: var(--off-surface);
  font-size: 0.88rem;
  color: var(--off-text-primary);
  outline: none;
}

.g3c-select:focus {
  border-color: var(--off-green-600);
}

.g3c-stats-and-reset {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  font-size: 0.88rem;
}

.g3c-count-badge {
  background: var(--off-green-100);
  color: var(--off-green-900);
  padding: 0.25rem 0.65rem;
  border-radius: var(--off-radius-pill);
  font-weight: 700;
}

.g3c-reset-btn {
  background: none;
  border: none;
  color: var(--off-text-muted);
  text-decoration: underline;
  cursor: pointer;
  font-size: 0.85rem;
  padding: 0.2rem 0.4rem;
}
.g3c-reset-btn:hover {
  color: var(--off-green-900);
}

/* Cards Grid */
.g3c-cards-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
  gap: 1.25rem;
}

.g3c-query-card {
  background: var(--off-surface);
  border: 1px solid var(--off-border);
  border-radius: var(--off-radius-card);
  padding: 1.25rem;
  box-shadow: var(--off-shadow-sm);
  display: flex;
  flex-direction: column;
  transition: all 0.2s ease;
  position: relative;
}

.g3c-query-card:hover {
  border-color: var(--off-green-600);
  box-shadow: var(--off-shadow-hover);
  transform: translateY(-2px);
}

.g3c-query-card.featured {
  border-left: 4px solid var(--off-green-600);
}

.g3c-card-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 0.6rem;
  gap: 0.5rem;
}

.g3c-card-tags-top {
  display: flex;
  flex-wrap: wrap;
  gap: 0.3rem;
  align-items: center;
}

.g3c-type-badge {
  font-size: 0.75rem;
  font-weight: 700;
  padding: 0.2rem 0.55rem;
  border-radius: var(--off-radius-pill);
  background: #f1f5f9;
  color: var(--off-text-secondary);
}

.g3c-type-badge.scatter_plot { background: #eff6ff; color: #1d4ed8; }
.g3c-type-badge.bar_chart { background: #fdf2f8; color: #be185d; }
.g3c-type-badge.map { background: #ecfdf5; color: #047857; }
.g3c-type-badge.list { background: #fefce8; color: #a16207; }
.g3c-type-badge.facet { background: #faf5ff; color: #7e22ce; }

.g3c-geo-badge {
  font-size: 0.75rem;
  padding: 0.2rem 0.5rem;
  border-radius: var(--off-radius-pill);
  background: #f8fafc;
  border: 1px solid var(--off-border);
  color: var(--off-text-secondary);
}

.g3c-featured-star {
  color: #f59e0b;
  font-size: 0.9rem;
  cursor: help;
}

.g3c-card-title {
  font-size: 1.1rem;
  font-weight: 700;
  color: var(--off-green-900);
  margin: 0 0 0.45rem;
  line-height: 1.35;
}

.g3c-card-desc {
  font-size: 0.9rem;
  color: var(--off-text-secondary);
  line-height: 1.45;
  margin: 0 0 0.85rem;
  flex-grow: 1;
}

.g3c-author-line {
  font-size: 0.78rem;
  color: var(--off-text-muted);
  margin-bottom: 0.75rem;
  font-style: italic;
}

/* Combined Tags Chips */
.g3c-chips-wrap {
  display: flex;
  flex-wrap: wrap;
  gap: 0.35rem;
  margin-bottom: 1rem;
}

.g3c-chip {
  font-size: 0.74rem;
  font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace;
  padding: 0.15rem 0.5rem;
  border-radius: var(--off-radius-sm);
  background: #f1f5f9;
  color: #334155;
  border: 1px solid #e2e8f0;
}

.g3c-chip.category { background: #f0fdf4; border-color: #bbf7d0; color: #166534; }
.g3c-chip.axis { background: #eff6ff; border-color: #bfdbfe; color: #1e40af; }
.g3c-chip.label { background: #fef3c7; border-color: #fde68a; color: #92400e; }
.g3c-chip.ingredient { background: #faf5ff; border-color: #e9d5ff; color: #6b21a8; }
.g3c-chip.state { background: #f8fafc; border-color: #e2e8f0; color: #475569; }

/* Card Actions */
.g3c-card-footer {
  display: flex;
  flex-wrap: wrap;
  gap: 0.45rem;
  align-items: center;
  padding-top: 0.75rem;
  border-top: 1px solid var(--off-border);
}

.g3c-run-btn {
  flex-grow: 1;
  text-align: center;
  padding: 0.5rem 0.85rem;
  font-size: 0.85rem;
  font-weight: 600;
  border-radius: var(--off-radius-sm);
  background: var(--off-green-700);
  color: #ffffff !important;
  text-decoration: none;
  transition: all 0.15s ease;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 0.35rem;
}

.g3c-run-btn:hover {
  background: var(--off-green-800);
}

.g3c-copy-btn {
  padding: 0.5rem 0.65rem;
  font-size: 0.85rem;
  border: 1px solid var(--off-border);
  background: var(--off-surface);
  border-radius: var(--off-radius-sm);
  cursor: pointer;
  color: var(--off-text-secondary);
  transition: all 0.15s ease;
}

.g3c-copy-btn:hover {
  border-color: var(--off-green-600);
  color: var(--off-green-900);
  background: var(--off-green-50);
}

/* Expandable Params */
.g3c-params-details {
  margin-top: 0.5rem;
  font-size: 0.78rem;
  color: var(--off-text-muted);
}

.g3c-params-details summary {
  cursor: pointer;
  user-select: none;
  color: var(--off-text-secondary);
  padding: 0.2rem 0;
}

.g3c-params-details summary:hover {
  color: var(--off-green-700);
}

.g3c-params-pre {
  background: #f8fafc;
  padding: 0.5rem;
  border-radius: var(--off-radius-sm);
  border: 1px solid var(--off-border);
  overflow-x: auto;
  margin: 0.35rem 0 0;
  font-family: ui-monospace, SFMono-Regular, monospace;
}

/* Spotlight Example */
.g3c-spotlight-card {
  background: var(--off-surface);
  border: 1px solid var(--off-border);
  border-radius: var(--off-radius-card);
  padding: 1.75rem;
  box-shadow: var(--off-shadow-sm);
  margin-bottom: 2.5rem;
}
.g3c-spotlight-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1.75rem;
  align-items: center;
}
.g3c-spotlight-img {
  width: 100%;
  max-width: 100%;
  height: auto;
  border-radius: 12px;
  border: 1px solid var(--off-border);
  box-shadow: var(--off-shadow-sm);
  display: block;
}
.g3c-spotlight-content h3 {
  font-size: 1.35rem;
  font-weight: 800;
  color: var(--off-green-900);
  margin: 0 0 0.5rem;
}
.g3c-spotlight-content p {
  color: var(--off-text-secondary);
  font-size: 0.95rem;
  line-height: 1.5;
  margin: 0 0 1rem;
}

/* Formats Grid */
.g3c-formats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: 1.25rem;
  margin-bottom: 2.5rem;
}
.g3c-format-card {
  background: var(--off-surface);
  border: 1px solid var(--off-border);
  border-radius: var(--off-radius-card);
  padding: 1.35rem;
  box-shadow: var(--off-shadow-sm);
}
.g3c-format-card h4 {
  font-size: 1.1rem;
  font-weight: 700;
  color: var(--off-green-900);
  margin: 0 0 0.4rem;
  display: flex;
  align-items: center;
  gap: 0.45rem;
}
.g3c-format-card p {
  font-size: 0.9rem;
  color: var(--off-text-secondary);
  margin: 0;
  line-height: 1.45;
}

@media (max-width: 768px) {
  .g3c-spotlight-grid {
    grid-template-columns: 1fr;
  }
}

/* Empty State */
.g3c-no-results {
  grid-column: 1 / -1;
  text-align: center;
  padding: 3rem 1.5rem;
  color: var(--off-text-muted);
}
.g3c-no-results-icon {
  font-size: 2.5rem;
  margin-bottom: 0.5rem;
}

/* Contribute Banner */
.g3c-contribute-box {
  background: linear-gradient(135deg, #f0fdf4 0%, #ffffff 100%);
  border: 1px solid var(--off-green-100);
  border-radius: var(--off-radius-card);
  padding: 1.75rem;
  text-align: center;
  margin-top: 2.5rem;
}
.g3c-contribute-title {
  color: var(--off-green-900);
  font-size: 1.25rem;
  font-weight: 700;
  margin: 0 0 0.5rem;
}
.g3c-contribute-desc {
  color: var(--off-text-secondary);
  font-size: 0.95rem;
  max-width: 650px;
  margin: 0 auto 1.25rem;
}

/* Toast Notification */
.g3c-toast {
  position: fixed;
  bottom: 1.5rem;
  right: 1.5rem;
  background: var(--off-green-900);
  color: #ffffff;
  padding: 0.75rem 1.25rem;
  border-radius: var(--off-radius-pill);
  font-size: 0.9rem;
  font-weight: 600;
  box-shadow: 0 8px 24px rgba(0,0,0,0.18);
  opacity: 0;
  pointer-events: none;
  transform: translateY(12px);
  transition: all 0.25s ease;
  z-index: 9999;
}
.g3c-toast.show {
  opacity: 1;
  transform: translateY(0);
}

@media (max-width: 768px) {
  .g3c-hero-title { font-size: 1.85rem; }
  .g3c-hero-subtitle { font-size: 1rem; }
  .g3c-cards-grid { grid-template-columns: 1fr; }
  .g3c-secondary-filters { flex-direction: column; align-items: stretch; }
}
</style>
"""

def generate_js(lang="en"):
    is_fr = (lang == "fr")
    copied_text = "Lien copié dans le presse-papiers !" if is_fr else "Search link copied to clipboard!"
    return f"""
<script>
document.addEventListener('DOMContentLoaded', function() {{
  const searchInput = document.getElementById('g3c-search');
  const topicPills = document.querySelectorAll('.g3c-topic-pill');
  const typeSelect = document.getElementById('g3c-type-select');
  const geoSelect = document.getElementById('g3c-geo-select');
  const sortSelect = document.getElementById('g3c-sort-select');
  const resetBtn = document.getElementById('g3c-reset');
  const cards = Array.from(document.querySelectorAll('.g3c-query-card'));
  const countBadge = document.getElementById('g3c-count');
  const noResults = document.getElementById('g3c-no-results');
  const cardsContainer = document.getElementById('g3c-cards-grid');

  let activeTopic = 'all';

  function filterCards() {{
    const query = (searchInput ? searchInput.value : '').toLowerCase().trim();
    const selectedType = typeSelect ? typeSelect.value : 'all';
    const selectedGeo = geoSelect ? geoSelect.value : 'all';

    let visibleCount = 0;

    cards.forEach(card => {{
      const topic = card.getAttribute('data-topic') || '';
      const type = card.getAttribute('data-type') || '';
      const geos = (card.getAttribute('data-geos') || '').split(',');
      const searchTarget = (card.getAttribute('data-search') || '').toLowerCase();

      let matchTopic = (activeTopic === 'all') || (topic === activeTopic);
      let matchType = (selectedType === 'all') || (type === selectedType);
      let matchGeo = (selectedGeo === 'all') || geos.includes(selectedGeo);
      let matchQuery = !query || searchTarget.includes(query);

      if (matchTopic && matchType && matchGeo && matchQuery) {{
        card.style.display = 'flex';
        visibleCount++;
      }} else {{
        card.style.display = 'none';
      }}
    }});

    if (countBadge) {{
      countBadge.textContent = visibleCount;
    }}
    if (noResults) {{
      noResults.style.display = visibleCount === 0 ? 'block' : 'none';
    }}
  }}

  // Topic pills click
  topicPills.forEach(pill => {{
    pill.addEventListener('click', function() {{
      topicPills.forEach(p => p.classList.remove('active'));
      this.classList.add('active');
      activeTopic = this.getAttribute('data-topic') || 'all';
      filterCards();
    }});
  }});

  // Search input with debounce
  let debounceTimeout;
  if (searchInput) {{
    searchInput.addEventListener('input', function() {{
      clearTimeout(debounceTimeout);
      debounceTimeout = setTimeout(filterCards, 150);
    }});
  }}

  if (typeSelect) typeSelect.addEventListener('change', filterCards);
  if (geoSelect) geoSelect.addEventListener('change', filterCards);

  // Sorting
  if (sortSelect) {{
    sortSelect.addEventListener('change', function() {{
      const sortVal = this.value;
      cards.sort((a, b) => {{
        if (sortVal === 'featured') {{
          const aFeat = a.classList.contains('featured') ? 0 : 1;
          const bFeat = b.classList.contains('featured') ? 0 : 1;
          if (aFeat !== bFeat) return aFeat - bFeat;
          return a.getAttribute('data-title').localeCompare(b.getAttribute('data-title'));
        }} else if (sortVal === 'title') {{
          return a.getAttribute('data-title').localeCompare(b.getAttribute('data-title'));
        }} else if (sortVal === 'topic') {{
          return a.getAttribute('data-topic').localeCompare(b.getAttribute('data-topic'));
        }}
        return 0;
      }});
      cards.forEach(card => cardsContainer.appendChild(card));
      filterCards();
    }});
  }}

  // Reset button
  if (resetBtn) {{
    resetBtn.addEventListener('click', function(e) {{
      e.preventDefault();
      if (searchInput) searchInput.value = '';
      if (typeSelect) typeSelect.value = 'all';
      if (geoSelect) geoSelect.value = 'all';
      if (sortSelect) sortSelect.value = 'featured';
      topicPills.forEach(p => p.classList.remove('active'));
      const allPill = document.querySelector('.g3c-topic-pill[data-topic=\"all\"]');
      if (allPill) allPill.classList.add('active');
      activeTopic = 'all';
      filterCards();
    }});
  }}

  // Copy buttons & Toast
  const toast = document.getElementById('g3c-toast');
  function showToast(msg) {{
    if (!toast) return;
    toast.textContent = msg;
    toast.classList.add('show');
    setTimeout(() => toast.classList.remove('show'), 2500);
  }}

  document.querySelectorAll('.g3c-copy-btn').forEach(btn => {{
    btn.addEventListener('click', function() {{
      const url = this.getAttribute('data-url');
      if (!url) return;
      if (navigator.clipboard && navigator.clipboard.writeText) {{
        navigator.clipboard.writeText(url).then(() => {{
          showToast('{copied_text}');
        }}).catch(() => {{
          promptCopy(url);
        }});
      }} else {{
        promptCopy(url);
      }}
    }});
  }});

  function promptCopy(text) {{
    window.prompt('Copy query URL:', text);
  }}

  filterCards();
}});
</script>
"""

def generate_page_html(queries, lang="en"):
    is_fr = (lang == "fr")

    # Titles & UI strings
    t_page_title = "Recherche avancée et Graphiques en 3 clics" if is_fr else "Advanced Search & Visualizations: Graphs in 3 Clicks"
    t_hero_badge = "Visualisation de Données Ouvertes" if is_fr else "Open Data Visualizations"
    t_hero_subtitle = (
        "Explorez la base mondiale d'Open Food Facts sous forme de nuages de points interactifs, cartes d'origines, histogrammes comparatifs et exports sur-mesure."
        if is_fr else
        "Explore millions of open food products with interactive scatter plots, origin maps, comparison bar charts, and custom data exports in seconds."
    )
    t_hero_quote = "Si une image vaut 1000 mots, elle vaut aussi 1000 chiffres !" if is_fr else "If a picture is worth 1,000 words, it is also worth 1,000 digits!"
    t_btn_search = "🚀 Lancer la Recherche Avancée" if is_fr else "🚀 Launch Advanced Search"
    t_btn_showcase = "✨ Découvrir les Requêtes Utiles" if is_fr else "✨ Explore Useful Queries"
    t_btn_skip = "Passer le tutoriel" if is_fr else "Skip Tutorial"

    # 3 Clicks Section
    t_workflow_title = "Comment créer un graphique en 3 clics" if is_fr else "How to Create a Graph in 3 Clicks"
    t_workflow_sub = (
        "Le moteur de recherche avancée d'Open Food Facts vous permet d'analyser n'importe quel segment du marché alimentaire."
        if is_fr else
        "The Open Food Facts advanced search engine lets you filter and correlate any segment of the global food database."
    )

    t_step1_title = "1. Définir filtres et périmètre" if is_fr else "1. Scope & Filter Products"
    t_step1_desc = (
        "Choisissez jusqu'à 5 critères simultanés : catégorie (ex: céréales, fromages), pays de vente, marque, labels (Bio, Commerce équitable) ou notes Nutri-Score."
        if is_fr else
        "Combine up to 5 simultaneous criteria: category (e.g. cereals, cheeses), country of sale, brand, labels (Organic, Fair Trade), or Nutri-Score grades."
    )
    t_step1_f1 = "Catégories, marques, ingrédients" if is_fr else "Categories, brands, ingredients"
    t_step1_f2 = "Filtrage par pays et labels qualité" if is_fr else "Country of sale & quality labels"
    t_step1_f3 = "Critères cumulatifs (ET / OU)" if is_fr else "Multi-criteria Boolean filtering"

    t_step2_title = "2. Choisir vos axes d'analyse" if is_fr else "2. Select Axes & Visualization"
    t_step2_desc = (
        "Sélectionnez l'axe X et l'axe Y (sucre vs additifs, énergie vs lipides, sodium vs Nutri-Score). Activez des séries visuelles (produits bio, édulcorants)."
        if is_fr else
        "Choose your X and Y axes (sugars vs additives, calories vs fats, sodium vs Nutri-Score). Enable visual markers for organic products or sweeteners."
    )
    t_step2_f1 = "Nuages de points (Scatter plots)" if is_fr else "2-Axis Scatter plots"
    t_step2_f2 = "Histogrammes de distribution" if is_fr else "Distribution bar charts"
    t_step2_f3 = "Cartes géographiques & exports CSV" if is_fr else "Geospatial maps & CSV exports"

    t_step3_title = "3. Analyser, vérifier et partager" if is_fr else "3. Inspect, Verify & Share"
    t_step3_desc = (
        "Survolez les points pour afficher la fiche produit complète. Repérez les anomalies ou valeurs extrêmes, puis partagez l'URL persistante du graphique !"
        if is_fr else
        "Hover over data points to preview product sheets. Spot nutritional outliers, audit input errors, and share your persistent graph URL with the world."
    )
    t_step3_f1 = "Graphiques dynamiques et interactifs" if is_fr else "Dynamic interactive data points"
    t_step3_f2 = "Détection visuelle des valeurs aberrantes" if is_fr else "Visual outlier identification"
    t_step3_f3 = "URL pérenne pour partage et publications" if is_fr else "Permanent URL for papers & sharing"

    # Spotlight Case Study
    t_spotlight_badge = "Cas d'étude emblématique" if is_fr else "Iconic Case Study"
    t_spotlight_title = "Sucres et additifs dans les boissons sucrées (Opération Sodas)" if is_fr else "Sugars & Additives in Sodas (The Sodas Operation)"
    t_spotlight_desc = (
        "Ce graphique croise la teneur en sucre (axe X) et le nombre d'additifs (axe Y) des sodas collectés par la communauté. "
        "Les points verts mettent en valeur les produits certifiés biologiques, tandis que les marqueurs spécifiques signalent les boissons avec édulcorants intenses."
        if is_fr else
        "This iconic scatter plot correlates sugar content (X axis) with food additives count (Y axis) across sodas collected by the community. "
        "Green dots highlight certified organic sodas, while specific markers identify formulations containing intense artificial sweeteners."
    )
    t_spotlight_btn = "Explorer ce graphique en direct ↗" if is_fr else "Explore this Live Graph ↗"

    # Formats Cards
    t_format1_title = "Nuages de points (Scatter plots)" if is_fr else "2-Axis Scatter Plots"
    t_format1_desc = "Corrélez deux nutriments ou métriques au choix avec infobulles interactives au survol." if is_fr else "Correlate any two nutrients or metrics with interactive hover tooltips."
    t_format2_title = "Cartes des terroirs & origines" if is_fr else "Geospatial & Origins Maps"
    t_format2_desc = "Visualisez les lieux de fabrication et l'origine des ingrédients (AOP, AOC, bio)." if is_fr else "Map manufacturing sites and ingredient provenance (Protected Origins, Fair Trade)."
    t_format3_title = "Listes personnalisées & Exports" if is_fr else "Custom Lists & Data Exports"
    t_format3_desc = "Téléchargez les données filtrées en CSV ou Excel pour vos analyses approfondies (R, Python, LibreOffice)." if is_fr else "Download filtered datasets as CSV or Excel for in-depth data analysis (R, Python, LibreOffice)."

    # Callout
    t_callout_title = "Conseil de validation citoyenne" if is_fr else "Community Data Validation Tip"
    t_callout_desc = (
        "Avant de publier ou citer un graphique dans un article ou une étude, vérifiez les produits situés aux points extrêmes. "
        "Une coquille de saisie est toujours possible : si une valeur nutritionnelle semble démesurée, vérifiez l'emballage original sur Open Food Facts et corrigez-la en un clic !"
        if is_fr else
        "Before publishing or referencing a graph in an article or study, double-check products at extreme outlier points. "
        "Input errors can occur: if a value seems unusually high or low, check the original packaging photo on Open Food Facts and edit it directly!"
    )

    # Showcase Header
    t_showcase_title = "Bibliothèque de Requêtes Utiles & Graphiques Remarquables" if is_fr else "Curated Useful Queries & Community Graphs Showcase"
    t_showcase_sub = (
        "Découvrez les requêtes et visualisations conçues par la communauté Open Food Facts : analyses nutritionnelles, enquêtes citoyennes et requêtes de contribution."
        if is_fr else
        "Explore curated searches and visualizations crafted by the Open Food Facts community: nutritional analyses, civic investigations, and contributor workflows."
    )
    t_search_placeholder = "🔍 Rechercher par mot-clé, aliment, nutriment, auteur (ex: sodas, Tacite, sel, bio...)" if is_fr else "🔍 Search by keyword, food, nutrient, contributor (e.g. sodas, Tacite, salt, bio...)"
    t_label_topics = "Thématiques :" if is_fr else "Topics:"
    t_all_topics = "Toutes les thématiques" if is_fr else "All Topics"
    t_label_type = "Format d'affichage :" if is_fr else "Visualization Type:"
    t_all_types = "Tous les formats" if is_fr else "All Types"
    t_label_geo = "Géographie :" if is_fr else "Geography:"
    t_all_geos = "Toutes zones" if is_fr else "All Geographies"
    t_label_sort = "Trier par :" if is_fr else "Sort by:"
    t_sort_featured = "En vedette & populaires" if is_fr else "Featured & Curated"
    t_sort_title = "Titre (A-Z)" if is_fr else "Title (A-Z)"
    t_sort_topic = "Thématique" if is_fr else "Topic"
    t_results_count = "requêtes affichées" if is_fr else "queries shown"
    t_reset = "Réinitialiser les filtres" if is_fr else "Reset Filters"
    t_no_results = "Aucune requête ne correspond à vos critères." if is_fr else "No curated queries match your selected filters."

    # Contribute section
    t_contrib_title = "💡 Vous avez conçu une requête ou un graphique utile ?" if is_fr else "💡 Created an Insightful Query or Graph?"
    t_contrib_desc = (
        "Ajoutez votre requête à notre bibliothèque ouverte ! Soumettez simplement un fichier YAML dans le répertoire data/queries/ sur GitHub."
        if is_fr else
        "Add your search or chart to this open library! Simply submit a YAML file to the data/queries/ directory on GitHub via Pull Request."
    )
    t_btn_gh_contrib = "🚀 Proposer une requête sur GitHub" if is_fr else "🚀 Propose a Query on GitHub"

    # Build topic pill buttons
    topic_pills_html = [f'<button type="button" class="g3c-pill-btn g3c-topic-pill active" data-topic="all">🌐 {t_all_topics}</button>']
    for t_key, t_info in VALID_TOPICS.items():
        t_label = t_info["fr"] if is_fr else t_info["en"]
        topic_pills_html.append(
            f'<button type="button" class="g3c-pill-btn g3c-topic-pill" data-topic="{t_key}">{t_info["icon"]} {t_label}</button>'
        )

    # Build type options
    type_options_html = [f'<option value="all">{t_all_types}</option>']
    for type_key, type_info in VALID_QUERY_TYPES.items():
        type_label = type_info["fr"] if is_fr else type_info["en"]
        type_options_html.append(f'<option value="{type_key}">{type_info["icon"]} {type_label}</option>')

    # Build geo options
    geo_options_html = [f'<option value="all">{t_all_geos}</option>']
    for geo_key, geo_info in GEO_NAMES.items():
        geo_label = geo_info["fr"] if is_fr else geo_info["en"]
        geo_options_html.append(f'<option value="{geo_key}">{geo_info["flag"]} {geo_label}</option>')

    # Build cards HTML
    cards_html = []
    for q in queries:
        qid = html.escape(q.get("id", ""))
        title = html.escape(q.get("title", ""))
        desc = html.escape(q.get("description", ""))
        author = html.escape(q.get("author", "Open Food Facts Community"))
        topic = q.get("topic", "nutrition")
        q_type = q.get("query_type", "scatter_plot")
        geos = q.get("geographies", ["world"])
        url = html.escape(q.get("url", ""))
        featured = q.get("featured", False)
        tags_combined = q.get("tags_combined", [])
        params = q.get("parameters", {})
        keywords = q.get("keywords", [])

        # Search index string
        search_target = " ".join([
            title, desc, author, topic, q_type,
            " ".join(geos),
            " ".join(tags_combined),
            " ".join(keywords)
        ]).lower()
        search_attr = html.escape(search_target)

        # Type badge
        type_meta = VALID_QUERY_TYPES.get(q_type, {"en": q_type, "fr": q_type, "icon": "📈"})
        type_label = type_meta["fr"] if is_fr else type_meta["en"]
        type_badge_html = f'<span class="g3c-type-badge {q_type}">{type_meta["icon"]} {type_label}</span>'

        # Geo badges
        geo_badges_html = []
        for g in geos:
            g_meta = GEO_NAMES.get(g, {"flag": "📍", "en": g.upper(), "fr": g.upper()})
            geo_badges_html.append(f'<span class="g3c-geo-badge">{g_meta["flag"]} {g.upper()}</span>')
        geo_badges_str = " ".join(geo_badges_html)

        # Chips for combined tags
        chips_html = []
        for tag in tags_combined[:6]:
            tag_escaped = html.escape(str(tag))
            tag_class = "state"
            if tag_escaped.startswith("category:"): tag_class = "category"
            elif tag_escaped.startswith("axis_") or tag_escaped.startswith("nutriment:"): tag_class = "axis"
            elif tag_escaped.startswith("label:") or tag_escaped.startswith("series:"): tag_class = "label"
            elif tag_escaped.startswith("ingredient:"): tag_class = "ingredient"
            chips_html.append(f'<span class="g3c-chip {tag_class}">{tag_escaped}</span>')
        chips_str = "".join(chips_html)

        # Formatted params
        params_str = html.escape(yaml.dump(params, default_flow_style=False, sort_keys=False))

        featured_class = "featured" if featured else ""
        featured_star = '⭐ <span style="font-size:0.75rem;font-weight:600;color:#d97706;">Featured</span>' if featured else ""

        btn_run_text = "Ouvrir la requête" if is_fr else "Open Query"
        btn_copy_title = "Copier le lien" if is_fr else "Copy link"
        params_summary_text = "🔍 Voir les paramètres" if is_fr else "🔍 Inspect parameters"

        card = f"""
        <article class="g3c-query-card {featured_class}"
                 data-id="{qid}"
                 data-title="{title}"
                 data-topic="{topic}"
                 data-type="{q_type}"
                 data-geos="{','.join(geos)}"
                 data-search="{search_attr}">
          <div class="g3c-card-header">
            <div class="g3c-card-tags-top">
              {type_badge_html}
              {geo_badges_str}
            </div>
            {f'<div class="g3c-featured-star">{featured_star}</div>' if featured else ''}
          </div>
          <h3 class="g3c-card-title">{title}</h3>
          <p class="g3c-card-desc">{desc}</p>
          <div class="g3c-author-line">👤 {author}</div>
          <div class="g3c-chips-wrap">{chips_str}</div>
          <div class="g3c-card-footer">
            <a href="{url}" target="_blank" rel="noopener noreferrer" class="g3c-run-btn">
              {btn_run_text} ↗
            </a>
            <button type="button" class="g3c-copy-btn" data-url="{url}" title="{btn_copy_title}">
              📋
            </button>
          </div>
          <details class="g3c-params-details">
            <summary>{params_summary_text}</summary>
            <pre class="g3c-params-pre">{params_str}</pre>
          </details>
        </article>
        """
        cards_html.append(card)

    cards_str = "\n".join(cards_html)
    pills_str = "\n".join(topic_pills_html)
    types_str = "\n".join(type_options_html)
    geos_str = "\n".join(geo_options_html)

    css_block = generate_css()
    js_block = generate_js(lang)

    html_page = f"""
{css_block}

<div class="g3c-container">

  <!-- Hero Section -->
  <header class="g3c-hero">
    <div class="g3c-badge">📊 {t_hero_badge}</div>
    <h1 class="g3c-hero-title">{t_page_title}</h1>
    <p class="g3c-hero-subtitle">{t_hero_subtitle}</p>
    
    <div class="g3c-quote-card">
      &ldquo;{t_hero_quote}&rdquo;
    </div>

    <div class="g3c-hero-actions">
      <a href="https://world.openfoodfacts.org/cgi/search.pl?graph=1" class="g3c-btn g3c-btn-primary">
        {t_btn_search}
      </a>
      <a href="#g3c-showcase" class="g3c-btn g3c-btn-secondary">
        {t_btn_showcase}
      </a>
      <a href="https://world.openfoodfacts.org/cgi/search.pl" class="g3c-btn g3c-btn-secondary" title="{t_btn_skip}">
        {t_btn_skip} ➔
      </a>
    </div>
  </header>

  <!-- 3-Click Visual Workflow Guide -->
  <section class="g3c-workflow" id="g3c-workflow">
    <div class="g3c-section-header">
      <h2 class="g3c-section-title">{t_workflow_title}</h2>
      <p class="g3c-section-subtitle">{t_workflow_sub}</p>
    </div>

    <div class="g3c-steps-grid">
      <!-- Step 1 -->
      <div class="g3c-step-card">
        <div class="g3c-step-number">1</div>
        <div class="g3c-step-icon">🎯</div>
        <h3 class="g3c-step-title">{t_step1_title}</h3>
        <p class="g3c-step-desc">{t_step1_desc}</p>
        <ul class="g3c-step-features">
          <li>✔ {t_step1_f1}</li>
          <li>✔ {t_step1_f2}</li>
          <li>✔ {t_step1_f3}</li>
        </ul>
      </div>

      <!-- Step 2 -->
      <div class="g3c-step-card">
        <div class="g3c-step-number">2</div>
        <div class="g3c-step-icon">📐</div>
        <h3 class="g3c-step-title">{t_step2_title}</h3>
        <p class="g3c-step-desc">{t_step2_desc}</p>
        <ul class="g3c-step-features">
          <li>✔ {t_step2_f1}</li>
          <li>✔ {t_step2_f2}</li>
          <li>✔ {t_step2_f3}</li>
        </ul>
      </div>

      <!-- Step 3 -->
      <div class="g3c-step-card">
        <div class="g3c-step-number">3</div>
        <div class="g3c-step-icon">🚀</div>
        <h3 class="g3c-step-title">{t_step3_title}</h3>
        <p class="g3c-step-desc">{t_step3_desc}</p>
        <ul class="g3c-step-features">
          <li>✔ {t_step3_f1}</li>
          <li>✔ {t_step3_f2}</li>
          <li>✔ {t_step3_f3}</li>
        </ul>
      </div>
    </div>

    <!-- Spotlight Example Card -->
    <div class="g3c-spotlight-card">
      <div class="g3c-spotlight-grid">
        <a href="https://world.openfoodfacts.org/cgi/search.pl?action=process&amp;tagtype_0=categories&amp;tag_contains_0=contains&amp;tag_0=sodas&amp;sort_by=product_name&amp;page_size=20&amp;axis_x=sugars&amp;axis_y=additives_n&amp;graph_title=Sugars%20and%20additives%20in%20sodas&amp;series_organic=on&amp;series_fairtrade=on&amp;series_with_sweeteners=on&amp;generate_graph_scatter_plot=1" target="_blank" rel="noopener noreferrer">
          <img src="https://fr.blog.openfoodfacts.org/images/sucres_et_additifs_dans_les_sodas.png" alt="Sugars and additives in sodas scatter plot" class="g3c-spotlight-img" loading="lazy">
        </a>
        <div class="g3c-spotlight-content">
          <span class="g3c-badge">💡 {t_spotlight_badge}</span>
          <h3>{t_spotlight_title}</h3>
          <p>{t_spotlight_desc}</p>
          <a href="https://world.openfoodfacts.org/cgi/search.pl?action=process&amp;tagtype_0=categories&amp;tag_contains_0=contains&amp;tag_0=sodas&amp;sort_by=product_name&amp;page_size=20&amp;axis_x=sugars&amp;axis_y=additives_n&amp;graph_title=Sugars%20and%20additives%20in%20sodas&amp;series_organic=on&amp;series_fairtrade=on&amp;series_with_sweeteners=on&amp;generate_graph_scatter_plot=1" target="_blank" rel="noopener noreferrer" class="g3c-btn g3c-btn-primary">
            {t_spotlight_btn}
          </a>
        </div>
      </div>
    </div>

    <!-- Available Visualization Formats Grid -->
    <div class="g3c-formats-grid">
      <div class="g3c-format-card">
        <h4>📈 {t_format1_title}</h4>
        <p>{t_format1_desc}</p>
      </div>
      <div class="g3c-format-card">
        <h4>🗺️ {t_format2_title}</h4>
        <p>{t_format2_desc}</p>
      </div>
      <div class="g3c-format-card">
        <h4>📥 {t_format3_title}</h4>
        <p>{t_format3_desc}</p>
      </div>
    </div>

    <!-- Outlier Validation Callout -->
    <div class="g3c-callout">
      <div class="g3c-callout-icon">💡</div>
      <div class="g3c-callout-body">
        <h4>{t_callout_title}</h4>
        <p>{t_callout_desc}</p>
      </div>
    </div>
  </section>

  <!-- Interactive Useful Queries Showcase -->
  <section class="g3c-showcase-section" id="g3c-showcase">
    <div class="g3c-section-header">
      <h2 class="g3c-section-title">{t_showcase_title}</h2>
      <p class="g3c-section-subtitle">{t_showcase_sub}</p>
    </div>

    <!-- Filter & Search Controls -->
    <div class="g3c-controls-wrap">
      <!-- Search Input -->
      <div class="g3c-search-bar">
        <span class="g3c-search-icon">🔍</span>
        <input type="text" id="g3c-search" class="g3c-search-input" placeholder="{t_search_placeholder}" aria-label="Search curated queries">
      </div>

      <!-- Topic Pills -->
      <div class="g3c-filter-group">
        <span class="g3c-filter-label">{t_label_topics}</span>
        <div class="g3c-pills-row">
          {pills_str}
        </div>
      </div>

      <!-- Secondary Filters & Sort -->
      <div class="g3c-secondary-filters">
        <div class="g3c-select-wrap">
          <div>
            <label class="g3c-filter-label" for="g3c-type-select">{t_label_type}</label>
            <select id="g3c-type-select" class="g3c-select">
              {types_str}
            </select>
          </div>

          <div>
            <label class="g3c-filter-label" for="g3c-geo-select">{t_label_geo}</label>
            <select id="g3c-geo-select" class="g3c-select">
              {geos_str}
            </select>
          </div>

          <div>
            <label class="g3c-filter-label" for="g3c-sort-select">{t_label_sort}</label>
            <select id="g3c-sort-select" class="g3c-select">
              <option value="featured">{t_sort_featured}</option>
              <option value="title">{t_sort_title}</option>
              <option value="topic">{t_sort_topic}</option>
            </select>
          </div>
        </div>

        <div class="g3c-stats-and-reset">
          <span class="g3c-count-badge" id="g3c-count">{len(queries)}</span> {t_results_count}
          <button type="button" class="g3c-reset-btn" id="g3c-reset">{t_reset}</button>
        </div>
      </div>
    </div>

    <!-- Cards Grid -->
    <div class="g3c-cards-grid" id="g3c-cards-grid">
      {cards_str}

      <div class="g3c-no-results" id="g3c-no-results" style="display:none;">
        <div class="g3c-no-results-icon">🔎</div>
        <p>{t_no_results}</p>
      </div>
    </div>

    <!-- Contribute Callout -->
    <div class="g3c-contribute-box">
      <h3 class="g3c-contribute-title">{t_contrib_title}</h3>
      <p class="g3c-contribute-desc">{t_contrib_desc}</p>
      <a href="https://github.com/openfoodfacts/openfoodfacts-web/tree/main/data/queries" target="_blank" rel="noopener noreferrer" class="g3c-btn g3c-btn-primary">
        {t_btn_gh_contrib} ↗
      </a>
    </div>
  </section>

  <!-- Toast Notification element -->
  <div class="g3c-toast" id="g3c-toast"></div>

</div>

{js_block}
"""
    return html_page

def compile_queries(check_only=False, verbose=True):
    if verbose:
        print(f"Loading and validating queries from {QUERIES_DIR}...")

    items, errors, warnings = load_queries(QUERIES_DIR, validate=True)

    if warnings and verbose:
        for w in warnings[:10]:
            print(f"  [WARN] {w}")
        if len(warnings) > 10:
            print(f"  ... and {len(warnings) - 10} more warnings.")

    if errors:
        print(f"\n❌ Found {len(errors)} validation error(s) in query YAMLs:")
        for e in errors:
            print(f"  - {e}")
        return False

    if verbose:
        featured_count = sum(1 for q in items if q.get("featured"))
        topics_count = len(set(q.get("topic") for q in items))
        print(f"✅ Validated {len(items)} curated queries (Featured: {featured_count}, Topics: {topics_count})")

    if check_only:
        return True

    # 1. Compile structured queries dataset into data/queries.json
    dataset = {
        "count": len(items),
        "topics": list(VALID_TOPICS.keys()),
        "query_types": list(VALID_QUERY_TYPES.keys()),
        "geographies": list(GEO_NAMES.keys()),
        "queries": items
    }

    with open(COMPILED_JSON, "w", encoding="utf-8") as f:
        json.dump(dataset, f, ensure_ascii=False, indent=2)
    if verbose:
        print(f"Wrote compiled {COMPILED_JSON} ({len(items)} items)")

    # 2. Generate English modernized graphs-in-3-clicks.html
    en_html_path = os.path.join(REPO_ROOT, "lang", "en", "texts", "graphs-in-3-clicks.html")
    en_content = generate_page_html(items, lang="en")
    try:
        with open(en_html_path, "w", encoding="utf-8") as f:
            f.write(en_content)
        if verbose:
            print(f"Generated {en_html_path}")
    except PermissionError:
        fallback_path = os.path.join(DATA_DIR, "graphs-in-3-clicks.en.html")
        with open(fallback_path, "w", encoding="utf-8") as f:
            f.write(en_content)
        if verbose:
            print(f"Generated fallback {fallback_path} (sandbox prevented write to {en_html_path})")

    # 3. Generate French modernized graphs-in-3-clicks.html
    fr_html_path = os.path.join(REPO_ROOT, "lang", "fr", "texts", "graphs-in-3-clicks.html")
    fr_content = generate_page_html(items, lang="fr")
    try:
        with open(fr_html_path, "w", encoding="utf-8") as f:
            f.write(fr_content)
        if verbose:
            print(f"Generated {fr_html_path}")
    except PermissionError:
        fallback_path = os.path.join(DATA_DIR, "graphs-in-3-clicks.fr.html")
        with open(fallback_path, "w", encoding="utf-8") as f:
            f.write(fr_content)
        if verbose:
            print(f"Generated fallback {fallback_path} (sandbox prevented write to {fr_html_path})")

    return True

def main():
    check_only = "--check" in sys.argv
    success = compile_queries(check_only=check_only, verbose=True)
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
