#!/usr/bin/env python3
"""
Compilation script for Open Food Facts Historical Campaign & Mission Pages:
- Opération Sodas (`operation-sodas.html`)
- What's in my yogurt? (`whats-in-my-yogurt.html`)
- What's in my shampoo? (`whats-in-my-shampoo.html`)

Generates:
1. `lang/en/texts/<slug>.html` (World/English Product Opener text fragment)
2. `lang/fr/texts/<slug>.html` (French Product Opener text fragment)
3. `<slug>.html` (Standalone root HTML5 preview page with navigation)
"""

import json
import os
import sys
import yaml

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
DATA_DIR = os.path.join(REPO_ROOT, "data")
MISSIONS_DIR = os.path.join(DATA_DIR, "missions")

def load_mission(slug):
    fpath = os.path.join(MISSIONS_DIR, f"{slug}.yaml")
    if not os.path.exists(fpath):
        raise FileNotFoundError(f"Missing mission YAML file: {fpath}")
    with open(fpath, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)

def render_standalone_wrapper(title, lang, content):
    is_fr = (lang == "fr")
    return f"""<!DOCTYPE html>
<html lang="{lang}">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{title} — Open Food Facts</title>
  <meta name="description" content="{title} — Retrospective and interactive exploration by Open Food Facts.">
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=Open+Sans:wght@400;600;700&display=swap" rel="stylesheet">
  <style>
    body {{
      margin: 0;
      padding: 0;
      background: #fdfcfb;
      font-family: "Plus Jakarta Sans", "Open Sans", -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
      color: #0f172a;
      line-height: 1.6;
    }}
    .standalone-nav {{
      background: #ffffff;
      border-bottom: 1px solid #e2e8f0;
      padding: 0.85rem 1.5rem;
      display: flex;
      align-items: center;
      justify-content: space-between;
      flex-wrap: wrap;
      gap: 1rem;
      position: sticky;
      top: 0;
      z-index: 1000;
      box-shadow: 0 2px 8px rgba(0,0,0,0.03);
    }}
    .standalone-brand {{
      display: flex;
      align-items: center;
      gap: 0.75rem;
      text-decoration: none;
      color: #341100;
      font-weight: 800;
      font-size: 1.15rem;
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
      transition: color 0.15s;
    }}
    .standalone-links a:hover,
    .standalone-links a.active {{
      color: #ed8857;
    }}
    .standalone-footer {{
      border-top: 1px solid #e2e8f0;
      background: #ffffff;
      padding: 2.5rem 1.5rem;
      text-align: center;
      font-size: 0.9rem;
      color: #64748b;
      margin-top: 4rem;
    }}
    .standalone-footer a {{
      color: #ea580c;
      text-decoration: none;
      font-weight: 600;
    }}
  </style>
</head>
<body>
  <nav class="standalone-nav">
    <a href="https://world.openfoodfacts.org" class="standalone-brand">
      <img src="https://static.openfoodfacts.org/images/logos/off-logo-horizontal-light.svg" alt="Open Food Facts Logo">
      <span>{"Campagnes & Missions" if is_fr else "Campaigns & Missions"}</span>
    </a>
    <div class="standalone-links">
      <a href="scan-parties.html">{"Scan Parties" if is_fr else "Scan Parties"}</a>
      <a href="operation-sodas.html">Opération Sodas</a>
      <a href="whats-in-my-yogurt.html">What's in my yogurt?</a>
      <a href="whats-in-my-shampoo.html">What's in my shampoo?</a>
      <a href="https://world.openfoodfacts.org/contribute">{"Contribuer" if is_fr else "Contribute"}</a>
      <a href="https://slack.openfoodfacts.org" target="_blank" rel="noopener">Slack</a>
    </div>
  </nav>

  {content}

  <footer class="standalone-footer">
    <p>
      {"Open Food Facts est une association citoyenne à but non lucratif (loi 1901)." if is_fr else "Open Food Facts is a non-profit association of food citizens."} 
      {"Données sous licence libre ODbL." if is_fr else "Data released under the Open Database License (ODbL)."}
    </p>
    <p>
      <a href="scan-parties.html">{"&larr; Retour à l'annuaire des Scan Parties" if is_fr else "&larr; Back to Scan Parties Directory"}</a> • 
      <a href="https://world.openfoodfacts.org">{"Site officiel Open Food Facts" if is_fr else "Official Open Food Facts Website"}</a>
    </p>
  </footer>
</body>
</html>"""

