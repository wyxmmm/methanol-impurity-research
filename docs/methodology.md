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

## Planned computational analysis

The verified literature data will later be analyzed with Python. The purpose of the code will be to test whether impurity concentration, catalyst type, and operating conditions can help explain or predict changes in methanol performance.

The first stage will use summary statistics and graphs to examine the distribution of the data, differences among impurity categories, and the amount of missing information. Baseline and impurity observations will then be converted into comparable numerical outcomes when the metric, unit, catalyst, and operating conditions permit a valid comparison.

Possible model inputs include:

- impurity species, category, and concentration;
- catalyst family or composition;
- temperature and pressure;
- H2:CO2 ratio;
- space velocity;
- time on stream;
- exposure method, when consistently reported.

Separate analyses may be required for methanol yield, selectivity, productivity, normalized activity, and catalyst deactivation because these measurements do not represent the same outcome. Mechanistic observations and real-stream impurity measurements will be used to interpret results or define realistic scenarios, but they will not be treated as direct methanol-performance observations unless they contain compatible experimental outcomes.

The analysis will begin with simple, interpretable statistical models. More complex regression or machine-learning methods will be considered only if the verified dataset is large and consistent enough to support them. Model evaluation will separate studies by Study ID, rather than randomly mixing rows from the same paper between training and testing data. This is intended to reduce data leakage because several experimental rows can come from one publication. If the number of independent studies remains small, leave-one-study-out or grouped cross-validation will be considered instead of a single train-test split.

Results will include model accuracy, uncertainty, sensitivity to modeling choices, and the limitations created by missing or unevenly distributed evidence. Predictions will be presented as literature-derived estimates, not as replacements for laboratory experiments or industrial safety limits.

When coding begins, a `code/` folder will be added for the analysis scripts. Generated tables and figures will be kept separate from the original extracted data so that each step from literature values to final results can be checked and repeated.
