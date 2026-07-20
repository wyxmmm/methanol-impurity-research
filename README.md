# Methanol Impurity Research

This repository contains my ongoing AP Research project on how impurities in hydrogen, carbon dioxide, and synthesis-gas feeds affect methanol synthesis.

## Research question

> To what extent can literature-derived impurity concentration, catalyst family, and operating conditions predict methanol performance loss during CO2 hydrogenation and methanol synthesis?

The question is still being refined. The current stage of the project is literature review, data verification, and preparation for later analysis in Python.

## Current data

- `data/main_data.tsv` contains 301 extracted experimental conditions from 14 studies.
- `data/source_list.tsv` describes the 14 studies already extracted.
- `data/needs_manual_extraction.tsv` tracks 48 values that still need checking or graph digitization.
- `data/duplicate_check.tsv` records experiments that may overlap across publications.
- `data/gap_analysis.tsv` summarizes missing evidence in the current dataset.
- `data/candidate_sources.tsv` contains 28 possible sources for filling those gaps.
- `data/retrieval_priority.tsv` ranks 15 of those sources for follow-up.

One row in `main_data.tsv` represents one experimental condition. The same Study ID therefore appears more than once when a paper tests multiple impurities, catalyst formulations, concentrations, or operating conditions. These are not duplicate sources unless the duplicate-check table says otherwise.

## Repository structure

```text
data/    Extracted data, source records, and follow-up lists
docs/    Research question, methodology, log, and data definitions
```

A `code/` folder will be added when the dataset is ready for analysis.

## Current limitations

- The research and source verification are incomplete.
- Some values were reported only in graphs and still require manual extraction.
- Some related reports and articles may contain the same underlying experiments.
- The dataset mixes several methanol metrics, so only compatible measurements can be compared.
- Sulfur and nitrogen impurities are much better represented than water, oxygen, and realistic impurity mixtures.
- The current data should not be used for industrial design or safety decisions.

The research-paper PDFs are not included in this repository.
