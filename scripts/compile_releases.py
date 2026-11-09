#!/usr/bin/env python3
"""
Compilation and validation system for Open Food Facts Releases & Features.

Reads:
- data/releases.json (automated feed across all repositories)
- data/release_highlights.yaml (manual curated game-changing milestones)

Validates schemas, compiles localized static HTML fragments:
- lang/en/texts/releases.html
- lang/fr/texts/releases.html
And generates the standalone root page:
- releases.html

Usage:
    python3 scripts/compile_releases.py           # Compile JSON and HTML pages
    python3 scripts/compile_releases.py --check   # Validation only (CI friendly)
"""

import argparse
import datetime
import html
import json
import os
import re
import sys

# Ensure scripts directory and vendor are in path
SCRIPTS_DIR = os.path.dirname(os.path.abspath(__file__))
if SCRIPTS_DIR not in sys.path:
    sys.path.insert(0, SCRIPTS_DIR)

from i18n_utils import ensure_vendor_path, get_localized_field, SUPPORTED_LANGUAGES
ensure_vendor_path()

import yaml

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
DATA_DIR = os.path.join(REPO_ROOT, "data")
RELEASES_JSON = os.path.join(DATA_DIR, "releases.json")
HIGHLIGHTS_YAML = os.path.join(DATA_DIR, "release_highlights.yaml")

VALID_CATEGORIES = {
    "Core", "Mobile", "Prices", "AI & Robotoff", "Taxonomy",
    "SDKs", "JavaScript", "Misc", "Data Quality", "Folksonomy", "Folksonomy Engine"
}

CATEGORY_COLORS = {
    "Core": {"bg": "#eff6ff", "text": "#1d4ed8", "border": "#bfdbfe"},
    "Mobile": {"bg": "#ecfdf5", "text": "#047857", "border": "#a7f3d0"},
    "Prices": {"bg": "#fff7ed", "text": "#c2410c", "border": "#fed7aa"},
    "AI & Robotoff": {"bg": "#f5f3ff", "text": "#6d28d9", "border": "#ddd6fe"},
    "Taxonomy": {"bg": "#fefce8", "text": "#a16207", "border": "#fef08a"},
    "SDKs": {"bg": "#f0fdfa", "text": "#0f766e", "border": "#99f6e4"},
    "JavaScript": {"bg": "#fdf4ff", "text": "#a21caf", "border": "#f5d0fe"},
    "Data Quality": {"bg": "#fff1f2", "text": "#be123c", "border": "#fecdd3"},
    "Folksonomy": {"bg": "#f8fafc", "text": "#334155", "border": "#cbd5e1"},
    "Misc": {"bg": "#f8fafc", "text": "#475569", "border": "#e2e8f0"}
}

def load_data(validate=True):
    errors = []
    warnings = []

    # 1. Load releases.json
    if not os.path.exists(RELEASES_JSON):
        raise FileNotFoundError(f"Missing {RELEASES_JSON}. Run scripts/fetch_releases.py first.")

    with open(RELEASES_JSON, "r", encoding="utf-8") as f:
        releases = json.load(f)

    if not isinstance(releases, list):
        errors.append("releases.json: Expected root element to be a list.")
        releases = []

    for i, r in enumerate(releases):
        if not r.get("tag"):
            errors.append(f"releases.json [{i}]: Missing required field 'tag'")
        if not r.get("repo"):
            errors.append(f"releases.json [{i}]: Missing required field 'repo'")
        if not r.get("published_at"):
            warnings.append(f"releases.json [{i}]: Missing 'published_at' date")

    # 2. Load release_highlights.yaml
    if not os.path.exists(HIGHLIGHTS_YAML):
        raise FileNotFoundError(f"Missing {HIGHLIGHTS_YAML}.")

    with open(HIGHLIGHTS_YAML, "r", encoding="utf-8") as f:
        highlights_data = yaml.safe_load(f)

    highlights = highlights_data.get("highlights", []) if isinstance(highlights_data, dict) else []
    for h in highlights:
        if not h.get("id"):
            errors.append(f"{HIGHLIGHTS_YAML}: Highlight missing 'id'")
        if not h.get("title"):
            errors.append(f"{HIGHLIGHTS_YAML}: Highlight '{h.get('id')}' missing 'title'")
        if not h.get("summary"):
            errors.append(f"{HIGHLIGHTS_YAML}: Highlight '{h.get('id')}' missing 'summary'")
        if not h.get("date"):
            errors.append(f"{HIGHLIGHTS_YAML}: Highlight '{h.get('id')}' missing 'date'")

    return releases, highlights, errors, warnings

