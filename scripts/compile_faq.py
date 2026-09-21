#!/usr/bin/env python3
"""
Compilation and validation system for Open Food Facts FAQ.
Reads Markdown files with YAML frontmatter from data/faq/<lang>/*.md,
validates schemas, compiles data/faq.json, and generates rich single-page
interactive HTML FAQ pages in lang/<lang>/texts/faq.html.

Usage:
    python3 scripts/compile_faq.py          # Validate and compile
    python3 scripts/compile_faq.py --check  # Validate only (CI)
"""

import glob
import json
import os
import re
import sys
import unicodedata
import yaml

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
DATA_DIR = os.path.join(REPO_ROOT, "data")
FAQ_DIR = os.path.join(DATA_DIR, "faq")
COMPILED_JSON = os.path.join(DATA_DIR, "faq.json")

SUPPORTED_LANGS = ["en", "fr", "es", "de", "it"]

UI_STRINGS = {
    "en": {
        "title": "Frequently Asked Questions",
        "subtitle": "Quick answers to everything you need to know about Open Food Facts, the mobile app, food scores, and the producers platform.",
        "search_placeholder": "🔍 Search questions or keywords (e.g. Nutri-Score, account, scan...)",
        "search_tip": "Press / to search",
        "all_questions": "All topics",
        "questions_count": "{n} questions",
        "filter_label": "Topics:",
        "expand_all": "Expand all",
        "collapse_all": "Collapse all",
        "copy_link": "Copy link to question",
        "link_copied": "Link copied!",
        "no_results": "No questions match your search query",
        "clear_search": "Clear search",
        "still_questions": "Still have questions?",
        "still_sub": "Can't find what you're looking for? Join our welcoming community on Slack or get in touch with our team directly.",
        "btn_slack": "💬 Join our Slack",
        "btn_forum": "🗣️ Community Forum",
        "btn_email": "✉️ Email the Team",
        "results_stats": "Showing {shown} of {total} questions",
    },
    "fr": {
        "title": "Foire Aux Questions (FAQ)",
        "subtitle": "Trouvez rapidement des réponses à toutes vos questions sur Open Food Facts, l'application mobile, les scores nutritionnels et notre plateforme producteurs.",
        "search_placeholder": "🔍 Rechercher une question, un mot-clé (ex: Nutri-Score, compte, scanner...)",
        "search_tip": "Appuyez sur / pour rechercher",
        "all_questions": "Toutes les thématiques",
        "questions_count": "{n} questions",
        "filter_label": "Thématiques :",
        "expand_all": "Tout déplier",
        "collapse_all": "Tout replier",
        "copy_link": "Copier le lien",
        "link_copied": "Lien copié !",
        "no_results": "Aucune question ne correspond à votre recherche",
        "clear_search": "Réinitialiser la recherche",
        "still_questions": "Vous avez encore une question ?",
        "still_sub": "Vous ne trouvez pas ce que vous cherchez ? Rejoignez notre communauté bienveillante sur Slack ou contactez directement l'équipe.",
        "btn_slack": "💬 Rejoindre notre Slack",
        "btn_forum": "🗣️ Forum de discussion",
        "btn_email": "✉️ Écrire à l'équipe",
        "results_stats": "{shown} sur {total} questions affichées",
    },
    "es": {
        "title": "Preguntas Frecuentes (FAQ)",
        "subtitle": "Respuestas a las dudas más habituales sobre Open Food Facts, la app móvil, puntuaciones nutricionales y la plataforma de productores.",
        "search_placeholder": "🔍 Buscar preguntas o palabras clave (ej: Nutri-Score, cuenta, escaneo...)",
        "search_tip": "Pulsa / para buscar",
        "all_questions": "Todos los temas",
        "questions_count": "{n} preguntas",
        "filter_label": "Temas:",
        "expand_all": "Desplegar todo",
        "collapse_all": "Plegar todo",
        "copy_link": "Copiar enlace",
        "link_copied": "¡Enlace copiado!",
        "no_results": "No se encontraron preguntas que coincidan con la búsqueda",
        "clear_search": "Restablecer búsqueda",
        "still_questions": "¿Tienes más preguntas?",
        "still_sub": "¿No encuentras lo que buscas? Únete a nuestra comunidad en Slack o escribe directamente a nuestro equipo.",
        "btn_slack": "💬 Unirse a Slack",
        "btn_forum": "🗣️ Foro comunitario",
        "btn_email": "✉️ Escribir al equipo",
        "results_stats": "Mostrando {shown} de {total} preguntas",
    },
    "de": {
        "title": "Häufig gestellte Fragen (FAQ)",
        "subtitle": "Schnelle Antworten auf Fragen rund um Open Food Facts, die App, Scores und die Hersteller-Plattform.",
        "search_placeholder": "🔍 Fragen oder Stichworte suchen (z. B. Nutri-Score, Konto, Scannen...)",
        "search_tip": "Drücke / zum Suchen",
        "all_questions": "Alle Themen",
        "questions_count": "{n} Fragen",
        "filter_label": "Themen:",
        "expand_all": "Alle ausklappen",
        "collapse_all": "Alle einklappen",
        "copy_link": "Link kopieren",
        "link_copied": "Link kopiert!",
        "no_results": "Keine passenden Fragen gefunden",
        "clear_search": "Suche zurücksetzen",
        "still_questions": "Haben Sie weitere Fragen?",
        "still_sub": "Nicht fündig geworden? Treten Sie unserer Community auf Slack bei oder kontaktieren Sie das Team.",
        "btn_slack": "💬 Slack beitreten",
        "btn_forum": "🗣️ Community-Forum",
        "btn_email": "✉️ E-Mail an das Team",
        "results_stats": "{shown} von {total} Fragen angezeigt",
    },
    "it": {
        "title": "Domande Frequenti (FAQ)",
        "subtitle": "Risposte a tutte le domande su Open Food Facts, l'applicazione mobile, i punteggi nutrizionali e la piattaforma per i produttori.",
        "search_placeholder": "🔍 Cerca domande o parole chiave (es. Nutri-Score, account, scansione...)",
        "search_tip": "Premi / per cercare",
        "all_questions": "Tutti gli argomenti",
        "questions_count": "{n} domande",
        "filter_label": "Argomenti:",
        "expand_all": "Espandi tutto",
        "collapse_all": "Comprimi tutto",
        "copy_link": "Copia link",
        "link_copied": "Link copiato!",
        "no_results": "Nessuna domanda corrispondente alla ricerca",
        "clear_search": "Reimposta ricerca",
        "still_questions": "Hai ancora domande?",
        "still_sub": "Non hai trovato quello che cerchi? Unisciti alla nostra community su Slack o contatta direttamente il nostro team.",
        "btn_slack": "💬 Unisciti a Slack",
        "btn_forum": "🗣️ Forum della community",
        "btn_email": "✉️ Scrivi al team",
        "results_stats": "{shown} di {total} domande visualizzate",
    }
}

