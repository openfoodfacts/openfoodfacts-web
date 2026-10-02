#!/usr/bin/env python3
"""
Generate the modernized Open Food Facts Partners page.
Highlights:
- Active partners featured prominently on top to showcase momentum and lightly incentivize new partners
- Dedicated 'Your Organization Here' card within the active grid directing to fundraising@openfoodfacts.org
- Milestone & historic grants cleanly grouped
- Fixed all partner logos using verified absolute CDN URLs (https://static.openfoodfacts.org/images/...)
- Complete list of 6 NGI / NLnet projects with dates, fund tags, and links
- AFNIC with explicit dates (2020 'Une planète dans mon assiette', 2023 'Open Products Facts')
- The Perl Foundation with explicit dates (2020-2024 Outreachy internships)
- AIC updated official URL: https://communs.beta.gouv.fr/laureats/open-food-facts/
- ADEME 3 projects: Coût environnemental, Plein Pot, Appel à Communs Green-Score des recettes
- Hyper Open X (France 2030 / Bpifrance, horizontal scaling & MariaDB)
- FOODTURE (Horizon Europe, LCA and environmental quantification)
- Envol Vert (Empreinte Forêt / imported deforestation)
- Modern, accessible, bilingual (EN/FR) responsive layout
"""

def build_partners_html(lang="en"):
    is_fr = (lang == "fr")

    # Titles and labels
    hero_eyebrow = "🤝 ALLIANCES & PARTENARIATS INSTITUTIONNELS" if is_fr else "🤝 INSTITUTIONAL ALLIANCES & PARTNERSHIPS"
    hero_title = "Partenaires d'Open Food Facts" if is_fr else "Partners of Open Food Facts"
    hero_subtitle = "Construire ensemble les communs de la transparence alimentaire" if is_fr else "Building the Global Food Transparency Commons Together"
    hero_lead = (
        "Open Food Facts est un bien commun numérique d'intérêt général, bâti par des dizaines de milliers de citoyens bénévoles. "
        "Nous collaborons avec des agences publiques, des laboratoires de recherche scientifique, des fondations philanthropiques et des pionniers du logiciel libre "
        "pour faire progresser la transparence alimentaire, la santé planétaire et le pouvoir d'agir des consommateurs dans le monde entier."
        if is_fr else
        "Open Food Facts is an independent, non-profit digital public good built by tens of thousands of volunteer citizens. "
        "We collaborate with public agencies, scientific research institutes, philanthropic foundations, and open-source pioneers "
        "to advance food transparency, planetary health, and citizen empowerment across the world."
    )

    return f"""<!-- main column content - comment used to remove left column and center content on some pages -->
<style>
:root {{
  --off-espresso: #341100;
  --off-espresso-mid: #473526;
  --off-cream: #f9f8f6;
  --off-peach-tint: #ece0db;
  --off-orange: #ed8857;
  --off-orange-hover: #d77243;
  --off-green: #209552;
  --off-green-light: #e8f5e9;
  --off-green-dark: #1b5e20;
  --off-blue: #1976d2;
  --off-blue-light: #eff6ff;
  --off-purple: #7c3aed;
  --off-purple-light: #f5f3ff;
  --off-border: #e2e8f0;
  --off-surface: #ffffff;
  --off-text-muted: #64748b;
  --off-radius-pill: 999px;
  --off-radius-card: 18px;
  --off-shadow-sm: 0 4px 14px rgba(52, 17, 0, 0.05);
  --off-shadow-md: 0 10px 28px rgba(52, 17, 0, 0.08);
  --off-shadow-hover: 0 16px 36px rgba(52, 17, 0, 0.12);
}}

.off-partners-wrap {{
  font-family: "Plus Jakarta Sans", "Open Sans", -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
  color: var(--off-espresso);
  max-width: 1240px;
  margin: 0 auto 3.5rem auto;
  padding: 0 1rem;
  line-height: 1.6;
  box-sizing: border-box;
}}

.off-partners-wrap *,
.off-partners-wrap *::before,
.off-partners-wrap *::after {{
  box-sizing: border-box;
}}

/* Hero Section */
.off-partners-hero {{
  background: linear-gradient(180deg, #ffffff 0%, var(--off-cream) 100%);
  border: 1px solid var(--off-peach-tint);
  border-radius: 28px;
  padding: clamp(2rem, 4.5vw, 3.5rem);
  margin: 1.5rem 0 2.5rem 0;
  box-shadow: 0 12px 36px rgba(52, 17, 0, 0.06);
  text-align: center;
  position: relative;
  overflow: hidden;
}}

.off-partners-hero::before {{
  content: "";
  position: absolute;
  top: -80px;
  right: -80px;
  width: 240px;
  height: 240px;
  background: radial-gradient(circle, rgba(32, 149, 82, 0.15) 0%, rgba(32, 149, 82, 0) 70%);
  border-radius: 50%;
  pointer-events: none;
}}

.off-partners-eyebrow {{
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  background: var(--off-espresso-mid);
  color: #ffffff;
  font-size: 0.82rem;
  font-weight: 700;
  padding: 0.45rem 1.15rem;
  border-radius: var(--off-radius-pill);
  letter-spacing: 0.04em;
  margin-bottom: 1.25rem;
  text-transform: uppercase;
}}

.off-partners-hero h1 {{
  font-size: clamp(2.2rem, 4.5vw, 3.4rem);
  font-weight: 900;
  letter-spacing: -0.025em;
  color: var(--off-espresso);
  margin: 0 0 0.75rem 0;
  line-height: 1.15;
}}

.off-partners-hero .off-subtitle {{
  font-size: clamp(1.15rem, 2vw, 1.45rem);
  font-weight: 600;
  color: var(--off-orange);
  margin: 0 auto 1.25rem auto;
  max-width: 820px;
  line-height: 1.35;
}}

.off-partners-hero p.lead {{
  font-size: 1.05rem;
  color: var(--off-espresso-mid);
  max-width: 860px;
  margin: 0 auto 2rem auto;
  line-height: 1.65;
}}

/* Impact Numbers */
.off-partners-stats {{
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
  gap: 1.25rem;
  margin: 2rem 0;
}}

.off-stat-card {{
  background: #ffffff;
  border: 1px solid var(--off-peach-tint);
  border-radius: 16px;
  padding: 1.25rem 1rem;
  box-shadow: var(--off-shadow-sm);
  transition: transform 0.2s ease, box-shadow 0.2s ease;
}}

.off-stat-card:hover {{
  transform: translateY(-2px);
  box-shadow: var(--off-shadow-md);
}}

.off-stat-num {{
  font-size: clamp(1.6rem, 2.3vw, 2.1rem);
  font-weight: 800;
  color: var(--off-green);
  line-height: 1.1;
  margin-bottom: 0.25rem;
}}

.off-stat-lbl {{
  font-size: 0.82rem;
  font-weight: 600;
  color: var(--off-espresso-mid);
  text-transform: uppercase;
  letter-spacing: 0.03em;
}}

/* Action Buttons Strip */
.off-partners-actions {{
  display: flex;
  flex-wrap: wrap;
  justify-content: center;
  gap: 0.85rem;
  margin-top: 1rem;
}}

.off-btn {{
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  padding: 0.7rem 1.35rem;
  border-radius: var(--off-radius-pill);
  font-size: 0.92rem;
  font-weight: 700;
  text-decoration: none;
  transition: all 0.2s ease;
  cursor: pointer;
  border: 1px solid transparent;
}}

.off-btn-primary {{
  background: #209552;
  color: #ffffff !important;
  box-shadow: 0 4px 12px rgba(32, 149, 82, 0.25);
}}

.off-btn-primary:hover {{
  background: #1b5e20;
  transform: translateY(-1px);
  color: #ffffff !important;
}}

.off-btn-secondary {{
  background: var(--off-espresso);
  color: #ffffff !important;
}}

.off-btn-secondary:hover {{
  background: var(--off-espresso-mid);
  transform: translateY(-1px);
  color: #ffffff !important;
}}

.off-btn-outline {{
  background: #ffffff;
  color: var(--off-espresso) !important;
  border-color: var(--off-peach-tint);
  box-shadow: var(--off-shadow-sm);
}}

.off-btn-outline:hover {{
  border-color: var(--off-orange);
  color: var(--off-orange) !important;
  background: #fff8f4;
  transform: translateY(-1px);
}}

/* Section Headers */
.off-section {{
  margin-bottom: 3.5rem;
}}

.off-section-header {{
  margin-bottom: 1.75rem;
  border-bottom: 2px solid var(--off-peach-tint);
  padding-bottom: 0.85rem;
}}

.off-section-badge {{
  display: inline-block;
  background: var(--off-peach-tint);
  color: var(--off-espresso);
  font-size: 0.78rem;
  font-weight: 700;
  padding: 0.25rem 0.75rem;
  border-radius: var(--off-radius-pill);
  text-transform: uppercase;
  letter-spacing: 0.04em;
  margin-bottom: 0.5rem;
}}

.off-section-header h2 {{
  font-size: clamp(1.6rem, 2.7vw, 2.2rem);
  font-weight: 800;
  letter-spacing: -0.02em;
  color: var(--off-espresso);
  margin: 0.25rem 0 0.5rem 0;
}}

.off-section-header p {{
  font-size: 1rem;
  color: var(--off-espresso-mid);
  max-width: 820px;
  margin: 0;
}}

/* Independence Charter Box */
.off-charter-grid {{
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(320px, 1fr));
  gap: 1.5rem;
  margin-top: 1.5rem;
}}

.off-charter-card {{
  background: #ffffff;
  border-radius: var(--off-radius-card);
  padding: 1.75rem;
  border: 1px solid var(--off-peach-tint);
  box-shadow: var(--off-shadow-sm);
  display: flex;
  flex-direction: column;
  justify-content: space-between;
}}

.off-charter-card h3 {{
  font-size: 1.25rem;
  font-weight: 800;
  color: var(--off-espresso);
  margin: 0 0 0.75rem 0;
  display: flex;
  align-items: center;
  gap: 0.5rem;
}}

.off-charter-card p {{
  font-size: 0.95rem;
  color: var(--off-espresso-mid);
  line-height: 1.6;
  margin: 0 0 1rem 0;
}}

.off-charter-independent {{
  border-left: 5px solid #f97316;
}}

.off-charter-funding {{
  border-left: 5px solid var(--off-green);
}}

/* Search & Filter Bar */
.off-filter-container {{
  background: var(--off-cream);
  border: 1px solid var(--off-peach-tint);
  border-radius: 18px;
  padding: 1.25rem;
  margin-bottom: 2rem;
  display: flex;
  flex-direction: column;
  gap: 1rem;
}}

.off-search-input-wrap {{
  position: relative;
  width: 100%;
}}

.off-search-input {{
  width: 100%;
  padding: 0.85rem 1rem 0.85rem 2.85rem;
  border-radius: 12px;
  border: 1px solid var(--off-border);
  font-size: 0.95rem;
  color: var(--off-espresso);
  background: #ffffff;
  outline: none;
  transition: border-color 0.2s ease, box-shadow 0.2s ease;
}}

.off-search-input:focus {{
  border-color: var(--off-green);
  box-shadow: 0 0 0 3px rgba(32, 149, 82, 0.15);
}}

.off-search-icon {{
  position: absolute;
  left: 1rem;
  top: 50%;
  transform: translateY(-50%);
  color: var(--off-text-muted);
  pointer-events: none;
}}

.off-chips-row {{
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
  justify-content: center;
}}

.off-chip-btn {{
  padding: 0.45rem 1.1rem;
  border-radius: var(--off-radius-pill);
  border: 1px solid var(--off-border);
  background: #ffffff;
  color: var(--off-espresso-mid);
  font-size: 0.88rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s ease;
}}

.off-chip-btn:hover,
.off-chip-btn.active {{
  background: var(--off-espresso);
  color: #ffffff;
  border-color: var(--off-espresso);
}}

/* Subsection Dividers */
.off-subsection-heading {{
  display: flex;
  align-items: center;
  justify-content: space-between;
  flex-wrap: wrap;
  gap: 0.5rem;
  margin: 2.5rem 0 1.25rem 0;
  padding-bottom: 0.5rem;
  border-bottom: 2px solid var(--off-peach-tint);
}}

.off-subsection-heading h3 {{
  font-size: 1.35rem;
  font-weight: 800;
  color: var(--off-espresso);
  margin: 0;
  display: flex;
  align-items: center;
  gap: 0.5rem;
}}

.off-subsection-tag {{
  font-size: 0.82rem;
  font-weight: 700;
  color: var(--off-green-dark);
  background: var(--off-green-light);
  padding: 0.25rem 0.75rem;
  border-radius: var(--off-radius-pill);
}}

/* Partners Grid */
.off-partners-grid {{
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(320px, 1fr));
  gap: 1.5rem;
}}

.off-partner-card {{
  background: var(--off-surface);
  border: 1px solid var(--off-peach-tint);
  border-radius: var(--off-radius-card);
  padding: 1.6rem;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  box-shadow: var(--off-shadow-sm);
  transition: all 0.25s ease;
  position: relative;
}}

.off-partner-card:hover {{
  transform: translateY(-3px);
  box-shadow: var(--off-shadow-hover);
  border-color: var(--off-green);
}}

/* Wide card for comprehensive sections like EU / NLnet */
@media (min-width: 900px) {{
  .off-partner-card-wide {{
    grid-column: 1 / -1;
  }}
}}

/* Special CTA Card to lightly incentivize new partners */
.off-partner-card-cta {{
  background: linear-gradient(145deg, #ffffff 0%, var(--off-green-light) 100%);
  border: 2px dashed var(--off-green);
  text-align: center;
  align-items: center;
  justify-content: center;
  padding: 2rem 1.5rem;
}}

.off-partner-card-cta:hover {{
  border-color: var(--off-green-dark);
  box-shadow: 0 10px 24px rgba(32, 149, 82, 0.15);
}}

.off-partner-logo-box {{
  height: 90px;
  background: var(--off-cream);
  border: 1px solid var(--off-peach-tint);
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 0.85rem;
  margin-bottom: 1.25rem;
  overflow: hidden;
}}

.off-partner-logo-box img {{
  max-height: 100%;
  max-width: 100%;
  object-fit: contain;
  transition: transform 0.2s ease;
}}

.off-partner-card:hover .off-partner-logo-box img {{
  transform: scale(1.05);
}}

.off-partner-badge {{
  display: inline-block;
  background: var(--off-peach-tint);
  color: var(--off-espresso-mid);
  font-size: 0.74rem;
  font-weight: 700;
  padding: 0.2rem 0.65rem;
  border-radius: var(--off-radius-pill);
  text-transform: uppercase;
  letter-spacing: 0.03em;
  margin-bottom: 0.6rem;
}}

.off-partner-badge-active {{
  background: var(--off-green-light);
  color: var(--off-green-dark);
  border: 1px solid rgba(32, 149, 82, 0.25);
}}

.off-partner-badge-historic {{
  background: #f1f5f9;
  color: #475569;
  border: 1px solid #cbd5e1;
}}

.off-partner-name {{
  font-size: 1.22rem;
  font-weight: 800;
  color: var(--off-espresso);
  margin: 0 0 0.35rem 0;
}}

.off-partner-date-tag {{
  display: inline-flex;
  align-items: center;
  gap: 4px;
  background: var(--off-cream);
  border: 1px solid var(--off-border);
  color: var(--off-espresso);
  font-size: 0.76rem;
  font-weight: 700;
  padding: 0.2rem 0.55rem;
  border-radius: var(--off-radius-pill);
  margin-bottom: 0.75rem;
}}

.off-partner-desc {{
  font-size: 0.92rem;
  color: var(--off-espresso-mid);
  line-height: 1.6;
  margin-bottom: 1rem;
}}

.off-partner-milestone {{
  background: var(--off-cream);
  border-left: 3px solid var(--off-green);
  border-radius: 0 8px 8px 0;
  padding: 0.6rem 0.85rem;
  font-size: 0.84rem;
  color: var(--off-espresso-mid);
  margin-bottom: 0.75rem;
}}

.off-partner-milestone b {{
  color: var(--off-espresso);
}}

.off-partner-milestone a {{
  color: var(--off-green-dark);
  font-weight: 600;
  text-decoration: underline;
}}

.off-partner-footer {{
  border-top: 1px solid var(--off-border);
  padding-top: 0.85rem;
  display: flex;
  align-items: center;
  justify-content: space-between;
}}

.off-partner-link {{
  display: inline-flex;
  align-items: center;
  gap: 5px;
  font-size: 0.88rem;
  font-weight: 700;
  color: var(--off-green-dark);
  text-decoration: none;
}}

.off-partner-link:hover {{
  color: var(--off-green);
  text-decoration: underline;
}}

/* NLnet Projects Sub-Grid */
.off-nlnet-projects-grid {{
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: 1rem;
  margin: 1.25rem 0;
}}

.off-nlnet-project-item {{
  background: var(--off-cream);
  border: 1px solid var(--off-peach-tint);
  border-radius: 12px;
  padding: 1.1rem;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  transition: all 0.2s ease;
}}

.off-nlnet-project-item:hover {{
  border-color: var(--off-green);
  background: #ffffff;
  box-shadow: 0 6px 16px rgba(52, 17, 0, 0.06);
}}

.off-nlnet-meta {{
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 6px;
  margin-bottom: 0.5rem;
}}

.off-nlnet-date-badge {{
  background: var(--off-espresso);
  color: #ffffff;
  font-size: 0.72rem;
  font-weight: 700;
  padding: 0.15rem 0.55rem;
  border-radius: var(--off-radius-pill);
}}

.off-nlnet-fund-badge {{
  background: var(--off-blue-light);
  color: var(--off-blue);
  font-size: 0.72rem;
  font-weight: 700;
  padding: 0.15rem 0.55rem;
  border-radius: var(--off-radius-pill);
  border: 1px solid rgba(25, 118, 210, 0.2);
}}

.off-nlnet-item-title {{
  font-size: 0.98rem;
  font-weight: 800;
  color: var(--off-espresso);
  margin: 0 0 0.4rem 0;
  line-height: 1.3;
}}

.off-nlnet-item-desc {{
  font-size: 0.84rem;
  color: var(--off-espresso-mid);
  line-height: 1.5;
  margin-bottom: 0.85rem;
  flex-grow: 1;
}}

.off-nlnet-item-link {{
  font-size: 0.82rem;
  font-weight: 700;
  color: var(--off-green-dark);
  text-decoration: none;
  display: inline-flex;
  align-items: center;
  gap: 4px;
}}

.off-nlnet-item-link:hover {{
  text-decoration: underline;
  color: var(--off-green);
}}

/* Donors & Community Banner */
.off-donors-banner {{
  background: linear-gradient(135deg, var(--off-espresso) 0%, #473526 100%);
  color: #ffffff;
  border-radius: 24px;
  padding: clamp(2rem, 3.8vw, 3rem);
  text-align: center;
  box-shadow: var(--off-shadow-md);
  margin: 3.5rem 0 2.5rem 0;
}}

.off-donors-banner h3 {{
  font-size: clamp(1.5rem, 2.5vw, 2.1rem);
  font-weight: 800;
  color: #ffffff;
  margin: 0 0 0.75rem 0;
}}

.off-donors-banner p {{
  font-size: 1.05rem;
  color: var(--off-peach-tint);
  max-width: 760px;
  margin: 0 auto 1.75rem auto;
  line-height: 1.6;
}}

/* Contact Partnership Box */
.off-contact-alliance-box {{
  background: var(--off-cream);
  border: 2px dashed var(--off-green);
  border-radius: 20px;
  padding: 2.25rem 2rem;
  margin: 2.5rem 0;
  text-align: center;
}}

.off-contact-alliance-box h3 {{
  font-size: 1.45rem;
  font-weight: 800;
  color: var(--off-espresso);
  margin: 0 0 0.6rem 0;
}}

.off-contact-alliance-box p {{
  font-size: 1rem;
  color: var(--off-espresso-mid);
  max-width: 700px;
  margin: 0 auto 1.5rem auto;
  line-height: 1.6;
}}

.off-fundraising-highlight {{
  background: #ffffff;
  display: inline-block;
  padding: 0.5rem 1.25rem;
  border-radius: var(--off-radius-pill);
  border: 1px solid var(--off-peach-tint);
  font-size: 0.95rem;
  color: var(--off-espresso);
  margin-bottom: 1.25rem;
}}

.off-fundraising-highlight b {{
  color: var(--off-green-dark);
}}
</style>

<div class="off-partners-wrap" id="partners-page">

  <!-- HERO SECTION -->
  <div class="off-partners-hero">
    <div class="off-partners-eyebrow">{hero_eyebrow}</div>
    <h1>{hero_title}</h1>
    <h2 class="off-subtitle">{hero_subtitle}</h2>
    <p class="lead">{hero_lead}</p>

    <!-- Stats strip -->
    <div class="off-partners-stats">
      <div class="off-stat-card">
        <div class="off-stat-num">100%</div>
        <div class="off-stat-lbl">{"Indépendant de l'industrie" if is_fr else "Independent of Industry"}</div>
      </div>
      <div class="off-stat-card">
        <div class="off-stat-num">1 000+</div>
        <div class="off-stat-lbl">{"Études scientifiques" if is_fr else "Scientific Studies"}</div>
      </div>
      <div class="off-stat-card">
        <div class="off-stat-num">200+</div>
        <div class="off-stat-lbl">{"Applications & réutilisations" if is_fr else "Ecosystem Reuses"}</div>
      </div>
      <div class="off-stat-card">
        <div class="off-stat-num">5 000+</div>
        <div class="off-stat-lbl">{"Citoyens donateurs" if is_fr else "Citizen Donors"}</div>
      </div>
    </div>

    <!-- Action Buttons -->
    <div class="off-partners-actions">
      <a class="off-btn off-btn-primary" href="#partner-directory">
        <span>✨</span> {"Partenariats actifs & Projets en cours" if is_fr else "Active Partnerships & Ongoing Projects"}
      </a>
      <a class="off-btn off-btn-secondary" href="#charter">
        <span>🛡️</span> {"Notre charte d'indépendance" if is_fr else "Independence Charter"}
      </a>
      <a class="off-btn off-btn-outline" href="/donors">
        <span>🏆</span> {"Mur des donateurs citoyens" if is_fr else "Donors Wall & Hall of Fame"}
      </a>
      <a class="off-btn off-btn-outline" href="mailto:fundraising@openfoodfacts.org?subject=Partenariat%20ou%20M%C3%A9c%C3%A9nat%20Open%20Food%20Facts">
        <span>✉️</span> {"Mécénat & Alliances (fundraising@)" if is_fr else "Partner or Fund our Commons (fundraising@)"}
      </a>
    </div>
  </div>

  <!-- CHARTER & ETHICS SECTION -->
  <div class="off-section" id="charter">
    <div class="off-section-header">
      <span class="off-section-badge">{"Éthique & Indépendance" if is_fr else "Ethics & Independence"}</span>
      <h2>{"Une indépendance absolue au service de la confiance" if is_fr else "Uncompromising Independence as a Foundation of Trust"}</h2>
      <p>{"Pourquoi les citoyens, les scientifiques et les pouvoirs publics nous font-ils confiance ? Voici notre politique de financement et d'intégrité." if is_fr else "Why do citizens, scientists, and regulators trust Open Food Facts? Here is our clear framework for independence and funding integrity."}</p>
    </div>

    <div class="off-charter-grid">
      <!-- Independence Card -->
      <div class="off-charter-card off-charter-independent">
        <div>
          <h3><span>🛡️</span> {"Indépendance stricte vis-à-vis de l'industrie" if is_fr else "Strict Independence from the Food Industry"}</h3>
          <p>
            {"Open Food Facts n'accepte aucun soutien financier, sponsoring ou participation d'entreprises ou de fondations liées à l'industrie agroalimentaire. Cette règle est non négociable." if is_fr else "Open Food Facts does not accept any financial support, sponsorship, or governance participation from food corporations, agribusinesses, or retail conglomerates. This principle is strictly non-negotiable."}
          </p>
          <p>
            {"Cette étanchéité garantit une neutralité totale : nos calculs du Nutri-Score, du Green-Score et de NOVA sont 100 % impartiaux et protégés des pressions de lobbying." if is_fr else "This complete firewall ensures total objectivity: our algorithmic calculations for Nutri-Score, Green-Score, and NOVA are 100% impartial and insulated from corporate lobbying."}
          </p>
        </div>
        <div>
          <a class="off-btn off-btn-outline" href="/producers" style="width: 100%; text-align: center; border-color: #f97316; color: #c2410c !important;">
            {"Collaboration producteurs : données ouvertes gratuites" if is_fr else "Producer Collaboration: 100% Free Open Data"} →
          </a>
        </div>
      </div>

      <!-- Funding Card -->
      <div class="off-charter-card off-charter-funding">
        <div>
          <h3><span>⚖️</span> {"Subventions de projets vs Financement des communs" if is_fr else "Project Grants vs. Commons Infrastructure"}</h3>
          <p>
            {"Nos subventions publiques et philanthropiques (Google.org, Union Européenne / NLnet, Santé publique France, ADEME, France 2030, Fondation Afnic) financent des sauts technologiques précis (application mobile, Green-Score, moteur de recherche, base de prix, défragmentation de données, scalabilité)." if is_fr else "Targeted public and philanthropic grants (Google.org, European Commission / NLnet, Santé publique France, ADEME, France 2030, Afnic Foundation) fund specific technological breakthroughs (mobile app, Green-Score, search engine, crowdsourced prices, data defragmentation, horizontal scaling)."}
          </p>
          <p>
            {"En revanche, la colonne vertébrale du projet (serveurs, maintenance, bases de données, équipe permanente) repose sur les micro-dons citoyens sans restriction. Les dons individuels garantissent notre liberté quotidienne." if is_fr else "However, the vital spine of the project (servers, infrastructure, backups, permanent team) relies on unrestricted individual citizen micro-donations. General donations keep our foundation resilient."}
          </p>
        </div>
        <div>
          <a class="off-btn off-btn-outline" href="/donors" style="width: 100%; text-align: center; border-color: #209552; color: #166534 !important;">
            {"Découvrir le mur des donateurs particuliers" if is_fr else "Visit our Donors Wall & Hall of Fame"} →
          </a>
        </div>
      </div>
    </div>
  </div>

  <!-- PARTNER DIRECTORY & FILTER -->
  <div class="off-section" id="partner-directory">
    <div class="off-section-header">
      <span class="off-section-badge">{"Écosystème & Alliances" if is_fr else "Ecosystem & Alliances"}</span>
      <h2>{"Nos soutiens institutionnels, scientifiques et techniques" if is_fr else "Our Institutional, Scientific & Technical Partners"}</h2>
      <p>{"Découvrez nos partenariats en cours et les soutiens historiques qui ont façonné ce commun numérique mondial." if is_fr else "Discover our ongoing partnerships and historic milestones that shaped this global digital commons."}</p>
    </div>

    <!-- Search & Chips Filter -->
    <div class="off-filter-container">
      <div class="off-search-input-wrap">
        <span class="off-search-icon">🔍</span>
        <input type="text" id="partnerSearch" class="off-search-input" placeholder="{"Rechercher par nom, programme, mot-clé (ex: Nutri-Score, NGI, NLnet, ADEME, AIC, Envol Vert, Hyper Open X, FOODTURE)..." if is_fr else "Search by name, program, keyword (e.g. Nutri-Score, NGI, NLnet, ADEME, AIC, Envol Vert, Hyper Open X, FOODTURE)..."}" oninput="filterPartners()">
      </div>

      <div class="off-chips-row">
        <button class="off-chip-btn active" onclick="setCategory('all', this)">{"⭐ Tous les partenaires" if is_fr else "⭐ All Partners"}</button>
        <button class="off-chip-btn" onclick="setCategory('active', this)">🔥 {"Partenariats actifs" if is_fr else "Active Partnerships"}</button>
        <button class="off-chip-btn" onclick="setCategory('public', this)">🏛️ {"Institutions publiques & UE" if is_fr else "Public Agencies & EU"}</button>
        <button class="off-chip-btn" onclick="setCategory('science', this)">🎓 {"Recherche scientifique" if is_fr else "Scientific Research"}</button>
        <button class="off-chip-btn" onclick="setCategory('philanthropy', this)">🌍 {"Fondations philanthropiques" if is_fr else "Philanthropic Foundations"}</button>
        <button class="off-chip-btn" onclick="setCategory('tech', this)">💻 {"Hébergement & Tech libre" if is_fr else "Tech & Hosting"}</button>
        <button class="off-chip-btn" onclick="setCategory('historic', this)">📜 {"Soutiens historiques" if is_fr else "Milestone Grants"}</button>
      </div>
    </div>

    <!-- SECTION 1: ACTIVE PARTNERSHIPS (ON TOP) -->
    <div class="off-subsection-heading">
      <h3><span>🔥</span> {"Partenariats actifs & Projets en cours" if is_fr else "Active Partnerships & Ongoing Initiatives"}</h3>
      <span class="off-subsection-tag">{"Programmes & Projets en direct" if is_fr else "Current & Live Alliances"}</span>
    </div>

    <div class="off-partners-grid" id="partnersGridActive">

      <!-- ======================================================== -->
      <!-- 1. European Union - NGI & NLnet (WIDE CARD - 6 PROJECTS) -->
      <!-- ======================================================== -->
      <div class="off-partner-card off-partner-card-wide" data-category="public active" data-keywords="european union ue commission europeenne ngi nlnet next generation internet personal food facts folksonomy pomme d api open everything facts open prices explorer 2019 2020 2022 2024 2025 2026 active">
        <div>
          <div class="off-partner-logo-box" style="gap: 18px; height: 100px;">
            <img src="https://static.openfoodfacts.org/images/partner_logos/NGI.png" alt="NGI Next Generation Internet" style="max-height: 52px;">
            <img src="https://static.openfoodfacts.org/images/misc/nlnet_logo.svg" alt="NLnet Foundation" style="max-height: 48px;">
            <img src="https://static.openfoodfacts.org/images/misc/eucommission_logo.svg" alt="European Commission" style="max-height: 46px;">
          </div>
          <span class="off-partner-badge off-partner-badge-active">{"Partenariat actif • 6 Projets financés" if is_fr else "Active Alliance • 6 Funded Projects"}</span>
          <div style="display: flex; flex-wrap: wrap; align-items: baseline; gap: 8px; margin-bottom: 0.35rem;">
            <h3 class="off-partner-name" style="margin: 0;">{"Union Européenne (NGI) & Fondation NLnet" if is_fr else "European Union (NGI) & NLnet Foundation"}</h3>
            <span class="off-partner-date-tag">🗓️ 2019 – {"Présent" if is_fr else "Present"}</span>
          </div>
          <p class="off-partner-desc">
            {"La Commission Européenne (à travers son initiative Next Generation Internet - NGI) et la prestigieuse Fondation néerlandaise NLnet soutiennent en continu les briques technologiques clés d'Open Food Facts pour bâtir un Internet souverain, respectueux de la vie privée et accessible à tous :" if is_fr else "The European Commission (through the Next Generation Internet - NGI initiative) and the renowned NLnet Foundation fund Open Food Facts across 6 strategic milestones to build a privacy-first, sovereign, and human-centric digital commons:"}
          </p>

          <!-- 6 NLnet Projects Sub-Grid -->
          <div class="off-nlnet-projects-grid">

            <!-- 1. Personal Food Facts -->
            <div class="off-nlnet-project-item">
              <div>
                <div class="off-nlnet-meta">
                  <span class="off-nlnet-date-badge">12/2019</span>
                  <span class="off-nlnet-fund-badge">NGI0 Discovery</span>
                </div>
                <h4 class="off-nlnet-item-title">Personal Food Facts</h4>
                <p class="off-nlnet-item-desc">
                  {"Personnalisation alimentaire et alertes nutritionnelles/allergènes exécutées en local sur l'appareil pour protéger l'intimité médicale des citoyens sans fuite vers des tiers." if is_fr else "Privacy-protecting personalized search & dietary alerts computed locally on-device without leaking sensitive health or allergen data to third parties."}
                </p>
              </div>
              <div>
                <a class="off-nlnet-item-link" href="https://nlnet.nl/project/OpenFoodFacts/" target="_blank" rel="noopener noreferrer">
                  nlnet.nl/project/OpenFoodFacts ↗
                </a>
              </div>
            </div>

            <!-- 2. Folksonomy Engine -->
            <div class="off-nlnet-project-item">
              <div>
                <div class="off-nlnet-meta">
                  <span class="off-nlnet-date-badge">10/2020 – 05/2022</span>
                  <span class="off-nlnet-fund-badge">NGI0 Discovery</span>
                </div>
                <h4 class="off-nlnet-item-title">Folksonomy Engine for Food</h4>
                <p class="off-nlnet-item-desc">
                  {"Moteur de modélisation collaborative permettant aux citoyens, chercheurs et innovateurs d'ajouter des propriétés libres et personnalisées aux aliments au-delà des taxonomies figées." if is_fr else "Collaborative tagging engine allowing citizens, researchers, and innovators to add flexible, community-defined properties to food items beyond static taxonomies."}
                </p>
              </div>
              <div>
                <a class="off-nlnet-item-link" href="https://nlnet.nl/project/FolksonomyEngine/" target="_blank" rel="noopener noreferrer">
                  nlnet.nl/project/FolksonomyEngine ↗
                </a>
              </div>
            </div>

            <!-- 3. Pomme d’API -->
            <div class="off-nlnet-project-item">
              <div>
                <div class="off-nlnet-meta">
                  <span class="off-nlnet-date-badge">06/2024</span>
                  <span class="off-nlnet-fund-badge">NGI0 Commons Fund</span>
                </div>
                <h4 class="off-nlnet-item-title">Pomme d’API</h4>
                <p class="off-nlnet-item-desc">
                  {"Modernisation majeure de l'API Open Food Facts : spécifications OpenAPI, documentation interactive enrichie et accélération des échanges pour les 250+ applications de l'écosystème." if is_fr else "Major modernization of the Open Food Facts API: OpenAPI specifications, structured schemas, interactive documentation, and streamlined tools for 250+ ecosystem apps."}
                </p>
              </div>
              <div>
                <a class="off-nlnet-item-link" href="https://nlnet.nl/project/Pomme-dAPI/" target="_blank" rel="noopener noreferrer">
                  nlnet.nl/project/Pomme-dAPI ↗
                </a>
              </div>
            </div>

            <!-- 4. Open Everything Facts -->
            <div class="off-nlnet-project-item">
              <div>
                <div class="off-nlnet-meta">
                  <span class="off-nlnet-date-badge">06/2024</span>
                  <span class="off-nlnet-fund-badge">NGI0 Commons Fund</span>
                </div>
                <h4 class="off-nlnet-item-title">Open Everything Facts</h4>
                <p class="off-nlnet-item-desc">
                  {"Extension du modèle des communs au-delà de l'alimentation à tous les produits manufacturés dotés d'un code-barres (cosmétiques, animalerie, électroménager) pour éclairer les choix de consommation." if is_fr else "Extending the open commons beyond food to empower informed consumer choices on all barcoded consumer goods (cosmetics, pet food, home products)."}
                </p>
              </div>
              <div>
                <a class="off-nlnet-item-link" href="https://nlnet.nl/project/OpenEverythingFacts/" target="_blank" rel="noopener noreferrer">
                  nlnet.nl/project/OpenEverythingFacts ↗
                </a>
              </div>
            </div>

            <!-- 5. Open Prices -->
            <div class="off-nlnet-project-item">
              <div>
                <div class="off-nlnet-meta">
                  <span class="off-nlnet-date-badge">06/2025</span>
                  <span class="off-nlnet-fund-badge">NGI0 Commons Fund</span>
                </div>
                <h4 class="off-nlnet-item-title">Open Prices - Scaling Price Collection</h4>
                <p class="off-nlnet-item-desc">
                  {"Première base ouverte mondiale des prix collectés par crowdsourcing : modèles d'IA et de vision pour extraire prix et codes-barres sur les étiquettes de rayon et modération communautaire." if is_fr else "World's first crowdsourced open price database: machine learning tools to extract prices and barcodes from store shelf photos, validation pipelines, and community moderation."}
                </p>
              </div>
              <div>
                <a class="off-nlnet-item-link" href="https://nlnet.nl/project/OpenPrices/" target="_blank" rel="noopener noreferrer">
                  nlnet.nl/project/OpenPrices ↗
                </a>
              </div>
            </div>

            <!-- 6. Open Food Facts Explorer -->
            <div class="off-nlnet-project-item">
              <div>
                <div class="off-nlnet-meta">
                  <span class="off-nlnet-date-badge">06/2026</span>
                  <span class="off-nlnet-fund-badge">NGI0 Commons Fund</span>
                </div>
                <h4 class="off-nlnet-item-title">Open Food Facts Explorer</h4>
                <p class="off-nlnet-item-desc">
                  {"Nouveau frontend web moderne, accessible et ultra-rapide en SvelteKit pour Open Food Facts, découplant l'interface du backend historique pour faciliter les contributions des développeurs." if is_fr else "Modern, blazing-fast web frontend built in SvelteKit, decoupling the presentation layer from the legacy backend to boost sustainability and community developer contributions."}
                </p>
              </div>
              <div>
                <a class="off-nlnet-item-link" href="https://nlnet.nl/project/OFF-Explorer/" target="_blank" rel="noopener noreferrer">
                  nlnet.nl/project/OFF-Explorer ↗
                </a>
              </div>
            </div>

          </div>
        </div>
        <div class="off-partner-footer" style="padding-top: 1rem;">
          <a class="off-partner-link" href="https://nlnet.nl/search/static.html?q=open+food+facts&submit=Search" target="_blank" rel="noopener noreferrer">
            🔍 {"Voir la liste complète des 6 projets Open Food Facts sur le site NLnet" if is_fr else "View complete list of 6 Open Food Facts projects on NLnet"} ↗
          </a>
          <span style="font-size: 0.84rem; color: var(--off-espresso-mid);">{"Soutenu par le programme Horizon Europe de l'UE" if is_fr else "Supported by EU Horizon Europe programme"}</span>
        </div>
      </div>

      <!-- ======================================================== -->
      <!-- 2. ADEME (3 Key Projects) -->
      <!-- ======================================================== -->
      <div class="off-partner-card" data-category="public active" data-keywords="ademe agribalyse environnement acv analyse cycle de vie green-score ecoscore transition ecologique plein pot emballages appel a communs recettes cout environnemental 2020 2023 2025 2026 active">
        <div>
          <div class="off-partner-logo-box">
            <img src="https://static.openfoodfacts.org/images/misc/ADEME-logo.svg" alt="ADEME">
          </div>
          <span class="off-partner-badge off-partner-badge-active">{"Partenaire actif • 3 Programmes majeurs" if is_fr else "Active Partner • 3 Major Programmes"}</span>
          <div style="display: flex; flex-wrap: wrap; align-items: baseline; gap: 8px;">
            <h3 class="off-partner-name">ADEME</h3>
            <span class="off-partner-date-tag">🗓️ 2020 – {"Présent" if is_fr else "Present"}</span>
          </div>
          <p class="off-partner-desc">
            {"L'Agence de la transition écologique collabore activement avec Open Food Facts autour de plusieurs projets structurants pour accélérer la transparence environnementale :" if is_fr else "The French Agency for Ecological Transition collaborates actively with Open Food Facts across multiple core initiatives to advance environmental transparency:"}
          </p>
          <div class="off-partner-milestone" style="margin-bottom: 0.5rem;">
            <b>{"Agribalyse & Coût environnemental :" if is_fr else "Agribalyse & Environmental Cost:"}</b> {"Intégration des données d'Analyse du Cycle de Vie (ACV) d'Agribalyse pour calculer le Green-Score et modéliser le coût écologique réel des produits en amont de l'affichage environnemental officiel." if is_fr else "Integrating Agribalyse Life Cycle Assessment (LCA) data to compute the Green-Score and model the true ecological cost of food in support of official environmental labeling."}
          </div>
          <div class="off-partner-milestone" style="margin-bottom: 0.5rem;">
            <b>{"Plein Pot sur les Emballages (2023) :" if is_fr else "Plein Pot sur les Emballages (2023):"}</b> {"Opération de science participative soutenue par l'ADEME ayant documenté les matériaux, poids et recyclabilité sur plus de 10 000 emballages pour lutter contre le suremballage." if is_fr else "Participatory citizen-science campaign funded by ADEME documenting packaging materials, weights, and recyclability on 10,000+ products to fight overpackaging."}
          </div>
          <div class="off-partner-milestone" style="margin-bottom: 0.5rem;">
            <b>{"Appel à Communs (2025-2026) :" if is_fr else "Appel à Communs (2025-2026):"}</b> {"Sélection d'Open Food Facts comme commun numérique lauréat pour développer le Green-Score des recettes de cuisine et de la restauration collective." if is_fr else "Laureate of ADEME's Open Commons Call to extend the Green-Score calculation to cooking recipes and collective catering."}
          </div>
        </div>
        <div class="off-partner-footer">
          <a class="off-partner-link" href="https://www.ademe.fr/" target="_blank" rel="noopener noreferrer">
            ademe.fr ↗
          </a>
        </div>
      </div>

      <!-- ======================================================== -->
      <!-- 3. République Française - AIC / DINUM -->
      <!-- ======================================================== -->
      <div class="off-partner-card" data-category="public active" data-keywords="republique francaise dinum aic accelerateur initiatives citoyennes etat gouvernement premier ministre beta gouv communs numeriques 2021 active">
        <div>
          <div class="off-partner-logo-box" style="gap: 14px;">
            <img src="https://static.openfoodfacts.org/images/partner_logos/Republique_Francaise.png" alt="République Française" style="max-height: 56px;">
            <div style="display: flex; flex-direction: column; text-align: left; line-height: 1.15;">
              <span style="font-size: 1.05rem; font-weight: 900; color: #000091; letter-spacing: -0.01em;">DINUM</span>
              <span style="font-size: 0.72rem; font-weight: 700; color: var(--off-text-muted);">Accélérateur d'initiatives citoyennes</span>
            </div>
          </div>
          <span class="off-partner-badge off-partner-badge-active">{"Partenariat actif • Communs de l'État" if is_fr else "Active Alliance • State Digital Commons"}</span>
          <div style="display: flex; flex-wrap: wrap; align-items: baseline; gap: 8px;">
            <h3 class="off-partner-name">{"République Française (DINUM / AIC)" if is_fr else "French Republic (DINUM / AIC)"}</h3>
            <span class="off-partner-date-tag">🗓️ 2021 – {"Présent" if is_fr else "Present"}</span>
          </div>
          <p class="off-partner-desc">
            {"Accompagnement méthodologique, technique, administratif et stratégique par l'Accélérateur d'initiatives citoyennes (AIC) piloté par la Direction Interministérielle du Numérique (DINUM) auprès du Premier ministre. Open Food Facts fait partie des communs numériques d'intérêt général officiellement soutenus par l'État." if is_fr else "Methodological, technical, administrative, and strategic support from the French Government's Citizen Initiative Accelerator (AIC), led by the Interministerial Digital Directorate (DINUM). Open Food Facts is an officially recognized public digital commons laureate."}
          </p>
          <div class="off-partner-milestone">
            <b>Communs numériques (AIC) :</b> <a href="https://communs.beta.gouv.fr/laureats/open-food-facts/" target="_blank" rel="noopener noreferrer">{"Fiche officielle des lauréats sur communs.beta.gouv.fr" if is_fr else "Official AIC Laureate Sheet on communs.beta.gouv.fr"}</a>
          </div>
        </div>
        <div class="off-partner-footer">
          <a class="off-partner-link" href="https://communs.beta.gouv.fr/laureats/open-food-facts/" target="_blank" rel="noopener noreferrer">
            communs.beta.gouv.fr/laureats/open-food-facts ↗
          </a>
        </div>
      </div>

      <!-- ======================================================== -->
      <!-- 4. Santé publique France -->
      <!-- ======================================================== -->
      <div class="off-partner-card" data-category="public active" data-keywords="sante publique france nutriscore nutri-score public health gouvernement nutrition 2018 2014 active">
        <div>
          <div class="off-partner-logo-box">
            <img src="https://static.openfoodfacts.org/images/misc/sante-publique-france-logo.png" alt="Santé publique France">
          </div>
          <span class="off-partner-badge off-partner-badge-active">{"Partenaire actif • Santé Publique" if is_fr else "Active Partner • Public Health"}</span>
          <div style="display: flex; flex-wrap: wrap; align-items: baseline; gap: 8px;">
            <h3 class="off-partner-name">Santé publique France</h3>
            <span class="off-partner-date-tag">🗓️ 2018 – {"Présent" if is_fr else "Present"}</span>
          </div>
          <p class="off-partner-desc">
            {"Partenariat historique débuté dès 2014 pour le calcul pionnier du Nutri-Score et formalisé en 2018. Soutien financier pour le développement de la base de données et de l'application mobile, ainsi que la promotion conjointe de l'ouverture des données nutritionnelles." if is_fr else "Historic collaboration initiated in 2014 for the pioneering computation of Nutri-Score and formalized in 2018. Historical financial support for developing the database and mobile application, jointly championing food data openness."}
          </p>
          <div class="off-partner-milestone">
            <b>06-12-2018 :</b> <a href="https://www.santepubliquefrance.fr/Accueil-Presse/Tous-les-communiques/Sante-publique-France-et-Open-Food-Facts-s-associent-pour-renforcer-l-ouverture-des-donnees-sur-les-produits-alimentaires-et-favoriser-l-utilisation-du-Nutri-Score" target="_blank" rel="noopener noreferrer">{"Accord-cadre officiel Santé publique France & Open Food Facts" if is_fr else "Official Santé publique France & Open Food Facts Alliance"}</a>
          </div>
        </div>
        <div class="off-partner-footer">
          <a class="off-partner-link" href="https://www.santepubliquefrance.fr/" target="_blank" rel="noopener noreferrer">
            santepubliquefrance.fr ↗
          </a>
        </div>
      </div>

      <!-- ======================================================== -->
      <!-- 5. FOODTURE (Horizon Europe) -->
      <!-- ======================================================== -->
      <div class="off-partner-card" data-category="science active" data-keywords="foodture horizon europe acv lca recherche impact environnemental quantification commission europeenne 2023 2027 active">
        <div>
          <div class="off-partner-logo-box" style="gap: 12px;">
            <img src="https://static.openfoodfacts.org/images/misc/eucommission_logo.svg" alt="European Commission" style="max-height: 42px;">
            <span style="font-size: 1.25rem; font-weight: 900; color: #1e3a8a; letter-spacing: -0.01em;">FOOD<span style="color: #209552;">TURE</span></span>
          </div>
          <span class="off-partner-badge off-partner-badge-active">{"Recherche active • Horizon Europe" if is_fr else "Active Research • Horizon Europe"}</span>
          <div style="display: flex; flex-wrap: wrap; align-items: baseline; gap: 8px;">
            <h3 class="off-partner-name">FOODTURE (Horizon Europe)</h3>
            <span class="off-partner-date-tag">🗓️ 2023 – 2027</span>
          </div>
          <p class="off-partner-desc">
            {"Projet de recherche d'envergure financé par le programme Horizon Europe de la Commission Européenne (« Food for the future: Environmental quantification and impact reduction »). Le consortium mobilise l'infrastructure et la base ouverte d'Open Food Facts pour enrichir les méthodologies d'Analyse du Cycle de Vie (ACV), intégrer des inventaires environnementaux à haute résolution et révéler l'impact écologique réel des systèmes alimentaires." if is_fr else "Major research and innovation project funded under the European Commission's Horizon Europe framework ('Food for the future: Environmental quantification and impact reduction'). The consortium leverages Open Food Facts' crowdsourced data infrastructure to upgrade Life Cycle Assessment (LCA) methodologies, incorporate high-resolution inventories, and reveal the true environmental costs of European food supply chains."}
          </p>
          <div class="off-partner-milestone">
            <b>Horizon Europe :</b> <a href="https://foodture-project.eu" target="_blank" rel="noopener noreferrer">{"Consortium européen de recherche FOODTURE" if is_fr else "FOODTURE European Research Consortium"}</a>
          </div>
        </div>
        <div class="off-partner-footer">
          <a class="off-partner-link" href="https://foodture-project.eu" target="_blank" rel="noopener noreferrer">
            foodture-project.eu ↗
          </a>
        </div>
      </div>

      <!-- ======================================================== -->
      <!-- 6. Hyper Open X (France 2030 / Bpifrance) -->
      <!-- ======================================================== -->
      <div class="off-partner-card" data-category="tech active" data-keywords="hyper open x france 2030 bpifrance cloud mariadb repman horizontal scaling infra 2024 active">
        <div>
          <div class="off-partner-logo-box" style="background: linear-gradient(135deg, #0b132b, #1c2541); color: #fff;">
            <div style="font-family: 'Plus Jakarta Sans', sans-serif; font-weight: 900; font-size: 1.25rem; letter-spacing: -0.02em; color: #fff; display: flex; align-items: center; gap: 8px;">
              <span style="color: #00d084; font-size: 1.45rem;">⚡</span>
              <span>HYPER <span style="color: #00d084;">OPEN X</span></span>
            </div>
          </div>
          <span class="off-partner-badge off-partner-badge-active">{"Projet actif • France 2030" if is_fr else "Active Project • France 2030"}</span>
          <div style="display: flex; flex-wrap: wrap; align-items: baseline; gap: 8px;">
            <h3 class="off-partner-name">Hyper Open X (France 2030 / Bpi)</h3>
            <span class="off-partner-date-tag">🗓️ 2024 – {"Présent" if is_fr else "Present"}</span>
          </div>
          <p class="off-partner-desc">
            {"Projet d'envergure financé par France 2030 (opéré par Bpifrance) pour bâtir un cloud européen 100 % libre. Lauréat de l'appel à projets « Hyper Open Call 2 », Open Food Facts bénéficie d'un accompagnement technique pour moderniser son infrastructure de données (migration vers MariaDB et déploiement de RepMan pour la montée en charge horizontale / scaling), garantissant la haute disponibilité face aux millions de requêtes quotidiennes." if is_fr else "Flagship project funded by France 2030 (operated by Bpifrance) to develop a 100% open and sovereign European cloud. Selected as an 'Hyper Open Call 2' laureate, Open Food Facts received technical backing to scale its data infrastructure (MariaDB migration and RepMan horizontal clustering) to guarantee high availability under massive international API workloads."}
          </p>
          <div class="off-partner-milestone">
            <b>Hyper Open Call 2 :</b> <a href="https://hyperopenx.fr" target="_blank" rel="noopener noreferrer">{"Scaling horizontal & migration MariaDB (France 2030)" if is_fr else "Horizontal database scaling & MariaDB migration (France 2030)"}</a>
          </div>
        </div>
        <div class="off-partner-footer">
          <a class="off-partner-link" href="https://hyperopenx.fr" target="_blank" rel="noopener noreferrer">
            hyperopenx.fr ↗
          </a>
        </div>
      </div>

      <!-- ======================================================== -->
      <!-- 7. Envol Vert (Empreinte Forêt) -->
      <!-- ======================================================== -->
      <div class="off-partner-card" data-category="science active" data-keywords="envol vert empreinte foret deforestation forets rdue soja huile de palme cacao cafe biodiversite 2021 active">
        <div>
          <div class="off-partner-logo-box" style="background: #f0fdf4; border-color: #bbf7d0;">
            <div style="display: flex; align-items: center; gap: 10px;">
              <span style="font-size: 1.8rem;">🌳</span>
              <span style="font-size: 1.22rem; font-weight: 900; color: #166534; letter-spacing: 0.03em;">ENVOL <span style="color: #15803d;">VERT</span></span>
            </div>
          </div>
          <span class="off-partner-badge off-partner-badge-active">{"Partenaire actif • Biodiversité" if is_fr else "Active Partner • Biodiversity"}</span>
          <div style="display: flex; flex-wrap: wrap; align-items: baseline; gap: 8px;">
            <h3 class="off-partner-name">Envol Vert (Empreinte Forêt)</h3>
            <span class="off-partner-date-tag">🗓️ 2021 – {"Présent" if is_fr else "Present"}</span>
          </div>
          <p class="off-partner-desc">
            {"Partenariat stratégique avec l'ONG environnementale Envol Vert pour intégrer l'algorithme d'« Empreinte Forêt » au cœur d'Open Food Facts. Cette collaboration permet de calculer et d'afficher le risque de déforestation importée (soja d'élevage, huile de palme, cacao, café) sur plus de 128 000 produits alimentaires, afin d'éclairer les consommateurs et d'anticiper le Règlement européen sur la déforestation (RDUE)." if is_fr else "Strategic partnership with the NGO Envol Vert to incorporate its 'Forest Footprint' (Empreinte Forêt) algorithm directly into Open Food Facts. This tool calculates and reveals imported deforestation risks across key commodities (livestock soy, palm oil, cocoa, coffee) on over 128,000 food products, empowering consumers and paving the way for EU Deforestation Regulation (EUDR) transparency."}
          </p>
          <div class="off-partner-milestone">
            <b>Empreinte Forêt :</b> <a href="https://envol-vert.org" target="_blank" rel="noopener noreferrer">{"Algorithme citoyen de déforestation importée" if is_fr else "Imported Deforestation Risk Algorithm"}</a>
          </div>
        </div>
        <div class="off-partner-footer">
          <a class="off-partner-link" href="https://envol-vert.org" target="_blank" rel="noopener noreferrer">
            envol-vert.org ↗
          </a>
        </div>
      </div>

      <!-- ======================================================== -->
      <!-- 8. EREN - Inserm / Univ Sorbonne Paris Nord -->
      <!-- ======================================================== -->
      <div class="off-partner-card" data-category="science active" data-keywords="eren inserm nutriscore nutri-score recherche epidemiologie nutritionnelle universite sorbonne paris nord 2014 active">
        <div>
          <div class="off-partner-logo-box">
            <img src="https://static.openfoodfacts.org/images/misc/eren-logo.png" alt="EREN Inserm">
          </div>
          <span class="off-partner-badge off-partner-badge-active">{"Recherche active • Nutri-Score" if is_fr else "Active Research • Nutri-Score"}</span>
          <div style="display: flex; flex-wrap: wrap; align-items: baseline; gap: 8px;">
            <h3 class="off-partner-name">EREN (Inserm / Univ. Sorbonne Paris Nord)</h3>
            <span class="off-partner-date-tag">🗓️ 2014 – {"Présent" if is_fr else "Present"}</span>
          </div>
          <p class="off-partner-desc">
            {"L'Équipe de Recherche en Épidémiologie Nutritionnelle (fondatrice du Nutri-Score) utilise en continu la base Open Food Facts pour tester, affiner et valider scientifiquement la pertinence du logo 5 couleurs et ses actualisations algorithmiques." if is_fr else "The Nutritional Epidemiology Research Team (originators of Nutri-Score) continuously relies on Open Food Facts data to validate, test, and mathematically refine the front-of-pack 5-color algorithm and its updates."}
          </p>
          <div class="off-partner-milestone">
            <b>Validation scientifique :</b> <a href="https://www.em-consulte.com/article/993660/article/application-aux-produits-disponibles-sur-le-marche" target="_blank" rel="noopener noreferrer">{"Application aux produits du marché (2015)" if is_fr else "Market validation study (2015)"}</a>
          </div>
        </div>
        <div class="off-partner-footer">
          <a class="off-partner-link" href="https://eren.univ-paris13.fr/" target="_blank" rel="noopener noreferrer">
            eren.univ-paris13.fr ↗
          </a>
        </div>
      </div>

      <!-- ======================================================== -->
      <!-- 9. NutriNet-Santé -->
      <!-- ======================================================== -->
      <div class="off-partner-card" data-category="science active" data-keywords="nutrinet nutrinet-sante inserm cohorte additifs ultra-transformation sante publique 2014 active">
        <div>
          <div class="off-partner-logo-box">
            <img src="https://static.openfoodfacts.org/images/misc/nutrinet-logo.svg" alt="NutriNet-Santé">
          </div>
          <span class="off-partner-badge off-partner-badge-active">{"Recherche active • Cohorte épidémiologique" if is_fr else "Active Research • Cohort Study"}</span>
          <div style="display: flex; flex-wrap: wrap; align-items: baseline; gap: 8px;">
            <h3 class="off-partner-name">NutriNet-Santé</h3>
            <span class="off-partner-date-tag">🗓️ 2014 – {"Présent" if is_fr else "Present"}</span>
          </div>
          <p class="off-partner-desc">
            {"Étude de cohorte publique suivant des centaines de milliers de volontaires. Les données alimentaires NutriNet-Santé sont croisées avec les bases d'ingrédients et d'additifs d'Open Food Facts pour étudier les effets à long terme de l'alimentation ultra-transformée." if is_fr else "World-renowned cohort study tracking hundreds of thousands of volunteers. Researchers cross-reference NutriNet diet records with Open Food Facts additive and ultra-processed food data to evaluate chronic disease risks."}
          </p>
          <div class="off-partner-milestone">
            <b>Recherche citoyenne :</b> <a href="https://etude-nutrinet-sante.fr/profil/introduction" target="_blank" rel="noopener noreferrer">{"Participer à l'étude NutriNet-Santé" if is_fr else "Participate in the NutriNet-Santé Study"}</a>
          </div>
        </div>
        <div class="off-partner-footer">
          <a class="off-partner-link" href="https://etude-nutrinet-sante.fr/" target="_blank" rel="noopener noreferrer">
            etude-nutrinet-sante.fr ↗
          </a>
        </div>
      </div>

      <!-- ======================================================== -->
      <!-- 10. Fondation Free -->
      <!-- ======================================================== -->
      <div class="off-partner-card" data-category="tech active" data-keywords="free fondation free iliad serveurs hebergement infrastructure data 2018 active">
        <div>
          <div class="off-partner-logo-box">
            <img src="https://static.openfoodfacts.org/images/misc/fondation-free-logo.png" alt="Fondation Free">
          </div>
          <span class="off-partner-badge off-partner-badge-active">{"Hébergeur actif • Serveurs physiques" if is_fr else "Active Host • Bare-Metal Servers"}</span>
          <div style="display: flex; flex-wrap: wrap; align-items: baseline; gap: 8px;">
            <h3 class="off-partner-name">Fondation Free</h3>
            <span class="off-partner-date-tag">🗓️ 2018 – {"Présent" if is_fr else "Present"}</span>
          </div>
          <p class="off-partner-desc">
            {"Le site web et les bases de données d'Open Food Facts sont hébergés sur des grappes de serveurs physiques dédiés généreusement mis à disposition en datacenter par la Fondation Free depuis 2018." if is_fr else "The core Open Food Facts database and web servers are hosted on high-performance dedicated hardware generously provided in French datacenters by the Free Foundation since 2018."}
          </p>
          <div class="off-partner-milestone">
            <b>10-09-2018 :</b> <a href="https://blog.openfoodfacts.org/fr/news/2-nouveaux-serveurs-pour-heberger-open-food-facts-grace-a-la-fondation-free" target="_blank" rel="noopener noreferrer">{"Mise en service des serveurs Fondation Free" if is_fr else "Deployment of Free Foundation Servers"}</a>
          </div>
        </div>
        <div class="off-partner-footer">
          <a class="off-partner-link" href="https://www.fondation-free.fr/" target="_blank" rel="noopener noreferrer">
            fondation-free.fr ↗
          </a>
        </div>
      </div>

      <!-- ======================================================== -->
      <!-- 11. OVHcloud -->
      <!-- ======================================================== -->
      <div class="off-partner-card" data-category="tech active" data-keywords="ovh ovhcloud cloud ia serveurs intelligence artificielle calcul 2021 active">
        <div>
          <div class="off-partner-logo-box">
            <img src="https://static.openfoodfacts.org/images/misc/OVHcloud_logo.png" alt="OVHcloud">
          </div>
          <span class="off-partner-badge off-partner-badge-active">{"Partenaire actif • Cloud & IA" if is_fr else "Active Partner • Cloud & AI"}</span>
          <div style="display: flex; flex-wrap: wrap; align-items: baseline; gap: 8px;">
            <h3 class="off-partner-name">OVHcloud</h3>
            <span class="off-partner-date-tag">🗓️ 2021 – {"Présent" if is_fr else "Present"}</span>
          </div>
          <p class="off-partner-desc">
            {"Les algorithmes d'intelligence artificielle, l'extraction de données par vision (OCR) et les pipelines de calcul d'Open Food Facts tournent sur des infrastructures cloud européennes fournies gracieusement par OVHcloud." if is_fr else "Open Food Facts AI pipelines, OCR inference, and computer vision models run on enterprise cloud compute infrastructure generously provided by OVHcloud."}
          </p>
          <div class="off-partner-milestone">
            <b>{"Partenaire Cloud souverain :" if is_fr else "Sovereign Cloud Partner:"}</b> <span>{"Infrastructure européenne haute performance pour l'IA" if is_fr else "European high-performance infrastructure for open AI"}</span>
          </div>
        </div>
        <div class="off-partner-footer">
          <a class="off-partner-link" href="https://www.ovhcloud.com/" target="_blank" rel="noopener noreferrer">
            ovhcloud.com ↗
          </a>
        </div>
      </div>

      <!-- ======================================================== -->
      <!-- 12. The Perl Foundation -->
      <!-- ======================================================== -->
      <div class="off-partner-card" data-category="tech active" data-keywords="perl perl foundation code backend api outreachy mentorat open source stages bourses 2020 2021 2022 2023 2024 active">
        <div>
          <div class="off-partner-logo-box">
            <img src="https://static.openfoodfacts.org/images/misc/the-perl-foundation.jpg" alt="The Perl Foundation">
          </div>
          <span class="off-partner-badge off-partner-badge-active">{"Partenaire actif • Mentorat Open Source" if is_fr else "Active Partner • Open Source Mentorship"}</span>
          <div style="display: flex; flex-wrap: wrap; align-items: baseline; gap: 8px;">
            <h3 class="off-partner-name">The Perl Foundation</h3>
            <span class="off-partner-date-tag">🗓️ 2020 – 2024</span>
          </div>
          <p class="off-partner-desc">
            {"Le cœur historique de la base de données et de l'API Open Food Facts est développé en langage Perl. The Perl Foundation soutient continuellement notre infrastructure en finançant des bourses d'ingénierie et des stages de mentorat via le programme d'inclusion Outreachy (2020, 2021, 2022, 2023 et 2024) pour moderniser le code et développer la plateforme Producteurs." if is_fr else "The core database engine and backend API of Open Food Facts are powered by Perl. The Perl Foundation provides long-term technical and financial support by sponsoring engineering internships and mentorship grants through the Outreachy diversity program (2020, 2021, 2022, 2023, and 2024) to modernize code and enhance the Producer Platform."}
          </p>
          <div class="off-partner-milestone">
            <b>2020 – 2024 (Outreachy) :</b> <a href="https://news.perlfoundation.org/post/outreachy2021-complete" target="_blank" rel="noopener noreferrer">{"Financement de bourses de modernisation du code" if is_fr else "Mentored internships for codebase modernization"}</a>
          </div>
        </div>
        <div class="off-partner-footer">
          <a class="off-partner-link" href="https://www.perlfoundation.org/" target="_blank" rel="noopener noreferrer">
            perlfoundation.org ↗
          </a>
        </div>
      </div>

      <!-- ======================================================== -->
      <!-- 13. INCENTIVE CARD: YOUR ORGANIZATION HERE -->
      <!-- ======================================================== -->
      <div class="off-partner-card off-partner-card-cta" data-category="active philanthropy public tech" data-keywords="votre organisation ici join partnership mecenat subvention alliance sponsor">
        <div>
          <div style="font-size: 2.8rem; margin-bottom: 0.5rem;">🌱</div>
          <span class="off-partner-badge" style="background: var(--off-green); color: #ffffff;">{"Opportunité de partenariat" if is_fr else "Partnership Opportunity"}</span>
          <h3 class="off-partner-name" style="font-size: 1.35rem; margin-top: 0.5rem;">{"Votre organisation ici ?" if is_fr else "Your Organization Here?"}</h3>
          <p class="off-partner-desc" style="max-width: 320px; margin: 0.5rem auto 1.5rem auto;">
            {"Rejoignez les institutions, fondations et pionniers qui façonnent la transparence alimentaire mondiale. Construisons ensemble le prochain saut d'impact." if is_fr else "Join the institutions, foundations, and tech leaders shaping global food transparency. Partner with us to fund the next leap in open data."}
          </p>
          <a class="off-btn off-btn-primary" href="mailto:fundraising@openfoodfacts.org?subject=Proposition%20de%20partenariat%20Open%20Food%20Facts" style="width: 100%;">
            <span>✉️</span> {"Proposer une alliance" if is_fr else "Propose a Collaboration"}
          </a>
        </div>
      </div>

    </div>

    <!-- SECTION 2: HISTORIC & MILESTONE GRANTS -->
    <div class="off-subsection-heading" style="margin-top: 4rem;">
      <h3><span>🏛️</span> {"Grands mécènes & Soutiens historiques marquants" if is_fr else "Major Milestone Grants & Historic Foundations"}</h3>
      <span class="off-subsection-tag" style="background: #f1f5f9; color: #475569;">{"Fondations & Sauts technologiques clés" if is_fr else "Key Grants & Foundational Milestones"}</span>
    </div>

    <div class="off-partners-grid" id="partnersGridHistoric">

      <!-- 14. Google.org -->
      <div class="off-partner-card" data-category="philanthropy historic" data-keywords="google google.org climate impact challenge fellowship mobile eco-score ecoscore green-score 2021 2023 historic">
        <div>
          <div class="off-partner-logo-box">
            <img src="https://static.openfoodfacts.org/images/misc/google-org-logo.png" alt="Google.org">
          </div>
          <span class="off-partner-badge off-partner-badge-historic">{"Mécénat marquant • Climat & IA" if is_fr else "Milestone Grant • Climate & AI"}</span>
          <div style="display: flex; flex-wrap: wrap; align-items: baseline; gap: 8px;">
            <h3 class="off-partner-name">Google.org</h3>
            <span class="off-partner-date-tag">🗓️ 2021 – 2023</span>
          </div>
          <p class="off-partner-desc">
            {"Lauréat du Google Impact Challenge for Climate (2021) puis bénéficiaire du Google.org Fellowship (2023) avec une équipe d'ingénieurs Google mobilisée à plein temps pendant 6 mois pro bono pour développer l'IA de reconnaissance d'emballages, l'Eco-Score et la nouvelle application mobile." if is_fr else "Laureate of the Google Impact Challenge for Climate (2021), followed by a Google.org Fellowship (2023) featuring full-time Google engineers working pro bono for 6 months on computer vision models for packaging, Green-Score, and the modern mobile app."}
          </p>
          <div class="off-partner-milestone">
            <b>28-05-2021 :</b> <a href="https://blog.openfoodfacts.org/en/news/open-food-facts-laureate-of-the-google-fellowship-and-the-google-impact-challenge-for-climate" target="_blank" rel="noopener noreferrer">{"Lauréat du Google Impact Challenge for Climate" if is_fr else "Laureate of the Google Impact Challenge for Climate"}</a>
          </div>
        </div>
        <div class="off-partner-footer">
          <a class="off-partner-link" href="https://www.google.org/" target="_blank" rel="noopener noreferrer">
            google.org ↗
          </a>
        </div>
      </div>

      <!-- 15. Fondation AFNIC -->
      <div class="off-partner-card" data-category="philanthropy historic" data-keywords="afnic fondation afnic solidarite numerique une planete dans mon assiette open products facts eco-score 2020 2023 circular economy historic">
        <div>
          <div class="off-partner-logo-box">
            <img src="https://static.openfoodfacts.org/images/misc/logo_fondation_afnic.png" alt="Fondation AFNIC">
          </div>
          <span class="off-partner-badge off-partner-badge-historic">{"Mécénat marquant • Solidarité numérique" if is_fr else "Milestone Grant • Digital Solidarity"}</span>
          <div style="display: flex; flex-wrap: wrap; align-items: baseline; gap: 8px;">
            <h3 class="off-partner-name">Fondation AFNIC</h3>
            <span class="off-partner-date-tag">🗓️ 2020 &amp; 2023</span>
          </div>
          <p class="off-partner-desc">
            {"La Fondation Afnic pour la solidarité numérique soutient les initiatives numériques d'intérêt général à fort impact sociétal. Elle a primé et financé Open Food Facts à deux reprises pour des sauts d'échelle majeurs :" if is_fr else "The AFNIC Foundation for Digital Solidarity supports public-interest digital innovation with strong social impact. It awarded grants to Open Food Facts across two major strategic initiatives:"}
          </p>
          <div class="off-partner-milestone">
            <b>2020 (Lauréat) :</b> <b>{"Une planète dans mon assiette" if is_fr else "A Planet on My Plate"}</b> — {"Intégration de l'empreinte environnementale des aliments (calcul de l'Eco-Score / Green-Score en lien avec l'ADEME) directement dans l'application mobile pour guider les choix écologiques." if is_fr else "Integrating environmental impact (Eco-Score / Green-Score with ADEME) directly into the mobile app to guide sustainable food choices."}
          </div>
          <div class="off-partner-milestone">
            <b>2023 (Lauréat) :</b> <b>{"Open Products Facts" if is_fr else "Open Products Facts"}</b> — {"Redynamisation de la base de données ouverte dédiée à tous les produits non alimentaires du quotidien pour favoriser la durabilité, la réparation, le réemploi et défragmenter les données de l'économie circulaire." if is_fr else "Relaunching the open database for non-food everyday products to empower reuse, repair, recycling, and circular economy data interoperability."}
          </div>
        </div>
        <div class="off-partner-footer">
          <a class="off-partner-link" href="https://www.fondation-afnic.fr/" target="_blank" rel="noopener noreferrer">
            fondation-afnic.fr ↗
          </a>
        </div>
      </div>

      <!-- 16. Ford Foundation & Mozilla MOSS -->
      <div class="off-partner-card" data-category="philanthropy historic" data-keywords="ford foundation mozilla moss open collective open source mobile flutter civic tech 2020 historic">
        <div>
          <div class="off-partner-logo-box" style="gap: 15px;">
            <img src="https://static.openfoodfacts.org/images/misc/ford_logo.svg" alt="Ford Foundation" style="max-height: 42px;">
            <img src="https://static.openfoodfacts.org/images/misc/mozilla_logo.svg" alt="Mozilla MOSS" style="max-height: 38px;">
            <img src="https://static.openfoodfacts.org/images/misc/opencollective_logo.svg" alt="Open Collective" style="max-height: 36px;">
          </div>
          <span class="off-partner-badge off-partner-badge-historic">{"Mécénat marquant • Application Mobile" if is_fr else "Milestone Grant • Mobile App"}</span>
          <div style="display: flex; flex-wrap: wrap; align-items: baseline; gap: 8px;">
            <h3 class="off-partner-name">Ford Foundation &amp; Mozilla MOSS</h3>
            <span class="off-partner-date-tag">🗓️ 2020</span>
          </div>
          <p class="off-partner-desc">
            {"Financement décisif de la Fondation Ford et du Mozilla Open Source Support Program (MOSS), via Open Collective, ayant permis la conception de la nouvelle application mobile multiplateforme en Flutter." if is_fr else "Crucial grant from the Ford Foundation and Mozilla Open Source Support (MOSS) via Open Collective, funding the creation of the cross-platform Flutter mobile application."}
          </p>
          <div class="off-partner-milestone">
            <b>22-04-2020 :</b> <a href="https://blog.openfoodfacts.org/en/news/mozilla-and-the-ford-foundation-support-the-new-open-food-facts-app/" target="_blank" rel="noopener noreferrer">{"Annonce du soutien Mozilla & Ford Foundation" if is_fr else "Mozilla & Ford Foundation Support Announcement"}</a>
          </div>
        </div>
        <div class="off-partner-footer">
          <a class="off-partner-link" href="https://www.fordfoundation.org/" target="_blank" rel="noopener noreferrer">
            fordfoundation.org &amp; mozilla.org ↗
          </a>
        </div>
      </div>

      <!-- 17. DRG4Food (NutriSight) -->
      <div class="off-partner-card" data-category="science historic" data-keywords="drg4food nutrisight ia vision ocr commission europeenne confiance numerique 2023 2024 historic">
        <div>
          <div class="off-partner-logo-box">
            <img src="https://static.openfoodfacts.org/images/partner_logos/drg4food.png" alt="DRG4Food">
          </div>
          <span class="off-partner-badge off-partner-badge-historic">{"Projet européen • IA Responsable" if is_fr else "EU Programme • Responsible AI"}</span>
          <div style="display: flex; flex-wrap: wrap; align-items: baseline; gap: 8px;">
            <h3 class="off-partner-name">DRG4Food (NutriSight)</h3>
            <span class="off-partner-date-tag">🗓️ 2023 – 2024</span>
          </div>
          <p class="off-partner-desc">
            {"Projet financé par la Commission Européenne pour concevoir NutriSight, notre technologie de pointe d'extraction automatique des tableaux nutritionnels par vision artificielle respectueuse de la vie privée." if is_fr else "Financial award from the European Commission to build NutriSight, our cutting-edge computer vision system extracting nutrition facts from smartphone photos responsibly."}
          </p>
          <div class="off-partner-milestone">
            <b>Digital Responsibility :</b> <a href="https://drg4food.eu/" target="_blank" rel="noopener noreferrer">{"Programme européen DRG4Food" if is_fr else "European DRG4Food Initiative"}</a>
          </div>
        </div>
        <div class="off-partner-footer">
          <a class="off-partner-link" href="https://drg4food.eu/" target="_blank" rel="noopener noreferrer">
            drg4food.eu ↗
          </a>
        </div>
      </div>

      <!-- 18. DIVINFOOD -->
      <div class="off-partner-card" data-category="science historic" data-keywords="divinfood horizon 2020 agrobiodiversite legumes alimentation durable biodiversite europe 2022 2026 historic">
        <div>
          <div class="off-partner-logo-box">
            <img src="https://static.openfoodfacts.org/images/partner_logos/DivinFood.png" alt="DIVINFOOD">
          </div>
          <span class="off-partner-badge off-partner-badge-historic">{"Projet européen • Biodiversité" if is_fr else "EU Programme • Biodiversity"}</span>
          <div style="display: flex; flex-wrap: wrap; align-items: baseline; gap: 8px;">
            <h3 class="off-partner-name">DIVINFOOD (Horizon 2020)</h3>
            <span class="off-partner-date-tag">🗓️ 2022 – 2026</span>
          </div>
          <p class="off-partner-desc">
            {"Consortium européen financé par le programme Horizon 2020 de l'Union Européenne visant à développer des filières alimentaires valorisant l'agrobiodiversité négligée (légumineuses rustiques) pour bâtir des systèmes alimentaires sains et résilients." if is_fr else "European consortium funded by the EU Horizon 2020 programme, DIVINFOOD develops sustainable supply chains emphasizing neglected agrobiodiversity to reverse ecological decline and support consumer health."}
          </p>
          <div class="off-partner-milestone">
            <b>Horizon 2020 :</b> <a href="https://divinfood.eu/" target="_blank" rel="noopener noreferrer">{"Consulter les travaux du projet DIVINFOOD" if is_fr else "Explore the DIVINFOOD Project"}</a>
          </div>
        </div>
        <div class="off-partner-footer">
          <a class="off-partner-link" href="https://divinfood.eu/" target="_blank" rel="noopener noreferrer">
            divinfood.eu ↗
          </a>
        </div>
      </div>

      <!-- 19. XWiki -->
      <div class="off-partner-card" data-category="tech historic" data-keywords="xwiki wiki assemblee generale hebergement evenements paris logiciel libre 2017 historic">
        <div>
          <div class="off-partner-logo-box">
            <img src="https://static.openfoodfacts.org/images/misc/xwiki-logo.svg" alt="XWiki">
          </div>
          <span class="off-partner-badge off-partner-badge-historic">{"Soutien communautaire • Accueil" if is_fr else "Community Host • Venue"}</span>
          <div style="display: flex; flex-wrap: wrap; align-items: baseline; gap: 8px;">
            <h3 class="off-partner-name">XWiki</h3>
            <span class="off-partner-date-tag">🗓️ 2017 – {"Présent" if is_fr else "Present"}</span>
          </div>
          <p class="off-partner-desc">
            {"Pionnier français du logiciel libre, XWiki accueille régulièrement les événements associatifs d'Open Food Facts, notamment ses Assemblées Générales annuelles et ses hackathons dans ses locaux parisiens." if is_fr else "A pioneer of open-source collaborative software in France, XWiki regularly hosts Open Food Facts General Assemblies and community hackathons at their Paris headquarters."}
          </p>
          <div class="off-partner-milestone">
            <b>Communauté libre :</b> <span>{"Accueil de nos assemblées générales associatives" if is_fr else "Regular host for our association general assemblies"}</span>
          </div>
        </div>
        <div class="off-partner-footer">
          <a class="off-partner-link" href="https://xwiki.org/" target="_blank" rel="noopener noreferrer">
            xwiki.org ↗
          </a>
        </div>
      </div>

    </div>
  </div>

  <!-- DONORS WALL & COMMUNITY SPOTLIGHT -->
  <div class="off-donors-banner">
    <h3>{"👥 Chaque citoyen donateur est un partenaire à part entière" if is_fr else "👥 Every Individual Donor is a Vital Partner"}</h3>
    <p>
      {"Plus de 5 000 particuliers soutiennent Open Food Facts par des dons mensuels ou ponctuels. C'est ce soutien citoyen massif et récurrent qui garantit l'indépendance de nos serveurs et notre liberté d'action." if is_fr else "Thousands of individual citizens support Open Food Facts with regular micro-donations. This grassroots funding is what guarantees our servers stay online, our algorithms stay unbiased, and our data remains a public good."}
    </p>
    <div style="display: flex; flex-wrap: wrap; gap: 1rem; justify-content: center;">
      <a class="off-btn off-btn-primary" href="/donors" style="background: #ffffff; color: var(--off-espresso) !important; font-size: 1rem;">
        <span>🏆</span> {"Consulter le Mur des Donateurs &amp; Hall of Fame" if is_fr else "Visit Donors Wall &amp; Hall of Fame"} →
      </a>
      <a class="off-btn off-btn-outline" href="/donate" style="color: #ffffff !important; border-color: rgba(255,255,255,0.4); background: transparent;">
        <span>🧡</span> {"Faire un don défiscalisé" if is_fr else "Make a Tax-Deductible Donation"}
      </a>
    </div>
  </div>

  <!-- BECOME A PARTNER CALLOUT -->
  <div class="off-contact-alliance-box">
    <h3>{"🤝 Vous souhaitez soutenir notre mission, devenir grand mécène ou proposer une alliance ?" if is_fr else "🤝 Looking to Support our Mission, Provide Grant Funding, or Partner with Us?"}</h3>
    <p>
      {"Que vous représentiez une fondation philanthropique, une agence publique, un laboratoire de recherche ou un acteur du numérique d'intérêt général, construisons ensemble les briques d'un monde alimentaire plus transparent et durable." if is_fr else "Whether you represent a philanthropic foundation, a public agency, a university research lab, or an ethical digital initiative, let us join forces to make food transparency and open data a permanent global reality."}
    </p>
    <div>
      <div class="off-fundraising-highlight">
        <span>📬</span> {"Contact direct mécénat & subventions :" if is_fr else "Direct contact for grants & philanthropy:"} <b>fundraising@openfoodfacts.org</b>
      </div>
    </div>
    <div style="display: flex; flex-wrap: wrap; justify-content: center; gap: 1rem; margin-top: 0.5rem;">
      <a class="off-btn off-btn-primary" href="mailto:fundraising@openfoodfacts.org?subject=Proposition%20de%20partenariat%20ou%20m%C3%A9c%C3%A9nat%20Open%20Food%20Facts">
        <span>✉️</span> {"Écrire à l'équipe mécénat" if is_fr else "Contact Fundraising Team"} (fundraising@openfoodfacts.org)
      </a>
      <a class="off-btn off-btn-outline" href="/press">
        <span>🎙️</span> {"Espace presse & médias" if is_fr else "Press & Media Hub"} →
      </a>
    </div>
  </div>

</div>

<!-- INTERACTIVE FILTER & SEARCH JS -->
<script>
let currentCategory = 'all';

function setCategory(cat, btn) {{
  currentCategory = cat;
  document.querySelectorAll('.off-chip-btn').forEach(b => b.classList.remove('active'));
  btn.classList.add('active');
  filterPartners();
}}

function filterPartners() {{
  const query = (document.getElementById('partnerSearch').value || '').toLowerCase().trim();
  const allCards = document.querySelectorAll('.off-partner-card');

  allCards.forEach(card => {{
    const cat = card.getAttribute('data-category') || '';
    const keywords = (card.getAttribute('data-keywords') || '').toLowerCase();
    const text = card.innerText.toLowerCase();

    const matchesCat = (currentCategory === 'all' || cat.includes(currentCategory));
    const matchesQuery = (!query || keywords.includes(query) || text.includes(query));

    if (matchesCat && matchesQuery) {{
      card.style.display = 'flex';
    }} else {{
      card.style.display = 'none';
    }}
  }});
}}
</script>
"""

def main():
    # 1. Generate English
    en_html = build_partners_html("en")
    with open("lang/en/texts/partners.html", "w", encoding="utf-8") as f:
        f.write(en_html.strip() + "\n")
    print("Wrote lang/en/texts/partners.html")

    # 2. Generate French
    fr_html = build_partners_html("fr")
    with open("lang/fr/texts/partners.html", "w", encoding="utf-8") as f:
        f.write(fr_html.strip() + "\n")
    print("Wrote lang/fr/texts/partners.html")

if __name__ == "__main__":
    main()
