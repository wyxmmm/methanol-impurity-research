# Methodology

## Source selection

The current dataset comes from original studies that experimentally examine methanol synthesis under an impurity, contaminant, realistic gas mixture, or pre-poisoned catalyst condition. Reviews can help locate sources but are not counted as original experiments.

One original publication is counted as one source. If a paper tests several catalysts, impurities, concentrations, or operating conditions, each condition receives its own Experimental Row ID under the same Study ID.

## Data extraction

For each usable experiment, the extraction records the source, catalyst, impurity, operating conditions, methanol outcome, evidence location, and data-quality assessment. Values that appear only in figures are marked for manual extraction unless they have been deliberately digitized.

Missing information is not guessed. It is recorded as not reported, not accessible, partial access, or needing manual extraction.

## Baseline pairing

An impurity result can be paired only with a clean or reference condition from the same publication. The catalyst, outcome metric, unit, and major operating conditions must be comparable. Results from different papers are not paired as if they were one experiment.

When a valid pair exists, percent change is calculated as:

```text
100 x (value with impurity - baseline value) / baseline value
```

Calculated values are labeled separately from author-reported or digitized values.

## Duplicate checking

Related reports, theses, conference papers, and journal articles may describe the same underlying experiment. These records are retained for traceability, but suspected overlaps are marked in `data/duplicate_check.tsv` so they are not automatically treated as independent evidence.

## Planned analysis

Before modeling, the remaining graph values will be extracted, baseline links will be checked, duplicate experiments will be resolved, and incompatible outcome types will be separated. Python analysis will begin only after that review.
