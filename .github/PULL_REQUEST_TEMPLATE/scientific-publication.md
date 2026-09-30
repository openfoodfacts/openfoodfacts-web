## 🔬 Scientific Publication Contribution

Thank you for contributing to the Open Food Facts scientific publications directory!

### Summary of Changes
- **Title**: <!-- Full paper title -->
- **Authors**: <!-- e.g. Chantal Julia, Serge Hercberg -->
- **Year**: `YYYY`
- **Journal / Venue**: <!-- e.g. Foods, Nature Food, PLOS ONE -->
- **DOI / URL**: <!-- https://doi.org/... or https://... -->
- **Target File**: `data/scientific_publications/<id>.yaml`
- **Type of Change**:
  - [ ] Adding new scientific publication
  - [ ] Updating existing scientific publication
  - [ ] Adding DOI, open-access PDF link, or citation count
  - [ ] Adding research themes, excerpt, or Open Food Facts usage notes

### Related Issue
Closes #<!-- insert issue number if applicable -->

### Quality Checklist
- [ ] The publication uses or cites Open Food Facts data, API, or project.
- [ ] Checked against validation schema using `python3 scripts/build_scientific_publications.py --check`.
- [ ] Publication file is formatted properly in `data/scientific_publications/<id>.yaml`.
- [ ] First author surname and publication year match the filename id (`YYYY-author-slug.yaml`).
- [ ] URL is active and accessible (preferably DOI URL or open-access repository).
- [ ] Recompiled dataset using `python3 scripts/build_scientific_publications.py` (if applicable).
