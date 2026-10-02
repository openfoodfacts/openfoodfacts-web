#!/usr/bin/env python3
"""
generate_press_review.py

Generates the multilingual, fully deeplinkable Press Review pages for Open Food Facts.
Features:
- Full URL deeplinking (filters, search, and direct card permalinks via ?id=... and #press-...)
- Granular filtering by country, topic (nova, nutriscore, green-score, upf, seasonal, data journalism),
  source (France Inter, Le Monde...), media scope (national, regional, public reports, culinary blogs),
  type (article, podcast, video, study), and link accessibility (filtering out dead links)
- Wayback Machine archive fallbacks for inactive links
- Zero leakage of internal editorial notes
- Complete elimination of the 'OFF' acronym in favor of 'Open Food Facts'
- Copyable card permalinks with visual feedback
- Interactive active filter pills
"""

import glob
import json
import os
import re
import yaml

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
PRESS_DIR = os.path.join(REPO_ROOT, "data", "press-review")
MERGED_JSON = os.path.join(REPO_ROOT, "data", "press-review-merged.json")

def load_press_items():
    if os.path.isdir(PRESS_DIR) and os.listdir(PRESS_DIR):
        yaml_files = sorted(glob.glob(os.path.join(PRESS_DIR, "*.yaml")) + glob.glob(os.path.join(PRESS_DIR, "*.yml")))
        items = []
        for yf in yaml_files:
            with open(yf, "r", encoding="utf-8") as f:
                data = yaml.safe_load(f)
                if isinstance(data, dict):
                    items.append(data)
        items.sort(key=lambda x: (str(x.get("date", "2000-01-01")), str(x.get("title", ""))), reverse=True)
        return items
    elif os.path.exists(MERGED_JSON):
        with open(MERGED_JSON, "r", encoding="utf-8") as f:
            return json.load(f)
    return []

merged = load_press_items()
print(f"Loaded {len(merged)} press review items!")