def slugify(text, max_len=60):
    text = unicodedata.normalize("NFKD", str(text)).encode("ascii", "ignore").decode("ascii")
    text = re.sub(r"[^\w\s-]", "", text.lower()).strip()
    slug = re.sub(r"[-\s]+", "-", text)
    return slug[:max_len].rstrip("-")

def md_to_html(md_text):
    """
    Zero-dependency robust markdown to HTML converter for FAQ answers.
    Handles paragraphs, bold, italic, links, lists, code blocks, and blockquotes.
    """
    lines = md_text.splitlines()
    html_out = []
    in_list = False
    list_type = None
    para_lines = []

    def format_inline(text):
        # Images: ![alt](url)
        text = re.sub(r'!\[([^\]]*)\]\(([^)]+)\)', r'<img src="\2" alt="\1" class="faq-img" loading="lazy" />', text)
        # Bold: **bold** or __bold__
        text = re.sub(r'(\*\*|__)(.*?)\1', r'<strong>\2</strong>', text)
        # Italic: *italic* or _italic_ (avoiding intra-word underscores)
        text = re.sub(r'(?<!\w)(\*|_)(?!\s)(.*?)(?<!\s)\1(?!\w)', r'<em>\2</em>', text)
        # Inline code: `code`
        text = re.sub(r'`([^`]+)`', r'<code>\1</code>', text)
        # Links: [title](url)
        def link_repl(m):
            t, u = m.group(1), m.group(2)
            is_ext = u.startswith("http") or u.startswith("mailto:")
            target = ' target="_blank" rel="noopener noreferrer"' if u.startswith("http") else ""
            return f'<a href="{u}"{target}>{t}</a>'
        text = re.sub(r'\[([^\]]+)\]\(([^)]+)\)', link_repl, text)
        return text

    def flush_para():
        nonlocal para_lines
        if para_lines:
            content = " ".join(para_lines).strip()
            if content:
                content = format_inline(content)
                html_out.append(f"<p>{content}</p>")
            para_lines = []

    def flush_list():
        nonlocal in_list, list_type
        if in_list:
            html_out.append(f"</{list_type}>")
            in_list = False
            list_type = None

    for line in lines:
        stripped = line.strip()
        if not stripped or stripped == "---":
            flush_para()
            flush_list()
            continue

        # Unordered list: - or *
        ul_match = re.match(r"^[-*•]\s+(.*)$", stripped)
        if ul_match:
            flush_para()
            if not in_list or list_type != "ul":
                flush_list()
                html_out.append('<ul class="faq-list">')
                in_list = True
                list_type = "ul"
            item_text = format_inline(ul_match.group(1).strip())
            html_out.append(f"<li>{item_text}</li>")
            continue

        # Ordered list: 1. or 2.
        ol_match = re.match(r"^\d+\.\s+(.*)$", stripped)
        if ol_match:
            flush_para()
            if not in_list or list_type != "ol":
                flush_list()
                html_out.append('<ol class="faq-list">')
                in_list = True
                list_type = "ol"
            item_text = format_inline(ol_match.group(1).strip())
            html_out.append(f"<li>{item_text}</li>")
            continue

        # Blockquote: > quote
        if stripped.startswith(">"):
            flush_para()
            flush_list()
            quote_text = format_inline(stripped.lstrip("> ").strip())
            html_out.append(f'<blockquote class="faq-quote">{quote_text}</blockquote>')
            continue

        flush_list()
        para_lines.append(stripped)

    flush_para()
    flush_list()
    return "\n".join(html_out)

