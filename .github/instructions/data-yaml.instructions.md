---
applyTo: "data/**/*.yaml"
---

# Dataset YAML Guidelines

When adding or modifying YAML entities under `data/` (such as `data/reuses/`, `data/press-review/`, `data/queries/`, `data/scan_parties/`, or `data/missions/`), follow these rules:

## 1. File Naming and ID Consistency
- The entity file name must match the `id` field: `<id>.yaml`.
- Use lowercase alphanumeric characters, dashes, and underscores only for IDs (e.g. `my-awesome-app.yaml`).

## 2. Reuses Schema Requirements (`data/reuses/`)
- **Required fields:** `id`, `name`, `theme`.
- **Valid themes:** `nutrition`, `environment`, `tools`, `research`, `traceability`, `education`, `health`, `social`, `retail`, `general`, `ai`, `dietary`, `pregnancy`, `gluten`, `lactose`, `fodmap`, `allergies`, `vegan`, `halal_kosher`, `diabetes_keto`, `additives`.
- **Valid projects:** `openfoodfacts`, `openbeautyfacts`, `openpetfoodfacts`, `openproductsfacts`.
- If an install count is known, supply `installs_numeric` as an integer.

## 3. Press Review Schema Requirements (`data/press-review/`)
- Filename format: `YYYY-MM-DD-<slug>.yaml`.
- **Required fields:** `id` (same as the file name), `date` (`YYYY-MM-DD`), `source`, `title`, `type`.
- Valid types: `article`, `podcast`, `study`, `video`.

## 4. Validation
Before committing any changes to `data/`, run:
```bash
python3 scripts/compile.py --check
```
Ensure all schema and consistency checks pass.
