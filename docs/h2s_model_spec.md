# H₂S Model Specification

Version 1.0.0 — 2026-07-29

## The question the first H₂S model will answer

The primary question is:

> For a Cu/ZnO/Al₂O₃ methanol-synthesis catalyst directly exposed to H₂S in the synthesis feed, what fraction of its clean-feed methanol activity remains after a defined exposure under defined operating conditions?

This is deliberately narrower than “What does sulfur do to methanol synthesis?” It defines one measurable target and prevents data from different physical experiments from being averaged merely because every paper mentions H₂S.

The primary response is the dimensionless activity-retention fraction:

\[
A(t) = \frac{\text{methanol output under H₂S at }t}
{\text{counterfactual clean-feed methanol output at }t}
\]

The numerator and denominator may be a methanol rate, productivity, yield, or a clearly defined normalized activity, but they must represent the same catalyst, metric, and reaction conditions. Methanol selectivity alone is not a valid output because selectivity can remain high while conversion collapses.

## How the clean counterfactual is chosen

The preferred denominator, in order, is:

1. The same run immediately before H₂S, corrected using an observed clean-feed aging trend.
2. A matched clean control measured at the same time on stream.
3. A paired clean baseline under the same catalyst and reaction conditions.

A cross-study average is never used as a missing baseline. That would make the model look complete by inserting a value that was not observed.

## The evidence architecture

The H₂S evidence is divided into explicit strata:

| Stratum | Scientific meaning | Core fit? |
|---|---|---:|
| `core_continuous_cuznal` | H₂S is continuously co-fed over Cu/ZnO/Al₂O₃ during methanol synthesis | Yes, if the fit gate is met |
| `continuous_other_cu` | Direct H₂S cofeed over another Cu-containing formulation | Separate formulation analysis |
| `ex_situ_damage` | Catalyst is pre-poisoned, then tested in clean synthesis gas | Separate retained-damage model |
| `sulfur_loading_response` | Activity is related to measured catalyst sulfur loading, but gas-phase exposure is incomplete | Separate loading model |
| `guard_bed_protection` | An upstream bed removes H₂S before the methanol catalyst | Process-protection analysis only |
| `non_cu_expansion` | Pd, In, or another non-Cu catalyst | Future catalyst-family expansion |
| `mechanism_only` | No quantitative methanol-synthesis target | Explanation and mechanistic constraints |

The strata can inform one another, but observations are never moved between them to increase sample size.

## Required variables

For the core continuous-cofeed dataset, an observation must identify:

- study and physical experimental unit;
- catalyst family and formulation;
- H₂S concentration;
- exposure time;
- reaction temperature and pressure;
- feed basis and composition or ratio;
- space velocity;
- methanol metric, clean/initial value, and H₂S value;
- retention or the information required to calculate it;
- reported/calculated/digitized status;
- exact source location; and
- duplicate cluster.

Feed composition will not be forced into a single ambiguous `H2:CO2` field. CO₂ hydrogenation and CO/CO₂ syngas are different feed bases. The model-ready schema will retain CO, CO₂, and H₂ fractions when reported, plus a labelled ratio appropriate to that feed.

## Evidence tiers

- **Tier A:** Exact primary quantitative evidence with numerical exposure, identified catalyst and conditions, a matched or aging-corrected baseline, and no unresolved duplicate.
- **Tier B:** Quantitative evidence with one material limitation, such as graph digitization, censoring, an initial point already under H₂S, incomplete metadata, or a separate exposure protocol.
- **Tier C:** Supporting evidence with a major confound or missing exposure variable, including guard-bed tests, flow-changed cumulative stages, or concentration-free sulfur-loading experiments.
- **Tier D:** Mechanism/context, non-methanol reactions, mixed-sulfur field service, or catalyst families outside the declared stratum.

Tier and stratum are separate concepts. For example, Schühle’s exact commercial-CZA value can be Tier A evidence for the `ex_situ_damage` stratum while remaining ineligible for the continuous-cofeed core.

## Duplicate and independence rules

The independent unit is the physical experimental run, not a spreadsheet row.

- Two papers reporting the same run belong to one duplicate cluster.
- Several outcomes from one run may be retained, but they are not counted as independent experiments.
- Several time points from one curve remain one study/run group.
- When duplicate reports exist, the clearest paired primary report is preferred, followed by exact table text, exact prose, digitized figure, and secondary citation.
- The Pd/CeO₂ series shared by T1-010 and T1-012 will be represented once.
- The suspected shared Pd/SiO₂ and Pd/Nd₂O₃ runs in T1-007 and T2-005 will be resolved before any non-Cu expansion.

## What “averaging the best available data” means

Averages are allowed only for genuine replicates measured at the same catalyst, conditions, exposure, and outcome. The replicate count and standard deviation must be preserved.

The following are not valid averages:

- different catalyst formulations;
- continuous cofeed mixed with ex-situ poisoning;
- methanol rate mixed with selectivity;
- H₂S mixed with total sulfur or COS;
- different pressure/temperature/feed conditions; or
- missing variables filled with the mean of other studies.

This preserves every useful paper without pretending that unlike experiments are replicates.

## Censoring and uncertainty

Statements such as “CO conversion fell below 1%” are bounds. They will be stored as left-censored values, not converted to an exact endpoint. Digitized values will keep their extraction status and a sensitivity range. Reported error bars and replicate counts will be used when available; otherwise uncertainty will be marked unavailable rather than invented.

All validation is grouped by study. The primary test is leave-one-study-out validation, holding out an entire paper/run group. A random row split is forbidden because nearby time points from one curve would leak into both training and testing.

## Gate for a universal fitted curve

A cross-study core model will be fitted only if the final audited dataset has all of the following:

- at least four independent studies;
- at least 20 independent experimental units;
- at least four distinct H₂S concentrations;
- at least two studies with matched or aging-corrected clean baselines;
- at least 80% completeness of the required core fields;
- no more than three free model parameters; and
- enough quantitative studies to hold out at least two entire studies.

If the evidence does not meet this gate, the correct deliverable is not a weak universal regression. It is a validated evidence engine containing source-specific kinetic calculations, bounded scenarios, protocol-specific comparisons, and an exact list of measurements needed to unlock the next model.

The machine-readable specification is `config/h2s_model_spec.json`.
