# Translation Repetition Checker

## Purpose

This script detects accidental text repetitions in translation files that sometimes occur during the Crowdin translation process. These repetitions can happen when translators or the Crowdin system accidentally duplicate text.

## Examples of Issues Detected

### Spanish Translation
**Before (incorrect):**
```html
<p>¿Preguntas o comentarios? ¿Preguntas o comentarios? ¿Preguntas o comentarios? Questions or comments?</p>
```

**After (correct):**
```html
<p>¿Preguntas o comentarios? Reach out on Slack...</p>
```

### French Translation
**Before (incorrect):**
```html
<p>Open Food Facts est un canal de distribution de données essentiel. Open Food Facts est un canal de distribution de données essentiel. Partagez une fois...</p>
```

**After (correct):**
```html
<p>Open Food Facts est un canal de distribution de données essentiel. Environ 200 applications et services utilisent Open Food Facts. Partagez une fois...</p>
```

## Usage

### Check All Translation Files
```bash
perl scripts/check_translation_repetitions.pl
```

### Check Specific Files
```bash
perl scripts/check_translation_repetitions.pl lang/es/texts/press.html lang/fr/texts/index-pro.html
```

### Check Files in a Language
```bash
perl scripts/check_translation_repetitions.pl lang/es/texts/*.html
```

## How It Works

The script:
1. Reads HTML files from the `lang/` directory
2. Removes HTML comments to avoid false positives
3. Searches for text patterns that appear 2+ times consecutively
4. Filters out legitimate repetitions (HTML tags, CSS classes, etc.)
5. Reports any suspicious repetitions found

## Exit Codes

- `0`: No repetitions found (success)
- `1`: Repetitions detected (failure)

## Integration

This script is automatically run by the GitHub Actions workflow `.github/workflows/check_translation_repetitions.yml` on:
- Every push that modifies HTML files in `lang/` directories
- Every pull request that modifies HTML files in `lang/` directories

The workflow will:
- Only check changed files in pull requests (for efficiency)
- Post a comment on the PR if repetitions are found
- Block merging until the repetitions are fixed

## False Positives

The script attempts to filter out legitimate repetitions like:
- HTML structural elements (`</div>`, `<p>`, etc.)
- CSS classes and IDs
- Technical strings containing only letters, numbers, dashes, and underscores

If you encounter a false positive, please report it so the script can be improved.

## Maintenance

To update the script's detection logic, edit `scripts/check_translation_repetitions.pl`. The main detection happens in the `check_repetitions` subroutine.