def load_faq_for_lang(lang_code):
    lang_dir = os.path.join(FAQ_DIR, lang_code)
    if not os.path.isdir(lang_dir):
        return [], [f"Language directory does not exist: {lang_dir}"], []

    md_files = sorted(glob.glob(f"{lang_dir}/**/*.md", recursive=True))
    categories = []
    errors = []
    warnings = []
    seen_q_slugs = set()

    for fpath in md_files:
        if os.path.basename(fpath) == "index.md":
            continue

        rel_path = os.path.relpath(fpath, lang_dir)
        try:
            with open(fpath, "r", encoding="utf-8") as f:
                content = f.read()
        except Exception as e:
            errors.append(f"Could not read {fpath}: {e}")
            continue

        if not content.startswith("---"):
            errors.append(f"{rel_path}: Missing frontmatter delimiter '---'")
            continue

        parts = content.split("---", 2)
        if len(parts) < 3:
            errors.append(f"{rel_path}: Malformed frontmatter")
            continue

        try:
            fm = yaml.safe_load(parts[1]) or {}
        except Exception as e:
            errors.append(f"{rel_path}: YAML parsing error in frontmatter: {e}")
            continue

        body = parts[2].strip()

        cat_id = fm.get("id") or os.path.basename(fpath).split(".")[0]
        cat_title = fm.get("title") or cat_id.replace("-", " ").title()
        cat_icon = fm.get("icon") or "❓"
        cat_order = fm.get("order", 999)

        # Parse questions in body
        # Each question starts with "## Question Title"
        sections = re.split(r"(?m)^##\s+", "\n" + body)
        q_list = []
        for sec in sections:
            sec = sec.strip()
            if not sec:
                continue
            lines = sec.splitlines()
            q_title = lines[0].strip()
            # Clean possible trailing # or whitespace
            q_title = q_title.rstrip("#").strip()
            q_answer_md = "\n".join(lines[1:]).strip()

            if not q_title:
                warnings.append(f"{rel_path}: Found section with empty question title")
                continue

            base_slug = slugify(q_title)
            if not base_slug:
                base_slug = f"q-{len(q_list)+1}"

            q_slug = base_slug
            idx = 2
            while q_slug in seen_q_slugs:
                q_slug = f"{base_slug}-{idx}"
                idx += 1
            seen_q_slugs.add(q_slug)

            q_answer_html = md_to_html(q_answer_md)

            q_list.append({
                "id": q_slug,
                "category_id": cat_id,
                "category_title": cat_title,
                "question": q_title,
                "answer_markdown": q_answer_md,
                "answer_html": q_answer_html
            })

        if not q_list:
            warnings.append(f"{rel_path}: Category '{cat_title}' has no questions")

        categories.append({
            "id": cat_id,
            "title": cat_title,
            "icon": cat_icon,
            "order": cat_order,
            "file": rel_path,
            "questions": q_list
        })

    # Sort categories by order
    categories.sort(key=lambda c: (c.get("order", 999), c.get("title", "")))

    return categories, errors, warnings

