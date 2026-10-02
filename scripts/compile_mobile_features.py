#!/usr/bin/env python3
"""
Compiler and generator for Open Food Facts Mobile App Features catalog.
Reads structured data from `data/mobile_features.json` and generates:
- `lang/en/texts/mobile-features.html` (Product Opener fragment + Crowdin source)
- `lang/fr/texts/mobile-features.html` (Localized French fragment)
- `mobile-features.html` (Standalone root HTML5 preview page)
- Updates legacy card files in `lang/en/texts/mobileapp/features/*.html`
"""

import json
import os
import re

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
DATA_FILE = os.path.join(REPO_ROOT, "data", "mobile_features.json")
FEATURES_DIR = os.path.join(REPO_ROOT, "lang", "en", "texts", "mobileapp", "features")


def load_features():
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


CATEGORIES = {
    "all": {"label_en": "All Features", "label_fr": "Toutes les fonctionnalités", "icon": "✨"},
    "scan_search": {"label_en": "Scan & Search", "label_fr": "Scan & Recherche", "icon": "🔍"},
    "health_nutrition": {"label_en": "Health & Nutrition", "label_fr": "Santé & Nutrition", "icon": "🥗"},
    "diets_preferences": {"label_en": "Personal Preferences", "label_fr": "Préférences & Régimes", "icon": "⚙️"},
    "environment_packaging": {"label_en": "Planet & Packaging", "label_fr": "Planète & Emballages", "icon": "🌍"},
    "crowd_contribution": {"label_en": "Community & Contribution", "label_fr": "Communauté & Contribution", "icon": "🤝"},
    "tech_privacy": {"label_en": "Technology & Privacy", "label_fr": "Technologie & Univers", "icon": "🔒"},
}


def generate_feature_card_html(feat, lang="en", is_standalone=False):
    """Generate modern, clean HTML for an individual feature card."""
    is_fr = (lang == "fr")
    title = feat["title_fr"] if is_fr else feat["title_en"]
    desc = feat["desc_fr"] if is_fr else feat["desc_en"]
    badge = feat["badge_fr"] if is_fr else feat["badge_en"]
    
    icon_path = feat["icon"]
    if is_standalone and icon_path.startswith("/images/"):
        icon_path = "html" + icon_path
        
    cat_info = CATEGORIES.get(feat["category"], {})
    cat_label = cat_info.get("label_fr" if is_fr else "label_en", feat["category"])
    
    return f"""<article class="off-feat-card" data-category="{feat['category']}" data-id="{feat['id']}" id="feat-{feat['id']}">
  <div class="off-feat-card-top">
    <div class="off-feat-icon-wrap" style="background-color: {feat.get('color', '#F5F5F5')};">
      <img src="{icon_path}" alt="" width="28" height="28" loading="lazy">
    </div>
    <div class="off-feat-meta">
      <span class="off-feat-cat-pill">{cat_label}</span>
      <span class="off-feat-badge">{badge}</span>
    </div>
  </div>
  <h3 class="off-feat-title">{title}</h3>
  <p class="off-feat-desc">{desc}</p>
</article>"""


