#!/usr/bin/env python3
"""
Generate the Open Food Facts Reuses & Applications Showcase pages.
Generates:
- lang/en/texts/reuse.html
- lang/en/texts/reuses.html
- lang/fr/texts/reuses.html
- lang/fr/texts/reutilisations.html
"""

import json
import os
import urllib.parse

DATA_FILE = "data/reuses.json"
YAML_DIR = "data/reuses"

if os.path.isdir(YAML_DIR) and os.listdir(YAML_DIR):
    import glob, yaml
    yaml_files = sorted(glob.glob(os.path.join(YAML_DIR, "*.yaml")) + glob.glob(os.path.join(YAML_DIR, "*.yml")))
    ALL_REUSES = []
    for yf in yaml_files:
        with open(yf, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)
            if isinstance(data, dict):
                ALL_REUSES.append(data)
    ALL_REUSES.sort(key=lambda x: (not x.get("featured", False), (x.get("name") or "").lower()))
elif os.path.exists(DATA_FILE):
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        ALL_REUSES = json.load(f)
else:
    ALL_REUSES = []

TOTAL_APPS = len(ALL_REUSES)
TOTAL_INSTALLS_NUM = sum(r.get("installs_numeric", 0) for r in ALL_REUSES)
TOTAL_COUNTRIES = len(set(r.get("country") for r in ALL_REUSES if r.get("country")))
TOTAL_CONTRIBUTED_DATA = sum(r.get("data_contributions_count", 0) for r in ALL_REUSES)
print(f"Loaded {TOTAL_APPS} reuses for showcase generation. Recorded ecosystem installs: {TOTAL_INSTALLS_NUM:,}, Contributed products: {TOTAL_CONTRIBUTED_DATA:,}")

