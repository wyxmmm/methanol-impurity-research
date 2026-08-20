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

## Current evidence and model decision

The audit produced 75 curated observations and 38 source-specific kinetic
records. However, only one observation satisfies the strict core definition:
continuous H2S exposure over a commercial Cu/ZnO/Al2O3 catalyst during
methanol synthesis with a usable clean baseline.

That observation used 8.1 ppm H2S at 240 C and 20 bar. The catalyst retained
approximately 90% normalized methanol activity after 30 hours. It represents
one study, one experimental condition, and one H2S concentration.

| Universal-fit requirement | Required | Available |
|---|---:|---:|
| Independent studies | 4 | 1 |
| Independent experimental units | 20 | 1 |
| H2S concentrations | 4 | 1 |
| Studies with usable clean baselines | 2 | 1 |

The universal-fit gate therefore fails. No universal H2S curve was fitted.
This is a scientific evidence limitation, not a software failure. Holding out
the sole eligible study would leave no evidence for training a model.

## Implemented source-specific tools

`src/h2s_evidence_engine.py` preserves five calculations without treating
them as one interchangeable dataset:

| Tool | Calculation | Allowed use |
|---|---|---|
| `prasnikar_cza_endpoint` | Interpolates normalized methanol activity between 0 and 30 h | Only at the reported 8.1 ppm, 240 C, 20 bar conditions |
| `wood_c79_exponential` | Applies `A(t) = exp(-k_obs t)` using a reported decay rate | Only for the exact 1.6, 3.2, or 33 ppm C79-1 runs |
| `he_matched_cox_proxy` | Compares digitized H2S and clean COx-conversion traces | A COx proxy, not methanol productivity |
| `ying_empirical_decomposition` | Interpolates reported methanol-decomposition activity | Only within the reported 211 ppm, 260 C time series |
| `ying_intrinsic_decomposition` | Evaluates Ying's fitted deactivation equation | Methanol decomposition, not methanol synthesis |

Each tool checks its own experimental domain and rejects unsupported inputs.
The Prašnikar interpolation, for example, cannot vary H2S concentration or
predict beyond 30 hours. Wood's reported rates are not used to invent a new
concentration-response curve. He remains labeled as a COx-conversion proxy,
and both Ying calculations remain labeled as methanol-decomposition evidence.

For Ying's reported 260 C and 211 ppm series, the intrinsic equation
reproduces the seven source activity values with a within-source MAE of about
0.0595 and RMSE of 0.0657. This checks the implementation of that source's
equation; it does not validate transfer to methanol synthesis.

## Uncertainty and interpretation

Reported uncertainty is preserved when available. Missing error bars remain
missing. Approximate and digitized values keep those labels. The He trace
includes a digitization-sensitivity range, which is not presented as a
statistical confidence interval. No confidence interval is invented from the
spread of incompatible experiments.

The defensible conclusion is:

> The available literature was sufficient to build source-specific H2S
> deactivation calculations and an auditable evidence structure, but
> insufficient to validate a universal cross-study methanol-activity model.

The project must not claim that the current engine predicts methanol loss for
any Cu/ZnO/Al2O3 catalyst at any H2S concentration.

## Running the evidence engine

Rebuild the generated H2S results with:

```powershell
python -m src.h2s_evidence_engine
```

Query the bounded commercial-CZA endpoint interpolation with:

```powershell
python -m src.h2s_evidence_engine `
  --model prasnikar_cza_endpoint `
  --h2s-ppm 8.1 `
  --time-h 20
```

The estimate is approximately 0.933 activity retention. It means only an
endpoint-anchored interpolation under that source's exact conditions.

## Evidence needed for a future model

The most useful new experiments would measure the same catalyst at several
H2S concentrations, several exposure times, fixed operating conditions,
matched clean-aging controls, methanol rate or yield, and replicate
uncertainty. Multiple independent studies would then be needed for
whole-study validation.

The machine-readable specification is `config/h2s_model_spec.json`.
