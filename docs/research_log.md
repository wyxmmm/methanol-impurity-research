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

## 2026-08-12

### Part A external-transfer diagnostic completed

- Applied the unchanged Ghosh unsupported-In2O3 model to 88 clean-feed
  conditions from six external studies; no kinetic, adsorption, or
  thermodynamic parameter was fitted to those studies.
- Audited catalyst phase, preparation family, response provenance, inert-feed
  handling, flow normalization, and whether each condition lay inside the
  original model's numerical operating range.
- Resolved the Yang space-velocity question from the supplied main article:
  Figure 2 reports mass-normalized `mL g^-1 h^-1`. Its 26 rows were therefore
  released from the unit hold but remain lower-certainty because their
  responses were digitized from graphs.
- Obtained successful numerical solutions for all 88 conditions. The locked
  external-test MAEs were 2.124 percentage points for CO2 conversion, 18.479
  for methanol selectivity, and 2.067 for methanol yield.
- Determined that software execution was not the limiting issue. The main
  transfer weakness was methanol/RWGS product branching, with additional
  between-study effects associated with phase and catalyst preparation.
- Closed Part A as a diagnostic checkpoint. The result does not establish a
  universal unsupported-In2O3 model, an In2O3/ZrO2 model, or an H2S model.
- Added a controlled equation registry so the paper can trace every published,
  project-derived, source-specific, and candidate mathematical expression.
