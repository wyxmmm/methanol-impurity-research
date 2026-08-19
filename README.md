# Methanol Impurity Research

This repository contains my ongoing Research project on how impurities in hydrogen, carbon dioxide, and synthesis-gas feeds affect methanol synthesis.

## Research question

> To what extent can literature-derived impurity concentration, catalyst family, and operating conditions predict methanol performance loss during CO2 hydrogenation and methanol synthesis?

The H2S evidence stage is preserved as a completed no-fit checkpoint. The
active Catalyst 1 stage now focuses on externally validating a clean-reactor
kinetic model for unsupported In2O3 before adding another catalyst or impurity.

## Current data

- `data/main_data.tsv` contains 301 extracted experimental conditions from 14 studies.
- `data/source_list.tsv` describes the 14 studies already extracted.
- `data/needs_manual_extraction.tsv` tracks values that still need checking or graph digitization.
- `data/duplicate_check.tsv` records experiments that may overlap across publications.
- `data/gap_analysis.tsv` summarizes missing evidence in the current dataset.
- `data/candidate_sources.tsv` and `data/retrieval_priority.tsv` track follow-up sources.

One row in `main_data.tsv` represents one experimental condition. Repeated rows from one curve or companion publication are not automatically independent experiments.

Important: `data/pilot/sulfur_stage2_verified.csv` is preserved as a legacy Stage-2 input. Its T1-001 H2S rows are known reconciliation errors; `src/h2s_dataset_builder.py` quarantines them and replaces only the supported 4 h record. Do not use that CSV directly as validated H2S evidence.

## H2S evidence engine

The H2S stage is implemented in:

- `src/h2s_dataset_builder.py` - reconciles evidence into core, supporting, kinetic, excluded, and gap datasets;
- `src/h2s_evidence_engine.py` - runs bounded source-specific calculations with strict domain checks;
- `config/h2s_model_spec.json` - defines the eligibility and universal-fit gate;
- `tests/` - verifies corrections, evidence separation, equations, and the no-fit decision.

The audited literature currently provides only one strict continuous-H2S commercial-Cu/ZnO/Al2O3 methanol-synthesis observation. The universal fit gate therefore fails, and the code intentionally does not fit a general curve. It preserves source-specific calculations while preventing COx proxies or methanol-decomposition data from being presented as universal methanol-synthesis predictions.

See:

- `docs/h2s_model_spec.md`
- `docs/h2s_phase5_evidence_engine.md`
- `docs/h2s_paper_ready_explanation.md`

## Catalyst 1: unsupported In2O3

The first catalyst-specific reactor model reproduces Ghosh et al. (2021), DOI
`10.1016/j.cej.2021.129120`. It integrates three reversible reactions in an
isothermal, isobaric plug-flow reactor:

1. CO2 hydrogenation to methanol;
2. reverse water-gas shift to CO;
3. CO2 methanation to CH4.

The published parameters are used without refitting. Across all 32 reported
conditions, the reproduction has mean absolute errors of 0.712 percentage
points for CO2 conversion, 3.732 for MeOH selectivity, 3.538 for CO
selectivity, and 0.288 for CH4 selectivity.

The published-source reproduction has now been tested, without refitting, on
88 conditions from six outside unsupported-In2O3 studies. All conditions ran
successfully, but the locked model transferred unevenly: its mean absolute
errors were 2.124 percentage points for CO2 conversion, 18.479 for methanol
selectivity, and 2.067 for methanol yield. Part A therefore closes as a
diagnostic checkpoint, not as proof that the published parameters are a
general unsupported-In2O3 model. The principal transfer weakness is product
branching/selectivity rather than numerical solver failure.

Key files:

- `src/ghosh_in2o3_pfr.py` - published LHHW rates and PFR balances;
- `src/ghosh_in2o3_reproduction.py` - reproducible calibration, sensitivity,
  convergence, and validation-input outputs;
- `data/curated/unsupported_in2o3/` - 32 calibration conditions, published
  parameters, and six SI validation inputs;
- `docs/unsupported_in2o3/catalyst1_completion_protocol.md` - completion and
  external-validation rules;
- `docs/unsupported_in2o3/model_input_audit.md` - source assumptions,
  ambiguities, external-evidence provenance, and Yang flow-basis resolution;
- `docs/unsupported_in2o3/model_reproduction_and_transfer.md` - source
  reproduction, locked six-study transfer results, and failure diagnosis;
- `docs/model_equation_registry.md` - controlled record of the equations,
  units, provenance, domains, and implementation status used by the code.

## Run

```powershell
python -m pip install -r requirements.txt
python -m src.h2s_dataset_builder
python -m src.h2s_evidence_engine
python -m src.ghosh_in2o3_reproduction
python -m src.ghosh_external_validation_batch
python -m src.ghosh_part_a_diagnostics
python -m pytest -q
```

Generated H2S and unsupported-In2O3 result tables are intentionally ignored by
Git because they can be reproduced from the committed inputs.

## Repository structure

```text
config/  Machine-readable model rules
data/    Extracted data and compact source-derived H2S inputs
docs/    Research methods and interpretation
src/     Reproducible analysis code
tests/   Automated validation and integrity checks
```

## Current limitations

- The H2S core is too small for a defensible universal prediction model.
- The locked unsupported-In2O3 model runs across six external studies, but its
  product-selectivity transfer error is too large to call it a general
  validated model.
- Its parameter values do not represent supported In2O3/ZrO2.
- Several sources report proxies, reverse reactions, or incompatible exposure protocols.
- Most studies do not provide replicate uncertainty or matched clean-aging controls.
- Literature-derived outputs are not replacements for laboratory experiments or industrial safety limits.

The research-paper PDFs are not included in this repository.