def generate_catalog_html(lang="en", is_standalone=False):
    """Generate the full mobile-features catalog page."""
    is_fr = (lang == "fr")
    features = load_features()
    img_prefix = "html/images" if is_standalone else "/images"
    showcase_url = "mobile-app-showcase.html" if is_standalone else "/mobile-app-showcase"

    # Localized store links & badges (compliant with test_translation_qa.py)
    if is_fr:
        appstore_url = "https://apps.apple.com/app/open-food-facts/id588797948?l=fr&utm_source=off&utm_medium=web&utm_campaign=search_and_links_promo_fr"
        appstore_badge = f"{img_prefix}/misc/appstore/black/appstore_FR.svg"
        playstore_url = "https://play.google.com/store/apps/details?id=org.openfoodfacts.scanner&hl=fr&utm_source=off&utm_medium=web&utm_campaign=search_and_links_promo_fr"
        playstore_badge = f"{img_prefix}/misc/playstore/img/fr_get.svg"
        fdroid_badge = f"{img_prefix}/misc/fdroid-badge.svg"
        t_eyebrow = "📱 APPLICATION MOBILE OPEN FOOD FACTS (« SMOOTH APP » V2)"
        t_title = "Toutes les fonctionnalités de l'application mobile"
        t_subtitle = "Découvrez comment Open Food Facts décode l'alimentation, les cosmétiques, les produits pour animaux et du quotidien en toute transparence, sans publicité et avec un respect absolu de votre vie privée."
        t_stats_pill = f"⚡ {len(features)} fonctionnalités • 100 % Gratuite & Open Source"
        t_showcase_btn = "📱 Tester le simulateur interactif →"
        t_search_ph = "🔍 Rechercher une fonctionnalité (ex : hors-ligne, végan, additifs, prix, mode sombre, nutriscore...)"
        t_count_label = "fonctionnalités affichées"
        t_no_results = "Aucune fonctionnalité ne correspond à votre recherche."
        t_reset = "Réinitialiser les filtres"
        t_dl_title = "Téléchargez l'application mobile libre et citoyenne"
        t_dl_sub = "Disponible sur iOS, Android, F-Droid et en téléchargement APK direct. Plus de 60 millions de téléchargements dans l'écosystème."
    else:
        appstore_url = "https://apps.apple.com/app/open-food-facts/id588797948?l=en&utm_source=off&utm_medium=web&utm_campaign=search_and_links_promo_en"
        appstore_badge = f"{img_prefix}/misc/appstore/black/appstore_US.svg"
        playstore_url = "https://play.google.com/store/apps/details?id=org.openfoodfacts.scanner&hl=en&utm_source=off&utm_medium=web&utm_campaign=search_and_links_promo_en"
        playstore_badge = f"{img_prefix}/misc/playstore/img/en_get.svg"
        fdroid_badge = f"{img_prefix}/misc/fdroid-badge.svg"
        t_eyebrow = "📱 OPEN FOOD FACTS MOBILE APP (\"SMOOTH APP\" V2)"
        t_title = "Explore All Mobile App Features"
        t_subtitle = "Discover how Open Food Facts decodes food, cosmetics, pet food, and everyday products with complete transparency, zero advertisements, and 100% privacy by design."
        t_stats_pill = f"⚡ {len(features)} Powerful Features • 100% Free & Open Source"
        t_showcase_btn = "📱 Try Live Interactive Showcase →"
        t_search_ph = "🔍 Search features (e.g. offline, vegan, additives, prices, dark mode, nutriscore...)"
        t_count_label = "features displayed"
        t_no_results = "No features match your search criteria."
        t_reset = "Reset filters"
        t_dl_title = "Download the Free & Open-Source Mobile App"
        t_dl_sub = "Available on iOS, Android, F-Droid, and direct APK download. Over 60 million ecosystem app downloads worldwide."

    fdroid_url = "https://f-droid.org/packages/openfoodfacts.github.scrachx.openfood/"
    apk_url = "https://github.com/openfoodfacts/smooth-app/releases/latest"

    # Category counts
    cat_counts = {"all": len(features)}
    for f in features:
        cat_counts[f["category"]] = cat_counts.get(f["category"], 0) + 1

    # Filter buttons HTML
    pills_html = []
    for cat_id, cat_info in CATEGORIES.items():
        active = " active" if cat_id == "all" else ""
        label = cat_info["label_fr"] if is_fr else cat_info["label_en"]
        count = cat_counts.get(cat_id, 0)
        pills_html.append(
            f'<button type="button" class="off-feat-filter-btn{active}" data-cat="{cat_id}">'
            f'<span>{cat_info["icon"]} {label}</span>'
            f'<span class="off-feat-filter-count">{count}</span>'
            f'</button>'
        )

    # Cards HTML
    cards_html = [generate_feature_card_html(f, lang, is_standalone) for f in features]

    catalog_body = f"""<!-- Open Food Facts Mobile Features Catalog -->
<!-- Generated by scripts/compile_mobile_features.py -->
<style>
  :root {{
    --off-espresso: #341100;
    --off-espresso-mid: #473526;
    --off-cream: #f9f8f6;
    --off-peach-tint: #ece0db;
    --off-orange-dot: #ed8857;
    --off-green: #209552;
    --off-macchiato: #85746c;
    --off-radius-pill: 999px;
  }}

  .off-features-wrap {{
    font-family: "Plus Jakarta Sans", "Open Sans", -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
    color: var(--off-espresso);
    max-width: 1280px;
    margin: 0 auto 3rem auto;
    padding: 0 1rem;
    box-sizing: border-box;
  }}

  .off-features-wrap *,
  .off-features-wrap *::before,
  .off-features-wrap *::after {{
    box-sizing: border-box;
  }}

  /* Hero Banner */
  .off-features-hero {{
    background: linear-gradient(180deg, #ffffff 0%, var(--off-cream) 100%);
    border: 1px solid var(--off-peach-tint);
    border-radius: 28px;
    padding: clamp(1.75rem, 3.8vw, 3.25rem);
    margin-bottom: 2.25rem;
    box-shadow: 0 10px 32px rgba(52, 17, 0, 0.05);
    text-align: center;
  }}

  .off-feat-eyebrow {{
    display: inline-flex;
    align-items: center;
    gap: 0.5rem;
    background: var(--off-espresso-mid);
    color: #ffffff;
    font-size: 0.78rem;
    font-weight: 700;
    padding: 0.4rem 0.95rem;
    border-radius: var(--off-radius-pill);
    margin-bottom: 1.1rem;
    letter-spacing: 0.02em;
  }}

  .off-feat-hero-title {{
    font-size: clamp(2rem, 3.6vw, 3rem);
    font-weight: 800;
    line-height: 1.15;
    margin: 0 0 1rem 0;
    color: var(--off-espresso);
    letter-spacing: -0.02em;
  }}

  .off-feat-hero-sub {{
    font-size: clamp(1rem, 1.35vw, 1.15rem);
    line-height: 1.6;
    color: #51443d;
    max-width: 820px;
    margin: 0 auto 1.5rem auto;
  }}

  .off-feat-hero-actions {{
    display: flex;
    flex-wrap: wrap;
    align-items: center;
    justify-content: center;
    gap: 0.85rem;
  }}

  .off-feat-stats-pill {{
    display: inline-flex;
    align-items: center;
    gap: 0.45rem;
    background: #ffffff;
    color: var(--off-espresso);
    border: 1px solid var(--off-peach-tint);
    font-size: 0.86rem;
    font-weight: 700;
    padding: 0.55rem 1.1rem;
    border-radius: var(--off-radius-pill);
  }}

  .off-feat-sim-btn {{
    display: inline-flex;
    align-items: center;
    gap: 0.45rem;
    background: var(--off-espresso);
    color: #ffffff !important;
    text-decoration: none !important;
    font-size: 0.86rem;
    font-weight: 700;
    padding: 0.55rem 1.15rem;
    border-radius: var(--off-radius-pill);
    box-shadow: 0 4px 14px rgba(52, 17, 0, 0.16);
    transition: transform 0.15s ease, background 0.15s ease;
  }}

  .off-feat-sim-btn:hover {{
    transform: translateY(-1px);
    background: #473526;
  }}

  /* Filter & Search Bar */
  .off-feat-toolbar {{
    background: #ffffff;
    border: 1px solid var(--off-peach-tint);
    border-radius: 20px;
    padding: 1.15rem;
    margin-bottom: 2rem;
    box-shadow: 0 6px 20px rgba(52, 17, 0, 0.04);
    display: flex;
    flex-direction: column;
    gap: 1rem;
  }}

  .off-feat-search-wrap {{
    position: relative;
    width: 100%;
  }}

  .off-feat-search-input {{
    width: 100%;
    padding: 0.75rem 1.1rem;
    font-size: 0.95rem;
    border: 1.5px solid var(--off-peach-tint);
    border-radius: var(--off-radius-pill);
    background: var(--off-cream);
    color: var(--off-espresso);
    outline: none;
    transition: border-color 0.18s ease, background 0.18s ease;
  }}

  .off-feat-search-input:focus {{
    border-color: var(--off-espresso);
    background: #ffffff;
    box-shadow: 0 0 0 3px rgba(52, 17, 0, 0.08);
  }}

  .off-feat-pills-row {{
    display: flex;
    flex-wrap: wrap;
    gap: 0.5rem;
    align-items: center;
  }}

  .off-feat-filter-btn {{
    appearance: none;
    border: 1px solid var(--off-peach-tint);
    background: var(--off-cream);
    color: var(--off-espresso);
    font-size: 0.82rem;
    font-weight: 700;
    padding: 0.45rem 0.85rem;
    border-radius: var(--off-radius-pill);
    cursor: pointer;
    display: inline-flex;
    align-items: center;
    gap: 0.45rem;
    transition: all 0.16s ease;
  }}

  .off-feat-filter-btn:hover {{
    background: var(--off-peach-tint);
  }}

  .off-feat-filter-btn.active {{
    background: var(--off-espresso);
    color: #ffffff;
    border-color: var(--off-espresso);
    box-shadow: 0 3px 10px rgba(52, 17, 0, 0.15);
  }}

  .off-feat-filter-count {{
    background: rgba(0, 0, 0, 0.08);
    font-size: 0.72rem;
    padding: 0.1rem 0.45rem;
    border-radius: 999px;
  }}

  .off-feat-filter-btn.active .off-feat-filter-count {{
    background: rgba(255, 255, 255, 0.25);
  }}

  .off-feat-status-bar {{
    display: flex;
    justify-content: space-between;
    align-items: center;
    font-size: 0.82rem;
    color: var(--off-macchiato);
    font-weight: 600;
    padding: 0 0.25rem;
  }}

  /* Feature Cards Grid */
  .off-feat-grid {{
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(330px, 1fr));
    gap: 1.25rem;
  }}

  @media (max-width: 480px) {{
    .off-feat-grid {{
      grid-template-columns: 1fr;
    }}
  }}

  .off-feat-card {{
    background: #ffffff;
    border: 1px solid var(--off-peach-tint);
    border-radius: 20px;
    padding: 1.35rem;
    display: flex;
    flex-direction: column;
    gap: 0.75rem;
    box-shadow: 0 4px 14px rgba(52, 17, 0, 0.03);
    transition: transform 0.18s ease, box-shadow 0.18s ease, border-color 0.18s ease;
  }}

  .off-feat-card:hover {{
    transform: translateY(-3px);
    box-shadow: 0 12px 28px rgba(52, 17, 0, 0.08);
    border-color: var(--off-orange-dot);
  }}

  .off-feat-card-top {{
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 0.65rem;
  }}

  .off-feat-icon-wrap {{
    width: 48px;
    height: 48px;
    border-radius: 14px;
    display: flex;
    align-items: center;
    justify-content: center;
    flex-shrink: 0;
    border: 1px solid rgba(0, 0, 0, 0.06);
  }}

  .off-feat-icon-wrap img {{
    width: 26px;
    height: 26px;
    object-fit: contain;
  }}

  .off-feat-meta {{
    display: flex;
    align-items: center;
    gap: 0.4rem;
  }}

  .off-feat-cat-pill {{
    font-size: 0.7rem;
    font-weight: 700;
    color: var(--off-espresso-mid);
    background: var(--off-cream);
    padding: 0.25rem 0.55rem;
    border-radius: var(--off-radius-pill);
    border: 1px solid var(--off-peach-tint);
  }}

  .off-feat-badge {{
    font-size: 0.68rem;
    font-weight: 800;
    color: #0d522b;
    background: #bbefd2;
    padding: 0.22rem 0.5rem;
    border-radius: 6px;
  }}

  .off-feat-title {{
    font-size: 1.05rem;
    font-weight: 800;
    color: var(--off-espresso);
    margin: 0;
    line-height: 1.35;
  }}

  .off-feat-desc {{
    font-size: 0.88rem;
    line-height: 1.55;
    color: #51443d;
    margin: 0;
    flex: 1;
  }}

  .off-feat-empty {{
    display: none;
    text-align: center;
    padding: 3rem 1rem;
    background: #ffffff;
    border: 1px dashed var(--off-peach-tint);
    border-radius: 20px;
    font-size: 1rem;
    color: var(--off-macchiato);
  }}

  /* Download Call-to-Action */
  .off-feat-dl-box {{
    margin-top: 3.5rem;
    background: linear-gradient(135deg, #341100 0%, #473526 100%);
    color: #ffffff;
    border-radius: 24px;
    padding: clamp(1.5rem, 3.5vw, 2.5rem);
    display: flex;
    flex-wrap: wrap;
    align-items: center;
    justify-content: space-between;
    gap: 1.5rem;
  }}

  .off-feat-dl-badges {{
    display: flex;
    flex-wrap: wrap;
    align-items: center;
    gap: 0.85rem;
  }}

  .off-feat-dl-badges img {{
    height: 44px;
    width: auto;
    display: block;
  }}

  .off-feat-apk-pill {{
    display: inline-flex;
    align-items: center;
    gap: 0.45rem;
    background: rgba(255, 255, 255, 0.14);
    color: #ffffff !important;
    text-decoration: none !important;
    font-size: 0.85rem;
    font-weight: 700;
    padding: 0.65rem 1.15rem;
    border-radius: var(--off-radius-pill);
    border: 1px solid rgba(255, 255, 255, 0.28);
  }}

  .off-feat-apk-pill:hover {{
    background: rgba(255, 255, 255, 0.24);
  }}
</style>

<div class="off-features-wrap">
  <!-- Hero Section -->
  <header class="off-features-hero">
    <div class="off-feat-eyebrow">
      <span style="width:8px;height:8px;border-radius:50%;background:var(--off-orange-dot);display:inline-block;"></span>
      <span>{t_eyebrow}</span>
    </div>
    <h1 class="off-feat-hero-title">{t_title}</h1>
    <p class="off-feat-hero-sub">{t_subtitle}</p>
    <div class="off-feat-hero-actions">
      <span class="off-feat-stats-pill">{t_stats_pill}</span>
      <a href="{showcase_url}" class="off-feat-sim-btn">{t_showcase_btn}</a>
    </div>
  </header>

  <!-- Interactive Toolbar: Live Search & Category Pills -->
  <div class="off-feat-toolbar" role="region" aria-label="Feature Filters">
    <div class="off-feat-search-wrap">
      <input type="search" id="offFeatSearchInput" class="off-feat-search-input" placeholder="{t_search_ph}" aria-label="Search features">
    </div>
    <div class="off-feat-pills-row" role="group" aria-label="Filter by category">
      {"".join(pills_html)}
    </div>
    <div class="off-feat-status-bar">
      <span><strong id="offFeatCount">{len(features)}</strong> {t_count_label}</span>
      <button type="button" id="offFeatResetBtn" style="background:none;border:none;color:var(--off-espresso);cursor:pointer;font-weight:700;text-decoration:underline;font-size:0.8rem;" onclick="offResetFilters()">{t_reset}</button>
    </div>
  </div>

  <!-- Cards Grid -->
  <div class="off-feat-grid" id="offFeatGrid">
    {"".join(cards_html)}
  </div>

  <div class="off-feat-empty" id="offFeatEmpty">
    <p>{t_no_results}</p>
    <button type="button" class="off-feat-filter-btn active" onclick="offResetFilters()">{t_reset}</button>
  </div>

  <!-- Download Footer Banner -->
  <section class="off-feat-dl-box" aria-labelledby="offFeatDlTitle">
    <div style="max-width:580px;">
      <h2 id="offFeatDlTitle" style="font-size:clamp(1.35rem,2.2vw,1.85rem);font-weight:800;margin:0 0 0.5rem 0;color:#ffffff;">{t_dl_title}</h2>
      <p style="font-size:0.92rem;line-height:1.5;margin:0;color:#ece0db;">{t_dl_sub}</p>
    </div>
    <div class="off-feat-dl-badges">
      <a href="{appstore_url}" target="_blank" rel="noopener noreferrer">
        <img src="{appstore_badge}" alt="Download on the App Store" loading="lazy">
      </a>
      <a href="{playstore_url}" target="_blank" rel="noopener noreferrer">
        <img src="{playstore_badge}" alt="Get it on Google Play" loading="lazy">
      </a>
      <a href="{fdroid_url}" target="_blank" rel="noopener noreferrer">
        <img src="{fdroid_badge}" alt="Get it on F-Droid" loading="lazy">
      </a>
      <a href="{apk_url}" class="off-feat-apk-pill" target="_blank" rel="noopener noreferrer">
        📦 Direct APK (GitHub)
      </a>
    </div>
  </section>
</div>

<script>
(function() {{
  let activeCategory = "all";
  const searchInput = document.getElementById("offFeatSearchInput");
  const countEl = document.getElementById("offFeatCount");
  const emptyEl = document.getElementById("offFeatEmpty");
  const cards = Array.from(document.querySelectorAll(".off-feat-card"));

  function filterCards() {{
    const q = (searchInput?.value || "").toLowerCase().trim();
    let visibleCount = 0;

    cards.forEach(card => {{
      const matchesCat = (activeCategory === "all") || (card.getAttribute("data-category") === activeCategory);
      const text = card.textContent.toLowerCase();
      const matchesSearch = !q || text.includes(q);

      if (matchesCat && matchesSearch) {{
        card.style.display = "flex";
        visibleCount++;
      }} else {{
        card.style.display = "none";
      }}
    }});

    if (countEl) countEl.textContent = visibleCount;
    if (emptyEl) emptyEl.style.display = (visibleCount === 0) ? "block" : "none";
  }}

  document.querySelectorAll(".off-feat-filter-btn").forEach(btn => {{
    btn.addEventListener("click", () => {{
      document.querySelectorAll(".off-feat-filter-btn").forEach(b => b.classList.remove("active"));
      btn.classList.add("active");
      activeCategory = btn.getAttribute("data-cat") || "all";
      filterCards();
    }});
  }});

  if (searchInput) {{
    searchInput.addEventListener("input", filterCards);
  }}

  window.offResetFilters = function() {{
    activeCategory = "all";
    if (searchInput) searchInput.value = "";
    document.querySelectorAll(".off-feat-filter-btn").forEach(b => {{
      b.classList.toggle("active", b.getAttribute("data-cat") === "all");
    }});
    filterCards();
  }};

  // Handle URL hash anchor if linking directly to a feature
  const hash = window.location.hash.replace("#", "");
  if (hash) {{
    const target = document.getElementById("feat-" + hash);
    if (target) {{
      target.scrollIntoView({{ behavior: "smooth", block: "center" }});
      target.style.borderColor = "var(--off-orange-dot)";
      target.style.boxShadow = "0 0 0 3px rgba(237, 136, 87, 0.35)";
    }}
  }}
}})();
</script>
"""

    if not is_standalone:
        return catalog_body + "\n[[texts/edit-page-include.html]]\n"

    return f"""<!DOCTYPE html>
<html lang="{lang}">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Open Food Facts — Mobile App Features Catalog</title>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@500;600;700;800&display=swap" rel="stylesheet">
  <style>
    body {{
      margin: 0;
      padding: 1.5rem 0 3rem 0;
      background: #fdfcfb;
      font-family: "Plus Jakarta Sans", -apple-system, BlinkMacSystemFont, sans-serif;
    }}
    .standalone-header {{
      max-width: 1280px;
      margin: 0 auto 1.5rem auto;
      padding: 0 1rem;
      display: flex;
      align-items: center;
      justify-content: space-between;
      flex-wrap: wrap;
      gap: 1rem;
    }}
    .standalone-header img {{
      height: 42px;
      width: auto;
    }}
    .standalone-nav {{
      display: flex;
      gap: 1.25rem;
      font-size: 0.88rem;
      font-weight: 700;
    }}
    .standalone-nav a {{
      color: #341100;
      text-decoration: none;
    }}
  </style>
</head>
<body>
  <header class="standalone-header">
    <a href="https://world.openfoodfacts.org">
      <img src="html/images/logos/off-logo-horizontal-light.svg" alt="Open Food Facts">
    </a>
    <nav class="standalone-nav">
      <a href="mobile-app-showcase.html">Interactive App Showcase</a>
      <a href="https://world.openfoodfacts.org/open-food-facts-mobile-app">Official App Landing Page</a>
      <a href="https://github.com/openfoodfacts/smooth-app">Smooth App GitHub</a>
    </nav>
  </header>
  <main>
{catalog_body}
  </main>
</body>
</html>
"""


