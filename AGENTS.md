# Coding Agent Guidelines (`openfoodfacts-web`)

This file guides automated coding agents (including GitHub Copilot Coding Agent, Gemini, Claude, and local pair-programming assistants) working in `openfoodfacts-web`.

Please refer to the comprehensive instructions in:
- [`.github/copilot-instructions.md`](.github/copilot-instructions.md)

---

## Quick Reference

### 1. Key Rules
- **No external hotlinking:** Never hotlink external scripts/images. Save assets to `html/images/texts/` or use `https://static.openfoodfacts.org`.
- **Protected brand names (never translate):**
  - `Open Food Facts`
  - `Open Beauty Facts`
  - `Open Pet Food Facts`
  - `Open Prices`
  - `Nutri-Score`
  - `Eco-Score`
  - `Green-Score`
  - `NOVA`
- **HTML fragments:** Files in `lang/<lang>/texts/` are page fragments embedded by `product-opener`. Do NOT wrap them in `<html>` or `<body>` tags. Preserve `[[texts/...]]` template includes.
- **Translation QA:** See [`lang/AGENTS.md`](lang/AGENTS.md) for full localization and internationalization QA directives.

### 2. Validation & Testing
Always test your changes before concluding work:
```bash
# Validate all dataset YAML schemas and consistency
python3 scripts/compile.py --check

# Compile datasets and update HTML output
python3 scripts/compile.py

# Run unit tests
PYTHONPATH=scripts python3 scripts/test_translation_qa.py
PYTHONPATH=scripts python3 scripts/test_add_reuse.py
PYTHONPATH=scripts python3 scripts/test_add_press_review.py
PYTHONPATH=scripts python3 scripts/test_add_query.py
PYTHONPATH=scripts python3 scripts/test_add_scan_party.py
PYTHONPATH=scripts python3 scripts/test_add_scientific_publication.py
```

### 3. Conventional Commits
Use semantic commits: `feat:`, `fix:`, `docs:`, `chore:`, `test:`.