def generate_operation_sodas_html(data, lang="en"):
    is_fr = (lang == "fr")
    
    t = {
        "eyebrow": "🚀 Première Opération Thématique • Juin 2012" if is_fr else "🚀 Landmark 1st Thematic Sprint • June 2012",
        "title": "Opération Sodas" if is_fr else "Operation Sodas",
        "lead": (
            "Du 18 au 24 juin 2012, les premiers contributeurs d'Open Food Facts ont uni leurs forces pour collecter, photographier et analyser 150 boissons gazeuses et sucrées à travers la France. Une aventure pionnière qui a donné naissance aux premiers graphiques interactifs et prouvé la puissance des données ouvertes pour la santé publique."
            if is_fr else
            "From June 18 to 24, 2012, Open Food Facts' earliest contributors joined forces to photograph, catalog, and analyze 150 sugary and carbonated drinks across France. A landmark pioneer campaign that birthed interactive 3-click charts and proved the power of open food data for public health."
        ),
        "stat_sodas_num": "150",
        "stat_sodas_lbl": "Sodas Décryptés" if is_fr else "Sodas Mapped",
        "stat_sodas_sub": "Colas, limonades, tonics, thés glacés" if is_fr else "Colas, lemonades, tonics, iced teas",
        "stat_contrib_num": "60+",
        "stat_contrib_lbl": "Pionniers Mobilisés" if is_fr else "Pioneers Mobilized",
        "stat_contrib_sub": "En rayon, en ligne & à Nantes" if is_fr else "In stores, online & in Nantes",
        "stat_viz_num": "1er",
        "stat_viz_lbl": "Graphique Interactif" if is_fr else "Interactive Chart",
        "stat_viz_sub": "Fonctionnalité en 3 clics" if is_fr else "3-click chart feature",
        "stat_tax_num": "2012",
        "stat_tax_lbl": "Contexte Fiscal & Santé" if is_fr else "Tax & Public Health",
        "stat_tax_sub": "Lancement de la taxe soda" if is_fr else "Soda tax enforcement",
        
        "ctx_title": "Aux origines de l'opération : faire parler les étiquettes" if is_fr else "The Genesis: Making Nutrition Labels Speak",
        "ctx_p1": (
            "Open Food Facts a été lancé publiquement le 19 mai 2012. Dès les premières semaines, une question s'est imposée : à quoi peuvent servir concrètement des données alimentaires ouvertes ? Fin 2011 et début 2012, les débats parlementaires sur la « taxe soda » (entrée en vigueur le 1er janvier 2012) battaient leur plein. Mais au-delà de la célèbre canette rouge et blanche, de quoi sont réellement composés les milliers de sodas vendus en France ?"
            if is_fr else
            "Open Food Facts launched on May 19, 2012. Within weeks, a fundamental question arose: how can open food data deliver immediate, concrete value to citizens? In late 2011 and early 2012, French parliamentary debates on the 'soda tax' (enforced January 1, 2012) were raging. Yet beyond the ubiquitous red-and-white Coca-Cola can, what was actually inside the thousands of sodas sold across supermarkets?"
        ),
        "ctx_p2": (
            "L'Opération Sodas a été le premier banc d'essai collaboratif pour tester la réactivité de la communauté naissante, mobiliser des data journalistes et concevoir des outils d'exploration visuelle innovants."
            if is_fr else
            "Operation Sodas served as the very first collaborative proving ground to test the emerging community's energy, team up with data journalists, and build innovative visual exploration tools."
        ),
        
        "inq_title": "Les 5 Grandes Questions Citoyennes Posées en Rayon" if is_fr else "The 5 Core Citizen Inquiries in Supermarket Aisles",
        "chart_title": "La Naissance des « Graphiques en 3 Clics »" if is_fr else "The Birth of '3-Click Interactive Charts'",
        "chart_lead": (
            "L'un des apports majeurs de l'Opération Sodas a été le développement d'un générateur dynamique de nuages de points (scatter plots), permettant de croiser n'importe quel nutriment avec le nombre d'additifs."
            if is_fr else
            "One of Operation Sodas' defining breakthroughs was the development of a dynamic scatter plot generator directly within Open Food Facts, plotting any nutrient against the number of food additives."
        ),
        "chart_caption": "Graphique historique croisant sucres et nombre d'additifs dans les sodas (Open Food Facts, juin 2012)" if is_fr else "Historical scatter plot plotting sugars vs number of additives in sodas (Open Food Facts, June 2012)",
        "chart_cta": "Exécuter la requête en direct sur Open Food Facts &rarr;" if is_fr else "Run this live scatter query on Open Food Facts &rarr;",
        
        "media_title": "Écho Médiatique & Partenaires Pionniers" if is_fr else "Media Echo & Landmark Partners",
        "media_lead": (
            "Dès 2012, journalistes de données et spécialistes de santé se sont emparés des premiers jeux de données d'Open Food Facts :"
            if is_fr else
            "Back in 2012, data journalists and clinical specialists immediately seized Open Food Facts' raw datasets to investigate food quality:"
        ),
        
        "legacy_title": "De l'Opération Sodas à 3,8 millions de produits" if is_fr else "From Operation Sodas to 3.8 Million Products",
        "legacy_desc": (
            "Opération Sodas a été l'étincelle qui a démontré que la foule citoyenne pouvait cartographier une catégorie alimentaire complète en quelques jours. Cette méthode a ensuite inspiré <em>What's in my yogurt?</em> (2014), <em>What's in my shampoo?</em> (2016), et l'ensemble des Scan Parties qui se déroulent aujourd'hui dans toute l'Europe."
            if is_fr else
            "Operation Sodas proved that citizen crowdsourcing could map an entire grocery category in just a few days. This methodology laid the blueprint for <em>What's in my yogurt?</em> (2014), <em>What's in my shampoo?</em> (2016), and the vibrant Scan Parties organized across Europe today."
        ),
        "btn_scan_party": "Découvrir les Scan Parties d'aujourd'hui" if is_fr else "Explore Today's Scan Parties",
        "btn_add_product": "Ajouter une boisson à la base" if is_fr else "Add a beverage to Open Food Facts",
    }
    
    questions = data.get("key_questions", [])
    press = data.get("press_coverage", [])
    
    questions_html = ""
    for q in questions:
        q_text = q.get(f"question_{lang}", q.get("question_en"))
        f_text = q.get(f"finding_{lang}", q.get("finding_en"))
        questions_html += f"""
        <div class="off-card off-inq-card">
          <div class="off-inq-q">❓ {q_text}</div>
          <div class="off-inq-a">💡 {f_text}</div>
        </div>
        """
        
    press_html = ""
    for p in press:
        outlet = p.get("outlet", "")
        p_title = p.get("title", "")
        author = p.get("author", "")
        date = p.get("date", "")
        link = p.get("link", "#")
        quote = p.get("quote", "")
        press_html += f"""
        <div class="off-card off-press-card">
          <div class="off-press-top">
            <span class="off-press-outlet">{outlet}</span>
            <span class="off-press-date">{date}</span>
          </div>
          <h4 class="off-press-title"><a href="{link}" target="_blank" rel="noopener noreferrer">{p_title}</a></h4>
          <div class="off-press-author">✍️ {author}</div>
          <blockquote class="off-press-quote">« {quote} »</blockquote>
        </div>
        """

    return f"""<style>
/* Operation Sodas Revamped Showcase Styles */
.off-op-wrap {{
  --off-espresso: #341100;
  --off-espresso-mid: #473526;
  --off-cream: #fdfaf7;
  --off-peach-tint: #f5ebe6;
  --off-orange: #ea580c;
  --off-orange-hover: #c2410c;
  --off-blue: #0284c7;
  --off-green: #16a34a;
  --off-border: #e2e8f0;
  --off-surface: #ffffff;
  --off-radius: 20px;
  
  max-width: 1200px;
  margin: 0 auto 3.5rem auto;
  padding: 0 1rem;
  color: var(--off-espresso);
  font-family: "Plus Jakarta Sans", "Open Sans", -apple-system, BlinkMacSystemFont, sans-serif;
  line-height: 1.6;
}}

.off-op-hero {{
  background: linear-gradient(180deg, #ffffff 0%, var(--off-cream) 100%);
  border: 1px solid var(--off-peach-tint);
  border-radius: 28px;
  padding: clamp(2rem, 4vw, 3.5rem);
  text-align: center;
  margin: 1.5rem 0 2.5rem 0;
  box-shadow: 0 8px 30px rgba(52, 17, 0, 0.04);
}}

.off-badge-hero {{
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  background: #fff7ed;
  color: var(--off-orange);
  border: 1px solid #fed7aa;
  padding: 0.4rem 1rem;
  border-radius: 9999px;
  font-size: 0.85rem;
  font-weight: 700;
  letter-spacing: 0.03em;
  text-transform: uppercase;
  margin-bottom: 1.25rem;
}}

.off-op-hero h1 {{
  font-size: clamp(2.2rem, 4.5vw, 3.5rem);
  font-weight: 800;
  color: var(--off-espresso);
  margin: 0 0 1rem 0;
  line-height: 1.15;
}}

.off-op-hero p.lead {{
  font-size: clamp(1.05rem, 1.8vw, 1.25rem);
  color: var(--off-espresso-mid);
  max-width: 860px;
  margin: 0 auto 2rem auto;
}}

.off-stats-grid {{
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
  gap: 1.25rem;
  margin-top: 2rem;
}}

.off-stat-card {{
  background: var(--off-surface);
  border: 1px solid var(--off-border);
  border-radius: var(--off-radius);
  padding: 1.5rem;
  text-align: center;
  box-shadow: 0 4px 12px rgba(0,0,0,0.02);
  transition: transform 0.2s, box-shadow 0.2s;
}}
.off-stat-card:hover {{
  transform: translateY(-3px);
  box-shadow: 0 8px 24px rgba(0,0,0,0.06);
}}
.off-stat-num {{
  font-size: 2.2rem;
  font-weight: 800;
  color: var(--off-orange);
  line-height: 1;
  margin-bottom: 0.35rem;
}}
.off-stat-lbl {{
  font-size: 1rem;
  font-weight: 700;
  color: var(--off-espresso);
  margin-bottom: 0.25rem;
}}
.off-stat-sub {{
  font-size: 0.82rem;
  color: #64748b;
}}

.off-section {{
  margin: 3.5rem 0;
}}
.off-section-title {{
  font-size: 1.85rem;
  font-weight: 800;
  color: var(--off-espresso);
  margin-bottom: 0.75rem;
  text-align: center;
}}
.off-section-lead {{
  text-align: center;
  font-size: 1.05rem;
  color: var(--off-espresso-mid);
  max-width: 800px;
  margin: 0 auto 2rem auto;
}}

.off-inq-grid {{
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(320px, 1fr));
  gap: 1.5rem;
}}
.off-card {{
  background: var(--off-surface);
  border: 1px solid var(--off-border);
  border-radius: var(--off-radius);
  padding: 1.5rem;
  box-shadow: 0 4px 16px rgba(0,0,0,0.02);
}}
.off-inq-card {{
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}}
.off-inq-q {{
  font-size: 1.05rem;
  font-weight: 700;
  color: var(--off-espresso);
}}
.off-inq-a {{
  font-size: 0.92rem;
  color: #334155;
  background: #f8fafc;
  padding: 0.85rem;
  border-radius: 12px;
  border-left: 3px solid var(--off-orange);
}}

.off-chart-box {{
  background: #ffffff;
  border: 1px solid var(--off-border);
  border-radius: 24px;
  padding: clamp(1.5rem, 3vw, 2.5rem);
  text-align: center;
  box-shadow: 0 8px 24px rgba(0,0,0,0.04);
}}
.off-chart-img {{
  max-width: 100%;
  height: auto;
  border-radius: 12px;
  border: 1px solid #cbd5e1;
  box-shadow: 0 4px 12px rgba(0,0,0,0.05);
  margin: 1.5rem 0;
}}
.off-btn {{
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.85rem 1.75rem;
  border-radius: 9999px;
  font-weight: 700;
  font-size: 0.95rem;
  text-decoration: none;
  transition: all 0.2s;
  cursor: pointer;
}}
.off-btn-primary {{
  background: var(--off-orange);
  color: #ffffff;
}}
.off-btn-primary:hover {{
  background: var(--off-orange-hover);
  color: #ffffff;
}}
.off-btn-secondary {{
  background: #ffffff;
  color: var(--off-espresso);
  border: 1px solid var(--off-border);
}}
.off-btn-secondary:hover {{
  background: #f8fafc;
  border-color: #cbd5e1;
}}

.off-press-grid {{
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(270px, 1fr));
  gap: 1.5rem;
}}
.off-press-card {{
  display: flex;
  flex-direction: column;
  justify-content: space-between;
}}
.off-press-top {{
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 0.75rem;
}}
.off-press-outlet {{
  background: #f1f5f9;
  color: #0f172a;
  padding: 0.25rem 0.6rem;
  border-radius: 6px;
  font-weight: 700;
  font-size: 0.78rem;
  text-transform: uppercase;
}}
.off-press-date {{
  font-size: 0.8rem;
  color: #64748b;
}}
.off-press-title {{
  font-size: 1.05rem;
  font-weight: 700;
  margin: 0 0 0.5rem 0;
}}
.off-press-title a {{
  color: var(--off-espresso);
  text-decoration: none;
}}
.off-press-title a:hover {{
  color: var(--off-orange);
}}
.off-press-author {{
  font-size: 0.85rem;
  color: #64748b;
  margin-bottom: 0.75rem;
}}
.off-press-quote {{
  margin: 0;
  font-style: italic;
  font-size: 0.9rem;
  color: #475569;
  border-left: 2px solid #cbd5e1;
  padding-left: 0.75rem;
}}

.off-legacy-banner {{
  background: linear-gradient(135deg, #fff7ed 0%, #ffedd5 100%);
  border: 1px solid #fed7aa;
  border-radius: 24px;
  padding: clamp(2rem, 3.5vw, 3rem);
  text-align: center;
  margin-top: 3.5rem;
}}
.off-legacy-title {{
  font-size: 1.6rem;
  font-weight: 800;
  color: #9a3412;
  margin-bottom: 0.75rem;
}}
.off-legacy-desc {{
  font-size: 1.05rem;
  color: #7c2d12;
  max-width: 800px;
  margin: 0 auto 1.5rem auto;
}}
.off-legacy-actions {{
  display: flex;
  gap: 1rem;
  justify-content: center;
  flex-wrap: wrap;
}}
</style>

<div class="off-op-wrap">
  <!-- Hero Section -->
  <div class="off-op-hero">
    <div class="off-badge-hero">{t["eyebrow"]}</div>
    <h1>{t["title"]}</h1>
    <p class="lead">{t["lead"]}</p>
    
    <div class="off-stats-grid">
      <div class="off-stat-card">
        <div class="off-stat-num">{t["stat_sodas_num"]}</div>
        <div class="off-stat-lbl">{t["stat_sodas_lbl"]}</div>
        <div class="off-stat-sub">{t["stat_sodas_sub"]}</div>
      </div>
      <div class="off-stat-card">
        <div class="off-stat-num">{t["stat_contrib_num"]}</div>
        <div class="off-stat-lbl">{t["stat_contrib_lbl"]}</div>
        <div class="off-stat-sub">{t["stat_contrib_sub"]}</div>
      </div>
      <div class="off-stat-card">
        <div class="off-stat-num">{t["stat_viz_num"]}</div>
        <div class="off-stat-lbl">{t["stat_viz_lbl"]}</div>
        <div class="off-stat-sub">{t["stat_viz_sub"]}</div>
      </div>
      <div class="off-stat-card">
        <div class="off-stat-num">{t["stat_tax_num"]}</div>
        <div class="off-stat-lbl">{t["stat_tax_lbl"]}</div>
        <div class="off-stat-sub">{t["stat_tax_sub"]}</div>
      </div>
    </div>
  </div>

  <!-- Historical Context -->
  <div class="off-section">
    <div class="off-card" style="display: flex; flex-wrap: wrap; gap: 2rem; align-items: center;">
      <div style="flex: 1 1 400px;">
        <h3 style="font-size: 1.5rem; font-weight: 800; margin-top: 0;">{t["ctx_title"]}</h3>
        <p style="color: #334155; font-size: 0.98rem;">{t["ctx_p1"]}</p>
        <p style="color: #334155; font-size: 0.98rem;">{t["ctx_p2"]}</p>
      </div>
      <div style="flex: 0 0 280px; text-align: center; margin: 0 auto;">
        <img src="https://fr.openfoodfacts.org/images/misc/operation-soda.png" alt="Opération Sodas Badge" style="max-width: 220px; height: auto; border-radius: 16px; box-shadow: 0 4px 14px rgba(0,0,0,0.08);">
      </div>
    </div>
  </div>

  <!-- Citizen Questions Investigated -->
  <div class="off-section">
    <h3 class="off-section-title">{t["inq_title"]}</h3>
    <div class="off-inq-grid">
      {questions_html}
    </div>
  </div>

  <!-- 3-Click Chart Feature Breakthrough -->
  <div class="off-section">
    <div class="off-chart-box">
      <h3 style="font-size: 1.6rem; font-weight: 800; margin: 0 0 0.5rem 0;">{t["chart_title"]}</h3>
      <p style="color: #475569; max-width: 750px; margin: 0 auto 1.25rem auto;">{t["chart_lead"]}</p>
      
      <a href="{data.get('scatter_plot_url')}" target="_blank" rel="noopener noreferrer">
        <img src="https://fr.blog.openfoodfacts.org/images/sucres_et_additifs_dans_les_sodas.png" alt="{t['chart_caption']}" class="off-chart-img">
      </a>
      <p style="font-size: 0.85rem; color: #64748b; font-style: italic; margin-bottom: 1.5rem;">{t["chart_caption"]}</p>
      
      <a href="{data.get('scatter_plot_url')}" target="_blank" rel="noopener noreferrer" class="off-btn off-btn-primary">
        {t["chart_cta"]}
      </a>
    </div>
  </div>

  <!-- Media Coverage & Partners -->
  <div class="off-section">
    <h3 class="off-section-title">{t["media_title"]}</h3>
    <p class="off-section-lead">{t["media_lead"]}</p>
    <div class="off-press-grid">
      {press_html}
    </div>
  </div>

  <!-- Legacy & Future Call to Action -->
  <div class="off-legacy-banner">
    <div class="off-legacy-title">💡 {t["legacy_title"]}</div>
    <div class="off-legacy-desc">{t["legacy_desc"]}</div>
    <div class="off-legacy-actions">
      <a href="scan-parties.html" class="off-btn off-btn-primary">🎉 {t["btn_scan_party"]}</a>
      <a href="https://world.openfoodfacts.org/contribute" class="off-btn off-btn-secondary">📱 {t["btn_add_product"]}</a>
    </div>
  </div>
</div>
"""