def modernize_individual_card_files(features):
    """
    Update the individual legacy files in `lang/en/texts/mobileapp/features/*.html`
    to clean, modern semantic markup so any legacy includes render cleanly with valid paths.
    """
    os.makedirs(FEATURES_DIR, exist_ok=True)
    card_map = {f["id"]: f for f in features}
    
    # Also support aliases
    alias_map = {
        "readinessscore": {
            "id": "readinessscore",
            "category": "health_nutrition",
            "icon": "/images/misc/mobileapp/features/readinessscore.svg",
            "color": "#F1F3F4",
            "title_en": "Data Readiness & Quality Score",
            "desc_en": "Checks completeness of the product record, highlighting missing photos, nutritional data, or packaging details for contributors."
        }
    }

    for filename in sorted(os.listdir(FEATURES_DIR)):
        if not filename.endswith(".html"):
            continue
        feat_id = filename[:-5]
        feat = card_map.get(feat_id) or alias_map.get(feat_id)
        if not feat:
            continue
            
        icon_path = feat["icon"]
        # Ensure path is /images/... for web fragment
        if not icon_path.startswith("/images/"):
            icon_path = "/" + icon_path.lstrip("/")
            
        card_content = f"""<!-- {feat['title_en']} Card -->
<div class="off-feat-card" style="background:#ffffff;border:1px solid #ece0db;border-radius:18px;padding:1.25rem;display:flex;flex-direction:column;gap:0.65rem;">
  <div style="display:flex;align-items:center;gap:0.75rem;">
    <div style="width:44px;height:44px;border-radius:12px;background:{feat.get('color', '#F5F5F5')};display:flex;align-items:center;justify-content:center;flex-shrink:0;">
      <img src="{icon_path}" alt="" width="24" height="24" loading="lazy">
    </div>
    <h4 style="margin:0;font-size:1rem;font-weight:800;color:#341100;">{feat['title_en']}</h4>
  </div>
  <div style="font-size:0.86rem;line-height:1.55;color:#51443d;">
    {feat['desc_en']}
  </div>
</div>
"""
        filepath = os.path.join(FEATURES_DIR, filename)
        with open(filepath, "w", encoding="utf-8") as fp:
            fp.write(card_content)


def main():
    features = load_features()
    
    en_path = os.path.join(REPO_ROOT, "lang", "en", "texts", "mobile-features.html")
    fr_path = os.path.join(REPO_ROOT, "lang", "fr", "texts", "mobile-features.html")
    standalone_path = os.path.join(REPO_ROOT, "mobile-features.html")
    
    with open(en_path, "w", encoding="utf-8") as f:
        f.write(generate_catalog_html("en", is_standalone=False))
    print(f"Wrote {en_path}")

    with open(fr_path, "w", encoding="utf-8") as f:
        f.write(generate_catalog_html("fr", is_standalone=False))
    print(f"Wrote {fr_path}")

    with open(standalone_path, "w", encoding="utf-8") as f:
        f.write(generate_catalog_html("en", is_standalone=True))
    print(f"Wrote {standalone_path}")
    
    modernize_individual_card_files(features)
    print(f"Modernized {len(features)} feature cards in {FEATURES_DIR}")


if __name__ == "__main__":
    main()
