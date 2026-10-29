---
applyTo: "knowledge_panels/**"
---

# Knowledge Panels Guidelines

When adding or updating knowledge cards in `knowledge_panels/`:

## 1. Directory Structure
- Panels belong to taxonomy categories: `additives`, `categories`, `ingredients`, `labels`, `nutrients`, `nova-groups`.
- Edit the corresponding `world-en.yml` file within the category subdirectory (e.g., `knowledge_panels/additives/off/world-en.yml`).

## 2. Card Content & Format
- Keys must match taxonomy IDs with English language prefix (e.g., `"en:citric-acid"`).
- Standard section layout:
  - `***What it is:***` Concise description.
  - `***Why it's used:***` Purpose / common functions.
  - `***Concerns:***` Objective, fact-based concerns citing regulatory bodies (WHO, EFSA, FDA).
  - `***Sources:***` Hyperlinked references to authoritative bodies.
- Maintain a neutral, non-alarmist tone.

## 3. Building Panels
Test HTML generation after updating cards:
```bash
cd knowledge_panels
python3 build_html.py additives ingredients nutrients categories labels
```