def build_releases_html(releases, highlights, lang="en"):
    """
    Generate clean, accessible, modern HTML fragment matching Open Food Facts design system
    and inspired by aukilo.com/fr/news timeline.
    """
    is_fr = lang == "fr"

    # I18n UI strings
    ui = {
        "badge": "Releases & Innovations" if not is_fr else "Versions & Innovations",
        "title": "Open Food Facts Ecosystem Releases & Features",
        "title_fr": "Versions & Nouvelles Fonctionnalités d'Open Food Facts",
        "subtitle": (
            "Automatic live pulse of releases across Open Food Facts core server, mobile app, Open Prices, "
            "AI engines, and developer SDKs, along with the game-changing breakthroughs of the rolling year."
            if not is_fr else
            "Le pouls en direct des versions du serveur, de l'application mobile, d'Open Prices, "
            "des moteurs d'IA et des SDK, ainsi que les avancées majeures de l'année écoulée."
        ),
        "tab_highlights": "🌟 Game-Changing Milestones (Last Rolling Year)" if not is_fr else "🌟 Avancées Majeures (Année Écoulée)",
        "tab_timeline": "🕒 Full Release Timeline" if not is_fr else "🕒 Fil Chronologique des Versions",
        "search_placeholder": "Search by repository, version, feature or keyword..." if not is_fr else "Rechercher par dépôt, version, mot-clé...",
        "all_categories": "All Categories" if not is_fr else "Toutes catégories",
        "all_repos": "All Repositories" if not is_fr else "Tous dépôts",
        "time_filter_rolling": "Rolling Year (2025–2026)" if not is_fr else "Année écoulée (2025–2026)",
        "time_filter_all": "All Time" if not is_fr else "Tout l'historique",
        "stat_releases": "Releases Tracked" if not is_fr else "Versions répertoriées",
        "stat_rolling": "In Rolling Year" if not is_fr else "Dans l'année écoulée",
        "stat_repos": "Active Repositories" if not is_fr else "Dépôts actifs",
        "stat_pillars": "Strategic Milestones" if not is_fr else "Avancées stratégiques",
        "view_details": "Read release details" if not is_fr else "Lire les détails de cette version",
        "open_release": "Open on GitHub" if not is_fr else "Voir sur GitHub",
        "key_impact": "Key Impact" if not is_fr else "Impact Majeur",
        "key_highlights": "Highlights" if not is_fr else "Points Clés",
        "impact_badge": "Game-Changing" if not is_fr else "Révolutionnaire",
        "empty_message": "No releases match the selected filters." if not is_fr else "Aucune version ne correspond aux filtres sélectionnés.",
        "clear_filters": "Reset filters" if not is_fr else "Réinitialiser les filtres",
        "wiki_source": "Data synced automatically from" if not is_fr else "Données synchronisées automatiquement depuis",
    }

    page_title = ui["title_fr"] if is_fr else ui["title"]
    subtitle = ui["subtitle"]

    # Compute statistics
    total_releases = len(releases)
    rolling_releases = [r for r in releases if r.get("published_at", "") >= "2025-11-01"]
    active_repos = sorted(list(set(r.get("repo", "") for r in releases if r.get("repo"))))
    categories = sorted(list(set(r.get("category", "Core") for r in releases if r.get("category"))))

    # Build Highlights HTML (Manual View)
    highlights_cards = []
    for h in highlights:
        h_title = get_localized_field(h, "title", lang=lang)
        h_summary = get_localized_field(h, "summary", lang=lang)
        badge = h.get("badge_fr" if is_fr else "badge") or h.get("category", "").title()
        date_str = h.get("date", "")
        repos_pills = "".join(f'<span class="off-hl-repo-pill">{r.split("/")[1]}</span>' for r in h.get("repos", []))
        
        # Highlights list
        hl_items = []
        for item in h.get("highlights", []):
            text = item.get(lang) or item.get("en") or str(item)
            hl_items.append(f'<li>{html.escape(text)}</li>')
        hl_html = f'<ul class="off-hl-list">{"".join(hl_items)}</ul>' if hl_items else ""

        # Links
        link_items = []
        for l in h.get("links", []):
            l_title = l.get("title", "Reference")
            l_url = l.get("url", "#")
            link_items.append(
                f'<a href="{html.escape(l_url)}" class="off-hl-link" target="_blank" rel="noopener">'
                f'{html.escape(l_title)} ↗</a>'
            )
        links_html = f'<div class="off-hl-links">{"".join(link_items)}</div>' if link_items else ""

        highlights_cards.append(f"""
        <article class="off-hl-card" data-category="{html.escape(h.get('category', 'core'))}">
          <div class="off-hl-header">
            <div class="off-hl-badges">
              <span class="off-badge-pill off-badge-impact">{ui["impact_badge"]}</span>
              <span class="off-badge-pill off-badge-cat">{html.escape(badge)}</span>
              <time class="off-hl-date">{html.escape(date_str)}</time>
            </div>
            <div class="off-hl-repos">{repos_pills}</div>
          </div>
          <h3 class="off-hl-title">{html.escape(h_title)}</h3>
          <p class="off-hl-summary">{html.escape(h_summary)}</p>
          <div class="off-hl-body">
            <h4 class="off-hl-subheading">{ui["key_highlights"]}</h4>
            {hl_html}
          </div>
          {links_html}
        </article>
        """)

    highlights_section = f"""
    <div id="view-highlights" class="off-view-section active">
      <div class="off-hl-banner">
        <div class="off-hl-banner-icon">💡</div>
        <div class="off-hl-banner-text">
          <strong>{"Curated Editorial Overview" if not is_fr else "Synthèse Éditoriale"}</strong>:
          {"Detailed analysis of the most profound, game-changing shifts across Open Food Facts over the rolling year (November 2025 – November 2026), from automated environmental lifecycle scoring with Ecobalyse to privacy-first receipt anonymization, the launch of OpenFoodFacts Explorer, and multi-language SDK upgrades." if not is_fr else "Analyse détaillée des avancées les plus déterminantes de l'écosystème Open Food Facts sur l'année écoulée (novembre 2025 – novembre 2026) : calcul automatisé de l'empreinte écologique avec Ecobalyse, anonymisation des tickets de caisse, avènement d'OpenFoodFacts Explorer et modernisation des SDK."}
        </div>
      </div>
      <div class="off-highlights-grid">
        {"".join(highlights_cards)}
      </div>
    </div>
    """

    # Build Timeline HTML (Automated Feed)
    timeline_items = []
    for r in releases:
        tag = r.get("tag", "")
        repo = r.get("repo", "")
        repo_name = r.get("repo_name", repo.split("/")[1] if "/" in repo else repo)
        cat = r.get("category", "Core")
        pub = r.get("published_at", "")
        date_str = r.get("date_fr" if is_fr else "date_en") or pub[:10]
        html_url = r.get("html_url", "#")
        title = r.get("title") or tag
        summary = r.get("summary") or ""
        body_html = r.get("body_html") or ""
        is_rolling = pub >= "2025-11-01"

        cat_style = CATEGORY_COLORS.get(cat, CATEGORY_COLORS["Core"])
        cat_badge_style = f"background: {cat_style['bg']}; color: {cat_style['text']}; border: 1px solid {cat_style['border']};"

        # Content for collapsible details
        details_block = ""
        if body_html and len(body_html.strip()) > 30:
            details_block = f"""
            <details class="off-rel-details">
              <summary class="off-rel-summary-toggle">
                <span class="off-more-btn">{ui["view_details"]}</span>
              </summary>
              <div class="off-rel-prose">
                {body_html}
              </div>
            </details>
            """

        timeline_items.append(f"""
        <div class="off-rel-item" data-repo="{html.escape(repo)}" data-cat="{html.escape(cat)}" data-date="{html.escape(pub[:10])}" data-rolling="{str(is_rolling).lower()}">
          <span class="off-timeline-dot" aria-hidden="true"></span>
          <div class="off-rel-card">
            <div class="off-rel-meta">
              <span class="off-rel-tag">{html.escape(tag)}</span>
              <span class="off-rel-cat-badge" style="{cat_badge_style}">{html.escape(cat)}</span>
              <span class="off-rel-repo">{html.escape(repo_name)}</span>
              <time class="off-rel-date" datetime="{html.escape(pub)}">{html.escape(date_str)}</time>
            </div>
            <h3 class="off-rel-title">
              <a href="{html.escape(html_url)}" target="_blank" rel="noopener">{html.escape(title)}</a>
            </h3>
            {f'<p class="off-rel-summary">{html.escape(summary)}</p>' if summary else ''}
            {details_block}
            <div class="off-rel-actions">
              <a href="{html.escape(html_url)}" class="off-rel-btn" target="_blank" rel="noopener">
                {ui["open_release"]} ↗
              </a>
            </div>
          </div>
        </div>
        """)

    timeline_section = f"""
    <div id="view-timeline" class="off-view-section">
      <!-- Interactive Filter Controls -->
      <div class="off-filter-toolbar">
        <div class="off-search-wrap">
          <span class="off-search-icon">🔍</span>
          <input type="search" id="off-search-input" class="off-search-input" placeholder="{ui['search_placeholder']}" aria-label="Search releases">
        </div>
        
        <div class="off-filter-group">
          <select id="off-filter-cat" class="off-filter-select" aria-label="Filter by category">
            <option value="all">{ui["all_categories"]}</option>
            {''.join(f'<option value="{html.escape(c)}">{html.escape(c)}</option>' for c in categories)}
          </select>

          <select id="off-filter-repo" class="off-filter-select" aria-label="Filter by repository">
            <option value="all">{ui["all_repos"]}</option>
            {''.join(f'<option value="{html.escape(rp)}">{html.escape(rp)}</option>' for rp in active_repos)}
          </select>

          <select id="off-filter-time" class="off-filter-select" aria-label="Filter by time range">
            <option value="rolling" selected>{ui["time_filter_rolling"]}</option>
            <option value="all">{ui["time_filter_all"]}</option>
          </select>
        </div>
      </div>

      <div class="off-results-status">
        <span id="off-results-count">Showing {len(rolling_releases)} of {total_releases} releases</span>
        <button id="off-reset-filters" class="off-reset-btn" style="display: none;">{ui["clear_filters"]}</button>
      </div>

      <div id="off-timeline-container" class="off-timeline">
        <div class="off-timeline-line"></div>
        {"".join(timeline_items)}
      </div>

      <div id="off-empty-state" class="off-empty-state" style="display: none;">
        <p>🔍 {ui["empty_message"]}</p>
        <button onclick="document.getElementById('off-reset-filters').click();" class="off-rel-btn">{ui["clear_filters"]}</button>
      </div>
    </div>
    """

    # Assemble Full Fragment
    full_html = f"""<!--
  Open Food Facts — Ecosystem Releases & Features
  Compiled automatically via scripts/compile_releases.py
-->
<div class="off-releases-page">
  <header class="off-releases-hero">
    <div class="off-hero-content">
      <div class="off-hero-badge">
        <span class="off-hero-badge-dot"></span>
        <span>{ui["badge"]}</span>
      </div>
      <h1 class="off-hero-title">{page_title}</h1>
      <p class="off-hero-lead">{subtitle}</p>
      
      <!-- KPI Stats Bar -->
      <div class="off-stats-bar">
        <div class="off-stat-card">
          <span class="off-stat-val">{len(rolling_releases)}</span>
          <span class="off-stat-label">{ui["stat_rolling"]}</span>
        </div>
        <div class="off-stat-card">
          <span class="off-stat-val">{len(highlights)}</span>
          <span class="off-stat-label">{ui["stat_pillars"]}</span>
        </div>
        <div class="off-stat-card">
          <span class="off-stat-val">{len(active_repos)}</span>
          <span class="off-stat-label">{ui["stat_repos"]}</span>
        </div>
        <div class="off-stat-card">
          <span class="off-stat-val">{total_releases}</span>
          <span class="off-stat-label">{ui["stat_releases"]}</span>
        </div>
      </div>

      <!-- View Switcher Tabs -->
      <nav class="off-tab-nav" aria-label="Release Views">
        <button id="tab-btn-highlights" class="off-tab-btn active" data-target="view-highlights">
          {ui["tab_highlights"]}
        </button>
        <button id="tab-btn-timeline" class="off-tab-btn" data-target="view-timeline">
          {ui["tab_timeline"]}
        </button>
      </nav>
    </div>
  </header>

  <main class="off-releases-main">
    {highlights_section}
    {timeline_section}
    
    <footer class="off-releases-footer">
      <p>
        {ui["wiki_source"]}
        <a href="https://wiki.openfoodfacts.org/Releases_%26_Features" target="_blank" rel="noopener">
          Open Food Facts Wiki: Releases & Features
        </a>.
      </p>
    </footer>
  </main>
</div>

<style>
/* ==========================================================================
   Open Food Facts — Releases & Features Timeline Design System Styles
   Adhering to https://openfoodfacts.github.io/openfoodfacts-design/
   ========================================================================== */
.off-releases-page {{
  --off-brand-gradient: linear-gradient(135deg, #ed8857 0%, #ea580c 50%, #c2410c 100%);
  --off-primary: #ea580c;
  --off-primary-dark: #c2410c;
  --off-primary-light: #fff7ed;
  --off-primary-border: #fed7aa;
  --off-slate-900: #0f172a;
  --off-slate-800: #1e293b;
  --off-slate-700: #334155;
  --off-slate-600: #475569;
  --off-slate-500: #64748b;
  --off-slate-200: #e2e8f0;
  --off-slate-100: #f1f5f9;
  --off-slate-50: #f8fafc;
  --off-radius-card: 16px;
  --off-radius-pill: 9999px;
  --off-shadow-sm: 0 1px 3px rgba(0,0,0,0.06), 0 1px 2px rgba(0,0,0,0.04);
  --off-shadow-md: 0 4px 14px rgba(15, 23, 42, 0.06), 0 1px 3px rgba(15, 23, 42, 0.04);
  --off-shadow-hover: 0 10px 25px rgba(234, 88, 12, 0.12), 0 4px 10px rgba(15, 23, 42, 0.04);
  font-family: "Plus Jakarta Sans", -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
  color: var(--off-slate-900);
  background: #fdfcfb;
  margin: 0;
  padding: 0 0 4rem;
  line-height: 1.6;
}}

.off-releases-page * {{
  box-sizing: border-box;
}}

/* Accessibility: focus-visible */
.off-releases-page a:focus-visible,
.off-releases-page button:focus-visible,
.off-releases-page select:focus-visible,
.off-releases-page input:focus-visible,
.off-releases-page summary:focus-visible {{
  outline: 3px solid #ea580c;
  outline-offset: 3px;
}}

/* Hero Section */
.off-releases-hero {{
  background: linear-gradient(180deg, #fffaf5 0%, #fdfcfb 100%);
  border-bottom: 1px solid var(--off-slate-200);
  padding: 3.5rem 1.5rem 2rem;
  text-align: center;
}}
.off-hero-content {{
  max-width: 1040px;
  margin: 0 auto;
}}
.off-hero-badge {{
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 0.4rem 1rem;
  background: var(--off-primary-light);
  color: var(--off-primary-dark);
  border: 1px solid var(--off-primary-border);
  border-radius: var(--off-radius-pill);
  font-size: 0.85rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.04em;
  margin-bottom: 1.25rem;
}}
.off-hero-badge-dot {{
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: var(--off-primary);
  box-shadow: 0 0 0 3px rgba(234, 88, 12, 0.2);
}}
.off-hero-title {{
  font-size: clamp(2rem, 4vw, 2.85rem);
  font-weight: 800;
  color: var(--off-slate-900);
  line-height: 1.2;
  margin: 0 0 1rem;
  letter-spacing: -0.02em;
  text-wrap: balance;
}}
.off-hero-lead {{
  font-size: 1.1rem;
  color: var(--off-slate-600);
  line-height: 1.6;
  max-width: 800px;
  margin: 0 auto 2.25rem;
  text-wrap: pretty;
}}

/* Stats Bar */
.off-stats-bar {{
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(160px, 1fr));
  gap: 1rem;
  max-width: 840px;
  margin: 0 auto 2.5rem;
}}
.off-stat-card {{
  background: #ffffff;
  border: 1px solid var(--off-slate-200);
  border-radius: 12px;
  padding: 1rem 1.25rem;
  box-shadow: var(--off-shadow-sm);
  display: flex;
  flex-direction: column;
  align-items: center;
}}
.off-stat-val {{
  font-size: 1.75rem;
  font-weight: 800;
  color: var(--off-primary);
  line-height: 1.1;
  font-feature-settings: "tnum";
}}
.off-stat-label {{
  font-size: 0.8rem;
  color: var(--off-slate-500);
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.03em;
  margin-top: 0.35rem;
}}

/* View Switcher Tabs */
.off-tab-nav {{
  display: inline-flex;
  background: var(--off-slate-100);
  padding: 5px;
  border-radius: var(--off-radius-pill);
  border: 1px solid var(--off-slate-200);
  gap: 4px;
}}
.off-tab-btn {{
  background: transparent;
  border: none;
  padding: 0.65rem 1.4rem;
  border-radius: var(--off-radius-pill);
  font-size: 0.95rem;
  font-weight: 700;
  color: var(--off-slate-600);
  cursor: pointer;
  transition: all 0.2s ease;
  font-family: inherit;
}}
.off-tab-btn:hover {{
  color: var(--off-slate-900);
}}
.off-tab-btn.active {{
  background: #ffffff;
  color: var(--off-primary-dark);
  box-shadow: var(--off-shadow-sm);
}}

/* Main Container */
.off-releases-main {{
  max-width: 1100px;
  margin: 2.5rem auto 0;
  padding: 0 1.25rem;
}}
.off-view-section {{
  display: none;
}}
.off-view-section.active {{
  display: block;
  animation: offFadeIn 0.25s ease-out;
}}
@keyframes offFadeIn {{
  from {{ opacity: 0; transform: translateY(6px); }}
  to {{ opacity: 1; transform: translateY(0); }}
}}

/* Curated Highlights View */
.off-hl-banner {{
  display: flex;
  align-items: flex-start;
  gap: 1rem;
  background: #fffaf5;
  border: 1px solid var(--off-primary-border);
  border-radius: 12px;
  padding: 1.15rem 1.4rem;
  margin-bottom: 2rem;
  font-size: 0.95rem;
  color: #7c2d12;
  line-height: 1.55;
}}
.off-hl-banner-icon {{
  font-size: 1.6rem;
  line-height: 1;
}}
.off-highlights-grid {{
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(480px, 1fr));
  gap: 1.5rem;
}}
@media (max-width: 600px) {{
  .off-highlights-grid {{
    grid-template-columns: 1fr;
  }}
}}
.off-hl-card {{
  background: #ffffff;
  border: 1px solid var(--off-slate-200);
  border-radius: var(--off-radius-card);
  padding: 1.6rem;
  box-shadow: var(--off-shadow-sm);
  display: flex;
  flex-direction: column;
  transition: transform 0.2s ease, box-shadow 0.2s ease, border-color 0.2s ease;
}}
.off-hl-card:hover {{
  transform: translateY(-2px);
  box-shadow: var(--off-shadow-md);
  border-color: #fed7aa;
}}
.off-hl-header {{
  display: flex;
  align-items: center;
  justify-content: space-between;
  flex-wrap: wrap;
  gap: 0.5rem;
  margin-bottom: 0.85rem;
}}
.off-hl-badges {{
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  gap: 0.5rem;
}}
.off-badge-pill {{
  font-size: 0.72rem;
  font-weight: 700;
  text-transform: uppercase;
  padding: 0.22rem 0.6rem;
  border-radius: var(--off-radius-pill);
  letter-spacing: 0.04em;
}}
.off-badge-impact {{
  background: #ffedd5;
  color: #c2410c;
  border: 1px solid #fed7aa;
}}
.off-badge-cat {{
  background: #f1f5f9;
  color: #334155;
}}
.off-hl-date {{
  font-size: 0.8rem;
  color: var(--off-slate-500);
  font-weight: 600;
}}
.off-hl-repos {{
  display: flex;
  gap: 0.35rem;
}}
.off-hl-repo-pill {{
  font-family: "JetBrains Mono", monospace;
  font-size: 0.75rem;
  background: #f8fafc;
  border: 1px solid #e2e8f0;
  padding: 0.15rem 0.45rem;
  border-radius: 6px;
  color: #475569;
}}
.off-hl-title {{
  font-size: 1.35rem;
  font-weight: 800;
  color: var(--off-slate-900);
  line-height: 1.3;
  margin: 0 0 0.75rem;
}}
.off-hl-summary {{
  font-size: 0.95rem;
  color: var(--off-slate-700);
  line-height: 1.55;
  margin: 0 0 1.25rem;
}}
.off-hl-body {{
  background: #fafaf9;
  border-radius: 10px;
  padding: 1rem 1.15rem;
  margin-bottom: 1.25rem;
}}
.off-hl-subheading {{
  font-size: 0.8rem;
  font-weight: 800;
  text-transform: uppercase;
  color: var(--off-slate-500);
  letter-spacing: 0.05em;
  margin: 0 0 0.5rem;
}}
.off-hl-list {{
  margin: 0;
  padding-left: 1.2rem;
  font-size: 0.88rem;
  color: var(--off-slate-700);
}}
.off-hl-list li {{
  margin-bottom: 0.4rem;
}}
.off-hl-links {{
  margin-top: auto;
  display: flex;
  flex-wrap: wrap;
  gap: 0.65rem;
  padding-top: 0.75rem;
  border-top: 1px solid var(--off-slate-100);
}}
.off-hl-link {{
  display: inline-flex;
  align-items: center;
  gap: 4px;
  font-size: 0.85rem;
  font-weight: 700;
  color: var(--off-primary);
  text-decoration: none;
  transition: color 0.15s ease;
}}
.off-hl-link:hover {{
  color: var(--off-primary-dark);
  text-decoration: underline;
}}

/* Filter Toolbar */
.off-filter-toolbar {{
  background: #ffffff;
  border: 1px solid var(--off-slate-200);
  border-radius: 14px;
  padding: 1rem 1.25rem;
  box-shadow: var(--off-shadow-sm);
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  justify-content: space-between;
  gap: 1rem;
  margin-bottom: 1rem;
}}
.off-search-wrap {{
  flex: 1 1 280px;
  position: relative;
  display: flex;
  align-items: center;
}}
.off-search-icon {{
  position: absolute;
  left: 12px;
  font-size: 0.95rem;
  pointer-events: none;
  opacity: 0.6;
}}
.off-search-input {{
  width: 100%;
  padding: 0.6rem 0.85rem 0.6rem 2.3rem;
  border: 1px solid var(--off-slate-200);
  border-radius: 10px;
  font-size: 0.9rem;
  font-family: inherit;
  color: var(--off-slate-900);
  background: #fdfcfb;
  transition: border-color 0.15s ease, background 0.15s ease;
}}
.off-search-input:focus {{
  background: #ffffff;
  border-color: var(--off-primary);
}}
.off-filter-group {{
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 0.65rem;
}}
.off-filter-select {{
  padding: 0.55rem 0.85rem;
  border: 1px solid var(--off-slate-200);
  border-radius: 10px;
  font-size: 0.85rem;
  font-weight: 600;
  color: var(--off-slate-700);
  background: #ffffff;
  cursor: pointer;
  font-family: inherit;
}}
.off-results-status {{
  display: flex;
  align-items: center;
  justify-content: space-between;
  font-size: 0.85rem;
  color: var(--off-slate-500);
  font-weight: 600;
  margin-bottom: 1.5rem;
  padding: 0 0.5rem;
}}
.off-reset-btn {{
  background: transparent;
  border: none;
  color: var(--off-primary);
  font-weight: 700;
  cursor: pointer;
  font-size: 0.85rem;
  padding: 0;
}}
.off-reset-btn:hover {{
  text-decoration: underline;
}}

/* Aukilo-style Timeline */
.off-timeline {{
  position: relative;
  padding: 1rem 0;
}}
.off-timeline-line {{
  position: absolute;
  top: 15px;
  bottom: 15px;
  left: 20px;
  width: 2px;
  background: #fed7aa;
}}
@media (max-width: 680px) {{
  .off-timeline-line {{
    left: 12px;
  }}
}}
.off-rel-item {{
  position: relative;
  display: flex;
  align-items: flex-start;
  gap: 1.75rem;
  margin-bottom: 2rem;
}}
@media (max-width: 680px) {{
  .off-rel-item {{
    gap: 1rem;
  }}
}}
.off-timeline-dot {{
  position: relative;
  z-index: 2;
  width: 14px;
  height: 14px;
  border-radius: 50%;
  background: var(--off-primary);
  border: 3px solid #ffffff;
  box-shadow: 0 0 0 2px var(--off-primary);
  margin-top: 18px;
  margin-left: 14px;
  flex-shrink: 0;
}}
@media (max-width: 680px) {{
  .off-timeline-dot {{
    margin-left: 6px;
    width: 12px;
    height: 12px;
  }}
}}
.off-rel-card {{
  flex: 1;
  background: #ffffff;
  border: 1px solid var(--off-slate-200);
  border-radius: var(--off-radius-card);
  padding: 1.35rem 1.5rem;
  box-shadow: var(--off-shadow-sm);
  transition: transform 0.2s ease, box-shadow 0.2s ease;
}}
.off-rel-card:hover {{
  box-shadow: var(--off-shadow-md);
  border-color: #cbd5e1;
}}
.off-rel-meta {{
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  gap: 0.6rem;
  margin-bottom: 0.65rem;
}}
.off-rel-tag {{
  font-family: "JetBrains Mono", monospace;
  font-size: 0.85rem;
  font-weight: 700;
  background: #f1f5f9;
  color: var(--off-slate-900);
  padding: 0.18rem 0.55rem;
  border-radius: 6px;
}}
.off-rel-cat-badge {{
  font-size: 0.72rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.04em;
  padding: 0.18rem 0.55rem;
  border-radius: var(--off-radius-pill);
}}
.off-rel-repo {{
  font-size: 0.85rem;
  font-weight: 700;
  color: var(--off-slate-600);
}}
.off-rel-date {{
  margin-left: auto;
  font-size: 0.82rem;
  font-weight: 600;
  color: var(--off-slate-500);
}}
.off-rel-title {{
  font-size: 1.15rem;
  font-weight: 800;
  color: var(--off-slate-900);
  margin: 0 0 0.5rem;
  line-height: 1.35;
}}
.off-rel-title a {{
  color: inherit;
  text-decoration: none;
}}
.off-rel-title a:hover {{
  color: var(--off-primary);
}}
.off-rel-summary {{
  font-size: 0.9rem;
  color: var(--off-slate-600);
  margin: 0 0 0.85rem;
  line-height: 1.5;
}}

/* Expandable Details Disclosure */
.off-rel-details {{
  margin-top: 0.75rem;
  border-top: 1px dashed var(--off-slate-200);
  padding-top: 0.75rem;
}}
.off-rel-summary-toggle {{
  cursor: pointer;
  list-style: none;
  font-size: 0.85rem;
  font-weight: 700;
  color: var(--off-primary);
  display: inline-flex;
  align-items: center;
  gap: 5px;
}}
.off-rel-summary-toggle::-webkit-details-marker {{
  display: none;
}}
.off-rel-summary-toggle::after {{
  content: "▾";
  font-size: 0.9em;
  transition: transform 0.2s ease;
}}
.off-rel-details[open] .off-rel-summary-toggle::after {{
  transform: rotate(180deg);
}}
.off-rel-prose {{
  background: #fbfcfe;
  border: 1px solid #edf2f7;
  border-radius: 10px;
  padding: 1rem 1.25rem;
  margin-top: 0.75rem;
  font-size: 0.85rem;
  color: var(--off-slate-700);
  max-height: 480px;
  overflow-y: auto;
}}
.off-rel-prose h2, .off-rel-prose h3, .off-rel-prose h4 {{
  font-size: 0.95rem;
  font-weight: 700;
  color: var(--off-slate-800);
  margin: 0.8rem 0 0.35rem;
}}
.off-rel-prose ul {{
  margin: 0.25rem 0 0.75rem;
  padding-left: 1.2rem;
}}
.off-rel-prose li {{
  margin-bottom: 0.3rem;
}}
.off-rel-prose a {{
  color: var(--off-primary);
  text-decoration: underline;
}}
.off-rel-actions {{
  display: flex;
  justify-content: flex-end;
  margin-top: 0.85rem;
}}
.off-rel-btn {{
  display: inline-flex;
  align-items: center;
  gap: 4px;
  font-size: 0.8rem;
  font-weight: 700;
  color: var(--off-slate-700);
  background: var(--off-slate-100);
  border: 1px solid var(--off-slate-200);
  border-radius: 8px;
  padding: 0.35rem 0.75rem;
  text-decoration: none;
  cursor: pointer;
  transition: all 0.15s ease;
}}
.off-rel-btn:hover {{
  background: var(--off-primary);
  color: #ffffff;
  border-color: var(--off-primary);
}}

/* Empty state */
.off-empty-state {{
  text-align: center;
  padding: 3.5rem 1rem;
  background: #ffffff;
  border: 1px dashed var(--off-slate-200);
  border-radius: var(--off-radius-card);
  color: var(--off-slate-500);
  font-size: 1.05rem;
}}

/* Footer */
.off-releases-footer {{
  text-align: center;
  margin-top: 3.5rem;
  padding-top: 1.5rem;
  border-top: 1px solid var(--off-slate-200);
  font-size: 0.85rem;
  color: var(--off-slate-500);
}}
.off-releases-footer a {{
  color: var(--off-primary);
  text-decoration: none;
  font-weight: 600;
}}
.off-releases-footer a:hover {{
  text-decoration: underline;
}}
</style>

<script>
// Open Food Facts Releases & Features Interactive Filter and View Controller
(function() {{
  const tabHighlights = document.getElementById('tab-btn-highlights');
  const tabTimeline = document.getElementById('tab-btn-timeline');
  const viewHighlights = document.getElementById('view-highlights');
  const viewTimeline = document.getElementById('view-timeline');

  // Tab switching
  function switchTab(target) {{
    if (target === 'view-highlights') {{
      tabHighlights.classList.add('active');
      tabTimeline.classList.remove('active');
      viewHighlights.classList.add('active');
      viewTimeline.classList.remove('active');
    }} else {{
      tabTimeline.classList.add('active');
      tabHighlights.classList.remove('active');
      viewTimeline.classList.add('active');
      viewHighlights.classList.remove('active');
    }}
  }}

  if (tabHighlights && tabTimeline) {{
    tabHighlights.addEventListener('click', () => switchTab('view-highlights'));
    tabTimeline.addEventListener('click', () => switchTab('view-timeline'));
  }}

  // Timeline Filtering
  const searchInput = document.getElementById('off-search-input');
  const filterCat = document.getElementById('off-filter-cat');
  const filterRepo = document.getElementById('off-filter-repo');
  const filterTime = document.getElementById('off-filter-time');
  const resultsCount = document.getElementById('off-results-count');
  const resetBtn = document.getElementById('off-reset-filters');
  const emptyState = document.getElementById('off-empty-state');
  const items = document.querySelectorAll('.off-rel-item');
  const totalCount = items.length;

  function filterReleases() {{
    const query = (searchInput.value || '').toLowerCase().trim();
    const selCat = filterCat.value;
    const selRepo = filterRepo.value;
    const selTime = filterTime.value;

    let visibleCount = 0;
    const isFiltered = query !== '' || selCat !== 'all' || selRepo !== 'all' || selTime !== 'rolling';

    if (resetBtn) {{
      resetBtn.style.display = isFiltered ? 'inline-block' : 'none';
    }}

    items.forEach(el => {{
      const repo = el.getAttribute('data-repo') || '';
      const cat = el.getAttribute('data-cat') || '';
      const isRolling = el.getAttribute('data-rolling') === 'true';
      const text = el.textContent.toLowerCase();

      let match = true;
      if (selCat !== 'all' && cat !== selCat) match = false;
      if (selRepo !== 'all' && repo !== selRepo) match = false;
      if (selTime === 'rolling' && !isRolling) match = false;
      if (query && !text.includes(query)) match = false;

      if (match) {{
        el.style.display = 'flex';
        visibleCount++;
      }} else {{
        el.style.display = 'none';
      }}
    }});

    if (resultsCount) {{
      resultsCount.textContent = `Showing ${{visibleCount}} of ${{totalCount}} releases`;
    }}

    if (emptyState) {{
      emptyState.style.display = visibleCount === 0 ? 'block' : 'none';
    }}
  }}

  if (searchInput) searchInput.addEventListener('input', filterReleases);
  if (filterCat) filterCat.addEventListener('change', filterReleases);
  if (filterRepo) filterRepo.addEventListener('change', filterReleases);
  if (filterTime) filterTime.addEventListener('change', filterReleases);

  if (resetBtn) {{
    resetBtn.addEventListener('click', () => {{
      if (searchInput) searchInput.value = '';
      if (filterCat) filterCat.value = 'all';
      if (filterRepo) filterRepo.value = 'all';
      if (filterTime) filterTime.value = 'rolling';
      filterReleases();
    }});
  }}

  // Initial filter run (rolling year default)
  filterReleases();
}})();
</script>
"""
    return full_html