def build_faq_html(lang, categories):
    t = UI_STRINGS.get(lang, UI_STRINGS["en"])
    
    # Collect all questions flat
    all_questions = []
    for c in categories:
        for q in c["questions"]:
            item = dict(q)
            item["category_icon"] = c["icon"]
            all_questions.append(item)

    total_count = len(all_questions)

    # Categories tabs/pills
    category_pills = []
    # "All" pill
    category_pills.append(
        f'<button type="button" class="faq-pill active" data-cat="all">'
        f'<span class="faq-pill-icon">✨</span> '
        f'<span class="faq-pill-text">{t["all_questions"]}</span> '
        f'<span class="faq-pill-count">{total_count}</span>'
        f'</button>'
    )

    for c in categories:
        q_count = len(c["questions"])
        if q_count == 0:
            continue
        category_pills.append(
            f'<button type="button" class="faq-pill" data-cat="{c["id"]}">'
            f'<span class="faq-pill-icon">{c["icon"]}</span> '
            f'<span class="faq-pill-text">{c["title"]}</span> '
            f'<span class="faq-pill-count">{q_count}</span>'
            f'</button>'
        )

    category_pills_html = "\n".join(category_pills)

    # Accordions HTML
    faq_items_html = []
    for q in all_questions:
        q_id = q["id"]
        c_id = q["category_id"]
        c_title = q["category_title"]
        c_icon = q["category_icon"]
        q_title = q["question"]
        ans_html = q["answer_html"]

        faq_items_html.append(f"""
        <article class="faq-card" id="{q_id}" data-category="{c_id}" data-search="{c_title.lower()} {q_title.lower()}">
          <details class="faq-details">
            <summary class="faq-summary">
              <div class="faq-question-header">
                <span class="faq-category-badge"><span class="faq-badge-icon">{c_icon}</span> {c_title}</span>
                <h3 class="faq-question-title">{q_title}</h3>
              </div>
              <div class="faq-summary-actions">
                <button type="button" class="faq-copy-btn" data-anchor="{q_id}" title="{t['copy_link']}" aria-label="{t['copy_link']}">
                  <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                    <path d="M10 13a5 5 0 0 0 7.54.54l3-3a5 5 0 0 0-7.07-7.07l-1.72 1.71"></path>
                    <path d="M14 11a5 5 0 0 0-7.54-.54l-3 3a5 5 0 0 0 7.07 7.07l1.71-1.71"></path>
                  </svg>
                  <span class="faq-copied-tooltip">{t['link_copied']}</span>
                </button>
                <span class="faq-chevron" aria-hidden="true"></span>
              </div>
            </summary>
            <div class="faq-answer">
              <div class="faq-answer-inner">
                {ans_html}
              </div>
            </div>
          </details>
        </article>
        """)

    items_joined = "\n".join(faq_items_html)

    return f"""
<style>
/* ==========================================================================
   Open Food Facts FAQ - Responsive Single Page Styles
   ========================================================================== */

:root {{
  --off-green-900: #064e3b;
  --off-green-800: #065f46;
  --off-green-700: #047857;
  --off-green-600: #059669;
  --off-green-500: #10b981;
  --off-green-100: #d1fae5;
  --off-green-50: #ecfdf5;
  --off-surface: #ffffff;
  --off-bg: #f8fafc;
  --off-card-border: #e2e8f0;
  --off-card-border-hover: #cbd5e1;
  --off-text-primary: #0f172a;
  --off-text-secondary: #475569;
  --off-text-muted: #64748b;
  --off-accent: #2563eb;
  --off-shadow-sm: 0 1px 3px rgba(0,0,0,0.05);
  --off-shadow-md: 0 4px 12px rgba(0,0,0,0.06);
  --off-shadow-hover: 0 8px 24px rgba(4, 120, 87, 0.08);
  --off-radius-card: 14px;
  --off-radius-pill: 9999px;
  --off-pulse-bg: #fef08a;
}}

.faq-wrapper {{
  max-width: 980px;
  margin: 0 auto;
  padding: 1.5rem 1rem 4rem;
  color: var(--off-text-primary);
  font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Oxygen, Ubuntu, Cantarell, "Open Sans", "Helvetica Neue", sans-serif;
  line-height: 1.6;
}}

/* Hero Section */
.faq-hero {{
  text-align: center;
  margin-bottom: 2rem;
}}
.faq-title {{
  font-size: 2.35rem;
  font-weight: 800;
  color: var(--off-green-900);
  letter-spacing: -0.025em;
  margin: 0 0 0.65rem;
  line-height: 1.2;
}}
.faq-subtitle {{
  font-size: 1.1rem;
  color: var(--off-text-secondary);
  max-width: 680px;
  margin: 0 auto 1.5rem;
}}

/* Search Box */
.faq-search-box {{
  position: relative;
  max-width: 650px;
  margin: 0 auto 1.25rem;
}}
.faq-search-input {{
  width: 100%;
  padding: 0.95rem 4.5rem 0.95rem 2.85rem;
  font-size: 1.05rem;
  color: var(--off-text-primary);
  background: var(--off-surface);
  border: 2px solid var(--off-card-border);
  border-radius: var(--off-radius-pill);
  box-shadow: var(--off-shadow-md);
  transition: all 0.2s ease;
  outline: none;
  box-sizing: border-box;
}}
.faq-search-input:focus {{
  border-color: var(--off-green-600);
  box-shadow: 0 0 0 4px rgba(16, 185, 129, 0.15);
}}
.faq-search-icon {{
  position: absolute;
  left: 1.05rem;
  top: 50%;
  transform: translateY(-50%);
  color: var(--off-text-muted);
  pointer-events: none;
  font-size: 1.15rem;
}}
.faq-search-clear {{
  position: absolute;
  right: 1.1rem;
  top: 50%;
  transform: translateY(-50%);
  background: #f1f5f9;
  border: none;
  border-radius: 50%;
  width: 26px;
  height: 26px;
  cursor: pointer;
  color: var(--off-text-muted);
  font-weight: bold;
  font-size: 0.85rem;
  display: none;
  align-items: center;
  justify-content: center;
  transition: all 0.15s ease;
}}
.faq-search-clear:hover {{
  background: #e2e8f0;
  color: var(--off-text-primary);
}}
.faq-search-hint {{
  position: absolute;
  right: 1.2rem;
  top: 50%;
  transform: translateY(-50%);
  font-size: 0.72rem;
  font-weight: 700;
  color: var(--off-text-muted);
  background: #f1f5f9;
  padding: 0.18rem 0.45rem;
  border-radius: 6px;
  border: 1px solid #cbd5e1;
  pointer-events: none;
}}

/* Category Pills Bar */
.faq-pills-container {{
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
  justify-content: center;
  margin: 1.25rem 0 1.75rem;
  padding: 0.25rem;
}}
.faq-pill {{
  background: var(--off-surface);
  border: 1px solid var(--off-card-border);
  color: var(--off-text-secondary);
  border-radius: var(--off-radius-pill);
  padding: 0.42rem 0.85rem;
  font-size: 0.88rem;
  font-weight: 600;
  cursor: pointer;
  display: inline-flex;
  align-items: center;
  gap: 0.4rem;
  transition: all 0.18s ease;
  user-select: none;
}}
.faq-pill:hover {{
  background: #f1f5f9;
  border-color: var(--off-card-border-hover);
  color: var(--off-text-primary);
  transform: translateY(-1px);
}}
.faq-pill.active {{
  background: var(--off-green-700);
  border-color: var(--off-green-700);
  color: #ffffff;
  box-shadow: 0 2px 8px rgba(4, 120, 87, 0.25);
}}
.faq-pill-count {{
  font-size: 0.75rem;
  background: rgba(0,0,0,0.06);
  padding: 0.1rem 0.42rem;
  border-radius: var(--off-radius-pill);
}}
.faq-pill.active .faq-pill-count {{
  background: rgba(255,255,255,0.25);
  color: #ffffff;
}}

/* Toolbar Controls */
.faq-toolbar {{
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin: 0 0 1.25rem;
  padding: 0.5rem 0.25rem;
  border-bottom: 1px solid var(--off-card-border);
  font-size: 0.88rem;
}}
.faq-counter-text {{
  color: var(--off-text-muted);
  font-weight: 600;
}}
.faq-toolbar-actions {{
  display: flex;
  gap: 0.5rem;
}}
.faq-tool-btn {{
  background: transparent;
  border: 1px solid var(--off-card-border);
  color: var(--off-text-secondary);
  border-radius: 8px;
  padding: 0.35rem 0.75rem;
  font-size: 0.82rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.15s ease;
}}
.faq-tool-btn:hover {{
  background: #f1f5f9;
  color: var(--off-text-primary);
}}

/* FAQ Accordion List */
.faq-list-container {{
  display: flex;
  flex-direction: column;
  gap: 0.85rem;
}}
.faq-card {{
  background: var(--off-surface);
  border: 1px solid var(--off-card-border);
  border-radius: var(--off-radius-card);
  box-shadow: var(--off-shadow-sm);
  transition: border-color 0.2s ease, box-shadow 0.2s ease, transform 0.2s ease;
  overflow: hidden;
}}
.faq-card:hover {{
  border-color: var(--off-green-500);
  box-shadow: var(--off-shadow-hover);
}}
.faq-card.faq-target {{
  border-color: var(--off-green-600);
  box-shadow: 0 0 0 3px rgba(16, 185, 129, 0.35);
  animation: off-faq-pulse 2s ease;
}}
@keyframes off-faq-pulse {{
  0% {{ background-color: #fef08a; }}
  100% {{ background-color: var(--off-surface); }}
}}

.faq-details {{
  width: 100%;
}}
.faq-summary {{
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 1.1rem 1.25rem;
  cursor: pointer;
  list-style: none;
  gap: 1rem;
}}
.faq-summary::-webkit-details-marker {{
  display: none;
}}
.faq-question-header {{
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  gap: 0.35rem;
  flex: 1;
}}
.faq-category-badge {{
  font-size: 0.76rem;
  font-weight: 700;
  color: var(--off-green-800);
  background: var(--off-green-50);
  border: 1px solid var(--off-green-100);
  padding: 0.15rem 0.5rem;
  border-radius: 6px;
  display: inline-flex;
  align-items: center;
  gap: 0.3rem;
  text-transform: uppercase;
  letter-spacing: 0.03em;
}}
.faq-question-title {{
  margin: 0;
  font-size: 1.08rem;
  font-weight: 700;
  color: var(--off-text-primary);
  line-height: 1.35;
}}
.faq-summary-actions {{
  display: flex;
  align-items: center;
  gap: 0.6rem;
  flex-shrink: 0;
}}
.faq-copy-btn {{
  position: relative;
  background: transparent;
  border: 1px solid transparent;
  color: var(--off-text-muted);
  border-radius: 6px;
  padding: 0.35rem;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.15s ease;
}}
.faq-copy-btn:hover {{
  background: #f1f5f9;
  border-color: #cbd5e1;
  color: var(--off-text-primary);
}}
.faq-copied-tooltip {{
  position: absolute;
  bottom: 125%;
  right: 0;
  background: #0f172a;
  color: #ffffff;
  font-size: 0.72rem;
  font-weight: 600;
  padding: 0.2rem 0.5rem;
  border-radius: 4px;
  white-space: nowrap;
  opacity: 0;
  pointer-events: none;
  transition: opacity 0.2s ease;
}}
.faq-copy-btn.copied .faq-copied-tooltip {{
  opacity: 1;
}}
.faq-chevron {{
  width: 10px;
  height: 10px;
  border-right: 2px solid var(--off-text-muted);
  border-bottom: 2px solid var(--off-text-muted);
  transform: rotate(45deg);
  transition: transform 0.25s ease;
  margin-left: 0.25rem;
}}
.faq-details[open] .faq-chevron {{
  transform: rotate(-135deg);
}}

/* Answer Drawer */
.faq-answer {{
  padding: 0 1.25rem 1.25rem;
  border-top: 1px solid #f1f5f9;
}}
.faq-answer-inner {{
  padding-top: 1rem;
  color: var(--off-text-secondary);
  font-size: 0.98rem;
  line-height: 1.68;
}}
.faq-answer-inner p {{
  margin: 0 0 0.85rem;
}}
.faq-answer-inner p:last-child {{
  margin-bottom: 0;
}}
.faq-answer-inner a {{
  color: var(--off-green-700);
  font-weight: 600;
  text-decoration: underline;
  text-underline-offset: 2px;
}}
.faq-answer-inner a:hover {{
  color: var(--off-green-900);
}}
.faq-list {{
  margin: 0.5rem 0 1rem 1.35rem;
  padding: 0;
}}
.faq-list li {{
  margin-bottom: 0.35rem;
}}
.faq-quote {{
  margin: 0.75rem 0;
  padding: 0.5rem 1rem;
  border-left: 4px solid var(--off-green-600);
  background: var(--off-green-50);
  border-radius: 0 8px 8px 0;
  color: var(--off-green-900);
  font-style: italic;
}}
.faq-answer-inner code {{
  background: #f1f5f9;
  color: #0f172a;
  padding: 0.15rem 0.35rem;
  border-radius: 4px;
  font-size: 0.88em;
  font-family: monospace;
}}
.faq-img {{
  max-width: 100%;
  height: auto;
  border-radius: 8px;
  margin: 0.75rem 0;
  border: 1px solid var(--off-card-border);
}}

/* Highlight Match */
mark.faq-highlight {{
  background-color: #fef08a;
  color: #0f172a;
  padding: 0.05rem 0.2rem;
  border-radius: 3px;
}}

/* Empty State */
.faq-empty-state {{
  text-align: center;
  padding: 3.5rem 1.5rem;
  background: var(--off-surface);
  border: 2px dashed var(--off-card-border);
  border-radius: var(--off-radius-card);
  display: none;
}}
.faq-empty-icon {{
  font-size: 3rem;
  margin-bottom: 0.5rem;
}}
.faq-empty-title {{
  font-size: 1.25rem;
  font-weight: 700;
  margin: 0 0 0.5rem;
}}
.faq-empty-btn {{
  background: var(--off-green-700);
  color: #ffffff;
  border: none;
  padding: 0.55rem 1.25rem;
  border-radius: var(--off-radius-pill);
  font-weight: 600;
  font-size: 0.92rem;
  cursor: pointer;
  margin-top: 1rem;
  transition: background 0.15s ease;
}}
.faq-empty-btn:hover {{
  background: var(--off-green-800);
}}

/* Footer Help CTA */
.faq-footer-cta {{
  margin-top: 3.5rem;
  padding: 2.25rem 1.75rem;
  background: linear-gradient(135deg, var(--off-green-50) 0%, #f0fdf4 100%);
  border: 1px solid var(--off-green-100);
  border-radius: var(--off-radius-card);
  text-align: center;
}}
.faq-footer-title {{
  font-size: 1.45rem;
  font-weight: 800;
  color: var(--off-green-900);
  margin: 0 0 0.5rem;
}}
.faq-footer-desc {{
  font-size: 1rem;
  color: var(--off-text-secondary);
  max-width: 600px;
  margin: 0 auto 1.5rem;
}}
.faq-footer-buttons {{
  display: flex;
  flex-wrap: wrap;
  gap: 0.75rem;
  justify-content: center;
}}
.faq-footer-btn {{
  display: inline-flex;
  align-items: center;
  gap: 0.45rem;
  padding: 0.65rem 1.25rem;
  border-radius: var(--off-radius-pill);
  font-weight: 700;
  font-size: 0.92rem;
  text-decoration: none;
  transition: all 0.18s ease;
}}
.faq-footer-btn-primary {{
  background: var(--off-green-700);
  color: #ffffff !important;
}}
.faq-footer-btn-primary:hover {{
  background: var(--off-green-800);
  transform: translateY(-1px);
}}
.faq-footer-btn-secondary {{
  background: var(--off-surface);
  border: 1px solid var(--off-card-border);
  color: var(--off-text-primary) !important;
}}
.faq-footer-btn-secondary:hover {{
  background: #f1f5f9;
  border-color: #cbd5e1;
  transform: translateY(-1px);
}}

@media (max-width: 640px) {{
  .faq-title {{
    font-size: 1.75rem;
  }}
  .faq-pills-container {{
    justify-content: flex-start;
    overflow-x: auto;
    flex-wrap: nowrap;
    padding-bottom: 0.5rem;
    -webkit-overflow-scrolling: touch;
  }}
  .faq-pill {{
    flex-shrink: 0;
  }}
  .faq-search-hint {{
    display: none;
  }}
  .faq-footer-buttons {{
    flex-direction: column;
  }}
  .faq-footer-btn {{
    width: 100%;
    justify-content: center;
  }}
}}
</style>

<div class="faq-wrapper" id="faq-app">
  <!-- Hero Section -->
  <header class="faq-hero">
    <h1 class="faq-title">{t["title"]}</h1>
    <p class="faq-subtitle">{t["subtitle"]}</p>

    <!-- Search Box -->
    <div class="faq-search-box">
      <span class="faq-search-icon" aria-hidden="true">🔍</span>
      <input type="search" id="faqSearchInput" class="faq-search-input" placeholder="{t['search_placeholder']}" autocomplete="off" />
      <button type="button" id="faqSearchClear" class="faq-search-clear" aria-label="{t['clear_search']}">✕</button>
      <span class="faq-search-hint">/</span>
    </div>

    <!-- Category Pills -->
    <nav class="faq-pills-container" aria-label="{t['filter_label']}">
      {category_pills_html}
    </nav>
  </header>

  <!-- Toolbar Controls -->
  <div class="faq-toolbar">
    <div class="faq-counter-text" id="faqCounter">{total_count} {t['all_questions'].lower()}</div>
    <div class="faq-toolbar-actions">
      <button type="button" class="faq-tool-btn" id="btnExpandAll">{t['expand_all']}</button>
      <button type="button" class="faq-tool-btn" id="btnCollapseAll">{t['collapse_all']}</button>
    </div>
  </div>

  <!-- FAQ Items Container -->
  <main class="faq-list-container" id="faqList">
    {items_joined}

    <!-- Empty Search State -->
    <div class="faq-empty-state" id="faqEmptyState">
      <div class="faq-empty-icon">🔎</div>
      <h3 class="faq-empty-title">{t['no_results']}</h3>
      <p class="faq-subtitle" id="faqEmptyQuery"></p>
      <button type="button" class="faq-empty-btn" id="faqResetSearchBtn">{t['clear_search']}</button>
    </div>
  </main>

  <!-- Contact Footer CTA -->
  <footer class="faq-footer-cta">
    <h2 class="faq-footer-title">{t['still_questions']}</h2>
    <p class="faq-footer-desc">{t['still_sub']}</p>
    <div class="faq-footer-buttons">
      <a href="https://slack.openfoodfacts.org/" target="_blank" rel="noopener noreferrer" class="faq-footer-btn faq-footer-btn-primary">{t['btn_slack']}</a>
      <a href="https://forum.openfoodfacts.org/" target="_blank" rel="noopener noreferrer" class="faq-footer-btn faq-footer-btn-secondary">{t['btn_forum']}</a>
      <a href="mailto:contact@openfoodfacts.org" class="faq-footer-btn faq-footer-btn-secondary">{t['btn_email']}</a>
    </div>
  </footer>
</div>

<script>
(function() {{
  const searchInput = document.getElementById("faqSearchInput");
  const searchClear = document.getElementById("faqSearchClear");
  const pills = document.querySelectorAll(".faq-pill");
  const cards = document.querySelectorAll(".faq-card");
  const counter = document.getElementById("faqCounter");
  const emptyState = document.getElementById("faqEmptyState");
  const emptyQuery = document.getElementById("faqEmptyQuery");
  const resetBtn = document.getElementById("faqResetSearchBtn");
  const btnExpandAll = document.getElementById("btnExpandAll");
  const btnCollapseAll = document.getElementById("btnCollapseAll");

  let activeCategory = "all";
  let currentSearch = "";

  function filterFaq() {{
    const query = currentSearch.trim().toLowerCase();
    let visibleCount = 0;

    cards.forEach(card => {{
      const cat = card.getAttribute("data-category");
      const searchData = card.getAttribute("data-search") || "";
      const textContent = card.innerText.toLowerCase();

      const matchesCat = (activeCategory === "all" || cat === activeCategory);
      const matchesQuery = !query || searchData.includes(query) || textContent.includes(query);

      if (matchesCat && matchesQuery) {{
        card.style.display = "";
        visibleCount++;
        // If user typed a search query of 2+ characters, auto-expand the match
        if (query.length >= 2) {{
          card.querySelector("details").open = true;
        }}
      }} else {{
        card.style.display = "none";
      }}
    }});

    // Update Counter
    if (counter) {{
      if (query || activeCategory !== "all") {{
        counter.textContent = visibleCount + " / {total_count} questions";
      }} else {{
        counter.textContent = "{total_count} questions";
      }}
    }}

    // Toggle Empty State
    if (emptyState) {{
      if (visibleCount === 0) {{
        emptyState.style.display = "block";
        if (emptyQuery) {{
          emptyQuery.textContent = query ? '“' + query + '”' : '';
        }}
      }} else {{
        emptyState.style.display = "none";
      }}
    }}

    // Toggle Clear Search button
    if (searchClear) {{
      searchClear.style.display = query ? "flex" : "none";
    }}
  }}

  // Category Pill Clicks
  pills.forEach(pill => {{
    pill.addEventListener("click", () => {{
      pills.forEach(p => p.classList.remove("active"));
      pill.classList.add("active");
      activeCategory = pill.getAttribute("data-cat") || "all";
      filterFaq();
    }});
  }});

  // Search Input Events
  if (searchInput) {{
    searchInput.addEventListener("input", (e) => {{
      currentSearch = e.target.value;
      filterFaq();
    }});

    // Keyboard shortcut: '/' focuses search input
    document.addEventListener("keydown", (e) => {{
      if (e.key === "/" && document.activeElement !== searchInput && document.activeElement.tagName !== "INPUT" && document.activeElement.tagName !== "TEXTAREA") {{
        e.preventDefault();
        searchInput.focus();
        searchInput.select();
      }}
      if (e.key === "Escape" && document.activeElement === searchInput) {{
        searchInput.value = "";
        currentSearch = "";
        filterFaq();
        searchInput.blur();
      }}
    }});
  }}

  if (searchClear) {{
    searchClear.addEventListener("click", () => {{
      if (searchInput) {{
        searchInput.value = "";
        searchInput.focus();
      }}
      currentSearch = "";
      filterFaq();
    }});
  }}

  if (resetBtn) {{
    resetBtn.addEventListener("click", () => {{
      if (searchInput) searchInput.value = "";
      currentSearch = "";
      activeCategory = "all";
      pills.forEach(p => p.classList.remove("active"));
      const allPill = document.querySelector('.faq-pill[data-cat="all"]');
      if (allPill) allPill.classList.add("active");
      filterFaq();
    }});
  }}

  // Expand / Collapse All
  if (btnExpandAll) {{
    btnExpandAll.addEventListener("click", () => {{
      cards.forEach(card => {{
        if (card.style.display !== "none") {{
          card.querySelector("details").open = true;
        }}
      }});
    }});
  }}

  if (btnCollapseAll) {{
    btnCollapseAll.addEventListener("click", () => {{
      cards.forEach(card => {{
        card.querySelector("details").open = false;
      }});
    }});
  }}

  // Copy Link Buttons
  document.querySelectorAll(".faq-copy-btn").forEach(btn => {{
    btn.addEventListener("click", (e) => {{
      e.stopPropagation();
      e.preventDefault();
      const anchor = btn.getAttribute("data-anchor");
      const url = window.location.origin + window.location.pathname + "#" + anchor;
      if (navigator.clipboard && navigator.clipboard.writeText) {{
        navigator.clipboard.writeText(url).then(() => {{
          btn.classList.add("copied");
          setTimeout(() => btn.classList.remove("copied"), 1800);
        }}).catch(() => {{}});
      }} else {{
        window.location.hash = anchor;
      }}
    }});
  }});

  // Deep Linking from URL Hash (#slug)
  function handleHashTarget() {{
    const hash = window.location.hash ? window.location.hash.substring(1) : "";
    if (!hash) return;
    const targetCard = document.getElementById(hash);
    if (targetCard) {{
      const cat = targetCard.getAttribute("data-category");
      // If a category was filtered out, switch to all or that category
      if (activeCategory !== "all" && activeCategory !== cat) {{
        activeCategory = "all";
        pills.forEach(p => p.classList.remove("active"));
        const allPill = document.querySelector('.faq-pill[data-cat="all"]');
        if (allPill) allPill.classList.add("active");
        filterFaq();
      }}
      targetCard.style.display = "";
      const details = targetCard.querySelector("details");
      if (details) details.open = true;
      targetCard.classList.add("faq-target");
      targetCard.scrollIntoView({{ behavior: "smooth", block: "center" }});
      setTimeout(() => targetCard.classList.remove("faq-target"), 2500);
    }}
  }}

  window.addEventListener("hashchange", handleHashTarget);
  document.addEventListener("DOMContentLoaded", handleHashTarget);
  if (document.readyState !== "loading") {{
    handleHashTarget();
  }}
}})();
</script>
"""