def generate_html(lang="en"):
    is_fr = (lang == "fr")

    # Translations
    t_title = "🚀 Vitrine de l'écosystème & des réutilisations" if is_fr else "🚀 Open Food Facts Ecosystem & Reuses Showcase"
    t_subtitle = (
        "Découvrez des centaines d'applications, projets de recherche, plateformes citoyennes et outils propulsés par les données ouvertes d'Open Food Facts."
        if is_fr else
        "Discover hundreds of mobile apps, research projects, civic platforms, and tools powered by Open Food Facts open data."
    )
    
    # Impact Hero Stats
    t_stat_installs_num = "60M+"
    t_stat_installs_label = "Téléchargements cumulés" if is_fr else "Combined App Downloads"
    t_stat_installs_sub = "Google Play & App Store" if is_fr else "Google Play & App Store"

    t_stat_apps_num = f"{TOTAL_APPS}+"
    t_stat_apps_label = "Réutilisations & services" if is_fr else "Active Reuses & Services"
    t_stat_apps_sub = "En production mondiale" if is_fr else "In production worldwide"

    t_stat_contribs_num = f"{TOTAL_CONTRIBUTED_DATA / 1000000:.1f}M+" if TOTAL_CONTRIBUTED_DATA >= 1000000 else (f"{TOTAL_CONTRIBUTED_DATA // 1000}K+" if TOTAL_CONTRIBUTED_DATA >= 1000 else f"{TOTAL_CONTRIBUTED_DATA}")
    t_stat_contribs_label = "Produits contribués" if is_fr else "Products Contributed Back"
    t_stat_contribs_sub = "Données au bien commun" if is_fr else "To the global commons"

    t_stat_countries_num = f"{TOTAL_COUNTRIES}+"
    t_stat_countries_label = "Pays & territoires" if is_fr else "Geographies Reached"
    t_stat_countries_sub = "Impact international" if is_fr else "Global food transparency"

    t_stat_open_num = "100%"
    t_stat_open_label = "Données ouvertes" if is_fr else "Open Data & Commons"
    t_stat_open_sub = "Licence ODbL & API libre" if is_fr else "ODbL & free open API"

    # Header Action Buttons
    t_submit_gh_btn = "🚀 Déclarer via GitHub" if is_fr else "🚀 Register via GitHub"
    t_edit_gh_btn = "✏️ Proposer une modif (PR)" if is_fr else "✏️ Propose an Edit (PR)"
    t_donate_btn = "💝 Soutenir par un don" if is_fr else "💝 Donate to the NGO"
    t_submit_form_btn = "📝 Formulaire Google" if is_fr else "📝 Google Form"
    t_submit_drawer_btn = "ℹ️ Options de soumission" if is_fr else "ℹ️ Submit Options"
    t_sdk_btn = "📦 SDKs & API Développeurs" if is_fr else "📦 Developer SDKs & API"
    t_team_btn = "🤝 Équipe Réutilisateurs" if is_fr else "🤝 Reusers Community"

    # API banner
    t_api_banner_title = "📢 Développeur ou créateur d'app ? Rejoignez la communauté des réutilisateurs !" if is_fr else "📢 Building an app or service with Open Food Facts? Join our community!"
    t_api_banner_text = "Accédez à des milliards de points de données alimentaires, suivez les évolutions de l'API, échangez avec les développeurs et contribuez au bien commun." if is_fr else "Access billions of food data points, stay updated on API releases, connect directly with core developers, and contribute back to the open commons."
    t_link_api_list = "✉️ Liste d'annonces API" if is_fr else "✉️ API Announcements Mailing List"
    t_link_slack = "💬 Slack #reuse & #api" if is_fr else "💬 Slack #reuse & #api"
    t_link_meet = "🗓️ Réunion mensuelle (3e mardi)" if is_fr else "🗓️ Monthly Meeting (3rd Tuesday)"
    t_link_form = "📝 Déclarer sur Formulaire" if is_fr else "📝 Register on Form"
    t_link_gh = "🚀 Déclarer sur GitHub" if is_fr else "🚀 Register on GitHub"
    t_link_edit_gh = "✏️ Proposer un correctif sur GitHub" if is_fr else "✏️ Propose a correction on GitHub"
    t_link_donate = "💝 Soutenir l'association" if is_fr else "💝 Donate to the NGO"

    # SDK Drawer
    t_sdk_title = "🛠️ SDKs Développeurs & Bonnes Pratiques d'Intégration" if is_fr else "🛠️ Developer SDKs & Integration Best Practices"
    t_sdk_p1 = "L'API d'Open Food Facts est gratuite, ouverte et disponible pour tout le monde sous licence Open Database License (ODbL)." if is_fr else "The Open Food Facts API is free, open, and available to everyone under the Open Database License (ODbL)."
    t_rule1_title = "1. Mentionnez la source (ODbL)" if is_fr else "1. Attribute Open Food Facts (ODbL)"
    t_rule1_desc = "Indiquez clairement dans votre application ou site : « Données issues d'Open Food Facts » avec un lien vers la fiche produit." if is_fr else "Visible attribution: credit 'Data from Open Food Facts' with a link to the product or openfoodfacts.org."
    t_rule2_title = "2. Identifiez vos requêtes (User-Agent)" if is_fr else "2. Identify Your Requests (User-Agent)"
    t_rule2_desc = "Renseignez un en-tête User-Agent personnalisé (ex: MonApp/1.0 contact@monapp.com) pour éviter tout blocage automatique." if is_fr else "Set a descriptive User-Agent (e.g. MyApp/1.0 contact@myapp.com) so we can identify your traffic and support you."
    t_rule3_title = "3. Bouclez la boucle : contribuez !" if is_fr else "3. Close the Loop: Contribute Back!"
    t_rule3_desc = "Permettez à vos utilisateurs d'ajouter des produits ou d'envoyer des photos. Plus la base grandit, plus votre application s'améliore." if is_fr else "Allow your users to upload missing products and packaging photos. Enriched data directly benefits your app."

    # Submit Drawer
    t_sub_title = "Soumettre ou actualiser une réutilisation" if is_fr else "Submit or Update a Reuse"
    t_sub_desc = "Vous utilisez les données d'Open Food Facts dans une application, un site, une étude ou un projet étudiant ? Faites-le nous savoir pour être mis en valeur dans cette vitrine !" if is_fr else "Using Open Food Facts in an app, website, study, or student project? Let us know to be featured in this showcase!"
    t_sub_card1_title = "🚀 1. Déclarer une nouvelle application" if is_fr else "🚀 1. Register a New Application"
    t_sub_card1_desc = "Ouvrez une demande pré-remplie en un clic sur GitHub pour que votre application soit ajoutée à la vitrine." if is_fr else "Open a pre-filled 1-click issue on GitHub to get your application featured in this showcase."
    t_sub_card2_title = "✏️ 2. Proposer une correction (Pull Request)" if is_fr else "✏️ 2. Propose a Correction (Pull Request)"
    t_sub_card2_desc = "Une information est inexacte, un lien est mort ou vous souhaitez actualiser vos données ? Modifiez directement le fichier de votre app dans data/reuses/ sur GitHub !" if is_fr else "Notice outdated info, a broken link, or want to update your app details? Edit your app YAML in data/reuses/ directly on GitHub to create a Pull Request!"
    t_sub_card3_title = "💝 3. Soutenir l'association par un don" if is_fr else "💝 3. Support the Open Food Facts NGO"
    t_sub_card3_desc = "Open Food Facts est une association citoyenne à but non lucratif. Les dons financent les serveurs, la bande passante et l'API ouverte pour tous." if is_fr else "Open Food Facts is an independent citizen non-profit. Donations fund servers, bandwidth, and the free open API for everyone."

    t_btn_gh = "🚀 Ouvrir une issue GitHub" if is_fr else "🚀 Open GitHub Issue"
    t_btn_gform = "📝 Formulaire Google" if is_fr else "📝 Official Google Form"
    t_btn_mail = "✉️ Contacter l'équipe" if is_fr else "✉️ Email Reuse Team"
    t_btn_edit_gh = "✏️ Éditer sur GitHub (PR)" if is_fr else "✏️ Edit on GitHub (PR)"
    t_btn_donate = "💝 Faire un don défiscalisé" if is_fr else "💝 Make a Donation"

    # Multi-Filter Labels
    t_filter_options_btn = "Filtres avancés & critères multiples" if is_fr else "Multi-Criteria Filters"
    t_search_ph = "🔍 Rechercher par nom, thématique, pays, plateforme, mot-clé..." if is_fr else "🔍 Search by app name, theme, country, platform, keywords..."
    t_sort_featured = "En vedette & Contributeurs" if is_fr else "Featured & Contributors"
    t_sort_contributions = "🤝 Plus fortes contributions (Données)" if is_fr else "🤝 Most Contributed Data"
    t_sort_installs = "⚡ Les plus populaires (Téléchargements)" if is_fr else "⚡ Most Popular (Downloads)"
    t_sort_az = "Nom (A-Z)" if is_fr else "Name (A-Z)"
    t_sort_country = "Pays (A-Z)" if is_fr else "Country (A-Z)"
    t_reset = "Réinitialiser" if is_fr else "Reset All"
    t_show_all = "Tout afficher" if is_fr else "Show all"
    t_details_btn = "Détails" if is_fr else "Details"
    t_clear_all = "Effacer les critères" if is_fr else "Clear all criteria"

    # Modal Labels
    t_modal_yuka_title = "Base de données propre & Contributions en retour" if is_fr else "Proprietary Database & Community Contributions"
    t_modal_yuka_desc = (
        "Yuka a démarré historiquement avec Open Food Facts avant de développer sa propre base de données propriétaire "
        "(ils n'utilisent plus les données ODbL d'Open Food Facts). Néanmoins, Yuka continue de contribuer en retour "
        "des photos d'emballage et certaines données de produits à la base mondiale Open Food Facts."
        if is_fr else
        "Yuka originally launched using Open Food Facts and subsequently developed its own independent proprietary database "
        "(they no longer use Open Food Facts ODbL data). However, Yuka continues to contribute product packaging photos "
        "and select data back to the Open Food Facts global commons."
    )
    t_modal_donation_title = "Soutien financier de l'association Open Food Facts" if is_fr else "Financial Supporter of Open Food Facts NGO"
    t_modal_donation_desc = (
        "Cette application soutient financièrement l'infrastructure, les serveurs et le bien commun d'Open Food Facts via des dons à l'association."
        if is_fr else
        "This application financially supports Open Food Facts open infrastructure, servers, and digital commons through donations to the non-profit."
    )
    t_modal_datacontrib_title = "Contributions de données au bien commun" if is_fr else "Community Data Contributions"
    t_modal_contrib_title = "Statut Open Data & Contributions" if is_fr else "Open Data Status & Contributions"
    t_modal_links_title = "Plateformes & Téléchargements" if is_fr else "Available Platforms & Downloads"
    t_modal_stats_title = "Statistiques d'utilisation" if is_fr else "Usage & Reach Statistics"
    t_modal_share_label = "Lien direct vers cette application :" if is_fr else "Direct link to this application:"
    t_copy_btn = "Copier" if is_fr else "Copy"
    t_copied_toast = "Lien direct copié dans le presse-papier !" if is_fr else "Direct link copied to clipboard!"
    t_modal_edit_notice = (
        "Une information est inexacte ou obsolète ? Proposez une modification directement sur le fichier YAML de cette app via une Pull Request sur GitHub."
        if is_fr else
        "Notice outdated or inaccurate information? Propose a correction directly on this app's YAML file via a GitHub Pull Request."
    )
    t_modal_edit_btn = "✏️ Proposer une correction sur GitHub" if is_fr else "✏️ Propose an Edit on GitHub"
    t_modal_support_text = (
        "Vous utilisez Open Food Facts ? Aidez l'association à maintenir ses serveurs et son API libre."
        if is_fr else
        "Relying on Open Food Facts? Help fund our independent servers and free open API."
    )
    t_modal_donate_btn = "💝 Soutenir par un don" if is_fr else "💝 Support with a Donation"

    # Multi-Filter category titles
    t_cat_themes_diets = "Régimes & Santé" if is_fr else "Diets & Health"
    t_cat_themes_general = "Domaines Généraux" if is_fr else "General Domains"
    t_cat_platforms = "Plateformes" if is_fr else "Platforms"
    t_cat_projects = "Projets" if is_fr else "Projects"
    t_cat_contribs = "Contributions & Soutien" if is_fr else "Contributions & Support"
    t_cat_countries = "Pays / Régions" if is_fr else "Geographies"

    # Badges
    t_badge_donation = "Soutient l'association" if is_fr else "NGO Supporter"
    t_badge_installs = "téléch." if is_fr else "installs"
    t_card_edit = "Modifier" if is_fr else "Edit"
    t_card_edit_title = "Proposer une modification pour cette app sur GitHub" if is_fr else "Propose an edit for this app on GitHub"

    # Localized Store Badges
    play_badge_svg = f"/images/misc/playstore/img/{'fr' if is_fr else 'en'}_get.svg"
    appstore_badge_svg = f"/images/misc/appstore/black/{'appstore_FR' if is_fr else 'appstore_US'}.svg"

    # GitHub Issue Template Link & Edit URL
    gh_edit_url = "https://github.com/openfoodfacts/openfoodfacts-web/tree/main/data/reuses"
    gh_magic_url = "https://github.com/openfoodfacts/openfoodfacts-web/issues/new?template=new-reuse.yml"

    json_data = json.dumps(ALL_REUSES, ensure_ascii=False)

    return f"""<style>
.showcase-header {{
  margin: 1.75rem 0 1.25rem;
}}
.showcase-actions {{
  display: flex;
  flex-wrap: wrap;
  gap: 0.65rem;
  justify-content: center;
  margin: 1.25rem 0 1.5rem;
}}
.showcase-btn {{
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
.ecosystem-impact-hero {{
  background: linear-gradient(135deg, #fff7ed 0%, #f0fdf4 100%);
  border: 1px solid #fed7aa;
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
.impact-stat-item {{
  text-align: center;
  flex: 1 1 160px;
}}
.impact-stat-number {{
  font-size: 2.1rem;
  font-weight: 900;
  color: #c2410c;
  line-height: 1.1;
  margin-bottom: 0.2rem;
  font-family: system-ui, -apple-system, sans-serif;
}}
.impact-stat-label {{
  font-size: 0.88rem;
  font-weight: 700;
  color: #0f172a;
  margin-bottom: 0.15rem;
}}
.impact-stat-sub {{
  font-size: 0.76rem;
  color: #64748b;
}}
.impact-stat-divider {{
  width: 1px;
  height: 44px;
  background: #cbd5e1;
  display: none;
}}
@media (min-width: 768px) {{
  .impact-stat-divider {{
    display: block;
  }}
}}

/* API & Community Banner */
.api-community-banner {{
  background: #f0fdf4;
  border: 1px solid #bbf7d0;
  border-left: 4px solid #16a34a;
  border-radius: 12px;
  padding: 1.25rem 1.5rem;
  margin: 1.25rem auto 1.75rem;
  max-width: 1200px;
  text-align: left;
  box-shadow: 0 2px 6px rgba(0,0,0,0.03);
}}
.api-banner-header {{
  display: flex;
  align-items: center;
  gap: 0.6rem;
  margin-bottom: 0.5rem;
}}
.api-banner-header h3 {{
  font-size: 1.15rem;
  font-weight: 700;
  color: #166534;
  margin: 0;
}}
.api-banner-text {{
  font-size: 0.92rem;
  color: #14532d;
  margin: 0 0 1rem;
  line-height: 1.5;
}}
.api-banner-links {{
  display: flex;
  flex-wrap: wrap;
  gap: 0.65rem;
}}
.api-chip-link {{
  display: inline-flex;
  align-items: center;
  gap: 5px;
  padding: 0.35rem 0.75rem;
  border-radius: 20px;
  background: #ffffff;
  border: 1px solid #86efac;
  color: #15803d;
  font-size: 0.85rem;
  font-weight: 600;
  text-decoration: none;
  transition: all 0.2s ease;
}}
.api-chip-link:hover {{
  background: #16a34a;
  color: #ffffff;
  border-color: #16a34a;
}}
.donation-chip {{
  border-color: #fbcfe8 !important;
  color: #be185d !important;
  background: #fdf2f8 !important;
}}
.donation-chip:hover {{
  background: #db2777 !important;
  color: #ffffff !important;
  border-color: #db2777 !important;
}}

/* Drawers */
.showcase-drawer {{
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
.showcase-drawer.open {{
  display: block;
  animation: showcaseFade 0.25s ease-out;
}}
@keyframes showcaseFade {{
  from {{ opacity: 0; transform: translateY(-6px); }}
  to {{ opacity: 1; transform: translateY(0); }}
}}
.drawer-cards-grid {{
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: 1.25rem;
  margin: 1.25rem 0;
}}
.drawer-card {{
  background: #ffffff;
  border: 1px solid #e2e8f0;
  border-radius: 12px;
  padding: 1.25rem;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
}}
.drawer-card h4 {{
  margin: 0 0 0.5rem;
  font-size: 1.05rem;
  font-weight: 700;
  color: #0f172a;
}}
.drawer-card p {{
  font-size: 0.88rem;
  color: #64748b;
  line-height: 1.45;
  margin: 0 0 1rem;
}}

.sdk-grid {{
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  gap: 0.75rem;
  margin: 1.25rem 0;
}}
.sdk-pill {{
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 0.6rem 0.85rem;
  border-radius: 10px;
  background: #ffffff;
  border: 1px solid #cbd5e1;
  color: #0f172a;
  font-size: 0.88rem;
  font-weight: 600;
  text-decoration: none;
  transition: all 0.2s ease;
}}
.sdk-pill:hover {{
  border-color: #e65100;
  color: #e65100;
  box-shadow: 0 2px 8px rgba(230,81,0,0.12);
}}
.rules-grid {{
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(260px, 1fr));
  gap: 1rem;
  margin-top: 1.5rem;
}}
.rule-card {{
  background: #ffffff;
  border-radius: 10px;
  border: 1px solid #e2e8f0;
  padding: 1rem;
}}
.rule-card h4 {{
  font-size: 0.95rem;
  font-weight: 700;
  color: #0f172a;
  margin: 0 0 0.4rem;
}}
.rule-card p {{
  font-size: 0.84rem;
  color: #64748b;
  margin: 0;
  line-height: 1.45;
}}

/* Filter Bar */
.showcase-filters-bar {{
  max-width: 1200px;
  margin: 0 auto 1.5rem;
  display: flex;
  flex-wrap: wrap;
  gap: 0.85rem;
  align-items: center;
  justify-content: space-between;
}}
.showcase-search-wrap {{
  flex: 1 1 320px;
  position: relative;
}}
.showcase-search-input {{
  width: 100% !important;
  padding: 0.65rem 1rem 0.65rem 2.5rem !important;
  border-radius: 10px !important;
  border: 1px solid #cbd5e1 !important;
  font-size: 0.95rem !important;
  margin: 0 !important;
}}
.showcase-search-icon {{
  position: absolute;
  left: 0.75rem;
  top: 50%;
  transform: translateY(-50%);
  color: #94a3b8;
  font-size: 1.25rem;
  pointer-events: none;
}}
.filter-toggle-btn {{
  display: inline-flex;
  align-items: center;
  gap: 6px;
  cursor: pointer;
}}
.filter-count-badge {{
  background: #e65100;
  color: #ffffff;
  border-radius: 12px;
  font-size: 0.72rem;
  padding: 1px 7px;
  font-weight: 700;
}}

/* Multi-Criteria Filter Panel */
.multi-filter-panel {{
  display: none;
  background: #f8fafc;
  border: 1px solid #e2e8f0;
  border-radius: 14px;
  padding: 1.5rem;
  margin: 1rem auto 1.5rem;
  max-width: 1200px;
  text-align: left;
  box-shadow: 0 4px 14px rgba(0,0,0,0.04);
}}
.multi-filter-panel.open {{
  display: block;
  animation: filterPanelFade 0.2s ease-out;
}}
@keyframes filterPanelFade {{
  from {{ opacity: 0; transform: translateY(-6px); }}
  to {{ opacity: 1; transform: translateY(0); }}
}}
.multi-filter-grid {{
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(190px, 1fr));
  gap: 1.25rem;
}}
.multi-filter-col h4 {{
  font-size: 0.88rem;
  font-weight: 700;
  color: #1e293b;
  margin: 0 0 0.65rem;
  border-bottom: 1px solid #e2e8f0;
  padding-bottom: 0.35rem;
}}
.filter-checkbox-label {{
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 0.84rem;
  color: #334155;
  cursor: pointer;
  margin-bottom: 0.4rem;
  user-select: none;
}}
.filter-checkbox-label input[type="checkbox"] {{
  width: 16px;
  height: 16px;
  cursor: pointer;
  margin: 0;
  accent-color: #e65100;
}}

/* Active Filters Wrap */
.active-filters-wrap {{
  display: none;
  flex-wrap: wrap;
  gap: 0.45rem;
  align-items: center;
  margin: 0.5rem auto 1.25rem;
  max-width: 1200px;
  padding: 0 0.5rem;
}}
.active-filter-pill {{
  display: inline-flex;
  align-items: center;
  gap: 5px;
  background: #fff7ed;
  color: #c2410c;
  border: 1px solid #fed7aa;
  padding: 0.25rem 0.6rem;
  border-radius: 16px;
  font-size: 0.78rem;
  font-weight: 600;
}}
.active-filter-remove {{
  background: none;
  border: none;
  cursor: pointer;
  color: #c2410c;
  font-size: 14px;
  padding: 0 2px;
  line-height: 1;
}}
.active-filter-remove:hover {{
  color: #9a3412;
}}

/* Stats Row */
.showcase-stats {{
  display: flex;
  justify-content: space-between;
  align-items: center;
  max-width: 1200px;
  margin: 0 auto 1.25rem;
  padding: 0 0.5rem;
}}
.showcase-count {{
  font-size: 0.95rem;
  color: #64748b;
  font-weight: 600;
}}

/* Grid & Cards */
.showcase-grid {{
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(340px, 1fr));
  gap: 1.5rem;
  max-width: 1200px;
  margin: 0 auto 2.5rem;
}}
.reuse-card {{
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
.reuse-card:hover {{
  transform: translateY(-3px);
  box-shadow: 0 10px 22px rgba(0,0,0,0.08);
  border-color: #cbd5e1;
}}
.reuse-card.highlighted {{
  border-color: #e65100 !important;
  box-shadow: 0 0 0 3px rgba(230,81,0,0.2), 0 10px 22px rgba(0,0,0,0.08) !important;
}}
.reuse-card-top {{
  display: flex;
  gap: 0.85rem;
  align-items: flex-start;
  margin-bottom: 0.85rem;
}}
.reuse-app-icon {{
  width: 48px;
  height: 48px;
  border-radius: 10px;
  object-fit: contain;
  background: #f8fafc;
  border: 1px solid #e2e8f0;
  padding: 3px;
  flex-shrink: 0;
}}
.reuse-app-meta {{
  flex: 1;
}}
.reuse-app-name {{
  font-size: 1.12rem;
  font-weight: 700;
  color: #0f172a;
  margin: 0 0 0.2rem;
  line-height: 1.3;
}}
.reuse-app-name a {{
  color: inherit;
  text-decoration: none;
}}
.reuse-app-name a:hover {{
  color: #e65100;
  text-decoration: underline;
}}
.anchor-copy-btn {{
  background: none;
  border: none;
  color: #94a3b8;
  cursor: pointer;
  padding: 3px 6px;
  border-radius: 6px;
  display: inline-flex;
  align-items: center;
  transition: color 0.15s, background 0.15s;
}}
.anchor-copy-btn:hover {{
  color: #e65100;
  background: #fff7ed;
}}
.reuse-tags-row {{
  display: flex;
  flex-wrap: wrap;
  gap: 0.35rem;
  align-items: center;
}}
.reuse-project-tag {{
  font-size: 0.72rem;
  font-weight: 600;
  padding: 0.15rem 0.5rem;
  border-radius: 4px;
  background: #fff7ed;
  color: #c2410c;
  border: 1px solid #ffedd5;
}}
.reuse-geo-tag {{
  font-size: 0.72rem;
  color: #475569;
  background: #f1f5f9;
  padding: 0.15rem 0.5rem;
  border-radius: 4px;
}}
.reuse-theme-tag {{
  font-size: 0.72rem;
  font-weight: 600;
  padding: 0.15rem 0.5rem;
  border-radius: 4px;
  display: inline-flex;
  align-items: center;
  gap: 3px;
  border: 1px solid transparent;
}}
.topic-chips-bar {{
  display: flex;
  flex-wrap: wrap;
  gap: 0.45rem;
  margin: 1.1rem auto 1.4rem;
  max-width: 1200px;
  padding: 0 0.5rem;
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
  background: #e65100;
  border-color: #e65100;
  color: #ffffff;
  box-shadow: 0 2px 8px rgba(230,81,0,0.25);
}}
.reuse-tagline {{
  font-size: 0.88rem;
  font-weight: 600;
  color: #334155;
  margin-bottom: 0.5rem;
  line-height: 1.4;
}}
.reuse-description {{
  font-size: 0.84rem;
  color: #64748b;
  margin: 0 0 0.85rem;
  line-height: 1.45;
  display: -webkit-box;
  -webkit-line-clamp: 3;
  -webkit-box-orient: vertical;
  overflow: hidden;
}}
.reuse-badges-row {{
  display: flex;
  flex-wrap: wrap;
  gap: 0.4rem;
  margin-bottom: 1rem;
}}
.reuse-badge {{
  font-size: 0.72rem;
  font-weight: 700;
  padding: 0.2rem 0.55rem;
  border-radius: 6px;
  display: inline-flex;
  align-items: center;
  gap: 4px;
}}
.badge-donation {{ background: #fdf2f8; color: #db2777; border: 1px solid #fbcfe8; font-weight: 700; }}
.badge-installs {{ background: #f0fdf4; color: #166534; border: 1px solid #bbf7d0; font-weight: 700; }}
.badge-rating {{ background: #fffbeb; color: #b45309; border: 1px solid #fef3c7; font-weight: 700; }}
.badge-data {{ background: #ecfdf5; color: #047857; border: 1px solid #a7f3d0; }}
.badge-photo {{ background: #f0fdf4; color: #15803d; border: 1px solid #bbf7d0; }}
.badge-odbl {{ background: #eff6ff; color: #1d4ed8; border: 1px solid #bfdbfe; }}
.badge-foss {{ background: #faf5ff; color: #7e22ce; border: 1px solid #e9d5ff; }}
.badge-yuka {{ background: #fef3c7; color: #92400e; border: 1px solid #fde68a; font-weight: 600; }}

.reuse-card-footer {{
  margin-top: auto;
  padding-top: 0.85rem;
  border-top: 1px solid #f1f5f9;
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  justify-content: space-between;
  gap: 0.5rem;
}}
.store-badges-wrap {{
  display: flex;
  flex-wrap: wrap;
  gap: 0.45rem;
  align-items: center;
}}
.store-badge-link {{
  display: inline-flex;
  align-items: center;
  transition: opacity 0.15s ease, transform 0.15s ease;
}}
.store-badge-link:hover {{
  opacity: 0.88;
  transform: translateY(-1px);
}}
.store-badge-link img {{
  height: 32px;
  width: auto;
  border-radius: 4px;
}}
.store-mini-btn {{
  display: inline-flex;
  align-items: center;
  gap: 4px;
  padding: 0.3rem 0.6rem;
  border-radius: 6px;
  background: #f1f5f9;
  color: #334155;
  font-size: 0.78rem;
  font-weight: 600;
  text-decoration: none;
  border: 1px solid #cbd5e1;
}}
.store-mini-btn:hover {{
  background: #e2e8f0;
  color: #0f172a;
}}
.card-actions-right {{
  display: flex;
  align-items: center;
  gap: 8px;
  margin-left: auto;
}}
.card-edit-btn {{
  background: none;
  border: none;
  color: #64748b;
  font-size: 0.78rem;
  font-weight: 600;
  cursor: pointer;
  padding: 0;
  display: inline-flex;
  align-items: center;
  gap: 2px;
  text-decoration: none;
}}
.card-edit-btn:hover {{
  color: #0284c7;
  text-decoration: underline;
}}
.card-details-btn {{
  background: none;
  border: none;
  color: #e65100;
  font-size: 0.82rem;
  font-weight: 700;
  cursor: pointer;
  padding: 0;
}}
.card-details-btn:hover {{
  text-decoration: underline;
}}

/* Modal Overlay & Dialog */
.app-modal-overlay {{
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
.app-modal-overlay.open {{
  display: flex;
  animation: modalFadeIn 0.2s ease-out;
}}
@keyframes modalFadeIn {{
  from {{ opacity: 0; }}
  to {{ opacity: 1; }}
}}
.app-modal-container {{
  background: #ffffff;
  border-radius: 18px;
  max-width: 660px;
  width: 100%;
  padding: 2rem;
  position: relative;
  box-shadow: 0 20px 40px rgba(0,0,0,0.22);
  text-align: left;
  max-height: 90vh;
  overflow-y: auto;
}}
.app-modal-close {{
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
.app-modal-close:hover {{
  color: #0f172a;
  background: #f1f5f9;
}}
.app-modal-header {{
  display: flex;
  gap: 1.25rem;
  align-items: flex-start;
  margin-bottom: 1rem;
}}
.app-modal-icon {{
  width: 68px;
  height: 68px;
  border-radius: 14px;
  object-fit: contain;
  background: #f8fafc;
  border: 1px solid #e2e8f0;
  padding: 4px;
  flex-shrink: 0;
}}
.app-modal-title {{
  font-size: 1.45rem;
  font-weight: 800;
  color: #0f172a;
  margin: 0 0 0.4rem;
}}
.app-modal-tagline {{
  font-size: 1rem;
  font-weight: 600;
  color: #475569;
  margin-bottom: 0.75rem;
}}
.app-modal-desc {{
  font-size: 0.92rem;
  color: #64748b;
  line-height: 1.6;
  margin-bottom: 1.25rem;
}}
.app-modal-donation-box {{
  background: #fdf2f8;
  border: 1px solid #fbcfe8;
  border-left: 4px solid #db2777;
  border-radius: 10px;
  padding: 1rem;
  margin-bottom: 1.25rem;
}}
.app-modal-datacontrib-box {{
  background: #ecfdf5;
  border: 1px solid #a7f3d0;
  border-left: 4px solid #059669;
  border-radius: 10px;
  padding: 1rem;
  margin-bottom: 1.25rem;
}}
.app-modal-yuka-box {{
  background: #fefce8;
  border: 1px solid #fef08a;
  border-left: 4px solid #ca8a04;
  border-radius: 10px;
  padding: 1rem;
  margin-bottom: 1.25rem;
}}
.app-modal-stats-bar {{
  background: #f8fafc;
  border: 1px solid #e2e8f0;
  border-radius: 10px;
  padding: 0.85rem 1rem;
  margin-bottom: 1.25rem;
  display: flex;
  flex-wrap: wrap;
  gap: 1.25rem;
}}
.app-modal-stat-pill {{
  display: inline-flex;
  align-items: center;
  gap: 6px;
  font-size: 0.88rem;
  font-weight: 600;
  color: #1e293b;
}}
.app-modal-links-grid {{
  display: flex;
  flex-wrap: wrap;
  gap: 0.65rem;
  align-items: center;
}}
.app-modal-share-bar {{
  background: #f8fafc;
  border: 1px solid #e2e8f0;
  border-radius: 10px;
  padding: 1rem;
  margin-top: 1.25rem;
}}
.app-modal-edit-bar {{
  background: #f0f9ff;
  border: 1px solid #bae6fd;
  border-radius: 10px;
  padding: 1rem;
  margin-top: 1rem;
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}}
.app-modal-donate-bar {{
  background: #fff1f2;
  border: 1px solid #fecdd3;
  border-radius: 10px;
  padding: 1rem;
  margin-top: 1rem;
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}}
</style>

<div class="showcase-header text-center">
  <h1 class="title-2 emphasized-title">{t_title}</h1>
  <h4 class="subheader">{t_subtitle}</h4>
  
  <div class="showcase-actions">
    <a href="{gh_magic_url}" target="_blank" rel="noopener noreferrer" class="button round primary small showcase-btn">
      <span class="material-icons">add_circle</span> {t_submit_gh_btn}
    </a>
    <a href="{gh_edit_url}" target="_blank" rel="noopener noreferrer" class="button round secondary small showcase-btn">
      <span class="material-icons">edit_note</span> {t_edit_gh_btn}
    </a>
    <a href="https://donate.openfoodfacts.org/" target="_blank" rel="noopener noreferrer" class="button round small showcase-btn" style="background: #db2777; border-color: #db2777; color: #ffffff;">
      <span class="material-icons">volunteer_activism</span> {t_donate_btn}
    </a>
    <a href="https://forms.gle/hwaeqBfs8ywwhbTg8" target="_blank" rel="noopener noreferrer" class="button round secondary small showcase-btn">
      <span class="material-icons">assignment</span> {t_submit_form_btn}
    </a>
    <button type="button" class="button round secondary small showcase-btn" onclick="toggleDrawer('submitDrawer')">
      <span class="material-icons">tune</span> {t_submit_drawer_btn}
    </button>
    <button type="button" class="button round secondary small showcase-btn" onclick="toggleDrawer('sdkDrawer')">
      <span class="material-icons">code</span> {t_sdk_btn}
    </button>
    <a href="https://wiki.openfoodfacts.org/Reusers_team" target="_blank" rel="noopener noreferrer" class="button round secondary small showcase-btn">
      <span class="material-icons">group</span> {t_team_btn}
    </a>
  </div>
</div>

<!-- Ecosystem Impact Hero Stat Counter -->
<div class="ecosystem-impact-hero">
  <div class="impact-stat-item">
    <div class="impact-stat-number">{t_stat_installs_num}</div>
    <div class="impact-stat-label">{t_stat_installs_label}</div>
    <div class="impact-stat-sub">{t_stat_installs_sub}</div>
  </div>
  <div class="impact-stat-divider"></div>
  <div class="impact-stat-item">
    <div class="impact-stat-number">{t_stat_apps_num}</div>
    <div class="impact-stat-label">{t_stat_apps_label}</div>
    <div class="impact-stat-sub">{t_stat_apps_sub}</div>
  </div>
  <div class="impact-stat-divider"></div>
  <div class="impact-stat-item">
    <div class="impact-stat-number">{t_stat_contribs_num}</div>
    <div class="impact-stat-label">{t_stat_contribs_label}</div>
    <div class="impact-stat-sub">{t_stat_contribs_sub}</div>
  </div>
  <div class="impact-stat-divider"></div>
  <div class="impact-stat-item">
    <div class="impact-stat-number">{t_stat_countries_num}</div>
    <div class="impact-stat-label">{t_stat_countries_label}</div>
    <div class="impact-stat-sub">{t_stat_countries_sub}</div>
  </div>
  <div class="impact-stat-divider"></div>
  <div class="impact-stat-item">
    <div class="impact-stat-number">{t_stat_open_num}</div>
    <div class="impact-stat-label">{t_stat_open_label}</div>
    <div class="impact-stat-sub">{t_stat_open_sub}</div>
  </div>
</div>

<!-- API & Community Callout Banner -->
<div class="api-community-banner">
  <div class="api-banner-header">
    <span class="material-icons" style="color: #16a34a; font-size: 1.6rem;">hub</span>
    <h3>{t_api_banner_title}</h3>
  </div>
  <p class="api-banner-text">{t_api_banner_text}</p>
  <div class="api-banner-links">
    <a href="https://groups.google.com/forum/#!forum/openfoodfacts" target="_blank" rel="noopener noreferrer" class="api-chip-link">{t_link_api_list}</a>
    <a href="https://slack.openfoodfacts.org/" target="_blank" rel="noopener noreferrer" class="api-chip-link">{t_link_slack}</a>
    <a href="https://meet.google.com/osk-fmrd-ypf" target="_blank" rel="noopener noreferrer" class="api-chip-link">{t_link_meet}</a>
    <a href="{gh_magic_url}" target="_blank" rel="noopener noreferrer" class="api-chip-link">{t_link_gh}</a>
    <a href="{gh_edit_url}" target="_blank" rel="noopener noreferrer" class="api-chip-link">{t_link_edit_gh}</a>
    <a href="https://donate.openfoodfacts.org/" target="_blank" rel="noopener noreferrer" class="api-chip-link donation-chip">{t_link_donate}</a>
    <a href="https://forms.gle/hwaeqBfs8ywwhbTg8" target="_blank" rel="noopener noreferrer" class="api-chip-link">{t_link_form}</a>
  </div>
</div>

<!-- Submit / Update / Donate Drawer -->
<div class="showcase-drawer" id="submitDrawer">
  <div style="display: flex; justify-content: space-between; align-items: center;">
    <h3 style="margin: 0; font-size: 1.25rem; color: #0f172a;">{t_sub_title}</h3>
    <button type="button" style="background: none; border: none; font-size: 1.5rem; cursor: pointer; color: #64748b;" onclick="toggleDrawer('submitDrawer')">&times;</button>
  </div>
  <p style="font-size: 0.92rem; color: #475569; margin: 0.5rem 0 1rem;">{t_sub_desc}</p>
  
  <div class="drawer-cards-grid">
    <div class="drawer-card">
      <div>
        <h4>{t_sub_card1_title}</h4>
        <p>{t_sub_card1_desc}</p>
      </div>
      <div style="display: flex; flex-wrap: wrap; gap: 0.5rem;">
        <a href="{gh_magic_url}" target="_blank" rel="noopener noreferrer" class="button round primary small showcase-btn">
          <span class="material-icons">launch</span> {t_btn_gh}
        </a>
        <a href="https://forms.gle/hwaeqBfs8ywwhbTg8" target="_blank" rel="noopener noreferrer" class="button round secondary small showcase-btn">
          <span class="material-icons">assignment</span> {t_btn_gform}
        </a>
      </div>
    </div>

    <div class="drawer-card" style="border-color: #bae6fd; background: #f0f9ff;">
      <div>
        <h4 style="color: #0369a1;">{t_sub_card2_title}</h4>
        <p style="color: #0c4a6e;">{t_sub_card2_desc}</p>
      </div>
      <div>
        <a href="{gh_edit_url}" target="_blank" rel="noopener noreferrer" class="button round secondary small showcase-btn" style="border-color: #0284c7; color: #0284c7;">
          <span class="material-icons">edit_note</span> {t_btn_edit_gh}
        </a>
      </div>
    </div>

    <div class="drawer-card" style="border-color: #fbcfe8; background: #fdf2f8;">
      <div>
        <h4 style="color: #9d174d;">{t_sub_card3_title}</h4>
        <p style="color: #831843;">{t_sub_card3_desc}</p>
      </div>
      <div>
        <a href="https://donate.openfoodfacts.org/" target="_blank" rel="noopener noreferrer" class="button round small showcase-btn" style="background: #db2777; color: white; border: none;">
          <span class="material-icons">volunteer_activism</span> {t_btn_donate}
        </a>
      </div>
    </div>
  </div>
</div>

<!-- SDKs & Developer Drawer -->
<div class="showcase-drawer" id="sdkDrawer">
  <div style="display: flex; justify-content: space-between; align-items: center;">
    <h3 style="margin: 0; font-size: 1.2rem; color: #0f172a;">{t_sdk_title}</h3>
    <button type="button" style="background: none; border: none; font-size: 1.5rem; cursor: pointer; color: #64748b;" onclick="toggleDrawer('sdkDrawer')">&times;</button>
  </div>
  <p style="font-size: 0.92rem; color: #475569; margin: 0.5rem 0 1rem;">{t_sdk_p1} <a href="https://openfoodfacts.github.io/openfoodfacts-server/api/" target="_blank" rel="noopener noreferrer" style="font-weight: 700; color: #e65100;">Consulter la documentation OpenAPI 3.1 &rarr;</a></p>
  
  <div class="sdk-grid">
    <a class="sdk-pill" href="https://pub.dev/packages/openfoodfacts" target="_blank" rel="noopener noreferrer">🎯 Flutter / Dart (Official)</a>
    <a class="sdk-pill" href="https://github.com/openfoodfacts/openfoodfacts-python" target="_blank" rel="noopener noreferrer">🐍 Python (Official)</a>
    <a class="sdk-pill" href="https://github.com/openfoodfacts/openfoodfacts-js" target="_blank" rel="noopener noreferrer">⚡ JavaScript / TS (Official)</a>
    <a class="sdk-pill" href="https://github.com/openfoodfacts/openfoodfacts-kotlin" target="_blank" rel="noopener noreferrer">☕ Kotlin</a>
    <a class="sdk-pill" href="https://github.com/openfoodfacts/openfoodfacts-java" target="_blank" rel="noopener noreferrer">☕ Java</a>
    <a class="sdk-pill" href="https://github.com/openfoodfacts/openfoodfacts-go" target="_blank" rel="noopener noreferrer">🐹 Go</a>
    <a class="sdk-pill" href="https://github.com/openfoodfacts/openfoodfacts-swift" target="_blank" rel="noopener noreferrer">🍎 Swift / iOS</a>
    <a class="sdk-pill" href="https://github.com/openfoodfacts/openfoodfacts-php" target="_blank" rel="noopener noreferrer">🐘 PHP &amp; Laravel</a>
    <a class="sdk-pill" href="https://github.com/openfoodfacts/openfoodfacts-rust" target="_blank" rel="noopener noreferrer">🦀 Rust</a>
    <a class="sdk-pill" href="https://github.com/openfoodfacts/openfoodfacts-ruby" target="_blank" rel="noopener noreferrer">💎 Ruby</a>
    <a class="sdk-pill" href="https://github.com/openfoodfacts/openfoodfacts-elixir" target="_blank" rel="noopener noreferrer">🟣 Elixir</a>
    <a class="sdk-pill" href="https://github.com/openfoodfacts/openfoodfacts-csharp" target="_blank" rel="noopener noreferrer">🔷 .NET / C#</a>
  </div>

  <div class="rules-grid">
    <div class="rule-card">
      <h4>{t_rule1_title}</h4>
      <p>{t_rule1_desc}</p>
    </div>
    <div class="rule-card">
      <h4>{t_rule2_title}</h4>
      <p>{t_rule2_desc}</p>
    </div>
    <div class="rule-card">
      <h4>{t_rule3_title}</h4>
      <p>{t_rule3_desc}</p>
    </div>
  </div>
</div>

<!-- Search and Filter Bar -->
<div class="showcase-filters-bar">
  <div class="showcase-search-wrap">
    <span class="material-icons showcase-search-icon">search</span>
    <input type="search" id="showcaseSearch" class="showcase-search-input" placeholder="{t_search_ph}" oninput="applyFilters()">
  </div>

  <button type="button" class="button secondary small filter-toggle-btn showcase-btn" onclick="toggleMultiFilterPanel()">
    <span class="material-icons">tune</span> {t_filter_options_btn}
    <span id="activeFilterBadge" class="filter-count-badge" style="display: none;">0</span>
  </button>

  <div style="display: flex; align-items: center; gap: 0.5rem;">
    <label for="sortSelect" style="font-size: 0.85rem; color: #64748b; font-weight: 600; margin: 0;">Sort:</label>
    <select id="sortSelect" onchange="applyFilters()" style="margin: 0; padding: 0.45rem 0.75rem; border-radius: 8px; border: 1px solid #cbd5e1; font-size: 0.88rem;">
      <option value="featured">{t_sort_featured}</option>
      <option value="contributions">{t_sort_contributions}</option>
      <option value="installs">{t_sort_installs}</option>
      <option value="az">{t_sort_az}</option>
      <option value="country">{t_sort_country}</option>
    </select>
  </div>
</div>

<!-- Granular Quick-Filter Topic Chips Bar -->
<div class="topic-chips-bar">
  <button type="button" class="chip-btn active" onclick="selectThemeChip(this, 'all')">✨ {'Toutes les réutilisations' if is_fr else 'All Reuses'}</button>
  <button type="button" class="chip-btn" onclick="selectThemeChip(this, 'pregnancy')">🤰 {'Grossesse' if is_fr else 'Pregnancy'}</button>
  <button type="button" class="chip-btn" onclick="selectThemeChip(this, 'gluten')">🌾 {'Sans gluten' if is_fr else 'Gluten-Free'}</button>
  <button type="button" class="chip-btn" onclick="selectThemeChip(this, 'lactose')">🥛 {'Sans lactose' if is_fr else 'Lactose-Free'}</button>
  <button type="button" class="chip-btn" onclick="selectThemeChip(this, 'fodmap')">🍏 FODMAP</button>
  <button type="button" class="chip-btn" onclick="selectThemeChip(this, 'allergies')">⚠️ Allergies</button>
  <button type="button" class="chip-btn" onclick="selectThemeChip(this, 'vegan')">🌱 Vegan</button>
  <button type="button" class="chip-btn" onclick="selectThemeChip(this, 'diabetes_keto')">🩸 {'Diabète / Keto' if is_fr else 'Diabetes / Keto'}</button>
  <button type="button" class="chip-btn" onclick="selectThemeChip(this, 'additives')">🧪 {'Additifs' if is_fr else 'Additives'}</button>
  <button type="button" class="chip-btn" onclick="selectThemeChip(this, 'environment')">♻️ {'Environnement' if is_fr else 'Environment'}</button>
  <button type="button" class="chip-btn" onclick="selectThemeChip(this, 'tools')">🛠️ {'Outils & Frigo' if is_fr else 'Tools & Pantry'}</button>
  <button type="button" class="chip-btn" onclick="selectThemeChip(this, 'research')">🔬 {'Recherche' if is_fr else 'Research'}</button>
  <button type="button" class="chip-btn" onclick="selectThemeChip(this, 'traceability')">🏷️ {'Traçabilité' if is_fr else 'Traceability'}</button>
</div>

<!-- Multi-Criteria Checkbox Filter Panel -->
<div class="multi-filter-panel" id="multiFilterPanel">
  <div class="multi-filter-grid">
    <div class="multi-filter-col">
      <h4>{t_cat_themes_diets}</h4>
      <label class="filter-checkbox-label"><input type="checkbox" name="filter_theme" value="pregnancy" onchange="applyFilters()"> 🤰 {'Grossesse & Maternité' if is_fr else 'Pregnancy & Maternity'}</label>
      <label class="filter-checkbox-label"><input type="checkbox" name="filter_theme" value="gluten" onchange="applyFilters()"> 🌾 {'Sans Gluten & Cœliaque' if is_fr else 'Gluten-Free & Celiac'}</label>
      <label class="filter-checkbox-label"><input type="checkbox" name="filter_theme" value="lactose" onchange="applyFilters()"> 🥛 {'Sans Lactose & Produits Laitiers' if is_fr else 'Lactose-Free & Dairy'}</label>
      <label class="filter-checkbox-label"><input type="checkbox" name="filter_theme" value="fodmap" onchange="applyFilters()"> 🍏 {'FODMAP & Intestin Irritable' if is_fr else 'FODMAP & IBS'}</label>
      <label class="filter-checkbox-label"><input type="checkbox" name="filter_theme" value="allergies" onchange="applyFilters()"> ⚠️ {'Allergies & Intolérances' if is_fr else 'Allergies & Intolerances'}</label>
      <label class="filter-checkbox-label"><input type="checkbox" name="filter_theme" value="vegan" onchange="applyFilters()"> 🌱 {'Végétalien & Végétarien' if is_fr else 'Vegan & Vegetarian'}</label>
      <label class="filter-checkbox-label"><input type="checkbox" name="filter_theme" value="halal_kosher" onchange="applyFilters()"> 🕊️ {'Halal & Casher' if is_fr else 'Halal & Kosher'}</label>
      <label class="filter-checkbox-label"><input type="checkbox" name="filter_theme" value="diabetes_keto" onchange="applyFilters()"> 🩸 {'Diabète & Indice Glycémique' if is_fr else 'Diabetes & Low-Carb / Keto'}</label>
      <label class="filter-checkbox-label"><input type="checkbox" name="filter_theme" value="additives" onchange="applyFilters()"> 🧪 {'Additifs & Ultra-transformation' if is_fr else 'Additives & Ultra-Processing'}</label>
    </div>

    <div class="multi-filter-col">
      <h4>{t_cat_themes_general}</h4>
      <label class="filter-checkbox-label"><input type="checkbox" name="filter_theme" value="nutrition" onchange="applyFilters()"> 🥗 {'Nutrition & Santé Générale' if is_fr else 'Nutrition & General Health'}</label>
      <label class="filter-checkbox-label"><input type="checkbox" name="filter_theme" value="environment" onchange="applyFilters()"> ♻️ {'Environnement & Éco-Score' if is_fr else 'Environment & Eco-Score'}</label>
      <label class="filter-checkbox-label"><input type="checkbox" name="filter_theme" value="tools" onchange="applyFilters()"> 🛠️ {'Outils & Frigo' if is_fr else 'Tools & Pantry'}</label>
      <label class="filter-checkbox-label"><input type="checkbox" name="filter_theme" value="research" onchange="applyFilters()"> 🔬 {'Science & Recherche' if is_fr else 'Science & Research'}</label>
      <label class="filter-checkbox-label"><input type="checkbox" name="filter_theme" value="traceability" onchange="applyFilters()"> 🏷️ {'Traçabilité & Terroir' if is_fr else 'Traceability & Local'}</label>
      <label class="filter-checkbox-label"><input type="checkbox" name="filter_theme" value="education" onchange="applyFilters()"> 🎓 {'Éducation & Jeux' if is_fr else 'Education & Games'}</label>
    </div>

    <div class="multi-filter-col">
      <h4>{t_cat_platforms}</h4>
      <label class="filter-checkbox-label"><input type="checkbox" name="filter_platform" value="android" onchange="applyFilters()"> 🤖 Android (Play Store)</label>
      <label class="filter-checkbox-label"><input type="checkbox" name="filter_platform" value="ios" onchange="applyFilters()"> 🍎 iOS (App Store)</label>
      <label class="filter-checkbox-label"><input type="checkbox" name="filter_platform" value="fdroid" onchange="applyFilters()"> 🤖 F-Droid (FOSS)</label>
      <label class="filter-checkbox-label"><input type="checkbox" name="filter_platform" value="web" onchange="applyFilters()"> 🌐 Web / PWA</label>
      <label class="filter-checkbox-label"><input type="checkbox" name="filter_platform" value="github" onchange="applyFilters()"> 💻 Open Source (GitHub)</label>
    </div>

    <div class="multi-filter-col">
      <h4>{t_cat_projects}</h4>
      <label class="filter-checkbox-label"><input type="checkbox" name="filter_project" value="openfoodfacts" onchange="applyFilters()"> 🍊 Open Food Facts</label>
      <label class="filter-checkbox-label"><input type="checkbox" name="filter_project" value="openbeautyfacts" onchange="applyFilters()"> 🧴 Open Beauty Facts</label>
      <label class="filter-checkbox-label"><input type="checkbox" name="filter_project" value="openpetfoodfacts" onchange="applyFilters()"> 🐾 Open Pet Food Facts</label>
      <label class="filter-checkbox-label"><input type="checkbox" name="filter_project" value="openproductsfacts" onchange="applyFilters()"> 📸 Open Products Facts</label>
    </div>

    <div class="multi-filter-col">
      <h4>{t_cat_contribs}</h4>
      <label class="filter-checkbox-label"><input type="checkbox" name="filter_contrib" value="donation" onchange="applyFilters()"> 💝 {'Soutient l\'association (Dons)' if is_fr else 'Supports OFF NGO (Donations)'}</label>
      <label class="filter-checkbox-label"><input type="checkbox" name="filter_contrib" value="data" onchange="applyFilters()"> 🤝 {'Données contribuées' if is_fr else 'Contributes Data Back'}</label>
      <label class="filter-checkbox-label"><input type="checkbox" name="filter_contrib" value="photos" onchange="applyFilters()"> 📸 {'Photos contribuées' if is_fr else 'Contributes Photos'}</label>
      <label class="filter-checkbox-label"><input type="checkbox" name="filter_contrib" value="odbl" onchange="applyFilters()"> ⚖️ {'Licence ODbL' if is_fr else 'ODbL Compliant'}</label>
      <label class="filter-checkbox-label"><input type="checkbox" name="filter_contrib" value="foss" onchange="applyFilters()"> 💖 Open Source</label>
    </div>

    <div class="multi-filter-col">
      <h4>{t_cat_countries}</h4>
      <label class="filter-checkbox-label"><input type="checkbox" name="filter_country" value="global" onchange="applyFilters()"> 🌍 Worldwide</label>
      <label class="filter-checkbox-label"><input type="checkbox" name="filter_country" value="fra" onchange="applyFilters()"> 🇫🇷 France</label>
      <label class="filter-checkbox-label"><input type="checkbox" name="filter_country" value="usa" onchange="applyFilters()"> 🇺🇸 USA</label>
      <label class="filter-checkbox-label"><input type="checkbox" name="filter_country" value="deu" onchange="applyFilters()"> 🇩🇪 Germany</label>
      <label class="filter-checkbox-label"><input type="checkbox" name="filter_country" value="esp" onchange="applyFilters()"> 🇪🇸 Spain</label>
      <label class="filter-checkbox-label"><input type="checkbox" name="filter_country" value="ita" onchange="applyFilters()"> 🇮🇹 Italy</label>
      <label class="filter-checkbox-label"><input type="checkbox" name="filter_country" value="gbr" onchange="applyFilters()"> 🇬🇧 UK</label>
      <label class="filter-checkbox-label"><input type="checkbox" name="filter_country" value="ind" onchange="applyFilters()"> 🇮🇳 India</label>
      <label class="filter-checkbox-label"><input type="checkbox" name="filter_country" value="pol" onchange="applyFilters()"> 🇵🇱 Poland</label>
      <label class="filter-checkbox-label"><input type="checkbox" name="filter_country" value="bra" onchange="applyFilters()"> 🇧🇷 Brazil</label>
      <label class="filter-checkbox-label"><input type="checkbox" name="filter_country" value="che" onchange="applyFilters()"> 🇨🇭 Switzerland</label>
      <label class="filter-checkbox-label"><input type="checkbox" name="filter_country" value="bel" onchange="applyFilters()"> 🇧🇪 Belgium</label>
    </div>
  </div>
  <div style="margin-top: 1rem; text-align: right;">
    <button type="button" class="button secondary small" onclick="resetFilters()" style="margin: 0;">{t_clear_all}</button>
  </div>
</div>

<!-- Active Filter Pills Bar -->
<div class="active-filters-wrap" id="activeFiltersWrap"></div>

<!-- Stats and Count -->
<div class="showcase-stats">
  <div class="showcase-count" id="showcaseCount">Showing {len(ALL_REUSES)} reuses</div>
  <button type="button" class="button secondary small" onclick="resetFilters()" style="margin: 0;">{t_reset}</button>
</div>

<!-- Card Grid -->
<div class="showcase-grid" id="showcaseGrid"></div>

<!-- Load More / Show All Pagination Bar -->
<div id="loadMoreWrap" style="display: none; justify-content: center; gap: 0.75rem; margin: 2rem 0 3.5rem;">
  <button type="button" id="loadMoreBtn" class="button round primary showcase-btn" onclick="loadMoreCards()"></button>
  <button type="button" class="button round secondary showcase-btn" onclick="showAllCards()">{t_show_all}</button>
</div>

<!-- App Details Modal -->
<div id="appModalOverlay" class="app-modal-overlay" onclick="onModalBackdropClick(event)">
  <div class="app-modal-container" role="dialog" aria-modal="true">
    <button type="button" class="app-modal-close" onclick="closeAppModal()">&times;</button>
    
    <div class="app-modal-header">
      <img id="modalAppIcon" class="app-modal-icon" src="" alt="">
      <div class="app-modal-header-meta">
        <h2 id="modalAppName" class="app-modal-title"></h2>
        <div id="modalAppTags" class="reuse-tags-row"></div>
      </div>
    </div>

    <div id="modalAppTagline" class="app-modal-tagline"></div>
    <div id="modalAppDesc" class="app-modal-desc"></div>

    <!-- Financial Supporter NGO Box -->
    <div id="modalDonationBox" class="app-modal-donation-box" style="display: none;">
      <div style="display: flex; align-items: center; gap: 8px;">
        <span class="material-icons" style="color: #db2777; font-size: 22px;">volunteer_activism</span>
        <strong style="color: #9d174d; font-size: 0.95rem;">{t_modal_donation_title}</strong>
      </div>
      <div id="modalDonationText" style="margin: 0.45rem 0 0; font-size: 0.88rem; color: #9d174d; line-height: 1.45;">{t_modal_donation_desc}</div>
    </div>

    <!-- Community Data Contributions Box -->
    <div id="modalDataContribBox" class="app-modal-datacontrib-box" style="display: none;">
      <div style="display: flex; align-items: center; gap: 8px;">
        <span class="material-icons" style="color: #059669; font-size: 22px;">handshake</span>
        <strong style="color: #065f46; font-size: 0.95rem;">{t_modal_datacontrib_title}</strong>
      </div>
      <div id="modalDataContribText" style="margin: 0.45rem 0 0; font-size: 0.88rem; color: #065f46; line-height: 1.45;"></div>
    </div>

    <!-- Yuka Special Box -->
    <div id="modalYukaBox" class="app-modal-yuka-box" style="display: none;">
      <div style="display: flex; align-items: center; gap: 6px;">
        <span class="material-icons" style="color: #b45309; font-size: 20px;">inventory_2</span>
        <strong style="color: #92400e;">{t_modal_yuka_title}</strong>
      </div>
      <p style="margin: 0.45rem 0 0; font-size: 0.88rem; color: #92400e; line-height: 1.45;">{t_modal_yuka_desc}</p>
    </div>

    <!-- Usage & Reach Stats Bar -->
    <div id="modalStatsBar" class="app-modal-stats-bar" style="display: none;">
      <div id="modalStatsInstalls" class="app-modal-stat-pill" style="display: none;">
        <span class="material-icons" style="color: #16a34a; font-size: 18px;">cloud_download</span>
        <span id="modalStatsInstallsText"></span>
      </div>
      <div id="modalStatsRating" class="app-modal-stat-pill" style="display: none;">
        <span class="material-icons" style="color: #d97706; font-size: 18px;">star</span>
        <span id="modalStatsRatingText"></span>
      </div>
    </div>

    <!-- Badges -->
    <div style="margin: 1.25rem 0 0.5rem; font-weight: 700; font-size: 0.88rem; color: #334155;">{t_modal_contrib_title}</div>
    <div id="modalAppBadges" class="reuse-badges-row" style="margin-bottom: 1.25rem;"></div>

    <!-- Store Links -->
    <div style="margin: 1.25rem 0 0.5rem; font-weight: 700; font-size: 0.88rem; color: #334155;">{t_modal_links_title}</div>
    <div id="modalAppLinks" class="app-modal-links-grid"></div>

    <!-- Direct GitHub Edit Box -->
    <div class="app-modal-edit-bar">
      <div style="display: flex; align-items: center; gap: 6px; font-size: 0.86rem; color: #0369a1; line-height: 1.4;">
        <span class="material-icons" style="font-size: 18px; color: #0284c7;">edit_note</span>
        <span>{t_modal_edit_notice}</span>
      </div>
      <a id="modalGhEditLink" href="{gh_edit_url}" target="_blank" rel="noopener noreferrer" class="button small secondary showcase-btn" style="align-self: flex-start;">
        <span class="material-icons" style="font-size: 14px;">open_in_new</span> {t_modal_edit_btn}
      </a>
    </div>

    <!-- Support NGO Bar -->
    <div class="app-modal-donate-bar">
      <div style="display: flex; align-items: center; gap: 6px; font-size: 0.86rem; color: #9d174d; line-height: 1.4;">
        <span class="material-icons" style="font-size: 18px; color: #db2777;">favorite</span>
        <span>{t_modal_support_text}</span>
      </div>
      <a href="https://donate.openfoodfacts.org/" target="_blank" rel="noopener noreferrer" class="button small showcase-btn" style="background: #db2777; color: white; border: none; align-self: flex-start;">
        <span class="material-icons" style="font-size: 14px;">volunteer_activism</span> {t_modal_donate_btn}
      </a>
    </div>

    <!-- Share Link -->
    <div class="app-modal-share-bar">
      <label style="font-size: 0.82rem; font-weight: 600; color: #64748b; margin-bottom: 4px; display: block;">{t_modal_share_label}</label>
      <div style="display: flex; gap: 0.5rem;">
        <input type="text" id="modalShareInput" readonly style="margin: 0; font-size: 0.85rem; background: #f8fafc;">
        <button type="button" class="button small secondary" style="margin: 0; white-space: nowrap;" onclick="copyModalShareLink()">{t_copy_btn}</button>
      </div>
      <div id="modalShareToast" style="display: none; font-size: 0.8rem; color: #16a34a; font-weight: 600; margin-top: 4px;">✓ {t_copied_toast}</div>
    </div>
  </div>
</div>

<script>
const REUSES_DATA = {json_data};
const IS_FR = {'true' if is_fr else 'false'};
const PLAYSTORE_BADGE_SRC = "{play_badge_svg}";
const APPSTORE_BADGE_SRC = "{appstore_badge_svg}";
const GH_EDIT_URL = "{gh_edit_url}";

const COUNTRY_FLAGS = {{
  "fra": "🇫🇷 France",
  "usa": "🇺🇸 USA",
  "gbr": "🇬🇧 UK",
  "deu": "🇩🇪 Germany",
  "esp": "🇪🇸 Spain",
  "ita": "🇮🇹 Italy",
  "che": "🇨🇭 Switzerland",
  "bel": "🇧🇪 Belgium",
  "nld": "🇳🇱 Netherlands",
  "cze": "🇨🇿 Czechia",
  "pol": "🇵🇱 Poland",
  "ind": "🇮🇳 India",
  "bra": "🇧🇷 Brazil",
  "global": "🌍 Worldwide"
}};

function getProjectTag(project) {{
  switch(project) {{
    case "openbeautyfacts": return '<span class="reuse-project-tag" style="background: #fdf2f8; color: #be185d; border-color: #fce7f3;">🧴 Open Beauty Facts</span>';
    case "openpetfoodfacts": return '<span class="reuse-project-tag" style="background: #fefce8; color: #a16207; border-color: #fef9c3;">🐾 Open Pet Food</span>';
    case "openproductsfacts": return '<span class="reuse-project-tag" style="background: #f0fdf4; color: #15803d; border-color: #dcfce7;">📸 Open Products</span>';
    default: return '<span class="reuse-project-tag">🍊 Open Food Facts</span>';
  }}
}}

function getThemeTag(theme) {{
  switch(theme) {{
    case "pregnancy": return '<span class="reuse-theme-tag" style="background: #fdf2f8; color: #db2777; border-color: #fce7f3;">🤰 ' + (IS_FR ? "Grossesse" : "Pregnancy") + '</span>';
    case "gluten": return '<span class="reuse-theme-tag" style="background: #fefce8; color: #ca8a04; border-color: #fef08a;">🌾 ' + (IS_FR ? "Sans gluten" : "Gluten-Free") + '</span>';
    case "lactose": return '<span class="reuse-theme-tag" style="background: #eff6ff; color: #2563eb; border-color: #dbeafe;">🥛 ' + (IS_FR ? "Sans lactose" : "Lactose-Free") + '</span>';
    case "fodmap": return '<span class="reuse-theme-tag" style="background: #f0fdf4; color: #16a34a; border-color: #dcfce7;">🍏 FODMAP</span>';
    case "allergies": return '<span class="reuse-theme-tag" style="background: #fff1f2; color: #e11d48; border-color: #ffe4e6;">⚠️ ' + (IS_FR ? "Allergies" : "Allergies") + '</span>';
    case "vegan": return '<span class="reuse-theme-tag" style="background: #f0fdf4; color: #15803d; border-color: #bbf7d0;">🌱 Vegan</span>';
    case "halal_kosher": return '<span class="reuse-theme-tag" style="background: #f8fafc; color: #475569; border-color: #e2e8f0;">🕊️ Halal/Kosher</span>';
    case "diabetes_keto": return '<span class="reuse-theme-tag" style="background: #faf5ff; color: #9333ea; border-color: #f3e8ff;">🩸 ' + (IS_FR ? "Diabète/Keto" : "Diabetes/Keto") + '</span>';
    case "additives": return '<span class="reuse-theme-tag" style="background: #fff7ed; color: #ea580c; border-color: #ffedd5;">🧪 ' + (IS_FR ? "Additifs" : "Additives") + '</span>';
    case "environment": return '<span class="reuse-theme-tag" style="background: #ecfdf5; color: #059669; border-color: #a7f3d0;">♻️ ' + (IS_FR ? "Environnement" : "Environment") + '</span>';
    case "tools": return '<span class="reuse-theme-tag" style="background: #f1f5f9; color: #475569; border-color: #cbd5e1;">🛠️ ' + (IS_FR ? "Outils" : "Tools") + '</span>';
    case "research": return '<span class="reuse-theme-tag" style="background: #f5f3ff; color: #7c3aed; border-color: #ddd6fe;">🔬 ' + (IS_FR ? "Recherche" : "Research") + '</span>';
    case "traceability": return '<span class="reuse-theme-tag" style="background: #fffbeb; color: #d97706; border-color: #fde68a;">🏷️ ' + (IS_FR ? "Traçabilité" : "Traceability") + '</span>';
    case "education": return '<span class="reuse-theme-tag" style="background: #eef2ff; color: #4f46e5; border-color: #e0e7ff;">🎓 ' + (IS_FR ? "Éducation" : "Education") + '</span>';
    case "nutrition": return '<span class="reuse-theme-tag" style="background: #f0fdf4; color: #15803d; border-color: #bbf7d0;">🥗 Nutrition</span>';
    default: return "";
  }}
}}

const THEME_LABELS = {{
  "pregnancy": IS_FR ? "🤰 Grossesse" : "🤰 Pregnancy",
  "gluten": IS_FR ? "🌾 Sans gluten" : "🌾 Gluten-Free",
  "lactose": IS_FR ? "🥛 Sans lactose" : "🥛 Lactose-Free",
  "fodmap": "🍏 FODMAP",
  "allergies": IS_FR ? "⚠️ Allergies" : "⚠️ Allergies",
  "vegan": "🌱 Vegan",
  "halal_kosher": "🕊️ Halal/Kosher",
  "diabetes_keto": IS_FR ? "🩸 Diabète & Keto" : "🩸 Diabetes & Keto",
  "additives": IS_FR ? "🧪 Additifs" : "🧪 Additives",
  "nutrition": IS_FR ? "🥗 Nutrition" : "🥗 Nutrition",
  "environment": IS_FR ? "♻️ Environnement" : "♻️ Environment",
  "tools": IS_FR ? "🛠️ Outils" : "🛠️ Tools",
  "research": IS_FR ? "🔬 Recherche" : "🔬 Research",
  "traceability": IS_FR ? "🏷️ Traçabilité" : "🏷️ Traceability",
  "education": IS_FR ? "🎓 Éducation" : "🎓 Education"
}};

function getAppIconUrl(item) {{
  if (item.cached_icon) return item.cached_icon;
  if (item.icon_url) return item.icon_url;
  const domain = item.domain || (item.website ? item.website.replace(/^https?:\\/\\/(www\\.)?/, "").split("/")[0] : "");
  if (domain && domain.indexOf(".") !== -1) {{
    return "https://icons.duckduckgo.com/ip3/" + encodeURIComponent(domain) + ".ico";
  }}
  return "/images/reuses/default-app-icon.png";
}}

function formatContribCount(n) {{
  if (!n) return "0";
  if (n >= 1000000) return (n / 1000000).toFixed(1).replace(/\\.0$/, "") + "M";
  if (n >= 1000) return (n / 1000).toFixed(n >= 10000 ? 0 : 1).replace(/\\.0$/, "") + "K";
  return n.toString();
}}

function renderCard(item) {{
  const iconSrc = getAppIconUrl(item);
  const iconImg = '<img class="reuse-app-icon" src="' + iconSrc + '" alt="" loading="lazy" onerror="this.onerror=null; this.src=\\'/images/reuses/default-app-icon.png\\';">';
  
  const flagLabel = COUNTRY_FLAGS[item.country] || item.country_label || "🌍 Global";
  
  // Badges
  const badges = [];
  if (item.donates_to_ngo) {{
    const badgeText = (IS_FR && item.supporter_badge_fr) ? item.supporter_badge_fr : (item.supporter_badge || (IS_FR ? "Soutient l'association" : "NGO Supporter"));
    const donorNote = (IS_FR && item.donation_note_fr) ? item.donation_note_fr : (item.donation_note || (IS_FR ? "Soutient l'association Open Food Facts par des dons financiers" : "Financial supporter of the Open Food Facts NGO"));
    badges.push('<span class="reuse-badge badge-donation" title="' + String(donorNote).replace(/"/g, '&quot;') + '">💝 ' + badgeText + '</span>');
  }}
  if (item.special_badge === "yuka" || item.id === "yuka") {{
    badges.push('<span class="reuse-badge badge-yuka" title="' + (IS_FR ? "Yuka n'utilise plus les données ODbL d'Open Food Facts (base de données propre), mais contribue toujours des photos et certaines données en retour." : "Yuka no longer uses Open Food Facts ODbL data (maintains proprietary database), but still contributes back photos and select data.") + '">📦 ' + (IS_FR ? "Base propre (Contribue photos & données)" : "Own DB (Contributes photos & data)") + '</span>');
  }}
  if (item.installs) {{
    badges.push('<span class="reuse-badge badge-installs" title="' + (IS_FR ? "Téléchargements estimés sur les stores d'applications" : "Estimated app store downloads") + '">📥 ' + item.installs + ' ' + (IS_FR ? "téléch." : "installs") + '</span>');
  }}
  if (item.rating) {{
    badges.push('<span class="reuse-badge badge-rating" title="' + (IS_FR ? "Note sur les stores d'applications" : "App store rating") + '">⭐ ' + item.rating + '</span>');
  }}
  if (item.data_contributions_count && item.data_contributions_count > 0) {{
    const formattedCount = formatContribCount(item.data_contributions_count);
    const dataTitle = (IS_FR ? ("A contribué " + Number(item.data_contributions_count).toLocaleString('fr-FR') + " produits à Open Food Facts") : ("Contributed " + Number(item.data_contributions_count).toLocaleString('en-US') + " products to Open Food Facts"));
    if (item.data_source_url) {{
      badges.push('<a href="' + item.data_source_url + '" target="_blank" rel="noopener noreferrer" class="reuse-badge badge-data" title="' + String(dataTitle).replace(/"/g, '&quot;') + '" onclick="event.stopPropagation();" style="text-decoration: none;">🤝 ' + formattedCount + ' ' + (IS_FR ? "données" : "data") + ' ↗</a>');
    }} else {{
      badges.push('<span class="reuse-badge badge-data" title="' + String(dataTitle).replace(/"/g, '&quot;') + '">🤝 ' + formattedCount + ' ' + (IS_FR ? "données" : "data") + '</span>');
    }}
  }} else if (item.contributes_data) {{
    badges.push('<span class="reuse-badge badge-data" title="' + (IS_FR ? "Contribue des données et nouveaux produits en retour" : "Actively pushes new products & data back") + '">🤝 ' + (IS_FR ? "Données" : "Data") + '</span>');
  }}
  if (item.contributes_photos) badges.push('<span class="reuse-badge badge-photo" title="Uploads product packaging photos">📸 Photos</span>');
  if (item.odbl_compliant) badges.push('<span class="reuse-badge badge-odbl" title="Credits Open Food Facts and respects ODbL">⚖️ ODbL</span>');
  if (item.open_source) badges.push('<span class="reuse-badge badge-foss" title="Free and Open Source Software">💖 FOSS</span>');
  
  // Store badges
  const storeBadges = [];
  if (item.play_store) {{
    storeBadges.push('<a class="store-badge-link" href="' + item.play_store + '" target="_blank" rel="noopener noreferrer" title="Google Play Store"><img src="' + PLAYSTORE_BADGE_SRC + '" alt="Google Play"></a>');
  }}
  if (item.app_store) {{
    storeBadges.push('<a class="store-badge-link" href="' + item.app_store + '" target="_blank" rel="noopener noreferrer" title="Apple App Store"><img src="' + APPSTORE_BADGE_SRC + '" alt="App Store"></a>');
  }}
  if (item.fdroid) {{
    storeBadges.push('<a class="store-badge-link" href="' + item.fdroid + '" target="_blank" rel="noopener noreferrer" title="F-Droid"><img src="/images/misc/fdroid-badge.svg" alt="F-Droid"></a>');
  }}
  if (item.github) {{
    storeBadges.push('<a class="store-mini-btn" href="' + item.github + '" target="_blank" rel="noopener noreferrer" title="GitHub Code"><span class="material-icons" style="font-size: 15px;">code</span> Code</a>');
  }}
  if (item.website && !item.play_store && !item.app_store) {{
    storeBadges.push('<a class="store-mini-btn" href="' + item.website + '" target="_blank" rel="noopener noreferrer"><span class="material-icons" style="font-size: 15px;">language</span> ' + (IS_FR ? "Visiter" : "Website") + '</a>');
  }}

  const nonNutrThemes = (item.themes && item.themes.length > 0)
    ? item.themes.filter(t => t !== "nutrition")
    : (item.theme && item.theme !== "nutrition" ? [item.theme] : []);
  const themeBadges = nonNutrThemes.map(getThemeTag).join("");

  return '<div class="reuse-card" id="app-' + item.id + '">' +
    '<div>' +
      '<div class="reuse-card-top">' +
        iconImg +
        '<div class="reuse-app-meta">' +
          '<div style="display: flex; justify-content: space-between; align-items: flex-start; gap: 4px;">' +
            '<h3 class="reuse-app-name"><a href="javascript:void(0)" onclick="openAppModal(\\'' + item.id + '\\', event)">' + item.name + '</a></h3>' +
            '<button type="button" class="anchor-copy-btn" onclick="openAppModal(\\'' + item.id + '\\', event)" title="' + (IS_FR ? "Partager / Détails" : "Share / Details") + '"><span class="material-icons" style="font-size: 17px;">link</span></button>' +
          '</div>' +
          '<div class="reuse-tags-row">' +
            getProjectTag(item.project) +
            '<span class="reuse-geo-tag">' + flagLabel + '</span>' +
            themeBadges +
          '</div>' +
        '</div>' +
      '</div>' +
      '<div class="reuse-tagline">' + item.tagline + '</div>' +
      '<p class="reuse-description">' + item.description + '</p>' +
      '<div class="reuse-badges-row">' + badges.join("") + '</div>' +
    '</div>' +
    '<div class="reuse-card-footer">' +
      '<div class="store-badges-wrap">' + storeBadges.join(" ") + '</div>' +
      '<div class="card-actions-right">' +
        '<a class="card-edit-btn" href="https://github.com/openfoodfacts/openfoodfacts-web/edit/main/data/reuses/' + item.id + '.yaml" target="_blank" rel="noopener noreferrer" title="' + (IS_FR ? "Proposer une modification sur GitHub" : "Propose an edit on GitHub") + '"><span class="material-icons" style="font-size: 13px;">edit</span> ' + (IS_FR ? "Modifier" : "Edit") + '</a>' +
        '<button type="button" class="card-details-btn" onclick="openAppModal(\\'' + item.id + '\\', event)">' + (IS_FR ? "Détails" : "Details") + ' &rarr;</button>' +
      '</div>' +
    '</div>' +
  '</div>';
}}

let currentFilteredList = [];
let displayedCount = 0;
const PAGE_SIZE = 48;

function renderList(list) {{
  currentFilteredList = list;
  displayedCount = Math.min(list.length, PAGE_SIZE);
  
  const grid = document.getElementById("showcaseGrid");
  const count = document.getElementById("showcaseCount");
  const loadMoreWrap = document.getElementById("loadMoreWrap");
  
  if (!list.length) {{
    grid.innerHTML = '<div style="grid-column: 1 / -1; text-align: center; padding: 3rem; color: #64748b; font-size: 1.1rem;">' + (IS_FR ? "Aucune réutilisation ne correspond à vos filtres." : "No reuses found matching your criteria.") + '</div>';
    count.textContent = IS_FR ? "0 réutilisation" : "0 reuses";
    if (loadMoreWrap) loadMoreWrap.style.display = "none";
    return;
  }}
  
  grid.innerHTML = list.slice(0, displayedCount).map(renderCard).join("");
  updateCountAndLoadMore();
}}

function loadMoreCards() {{
  if (displayedCount >= currentFilteredList.length) return;
  const nextBatch = currentFilteredList.slice(displayedCount, displayedCount + PAGE_SIZE);
  const grid = document.getElementById("showcaseGrid");
  const temp = document.createElement("div");
  temp.innerHTML = nextBatch.map(renderCard).join("");
  while (temp.firstChild) {{
    grid.appendChild(temp.firstChild);
  }}
  displayedCount += nextBatch.length;
  updateCountAndLoadMore();
}}

function showAllCards() {{
  if (displayedCount >= currentFilteredList.length) return;
  const remaining = currentFilteredList.slice(displayedCount);
  const grid = document.getElementById("showcaseGrid");
  const temp = document.createElement("div");
  temp.innerHTML = remaining.map(renderCard).join("");
  while (temp.firstChild) {{
    grid.appendChild(temp.firstChild);
  }}
  displayedCount = currentFilteredList.length;
  updateCountAndLoadMore();
}}

function updateCountAndLoadMore() {{
  const count = document.getElementById("showcaseCount");
  const loadMoreWrap = document.getElementById("loadMoreWrap");
  const loadMoreBtn = document.getElementById("loadMoreBtn");
  
  const total = currentFilteredList.length;
  if (displayedCount < total) {{
    count.textContent = IS_FR 
      ? "Affichage de " + displayedCount + " sur " + total + " réutilisations (" + REUSES_DATA.length + " au total)"
      : "Showing " + displayedCount + " of " + total + " reuses (" + REUSES_DATA.length + " total)";
    if (loadMoreWrap) loadMoreWrap.style.display = "flex";
    if (loadMoreBtn) {{
      const remaining = total - displayedCount;
      const step = Math.min(PAGE_SIZE, remaining);
      loadMoreBtn.textContent = IS_FR 
        ? "Afficher plus de réutilisations (+" + step + ")" 
        : "Load More Reuses (+" + step + ")";
    }}
  }} else {{
    count.textContent = IS_FR 
      ? "Affichage de " + total + " sur " + REUSES_DATA.length + " réutilisations"
      : "Showing " + total + " of " + REUSES_DATA.length + " reuses";
    if (loadMoreWrap) loadMoreWrap.style.display = "none";
  }}
}}

function toggleMultiFilterPanel() {{
  const p = document.getElementById("multiFilterPanel");
  p.classList.toggle("open");
}}

function getCheckedValues(name) {{
  return Array.from(document.querySelectorAll('input[name="' + name + '"]:checked')).map(el => el.value);
}}

let selectedQuickTheme = "all";

function selectThemeChip(btn, themeVal) {{
  selectedQuickTheme = themeVal;
  document.querySelectorAll(".topic-chips-bar .chip-btn").forEach(el => el.classList.remove("active"));
  if (btn) btn.classList.add("active");
  // Clear any theme checkboxes in drawer to avoid empty AND intersection
  document.querySelectorAll('input[name="filter_theme"]').forEach(el => el.checked = false);
  applyFilters();
}}

function applyFilters() {{
  const q = document.getElementById("showcaseSearch").value.toLowerCase().trim();
  const sortVal = document.getElementById("sortSelect").value;
  
  const checkedThemes = getCheckedValues("filter_theme");
  const checkedPlatforms = getCheckedValues("filter_platform");
  const checkedProjects = getCheckedValues("filter_project");
  const checkedContribs = getCheckedValues("filter_contrib");
  const checkedCountries = getCheckedValues("filter_country");

  // If user ticked a theme in drawer, reset quick theme chip to 'all'
  if (checkedThemes.length > 0 && selectedQuickTheme !== "all") {{
    selectedQuickTheme = "all";
    document.querySelectorAll(".topic-chips-bar .chip-btn").forEach(el => {{
      const onclickAttr = el.getAttribute("onclick") || "";
      el.classList.toggle("active", onclickAttr.indexOf("'all'") !== -1);
    }});
  }}
  
  // Total active filter count
  const quickThemeCount = (selectedQuickTheme !== "all") ? 1 : 0;
  const totalActiveFilters = quickThemeCount + checkedThemes.length + checkedPlatforms.length + checkedProjects.length + checkedContribs.length + checkedCountries.length;
  const badge = document.getElementById("activeFilterBadge");
  if (totalActiveFilters > 0) {{
    badge.textContent = totalActiveFilters;
    badge.style.display = "inline-block";
  }} else {{
    badge.style.display = "none";
  }}
  
  // Render active filter pills
  renderActiveFilterPills(checkedThemes, checkedPlatforms, checkedProjects, checkedContribs, checkedCountries);

  const filtered = REUSES_DATA.filter(item => {{
    // Search query
    if (q) {{
      const text = (item.name + " " + item.tagline + " " + item.description + " " + (item.keywords || "") + " " + (item.domain || "")).toLowerCase();
      if (!text.includes(q)) return false;
    }}
    
    // Quick Theme Chip
    if (selectedQuickTheme !== "all") {{
      const itemThemes = Array.isArray(item.themes) && item.themes.length > 0 ? item.themes : (item.theme ? [item.theme] : []);
      if (!itemThemes.includes(selectedQuickTheme) && item.theme !== selectedQuickTheme) return false;
    }}

    // Themes (OR within themes)
    if (checkedThemes.length > 0) {{
      const itemThemes = Array.isArray(item.themes) && item.themes.length > 0 ? item.themes : (item.theme ? [item.theme] : []);
      const matchesAnyTheme = checkedThemes.some(t => itemThemes.includes(t) || item.theme === t);
      if (!matchesAnyTheme) return false;
    }}
    
    // Projects (OR within projects)
    if (checkedProjects.length > 0 && !checkedProjects.includes(item.project)) {{
      return false;
    }}
    
    // Geographies (OR within countries)
    if (checkedCountries.length > 0 && !checkedCountries.includes(item.country)) {{
      return false;
    }}
    
    // Platforms (OR within platforms: item must match at least one ticked platform)
    if (checkedPlatforms.length > 0) {{
      const matchesPlatform = checkedPlatforms.some(p => {{
        if (p === "android") return !!item.play_store;
        if (p === "ios") return !!item.app_store;
        if (p === "fdroid") return !!item.fdroid;
        if (p === "web") return !!item.website;
        if (p === "github") return !!item.github;
        return false;
      }});
      if (!matchesPlatform) return false;
    }}
    
    // Contributions (AND within contribs: item must satisfy all checked contributions)
    if (checkedContribs.length > 0) {{
      for (const c of checkedContribs) {{
        if (c === "donation" && !item.donates_to_ngo) return false;
        if (c === "data" && !item.contributes_data) return false;
        if (c === "photos" && !item.contributes_photos) return false;
        if (c === "odbl" && !item.odbl_compliant) return false;
        if (c === "foss" && !item.open_source) return false;
      }}
    }}
    
    return true;
  }});
  
  if (sortVal === "az") {{
    filtered.sort((a, b) => a.name.localeCompare(b.name));
  }} else if (sortVal === "country") {{
    filtered.sort((a, b) => (a.country_label || "").localeCompare(b.country_label || ""));
  }} else if (sortVal === "installs") {{
    filtered.sort((a, b) => (b.installs_numeric || 0) - (a.installs_numeric || 0));
  }} else if (sortVal === "contributions") {{
    filtered.sort((a, b) => (b.data_contributions_count || 0) - (a.data_contributions_count || 0) || (b.installs_numeric || 0) - (a.installs_numeric || 0));
  }} else if (sortVal === "featured") {{
    filtered.sort((a, b) => 
      (b.featured ? 1 : 0) - (a.featured ? 1 : 0) ||
      (b.donates_to_ngo ? 1 : 0) - (a.donates_to_ngo ? 1 : 0) ||
      (b.data_contributions_count || 0) - (a.data_contributions_count || 0) ||
      (b.contributes_data ? 1 : 0) - (a.contributes_data ? 1 : 0) ||
      (b.installs_numeric || 0) - (a.installs_numeric || 0)
    );
  }}
  
  renderList(filtered);
}}

function renderActiveFilterPills(themes, platforms, projects, contribs, countries) {{
  const wrap = document.getElementById("activeFiltersWrap");
  const pills = [];
  
  if (selectedQuickTheme !== "all") {{
    pills.push({{ name: "quick_theme", val: selectedQuickTheme, label: (THEME_LABELS[selectedQuickTheme] || selectedQuickTheme) }});
  }}
  themes.forEach(val => pills.push({{ name: "filter_theme", val: val, label: (THEME_LABELS[val] || ("Theme: " + val)) }}));
  platforms.forEach(val => pills.push({{ name: "filter_platform", val: val, label: "Platform: " + val }}));
  projects.forEach(val => pills.push({{ name: "filter_project", val: val, label: "Project: " + val }}));
  contribs.forEach(val => {{
    const l = val === "donation" ? (IS_FR ? "💝 Soutient l'association" : "💝 NGO Supporter") : ("Contrib: " + val);
    pills.push({{ name: "filter_contrib", val: val, label: l }});
  }});
  countries.forEach(val => pills.push({{ name: "filter_country", val: val, label: "Geo: " + (COUNTRY_FLAGS[val] || val) }}));
  
  if (!pills.length) {{
    wrap.style.display = "none";
    wrap.innerHTML = "";
    return;
  }}
  
  wrap.style.display = "flex";
  wrap.innerHTML = pills.map(p => 
    '<span class="active-filter-pill">' + p.label + 
    ' <button type="button" class="active-filter-remove" onclick="removeSingleFilter(\\'' + p.name + '\\', \\'' + p.val + '\\')">&times;</button></span>'
  ).join("") + 
  '<button type="button" class="button secondary small" style="margin: 0; padding: 0.2rem 0.5rem; font-size: 0.75rem;" onclick="resetFilters()">' + (IS_FR ? "Tout effacer" : "Clear all") + '</button>';
}}

function removeSingleFilter(inputName, val) {{
  if (inputName === "quick_theme") {{
    selectedQuickTheme = "all";
    document.querySelectorAll(".topic-chips-bar .chip-btn").forEach(el => {{
      const onclickAttr = el.getAttribute("onclick") || "";
      el.classList.toggle("active", onclickAttr.indexOf("'all'") !== -1);
    }});
    applyFilters();
    return;
  }}
  const el = document.querySelector('input[name="' + inputName + '"][value="' + val + '"]');
  if (el) {{
    el.checked = false;
    applyFilters();
  }}
}}

function resetFilters() {{
  document.getElementById("showcaseSearch").value = "";
  document.getElementById("sortSelect").value = "featured";
  selectedQuickTheme = "all";
  document.querySelectorAll(".topic-chips-bar .chip-btn").forEach(el => {{
    const onclickAttr = el.getAttribute("onclick") || "";
    el.classList.toggle("active", onclickAttr.indexOf("'all'") !== -1);
  }});
  document.querySelectorAll('input[type="checkbox"]').forEach(el => el.checked = false);
  applyFilters();
}}

function toggleDrawer(id) {{
  const d = document.getElementById(id);
  d.classList.toggle("open");
  if (d.classList.contains("open")) {{
    d.scrollIntoView({{ behavior: "smooth", block: "start" }});
  }}
}}

/* Anchor & App Details Modal System */
function openAppModal(appId, event) {{
  if (event) event.preventDefault();
  if (appId === "macrofactor-diet-sidekick") appId = "macrofactor";
  const item = REUSES_DATA.find(r => r.id === appId);
  if (!item) return;

  const modal = document.getElementById("appModalOverlay");
  const iconImg = document.getElementById("modalAppIcon");
  const nameEl = document.getElementById("modalAppName");
  const tagsEl = document.getElementById("modalAppTags");
  const taglineEl = document.getElementById("modalAppTagline");
  const descEl = document.getElementById("modalAppDesc");
  const donationBox = document.getElementById("modalDonationBox");
  const donationText = document.getElementById("modalDonationText");
  const dataContribBox = document.getElementById("modalDataContribBox");
  const dataContribText = document.getElementById("modalDataContribText");
  const yukaBox = document.getElementById("modalYukaBox");
  const statsBar = document.getElementById("modalStatsBar");
  const statsInstalls = document.getElementById("modalStatsInstalls");
  const statsInstallsText = document.getElementById("modalStatsInstallsText");
  const statsRating = document.getElementById("modalStatsRating");
  const statsRatingText = document.getElementById("modalStatsRatingText");
  const badgesEl = document.getElementById("modalAppBadges");
  const linksEl = document.getElementById("modalAppLinks");
  const shareInput = document.getElementById("modalShareInput");
  const shareToast = document.getElementById("modalShareToast");

  iconImg.src = getAppIconUrl(item);
  iconImg.onerror = function() {{ this.src = '/images/reuses/default-app-icon.png'; }};
  nameEl.textContent = item.name;
  taglineEl.textContent = item.tagline || "";
  descEl.textContent = item.description || "";

  // Tags
  const flagLabel = COUNTRY_FLAGS[item.country] || item.country_label || "🌍 Global";
  const modalThemes = (item.themes && item.themes.length > 0)
    ? item.themes
    : (item.theme ? [item.theme] : []);
  const modalThemeBadges = modalThemes.map(getThemeTag).join("");
  tagsEl.innerHTML = getProjectTag(item.project) + '<span class="reuse-geo-tag">' + flagLabel + '</span>' + modalThemeBadges;

  // Donation NGO Box
  if (item.donates_to_ngo) {{
    donationBox.style.display = "block";
    const customNote = (IS_FR && item.donation_note_fr) ? item.donation_note_fr : (item.donation_note || "");
    let supporterHtml = "";
    if (item.supporter_badge) {{
      const bText = (IS_FR && item.supporter_badge_fr) ? item.supporter_badge_fr : item.supporter_badge;
      supporterHtml += '<div style="font-weight: 700; color: #db2777; margin-bottom: 4px;">💝 ' + bText + '</div>';
    }}
    if (customNote) {{
      supporterHtml += '<p style="margin: 0; font-size: 0.9rem;">' + customNote + '</p>';
    }}
    if (item.supporter_years && item.supporter_years.length > 1) {{
      supporterHtml += '<div style="margin-top: 6px; font-size: 0.8rem; color: #9d174d;">🗓️ ' + (IS_FR ? "Années de soutien : " : "Years of support: ") + item.supporter_years.join(", ") + '</div>';
    }}
    donationText.innerHTML = supporterHtml;
  }} else {{
    donationBox.style.display = "none";
  }}

  // Data Contributions Box
  if (item.data_contributions_count && item.data_contributions_count > 0) {{
    dataContribBox.style.display = "block";
    let dcHtml = '<p style="margin: 0 0 8px 0; font-size: 0.9rem;">' +
      (IS_FR
        ? ('Cette application contribue activement au bien commun avec <strong>' + Number(item.data_contributions_count).toLocaleString('fr-FR') + ' produits</strong> ajoutés ou complétés dans Open Food Facts.')
        : ('This application actively contributes back to the global commons with <strong>' + Number(item.data_contributions_count).toLocaleString('en-US') + ' products</strong> added or enriched in Open Food Facts.')
      ) + '</p>';
    if (item.data_source_url) {{
      dcHtml += '<a href="' + item.data_source_url + '" target="_blank" rel="noopener noreferrer" class="store-mini-btn" style="display: inline-flex; align-items: center; gap: 4px; background: #059669; color: #ffffff; text-decoration: none; padding: 4px 10px; border-radius: 6px; font-weight: 600; font-size: 0.8rem;">' +
        '<span class="material-icons" style="font-size: 14px;">open_in_new</span> ' +
        (IS_FR ? "Explorer la source de données sur Open Food Facts" : "Explore data source on Open Food Facts") + '</a>';
    }}
    dataContribText.innerHTML = dcHtml;
  }} else {{
    dataContribBox.style.display = "none";
  }}

  // Yuka Special DB Box
  if (item.special_badge === "yuka" || item.id === "yuka") {{
    yukaBox.style.display = "block";
  }} else {{
    yukaBox.style.display = "none";
  }}

  // Usage Stats Bar
  if (item.installs || item.rating) {{
    statsBar.style.display = "flex";
    if (item.installs) {{
      statsInstalls.style.display = "inline-flex";
      statsInstallsText.textContent = (IS_FR ? "Téléchargements : " : "Downloads: ") + item.installs;
    }} else {{
      statsInstalls.style.display = "none";
    }}
    if (item.rating) {{
      statsRating.style.display = "inline-flex";
      statsRatingText.textContent = (IS_FR ? "Note du store : " : "Store Rating: ") + item.rating + " / 5";
    }} else {{
      statsRating.style.display = "none";
    }}
  }} else {{
    statsBar.style.display = "none";
  }}

  // Badges
  const badges = [];
  if (item.donates_to_ngo) {{
    const modalBadgeText = (IS_FR && item.supporter_badge_fr) ? item.supporter_badge_fr : (item.supporter_badge || (IS_FR ? "Soutient l'association" : "NGO Supporter"));
    badges.push('<span class="reuse-badge badge-donation">💝 ' + modalBadgeText + '</span>');
  }}
  if (item.special_badge === "yuka" || item.id === "yuka") {{
    badges.push('<span class="reuse-badge badge-yuka">📦 ' + (IS_FR ? "Base propre (Contribue photos & données)" : "Own DB (Contributes photos & data)") + '</span>');
  }}
  if (item.installs) {{
    badges.push('<span class="reuse-badge badge-installs">📥 ' + item.installs + ' ' + (IS_FR ? "téléch." : "installs") + '</span>');
  }}
  if (item.rating) {{
    badges.push('<span class="reuse-badge badge-rating">⭐ ' + item.rating + '</span>');
  }}
  if (item.data_contributions_count && item.data_contributions_count > 0) {{
    const formattedCount = formatContribCount(item.data_contributions_count);
    if (item.data_source_url) {{
      badges.push('<a href="' + item.data_source_url + '" target="_blank" rel="noopener noreferrer" class="reuse-badge badge-data" style="text-decoration:none;">🤝 ' + formattedCount + ' ' + (IS_FR ? "produits" : "products") + ' ↗</a>');
    }} else {{
      badges.push('<span class="reuse-badge badge-data">🤝 ' + formattedCount + ' ' + (IS_FR ? "produits" : "products") + '</span>');
    }}
  }} else if (item.contributes_data) {{
    badges.push('<span class="reuse-badge badge-data">🤝 ' + (IS_FR ? "Données" : "Data") + '</span>');
  }}
  if (item.contributes_photos) badges.push('<span class="reuse-badge badge-photo">📸 Photos</span>');
  if (item.odbl_compliant) badges.push('<span class="reuse-badge badge-odbl">⚖️ ODbL</span>');
  if (item.open_source) badges.push('<span class="reuse-badge badge-foss">💖 Open Source</span>');
  badgesEl.innerHTML = badges.length ? badges.join(" ") : '<span style="color: #94a3b8; font-size: 0.85rem;">-</span>';

  // Platform Links
  const links = [];
  if (item.play_store) {{
    links.push('<a class="store-badge-link" href="' + item.play_store + '" target="_blank" rel="noopener noreferrer"><img src="' + PLAYSTORE_BADGE_SRC + '" alt="Google Play"></a>');
  }}
  if (item.app_store) {{
    links.push('<a class="store-badge-link" href="' + item.app_store + '" target="_blank" rel="noopener noreferrer"><img src="' + APPSTORE_BADGE_SRC + '" alt="App Store"></a>');
  }}
  if (item.fdroid) {{
    links.push('<a class="store-badge-link" href="' + item.fdroid + '" target="_blank" rel="noopener noreferrer"><img src="/images/misc/fdroid-badge.svg" alt="F-Droid"></a>');
  }}
  if (item.github) {{
    links.push('<a class="button small secondary showcase-btn" href="' + item.github + '" target="_blank" rel="noopener noreferrer"><span class="material-icons" style="font-size: 16px;">code</span> Code Repository</a>');
  }}
  if (item.website) {{
    links.push('<a class="button small primary showcase-btn" href="' + item.website + '" target="_blank" rel="noopener noreferrer"><span class="material-icons" style="font-size: 16px;">language</span> ' + (IS_FR ? "Site officiel" : "Official Website") + ' &rarr;</a>');
  }}
  linksEl.innerHTML = links.join(" ");

  // Direct GitHub Edit link for this app
  const ghEditLink = document.getElementById("modalGhEditLink");
  if (ghEditLink) {{
    ghEditLink.href = "https://github.com/openfoodfacts/openfoodfacts-web/edit/main/data/reuses/" + item.id + ".yaml";
  }}

  // Direct Share Link
  const shareUrl = window.location.origin + window.location.pathname + "#" + item.id;
  shareInput.value = shareUrl;
  shareToast.style.display = "none";

  // Update hash without jumping
  history.replaceState(null, null, "#" + item.id);

  // Highlight card in grid
  document.querySelectorAll(".reuse-card").forEach(c => c.classList.remove("highlighted"));
  const card = document.getElementById("app-" + item.id);
  if (card) card.classList.add("highlighted");

  modal.classList.add("open");
}}

function closeAppModal() {{
  const modal = document.getElementById("appModalOverlay");
  modal.classList.remove("open");
  history.replaceState(null, null, window.location.pathname + window.location.search);
}}

function onModalBackdropClick(event) {{
  if (event.target.id === "appModalOverlay") {{
    closeAppModal();
  }}
}}

function copyModalShareLink() {{
  const input = document.getElementById("modalShareInput");
  input.select();
  navigator.clipboard.writeText(input.value).then(() => {{
    const toast = document.getElementById("modalShareToast");
    toast.style.display = "block";
    setTimeout(() => {{ toast.style.display = "none"; }}, 3000);
  }});
}}

window.addEventListener("keydown", function(e) {{
  if (e.key === "Escape") {{
    closeAppModal();
  }}
}});

// Handle initial anchor hash
function checkHash() {{
  const hash = window.location.hash.replace(/^#app-|^#/, "");
  if (hash) {{
    openAppModal(hash);
  }}
}}

// Initialize
applyFilters();
window.addEventListener("load", checkHash);
window.addEventListener("hashchange", checkHash);
</script>
"""

def main():
    en_html = generate_html("en")
    fr_html = generate_html("fr")

    with open("lang/en/texts/reuse.html", "w", encoding="utf-8") as f:
        f.write(en_html)
    print("Wrote lang/en/texts/reuse.html")

    with open("lang/en/texts/reuses.html", "w", encoding="utf-8") as f:
        f.write(en_html)
    print("Wrote lang/en/texts/reuses.html")

    with open("lang/fr/texts/reuses.html", "w", encoding="utf-8") as f:
        f.write(fr_html)
    print("Wrote lang/fr/texts/reuses.html")

    with open("lang/fr/texts/reutilisations.html", "w", encoding="utf-8") as f:
        f.write(fr_html)
    print("Wrote lang/fr/texts/reutilisations.html")

if __name__ == "__main__":
    main()
