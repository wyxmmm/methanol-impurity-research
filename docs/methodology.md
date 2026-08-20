# Methodology

This document records the rules I use to decide which literature results can
be compared. The purpose is to prevent a larger-looking dataset from hiding
important differences between catalysts, exposure methods, and methanol
measurements.

## Source selection

I use original studies that experimentally examine methanol synthesis under an
impurity, contaminant, realistic gas mixture, or pre-poisoned catalyst
condition. Reviews can help me locate sources, but I do not count them as
original experiments.

One original publication is counted as one source. If a paper tests several catalysts, impurities, concentrations, or operating conditions, each condition receives its own Experimental Row ID under the same Study ID.

## Data extraction

For each usable experiment, I record the source, catalyst, impurity, operating
conditions, methanol outcome, evidence location, and data-quality assessment.
Values that appear only in figures are marked for manual extraction unless
they have been deliberately digitized.

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

## Catalyst-specific modeling sequence

I separate a clean-catalyst model from the impurity-response calculation. The
first clean model is unsupported In2O3. It reproduced its source, but the
outside-study test showed that it remains source-specific. I therefore cannot
quietly reuse its numerical parameters for supported In2O3/ZrO2 or attach an
In2O3/ZrO2 impurity response to it.

## How I analyze the models

I use Python to test whether impurity concentration, catalyst type, and
operating conditions can help explain or predict changes in methanol
performance. I begin with transparent calculations and plots before
considering a fitted model.

Summary statistics and graphs are used to examine the distribution of the
data, differences among impurity categories, and missing information.
Baseline and impurity observations are converted into comparable numerical
outcomes only when the metric, unit, catalyst, and operating conditions permit
a valid comparison.

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

The Ghosh unsupported-In2O3 implementation uses the reported single-site LHHW
rates in a plug-flow reactor. Published parameters are tested without
refitting first. Source reproduction uses all 32 reported conditions, while
external validation must hold out an entire compatible outside study.
Generated tables and figures remain separate from committed source-derived
inputs so each calculation can be checked and repeated.

Model evaluation reports conversion and selectivity errors in percentage
points, RMSE, bias, productivity ratios or log error, qualitative operating-
condition trends, numerical convergence, and sensitivity to source
ambiguities. MAPE is avoided for near-zero outcomes. Refitting is permitted
only if multiple compatible datasets exist, one complete study remains held
out, parameters are identifiable, and uncertainty can be reported.

## Equation governance

Every mathematical operation used for a reported model result is recorded in
`docs/model_equation_registry.md`. Each entry identifies the equation,
variables and units, source or project derivation, applicability domain, and
implementation status. This separates published kinetic equations from
project-derived conversions and from candidate equations that have not been
implemented or validated.

The registry also preserves the model hierarchy used by this project:

```text
operating conditions -> clean-catalyst methanol output
                     -> impurity-retention response
                     -> impurity-affected methanol output
```

The clean-catalyst layer is necessary for the final impurity question, but it
is not itself the endpoint. Equations and fitted values cannot be transferred
between unsupported In2O3, supported In2O3/ZrO2, and Cu/ZnO/Al2O3 without an
explicit evidence bridge and a documented validation decision.
