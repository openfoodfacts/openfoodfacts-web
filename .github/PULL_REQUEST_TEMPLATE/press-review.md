## 📰 Press Review Contribution

Thank you for contributing to the Open Food Facts Press Review!

### Summary of Changes
- **Source**: <!-- e.g. Le Monde, France Inter, BBC -->
- **Publication Date**: `YYYY-MM-DD`
- **Media Type**: [ ] Article [ ] Podcast [ ] Video [ ] Study
- **Target File**: `data/press-review/<id>.yaml`
- **Type of Change**:
  - [ ] Adding new press mention
  - [ ] Updating existing press mention
  - [ ] Correcting dead link or adding archive fallback
  - [ ] Adding topics, verbatim quotes, or editorial notes

### Related Issue
Closes #<!-- insert issue number if applicable -->

### Quality Checklist
- [ ] The media piece explicitly mentions or relies on Open Food Facts data / project.
- [ ] Spelled out "Open Food Facts" instead of the "OFF" acronym across all fields.
- [ ] Checked against validation schema using `python3 scripts/compile_press_review.py --check`.
- [ ] Date is in `YYYY-MM-DD` format and matches filename prefix.
- [ ] Link is active and accessible (or marked `dead_link: true` with archive fallback if applicable).
- [ ] Internal editorial remarks are placed in `editorial_note` (not leaked in `verbatim`).
- [ ] Recompiled dataset and pages using `python3 scripts/compile_press_review.py` (if applicable).