def generate_whats_in_my_yogurt_html(data, lang="en"):
    is_fr = (lang == "fr")
    
    t = {
        "eyebrow": "🌍 Open Data Day 2014 • Campagne Mondiale" if is_fr else "🌍 Open Data Day 2014 • Global Crowdsourcing Quest",
        "title": "What's in my yogurt?" if not is_fr else "Qu'y a-t-il dans mon yaourt ?",
        "lead": (
            "Lancé lors de la Journée Internationale des Données Ouvertes (22 février 2014), le projet « What's in my yogurt? » a mobilisé des citoyens dans plus de 20 pays pour décrypter les rayons frais : portions de 125g contre 180g, taux de vrais fruits, additifs dans les 0% et sucres ajoutés sous toutes les latitudes."
            if is_fr else
            "Launched on Open Data Day (February 22, 2014), 'What's in my yogurt?' mobilized citizen contributors in over 20 countries to scan dairy aisles: comparing 125g vs 180g portion sizes, real fruit percentages, additives in fat-free formulas, and sugar levels worldwide."
        ),
        "stat_yogurts_num": "1 000+",
        "stat_yogurts_lbl": "Yaourts Décryptés" if is_fr else "Yogurts Mapped",
        "stat_yogurts_sub": "Nature, aux fruits, brassés, soja" if is_fr else "Plain, fruit, stirred, soy & Greek",
        "stat_countries_num": "20+",
        "stat_countries_lbl": "Pays Mobilisés" if is_fr else "Countries Mobilized",
        "stat_countries_sub": "Équipes nationales citoyennes" if is_fr else "National contributor squads",
        "stat_formats_num": "125g vs 180g",
        "stat_formats_lbl": "Écarts de Portion" if is_fr else "Portion Disparities",
        "stat_formats_sub": "France vs Suisse & États-Unis" if is_fr else "France vs Switzerland & USA",
        "stat_day_num": "ODD 2014",
        "stat_day_lbl": "Open Data Day" if is_fr else "Open Data Day",
        "stat_day_sub": "whatsinmyyogurt.com" if is_fr else "whatsinmyyogurt.com",
        
        "trojan_title": "Le « Cheval de Troie » au fond du réfrigérateur" if is_fr else "The 'Trojan Horse' into Everyday Refrigerators",
        "trojan_p1": (
            "Pourquoi choisir les yaourts après les sodas ? Parce que le yaourt est un aliment du quotidien consommé massivement par les familles et les enfants. Pourtant, derrière une image universelle de produit « santé », les étiquettes recèlent des disparités frappantes : épaississants masquant le manque de matière grasse, sirop de glucose-fructose, faux morceaux de fruits et variations géographiques majeures."
            if is_fr else
            "Why focus on yogurts after sodas? Because yogurt is a household staple enjoyed daily by hundreds of millions of children and families. Yet behind its innocent 'health food' halo, nutrition labels conceal staggering contrasts: synthetic thickeners masking fat-free textures, high-fructose corn syrups, deceptive fruit imagery, and extreme geographical variations."
        ),
        "trojan_p2": (
            "En incitant chacun à photographier le pot de son frigo ou de l'épicerie du coin, Open Food Facts a utilisé le yaourt comme un cheval de Troie pour faire entrer la transparence alimentaire dans les foyers."
            if is_fr else
            "By inviting everyday shoppers to snap pictures of the yogurt cups in their kitchen or local co-op, Open Food Facts used yogurt as a friendly Trojan Horse to bring open data literacy into household routines."
        ),
        
        "inq_title": "Les Révélations de l'Enquête Mondiale" if is_fr else "Key Discoveries of the Global Yogurt Inquiry",
        "squads_title": "Équipes Internationales & Compétition Conviviale" if is_fr else "Country Squads & Friendly Global Competition",
        "queries_title": "Explorer les Données en Direct (Requêtes Live)" if is_fr else "Explore Live Yogurt Datasets",
        "queries_lead": (
            "Grâce aux données collectées, plusieurs visualisations et analyses comparatives continuent d'éclairer les consommateurs en temps réel :"
            if is_fr else
            "Thanks to the crowdsourced data, several live queries and comparative scatter plots continue to empower consumers today:"
        ),
        "btn_scan_party": "Participer à une Scan Party" if is_fr else "Join a Scan Party",
        "btn_add_yogurt": "Ajouter un yaourt à Open Food Facts" if is_fr else "Add a yogurt to Open Food Facts",
    }
    
    questions = data.get("key_questions", [])
    squads = data.get("country_teams", [])
    queries = data.get("related_queries", [])
    
    questions_html = ""
    for q in questions:
        q_text = q.get(f"question_{lang}", q.get("question_en"))
        f_text = q.get(f"finding_{lang}", q.get("finding_en"))
        questions_html += f"""
        <div class="off-card off-inq-card">
          <div class="off-inq-q">🥛 {q_text}</div>
          <div class="off-inq-a">💡 {f_text}</div>
        </div>
        """
        
    squads_html = ""
    for s in squads:
        country = s.get("country", "")
        notes = s.get("notes", "")
        squads_html += f"""
        <div class="off-card" style="border-left: 4px solid var(--off-blue);">
          <h4 style="margin: 0 0 0.5rem 0; font-size: 1.1rem; color: #0284c7;">🚩 {country}</h4>
          <p style="margin: 0; font-size: 0.9rem; color: #334155;">{notes}</p>
        </div>
        """

    queries_html = ""
    for q in queries:
        q_id = q.get("id", "")
        q_title = q.get("title", "")
        q_url = q.get("url", "#")
        queries_html += f"""
        <div class="off-card" style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 1rem;">
          <div>
            <div style="font-weight: 700; font-size: 1.05rem; color: #0f172a;">📊 {q_title}</div>
            <div style="font-size: 0.8rem; color: #64748b; font-family: monospace;">query: {q_id}</div>
          </div>
          <a href="{q_url}" target="_blank" rel="noopener noreferrer" class="off-btn off-btn-blue">
            {"Voir l'analyse &rarr;" if is_fr else "View live query &rarr;"}
          </a>
        </div>
        """

    return f"""<style>
/* What's In My Yogurt Revamped Showcase Styles */
.off-yg-wrap {{
  --off-espresso: #0f172a;
  --off-blue: #0284c7;
  --off-blue-dark: #0369a1;
  --off-blue-light: #f0f9ff;
  --off-blue-border: #bae6fd;
  --off-border: #e2e8f0;
  --off-surface: #ffffff;
  --off-radius: 20px;
  
  max-width: 1200px;
  margin: 0 auto 3.5rem auto;
  padding: 0 1rem;
  color: var(--off-espresso);
  font-family: "Plus Jakarta Sans", "Open Sans", -apple-system, BlinkMacSystemFont, sans-serif;
  line-height: 1.6;
}}

.off-yg-hero {{
  background: linear-gradient(180deg, #ffffff 0%, var(--off-blue-light) 100%);
  border: 1px solid var(--off-blue-border);
  border-radius: 28px;
  padding: clamp(2rem, 4vw, 3.5rem);
  text-align: center;
  margin: 1.5rem 0 2.5rem 0;
  box-shadow: 0 8px 30px rgba(2, 132, 199, 0.06);
}}

.off-badge-blue {{
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  background: #e0f2fe;
  color: var(--off-blue-dark);
  border: 1px solid var(--off-blue-border);
  padding: 0.4rem 1rem;
  border-radius: 9999px;
  font-size: 0.85rem;
  font-weight: 700;
  letter-spacing: 0.03em;
  text-transform: uppercase;
  margin-bottom: 1.25rem;
}}

.off-yg-hero h1 {{
  font-size: clamp(2.2rem, 4.5vw, 3.5rem);
  font-weight: 800;
  color: #0c4a6e;
  margin: 0 0 1rem 0;
  line-height: 1.15;
}}

.off-yg-hero p.lead {{
  font-size: clamp(1.05rem, 1.8vw, 1.25rem);
  color: #334155;
  max-width: 860px;
  margin: 0 auto 2rem auto;
}}

.off-stats-grid {{
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
  gap: 1.25rem;
  margin-top: 2rem;
}}

.off-stat-card {{
  background: var(--off-surface);
  border: 1px solid var(--off-border);
  border-radius: var(--off-radius);
  padding: 1.5rem;
  text-align: center;
  box-shadow: 0 4px 12px rgba(0,0,0,0.02);
  transition: transform 0.2s, box-shadow 0.2s;
}}
.off-stat-card:hover {{
  transform: translateY(-3px);
  box-shadow: 0 8px 24px rgba(2, 132, 199, 0.08);
}}
.off-stat-num-blue {{
  font-size: 2.2rem;
  font-weight: 800;
  color: var(--off-blue);
  line-height: 1;
  margin-bottom: 0.35rem;
}}
.off-stat-lbl {{
  font-size: 1rem;
  font-weight: 700;
  color: #0f172a;
  margin-bottom: 0.25rem;
}}
.off-stat-sub {{
  font-size: 0.82rem;
  color: #64748b;
}}

.off-section {{
  margin: 3.5rem 0;
}}
.off-section-title {{
  font-size: 1.85rem;
  font-weight: 800;
  color: #0c4a6e;
  margin-bottom: 0.75rem;
  text-align: center;
}}
.off-section-lead {{
  text-align: center;
  font-size: 1.05rem;
  color: #475569;
  max-width: 800px;
  margin: 0 auto 2rem auto;
}}

.off-card {{
  background: var(--off-surface);
  border: 1px solid var(--off-border);
  border-radius: var(--off-radius);
  padding: 1.5rem;
  box-shadow: 0 4px 16px rgba(0,0,0,0.02);
}}
.off-inq-card {{
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}}
.off-inq-q {{
  font-size: 1.05rem;
  font-weight: 700;
  color: #0c4a6e;
}}
.off-inq-a {{
  font-size: 0.92rem;
  color: #334155;
  background: #f8fafc;
  padding: 0.85rem;
  border-radius: 12px;
  border-left: 3px solid var(--off-blue);
}}

.off-btn {{
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.85rem 1.75rem;
  border-radius: 9999px;
  font-weight: 700;
  font-size: 0.95rem;
  text-decoration: none;
  transition: all 0.2s;
  cursor: pointer;
}}
.off-btn-blue {{
  background: var(--off-blue);
  color: #ffffff;
}}
.off-btn-blue:hover {{
  background: var(--off-blue-dark);
  color: #ffffff;
}}
.off-btn-secondary {{
  background: #ffffff;
  color: #0f172a;
  border: 1px solid var(--off-border);
}}
.off-btn-secondary:hover {{
  background: #f8fafc;
}}

.off-legacy-banner-blue {{
  background: linear-gradient(135deg, #f0f9ff 0%, #e0f2fe 100%);
  border: 1px solid #bae6fd;
  border-radius: 24px;
  padding: clamp(2rem, 3.5vw, 3rem);
  text-align: center;
  margin-top: 3.5rem;
}}
.off-legacy-title-blue {{
  font-size: 1.6rem;
  font-weight: 800;
  color: #0369a1;
  margin-bottom: 0.75rem;
}}
.off-legacy-desc-blue {{
  font-size: 1.05rem;
  color: #075985;
  max-width: 800px;
  margin: 0 auto 1.5rem auto;
}}
.off-legacy-actions {{
  display: flex;
  gap: 1rem;
  justify-content: center;
  flex-wrap: wrap;
}}
</style>

<div class="off-yg-wrap">
  <!-- Hero Section -->
  <div class="off-yg-hero">
    <div class="off-badge-blue">{t["eyebrow"]}</div>
    <h1>{t["title"]}</h1>
    <p class="lead">{t["lead"]}</p>
    
    <div class="off-stats-grid">
      <div class="off-stat-card">
        <div class="off-stat-num-blue">{t["stat_yogurts_num"]}</div>
        <div class="off-stat-lbl">{t["stat_yogurts_lbl"]}</div>
        <div class="off-stat-sub">{t["stat_yogurts_sub"]}</div>
      </div>
      <div class="off-stat-card">
        <div class="off-stat-num-blue">{t["stat_countries_num"]}</div>
        <div class="off-stat-lbl">{t["stat_countries_lbl"]}</div>
        <div class="off-stat-sub">{t["stat_countries_sub"]}</div>
      </div>
      <div class="off-stat-card">
        <div class="off-stat-num-blue">{t["stat_formats_num"]}</div>
        <div class="off-stat-lbl">{t["stat_formats_lbl"]}</div>
        <div class="off-stat-sub">{t["stat_formats_sub"]}</div>
      </div>
      <div class="off-stat-card">
        <div class="off-stat-num-blue">{t["stat_day_num"]}</div>
        <div class="off-stat-lbl">{t["stat_day_lbl"]}</div>
        <div class="off-stat-sub">{t["stat_day_sub"]}</div>
      </div>
    </div>
  </div>

  <!-- Trojan Horse Concept -->
  <div class="off-section">
    <div class="off-card" style="display: flex; flex-wrap: wrap; gap: 2rem; align-items: center;">
      <div style="flex: 1 1 400px;">
        <h3 style="font-size: 1.5rem; font-weight: 800; color: #0c4a6e; margin-top: 0;">{t["trojan_title"]}</h3>
        <p style="color: #334155; font-size: 0.98rem;">{t["trojan_p1"]}</p>
        <p style="color: #334155; font-size: 0.98rem;">{t["trojan_p2"]}</p>
      </div>
      <div style="flex: 0 0 280px; text-align: center; margin: 0 auto;">
        <img src="https://fr.openfoodfacts.org/images/misc/yogurt-400x300.png" alt="What's in my yogurt badge" style="max-width: 240px; height: auto; border-radius: 16px; box-shadow: 0 4px 14px rgba(0,0,0,0.08);">
      </div>
    </div>
  </div>

  <!-- Key Discoveries -->
  <div class="off-section">
    <h3 class="off-section-title">{t["inq_title"]}</h3>
    <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(320px, 1fr)); gap: 1.5rem;">
      {questions_html}
    </div>
  </div>

  <!-- Country Squads -->
  <div class="off-section">
    <h3 class="off-section-title">{t["squads_title"]}</h3>
    <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(260px, 1fr)); gap: 1.25rem;">
      {squads_html}
    </div>
  </div>

  <!-- Live Queries Exploration -->
  <div class="off-section">
    <h3 class="off-section-title">{t["queries_title"]}</h3>
    <p class="off-section-lead">{t["queries_lead"]}</p>
    <div style="display: flex; flex-direction: column; gap: 1rem; max-width: 860px; margin: 0 auto;">
      {queries_html}
    </div>
  </div>

  <!-- Bottom CTA Banner -->
  <div class="off-legacy-banner-blue">
    <div class="off-legacy-title-blue">🥛 {"Prêt à faire parler les rayons frais ?" if is_fr else "Ready to demystify yogurt aisles?"}</div>
    <div class="off-legacy-desc-blue">
      {"Découvrez les scan parties organisées près de chez vous ou enrichissez directement la base de données ouverte !" if is_fr else "Find a scan party in your local community or scan yogurts with the Open Food Facts mobile app!"}
    </div>
    <div class="off-legacy-actions">
      <a href="scan-parties.html" class="off-btn off-btn-blue">🎉 {t["btn_scan_party"]}</a>
      <a href="https://world.openfoodfacts.org/category/yogurts" class="off-btn off-btn-secondary">🔍 {t["btn_add_yogurt"]}</a>
    </div>
  </div>
</div>
"""

