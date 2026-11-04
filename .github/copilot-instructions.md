# GitHub Copilot Instructions for `openfoodfacts-web`

Welcome to `openfoodfacts-web`. This repository houses the static content, multilingual page fragments, knowledge panels, and curated datasets that power the public-facing pages of the [Open Food Facts](https://world.openfoodfacts.org) platform (in conjunction with the backend server `openfoodfacts-server` / `product-opener`).

---

## Repository Architecture & Directory Roles

- **`data/`**: Curated YAML source files for ecosystem datasets:
  - `data/reuses/`: Open data reuses and third-party applications.
  - `data/press-review/`: Press articles, media appearances, podcasts, and scientific studies.
  - `data/faq/`: Categorized Markdown FAQs organized by language (`en`, `fr`, `es`, `de`, `it`).
  - `data/queries/`: Curated search queries for exploring food data.
  - `data/scan_parties/`: Community scan events and hackathons.
  - `data/missions/`: Historical campaign and mission data (Opération Sodas, yogurt, shampoo).
- **`lang/`**: Multilingual static page fragments and translations:
  - `lang/en/texts/`: **Canonical English source** for static content pages (e.g. `data.html`, `discover.html`, `contribute.html`).
  - `lang/<locale>/texts/`: Localized versions synced via Crowdin.
- **`html/`**: Static assets committed to the repository:
  - `html/images/texts/`: Local image assets referenced by static text pages.
- **`knowledge_panels/`**: Taxonomy-linked knowledge card definitions (additives, ingredients, nutrients, categories, labels).
- **`scripts/`**: Python 3 orchestrators, compilers, validators, and unit tests:
  - `scripts/compile.py`: Master compilation and validation pipeline for all datasets.
- **Root `.html` files**: Standalone HTML5 pages designed for direct previewing (e.g. `scores-and-methodologies.html`, `impact.html`, `operation-sodas.html`, `whats-in-my-yogurt.html`, `whats-in-my-shampoo.html`, `scan-parties.html`).

---

## Core Rules & Constraints

### 1. No External Hotlinking
- **Never** hotlink images, stylesheets, or JavaScript from external third-party websites (unless pointing to the official CDN `https://static.openfoodfacts.org`).
- Place local images under `html/images/texts/` or the appropriate subfolder and commit them to the repository.

### 2. Protect Brand Names & Protected Terms (The "No-Translate" List)
Never translate or alter these registered brand names and scoring systems in any language:
- **Open Food Facts** (never "Abierto hechos de comida", "Faches de l'alimentacion dobèrta", etc.)
- **Open Beauty Facts**
- **Open Pet Food Facts**
- **Open Prices**
- **Nutri-Score**
- **Eco-Score**
- **Green-Score**
- **NOVA** (when referring to the NOVA food processing classification system)

### 3. HTML Fragments vs. Standalone Pages
- Files in `lang/<lang>/texts/*.html` are **HTML fragments**, not standalone pages. They are embedded inside the `product-opener` page shell.
  - **Do NOT** add `<!DOCTYPE html>`, `<html>`, `<head>`, or `<body>` tags to files in `lang/<lang>/texts/`.
  - Use semantic tags (`<h1>`, `<section>`, `<p>`, `<ul>`, `<table>`).
- Only root `.html` files (e.g., `operation-sodas.html`) are standalone HTML documents.

### 4. Template Includes Syntax
- The Perl-based `product-opener` server uses `[[texts/path/to/include.html]]` syntax to embed shared components.
- Preserve existing `[[...]]` includes and do not alter their bracket syntax or paths.

### 5. Translation Syntax & Placeholders
- Keep placeholders (`%s`, `%d`, `{count}`, `%(name)s`, `<br>`) identical to the source string.
- Respect regional typography (e.g., French non-breaking spaces before `:` `;` `?` `!`).

---

## Validation, Testing & Build Commands

When making changes, run the following commands to validate your work before submitting:

### 1. Master Compilation & Schema Validation
Always validate dataset YAML files:
```bash
# Dry-run validation only (fast CI check):
python3 scripts/compile.py --check

# Compile datasets to JSON and generate HTML pages:
python3 scripts/compile.py
```

### 2. Targeted Dataset Compilers
```bash
python3 scripts/compile_reuses.py --check
python3 scripts/compile_press_review.py --check
python3 scripts/compile_faq.py --check
python3 scripts/compile_queries.py --check
python3 scripts/compile_scan_parties.py --check
python3 scripts/compile_campaign_pages.py
```

### 3. Unit Tests
Run unit tests for modified components:
```bash
PYTHONPATH=scripts python3 scripts/test_translation_qa.py
PYTHONPATH=scripts python3 scripts/test_add_reuse.py
PYTHONPATH=scripts python3 scripts/test_add_press_review.py
PYTHONPATH=scripts python3 scripts/test_add_query.py
PYTHONPATH=scripts python3 scripts/test_add_scan_party.py
PYTHONPATH=scripts python3 scripts/test_add_scientific_publication.py
```

### 4. Local Preview
To preview pages locally in your browser:
```bash
python3 -m http.server 8000
```
Then visit `http://localhost:8000/<page>.html`.

---

## Commit & Pull Request Conventions

- **Semantic Commits:** Use Conventional Commits format:
  - `feat: <description>` for new pages or features
  - `fix: <description>` for bug fixes or corrections
  - `docs: <description>` for documentation changes
  - `chore: <description>` for maintenance or dependency updates
- **Pull Request Acceptance:**
  - `python3 scripts/compile.py --check` must pass without schema errors.
  - No hotlinked external assets.
  - Reference relevant issue in PR description (e.g., `Closes #<issue_number>`).
