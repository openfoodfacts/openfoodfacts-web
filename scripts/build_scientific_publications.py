#!/usr/bin/env python3
"""
Compile data/scientific_publications/*.yaml into:
- data/scientific_publications.json
- lang/en/texts/scientific-publications.html
- lang/fr/texts/scientific-publications.html
"""

import glob
import json
import os
import re
import urllib.parse
import yaml

PUBLICATIONS_DIR = "data/scientific_publications"
OUTPUT_JSON = "data/scientific_publications.json"

def load_all_publications():
    pubs = []
    yaml_files = sorted(glob.glob(os.path.join(PUBLICATIONS_DIR, "*.yaml")))
    for path in yaml_files:
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = yaml.safe_load(f)
                if not data or not isinstance(data, dict):
                    continue
                if not data.get("id"):
                    data["id"] = os.path.splitext(os.path.basename(path))[0]
                pubs.append(data)
        except Exception as e:
            print(f"Warning: Error parsing {path}: {e}")
    
    # Sort by year descending by default
    pubs.sort(key=lambda p: (-(p.get("year") or 0), -(p.get("num_citations") or 0), p.get("title", "")))
    return pubs

def generate_bibtex(p):
    pid = p.get("id", "article")
    authors = " and ".join(p.get("authors") or ["Open Food Facts"])
    title = p.get("title", "")
    journal = p.get("journal", "")
    year = p.get("year", "")
    volume = p.get("volume", "")
    pages = p.get("pages", "")
    doi = p.get("doi", "")
    
    lines = [
        f"@article{{{pid},",
        f"  title = {{{title}}},",
        f"  author = {{{authors}}},"
    ]
    if journal:
        lines.append(f"  journal = {{{journal}}},")
    if year:
        lines.append(f"  year = {{{year}}},")
    if volume:
        lines.append(f"  volume = {{{volume}}},")
    if pages:
        lines.append(f"  pages = {{{pages}}},")
    if doi:
        lines.append(f"  doi = {{{doi}}},")
    lines.append("}")
    return "\n".join(lines)

def generate_apa(p):
    authors = p.get("authors") or []
    if len(authors) > 3:
        author_str = f"{authors[0]} et al."
    elif authors:
        author_str = ", ".join(authors)
    else:
        author_str = "Open Food Facts"

    year_str = f"({p.get('year', '')})" if p.get('year') else ""
    title_str = p.get('title', '').rstrip('.') + "."
    journal_str = f"_{p.get('journal')}_" if p.get('journal') else ""
    vol_str = f", {p.get('volume')}" if p.get('volume') else ""
    pages_str = f", {p.get('pages')}" if p.get('pages') else ""
    doi_str = f" https://doi.org/{p.get('doi')}" if p.get('doi') else ""

    return f"{author_str} {year_str}. {title_str} {journal_str}{vol_str}{pages_str}.{doi_str}".strip()

