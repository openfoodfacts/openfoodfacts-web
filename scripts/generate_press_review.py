#!/usr/bin/env python3
import glob, json, os, re
from urllib.parse import urlparse
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

# Generate HTML Template function
def build_html(lang="fr", items=None):
    is_fr = (lang == "fr")
    if items is None:
        items = merged
    
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
    
    t_chip_all = "Tout" if is_fr else "All Mentions"
    t_chip_articles = "📰 Articles & Presse" if is_fr else "📰 Articles & Press"
    t_chip_podcasts = "🎙️ Podcasts & Radio" if is_fr else "🎙️ Podcasts & Radio"
    t_chip_videos = "📺 Vidéos & TV" if is_fr else "📺 Videos & TV"
    t_chip_studies = "📑 Rapports & Études" if is_fr else "📑 Reports & Studies"
    t_chip_verbatim = "💬 Avec citations" if is_fr else "💬 With Quotes"
    
    t_search_placeholder = "🔍 Rechercher par titre, média, mot-clé, auteur, citation..." if is_fr else "🔍 Search by title, media outlet, author, topic, quote..."
    t_opt_all_types = "Tous les types" if is_fr else "All Types"
    t_opt_all_langs = "Toutes les langues" if is_fr else "All Languages"
    t_opt_all_years = "Toutes les années" if is_fr else "All Years"
    t_sort_newest = "Plus récents d'abord" if is_fr else "Newest First"
    t_sort_oldest = "Plus anciens d'abord" if is_fr else "Oldest First"
    t_sort_outlet = "Média (A-Z)" if is_fr else "Media Outlet (A-Z)"
    t_sort_title = "Titre (A-Z)" if is_fr else "Title (A-Z)"
    t_reset = "Réinitialiser" if is_fr else "Reset Filters"
    t_load_more = "Afficher plus de mentions" if is_fr else "Load More Mentions"
    t_read_btn = "Consulter la source" if is_fr else "View Source"

    # Collect available years
    years = sorted(list(set(int(item["date"][:4]) for item in items if item.get("date") and len(item["date"]) >= 4)), reverse=True)
    year_options = "".join(f'<option value="{y}">{y}</option>' for y in years)

    data_json = json.dumps(items, ensure_ascii=False)

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
  margin: 1.5rem 0;
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
}}
.press-chip-btn:hover, .press-chip-btn.active {{
  background: #341100;
  color: #ffffff;
  border-color: #341100;
}}
.press-filter-bar {{
  display: flex;
  flex-wrap: wrap;
  gap: 0.85rem;
  align-items: center;
  justify-content: center;
  margin: 1.5rem 0 1.5rem;
  padding: 1.15rem;
  background: #f8fafc;
  border-radius: 14px;
  border: 1px solid #e2e8f0;
}}
.press-search-input {{
  min-width: 250px;
  flex: 1 1 250px;
  margin: 0 !important;
  padding: 0.5rem 0.9rem !important;
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
  color: #334155;
  font-size: 0.88rem;
  white-space: nowrap;
}}
.press-filter-group select {{
  margin: 0 !important;
  padding: 0.45rem 0.75rem !important;
  border-radius: 8px !important;
  border: 1px solid #cbd5e1 !important;
  background-color: #fff !important;
  font-size: 0.88rem !important;
  cursor: pointer;
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
  grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
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
  transition: transform 0.2s ease, box-shadow 0.2s ease;
  position: relative;
}}
.press-card:hover {{
  transform: translateY(-2px);
  box-shadow: 0 8px 18px rgba(0,0,0,0.08);
  border-color: #cbd5e1;
}}
.press-card-header {{
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 0.75rem;
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
  margin-bottom: 0.65rem;
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
.press-tag-list {{
  display: flex;
  gap: 0.35rem;
}}
.press-tag {{
  font-size: 0.7rem;
  padding: 0.15rem 0.45rem;
  background: #f1f5f9;
  color: #475569;
  border-radius: 4px;
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
    <a id="btnGhIssue" class="button round small press-header-btn" href="#" target="_blank" rel="noopener noreferrer" style="background-color: #24292f !important; color: #fff !important;">
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
  <button type="button" class="press-chip-btn active" onclick="selectChip(this, 'all')">{t_chip_all} ({len(merged)})</button>
  <button type="button" class="press-chip-btn" onclick="selectChip(this, 'article')">{t_chip_articles}</button>
  <button type="button" class="press-chip-btn" onclick="selectChip(this, 'podcast')">{t_chip_podcasts}</button>
  <button type="button" class="press-chip-btn" onclick="selectChip(this, 'video')">{t_chip_videos}</button>
  <button type="button" class="press-chip-btn" onclick="selectChip(this, 'study')">{t_chip_studies}</button>
  <button type="button" class="press-chip-btn" onclick="selectChip(this, 'verbatim')">{t_chip_verbatim}</button>
</div>

<div class="press-filter-bar">
  <input type="search" id="pressSearch" class="press-search-input" placeholder="{t_search_placeholder}" oninput="applyFilters()">
  
  <div class="press-filter-group">
    <label for="typeSelect">Type:</label>
    <select id="typeSelect" onchange="applyFilters()">
      <option value="all">{t_opt_all_types}</option>
      <option value="article">📰 Article / Presse</option>
      <option value="podcast">🎙️ Podcast / Radio</option>
      <option value="video">📺 TV / Vidéo</option>
      <option value="study">📑 Rapport / Étude</option>
    </select>
  </div>

  <div class="press-filter-group">
    <label for="langSelect">Lang:</label>
    <select id="langSelect" onchange="applyFilters()">
      <option value="all">{t_opt_all_langs}</option>
      <option value="fr">🇫🇷 Français</option>
      <option value="en">🇬🇧 English</option>
      <option value="de">🇩🇪 Deutsch</option>
      <option value="es">🇪🇸 Español</option>
      <option value="it">🇮🇹 Italiano</option>
    </select>
  </div>

  <div class="press-filter-group">
    <label for="yearSelect">Year:</label>
    <select id="yearSelect" onchange="applyFilters()">
      <option value="all">{t_opt_all_years}</option>
      {year_options}
    </select>
  </div>

  <div class="press-filter-group">
    <label for="sortSelect">Sort:</label>
    <select id="sortSelect" onchange="applyFilters()">
      <option value="newest">{t_sort_newest}</option>
      <option value="oldest">{t_sort_oldest}</option>
      <option value="outlet">{t_sort_outlet}</option>
      <option value="title">{t_sort_title}</option>
    </select>
  </div>
</div>

<div class="press-stats">
  <div class="press-count" id="pressCount">Showing {len(merged)} mentions</div>
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
  "nld": "🇳🇱"
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

function renderCard(item) {{
  const flag = COUNTRY_FLAGS[item.country] || "";
  const faviconUrl = item.domain ? "https://www.google.com/s2/favicons?domain=" + encodeURIComponent(item.domain) + "&sz=128" : "";
  const logoImg = faviconUrl ? '<img class="press-outlet-logo" src="' + faviconUrl + '" alt="" loading="lazy" onerror="this.style.display=\\'none\\';">' : '<span class="material-icons" style="font-size: 20px; color: #94a3b8;">newspaper</span>';
  const dateFormatted = formatDate(item.date);
  
  const linkAttr = item.link ? ' href="' + item.link + '" target="_blank" rel="noopener noreferrer"' : '';
  const titleHtml = item.link ? '<a' + linkAttr + '>' + item.title + '</a>' : item.title;
  
  let verbatimHtml = "";
  if (item.verbatim) {{
    verbatimHtml = '<div class="press-verbatim">' + item.verbatim + '</div>';
  }}
  
  let authorHtml = "";
  if (item.author) {{
    authorHtml = '<div class="press-meta-sub">✍️ ' + item.author + '</div>';
  }}

  let actionBtn = "";
  if (item.link) {{
    let actionLabel = IS_FR ? "Consulter l'article" : "Read Article";
    if (item.type === "podcast") actionLabel = IS_FR ? "Écouter l'émission" : "Listen";
    else if (item.type === "video") actionLabel = IS_FR ? "Voir la vidéo" : "Watch";
    else if (item.type === "study") actionLabel = IS_FR ? "Consulter l'étude" : "Read Report";
    
    actionBtn = '<a class="press-action-link"' + linkAttr + '>' + actionLabel + ' <span class="material-icons">arrow_forward</span></a>';
  }}

  return '<div class="press-card">' +
    '<div>' +
      '<div class="press-card-header">' +
        '<div class="press-outlet-wrap">' +
          logoImg +
          '<span class="press-outlet-name">' + (item.source || item.domain || "Média") + ' ' + flag + '</span>' +
        '</div>' +
        getTypeBadge(item.type) +
      '</div>' +
      (dateFormatted ? '<div class="press-date">' + dateFormatted + '</div>' : '') +
      '<h3 class="press-title">' + titleHtml + '</h3>' +
      authorHtml +
      verbatimHtml +
    '</div>' +
    '<div class="press-card-footer">' +
      '<span class="press-tag">' + (item.lang ? item.lang.toUpperCase() : "FR") + '</span>' +
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
}}

function loadMore() {{
  currentPage++;
  renderList();
}}

let activeChip = "all";

function selectChip(btn, chipVal) {{
  document.querySelectorAll(".press-chip-btn").forEach(b => b.classList.remove("active"));
  btn.classList.add("active");
  activeChip = chipVal;
  
  if (chipVal === "article" || chipVal === "podcast" || chipVal === "video" || chipVal === "study") {{
    document.getElementById("typeSelect").value = chipVal;
  }} else if (chipVal === "all") {{
    document.getElementById("typeSelect").value = "all";
  }}
  
  applyFilters();
}}

function applyFilters() {{
  const q = document.getElementById("pressSearch").value.toLowerCase().trim();
  const typeVal = document.getElementById("typeSelect").value;
  const langVal = document.getElementById("langSelect").value;
  const yearVal = document.getElementById("yearSelect").value;
  const sortVal = document.getElementById("sortSelect").value;
  
  currentFiltered = ALL_PRESS.filter(item => {{
    if (activeChip === "verbatim" && !item.verbatim) return false;
    if (typeVal !== "all" && item.type !== typeVal) return false;
    if (langVal !== "all" && item.lang !== langVal) return false;
    if (yearVal !== "all" && !item.date.startsWith(yearVal)) return false;
    
    if (q) {{
      const text = (item.title + " " + item.source + " " + item.author + " " + item.verbatim + " " + item.topic + " " + item.domain).toLowerCase();
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

function resetFilters() {{
  document.getElementById("pressSearch").value = "";
  document.getElementById("typeSelect").value = "all";
  document.getElementById("langSelect").value = "all";
  document.getElementById("yearSelect").value = "all";
  document.getElementById("sortSelect").value = "newest";
  activeChip = "all";
  document.querySelectorAll(".press-chip-btn").forEach(b => {{
    if (b.getAttribute("onclick").includes("'all'")) b.classList.add("active");
    else b.classList.remove("active");
  }});
  applyFilters();
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
  ghBtn.href = "https://github.com/openfoodfacts/openfoodfacts-web/issues/new?title=" + encodeURIComponent(issueTitle) + "&body=" + encodeURIComponent(issueBody) + "&labels=press-review,documentation";
  
  const mailBtn = document.getElementById("btnMailto");
  mailBtn.href = "mailto:presse@openfoodfacts.org?subject=" + encodeURIComponent(issueTitle) + "&body=" + encodeURIComponent(issueBody.replace(/\\n/g, "\\r\\n"));
}}

document.addEventListener("DOMContentLoaded", () => {{
  currentFiltered = ALL_PRESS.slice();
  renderList();
  updateSubmitLinks();
}});
if (document.readyState !== "loading") {{
  currentFiltered = ALL_PRESS.slice();
  renderList();
  updateSubmitLinks();
}}
</script>
"""

# Write French version
fr_html = build_html("fr")
with open("lang/fr/texts/revue-de-presse-fr.html", "w", encoding="utf-8") as f:
    f.write(fr_html.strip() + "\n")
print("Wrote lang/fr/texts/revue-de-presse-fr.html")

# Write English version (both as revue-de-presse-fr.html for direct access and press-review.html)
en_html = build_html("en")
with open("lang/en/texts/revue-de-presse-fr.html", "w", encoding="utf-8") as f:
    f.write(en_html.strip() + "\n")
print("Wrote lang/en/texts/revue-de-presse-fr.html")

with open("lang/en/texts/press-review.html", "w", encoding="utf-8") as f:
    f.write(en_html.strip() + "\n")
print("Wrote lang/en/texts/press-review.html")

