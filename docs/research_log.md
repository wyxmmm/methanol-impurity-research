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

## 2026-07-30

### H2S evidence gate completed

- Reconciled the strict H2S evidence into core, supporting, kinetic, excluded,
  and evidence-gap records.
- Implemented bounded source-specific calculations and automatic refusal of
  unsupported cross-study predictions.
- Determined that the universal H2S fit gate failed because the literature did
  not provide enough independent compatible studies, concentrations,
  experimental units, or matched baselines.
- Preserved the completed H2S work as a defensible no-fit result rather than
  forcing a universal curve.

## 2026-08-03

### Unsupported-In2O3 model reproduction

- Verified the Ghosh main article and genuine Supporting Information.
- Curated 32 calibration conditions, ten published single-site parameters,
  and six SI validation inputs.
- Implemented the three reversible LHHW rates and plug-flow molar balances
  without refitting the parameters.
- Reproduced the calibration data with MAEs of 0.712 percentage points for CO2
  conversion, 3.732 for MeOH selectivity, 3.538 for CO selectivity, and 0.288
  for CH4 selectivity.
- Tested pressure convention, catalyst-mass basis, adsorption-enthalpy
  assignment, and numerical integration convergence.
- Did not calculate an invented held-out score: the SI lists validation inputs
  but not measured outputs, and anonymous parity points cannot be mapped to
  individual runs.

## 2026-08-04

### Catalyst 1 direction locked

- Selected unsupported In2O3 as Catalyst 1 because it currently has the most
  complete compatible kinetic dataset and a reproducible published model.
- Defined whole-study external validation as the next scientific gate.
- Kept the project on the kinetic-model-first path unless an explicit later
  decision changes it.
- Defined a 15-phase completion protocol covering evidence eligibility,
  validation, failure diagnosis, refitting, uncertainty, domain protection,
  versioning, and the gate before another catalyst or impurity.

### Next action

- Perform targeted research and condition-level extraction for independent
  unsupported or bulk In2O3 studies, beginning with Martin and Frei.
- Apply the unchanged Ghosh parameters to a compatible held-out study before
  considering refitting.
