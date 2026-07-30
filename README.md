# Methanol Impurity Research

This repository contains my ongoing AP Research project on how impurities in hydrogen, carbon dioxide, and synthesis-gas feeds affect methanol synthesis.

## Research question

> To what extent can literature-derived impurity concentration, catalyst family, and operating conditions predict methanol performance loss during CO2 hydrogenation and methanol synthesis?

The current computational stage focuses on H2S and uses an explicit evidence gate before fitting any cross-study model.

## Current data

- `data/main_data.tsv` contains 301 extracted experimental conditions from 14 studies.
- `data/source_list.tsv` describes the 14 studies already extracted.
- `data/needs_manual_extraction.tsv` tracks values that still need checking or graph digitization.
- `data/duplicate_check.tsv` records experiments that may overlap across publications.
- `data/gap_analysis.tsv` summarizes missing evidence in the current dataset.
- `data/candidate_sources.tsv` and `data/retrieval_priority.tsv` track follow-up sources.

One row in `main_data.tsv` represents one experimental condition. Repeated rows from one curve or companion publication are not automatically independent experiments.

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

## Run

```powershell
python -m pip install -r requirements.txt
python -m src.h2s_dataset_builder
python -m src.h2s_evidence_engine
python -m pytest -q
```

Generated H2S datasets and results are intentionally ignored by Git because they can be reproduced from the committed inputs.

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
- Several sources report proxies, reverse reactions, or incompatible exposure protocols.
- Most studies do not provide replicate uncertainty or matched clean-aging controls.
- Literature-derived outputs are not replacements for laboratory experiments or industrial safety limits.

The research-paper PDFs are not included in this repository.
