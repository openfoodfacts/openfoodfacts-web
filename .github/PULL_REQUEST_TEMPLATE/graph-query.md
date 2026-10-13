## 📊 Useful Query / Graph Contribution

Thank you for contributing to the Open Food Facts Useful Queries & Graphs directory!

### Summary of Changes
- **Query Title**: <!-- e.g. Sugars vs Additives in Yogurts -->
- **Food Topic**: <!-- e.g. beverages, dairy, breakfast, sweets, meat, meals, nutrition, quality -->
- **Query Type**: <!-- e.g. scatter_plot, bar_chart, map, list, facet -->
- **URL**: <!-- https://world.openfoodfacts.org/cgi/search.pl?... -->
- **Target File**: `data/queries/<id>.yaml`
- **Type of Change**:
  - [ ] Adding new curated query or graph
  - [ ] Updating existing query parameters or description
  - [ ] Fixing broken URL or updating search criteria

### Related Issue
Closes #<!-- insert issue number if applicable -->

### Quality Checklist
- [ ] Checked against validation schema using `python3 scripts/compile_queries.py --check`.
- [ ] Query file is formatted properly in `data/queries/<id>.yaml`.
- [ ] URL is active and generates meaningful results on Open Food Facts.
- [ ] Recompiled dataset using `python3 scripts/compile_queries.py` (if applicable).
