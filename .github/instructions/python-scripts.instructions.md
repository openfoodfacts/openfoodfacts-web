---
applyTo: "scripts/**/*.py"
---

# Python Automation & Compilation Guidelines

When creating or modifying Python scripts in `scripts/`:

## 1. Principles
- **Idempotency:** Scripts should produce reproducible JSON/HTML outputs without side-effects or order-dependent diffs.
- **Dry-run Support:** All compilation scripts must implement a `--check` flag to validate data without writing files (used heavily in CI workflows).
- **Graceful Error Handling:** Print actionable errors with exact filenames and validation failures, exiting with code 0 on success and 1 on error.
- **Backward Compatibility:** Ensure generated JSON datasets (e.g. `data/reuses.json`) retain expected field types and structures consumed downstream.

## 2. Dependencies & Compatibility
- Target Python 3.10+.
- Stick to standard library modules where possible, with approved packages: `PyYAML` (`yaml`), `beautifulsoup4` (`bs4`).

## 3. Testing
Ensure unit tests cover new helpers or validation logic:
```bash
python3 scripts/compile.py --check
PYTHONPATH=scripts python3 -m unittest discover -s scripts -p "test_*.py"
```
