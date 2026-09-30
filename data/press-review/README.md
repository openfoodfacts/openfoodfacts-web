# Open Food Facts Press Review System

The Open Food Facts Press Review documents and showcases media mentions, investigative television reports, radio broadcasts, podcasts, scientific studies, and press articles covering Open Food Facts worldwide since 2012.

---

## 🏗️ Architecture & Directory Structure

```
openfoodfacts-web/
├── data/
│   ├── press-review/               # Individual press mentions (*.yaml)
│   │   ├── 2025-08-08-france-inter-les-super-pouvoirs-de-lassiette.yaml
│   │   └── ...
│   ├── press-review-merged.json    # Compiled unified JSON dataset (stripped of internal notes)
│   └── press-review.csv            # Legacy tabular export
├── lang/
│   ├── fr/texts/revue-de-presse-fr.html   # Compiled French Press Review interface
│   ├── en/texts/press-review.html         # Compiled English Press Review interface
│   └── */texts/presskit*.html             # Country-specific press kits and hub
├── scripts/
│   ├── compile_press_review.py     # Schema validation and HTML/JSON compiler
│   ├── add_press_review.py         # Helper to parse issues & add press mentions
│   ├── clean_and_enrich_press_review.py # Quality checks, topics, and enrichment
│   ├── generate_press_review.py    # Generates interactive press review HTML
│   ├── generate_country_presskits.py # Generates localized country press kits
│   └── generate_press_hub.py       # Generates the press hub
└── .github/
    ├── ISSUE_TEMPLATE/
    │   ├── new-press-review.yml    # GitHub Issue Form template
    │   └── new-press-review.md     # GitHub Markdown template fallback
    ├── PULL_REQUEST_TEMPLATE/
    │   └── press-review.md         # Press Review PR checklist template
    └── workflows/
        ├── press-review-issue-to-pr.yml # Automated Issue -> PR workflow
        └── press-review-ci.yml          # CI validation workflow
```

---

## 📰 Proposing a Press Mention via GitHub Issues

Anyone can propose new media coverage via GitHub Issues:

1. Click **"New Issue"** and select **"📰 Suggest a new Press Mention"** (or use the direct URL:  
   `https://github.com/openfoodfacts/openfoodfacts-web/issues/new?template=new-press-review.yml`).
2. Fill out the form:
   - **Article / Segment Title**: Headline or broadcast title.
   - **Media Source**: Newspaper, channel, station, or website (e.g. *Le Monde*, *France Inter*, *The Guardian*).
   - **Publication Date**: `YYYY-MM-DD` format.
   - **URL / Web Link**: Direct link to the piece.
   - **Media Type**: `article`, `podcast`, `video`, or `study`.
   - **Media Scope**: `national`, `regional`, `specialized`, `culinary_blog`, or `report`.
   - **Language & Country**: Primary language (`fr`, `en`, etc.) and country code (`fra`, `deu`, `esp`, `eu`, etc.).
   - **Topics Covered**: Nutri-Score, NOVA, UPF, Green-Score, Open Data, Data Journalism, etc.
   - **Verbatim / Key Quote**: Excerpt where Open Food Facts is highlighted.
   - **Editorial Note**: Optional internal note for maintainers (not published publicly).
3. Once submitted with the `press-review` label, GitHub Actions automatically:
   - Runs `scripts/add_press_review.py --from-env --compile --json`.
   - Normalizes fields, extracts the domain, removes abbreviations (replaces `OFF` with `Open Food Facts`).
   - Generates the standardized YAML file under `data/press-review/<id>.yaml`.
   - Validates schema against `scripts/compile_press_review.py`.
   - Opens a **Pull Request** for team review and comments back on the issue!

---

## ✍️ Submitting a Pull Request directly

Contributors and maintainers can also add entries locally:

### Using the Helper Script (`scripts/add_press_review.py`)

```bash
# Add an entry via CLI flags:
python3 scripts/add_press_review.py \
    --title "How Open Food Facts Empowers Consumers" \
    --source "The Guardian" \
    --date "2026-09-30" \
    --link "https://www.theguardian.com/food/2026/sep/30/open-food-facts" \
    --type article \
    --media-scope national \
    --lang en \
    --country gbr \
    --topics nutriscore open-data \
    --compile

# Test validation without saving (dry-run):
python3 scripts/add_press_review.py --dry-run --json ...
```

### Manual YAML Entry

Create a file named `data/press-review/<YYYY-MM-DD>-<source-slug>-<title-slug>.yaml`:

```yaml
id: 2026-09-30-the-guardian-how-open-food-facts-empowers-con
date: '2026-09-30'
source: The Guardian
title: How Open Food Facts Empowers Consumers
link: https://www.theguardian.com/food/2026/sep/30/open-food-facts
domain: theguardian.com
type: article
media_scope: national
raw_type: Article
lang: en
country: gbr
author: Jane Doe
topic: ''
topics:
  - nutriscore
  - open-data
verbatim: "Open Food Facts has become the go-to independent database for consumers."
editorial_note: "Featured on the front page of the food section."
dead_link: false
selected: false
origin: github-issue
```

---

## 🔍 Validation & Compilation

Run schema checks across all press review YAML files:
```bash
python3 scripts/compile_press_review.py --check
```

Recompile `data/press-review-merged.json` and generate updated HTML views:
```bash
python3 scripts/compile_press_review.py
```

---

## 📋 Schema Rules & Conventions

- **ID & Filename**: The `id` must strictly match the filename stem (without `.yaml`).
- **Date**: Must strictly follow `YYYY-MM-DD`.
- **Media Type**: Must be one of `article`, `podcast`, `video`, `study`.
- **Media Scope**: Must be one of `national`, `regional`, `specialized`, `culinary_blog`, `report`.
- **No 'OFF' Acronym**: In public fields (`title`, `source`, `verbatim`, `topic`), always spell out `Open Food Facts`.
- **Editorial Notes**: Any internal observations, paywall notes, or private maintainer comments must be kept in `editorial_note` (which is excluded from compiled public output).