def compile_faq(check_only=False, verbose=True):
    if verbose:
        print(f"Loading and validating FAQ from {FAQ_DIR}...")

    all_data = {}
    has_errors = False

    for lang in SUPPORTED_LANGS:
        categories, errors, warnings = load_faq_for_lang(lang)

        if warnings and verbose:
            for w in warnings[:5]:
                print(f"  [{lang} WARN] {w}")
            if len(warnings) > 5:
                print(f"  [{lang} WARN] ... and {len(warnings) - 5} more warnings.")

        if errors:
            has_errors = True
            print(f"\n❌ [{lang}] Found {len(errors)} validation error(s):")
            for e in errors:
                print(f"  - {e}")
            continue

        q_count = sum(len(c["questions"]) for c in categories)
        if verbose:
            print(f"  ✅ [{lang}] Loaded {len(categories)} categories, {q_count} questions")

        all_data[lang] = categories

    if has_errors:
        return False

    if check_only:
        return True

    # 1. Write compiled data/faq.json
    os.makedirs(DATA_DIR, exist_ok=True)
    with open(COMPILED_JSON, "w", encoding="utf-8") as f:
        json.dump(all_data, f, ensure_ascii=False, indent=2)
    if verbose:
        print(f"\nWrote compiled dataset: {COMPILED_JSON}")

    # 2. Write localized HTML pages in lang/<lang>/texts/faq.html
    for lang in SUPPORTED_LANGS:
        categories = all_data.get(lang, [])
        if not categories:
            continue

        html_content = build_faq_html(lang, categories)
        out_path = os.path.join(REPO_ROOT, "lang", lang, "texts", "faq.html")
        os.makedirs(os.path.dirname(out_path), exist_ok=True)

        with open(out_path, "w", encoding="utf-8") as f:
            f.write(html_content.strip() + "\n")

        if verbose:
            print(f"Wrote {out_path} ({sum(len(c['questions']) for c in categories)} questions)")

    return True

if __name__ == "__main__":
    check_mode = "--check" in sys.argv
    success = compile_faq(check_only=check_mode, verbose=True)
    sys.exit(0 if success else 1)