def generate_whats_in_my_shampoo_html(data, lang="en"):
    is_fr = (lang == "fr")
    
    t = {
        "eyebrow": "🧴 Open Beauty Facts • Open Data Day 2016" if is_fr else "🧴 Open Beauty Facts • Open Data Day 2016",
        "title": "What's in my shampoo?" if not is_fr else "Qu'y a-t-il dans mon shampooing ?",
        "lead": (
            "Le 5 mars 2016, à l'occasion de l'Open Data Day, la communauté Open Food Facts a poussé la porte de la salle de bain pour donner naissance à Open Beauty Facts. Objectif : photographier et décrypter la nomenclature INCI en latin, identifier conservateurs, allergènes et silicones dans les shampooings du monde entier."
            if is_fr else
            "On March 5, 2016, for Open Data Day, the Open Food Facts community opened the bathroom door to launch Open Beauty Facts. The mission: photograph and decipher complex Latin INCI cosmetic formulations, count chemicals, and identify preservatives, allergens, and silicones in shampoos worldwide."
        ),
        "stat_shampoos_num": "1 200+",
        "stat_shampoos_lbl": "Shampooings Décryptés" if is_fr else "Shampoos Decrypted",
        "stat_shampoos_sub": "Classiques, bios, solides, antipelliculaires" if is_fr else "Conventional, organic, solid, anti-dandruff",
        "stat_comp_num": "10 à 42",
        "stat_comp_lbl": "Ingrédients par Flacon" if is_fr else "Ingredients per Bottle",
        "stat_comp_sub": "De l'ultra-court au cocktail chimique" if is_fr else "From minimalist to 40+ chemicals",
        "stat_inci_num": "INCI",
        "stat_inci_lbl": "Latin Décodé en Clair" if is_fr else "Plain English Translation",
        "stat_inci_sub": "Aqua = Eau, tensioactifs, silicones" if is_fr else "Aqua = Water, sulfates, silicones",
        "stat_gouv_num": "data.gouv.fr",
        "stat_gouv_lbl": "Jeu de Données Ouvert" if is_fr else "Public Open Commons",
        "stat_gouv_sub": "Réutilisation citoyenne & recherche" if is_fr else "Citizen science & academic reuse",
        
        "latin_title": "Pourquoi décrypter la salle de bain ?" if is_fr else "Why Decipher the Bathroom Cabinet?",
        "latin_p1": (
            "Contrairement à l'alimentation où les ingrédients sont souvent formulés en langage courant (farine, sucre, huile), les cosmétiques imposent la nomenclature internationale INCI : un mélange de latin (pour les extraits végétaux) et de termes chimiques complexes. Sans formation scientifique poussée, il est presque impossible pour un citoyen de comprendre ce qu'il applique sur son cuir chevelu."
            if is_fr else
            "Unlike food where ingredients are expressed in familiar words (wheat, sugar, olive oil), personal care items mandate INCI nomenclature: an obscure blend of Latin botanical names and chemical codes. Without a degree in chemistry, it is virtually impossible for shoppers to know what touches their scalp and hair every morning."
        ),
        "latin_p2": (
            "Open Beauty Facts a été bâti pour combler ce gouffre : traduire « Aqua » en eau, repérer le phénoxyéthanol, les parabènes, les sulfates décapants (SLS/SLES) et les 26 substances parfumantes allergènes à déclaration obligatoire en Europe."
            if is_fr else
            "Open Beauty Facts was built to bridge this knowledge gap: translating 'Aqua' into water, highlighting phenoxyethanol, parabens, stripping sulfates (SLS/SLES), and the 26 mandatory fragrance allergens regulated under European consumer law."
        ),
        
        "inq_title": "Les Révélations de l'Enquête Cosmétique" if is_fr else "Core Insights from the Shampoo Expedition",
        "goals_title": "Objectifs Mondiaux du Projet" if is_fr else "Worldwide Mission Milestones",
        "btn_obf": "Visiter Open Beauty Facts" if is_fr else "Explore Open Beauty Facts",
        "btn_scan": "Rejoindre une Scan Party" if is_fr else "Join a Scan Party",
    }
    
    questions = data.get("key_questions", [])
    goals = data.get("global_goals", [])
    
    questions_html = ""
    for q in questions:
        q_text = q.get(f"question_{lang}", q.get("question_en"))
        f_text = q.get(f"finding_{lang}", q.get("finding_en"))
        questions_html += f"""
        <div class="off-card off-inq-card">
          <div class="off-inq-q">🧴 {q_text}</div>
          <div class="off-inq-a">💡 {f_text}</div>
        </div>
        """
        
    goals_html = ""
    for g in goals:
        g_text = g.get(f"goal_{lang}", g.get("goal_en"))
        goals_html += f"""
        <div class="off-card" style="border-left: 4px solid var(--off-purple);">
          <div style="font-weight: 700; font-size: 1rem; color: #581c87;">🎯 {g_text}</div>
        </div>
        """

    return f"""<style>
/* What's In My Shampoo Revamped Showcase Styles */
.off-sh-wrap {{
  --off-espresso: #0f172a;
  --off-purple: #9333ea;
  --off-purple-dark: #7e22ce;
  --off-purple-light: #fdf4ff;
  --off-purple-border: #f0abfc;
  --off-border: #e2e8f0;
  --off-surface: #ffffff;
  --off-radius: 20px;
  
  max-width: 1200px;
  margin: 0 auto 3.5rem auto;
  padding: 0 1rem;
  color: var(--off-espresso);
  font-family: "Plus Jakarta Sans", "Open Sans", -apple-system, BlinkMacSystemFont, sans-serif;
  line-height: 1.6;
}}

.off-sh-hero {{
  background: linear-gradient(180deg, #ffffff 0%, var(--off-purple-light) 100%);
  border: 1px solid var(--off-purple-border);
  border-radius: 28px;
  padding: clamp(2rem, 4vw, 3.5rem);
  text-align: center;
  margin: 1.5rem 0 2.5rem 0;
  box-shadow: 0 8px 30px rgba(147, 51, 234, 0.06);
}}

.off-badge-purple {{
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  background: #fae8ff;
  color: var(--off-purple-dark);
  border: 1px solid var(--off-purple-border);
  padding: 0.4rem 1rem;
  border-radius: 9999px;
  font-size: 0.85rem;
  font-weight: 700;
  letter-spacing: 0.03em;
  text-transform: uppercase;
  margin-bottom: 1.25rem;
}}

.off-sh-hero h1 {{
  font-size: clamp(2.2rem, 4.5vw, 3.5rem);
  font-weight: 800;
  color: #581c87;
  margin: 0 0 1rem 0;
  line-height: 1.15;
}}

.off-sh-hero p.lead {{
  font-size: clamp(1.05rem, 1.8vw, 1.25rem);
  color: #334155;
  max-width: 860px;
  margin: 0 auto 2rem auto;
}}

.off-stats-grid {{
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
  gap: 1.25rem;
  margin-top: 2rem;
}}

.off-stat-card {{
  background: var(--off-surface);
  border: 1px solid var(--off-border);
  border-radius: var(--off-radius);
  padding: 1.5rem;
  text-align: center;
  box-shadow: 0 4px 12px rgba(0,0,0,0.02);
  transition: transform 0.2s, box-shadow 0.2s;
}}
.off-stat-card:hover {{
  transform: translateY(-3px);
  box-shadow: 0 8px 24px rgba(147, 51, 234, 0.08);
}}
.off-stat-num-purple {{
  font-size: 2.2rem;
  font-weight: 800;
  color: var(--off-purple);
  line-height: 1;
  margin-bottom: 0.35rem;
}}
.off-stat-lbl {{
  font-size: 1rem;
  font-weight: 700;
  color: #0f172a;
  margin-bottom: 0.25rem;
}}
.off-stat-sub {{
  font-size: 0.82rem;
  color: #64748b;
}}

.off-section {{
  margin: 3.5rem 0;
}}
.off-section-title {{
  font-size: 1.85rem;
  font-weight: 800;
  color: #581c87;
  margin-bottom: 0.75rem;
  text-align: center;
}}
.off-section-lead {{
  text-align: center;
  font-size: 1.05rem;
  color: #475569;
  max-width: 800px;
  margin: 0 auto 2rem auto;
}}

.off-card {{
  background: var(--off-surface);
  border: 1px solid var(--off-border);
  border-radius: var(--off-radius);
  padding: 1.5rem;
  box-shadow: 0 4px 16px rgba(0,0,0,0.02);
}}
.off-inq-card {{
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}}
.off-inq-q {{
  font-size: 1.05rem;
  font-weight: 700;
  color: #581c87;
}}
.off-inq-a {{
  font-size: 0.92rem;
  color: #334155;
  background: #faf5ff;
  padding: 0.85rem;
  border-radius: 12px;
  border-left: 3px solid var(--off-purple);
}}

.off-btn {{
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.85rem 1.75rem;
  border-radius: 9999px;
  font-weight: 700;
  font-size: 0.95rem;
  text-decoration: none;
  transition: all 0.2s;
  cursor: pointer;
}}
.off-btn-purple {{
  background: var(--off-purple);
  color: #ffffff;
}}
.off-btn-purple:hover {{
  background: var(--off-purple-dark);
  color: #ffffff;
}}
.off-btn-secondary {{
  background: #ffffff;
  color: #0f172a;
  border: 1px solid var(--off-border);
}}
.off-btn-secondary:hover {{
  background: #f8fafc;
}}

.off-legacy-banner-purple {{
  background: linear-gradient(135deg, #fdf4ff 0%, #fae8ff 100%);
  border: 1px solid #f0abfc;
  border-radius: 24px;
  padding: clamp(2rem, 3.5vw, 3rem);
  text-align: center;
  margin-top: 3.5rem;
}}
.off-legacy-title-purple {{
  font-size: 1.6rem;
  font-weight: 800;
  color: #701a75;
  margin-bottom: 0.75rem;
}}
.off-legacy-desc-purple {{
  font-size: 1.05rem;
  color: #86198f;
  max-width: 800px;
  margin: 0 auto 1.5rem auto;
}}
.off-legacy-actions {{
  display: flex;
  gap: 1rem;
  justify-content: center;
  flex-wrap: wrap;
}}
</style>

<div class="off-sh-wrap">
  <!-- Hero Section -->
  <div class="off-sh-hero">
    <div class="off-badge-purple">{t["eyebrow"]}</div>
    <h1>{t["title"]}</h1>
    <p class="lead">{t["lead"]}</p>
    
    <div class="off-stats-grid">
      <div class="off-stat-card">
        <div class="off-stat-num-purple">{t["stat_shampoos_num"]}</div>
        <div class="off-stat-lbl">{t["stat_shampoos_lbl"]}</div>
        <div class="off-stat-sub">{t["stat_shampoos_sub"]}</div>
      </div>
      <div class="off-stat-card">
        <div class="off-stat-num-purple">{t["stat_comp_num"]}</div>
        <div class="off-stat-lbl">{t["stat_comp_lbl"]}</div>
        <div class="off-stat-sub">{t["stat_comp_sub"]}</div>
      </div>
      <div class="off-stat-card">
        <div class="off-stat-num-purple">{t["stat_inci_num"]}</div>
        <div class="off-stat-lbl">{t["stat_inci_lbl"]}</div>
        <div class="off-stat-sub">{t["stat_inci_sub"]}</div>
      </div>
      <div class="off-stat-card">
        <div class="off-stat-num-purple">{t["stat_gouv_num"]}</div>
        <div class="off-stat-lbl">{t["stat_gouv_lbl"]}</div>
        <div class="off-stat-sub">{t["stat_gouv_sub"]}</div>
      </div>
    </div>
  </div>

  <!-- Why Bathroom / Deciphering Latin -->
  <div class="off-section">
    <div class="off-card" style="display: flex; flex-wrap: wrap; gap: 2rem; align-items: center;">
      <div style="flex: 1 1 400px;">
        <h3 style="font-size: 1.5rem; font-weight: 800; color: #581c87; margin-top: 0;">{t["latin_title"]}</h3>
        <p style="color: #334155; font-size: 0.98rem;">{t["latin_p1"]}</p>
        <p style="color: #334155; font-size: 0.98rem;">{t["latin_p2"]}</p>
      </div>
      <div style="flex: 0 0 280px; text-align: center; margin: 0 auto;">
        <img src="https://world.openfoodfacts.org/images/misc/open-beauty-facts-logo.png" alt="Open Beauty Facts Logo" style="max-width: 220px; height: auto; border-radius: 16px; box-shadow: 0 4px 14px rgba(0,0,0,0.08);">
      </div>
    </div>
  </div>

  <!-- Key Discoveries -->
  <div class="off-section">
    <h3 class="off-section-title">{t["inq_title"]}</h3>
    <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(320px, 1fr)); gap: 1.5rem;">
      {questions_html}
    </div>
  </div>

  <!-- Worldwide Goals -->
  <div class="off-section">
    <h3 class="off-section-title">{t["goals_title"]}</h3>
    <div style="display: flex; flex-direction: column; gap: 1rem; max-width: 860px; margin: 0 auto;">
      {goals_html}
    </div>
  </div>

  <!-- Bottom CTA Banner -->
  <div class="off-legacy-banner-purple">
    <div class="off-legacy-title-purple">🧴 {"Envie d'ouvrir les cosmétiques de votre salle de bain ?" if is_fr else "Ready to open the personal care products in your home?"}</div>
    <div class="off-legacy-desc-purple">
      {"Consultez la base de données ouverte Open Beauty Facts ou organisez un atelier de scan collaboratif !" if is_fr else "Search the Open Beauty Facts public database or organize a collaborative scan party!"}
    </div>
    <div class="off-legacy-actions">
      <a href="https://world.openbeautyfacts.org" target="_blank" rel="noopener noreferrer" class="off-btn off-btn-purple">🔍 {t["btn_obf"]}</a>
      <a href="scan-parties.html" class="off-btn off-btn-secondary">🎉 {t["btn_scan"]}</a>
    </div>
  </div>
</div>
"""