def generate_standalone_root_page(en_html):
    """
    Wrap the English releases fragment in the full standalone HTML page
    with Open Food Facts design system navigation and metadata.
    """
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Open Food Facts — Ecosystem Releases & Features</title>
  <meta name="description" content="Automatic release tracker and game-changing innovations timeline across Open Food Facts: core server, mobile app, Open Prices, AI engines, and developer SDKs.">
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800;900&family=JetBrains+Mono:wght@400;500;700&display=swap" rel="stylesheet">
  <style>
    body {{
      margin: 0;
      padding: 0;
      background: #fdfcfb;
      font-family: "Plus Jakarta Sans", -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
      color: #0f172a;
    }}
    .standalone-nav {{
      background: #ffffff;
      border-bottom: 1px solid #e2e8f0;
      padding: 0.75rem 1.5rem;
      display: flex;
      align-items: center;
      justify-content: space-between;
      flex-wrap: wrap;
      gap: 1rem;
    }}
    .standalone-brand {{
      display: flex;
      align-items: center;
      gap: 0.75rem;
      text-decoration: none;
      color: #341100;
      font-weight: 800;
      font-size: 1.1rem;
    }}
    .standalone-brand img {{
      height: 32px;
      width: auto;
    }}
    .standalone-links {{
      display: flex;
      align-items: center;
      gap: 1.25rem;
      font-size: 0.9rem;
    }}
    .standalone-links a {{
      color: #473526;
      text-decoration: none;
      font-weight: 600;
    }}
    .standalone-links a:hover {{
      color: #ed8857;
    }}
    .standalone-links a.active {{
      color: #ea580c;
      font-weight: 700;
    }}
  </style>
