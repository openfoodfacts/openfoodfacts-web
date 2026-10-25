---
applyTo: "lang/**/texts/*.html"
---

# Static HTML Text Fragments Guidelines

When editing or adding HTML page fragments under `lang/<lang>/texts/`:

## 1. Fragment Structure (Not Full Documents)
- These files are text fragments inserted into the `product-opener` shell.
- **Never include** `<!DOCTYPE html>`, `<html>`, `<head>`, or `<body>` tags.
- Use clean semantic HTML (`<h1>`, `<h2>`, `<p>`, `<ul>`, `<section>`, `<div>`).

## 2. Asset Integrity
- **No external hotlinking:** Never link to external third-party images or scripts. Place images in `html/images/texts/` and commit them to git, or use `https://static.openfoodfacts.org/...`.
- Relative links to other OFF pages should omit locale prefixes where appropriate or follow project URL standards (e.g., `<a href="/data">` or `<a href="/reuses">`).

## 3. Server Includes
- The platform uses `[[texts/path/to/include.html]]` for reusable components.
- Retain existing includes and keep paths relative to `texts/`.

## 4. Internationalization & Protected Terms
- English in `lang/en/texts/` is the canonical reference.
- **Never translate brand and system names:**
  - `Open Food Facts`, `Open Beauty Facts`, `Open Pet Food Facts`, `Open Prices`
  - `Nutri-Score`, `Eco-Score`, `Green-Score`, `NOVA`
- In translated files (`lang/fr/`, `lang/es/`, etc.), keep all placeholders (`%s`, `{count}`, etc.) intact.
