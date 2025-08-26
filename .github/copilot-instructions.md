# OpenFoodFacts Web Content Repository

**Always reference these instructions first and fallback to search or bash commands only when you encounter unexpected information that does not match the info here.**

## Overview

OpenFoodFacts Web is a static content repository that provides HTML content, knowledge panels, and multi-language assets for the main OpenFoodFacts server application. This repository contains NO server-side application code - it is purely static content that gets deployed to production servers.

## Working Effectively

### Environment Setup and Dependencies

Set up the repository for development:

```bash
# Install Python dependencies for knowledge panels (REQUIRED)
cd knowledge_panels
python3 -m pip install -r requirements.txt --user
```

This takes ~10 seconds. NEVER CANCEL - wait for completion.

```bash
# Install additional validation tools (OPTIONAL)
pip3 install beautifulsoup4 pyspelling
sudo apt-get install -y aspell aspell-en
```

This takes ~30 seconds. NEVER CANCEL - wait for completion.

### Core Build Process

**Build knowledge panels HTML from YAML content:**

```bash
cd knowledge_panels
python3 build_html.py additives ingredients nutrients categories labels
```

**TIMING**: Takes ~5 seconds. NEVER CANCEL - wait for completion.
**OUTPUT**: Generates thousands of HTML files in `lang/` directories for all supported languages.
**VALIDATION**: Successfully generates files for 100+ languages, some warnings about unknown languages are expected.

This is the ONLY build command in the repository. There are no other compilation or build steps.

### Additional Validation Commands

**Validate forbidden strings in index.html files:**

```bash
# Check for unwanted project names in OFF index files
FORBIDDEN_STRINGS=("Open Pet Food Facts" "Open Beauty Facts" "Open Products Facts")
FILES=$(find ./lang/ -name 'index.html' -path '*/texts/*')

for file in $FILES; do
  for string in "${FORBIDDEN_STRINGS[@]}"; do
    if grep -q "$string" "$file"; then
      echo "Error: '$string' found in $file"
      exit 1
    fi
  done
done
echo "No forbidden strings found."
```

**TIMING**: Takes ~2 seconds. NEVER CANCEL - wait for completion.
**OUTPUT**: Should report "No forbidden strings found" for OFF content, but may find expected instances in OPF/OBF/OPFF project directories (which is valid).

### Validation and Quality Checks

```bash
python3 .github/scripts/check_includes.py
```

**TIMING**: Takes ~15-20 seconds. NEVER CANCEL - wait for completion.
**OUTPUT**: Warnings about missing translated files are expected. Only exit code 1 with actual missing includes is a real error.
**DEPENDENCIES**: Requires `pip3 install beautifulsoup4`

**Spellcheck HTML content (will fail on technical terms - expected):**

```bash
pyspelling -c spellcheck.yaml
```

**TIMING**: Takes ~1 second.
**OUTPUT**: Will report many "misspelled" technical terms, product names, and URLs. This is expected behavior.
**DEPENDENCIES**: Requires `pip3 install pyspelling` and `sudo apt-get install -y aspell aspell-en`

### Repository Structure and Navigation

**Key directories:**
- `lang/en/texts/` - English HTML content (main source)
- `lang/{language}/texts/` - Translated content for 100+ languages
- `knowledge_panels/` - YAML source files and Python build scripts
- `knowledge_panels/{additives,ingredients,nutrients,categories,labels}/` - Knowledge panel YAML sources
- `lang/{project}/{language}/knowledge_panels/` - Generated HTML knowledge panels
- `.github/workflows/` - CI/CD automation

**Important files:**
- `knowledge_panels/requirements.txt` - Python dependencies
- `knowledge_panels/build_html.py` - Main build script for knowledge panels
- `spellcheck.yaml` - Spell checking configuration
- `.github/scripts/check_includes.py` - Translation validation

### Development Workflows

**Adding/editing static HTML content:**
1. Edit files in `lang/en/texts/`
2. Run validation scripts to check for issues
3. Content gets translated via Crowdin (external process)

**Adding/editing knowledge panels:**
1. Edit YAML files in `knowledge_panels/{category}/off/world-en.yml`
2. Run `python3 build_html.py {categories}` to generate HTML
3. Generated files will be created in `lang/` directories

**Before committing any change:**
```bash
# Validate includes are preserved
python3 .github/scripts/check_includes.py

# Generate fresh knowledge panels if YAML was modified
cd knowledge_panels
python3 build_html.py additives ingredients nutrients categories labels
```

## Critical Validation Scenarios

Since this is static content, validation focuses on content quality rather than functional testing:

**ALWAYS test after knowledge panel changes:**
1. Run the build command to generate HTML files
2. Check that files are generated in expected `lang/` directories
3. Verify no errors in build output (warnings about unknown languages are OK)

**ALWAYS test after HTML content changes:**
1. Run the includes checker to ensure translation consistency
2. Verify HTML syntax is valid (no broken tags or structures)

## CI/CD Process

**GitHub Actions handle:**
- Automatic knowledge panel HTML generation when YAML files change
- Deployment to staging servers via SSH
- Translation management via Crowdin integration

**Manual deployment to production is still required.**

## Common Issues and Troubleshooting

**"No module named 'xyz'" errors:**
- Install Python dependencies: `pip3 install -r knowledge_panels/requirements.txt --user`

**Build script fails:**
- Ensure you're in the `knowledge_panels/` directory when running `build_html.py`
- Python 3.12+ is required

**Generated files not appearing:**
- Check that YAML source files exist in correct category subdirectories
- Verify YAML syntax is valid
- Run build command from `knowledge_panels/` directory

**Many "misspelled words" in spell check:**
- This is expected behavior - technical terms, product names, and URLs trigger false positives
- Focus on actual content errors, not terminology flags

## Technologies and Dependencies

- **Python 3.12+** - For knowledge panel generation
- **YAML** - Knowledge panel content format  
- **HTML/CSS** - Static content format
- **BeautifulSoup4** - HTML parsing for validation
- **Crowdin** - Translation management (external service)
- **GitHub Actions** - CI/CD automation

## DO NOT attempt to:

- Start a web server (this is static content only)
- Run unit tests (there are none)
- Build a traditional application (no compilation needed)
- Fix spell check "errors" for technical terms (expected false positives)

## Expected File Changes

When working in this repository, expect to see:
- Changes to HTML files in `lang/en/texts/` (content edits)
- Changes to YAML files in `knowledge_panels/` (knowledge panel content)
- Thousands of generated HTML files in `lang/` directories after running build scripts

The generated HTML files ARE intended to be committed to the repository.