def compile_campaign_pages(verbose=True):
    if verbose:
        print("🚀 Compiling Campaign Pages from YAML...")

    # 1. Opération Sodas
    sodas_data = load_mission("operation-sodas")
    en_sodas = generate_operation_sodas_html(sodas_data, lang="en")
    fr_sodas = generate_operation_sodas_html(sodas_data, lang="fr")
    root_sodas = render_standalone_wrapper("Opération Sodas", "fr", fr_sodas)
    
    with open(os.path.join(REPO_ROOT, "lang", "en", "texts", "operation-sodas.html"), "w", encoding="utf-8") as f:
        f.write(en_sodas)
    with open(os.path.join(REPO_ROOT, "lang", "fr", "texts", "operation-sodas.html"), "w", encoding="utf-8") as f:
        f.write(fr_sodas)
    with open(os.path.join(REPO_ROOT, "operation-sodas.html"), "w", encoding="utf-8") as f:
        f.write(root_sodas)
    if verbose:
        print("  ✅ Opération Sodas compiled (lang/en, lang/fr, root)")

    # 2. What's in my yogurt?
    yogurt_data = load_mission("whats-in-my-yogurt")
    en_yogurt = generate_whats_in_my_yogurt_html(yogurt_data, lang="en")
    fr_yogurt = generate_whats_in_my_yogurt_html(yogurt_data, lang="fr")
    root_yogurt = render_standalone_wrapper("What's in my yogurt?", "en", en_yogurt)
    
    with open(os.path.join(REPO_ROOT, "lang", "en", "texts", "whats-in-my-yogurt.html"), "w", encoding="utf-8") as f:
        f.write(en_yogurt)
    with open(os.path.join(REPO_ROOT, "lang", "fr", "texts", "whats-in-my-yogurt.html"), "w", encoding="utf-8") as f:
        f.write(fr_yogurt)
    with open(os.path.join(REPO_ROOT, "whats-in-my-yogurt.html"), "w", encoding="utf-8") as f:
        f.write(root_yogurt)
    if verbose:
        print("  ✅ What's in my yogurt? compiled (lang/en, lang/fr, root)")

    # 3. What's in my shampoo?
    shampoo_data = load_mission("whats-in-my-shampoo")
    en_shampoo = generate_whats_in_my_shampoo_html(shampoo_data, lang="en")
    fr_shampoo = generate_whats_in_my_shampoo_html(shampoo_data, lang="fr")
    root_shampoo = render_standalone_wrapper("What's in my shampoo?", "en", en_shampoo)
    
    obf_en_dir = os.path.join(REPO_ROOT, "lang", "obf", "en", "texts")
    obf_fr_dir = os.path.join(REPO_ROOT, "lang", "obf", "fr", "texts")
    os.makedirs(obf_en_dir, exist_ok=True)
    os.makedirs(obf_fr_dir, exist_ok=True)

    with open(os.path.join(obf_en_dir, "whats-in-my-shampoo.html"), "w", encoding="utf-8") as f:
        f.write(en_shampoo)
    with open(os.path.join(obf_fr_dir, "whats-in-my-shampoo.html"), "w", encoding="utf-8") as f:
        f.write(fr_shampoo)
    with open(os.path.join(REPO_ROOT, "whats-in-my-shampoo.html"), "w", encoding="utf-8") as f:
        f.write(root_shampoo)
    if verbose:
        print("  ✅ What's in my shampoo? compiled (lang/obf/en, lang/obf/fr, root)")

    return True

def main():
    success = compile_campaign_pages(verbose=True)
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
