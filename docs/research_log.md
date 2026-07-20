# Research Log

This log begins with the reorganization of the project. Earlier work was completed outside this repository and is summarized here instead of being assigned invented dates.

## 2026-07-19

### Work summarized and organized

- Narrowed the project from a broad comparison of green- and blue-hydrogen methanol costs to the effect of feed impurities on methanol synthesis.
- Organized 14 extracted papers into one condition-level dataset.
- Combined 301 experimental rows while keeping multiple conditions from the same paper under one Study ID.
- Identified 48 rows that still need manual extraction or graph checking.
- Separated possible duplicate experiments from genuinely repeated conditions within one paper.
- Compiled 28 additional candidate sources and ranked 15 for follow-up.
- Simplified the repository so that the data and research documents are easier to review.

### Current limitations

- Some paired baseline IDs still need verification.
- Several graph-only values have not been digitized.
- Related publications may reuse the same experiments.
- Sulfur and nitrogen evidence dominates the current dataset.
- The final statistical approach has not been selected.

### Next actions

- Check the rows listed in `data/needs_manual_extraction.tsv` against the original papers.
- Resolve the relationships listed in `data/duplicate_check.tsv`.
- Review the highest-priority candidate sources.
- Decide which methanol outcome types have enough compatible observations for analysis.

Future entries should record the date, work completed, decisions made, unresolved questions, and next action.