def generate_html(pubs, lang="en"):
    is_fr = (lang == "fr")
    total_pubs = len(pubs)
    total_citations = sum(p.get("num_citations") or 0 for p in pubs)
    
    unique_years = sorted(set(p.get("year") for p in pubs if p.get("year")), reverse=True)
    all_themes = set()
    for p in pubs:
        for t in p.get("themes", []):
            all_themes.add(t)

    t_title = "🔬 Publications scientifiques citant Open Food Facts" if is_fr else "🔬 Scientific Publications Citing Open Food Facts"
    t_subtitle = (
        "Découvrez les recherches universitaires, études épidémiologiques et projets d'intelligence artificielle fondés sur les données ouvertes d'Open Food Facts."
        if is_fr else
        "Explore academic research, epidemiological studies, and machine learning breakthroughs powered by Open Food Facts open data."
    )

    t_stat_pubs_num = f"{total_pubs}+"
    t_stat_pubs_label = "Articles référencés" if is_fr else "Indexed Publications"
    t_stat_pubs_sub = "Dans cette vitrine" if is_fr else "Curated in this showcase"

    t_stat_cit_num = f"{total_citations:,}+"
    t_stat_cit_label = "Citations cumulées" if is_fr else "Cumulative Citations"
    t_stat_cit_sub = "Reconnaissance scientifique" if is_fr else "Academic impact & reach"

    t_stat_global_num = "600+"
    t_stat_global_label = "Citations Google Scholar" if is_fr else "Google Scholar Papers"
    t_stat_global_sub = "Depuis 2012" if is_fr else "Since 2012"

    t_stat_open_num = "100%"
    t_stat_open_label = "Science ouverte & ODbL" if is_fr else "Open Science & ODbL"
    t_stat_open_sub = "Données accessibles à tous" if is_fr else "Freely accessible open data"

    t_submit_gh_btn = "🚀 Déclarer une publication" if is_fr else "🚀 Submit a Publication"
    t_edit_gh_btn = "✏️ Proposer une modif (PR)" if is_fr else "✏️ Propose an Edit (PR)"
    t_scholar_btn = "🎓 Google Scholar" if is_fr else "🎓 Google Scholar"
    t_resources_drawer_btn = "📚 Ressources & Données" if is_fr else "📚 Researcher Resources"
    t_cite_drawer_btn = "📖 Comment citer OFF" if is_fr else "📖 How to Cite OFF"
    t_webinars_btn = "🎥 Webinaire chercheurs" if is_fr else "🎥 Researcher Webinars"

    # Pre-render publications JSON for the client side
    pubs_client = []
    for p in pubs:
        item = dict(p)
        item["bibtex"] = generate_bibtex(p)
        item["apa"] = generate_apa(p)
        pubs_client.append(item)

    json_data = json.dumps(pubs_client, ensure_ascii=False)

    return f"""<style>
.sci-header {{
  margin: 1.75rem 0 1.25rem;
}}
.sci-actions {{
  display: flex;
  flex-wrap: wrap;
  gap: 0.65rem;
  justify-content: center;
  margin: 1.25rem 0 1.5rem;
}}
.sci-btn {{
  display: inline-flex !important;
  align-items: center !important;
  justify-content: center !important;
  gap: 6px !important;
  font-weight: 600 !important;
  margin: 0 !important;
  vertical-align: middle !important;
  text-decoration: none !important;
}}

/* Ecosystem Impact Hero Bar */
.sci-impact-hero {{
  background: linear-gradient(135deg, #f0fdf4 0%, #eff6ff 100%);
  border: 1px solid #bbf7d0;
  border-radius: 16px;
  padding: 1.25rem 1.5rem;
  margin: 1.25rem auto 1.75rem;
  max-width: 1200px;
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  justify-content: space-around;
  gap: 1.25rem;
  box-shadow: 0 3px 10px rgba(0,0,0,0.03);
}}
.sci-stat-item {{
  text-align: center;
  flex: 1 1 160px;
}}
.sci-stat-number {{
  font-size: 2.1rem;
  font-weight: 900;
  color: #047857;
  line-height: 1.1;
  margin-bottom: 0.2rem;
  font-family: system-ui, -apple-system, sans-serif;
}}
.sci-stat-label {{
  font-size: 0.88rem;
  font-weight: 700;
  color: #0f172a;
  margin-bottom: 0.15rem;
}}
.sci-stat-sub {{
  font-size: 0.76rem;
  color: #64748b;
}}
.sci-stat-divider {{
  width: 1px;
  height: 44px;
  background: #cbd5e1;
  display: none;
}}
@media (min-width: 768px) {{
  .sci-stat-divider {{
    display: block;
  }}
}}

/* Callout Banner */
.sci-banner {{
  background: #f8fafc;
  border: 1px solid #e2e8f0;
  border-left: 4px solid #0284c7;
  border-radius: 12px;
  padding: 1.25rem 1.5rem;
  margin: 1.25rem auto 1.75rem;
  max-width: 1200px;
  text-align: left;
  box-shadow: 0 2px 6px rgba(0,0,0,0.03);
}}
.sci-banner-header {{
  display: flex;
  align-items: center;
  gap: 0.6rem;
  margin-bottom: 0.5rem;
}}
.sci-banner-header h3 {{
  font-size: 1.15rem;
  font-weight: 700;
  color: #0369a1;
  margin: 0;
}}
.sci-banner-text {{
  font-size: 0.92rem;
  color: #334155;
  margin: 0 0 1rem;
  line-height: 1.5;
}}
.sci-banner-links {{
  display: flex;
  flex-wrap: wrap;
  gap: 0.65rem;
}}
.sci-chip-link {{
  display: inline-flex;
  align-items: center;
  gap: 5px;
  padding: 0.35rem 0.75rem;
  border-radius: 20px;
  background: #ffffff;
  border: 1px solid #cbd5e1;
  color: #1e293b;
  font-size: 0.85rem;
  font-weight: 600;
  text-decoration: none;
  transition: all 0.2s ease;
}}
.sci-chip-link:hover {{
  background: #0284c7;
  color: #ffffff;
  border-color: #0284c7;
}}

/* Drawers */
.sci-drawer {{
  display: none;
  background: #f8fafc;
  border: 1px solid #e2e8f0;
  border-radius: 14px;
  padding: 1.5rem;
  max-width: 1200px;
  margin: 0 auto 2rem;
  box-shadow: 0 4px 14px rgba(0,0,0,0.06);
  text-align: left;
}}
.sci-drawer.open {{
  display: block;
  animation: sciFade 0.25s ease-out;
}}
@keyframes sciFade {{
  from {{ opacity: 0; transform: translateY(-6px); }}
  to {{ opacity: 1; transform: translateY(0); }}
}}
.sci-drawer-grid {{
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: 1.25rem;
  margin: 1.25rem 0;
}}
.sci-drawer-card {{
  background: #ffffff;
  border: 1px solid #e2e8f0;
  border-radius: 12px;
  padding: 1.25rem;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
}}
.sci-drawer-card h4 {{
  margin: 0 0 0.5rem;
  font-size: 1.05rem;
  font-weight: 700;
  color: #0f172a;
}}
.sci-drawer-card p {{
  font-size: 0.88rem;
  color: #64748b;
  line-height: 1.45;
  margin: 0 0 1rem;
}}

/* Filter Bar */
.sci-filters-bar {{
  max-width: 1200px;
  margin: 0 auto 1.5rem;
  display: flex;
  flex-wrap: wrap;
  gap: 0.85rem;
  align-items: center;
  justify-content: space-between;
}}
.sci-search-wrap {{
  flex: 1 1 320px;
  position: relative;
}}
.sci-search-input {{
  width: 100% !important;
  padding: 0.65rem 1rem 0.65rem 2.5rem !important;
  border: 1px solid #cbd5e1 !important;
  border-radius: 24px !important;
  font-size: 0.95rem !important;
  background: #ffffff !important;
  box-shadow: 0 1px 3px rgba(0,0,0,0.04) !important;
  margin-bottom: 0 !important;
}}
.sci-search-icon {{
  position: absolute;
  left: 0.85rem;
  top: 50%;
  transform: translateY(-50%);
  color: #94a3b8;
  pointer-events: none;
  font-size: 1.15rem;
}}
.sci-filter-controls {{
  display: flex;
  flex-wrap: wrap;
  gap: 0.65rem;
  align-items: center;
}}
.sci-select {{
  padding: 0.45rem 2rem 0.45rem 0.85rem !important;
  border: 1px solid #cbd5e1 !important;
  border-radius: 20px !important;
  font-size: 0.88rem !important;
  background: #ffffff !important;
  color: #1e293b !important;
  cursor: pointer;
  margin-bottom: 0 !important;
  height: auto !important;
}}

/* Quick Topic Chips */
.topic-chips-bar {{
  max-width: 1200px;
  margin: 0 auto 1.25rem;
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
  align-items: center;
  justify-content: center;
}}
.topic-chips-bar .chip-btn {{
  display: inline-flex;
  align-items: center;
  gap: 5px;
  background: #ffffff;
  border: 1px solid #cbd5e1;
  border-radius: 9999px;
  padding: 0.38rem 0.85rem;
  font-size: 0.84rem;
  font-weight: 600;
  color: #334155;
  cursor: pointer;
  transition: all 0.15s ease;
  user-select: none;
}}
.topic-chips-bar .chip-btn:hover {{
  background: #f1f5f9;
  border-color: #94a3b8;
  color: #0f172a;
}}
.topic-chips-bar .chip-btn.active {{
  background: #0284c7;
  border-color: #0284c7;
  color: #ffffff;
  box-shadow: 0 2px 8px rgba(2,132,199,0.25);
}}

/* Multi Filter Panel */
.multi-filter-panel {{
  display: none;
  background: #f8fafc;
  border: 1px solid #cbd5e1;
  border-radius: 12px;
  padding: 1.25rem;
  max-width: 1200px;
  margin: 0 auto 1.5rem;
  text-align: left;
}}
.multi-filter-panel.open {{
  display: block;
  animation: sciFade 0.2s ease-out;
}}
.multi-filter-grid {{
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
  gap: 1.25rem;
}}
.multi-filter-col h4 {{
  font-size: 0.92rem;
  font-weight: 700;
  color: #0f172a;
  margin: 0 0 0.6rem;
  border-bottom: 2px solid #e2e8f0;
  padding-bottom: 0.3rem;
}}
.filter-checkbox-label {{
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 0.84rem;
  color: #334155;
  margin-bottom: 0.35rem;
  cursor: pointer;
}}
.filter-checkbox-label input {{
  margin: 0 !important;
}}

/* Stats and Count */
.sci-stats {{
  max-width: 1200px;
  margin: 0 auto 1.25rem;
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 0.92rem;
  color: #64748b;
}}
.sci-count {{
  font-weight: 600;
  color: #0f172a;
}}

/* Grid & Cards */
.sci-grid {{
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
  gap: 1.5rem;
  max-width: 1200px;
  margin: 0 auto 2.5rem;
}}
.sci-card {{
  border: 1px solid #e2e8f0;
  border-radius: 16px;
  background: #ffffff;
  padding: 1.35rem;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  text-align: left;
  box-shadow: 0 2px 6px rgba(0,0,0,0.03);
  transition: transform 0.2s ease, box-shadow 0.2s ease, border-color 0.2s ease;
  position: relative;
}}
.sci-card:hover {{
  transform: translateY(-3px);
  box-shadow: 0 10px 22px rgba(0,0,0,0.08);
  border-color: #cbd5e1;
}}
.sci-card.highlighted {{
  border-color: #0284c7 !important;
  box-shadow: 0 0 0 3px rgba(2,132,199,0.2), 0 10px 22px rgba(0,0,0,0.08) !important;
}}
.sci-card-header {{
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 0.5rem;
  margin-bottom: 0.5rem;
}}
.sci-card-year {{
  font-size: 0.82rem;
  font-weight: 700;
  color: #0284c7;
  background: #e0f2fe;
  padding: 0.15rem 0.55rem;
  border-radius: 12px;
}}
.sci-card-citations {{
  font-size: 0.78rem;
  font-weight: 700;
  color: #b45309;
  background: #fef3c7;
  border: 1px solid #fde68a;
  padding: 0.15rem 0.55rem;
  border-radius: 12px;
  display: inline-flex;
  align-items: center;
  gap: 3px;
}}
.sci-card-title {{
  font-size: 1.08rem;
  font-weight: 700;
  color: #0f172a;
  margin: 0 0 0.45rem;
  line-height: 1.35;
}}
.sci-card-title a {{
  color: inherit;
  text-decoration: none;
}}
.sci-card-title a:hover {{
  color: #0284c7;
  text-decoration: underline;
}}
.sci-card-authors {{
  font-size: 0.86rem;
  color: #475569;
  margin-bottom: 0.35rem;
  line-height: 1.4;
}}
.sci-card-journal {{
  font-size: 0.82rem;
  font-style: italic;
  color: #64748b;
  margin-bottom: 0.75rem;
}}
.sci-card-excerpt {{
  background: #f8fafc;
  border-left: 3px solid #cbd5e1;
  border-radius: 4px;
  padding: 0.6rem 0.75rem;
  font-size: 0.82rem;
  color: #334155;
  line-height: 1.45;
  margin: 0 0 0.85rem;
  font-style: italic;
  display: -webkit-box;
  -webkit-line-clamp: 3;
  -webkit-box-orient: vertical;
  overflow: hidden;
}}
.sci-tags-row {{
  display: flex;
  flex-wrap: wrap;
  gap: 0.35rem;
  margin-bottom: 0.85rem;
}}
.sci-tag {{
  font-size: 0.72rem;
  font-weight: 600;
  padding: 0.18rem 0.5rem;
  border-radius: 6px;
  background: #f1f5f9;
  color: #475569;
}}
.sci-tag-theme {{ background: #ecfdf5; color: #047857; }}
.sci-tag-geo {{ background: #eff6ff; color: #1d4ed8; }}

.sci-card-footer {{
  margin-top: auto;
  padding-top: 0.85rem;
  border-top: 1px solid #f1f5f9;
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  justify-content: space-between;
  gap: 0.5rem;
}}
.sci-card-links {{
  display: flex;
  flex-wrap: wrap;
  gap: 0.4rem;
}}
.sci-link-btn {{
  display: inline-flex;
  align-items: center;
  gap: 4px;
  padding: 0.28rem 0.65rem;
  border-radius: 6px;
  font-size: 0.78rem;
  font-weight: 600;
  text-decoration: none;
  border: 1px solid #cbd5e1;
  background: #ffffff;
  color: #334155;
  transition: all 0.15s ease;
}}
.sci-link-btn:hover {{
  background: #f8fafc;
  color: #0284c7;
  border-color: #0284c7;
}}
.sci-details-btn {{
  display: inline-flex;
  align-items: center;
  gap: 4px;
  padding: 0.28rem 0.65rem;
  border-radius: 6px;
  font-size: 0.78rem;
  font-weight: 600;
  border: 1px solid #0284c7;
  background: #0284c7;
  color: #ffffff;
  cursor: pointer;
  transition: all 0.15s ease;
}}
.sci-details-btn:hover {{
  background: #0369a1;
  border-color: #0369a1;
  color: #ffffff;
}}

/* Modal Overlay & Dialog */
.sci-modal-overlay {{
  display: none;
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(15, 23, 42, 0.65);
  backdrop-filter: blur(4px);
  z-index: 99999;
  align-items: center;
  justify-content: center;
  padding: 1.25rem;
  overflow-y: auto;
}}
.sci-modal-overlay.open {{
  display: flex;
  animation: sciModalFadeIn 0.2s ease-out;
}}
@keyframes sciModalFadeIn {{
  from {{ opacity: 0; }}
  to {{ opacity: 1; }}
}}
.sci-modal-container {{
  background: #ffffff;
  border-radius: 18px;
  max-width: 720px;
  width: 100%;
  padding: 2rem;
  position: relative;
  box-shadow: 0 20px 40px rgba(0,0,0,0.22);
  text-align: left;
  max-height: 90vh;
  overflow-y: auto;
}}
.sci-modal-close {{
  position: absolute;
  top: 1rem;
  right: 1.25rem;
  background: none;
  border: none;
  font-size: 2rem;
  color: #94a3b8;
  cursor: pointer;
  line-height: 1;
  padding: 0.2rem 0.5rem;
  border-radius: 8px;
}}
.sci-modal-close:hover {{
  color: #0f172a;
  background: #f1f5f9;
}}
.sci-citation-box {{
  background: #f8fafc;
  border: 1px solid #e2e8f0;
  border-radius: 10px;
  padding: 1rem;
  margin: 1.25rem 0;
  font-family: monospace;
  font-size: 0.85rem;
  white-space: pre-wrap;
  word-break: break-all;
  position: relative;
}}
.sci-copy-icon-btn {{
  position: absolute;
  top: 0.6rem;
  right: 0.6rem;
  background: #ffffff;
  border: 1px solid #cbd5e1;
  border-radius: 6px;
  padding: 0.25rem 0.55rem;
  font-size: 0.78rem;
  cursor: pointer;
}}
</style>

<div class="sci-header text-center">
  <h1 class="title-2 emphasized-title">{t_title}</h1>
  <h4 class="subheader">{t_subtitle}</h4>
  
  <div class="sci-actions">
    <a href="https://github.com/openfoodfacts/openfoodfacts-web/issues/new?title=%5BPublication%5D+New+Scientific+Paper%3A+&labels=science%2Cdocumentation&body=%23%23%23+%F0%9F%93%96+Paper+Title%0A%3C%21--+Enter+full+article+title+--%3E%0A%0A%23%23%23+%F0%9F%91%A8%E2%80%8D%F0%9F%94%AC+Authors+%26+Journal%0A-+Authors%3A+%0A-+Journal+%2F+Conference%3A+%0A-+Year%3A+%0A-+DOI%3A+%0A-+URL%3A+%0A%0A%23%23%23+%F0%9F%94%AC+Open+Food+Facts+Usage+%26+Findings%0A%3C%21--+How+did+this+study+use+Open+Food+Facts+data%3F+--%3E%0A" target="_blank" rel="noopener noreferrer" class="button round primary small sci-btn">
      <span class="material-icons">add_circle</span> {t_submit_gh_btn}
    </a>
    <a href="https://github.com/openfoodfacts/openfoodfacts-web/tree/main/data/scientific_publications" target="_blank" rel="noopener noreferrer" class="button round secondary small sci-btn">
      <span class="material-icons">edit_note</span> {t_edit_gh_btn}
    </a>
    <a href="https://scholar.google.com/scholar?hl=en&as_sdt=0%2C5&q=%22open+food+facts%22+OR+%22openfoodfacts%22&btnG=" target="_blank" rel="noopener noreferrer" class="button round secondary small sci-btn">
      <span class="material-icons">school</span> {t_scholar_btn}
    </a>
    <button type="button" class="button round secondary small sci-btn" onclick="toggleSciDrawer('citeDrawer')">
      <span class="material-icons">format_quote</span> {t_cite_drawer_btn}
    </button>
    <button type="button" class="button round secondary small sci-btn" onclick="toggleSciDrawer('resourcesDrawer')">
      <span class="material-icons">dataset</span> {t_resources_drawer_btn}
    </button>
    <a href="https://link.openfoodfacts.org/form-web-sci-{'fr' if is_fr else 'en'}" target="_blank" rel="noopener noreferrer" class="button round small sci-btn" style="background: #0284c7; border-color: #0284c7; color: #ffffff;">
      <span class="material-icons">videocam</span> {t_webinars_btn}
    </a>
  </div>
</div>

<!-- Impact Hero Stats Bar -->
<div class="sci-impact-hero">
  <div class="sci-stat-item">
    <div class="sci-stat-number">{t_stat_pubs_num}</div>
    <div class="sci-stat-label">{t_stat_pubs_label}</div>
    <div class="sci-stat-sub">{t_stat_pubs_sub}</div>
  </div>
  <div class="sci-stat-divider"></div>
  <div class="sci-stat-item">
    <div class="sci-stat-number">{t_stat_cit_num}</div>
    <div class="sci-stat-label">{t_stat_cit_label}</div>
    <div class="sci-stat-sub">{t_stat_cit_sub}</div>
  </div>
  <div class="sci-stat-divider"></div>
  <div class="sci-stat-item">
    <div class="sci-stat-number">{t_stat_global_num}</div>
    <div class="sci-stat-label">{t_stat_global_label}</div>
    <div class="sci-stat-sub">{t_stat_global_sub}</div>
  </div>
  <div class="sci-stat-divider"></div>
  <div class="sci-stat-item">
    <div class="sci-stat-number">{t_stat_open_num}</div>
    <div class="sci-stat-label">{t_stat_open_label}</div>
    <div class="sci-stat-sub">{t_stat_open_sub}</div>
  </div>
</div>

<!-- Callout Banner for Research Teams -->
<div class="sci-banner">
  <div class="sci-banner-header">
    <span class="material-icons" style="color: #0284c7; font-size: 1.6rem;">biotech</span>
    <h3>{"📢 Vous utilisez Open Food Facts dans un projet de recherche ?" if is_fr else "📢 Conducting research with Open Food Facts? Partner with us!"}</h3>
  </div>
  <p class="sci-banner-text">{"Nous accompagnons les équipes scientifiques (INSERM, Inrae, Cnam, universités) dans l'extraction de données, la création de taxonomies, et l'organisation de scan-parties ciblées." if is_fr else "We support academic and clinical research teams (epidemiology, NLP, nutritional profiling, consumer behavior) with custom data extracts, API access, and targeted scan campaigns."}</p>
  <div class="sci-banner-links">
    <a href="mailto:contact@openfoodfacts.org" class="sci-chip-link">✉️ contact@openfoodfacts.org</a>
    <a href="/data" class="sci-chip-link">💾 {"Téléchargement des bases (Exports)" if is_fr else "Download Database Dumps"}</a>
    <a href="https://wiki.openfoodfacts.org/Open_Food_Facts_and_Science" target="_blank" rel="noopener noreferrer" class="sci-chip-link">📖 {"Page Wiki Science" if is_fr else "Science Wiki"}</a>
    <a href="https://github.com/openfoodfacts/openfoodfacts-web/issues/new?title=%5BPublication%5D+New+Scientific+Paper%3A+&labels=science%2Cdocumentation" target="_blank" rel="noopener noreferrer" class="sci-chip-link">🚀 {"Signaler votre article" if is_fr else "Submit Your Publication"}</a>
  </div>
</div>

<!-- Drawer: How to Cite Open Food Facts -->
<div class="sci-drawer" id="citeDrawer">
  <div style="display: flex; justify-content: space-between; align-items: center;">
    <h3 style="margin: 0; font-size: 1.25rem; color: #0f172a;">{"Comment citer Open Food Facts dans vos travaux scientifiques" if is_fr else "How to Cite Open Food Facts in Academic Publications"}</h3>
    <button type="button" style="background: none; border: none; font-size: 1.5rem; cursor: pointer; color: #64748b;" onclick="toggleSciDrawer('citeDrawer')">&times;</button>
  </div>
  <p style="font-size: 0.92rem; color: #475569; margin: 0.5rem 0 1rem;">{"Si vous utilisez nos données ou notre API dans une publication, merci de mentionner la source et la date d'accès conformément à la licence ODbL." if is_fr else "If you use Open Food Facts in your research, please cite our database and specify the snapshot date according to the ODbL license."}</p>
  
  <div class="sci-drawer-grid">
    <div class="sci-drawer-card">
      <h4>{"Citation du jeu de données (Format APA)" if is_fr else "Dataset Citation (APA Style)"}</h4>
      <p style="background: #f1f5f9; padding: 0.75rem; border-radius: 8px; font-family: monospace; font-size: 0.82rem;">Open Food Facts. (2025). Open Food Facts Database [Data set]. Retrieved from https://world.openfoodfacts.org/data</p>
    </div>
    <div class="sci-drawer-card">
      <h4>{"Citation BibTeX" if is_fr else "BibTeX Entry"}</h4>
      <pre style="background: #f1f5f9; padding: 0.75rem; border-radius: 8px; font-size: 0.78rem; overflow-x: auto;">@misc{{openfoodfacts_dataset,
  author = {{{{Open Food Facts}}}},
  title = {{Open Food Facts Database}},
  year = {{2025}},
  url = {{https://world.openfoodfacts.org/data}},
  note = {{Open Database License (ODbL)}}
}}</pre>
    </div>
  </div>
</div>

<!-- Drawer: Resources for Researchers -->
<div class="sci-drawer" id="resourcesDrawer">
  <div style="display: flex; justify-content: space-between; align-items: center;">
    <h3 style="margin: 0; font-size: 1.25rem; color: #0f172a;">{"Ressources & Accès aux données pour la recherche" if is_fr else "Resources & Data Access for Researchers"}</h3>
    <button type="button" style="background: none; border: none; font-size: 1.5rem; cursor: pointer; color: #64748b;" onclick="toggleSciDrawer('resourcesDrawer')">&times;</button>
  </div>
  <div class="sci-drawer-grid">
    <div class="sci-drawer-card">
      <div>
        <h4>📦 {"Exports de base de données" if is_fr else "Full Database Dumps"}</h4>
        <p>{"Exports quotidiens complets au format JSONL, CSV, MongoDB dump, et Parquet pour l'analyse Big Data." if is_fr else "Daily database snapshots in JSONL, CSV, MongoDB dumps, and Parquet for big-data and statistical analyses."}</p>
      </div>
      <a href="/data" class="button small primary sci-btn">{"Accéder aux exports" if is_fr else "Access Data Page"} &rarr;</a>
    </div>
    <div class="sci-drawer-card">
      <div>
        <h4>🔌 {"API & SDKs" if is_fr else "REST API & SDKs"}</h4>
        <p>{"Interrogez directement notre API avec des bibliothèques officielles en Python (openfoodfacts-python), R, Dart, ou JavaScript." if is_fr else "Direct query access using official SDKs in Python (openfoodfacts-python), R, Dart, and JavaScript."}</p>
      </div>
      <a href="https://wiki.openfoodfacts.org/API" target="_blank" rel="noopener noreferrer" class="button small secondary sci-btn">{"Documentation API" if is_fr else "API Documentation"} &rarr;</a>
    </div>
    <div class="sci-drawer-card">
      <div>
        <h4>⚖️ {"Licences ODbL & DbCL" if is_fr else "Open Licensing (ODbL)"}</h4>
        <p>{"Base de données libre sous licence Open Database License (ODbL) et photos sous Creative Commons CC-BY-SA." if is_fr else "Database contents available under Open Database License (ODbL) and images under Creative Commons CC-BY-SA."}</p>
      </div>
      <a href="/terms-of-use" class="button small secondary sci-btn">{"Conditions d'utilisation" if is_fr else "Terms of Use"} &rarr;</a>
    </div>
  </div>
</div>

<!-- Quick Topic Filter Chips -->
<div class="topic-chips-bar">
  <button type="button" class="chip-btn active" onclick="selectSciTheme(this, 'all')">{"🌟 Tous les articles" if is_fr else "🌟 All Articles"}</button>
  <button type="button" class="chip-btn" onclick="selectSciTheme(this, 'nutrition')">🥗 {"Nutrition & Nutri-Score" if is_fr else "Nutrition & Nutri-Score"}</button>
  <button type="button" class="chip-btn" onclick="selectSciTheme(this, 'ultra_processed')">🏭 {"NOVA & Aliments Ultra-Transformés" if is_fr else "NOVA & Ultra-Processed"}</button>
  <button type="button" class="chip-btn" onclick="selectSciTheme(this, 'additives')">🧪 {"Additifs & Émulsifiants" if is_fr else "Additives & Emulsifiers"}</button>
  <button type="button" class="chip-btn" onclick="selectSciTheme(this, 'computer_science')">🤖 {"IA & Data Science" if is_fr else "AI & Data Science"}</button>
  <button type="button" class="chip-btn" onclick="selectSciTheme(this, 'environment')">♻️ {"Environnement & Éco-Score" if is_fr else "Environment & Eco-Score"}</button>
  <button type="button" class="chip-btn" onclick="selectSciTheme(this, 'labeling')">🏷️ {"Étiquetage & Politiques" if is_fr else "Labeling & Policy"}</button>
  <button type="button" class="chip-btn" onclick="selectSciTheme(this, 'halal_kosher')">🕊️ Halal / Kosher</button>
  <button type="button" class="chip-btn" onclick="selectSciTheme(this, 'allergies')">⚠️ {"Allergies" if is_fr else "Allergies"}</button>
</div>

<!-- Filter Bar -->
<div class="sci-filters-bar">
  <div class="sci-search-wrap">
    <span class="material-icons sci-search-icon">search</span>
    <input type="text" id="sciSearch" class="sci-search-input" placeholder="{'🔍 Rechercher par titre, auteur, revue, extrait, mot-clé...' if is_fr else '🔍 Search by title, author, journal, excerpt, keywords...'}" oninput="applySciFilters()">
  </div>

  <div class="sci-filter-controls">
    <select id="sciSort" class="sci-select" onchange="applySciFilters()">
      <option value="recent">{"📅 Plus récents d'abord" if is_fr else "📅 Most Recent First"}</option>
      <option value="citations">{"⭐ Plus cités d'abord" if is_fr else "⭐ Most Cited First"}</option>
      <option value="usage">{"🔬 Utilisation centrale de OFF" if is_fr else "🔬 Deep OFF Integration"}</option>
      <option value="title">{"Titre (A-Z)" if is_fr else "Title (A-Z)"}</option>
      <option value="journal">{"Revue / Conférence (A-Z)" if is_fr else "Journal / Conference (A-Z)"}</option>
    </select>

    <select id="sciYear" class="sci-select" onchange="applySciFilters()">
      <option value="all">{"Toutes les années" if is_fr else "All Years"}</option>
      {''.join(f'<option value="{y}">{y}</option>' for y in unique_years)}
    </select>

    <button type="button" class="button secondary small" style="margin: 0; border-radius: 20px; font-weight: 600;" onclick="toggleMultiFilterPanel()">
      <span class="material-icons" style="font-size: 15px; vertical-align: -2px;">tune</span> {"Filtres avancés" if is_fr else "Advanced Filters"}
    </button>
  </div>
</div>

<!-- Multi-Criteria Checkbox Panel -->
<div class="multi-filter-panel" id="multiFilterPanel">
  <div class="multi-filter-grid">
    <div class="multi-filter-col">
      <h4>{"Type de publication" if is_fr else "Publication Type"}</h4>
      <label class="filter-checkbox-label"><input type="checkbox" name="filter_type" value="paper" onchange="applySciFilters()"> 📄 {"Article scientifique (Journal)" if is_fr else "Journal Article"}</label>
      <label class="filter-checkbox-label"><input type="checkbox" name="filter_type" value="conference" onchange="applySciFilters()"> 🎤 {"Actes de conférence" if is_fr else "Conference Proceedings"}</label>
      <label class="filter-checkbox-label"><input type="checkbox" name="filter_type" value="study" onchange="applySciFilters()"> 📊 {"Étude & Rapport" if is_fr else "Study / Report"}</label>
      <label class="filter-checkbox-label"><input type="checkbox" name="filter_type" value="thesis" onchange="applySciFilters()"> 🎓 {"Thèse académique" if is_fr else "Thesis / Dissertation"}</label>
      <label class="filter-checkbox-label"><input type="checkbox" name="filter_type" value="review" onchange="applySciFilters()"> 📑 {"Revue systématique" if is_fr else "Review Article"}</label>
    </div>

    <div class="multi-filter-col">
      <h4>{"Portée & Citations" if is_fr else "Reach & Citations"}</h4>
      <label class="filter-checkbox-label"><input type="checkbox" name="filter_cit" value="cit_10" onchange="applySciFilters()"> ⭐ 10+ {"citations" if is_fr else "citations"}</label>
      <label class="filter-checkbox-label"><input type="checkbox" name="filter_cit" value="cit_50" onchange="applySciFilters()"> 🌟 50+ {"citations" if is_fr else "citations"}</label>
      <label class="filter-checkbox-label"><input type="checkbox" name="filter_cit" value="cit_100" onchange="applySciFilters()"> 🏆 100+ {"citations" if is_fr else "citations"}</label>
      <label class="filter-checkbox-label"><input type="checkbox" name="filter_cit" value="has_doi" onchange="applySciFilters()"> 🔗 {"Avec lien DOI" if is_fr else "Has DOI link"}</label>
      <label class="filter-checkbox-label"><input type="checkbox" name="filter_cit" value="has_pdf" onchange="applySciFilters()"> 📑 {"PDF en libre accès" if is_fr else "Open Access PDF"}</label>
    </div>

    <div class="multi-filter-col">
      <h4>{"Pays de l'équipe" if is_fr else "Research Geography"}</h4>
      <label class="filter-checkbox-label"><input type="checkbox" name="filter_country" value="fra" onchange="applySciFilters()"> 🇫🇷 France</label>
      <label class="filter-checkbox-label"><input type="checkbox" name="filter_country" value="usa" onchange="applySciFilters()"> 🇺🇸 USA</label>
      <label class="filter-checkbox-label"><input type="checkbox" name="filter_country" value="deu" onchange="applySciFilters()"> 🇩🇪 {"Allemagne" if is_fr else "Germany"}</label>
      <label class="filter-checkbox-label"><input type="checkbox" name="filter_country" value="esp" onchange="applySciFilters()"> 🇪🇸 {"Espagne" if is_fr else "Spain"}</label>
      <label class="filter-checkbox-label"><input type="checkbox" name="filter_country" value="ita" onchange="applySciFilters()"> 🇮🇹 {"Italie" if is_fr else "Italy"}</label>
      <label class="filter-checkbox-label"><input type="checkbox" name="filter_country" value="bel" onchange="applySciFilters()"> 🇧🇪 {"Belgique" if is_fr else "Belgium"}</label>
    </div>
  </div>
  <div style="margin-top: 1rem; text-align: right;">
    <button type="button" class="button secondary small" onclick="resetSciFilters()" style="margin: 0;">{"Réinitialiser les filtres" if is_fr else "Clear all criteria"}</button>
  </div>
</div>

<!-- Stats and Count -->
<div class="sci-stats">
  <div class="sci-count" id="sciCount">{"Chargement des publications..." if is_fr else "Loading publications..."}</div>
  <button type="button" class="button secondary small" onclick="resetSciFilters()" style="margin: 0;">{"Tout réinitialiser" if is_fr else "Reset All"}</button>
</div>

<!-- Publication Grid -->
<div class="sci-grid" id="sciGrid"></div>

<!-- Load More Pagination Bar -->
<div id="sciLoadMoreWrap" style="display: none; justify-content: center; gap: 0.75rem; margin: 2rem 0 3.5rem;">
  <button type="button" id="sciLoadMoreBtn" class="button round primary sci-btn" onclick="loadMoreSciCards()"></button>
  <button type="button" class="button round secondary sci-btn" onclick="showAllSciCards()">{"Tout afficher" if is_fr else "Show all"}</button>
</div>

<!-- Publication Details & Citation Modal -->
<div id="sciModalOverlay" class="sci-modal-overlay" onclick="onSciModalBackdropClick(event)">
  <div class="sci-modal-container" role="dialog" aria-modal="true">
    <button type="button" class="sci-modal-close" onclick="closeSciModal()">&times;</button>
    
    <div style="display: flex; gap: 8px; align-items: center; margin-bottom: 0.75rem;">
      <span id="modalYearBadge" class="sci-card-year"></span>
      <span id="modalCitBadge" class="sci-card-citations" style="display: none;"></span>
      <span id="modalTypeBadge" class="sci-tag"></span>
    </div>

    <h2 id="modalTitle" style="font-size: 1.35rem; font-weight: 800; color: #0f172a; margin: 0 0 0.5rem; line-height: 1.35;"></h2>
    <div id="modalAuthors" style="font-size: 0.95rem; color: #475569; margin-bottom: 0.4rem; font-weight: 600;"></div>
    <div id="modalJournal" style="font-size: 0.9rem; font-style: italic; color: #64748b; margin-bottom: 1rem;"></div>

    <!-- Excerpt with Open Food Facts Context -->
    <div id="modalExcerptWrap" style="display: none;">
      <div style="font-weight: 700; font-size: 0.88rem; color: #0f172a; margin-bottom: 0.35rem;">{"Extrait citant ou utilisant Open Food Facts :" if is_fr else "Excerpt referencing Open Food Facts:"}</div>
      <div id="modalExcerpt" class="sci-card-excerpt" style="-webkit-line-clamp: unset; font-size: 0.88rem; padding: 0.85rem 1rem;"></div>
    </div>

    <!-- Links Grid -->
    <div style="display: flex; flex-wrap: wrap; gap: 0.6rem; margin: 1.25rem 0;" id="modalLinksGrid"></div>

    <!-- Citation Box (BibTeX) -->
    <div style="margin-top: 1.25rem;">
      <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.35rem;">
        <span style="font-weight: 700; font-size: 0.88rem; color: #0f172a;">{"Notice BibTeX :" if is_fr else "BibTeX Entry:"}</span>
        <button type="button" class="button small secondary" style="margin: 0; padding: 0.2rem 0.6rem; font-size: 0.78rem;" onclick="copyBibtex()"><span class="material-icons" style="font-size: 14px; vertical-align: -2px;">content_copy</span> {"Copier BibTeX" if is_fr else "Copy BibTeX"}</button>
      </div>
      <div id="modalBibtex" class="sci-citation-box"></div>
    </div>

    <!-- APA Citation Box -->
    <div>
      <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.35rem;">
        <span style="font-weight: 700; font-size: 0.88rem; color: #0f172a;">{"Citation (Style APA) :" if is_fr else "Citation (APA Style):"}</span>
        <button type="button" class="button small secondary" style="margin: 0; padding: 0.2rem 0.6rem; font-size: 0.78rem;" onclick="copyApa()"><span class="material-icons" style="font-size: 14px; vertical-align: -2px;">content_copy</span> {"Copier APA" if is_fr else "Copy APA"}</button>
      </div>
      <div id="modalApa" style="background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 8px; padding: 0.75rem 1rem; font-size: 0.85rem; color: #334155;"></div>
    </div>

    <!-- Propose edit box -->
    <div style="background: #f0fdf4; border: 1px solid #bbf7d0; border-radius: 10px; padding: 1rem; margin-top: 1.25rem; display: flex; flex-direction: column; gap: 0.5rem;">
      <div style="display: flex; align-items: center; gap: 6px; font-size: 0.86rem; color: #166534;">
        <span class="material-icons" style="font-size: 18px; color: #16a34a;">edit_note</span>
        <span>{"Une information est inexacte ou vous êtes l'auteur de cette étude ? Proposez une mise à jour sur GitHub." if is_fr else "Notice inaccurate information or are you the author? Propose an update on GitHub."}</span>
      </div>
      <a id="modalEditLink" href="https://github.com/openfoodfacts/openfoodfacts-web/tree/main/data/scientific_publications" target="_blank" rel="noopener noreferrer" class="button small secondary sci-btn" style="align-self: flex-start;">
        <span class="material-icons" style="font-size: 14px;">edit</span> {"Modifier ce fichier YAML sur GitHub" if is_fr else "Edit this YAML on GitHub"}
      </a>
    </div>
  </div>
</div>

<script>
const IS_FR = {"true" if is_fr else "false"};
const PUBLICATIONS_DATA = {json_data};

const THEME_LABELS = {{
  "nutrition": IS_FR ? "🥗 Nutrition" : "🥗 Nutrition",
  "nutrient_profiling": IS_FR ? "🎯 Profilage nutritionnel" : "🎯 Nutrient Profiling",
  "ultra_processed": IS_FR ? "🏭 Ultra-transformé (NOVA)" : "🏭 Ultra-Processed (NOVA)",
  "additives": IS_FR ? "🧪 Additifs" : "🧪 Additives",
  "labeling": IS_FR ? "🏷️ Étiquetage" : "🏷️ Labeling",
  "computer_science": IS_FR ? "🤖 IA & Data Science" : "🤖 AI & Data Science",
  "environment": IS_FR ? "♻️ Environnement" : "♻️ Environment",
  "halal_kosher": "🕊️ Halal / Kosher",
  "allergies": IS_FR ? "⚠️ Allergies" : "⚠️ Allergies",
  "mobile_apps": IS_FR ? "📱 Applications" : "📱 Mobile Apps",
  "economy": IS_FR ? "💶 Économie" : "💶 Economy",
  "digital_platforms": IS_FR ? "🌐 Plateformes" : "🌐 Digital Platforms"
}};

const COUNTRY_FLAGS = {{
  "fra": "🇫🇷 France",
  "usa": "🇺🇸 USA",
  "deu": "🇩🇪 " + (IS_FR ? "Allemagne" : "Germany"),
  "esp": "🇪🇸 " + (IS_FR ? "Espagne" : "Spain"),
  "ita": "🇮🇹 " + (IS_FR ? "Italie" : "Italy"),
  "bel": "🇧🇪 " + (IS_FR ? "Belgique" : "Belgium"),
  "che": "🇨🇭 " + (IS_FR ? "Suisse" : "Switzerland"),
  "gbr": "🇬🇧 UK"
}};

let selectedQuickTheme = "all";
let currentFilteredList = [];
let displayedCount = 0;
const PAGE_SIZE = 36;

function toggleSciDrawer(id) {{
  const el = document.getElementById(id);
  if (el) el.classList.toggle("open");
}}

function toggleMultiFilterPanel() {{
  const p = document.getElementById("multiFilterPanel");
  if (p) p.classList.toggle("open");
}}

function selectSciTheme(btn, themeVal) {{
  selectedQuickTheme = themeVal;
  document.querySelectorAll(".topic-chips-bar .chip-btn").forEach(el => el.classList.remove("active"));
  if (btn) btn.classList.add("active");
  applySciFilters();
}}

function getCheckedValues(name) {{
  return Array.from(document.querySelectorAll('input[name="' + name + '"]:checked')).map(el => el.value);
}}

function resetSciFilters() {{
  document.getElementById("sciSearch").value = "";
  document.getElementById("sciSort").value = "recent";
  document.getElementById("sciYear").value = "all";
  document.querySelectorAll('input[name="filter_type"]').forEach(el => el.checked = false);
  document.querySelectorAll('input[name="filter_cit"]').forEach(el => el.checked = false);
  document.querySelectorAll('input[name="filter_country"]').forEach(el => el.checked = false);
  selectSciTheme(document.querySelector(".topic-chips-bar .chip-btn"), "all");
}}

function applySciFilters() {{
  const q = document.getElementById("sciSearch").value.toLowerCase().trim();
  const sortVal = document.getElementById("sciSort").value;
  const yearVal = document.getElementById("sciYear").value;

  const checkedTypes = getCheckedValues("filter_type");
  const checkedCits = getCheckedValues("filter_cit");
  const checkedCountries = getCheckedValues("filter_country");

  let filtered = PUBLICATIONS_DATA.filter(p => {{
    // Quick theme chip
    if (selectedQuickTheme !== "all") {{
      const themes = p.themes || [];
      if (!themes.includes(selectedQuickTheme)) return false;
    }}

    // Year
    if (yearVal !== "all" && String(p.year) !== yearVal) {{
      return false;
    }}

    // Publication Type
    if (checkedTypes.length > 0) {{
      const pType = p.type || "paper";
      if (!checkedTypes.includes(pType)) return false;
    }}

    // Reach / Citations checkboxes
    if (checkedCits.length > 0) {{
      for (const c of checkedCits) {{
        if (c === "cit_10" && (p.num_citations || 0) < 10) return false;
        if (c === "cit_50" && (p.num_citations || 0) < 50) return false;
        if (c === "cit_100" && (p.num_citations || 0) < 100) return false;
        if (c === "has_doi" && !p.doi) return false;
        if (c === "has_pdf" && !p.url_pdf) return false;
      }}
    }}

    // Country
    if (checkedCountries.length > 0) {{
      if (!p.country || !checkedCountries.includes(p.country.toLowerCase())) return false;
    }}

    // Search query
    if (q) {{
      const authors = (p.authors || []).join(" ").toLowerCase();
      const title = (p.title || "").toLowerCase();
      const journal = (p.journal || "").toLowerCase();
      const excerpt = (p.excerpt || "").toLowerCase();
      const doi = (p.doi || "").toLowerCase();
      if (!title.includes(q) && !authors.includes(q) && !journal.includes(q) && !excerpt.includes(q) && !doi.includes(q)) {{
        return false;
      }}
    }}

    return true;
  }});

  // Sort
  filtered.sort((a, b) => {{
    if (sortVal === "recent") {{
      return (b.year || 0) - (a.year || 0) || (b.num_citations || 0) - (a.num_citations || 0);
    }} else if (sortVal === "citations") {{
      return (b.num_citations || 0) - (a.num_citations || 0) || (b.year || 0) - (a.year || 0);
    }} else if (sortVal === "usage") {{
      return (b.usage_score || 0) - (a.usage_score || 0) || (b.num_citations || 0) - (a.num_citations || 0);
    }} else if (sortVal === "title") {{
      return (a.title || "").localeCompare(b.title || "");
    }} else if (sortVal === "journal") {{
      return (a.journal || "").localeCompare(b.journal || "");
    }}
    return 0;
  }});

  renderSciList(filtered);
}}

function renderSciCard(p) {{
  const yearBadge = p.year ? '<span class="sci-card-year">' + p.year + '</span>' : '';
  const citBadge = (p.num_citations !== null && p.num_citations !== undefined && p.num_citations > 0)
    ? '<span class="sci-card-citations" title="' + p.num_citations + ' ' + (IS_FR ? "citations académiques" : "citations") + '">⭐ ' + p.num_citations + ' ' + (IS_FR ? "cit." : "cit.") + '</span>'
    : '';

  const authorsStr = (p.authors && p.authors.length > 3)
    ? p.authors.slice(0, 3).join(", ") + " et al."
    : (p.authors || []).join(", ");

  const excerptHtml = p.excerpt
    ? '<div class="sci-card-excerpt" title="' + (IS_FR ? "Extrait mentionnant Open Food Facts" : "Excerpt mentioning Open Food Facts") + '">' + p.excerpt + '</div>'
    : '';

  const tags = [];
  if (p.themes) {{
    p.themes.slice(0, 2).forEach(t => {{
      tags.push('<span class="sci-tag sci-tag-theme">' + (THEME_LABELS[t] || t) + '</span>');
    }});
  }}
  if (p.country && COUNTRY_FLAGS[p.country.toLowerCase()]) {{
    tags.push('<span class="sci-tag sci-tag-geo">' + COUNTRY_FLAGS[p.country.toLowerCase()] + '</span>');
  }}

  const links = [];
  if (p.doi) {{
    links.push('<a class="sci-link-btn" href="https://doi.org/' + encodeURIComponent(p.doi) + '" target="_blank" rel="noopener noreferrer" title="DOI Resolver">🔗 DOI</a>');
  }} else if (p.url) {{
    links.push('<a class="sci-link-btn" href="' + p.url + '" target="_blank" rel="noopener noreferrer" title="Publisher Link">🌐 ' + (IS_FR ? "Article" : "Article") + '</a>');
  }}
  if (p.url_pdf) {{
    links.push('<a class="sci-link-btn" href="' + p.url_pdf + '" target="_blank" rel="noopener noreferrer" title="Open PDF">📄 PDF</a>');
  }}

  return '<div class="sci-card" id="pub-' + p.id + '">' +
    '<div>' +
      '<div class="sci-card-header">' +
        yearBadge +
        citBadge +
      '</div>' +
      '<h3 class="sci-card-title"><a href="javascript:void(0)" onclick="openSciModal(\\'' + p.id + '\\')">' + p.title + '</a></h3>' +
      '<div class="sci-card-authors">' + authorsStr + '</div>' +
      (p.journal ? '<div class="sci-card-journal">' + p.journal + (p.volume ? ', ' + p.volume : '') + (p.pages ? ', ' + p.pages : '') + '</div>' : '') +
      excerptHtml +
      '<div class="sci-tags-row">' + tags.join(" ") + '</div>' +
    '</div>' +
    '<div class="sci-card-footer">' +
      '<div class="sci-card-links">' + links.join(" ") + '</div>' +
      '<button type="button" class="sci-details-btn" onclick="openSciModal(\\'' + p.id + '\\')">' + (IS_FR ? "Détails & Citer" : "Details & Cite") + ' &rarr;</button>' +
    '</div>' +
  '</div>';
}}

function renderSciList(list) {{
  currentFilteredList = list;
  displayedCount = Math.min(list.length, PAGE_SIZE);

  const grid = document.getElementById("sciGrid");
  const count = document.getElementById("sciCount");
  const loadMoreWrap = document.getElementById("sciLoadMoreWrap");

  if (!list.length) {{
    grid.innerHTML = '<div style="grid-column: 1 / -1; text-align: center; padding: 3rem; color: #64748b; font-size: 1.1rem;">' +
      (IS_FR ? "Aucune publication ne correspond à vos filtres." : "No publications found matching your criteria.") + '</div>';
    count.textContent = IS_FR ? "0 publication" : "0 publications";
    if (loadMoreWrap) loadMoreWrap.style.display = "none";
    return;
  }}

  grid.innerHTML = list.slice(0, displayedCount).map(renderSciCard).join("");
  updateSciCountAndLoadMore();
}}

function loadMoreSciCards() {{
  if (displayedCount >= currentFilteredList.length) return;
  const nextBatch = currentFilteredList.slice(displayedCount, displayedCount + PAGE_SIZE);
  const grid = document.getElementById("sciGrid");
  const temp = document.createElement("div");
  temp.innerHTML = nextBatch.map(renderSciCard).join("");
  while (temp.firstChild) {{
    grid.appendChild(temp.firstChild);
  }}
  displayedCount += nextBatch.length;
  updateSciCountAndLoadMore();
}}

function showAllSciCards() {{
  if (displayedCount >= currentFilteredList.length) return;
  const remaining = currentFilteredList.slice(displayedCount);
  const grid = document.getElementById("sciGrid");
  const temp = document.createElement("div");
  temp.innerHTML = remaining.map(renderSciCard).join("");
  while (temp.firstChild) {{
    grid.appendChild(temp.firstChild);
  }}
  displayedCount = currentFilteredList.length;
  updateSciCountAndLoadMore();
}}

function updateSciCountAndLoadMore() {{
  const count = document.getElementById("sciCount");
  const loadMoreWrap = document.getElementById("sciLoadMoreWrap");
  const loadMoreBtn = document.getElementById("sciLoadMoreBtn");

  const total = currentFilteredList.length;
  if (displayedCount < total) {{
    count.textContent = IS_FR
      ? "Affichage de " + displayedCount + " sur " + total + " publications (" + PUBLICATIONS_DATA.length + " au total)"
      : "Showing " + displayedCount + " of " + total + " publications (" + PUBLICATIONS_DATA.length + " total)";
    if (loadMoreWrap) loadMoreWrap.style.display = "flex";
    if (loadMoreBtn) {{
      const remaining = total - displayedCount;
      const step = Math.min(PAGE_SIZE, remaining);
      loadMoreBtn.textContent = IS_FR ? "Afficher plus d'articles (+" + step + ")" : "Load More Articles (+" + step + ")";
    }}
  }} else {{
    count.textContent = IS_FR
      ? "Affichage de " + total + " sur " + PUBLICATIONS_DATA.length + " publications"
      : "Showing " + total + " of " + PUBLICATIONS_DATA.length + " publications";
    if (loadMoreWrap) loadMoreWrap.style.display = "none";
  }}
}}

let activePubForModal = null;

function openSciModal(id) {{
  const p = PUBLICATIONS_DATA.find(x => x.id === id);
  if (!p) return;
  activePubForModal = p;

  const modal = document.getElementById("sciModalOverlay");
  document.getElementById("modalTitle").textContent = p.title || "";
  document.getElementById("modalAuthors").textContent = (p.authors || []).join(", ");
  
  let journalInfo = p.journal || "";
  if (p.volume) journalInfo += ", Vol. " + p.volume;
  if (p.pages) journalInfo += ", pp. " + p.pages;
  document.getElementById("modalJournal").textContent = journalInfo;

  document.getElementById("modalYearBadge").textContent = p.year || "";
  
  const citBadge = document.getElementById("modalCitBadge");
  if (p.num_citations) {{
    citBadge.textContent = "⭐ " + p.num_citations + " citations";
    citBadge.style.display = "inline-flex";
  }} else {{
    citBadge.style.display = "none";
  }}

  document.getElementById("modalTypeBadge").textContent = (p.type || "paper").toUpperCase();

  const excerptWrap = document.getElementById("modalExcerptWrap");
  if (p.excerpt) {{
    document.getElementById("modalExcerpt").textContent = p.excerpt;
    excerptWrap.style.display = "block";
  }} else {{
    excerptWrap.style.display = "none";
  }}

  // Links
  const linksGrid = document.getElementById("modalLinksGrid");
  const links = [];
  if (p.doi) {{
    links.push('<a class="button small primary sci-btn" href="https://doi.org/' + encodeURIComponent(p.doi) + '" target="_blank" rel="noopener noreferrer"><span class="material-icons" style="font-size: 15px;">link</span> DOI Link</a>');
  }}
  if (p.url && (!p.doi || p.url.indexOf(p.doi) === -1)) {{
    links.push('<a class="button small secondary sci-btn" href="' + p.url + '" target="_blank" rel="noopener noreferrer"><span class="material-icons" style="font-size: 15px;">language</span> ' + (IS_FR ? "Page de l'article" : "Publisher Article") + '</a>');
  }}
  if (p.url_pdf) {{
    links.push('<a class="button small secondary sci-btn" href="' + p.url_pdf + '" target="_blank" rel="noopener noreferrer"><span class="material-icons" style="font-size: 15px;">picture_as_pdf</span> PDF</a>');
  }}
  linksGrid.innerHTML = links.join(" ");

  // BibTeX & APA
  document.getElementById("modalBibtex").textContent = p.bibtex || "";
  document.getElementById("modalApa").textContent = p.apa || "";

  // Edit Link
  const editLink = document.getElementById("modalEditLink");
  editLink.href = "https://github.com/openfoodfacts/openfoodfacts-web/edit/main/data/scientific_publications/" + p.id + ".yaml";

  // Highlight card
  document.querySelectorAll(".sci-card").forEach(c => c.classList.remove("highlighted"));
  const card = document.getElementById("pub-" + p.id);
  if (card) card.classList.add("highlighted");

  history.replaceState(null, null, "#" + p.id);
  modal.classList.add("open");
}}

function closeSciModal() {{
  const modal = document.getElementById("sciModalOverlay");
  modal.classList.remove("open");
  history.replaceState(null, null, window.location.pathname + window.location.search);
}}

function onSciModalBackdropClick(event) {{
  if (event.target.id === "sciModalOverlay") {{
    closeSciModal();
  }}
}}

function copyBibtex() {{
  if (!activePubForModal) return;
  navigator.clipboard.writeText(activePubForModal.bibtex || "").then(() => {{
    alert(IS_FR ? "Notice BibTeX copiée !" : "BibTeX entry copied to clipboard!");
  }});
}}

function copyApa() {{
  if (!activePubForModal) return;
  navigator.clipboard.writeText(activePubForModal.apa || "").then(() => {{
    alert(IS_FR ? "Citation APA copiée !" : "APA citation copied to clipboard!");
  }});
}}

window.addEventListener("keydown", function(e) {{
  if (e.key === "Escape") {{
    closeSciModal();
  }}
}});

function checkHash() {{
  const hash = window.location.hash.replace(/^#pub-|^#/, "");
  if (hash) {{
    openSciModal(hash);
  }}
}}

// Initialize
applySciFilters();
window.addEventListener("load", checkHash);
window.addEventListener("hashchange", checkHash);
</script>
"""

def main():
    pubs = load_all_publications()
    print(f"Loaded {len(pubs)} scientific publications from {PUBLICATIONS_DIR}")

    # Write aggregate JSON
    with open(OUTPUT_JSON, "w", encoding="utf-8") as f:
        json.dump(pubs, f, ensure_ascii=False, indent=2)
    print(f"Wrote aggregate JSON: {OUTPUT_JSON}")

    # Generate HTML for en and fr
    en_html = generate_html(pubs, "en")
    fr_html = generate_html(pubs, "fr")

    with open("lang/en/texts/scientific-publications.html", "w", encoding="utf-8") as f:
        f.write(en_html)
    print("Wrote lang/en/texts/scientific-publications.html")

    with open("lang/fr/texts/scientific-publications.html", "w", encoding="utf-8") as f:
        f.write(fr_html)
    print("Wrote lang/fr/texts/scientific-publications.html")

if __name__ == "__main__":
    main()