def build_html(lang="fr", items=None):
    is_fr = (lang == "fr")
    if items is None:
        items = merged

    # Clean items: ensure internal editorial notes are never leaked to client JSON
    clean_items = []
    for it in items:
        clean = dict(it)
        clean.pop("editorial_note", None)
        clean_items.append(clean)

    # Translations
    t_title = "📰 Revue de presse Open Food Facts" if is_fr else "📰 Open Food Facts in the Press"
    t_subtitle = "Toutes les mentions dans les médias, radios, télés et publications de 2012 à aujourd'hui." if is_fr else "All press, radio, TV, and media coverage of Open Food Facts from 2012 to today."
    t_submit_btn = "➕ Signaler une mention" if is_fr else "➕ Submit a Press Mention"
    t_assets_btn = "📁 Bibliothèque de logos & assets" if is_fr else "📁 Media Assets Library"
    t_presskit_btn = "← Espace presse" if is_fr else "← Press Page"

    t_drawer_title = "Signaler ou soumettre une mention presse" if is_fr else "Submit a Press Mention"
    t_drawer_desc = "Vous avez découvert ou publié un article, un podcast ou un reportage mentionnant Open Food Facts ? Partagez-le avec nous !" if is_fr else "Found or published an article, podcast, or report mentioning Open Food Facts? Share it with our team!"
    t_lbl_url = "Lien URL de l'article ou de l'émission :" if is_fr else "Article or Show URL:"
    t_lbl_title = "Titre de l'article :" if is_fr else "Article Title:"
    t_lbl_source = "Nom du média (ex: Le Monde, France Inter, BBC) :" if is_fr else "Media Outlet Name (e.g. Le Monde, BBC):"
    t_lbl_date = "Date de publication :" if is_fr else "Publication Date:"
    t_lbl_quote = "Citation ou passage mentionnant Open Food Facts (optionnel) :" if is_fr else "Quote or passage mentioning Open Food Facts (optional):"
    t_btn_gh = "🚀 Ouvrir une issue GitHub (1-clic)" if is_fr else "🚀 Open 1-Click GitHub Issue"
    t_btn_gform = "📝 Formulaire Google" if is_fr else "📝 Google Form"
    t_btn_mail = "✉️ Envoyer par email" if is_fr else "✉️ Send by Email"

    # Chips
    t_chip_all = "Tout" if is_fr else "All"
    t_chip_national = "📰 Presse nationale" if is_fr else "📰 National Press"
    t_chip_regional = "📍 Presse régionale" if is_fr else "📍 Regional Press"
    t_chip_reports = "📑 Rapports publics" if is_fr else "📑 Public Reports"
    t_chip_blogs = "🧑‍🍳 Blogs culinaires" if is_fr else "🧑‍🍳 Food Blogs"
    t_chip_nutriscore = "🏷️ Nutri-Score"
    t_chip_nova_upf = "🏷️ NOVA & UPF"
    t_chip_green = "🏷️ Green-Score"
    t_chip_podcasts = "🎙️ Podcasts & Radio" if is_fr else "🎙️ Podcasts & Radio"
    t_chip_videos = "📺 Vidéos & TV" if is_fr else "📺 Videos & TV"
    t_chip_verbatim = "💬 Avec citations" if is_fr else "💬 With Quotes"

    # Filter labels
    t_search_placeholder = "🔍 Rechercher par titre, média, sujet, auteur, citation..." if is_fr else "🔍 Search by title, outlet, topic, author, quote..."
    t_opt_all_topics = "Tous les sujets" if is_fr else "All Topics"
    t_opt_all_scopes = "Tous les médias" if is_fr else "All Media Scopes"
    t_opt_all_countries = "Tous les pays" if is_fr else "All Countries"
    t_opt_all_sources = "Toutes les sources" if is_fr else "All Outlets"
    t_opt_all_types = "Tous les formats" if is_fr else "All Formats"
    t_opt_all_links = "Tous les liens" if is_fr else "All Links"
    t_opt_links_active = "✅ Liens actifs uniquement" if is_fr else "✅ Active Links Only"
    t_opt_links_dead = "⚠️ Liens archivés / inactifs" if is_fr else "⚠️ Inactive / Archived Links"
    t_opt_all_years = "Toutes les années" if is_fr else "All Years"
    t_sort_newest = "Plus récents d'abord" if is_fr else "Newest First"
    t_sort_oldest = "Plus anciens d'abord" if is_fr else "Oldest First"
    t_sort_outlet = "Média (A-Z)" if is_fr else "Media Outlet (A-Z)"
    t_sort_title = "Titre (A-Z)" if is_fr else "Title (A-Z)"
    t_reset = "Réinitialiser les filtres" if is_fr else "Reset Filters"
    t_load_more = "Afficher plus de mentions" if is_fr else "Load More Mentions"

    # Extract distinct available years
    years = sorted(list(set(int(item["date"][:4]) for item in clean_items if item.get("date") and len(item["date"]) >= 4)), reverse=True)
    year_options = "".join(f'<option value="{y}">{y}</option>' for y in years)

    # Extract distinct sources with count >= 2
    from collections import Counter
    src_counter = Counter(it.get("source") for it in clean_items if it.get("source"))
    top_sources = [s for s, count in src_counter.most_common() if count >= 2]
    source_options = "".join(f'<option value="{s}">{s} ({src_counter[s]})</option>' for s in sorted(top_sources))

    data_json = json.dumps(clean_items, ensure_ascii=False)

    return f"""<style>
.press-review-header {{
  margin: 1.5rem 0 1.25rem;
}}
.press-header-actions {{
  display: flex;
  flex-wrap: wrap;
  gap: 0.65rem;
  justify-content: center;
  align-items: center;
  margin: 1.25rem 0 2rem;
}}
.press-header-btn {{
  display: inline-flex !important;
  align-items: center !important;
  justify-content: center !important;
  gap: 6px !important;
  font-weight: 600 !important;
  margin: 0 !important;
  vertical-align: middle !important;
}}
.press-drawer {{
  display: none;
  background: #f8fafc;
  border: 1px solid #e2e8f0;
  border-radius: 14px;
  padding: 1.5rem;
  max-width: 860px;
  margin: 0 auto 2rem;
  box-shadow: 0 4px 14px rgba(0,0,0,0.06);
  text-align: left;
}}
.press-drawer.open {{
  display: block;
  animation: pressFadeDown 0.25s ease-out;
}}
@keyframes pressFadeDown {{
  from {{ opacity: 0; transform: translateY(-10px); }}
  to {{ opacity: 1; transform: translateY(0); }}
}}
.press-form-grid {{
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1rem;
  margin-top: 1rem;
}}
@media (max-width: 640px) {{
  .press-form-grid {{ grid-template-columns: 1fr; }}
}}
.press-form-group {{
  display: flex;
  flex-direction: column;
  gap: 0.35rem;
}}
.press-form-group.full-width {{
  grid-column: 1 / -1;
}}
.press-form-group label {{
  font-size: 0.85rem;
  font-weight: 700;
  color: #334155;
  margin: 0;
}}
.press-form-group input, .press-form-group textarea {{
  margin: 0 !important;
  padding: 0.45rem 0.75rem !important;
  border-radius: 6px !important;
  border: 1px solid #cbd5e1 !important;
  font-size: 0.9rem !important;
}}
.press-form-actions {{
  display: flex;
  flex-wrap: wrap;
  gap: 0.65rem;
  margin-top: 1.25rem;
  align-items: center;
}}
.press-chips {{
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
  justify-content: center;
  margin: 1.25rem 0;
}}
.press-chip-btn {{
  padding: 0.35rem 0.85rem;
  border-radius: 20px;
  border: 1px solid #cbd5e1;
  background: #ffffff;
  color: #334155;
  font-size: 0.85rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s ease;
  white-space: nowrap;
}}
.press-chip-btn:hover, .press-chip-btn.active {{
  background: #341100;
  color: #ffffff;
  border-color: #341100;
}}
.press-filter-container {{
  background: #f8fafc;
  border-radius: 14px;
  border: 1px solid #e2e8f0;
  padding: 1.25rem;
  margin: 1.25rem 0 1.5rem;
  box-shadow: 0 1px 3px rgba(0,0,0,0.03);
}}
.press-filter-row {{
  display: flex;
  flex-wrap: wrap;
  gap: 0.75rem;
  align-items: center;
  justify-content: center;
  margin-bottom: 0.75rem;
}}
.press-filter-row:last-child {{
  margin-bottom: 0;
}}
.press-search-input {{
  min-width: 280px;
  flex: 2 1 280px;
  margin: 0 !important;
  padding: 0.55rem 0.9rem !important;
  border-radius: 8px !important;
  border: 1px solid #cbd5e1 !important;
  font-size: 0.95rem !important;
}}
.press-filter-group {{
  display: flex;
  align-items: center;
  gap: 0.45rem;
}}
.press-filter-group label {{
  font-weight: 600;
  margin: 0;
  color: #475569;
  font-size: 0.82rem;
  white-space: nowrap;
}}
.press-filter-group select {{
  margin: 0 !important;
  padding: 0.45rem 0.75rem !important;
  border-radius: 8px !important;
  border: 1px solid #cbd5e1 !important;
  background-color: #fff !important;
  font-size: 0.85rem !important;
  cursor: pointer;
}}

/* Active filter pills */
.press-active-pills {{
  display: flex;
  flex-wrap: wrap;
  gap: 0.45rem;
  align-items: center;
  margin: 0.75rem 0 0;
  padding-top: 0.75rem;
  border-top: 1px dashed #cbd5e1;
}}
.press-pill {{
  display: inline-flex;
  align-items: center;
  gap: 5px;
  background: #e2e8f0;
  color: #1e293b;
  padding: 0.2rem 0.6rem;
  border-radius: 14px;
  font-size: 0.78rem;
  font-weight: 600;
}}
.press-pill-remove {{
  background: none;
  border: none;
  cursor: pointer;
  padding: 0;
  font-size: 13px;
  font-weight: bold;
  color: #64748b;
  line-height: 1;
}}
.press-pill-remove:hover {{
  color: #b91c1c;
}}

.press-stats {{
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1.5rem;
  padding: 0 0.5rem;
}}
.press-count {{
  font-size: 0.95rem;
  color: #64748b;
  font-weight: 600;
}}
.press-grid {{
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(330px, 1fr));
  gap: 1.35rem;
  margin-bottom: 2.5rem;
}}
.press-card {{
  border: 1px solid #e2e8f0;
  border-radius: 14px;
  background: #ffffff;
  padding: 1.25rem;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  text-align: left;
  box-shadow: 0 2px 5px rgba(0,0,0,0.03);
  transition: transform 0.2s ease, box-shadow 0.2s ease, border-color 0.2s ease;
  position: relative;
}}
.press-card:hover {{
  transform: translateY(-2px);
  box-shadow: 0 8px 18px rgba(0,0,0,0.08);
  border-color: #cbd5e1;
}}
.press-card.press-card-highlighted {{
  outline: 3px solid #e65100;
  animation: pressCardPulse 2.5s ease;
}}
@keyframes pressCardPulse {{
  0% {{ box-shadow: 0 0 0 0 rgba(230, 81, 0, 0.6); }}
  70% {{ box-shadow: 0 0 0 14px rgba(230, 81, 0, 0); }}
  100% {{ box-shadow: 0 0 0 0 rgba(230, 81, 0, 0); }}
}}
.press-card-header {{
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 0.65rem;
}}
.press-outlet-wrap {{
  display: flex;
  align-items: center;
  gap: 0.55rem;
}}
.press-outlet-logo {{
  width: 26px;
  height: 26px;
  border-radius: 6px;
  object-fit: contain;
  background: #f1f5f9;
  border: 1px solid #e2e8f0;
  padding: 2px;
}}
.press-outlet-name {{
  font-size: 0.92rem;
  font-weight: 700;
  color: #1e293b;
}}
.press-badges-group {{
  display: flex;
  align-items: center;
  gap: 4px;
  flex-wrap: wrap;
}}
.press-type-badge {{
  font-size: 0.72rem;
  font-weight: 700;
  padding: 0.2rem 0.55rem;
  border-radius: 12px;
  background: #f1f5f9;
  color: #475569;
  text-transform: uppercase;
  letter-spacing: 0.3px;
}}
.press-type-badge.type-podcast {{ background: #fdf2f8; color: #9d174d; }}
.press-type-badge.type-video {{ background: #fef2f2; color: #b91c1c; }}
.press-type-badge.type-study {{ background: #eff6ff; color: #1d4ed8; }}
.press-type-badge.type-article {{ background: #f0fdf4; color: #15803d; }}

.press-scope-badge {{
  font-size: 0.7rem;
  font-weight: 600;
  padding: 0.15rem 0.45rem;
  border-radius: 6px;
}}
.press-scope-regional {{ background: #ede9fe; color: #5b21b6; }}
.press-scope-report {{ background: #dbeafe; color: #1e40af; }}
.press-scope-culinary {{ background: #fef3c7; color: #92400e; }}
.press-scope-specialized {{ background: #ccfbf1; color: #115e59; }}

.press-date {{
  font-size: 0.8rem;
  color: #64748b;
  margin-bottom: 0.45rem;
  font-weight: 500;
}}
.press-title {{
  font-size: 1.05rem;
  font-weight: 700;
  line-height: 1.4;
  margin: 0 0 0.5rem;
  color: #0f172a;
}}
.press-title a {{
  color: inherit;
  text-decoration: none;
}}
.press-title a:hover {{
  color: #e65100;
  text-decoration: underline;
}}
.press-meta-sub {{
  font-size: 0.82rem;
  color: #64748b;
  margin-bottom: 0.5rem;
}}
.press-topics-wrap {{
  display: flex;
  flex-wrap: wrap;
  gap: 4px;
  margin: 0.4rem 0 0.6rem;
}}
.press-topic-tag {{
  display: inline-block;
  font-size: 0.72rem;
  font-weight: 600;
  padding: 0.15rem 0.45rem;
  background: #f1f5f9;
  color: #475569;
  border-radius: 4px;
  cursor: pointer;
  transition: all 0.15s ease;
}}
.press-topic-tag:hover {{
  background: #e2e8f0;
  color: #0f172a;
}}
.press-dead-link-box {{
  display: flex;
  align-items: center;
  justify-content: space-between;
  background: #fff1f2;
  border: 1px solid #fecdd3;
  border-radius: 6px;
  padding: 0.35rem 0.6rem;
  font-size: 0.78rem;
  color: #9f1239;
  margin: 0.5rem 0;
}}
.press-archive-link {{
  display: inline-flex;
  align-items: center;
  gap: 3px;
  color: #b91c1c;
  font-weight: 600;
  text-decoration: underline;
}}
.press-verbatim {{
  margin: 0.5rem 0 0.85rem;
  padding: 0.6rem 0.75rem 0.6rem 1.85rem;
  background: #fffbeb;
  border-left: 3px solid #f59e0b;
  border-radius: 6px;
  font-size: 0.85rem;
  color: #78350f;
  line-height: 1.4;
  font-style: italic;
  position: relative;
}}
.press-verbatim::before {{
  content: "“";
  position: absolute;
  left: 6px;
  top: -2px;
  font-size: 1.5rem;
  color: #d97706;
  font-style: normal;
  line-height: 1;
}}
.press-card-footer {{
  margin-top: auto;
  padding-top: 0.75rem;
  display: flex;
  justify-content: space-between;
  align-items: center;
  border-top: 1px solid #f1f5f9;
}}
.press-card-actions-left {{
  display: flex;
  align-items: center;
  gap: 6px;
}}
.press-tag {{
  font-size: 0.7rem;
  padding: 0.15rem 0.45rem;
  background: #f1f5f9;
  color: #475569;
  border-radius: 4px;
}}
.press-share-btn {{
  background: none;
  border: 1px solid #e2e8f0;
  border-radius: 6px;
  padding: 2px 7px;
  font-size: 0.75rem;
  font-weight: 600;
  color: #64748b;
  cursor: pointer;
  display: inline-flex;
  align-items: center;
  gap: 3px;
  transition: all 0.15s ease;
}}
.press-share-btn:hover {{
  background: #f8fafc;
  border-color: #cbd5e1;
  color: #0f172a;
}}
.press-share-btn.copied {{
  background: #dcfce7;
  color: #15803d;
  border-color: #86efac;
}}
.press-edit-link {{
  display: inline-flex;
  align-items: center;
  gap: 3px;
  font-size: 0.75rem;
  color: #94a3b8;
  text-decoration: none;
}}
.press-edit-link:hover {{
  color: #475569;
  text-decoration: underline;
}}
.press-action-link {{
  display: inline-flex;
  align-items: center;
  gap: 4px;
  font-size: 0.85rem;
  font-weight: 600;
  color: #e65100;
  text-decoration: none;
}}
.press-action-link:hover {{
  text-decoration: underline;
}}
.press-action-link .material-icons {{
  font-size: 1rem;
}}
.press-load-more {{
  text-align: center;
  margin: 2rem 0 3rem;
}}
</style>

<div class="press-review-header text-center">
  <h1 class="title-2 emphasized-title">{t_title}</h1>
  <h4 class="subheader">{t_subtitle}</h4>
  
  <div class="press-header-actions">
    <button type="button" class="button round primary small press-header-btn" onclick="toggleSubmitDrawer()">
      <span class="material-icons">add_circle</span> {t_submit_btn}
    </button>
    <a href="/media-assets" class="button round secondary small press-header-btn">
      <span class="material-icons">folder</span> {t_assets_btn}
    </a>
    <a href="/press" class="button round secondary small press-header-btn">
      <span class="material-icons">newspaper</span> {t_presskit_btn}
    </a>
  </div>
</div>

<!-- Submit Mention Drawer -->
<div class="press-drawer" id="pressDrawer">
  <div style="display: flex; justify-content: space-between; align-items: center;">
    <h3 style="margin: 0; font-size: 1.15rem; color: #0f172a;">{t_drawer_title}</h3>
    <button type="button" style="background: none; border: none; font-size: 1.5rem; cursor: pointer; color: #64748b;" onclick="toggleSubmitDrawer()">&times;</button>
  </div>
  <p style="font-size: 0.9rem; color: #475569; margin: 0.4rem 0 1rem;">{t_drawer_desc}</p>
  
  <div class="press-form-grid">
    <div class="press-form-group full-width">
      <label for="subUrl">{t_lbl_url}</label>
      <input type="url" id="subUrl" placeholder="https://www.lemonde.fr/..." oninput="updateSubmitLinks()">
    </div>
    <div class="press-form-group">
      <label for="subTitle">{t_lbl_title}</label>
      <input type="text" id="subTitle" placeholder="Ex: Open Food Facts célèbre ses 10 ans" oninput="updateSubmitLinks()">
    </div>
    <div class="press-form-group">
      <label for="subSource">{t_lbl_source}</label>
      <input type="text" id="subSource" placeholder="Ex: France Inter, BBC, Le Monde..." oninput="updateSubmitLinks()">
    </div>
    <div class="press-form-group">
      <label for="subDate">{t_lbl_date}</label>
      <input type="date" id="subDate" oninput="updateSubmitLinks()">
    </div>
    <div class="press-form-group full-width">
      <label for="subQuote">{t_lbl_quote}</label>
      <textarea id="subQuote" rows="2" placeholder="Extrait de l'article..." oninput="updateSubmitLinks()"></textarea>
    </div>
  </div>
  
  <div class="press-form-actions">
    <a id="btnGhIssue" class="button round small press-header-btn" href="https://github.com/openfoodfacts/openfoodfacts-web/issues/new?template=new-press-review.yml" target="_blank" rel="noopener noreferrer" style="background-color: #24292f !important; color: #fff !important;">
      <span class="material-icons">open_in_new</span> {t_btn_gh}
    </a>
    <a id="btnGoogleForm" class="button round secondary small press-header-btn" href="https://docs.google.com/forms/d/e/1FAIpQLScpzGaRX6Vr7nFHYuApVx5cz2zjU_bKA85qnQpXHsrY0M0KRA/viewform" target="_blank" rel="noopener noreferrer">
      <span class="material-icons">assignment</span> {t_btn_gform}
    </a>
    <a id="btnMailto" class="button round secondary small press-header-btn" href="mailto:presse@openfoodfacts.org">
      <span class="material-icons">email</span> {t_btn_mail}
    </a>
  </div>
</div>

<div class="press-chips">
  <button type="button" class="press-chip-btn active" onclick="selectChip(this, 'all')">{t_chip_all} ({len(clean_items)})</button>
  <button type="button" class="press-chip-btn" onclick="selectChip(this, 'scope:national')">{t_chip_national}</button>
  <button type="button" class="press-chip-btn" onclick="selectChip(this, 'scope:regional')">{t_chip_regional}</button>
  <button type="button" class="press-chip-btn" onclick="selectChip(this, 'scope:report')">{t_chip_reports}</button>
  <button type="button" class="press-chip-btn" onclick="selectChip(this, 'scope:culinary_blog')">{t_chip_blogs}</button>
  <button type="button" class="press-chip-btn" onclick="selectChip(this, 'topic:nutriscore')">{t_chip_nutriscore}</button>
  <button type="button" class="press-chip-btn" onclick="selectChip(this, 'topic:nova')">{t_chip_nova_upf}</button>
  <button type="button" class="press-chip-btn" onclick="selectChip(this, 'topic:green-score')">{t_chip_green}</button>
  <button type="button" class="press-chip-btn" onclick="selectChip(this, 'type:podcast')">{t_chip_podcasts}</button>
  <button type="button" class="press-chip-btn" onclick="selectChip(this, 'type:video')">{t_chip_videos}</button>
  <button type="button" class="press-chip-btn" onclick="selectChip(this, 'chip:verbatim')">{t_chip_verbatim}</button>
</div>

<div class="press-filter-container">
  <div class="press-filter-row">
    <input type="search" id="pressSearch" class="press-search-input" placeholder="{t_search_placeholder}" oninput="onFilterChanged()">

    <div class="press-filter-group">
      <label for="topicSelect">Sujet / Topic:</label>
      <select id="topicSelect" onchange="onFilterChanged()">
        <option value="all">{t_opt_all_topics}</option>
        <option value="nutriscore">🏷️ Nutri-Score</option>
        <option value="nova">🏷️ Classification NOVA</option>
        <option value="upf">🏷️ Aliments ultra-transformés (UPF)</option>
        <option value="green-score">🏷️ Green-Score / Éco-Score</option>
        <option value="seasonal">🏷️ Fruits & Légumes de saison</option>
        <option value="data-journalism">🏷️ Journalisme de données</option>
        <option value="additives">🏷️ Additifs & Ingrédients</option>
        <option value="open-data">🏷️ Open Data & Communs</option>
      </select>
    </div>

    <div class="press-filter-group">
      <label for="countrySelect">Pays / Country:</label>
      <select id="countrySelect" onchange="onFilterChanged()">
        <option value="all">{t_opt_all_countries}</option>
        <option value="fra">🇫🇷 France</option>
        <option value="bel">🇧🇪 Belgique</option>
        <option value="che">🇨🇭 Suisse</option>
        <option value="deu">🇩🇪 Deutschland</option>
        <option value="esp">🇪🇸 España</option>
        <option value="ita">🇮🇹 Italia</option>
        <option value="gbr">🇬🇧 United Kingdom</option>
        <option value="usa">🇺🇸 United States</option>
        <option value="eu">🇪🇺 European Union</option>
        <option value="can">🇨🇦 Canada</option>
        <option value="sen">🇸🇳 Sénégal</option>
      </select>
    </div>

    <div class="press-filter-group">
      <label for="scopeSelect">Média / Granularité:</label>
      <select id="scopeSelect" onchange="onFilterChanged()">
        <option value="all">{t_opt_all_scopes}</option>
        <option value="national">📰 Presse nationale</option>
        <option value="regional">📍 Presse régionale (PQR)</option>
        <option value="report">📑 Rapports publics & Études</option>
        <option value="culinary_blog">🧑‍🍳 Blogs culinaires</option>
        <option value="specialized">🔬 Presse spécialisée & Tech</option>
      </select>
    </div>
  </div>

  <div class="press-filter-row">
    <div class="press-filter-group">
      <label for="sourceSelect">Source:</label>
      <select id="sourceSelect" onchange="onFilterChanged()">
        <option value="all">{t_opt_all_sources}</option>
        {source_options}
      </select>
    </div>

    <div class="press-filter-group">
      <label for="typeSelect">Format:</label>
      <select id="typeSelect" onchange="onFilterChanged()">
        <option value="all">{t_opt_all_types}</option>
        <option value="article">📰 Article / Presse</option>
        <option value="podcast">🎙️ Podcast / Radio</option>
        <option value="video">📺 TV / Vidéo</option>
        <option value="study">📑 Rapport / Étude</option>
      </select>
    </div>

    <div class="press-filter-group">
      <label for="linkSelect">Liens / Links:</label>
      <select id="linkSelect" onchange="onFilterChanged()">
        <option value="all">{t_opt_all_links}</option>
        <option value="active">{t_opt_links_active}</option>
        <option value="dead">{t_opt_links_dead}</option>
      </select>
    </div>

    <div class="press-filter-group">
      <label for="yearSelect">Année / Year:</label>
      <select id="yearSelect" onchange="onFilterChanged()">
        <option value="all">{t_opt_all_years}</option>
        {year_options}
      </select>
    </div>

    <div class="press-filter-group">
      <label for="sortSelect">Tri / Sort:</label>
      <select id="sortSelect" onchange="onFilterChanged()">
        <option value="newest">{t_sort_newest}</option>
        <option value="oldest">{t_sort_oldest}</option>
        <option value="outlet">{t_sort_outlet}</option>
        <option value="title">{t_sort_title}</option>
      </select>
    </div>
  </div>

  <div class="press-active-pills" id="activePillsWrap" style="display: none;"></div>
</div>

<div class="press-stats">
  <div class="press-count" id="pressCount">Showing {len(clean_items)} mentions</div>
  <button type="button" class="button secondary small" onclick="resetFilters()" style="margin: 0;">{t_reset}</button>
</div>

<div class="press-grid" id="pressGrid"></div>

<div class="press-load-more" id="loadMoreWrap">
  <button type="button" id="loadMoreBtn" class="button secondary small" onclick="loadMore()">{t_load_more}</button>
</div>

<script>
const ALL_PRESS = {data_json};
const IS_FR = {'true' if is_fr else 'false'};
const PAGE_SIZE = 24;
let currentPage = 1;
let currentFiltered = [];
let activeChip = "all";

const COUNTRY_FLAGS = {{
  "fra": "🇫🇷",
  "gbr": "🇬🇧",
  "usa": "🇺🇸",
  "che": "🇨🇭",
  "bel": "🇧🇪",
  "deu": "🇩🇪",
  "esp": "🇪🇸",
  "ita": "🇮🇹",
  "can": "🇨🇦",
  "lux": "🇱🇺",
  "nld": "🇳🇱",
  "eu": "🇪🇺",
  "sen": "🇸🇳"
}};

const TOPIC_LABELS = {{
  "nutriscore": "Nutri-Score",
  "nova": "NOVA",
  "upf": "Aliments ultra-transformés",
  "green-score": "Green-Score",
  "seasonal": "Saisonnalité",
  "data-journalism": "Journalisme de données",
  "additives": "Additifs",
  "open-data": "Open Data"
}};

function formatDate(isoStr) {{
  if (!isoStr) return "";
  const parts = isoStr.split("-");
  if (parts.length < 3) return isoStr;
  const yr = parts[0], mo = parseInt(parts[1], 10), da = parseInt(parts[2], 10);
  if (IS_FR) {{
    const months = ["", "janvier", "février", "mars", "avril", "mai", "juin", "juillet", "août", "septembre", "octobre", "novembre", "décembre"];
    return da + " " + months[mo] + " " + yr;
  }} else {{
    const months = ["", "Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"];
    return months[mo] + " " + da + ", " + yr;
  }}
}}

function getTypeBadge(type) {{
  switch(type) {{
    case "podcast": return '<span class="press-type-badge type-podcast">🎙️ ' + (IS_FR ? "Podcast / Radio" : "Podcast / Radio") + '</span>';
    case "video": return '<span class="press-type-badge type-video">📺 ' + (IS_FR ? "TV / Vidéo" : "Video / TV") + '</span>';
    case "study": return '<span class="press-type-badge type-study">📑 ' + (IS_FR ? "Rapport / Étude" : "Study / Report") + '</span>';
    default: return '<span class="press-type-badge type-article">📰 ' + (IS_FR ? "Article" : "Article") + '</span>';
  }}
}}

function getScopeBadge(scope) {{
  if (!scope || scope === "national") return "";
  switch(scope) {{
    case "regional": return '<span class="press-scope-badge press-scope-regional">📍 ' + (IS_FR ? "Presse régionale" : "Regional Media") + '</span>';
    case "report": return '<span class="press-scope-badge press-scope-report">📑 ' + (IS_FR ? "Rapport public" : "Public Report") + '</span>';
    case "culinary_blog": return '<span class="press-scope-badge press-scope-culinary">🧑‍🍳 ' + (IS_FR ? "Blog culinaire" : "Food Blog") + '</span>';
    case "specialized": return '<span class="press-scope-badge press-scope-specialized">🔬 ' + (IS_FR ? "Presse spécialisée" : "Specialized Press") + '</span>';
    default: return "";
  }}
}}

function renderCard(item) {{
  const flag = COUNTRY_FLAGS[item.country] || "";
  const faviconUrl = item.domain ? "https://www.google.com/s2/favicons?domain=" + encodeURIComponent(item.domain) + "&sz=128" : "";
  const logoImg = faviconUrl ? '<img class="press-outlet-logo" src="' + faviconUrl + '" alt="" loading="lazy" onerror="this.style.display=\\'none\\';">' : '<span class="material-icons" style="font-size: 20px; color: #94a3b8;">newspaper</span>';
  const dateFormatted = formatDate(item.date);
  
  const isDead = !!item.dead_link;
  const linkAttr = (item.link && !isDead) ? ' href="' + item.link + '" target="_blank" rel="noopener noreferrer"' : '';
  const titleHtml = linkAttr ? '<a' + linkAttr + '>' + item.title + '</a>' : item.title;
  
  let verbatimHtml = "";
  if (item.verbatim) {{
    verbatimHtml = '<div class="press-verbatim">' + item.verbatim + '</div>';
  }}
  
  let authorHtml = "";
  if (item.author) {{
    authorHtml = '<div class="press-meta-sub">✍️ ' + item.author + '</div>';
  }}

  let deadLinkHtml = "";
  if (isDead) {{
    const archiveUrl = "https://web.archive.org/web/*/" + (item.link || "");
    deadLinkHtml = '<div class="press-dead-link-box">' +
      '<span>⚠️ ' + (IS_FR ? "Lien d'origine inactif" : "Original link inactive") + '</span>' +
      (item.link ? '<a class="press-archive-link" href="' + archiveUrl + '" target="_blank" rel="noopener noreferrer" title="' + (IS_FR ? "Consulter sur Archive.org" : "View on Archive.org") + '">🏛️ Archive.org</a>' : '') +
    '</div>';
  }}

  let topicsHtml = "";
  if (item.topics && item.topics.length) {{
    topicsHtml = '<div class="press-topics-wrap">' +
      item.topics.map(t => '<span class="press-topic-tag" onclick="setTopicFilter(\\'' + t + '\\')" title="' + (IS_FR ? "Filtrer par ce sujet" : "Filter by this topic") + '">#' + (TOPIC_LABELS[t] || t) + '</span>').join("") +
    '</div>';
  }}

  let actionBtn = "";
  if (item.link) {{
    let actionLabel = IS_FR ? "Consulter l'article" : "Read Article";
    if (item.type === "podcast") actionLabel = IS_FR ? "Écouter l'émission" : "Listen";
    else if (item.type === "video") actionLabel = IS_FR ? "Voir la vidéo" : "Watch";
    else if (item.type === "study") actionLabel = IS_FR ? "Consulter l'étude" : "Read Report";
    
    if (isDead) {{
      const archiveUrl = "https://web.archive.org/web/*/" + item.link;
      actionBtn = '<a class="press-action-link" href="' + archiveUrl + '" target="_blank" rel="noopener noreferrer">' + (IS_FR ? "Consulter l'archive" : "View Archive") + ' <span class="material-icons">open_in_new</span></a>';
    }} else {{
      actionBtn = '<a class="press-action-link"' + linkAttr + '>' + actionLabel + ' <span class="material-icons">arrow_forward</span></a>';
    }}
  }}

  const scopeBadge = getScopeBadge(item.media_scope);

  return '<div class="press-card" id="press-' + (item.id || '') + '">' +
    '<div>' +
      '<div class="press-card-header">' +
        '<div class="press-outlet-wrap">' +
          logoImg +
          '<span class="press-outlet-name">' + (item.source || item.domain || "Média") + ' ' + flag + '</span>' +
        '</div>' +
        '<div class="press-badges-group">' +
          scopeBadge +
          getTypeBadge(item.type) +
        '</div>' +
      '</div>' +
      (dateFormatted ? '<div class="press-date">' + dateFormatted + '</div>' : '') +
      '<h3 class="press-title">' + titleHtml + '</h3>' +
      authorHtml +
      deadLinkHtml +
      topicsHtml +
      verbatimHtml +
    '</div>' +
    '<div class="press-card-footer">' +
      '<div class="press-card-actions-left">' +
        '<span class="press-tag">' + (item.lang ? item.lang.toUpperCase() : "FR") + '</span>' +
        '<button type="button" class="press-share-btn" onclick="copyCardPermalink(\\'' + (item.id || '') + '\\', this)" title="' + (IS_FR ? "Copier le permalien vers cette mention" : "Copy permalink to this mention") + '"><span class="material-icons" style="font-size: 13px;">share</span> ' + (IS_FR ? "Partager" : "Share") + '</button>' +
        '<a class="press-edit-link" href="https://github.com/openfoodfacts/openfoodfacts-web/edit/main/data/press-review/' + (item.id || '') + '.yaml" target="_blank" rel="noopener noreferrer" title="' + (IS_FR ? "Modifier cette mention sur GitHub" : "Edit on GitHub") + '"><span class="material-icons" style="font-size: 13px; vertical-align: middle;">edit</span> ' + (IS_FR ? "Modifier" : "Edit") + '</a>' +
      '</div>' +
      actionBtn +
    '</div>' +
  '</div>';
}}

function renderList() {{
  const grid = document.getElementById("pressGrid");
  const countSpan = document.getElementById("pressCount");
  const loadMoreBtn = document.getElementById("loadMoreBtn");
  
  const toShow = currentFiltered.slice(0, currentPage * PAGE_SIZE);
  
  if (!toShow.length) {{
    grid.innerHTML = '<div style="grid-column: 1 / -1; text-align: center; padding: 3rem; color: #64748b; font-size: 1.1rem;">' + (IS_FR ? "Aucune mention trouvée correspondant à vos critères." : "No press mentions found matching your criteria.") + '</div>';
    loadMoreBtn.style.display = "none";
    countSpan.textContent = IS_FR ? "0 mention" : "0 mentions";
    return;
  }}
  
  grid.innerHTML = toShow.map(renderCard).join("");
  
  const remaining = currentFiltered.length - toShow.length;
  if (remaining > 0) {{
    loadMoreBtn.style.display = "inline-block";
    loadMoreBtn.textContent = (IS_FR ? "Afficher plus de mentions (" + remaining + " restantes)" : "Load More Mentions (" + remaining + " remaining)");
  }} else {{
    loadMoreBtn.style.display = "none";
  }}
  
  countSpan.textContent = (IS_FR ? "Affichage de " + toShow.length + " sur " + currentFiltered.length + " mentions" : "Showing " + toShow.length + " of " + currentFiltered.length + " mentions");
  updateActivePills();
}}

function loadMore() {{
  currentPage++;
  renderList();
}}

function selectChip(btn, chipVal) {{
  document.querySelectorAll(".press-chip-btn").forEach(b => b.classList.remove("active"));
  btn.classList.add("active");
  activeChip = chipVal;

  if (chipVal === "all") {{
    resetDropdowns();
  }} else if (chipVal.startsWith("scope:")) {{
    document.getElementById("scopeSelect").value = chipVal.split(":")[1];
  }} else if (chipVal.startsWith("topic:")) {{
    document.getElementById("topicSelect").value = chipVal.split(":")[1];
  }} else if (chipVal.startsWith("type:")) {{
    document.getElementById("typeSelect").value = chipVal.split(":")[1];
  }}

  onFilterChanged();
}}

function setTopicFilter(t) {{
  document.getElementById("topicSelect").value = t;
  onFilterChanged();
}}

function resetDropdowns() {{
  document.getElementById("scopeSelect").value = "all";
  document.getElementById("topicSelect").value = "all";
  document.getElementById("typeSelect").value = "all";
}}

function onFilterChanged() {{
  applyFilters();
  syncUrlParams();
}}

function applyFilters() {{
  const q = document.getElementById("pressSearch").value.toLowerCase().trim();
  const topicVal = document.getElementById("topicSelect").value;
  const countryVal = document.getElementById("countrySelect").value;
  const scopeVal = document.getElementById("scopeSelect").value;
  const sourceVal = document.getElementById("sourceSelect").value;
  const typeVal = document.getElementById("typeSelect").value;
  const linkVal = document.getElementById("linkSelect").value;
  const yearVal = document.getElementById("yearSelect").value;
  const sortVal = document.getElementById("sortSelect").value;
  
  currentFiltered = ALL_PRESS.filter(item => {{
    if (activeChip === "chip:verbatim" && !item.verbatim) return false;
    if (topicVal !== "all") {{
      const topics = item.topics || [];
      if (!topics.includes(topicVal)) return false;
    }}
    if (countryVal !== "all" && item.country !== countryVal) return false;
    if (scopeVal !== "all" && item.media_scope !== scopeVal) return false;
    if (sourceVal !== "all" && item.source !== sourceVal) return false;
    if (typeVal !== "all" && item.type !== typeVal) return false;
    if (linkVal === "active" && item.dead_link) return false;
    if (linkVal === "dead" && !item.dead_link) return false;
    if (yearVal !== "all" && !item.date.startsWith(yearVal)) return false;
    
    if (q) {{
      const topicsStr = (item.topics || []).join(" ");
      const text = (item.title + " " + item.source + " " + item.author + " " + item.verbatim + " " + item.topic + " " + topicsStr + " " + item.domain).toLowerCase();
      if (!text.includes(q)) return false;
    }}
    return true;
  }});
  
  if (sortVal === "newest") {{
    currentFiltered.sort((a, b) => b.date.localeCompare(a.date));
  }} else if (sortVal === "oldest") {{
    currentFiltered.sort((a, b) => a.date.localeCompare(b.date));
  }} else if (sortVal === "outlet") {{
    currentFiltered.sort((a, b) => (a.source || "").localeCompare(b.source || ""));
  }} else if (sortVal === "title") {{
    currentFiltered.sort((a, b) => a.title.localeCompare(b.title));
  }}
  
  currentPage = 1;
  renderList();
}}

function syncUrlParams() {{
  const params = new URLSearchParams();
  const q = document.getElementById("pressSearch").value.trim();
  const topicVal = document.getElementById("topicSelect").value;
  const countryVal = document.getElementById("countrySelect").value;
  const scopeVal = document.getElementById("scopeSelect").value;
  const sourceVal = document.getElementById("sourceSelect").value;
  const typeVal = document.getElementById("typeSelect").value;
  const linkVal = document.getElementById("linkSelect").value;
  const yearVal = document.getElementById("yearSelect").value;
  const sortVal = document.getElementById("sortSelect").value;

  if (q) params.set("search", q);
  if (topicVal !== "all") params.set("topic", topicVal);
  if (countryVal !== "all") params.set("country", countryVal);
  if (scopeVal !== "all") params.set("scope", scopeVal);
  if (sourceVal !== "all") params.set("source", sourceVal);
  if (typeVal !== "all") params.set("type", typeVal);
  if (linkVal !== "all") params.set("dead_links", linkVal);
  if (yearVal !== "all") params.set("year", yearVal);
  if (sortVal !== "newest") params.set("sort", sortVal);

  const queryString = params.toString();
  const newUrl = window.location.pathname + (queryString ? "?" + queryString : "") + window.location.hash;
  window.history.replaceState(null, "", newUrl);
}}

function updateActivePills() {{
  const wrap = document.getElementById("activePillsWrap");
  const pills = [];

  const q = document.getElementById("pressSearch").value.trim();
  const topicVal = document.getElementById("topicSelect").value;
  const countryVal = document.getElementById("countrySelect").value;
  const scopeVal = document.getElementById("scopeSelect").value;
  const sourceVal = document.getElementById("sourceSelect").value;
  const typeVal = document.getElementById("typeSelect").value;
  const linkVal = document.getElementById("linkSelect").value;
  const yearVal = document.getElementById("yearSelect").value;

  if (q) pills.push('Recherche: "' + q + '" <button class="press-pill-remove" onclick="clearSpecificFilter(\\'q\\')">&times;</button>');
  if (topicVal !== "all") pills.push('Sujet: ' + (TOPIC_LABELS[topicVal] || topicVal) + ' <button class="press-pill-remove" onclick="clearSpecificFilter(\\'topic\\')">&times;</button>');
  if (countryVal !== "all") pills.push('Pays: ' + (COUNTRY_FLAGS[countryVal] || countryVal.toUpperCase()) + ' <button class="press-pill-remove" onclick="clearSpecificFilter(\\'country\\')">&times;</button>');
  if (scopeVal !== "all") pills.push('Média: ' + scopeVal + ' <button class="press-pill-remove" onclick="clearSpecificFilter(\\'scope\\')">&times;</button>');
  if (sourceVal !== "all") pills.push('Source: ' + sourceVal + ' <button class="press-pill-remove" onclick="clearSpecificFilter(\\'source\\')">&times;</button>');
  if (typeVal !== "all") pills.push('Type: ' + typeVal + ' <button class="press-pill-remove" onclick="clearSpecificFilter(\\'type\\')">&times;</button>');
  if (linkVal !== "all") pills.push('Liens: ' + (linkVal === "active" ? "Actifs" : "Archivés") + ' <button class="press-pill-remove" onclick="clearSpecificFilter(\\'link\\')">&times;</button>');
  if (yearVal !== "all") pills.push('Année: ' + yearVal + ' <button class="press-pill-remove" onclick="clearSpecificFilter(\\'year\\')">&times;</button>');

  if (pills.length) {{
    wrap.style.display = "flex";
    wrap.innerHTML = '<span style="font-size: 0.8rem; font-weight: 600; color: #64748b;">Filtres actifs :</span> ' +
      pills.map(p => '<span class="press-pill">' + p + '</span>').join("") +
      '<button type="button" class="button secondary small" onclick="resetFilters()" style="margin: 0 0 0 auto; padding: 2px 8px; font-size: 0.75rem;">' + (IS_FR ? "Tout effacer" : "Clear all") + '</button>';
  }} else {{
    wrap.style.display = "none";
    wrap.innerHTML = "";
  }}
}}

function clearSpecificFilter(key) {{
  switch(key) {{
    case "q": document.getElementById("pressSearch").value = ""; break;
    case "topic": document.getElementById("topicSelect").value = "all"; break;
    case "country": document.getElementById("countrySelect").value = "all"; break;
    case "scope": document.getElementById("scopeSelect").value = "all"; break;
    case "source": document.getElementById("sourceSelect").value = "all"; break;
    case "type": document.getElementById("typeSelect").value = "all"; break;
    case "link": document.getElementById("linkSelect").value = "all"; break;
    case "year": document.getElementById("yearSelect").value = "all"; break;
  }}
  onFilterChanged();
}}

function resetFilters() {{
  document.getElementById("pressSearch").value = "";
  document.getElementById("topicSelect").value = "all";
  document.getElementById("countrySelect").value = "all";
  document.getElementById("scopeSelect").value = "all";
  document.getElementById("sourceSelect").value = "all";
  document.getElementById("typeSelect").value = "all";
  document.getElementById("linkSelect").value = "all";
  document.getElementById("yearSelect").value = "all";
  document.getElementById("sortSelect").value = "newest";
  activeChip = "all";
  document.querySelectorAll(".press-chip-btn").forEach(b => {{
    if (b.getAttribute("onclick") && b.getAttribute("onclick").includes("'all'")) b.classList.add("active");
    else b.classList.remove("active");
  }});
  onFilterChanged();
}}

function copyCardPermalink(id, btn) {{
  const url = new URL(window.location.href);
  url.searchParams.set("id", id);
  url.hash = "press-" + id;
  navigator.clipboard.writeText(url.toString()).then(() => {{
    const origHtml = btn.innerHTML;
    btn.innerHTML = '<span class="material-icons" style="font-size: 13px;">check</span> ' + (IS_FR ? "Copié !" : "Copied!");
    btn.classList.add("copied");
    setTimeout(() => {{
      btn.innerHTML = origHtml;
      btn.classList.remove("copied");
    }}, 2000);
  }}).catch(() => {{
    prompt(IS_FR ? "Copiez ce lien :" : "Copy this link:", url.toString());
  }});
}}

function checkInitialDeeplink() {{
  const params = new URLSearchParams(window.location.search);
  const q = params.get("search") || params.get("q");
  const topic = params.get("topic");
  const country = params.get("country");
  const scope = params.get("scope");
  const source = params.get("source");
  const type = params.get("type");
  const deadLinks = params.get("dead_links");
  const year = params.get("year");
  const sort = params.get("sort");
  const targetId = params.get("id") || (window.location.hash ? window.location.hash.replace("#press-", "").replace("#", "") : null);

  if (q) document.getElementById("pressSearch").value = q;
  if (topic && document.querySelector('#topicSelect option[value="' + topic + '"]')) document.getElementById("topicSelect").value = topic;
  if (country && document.querySelector('#countrySelect option[value="' + country + '"]')) document.getElementById("countrySelect").value = country;
  if (scope && document.querySelector('#scopeSelect option[value="' + scope + '"]')) document.getElementById("scopeSelect").value = scope;
  if (source && document.querySelector('#sourceSelect option[value="' + source + '"]')) document.getElementById("sourceSelect").value = source;
  if (type && document.querySelector('#typeSelect option[value="' + type + '"]')) document.getElementById("typeSelect").value = type;
  if (deadLinks && document.querySelector('#linkSelect option[value="' + deadLinks + '"]')) document.getElementById("linkSelect").value = deadLinks;
  if (year && document.querySelector('#yearSelect option[value="' + year + '"]')) document.getElementById("yearSelect").value = year;
  if (sort && document.querySelector('#sortSelect option[value="' + sort + '"]')) document.getElementById("sortSelect").value = sort;

  applyFilters();

  if (targetId) {{
    // Locate target in ALL_PRESS
    const itemIndex = ALL_PRESS.findIndex(it => it.id === targetId);
    if (itemIndex >= 0) {{
      // Ensure target is in currentFiltered
      if (!currentFiltered.some(it => it.id === targetId)) {{
        // Reset filters if item was hidden
        resetFilters();
      }}
      const filteredIndex = currentFiltered.findIndex(it => it.id === targetId);
      if (filteredIndex >= 0) {{
        currentPage = Math.ceil((filteredIndex + 1) / PAGE_SIZE);
        renderList();
        setTimeout(() => {{
          const el = document.getElementById("press-" + targetId);
          if (el) {{
            el.scrollIntoView({{ behavior: "smooth", block: "center" }});
            el.classList.add("press-card-highlighted");
          }}
        }}, 200);
      }}
    }}
  }}
}}

function toggleSubmitDrawer() {{
  const d = document.getElementById("pressDrawer");
  d.classList.toggle("open");
  if (d.classList.contains("open")) {{
    d.scrollIntoView({{ behavior: "smooth", block: "start" }});
    updateSubmitLinks();
  }}
}}

function updateSubmitLinks() {{
  const url = document.getElementById("subUrl").value.trim();
  const title = document.getElementById("subTitle").value.trim();
  const source = document.getElementById("subSource").value.trim();
  const date = document.getElementById("subDate").value.trim();
  const quote = document.getElementById("subQuote").value.trim();
  
  const issueTitle = "[Revue de presse] " + (source ? source + ": " : "") + (title || (IS_FR ? "Nouvelle mention médiatique" : "New press mention"));
  const issueBody = "### " + (IS_FR ? "Nouvelle mention dans les médias" : "New Press / Media Mention") + "\\n\\n" +
    "- **" + (IS_FR ? "Titre" : "Title") + " :** " + (title || "N/A") + "\\n" +
    "- **" + (IS_FR ? "Média / Source" : "Outlet") + " :** " + (source || "N/A") + "\\n" +
    "- **" + (IS_FR ? "Lien / URL" : "URL") + " :** " + (url || "N/A") + "\\n" +
    "- **" + (IS_FR ? "Date" : "Date") + " :** " + (date || "N/A") + "\\n" +
    "- **" + (IS_FR ? "Citation / Verbatim" : "Quote") + " :**\\n> " + (quote || "N/A") + "\\n\\n" +
    "---\\n*" + (IS_FR ? "Soumis via la page Revue de Presse" : "Submitted via Press Review page") + "*";
  
  const ghBtn = document.getElementById("btnGhIssue");
  const params = new URLSearchParams();
  params.set("template", "new-press-review.yml");
  if (title) params.set("title", "[Press]: " + (source ? source + " - " : "") + title);
  if (source) params.set("source", source);
  if (date) params.set("date", date);
  if (url) params.set("link", url);
  if (quote) params.set("verbatim", quote);
  ghBtn.href = "https://github.com/openfoodfacts/openfoodfacts-web/issues/new?" + params.toString();
  
  const mailBtn = document.getElementById("btnMailto");
  mailBtn.href = "mailto:presse@openfoodfacts.org?subject=" + encodeURIComponent(issueTitle) + "&body=" + encodeURIComponent(issueBody.replace(/\\n/g, "\\r\\n"));
}}

document.addEventListener("DOMContentLoaded", () => {{
  checkInitialDeeplink();
  updateSubmitLinks();
}});
if (document.readyState !== "loading") {{
  checkInitialDeeplink();
  updateSubmitLinks();
}}
</script>
"""

def main(items=None):
    global merged
    if items is not None:
        merged = items

    # Write French version
    fr_html = build_html("fr", items=merged)
    with open("lang/fr/texts/revue-de-presse-fr.html", "w", encoding="utf-8") as f:
        f.write(fr_html.strip() + "\n")
    print("Wrote lang/fr/texts/revue-de-presse-fr.html")

    # Write English version (both as revue-de-presse-fr.html for direct access and press-review.html)
    en_html = build_html("en", items=merged)
    with open("lang/en/texts/revue-de-presse-fr.html", "w", encoding="utf-8") as f:
        f.write(en_html.strip() + "\n")
    print("Wrote lang/en/texts/revue-de-presse-fr.html")

    with open("lang/en/texts/press-review.html", "w", encoding="utf-8") as f:
        f.write(en_html.strip() + "\n")
    print("Wrote lang/en/texts/press-review.html")

if __name__ == "__main__":
    main()
