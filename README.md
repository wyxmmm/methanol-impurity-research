# Methanol Impurity Research

I started this project to understand how impurities in hydrogen, carbon
dioxide, and synthesis-gas feeds affect methanol production. My long-term goal
is to build a model that predicts a clearly defined impurity effect for a
specific catalyst and range of operating conditions.

## What I am trying to answer

> To what extent can literature-derived impurity concentration, catalyst family, and operating conditions predict methanol performance loss during CO2 hydrogenation and methanol synthesis?

In simpler terms, I am asking how contaminants in the gases used to make
methanol reduce catalyst performance, and whether published experiments are
consistent enough to predict that loss. Possible model inputs include the
impurity and its concentration, catalyst composition, temperature, pressure,
feed ratio, space velocity, exposure time, and how the impurity was
introduced. Possible outputs include methanol yield, selectivity,
productivity, formation rate, and catalyst deactivation. These outputs measure
different things and cannot automatically be combined.

The project focuses on experiments that actually measure methanol synthesis.
Mechanism studies and realistic gas-stream measurements can provide context,
but they are kept separate when they do not report a comparable methanol
outcome.

The H2S evidence stage is preserved as a completed no-fit checkpoint. I then
reproduced a published clean-reactor model for unsupported In2O3 and tested it
against outside studies. That model remains source-specific. Both stages are
supporting steps toward the main goal: a catalyst-matched impurity model that
predicts a clearly defined change in methanol performance.

## What I have collected

- `data/main_data.tsv` contains 301 extracted experimental conditions from 14 studies.
- `data/source_list.tsv` describes the 14 studies already extracted.
- `data/needs_manual_extraction.tsv` tracks values that still need checking or graph digitization.
- `data/duplicate_check.tsv` records experiments that may overlap across publications.
- `data/gap_analysis.tsv` summarizes missing evidence in the current dataset.
- `data/candidate_sources.tsv` and `data/retrieval_priority.tsv` track follow-up sources.

One row in `main_data.tsv` represents one experimental condition. Repeated rows from one curve or companion publication are not automatically independent experiments.

Important: `data/pilot/sulfur_stage2_verified.csv` is preserved as a legacy Stage-2 input. Its T1-001 H2S rows are known reconciliation errors; `src/h2s_dataset_builder.py` quarantines them and replaces only the supported 4 h record. Do not use that CSV directly as validated H2S evidence.

## What happened with the first H2S model

The H2S stage is implemented in:

- `src/h2s_dataset_builder.py` - reconciles evidence into core, supporting, kinetic, excluded, and gap datasets;
- `src/h2s_evidence_engine.py` - runs bounded source-specific calculations with strict domain checks;
- `config/h2s_model_spec.json` - defines the eligibility and universal-fit gate;
- `tests/` - verifies corrections, evidence separation, equations, and the no-fit decision.

The strict dataset currently has only one compatible continuous-H2S
commercial-Cu/ZnO/Al2O3 methanol-synthesis observation. That is not enough to
fit and test a general curve. The code therefore refuses to make a universal
prediction and keeps the useful source-specific calculations separate. This
was a no-fit result, but it helped define what evidence a later impurity model
actually needs.

The complete H2S evidence rules, result, implemented source-specific tools,
and limitations are consolidated in `docs/h2s_model_spec.md`.

## Why I studied clean unsupported In2O3

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

In this context, one "condition" is one reported combination of catalyst,
temperature, pressure, feed ratio, flow or space velocity, and measured
outcome. The 88 conditions are repeated settings collected from six papers;
they are not 88 independent studies.

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

## How to reproduce the calculations

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

## How I used AI and coding tools

I used OpenAI Codex extensively as a research and coding assistant. It helped
me organize literature, support data extraction from papers I supplied, draft
and revise Python code, run tests, find inconsistencies, and prepare early
documentation. Codex generated or revised substantial parts of the initial
code and writing under my direction.

I do not treat AI output as a scientific source. Numerical claims in this
repository should trace back to a cited paper, a committed data table, or a
reproducible calculation. I am reviewing the concepts and rewriting the main
explanations so I can understand and defend the final work. I also discuss the
scientific direction with my mentor. Any eventual paper will follow the AI
disclosure rules of the journal or competition where it is submitted.

## What this project cannot claim yet

- The H2S core is too small for a defensible universal prediction model.
- The locked unsupported-In2O3 model runs across six external studies, but its
  product-selectivity transfer error is too large to call it a general
  validated model.
- Its parameter values do not represent supported In2O3/ZrO2.
- Several sources report proxies, reverse reactions, or incompatible exposure protocols.
- Most studies do not provide replicate uncertainty or matched clean-aging controls.
- Literature-derived outputs are not replacements for laboratory experiments or industrial safety limits.

The research-paper PDFs are not included in this repository.