</head>
<body>
  <nav class="standalone-nav">
    <a href="https://world.openfoodfacts.org" class="standalone-brand">
      <img src="https://static.openfoodfacts.org/images/logos/off-logo-horizontal-light.svg" alt="Open Food Facts Logo">
      <span>Releases & Features</span>
    </a>
    <div class="standalone-links">
      <a href="releases.html" class="active">Releases</a>
      <a href="data-quality.html">Data Quality</a>
      <a href="scan-parties.html">Scan Parties</a>
      <a href="reuses.html">Reuses</a>
      <a href="press-review.html">Press Review</a>
      <a href="https://wiki.openfoodfacts.org/Releases_%26_Features" target="_blank" rel="noopener">Wiki ↗</a>
      <a href="https://github.com/openfoodfacts" target="_blank" rel="noopener">GitHub ↗</a>
    </div>
  </nav>
  {en_html}
</body>
</html>"""

def compile_releases(check_only=False, verbose=True):
    if verbose:
        print(f"Loading releases from {RELEASES_JSON} and {HIGHLIGHTS_YAML}...")

    releases, highlights, errors, warnings = load_data(validate=True)

    if warnings and verbose:
        for w in warnings:
            print(f"  [WARN] {w}")

    if errors:
        for e in errors:
            print(f"  [ERROR] {e}", file=sys.stderr)
        return False

    if verbose:
        rolling = [r for r in releases if r.get("published_at", "") >= "2025-11-01"]
        print(f"✅ Validated {len(releases)} releases ({len(rolling)} in rolling year) and {len(highlights)} curated highlights.")

    if check_only:
        return True

    # 1. Generate localized HTML fragments
    en_html = ""
    for target_lang in ["en", "fr"]:
        lang_html = build_releases_html(releases, highlights, lang=target_lang)
        if target_lang == "en":
            en_html = lang_html
        lang_path = os.path.join(REPO_ROOT, "lang", target_lang, "texts", "releases.html")
        os.makedirs(os.path.dirname(lang_path), exist_ok=True)
        try:
            with open(lang_path, "w", encoding="utf-8") as f:
                f.write(lang_html)
            if verbose:
                print(f"Wrote {lang_path}")
        except (PermissionError, OSError) as e:
            if verbose:
                print(f"  [WARN] Could not write {lang_path}: {e}")

    # 2. Generate standalone root page
    root_path = os.path.join(REPO_ROOT, "releases.html")
    root_html = generate_standalone_root_page(en_html)
    try:
        with open(root_path, "w", encoding="utf-8") as f:
            f.write(root_html)
        if verbose:
            print(f"Wrote {root_path}")
    except (PermissionError, OSError) as e:
        if verbose:
            print(f"  [WARN] Could not write {root_path}: {e}")

    return True

def main():
    check_mode = "--check" in sys.argv
    success = compile_releases(check_only=check_mode, verbose=True)
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
