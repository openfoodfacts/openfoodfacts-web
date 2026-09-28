# Open Food Facts FAQ System

The Open Food Facts FAQ provides multilingual, categorized, searchable, and interactive answers to common questions about Open Food Facts, food scores (Nutri-Score, Eco-Score, NOVA), the mobile application, and the producers platform.

---

## 🏗️ Architecture & Directory Structure

```
openfoodfacts-web/
├── data/
│   ├── faq/
│   │   ├── en/                   # English FAQ categories (*.md)
│   │   ├── fr/                   # French FAQ categories (*.md)
│   │   ├── es/                   # Spanish FAQ categories (*.md)
│   │   ├── de/                   # German FAQ categories (*.md)
│   │   └── it/                   # Italian FAQ categories (*.md)
│   └── faq.json                  # Compiled unified JSON dataset
├── lang/
│   └── <lang>/texts/faq.html     # Compiled single-page interactive HTML
├── scripts/
│   ├── compile_faq.py            # Validation and HTML/JSON compiler
│   └── add_faq_question.py       # Helper to parse issues & add questions
└── .github/
    ├── ISSUE_TEMPLATE/
    │   ├── new-faq-question.yml  # GitHub Issue Form template
    │   └── new-faq-question.md   # GitHub Markdown template
    ├── PULL_REQUEST_TEMPLATE/
    │   └── faq.md                # FAQ PR checklist template
    └── workflows/
        ├── faq-issue-to-pr.yml   # Automated Issue -> PR workflow
        └── faq-ci.yml            # CI validation workflow
```

---

## 💡 Proposing a Question via GitHub Issues

Anyone can propose new questions using GitHub Issues:

1. Click **"New Issue"** and select **"💡 Suggest a new FAQ question"** (or use the direct URL:  
   `https://github.com/openfoodfacts/openfoodfacts-web/issues/new?template=new-faq-question.yml`).
2. Fill out:
   - **Language**: `en`, `fr`, `es`, `de`, or `it`.
   - **Category**: Select the topic (e.g. Nutri-Score, Mobile App, Eco-Score).
   - **Question Title**: The question as users would search for it.
   - **Proposed Answer (Markdown)**: The complete answer in Markdown.
   - **Sources**: Documentation or scientific links.
3. Once submitted with the `faq` label, GitHub Actions automatically:
   - Runs `scripts/add_faq_question.py`.
   - Formats the question into the correct `data/faq/<lang>/<category>.md` file.
   - Verifies validation with `scripts/compile_faq.py --check`.
   - Opens a **Pull Request** for team review and comments back on your issue!

---

## ✍️ Submitting a Pull Request directly

Contributors can also contribute directly using Git:

1. Edit an existing category file or create a new one under `data/faq/<lang>/<filename>.md`.
2. Format the file with YAML frontmatter and questions:

```markdown
---
id: nutri-score
title: Nutri-Score
icon: 🥗
icon_name: heartbeat
order: 8
lang: en
---

## What should I do if the Nutri-Score of my product is incorrect?

Check your ingredients and nutrition table on the product sheet. If incorrect, update the values or contact producers@openfoodfacts.org.

---

## Where does the Nutri-Score come from?

The Nutri-Score is managed by Santé Publique France...

---
```

3. Run the validator:
   ```bash
   python3 scripts/compile_faq.py --check
   ```
4. Compile the output pages:
   ```bash
   python3 scripts/compile_faq.py
   ```
5. Submit your PR using the FAQ PR template (`.github/PULL_REQUEST_TEMPLATE/faq.md`).

---

## 👍 Thumbs Up / Thumbs Down & Matomo Tracking

Each question card includes an interactive helpfulness widget inside the answer drawer:
- **"Did this answer your question?"** (localized into English, French, Spanish, German, and Italian).
- **👍 Thumbs Up**: User found the answer helpful.
- **👎 Thumbs Down**: User still needs help.
- **Direct Edit Link**: Points directly to GitHub to edit the source markdown file (`/edit/main/data/faq/{lang}/{file}`).

### Matomo Logging Specification

When a user clicks 👍 or 👎, an event is logged to Matomo via `window._paq`:

```javascript
window._paq = window._paq || [];

// 1. Global event with question ID and language:
// Category: 'FAQ Feedback'
// Action:   'thumbs_up' | 'thumbs_down'
// Name:     '<question_id> [<lang>]' (e.g. 'nutri-score-incorrect [en]')
window._paq.push(['trackEvent', 'FAQ Feedback', action, questionId + ' [' + lang + ']']);

// 2. Language-segmented category for immediate per-language dashboard filtering:
// Category: 'FAQ Feedback (<lang>)' (e.g. 'FAQ Feedback (fr)')
// Action:   'thumbs_up' | 'thumbs_down'
// Name:     '<question_id>'
window._paq.push(['trackEvent', 'FAQ Feedback (' + lang + ')', action, questionId]);
```

### Local Persistence
Votes are stored in `localStorage` under `off_faq_feedback_<lang>_<question_id>` so returning users see their selection preserved and double-voting is prevented.

---

## 🛠️ CLI Tools & Helpers

### 1. Validate FAQ files
```bash
python3 scripts/compile_faq.py --check
```

### 2. Recompile dataset and HTML pages
```bash
python3 scripts/compile_faq.py
```

### 3. Add a question via CLI
```bash
python3 scripts/add_faq_question.py \
  --lang en \
  --category nutri-score \
  --question "How does Nutri-Score score beverages?" \
  --answer "Beverages have a specific algorithm focusing on energy, sugars, and sweeteners." \
  --compile
```

### 4. Parse from GitHub issue text
```bash
python3 scripts/add_faq_question.py --from-issue-file issue.md --compile
```
