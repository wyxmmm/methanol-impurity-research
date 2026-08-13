# Locked Ghosh-model test against the collected In2O3 studies

**Date:** 2026-08-12  
**Model:** Published Ghosh et al. 2021 single-site LHHW plug-flow model  
**Parameter status:** Locked; no kinetic, adsorption, or thermodynamic parameter was refitted.

## What was done

The 88 external clean unsupported-In2O3 conditions in `ghosh_yield_validation_candidates.csv` were passed through the Ghosh reactor simulator. Each row supplied:

- reported pressure;
- temperature;
- mass-normalized inlet flow or WHSV;
- H2/CO2 ratio;
- reported catalyst mass, or a documented 1 g normalization when only mass-normalized flow was available; and
- reported inert-gas fraction when present.

The simulator generated, for each condition:

- CO2 conversion;
- methanol, CO, and CH4 selectivity;
- methanol yield;
- methanol space-time yield;
- methanol outlet mole fraction;
- methanol molar flow; and
- methanol mass flow.

Predicted carbon-based methanol yield was calculated as:

```text
predicted MeOH yield (%) = predicted CO2 conversion (%)
                           * predicted MeOH selectivity (%) / 100
```

Every prediction was matched to the observed literature value, and signed error, absolute error, MAE, RMSE, and bias were calculated.

## Numerical verification

All 88 conditions converged. Increasing the integration grid from 800 to 1,600 steps changed the largest predicted methanol yield by only approximately `3.3e-12` percentage points. The observed model-data differences are therefore not numerical solver noise.

The inert-aware extension also reproduces the original simulator exactly when inert fraction is zero. It alters only inlet composition and partial-pressure accounting; it does not change the Ghosh reaction equations or parameters.

## Overall results

| Response | All-row MAE | Rows ready for interpretation, excluding Yang unit hold | Study-balanced mean MAE | Unit |
|---|---:|---:|---:|---|
| CO2 conversion | 2.124 | 1.817 | 2.197 | percentage points |
| Methanol selectivity | 18.479 | 15.233 | 13.870 | percentage points |
| Methanol yield | 2.067 | 1.788 | 1.796 | percentage points of inlet CO2 |
| Methanol STY | 0.0565 | 0.0565 | 0.0979 | g MeOH gcat^-1 h^-1 |

The all-row mean pools conditions, while the study-balanced value calculates one MAE per paper and then averages the paper errors. The latter prevents large studies from dominating.

## Results by complete external study

| Study | Rows | Conversion MAE | MeOH-selectivity MAE | MeOH-yield MAE | MeOH-STY MAE | Main interpretation |
|---|---:|---:|---:|---:|---:|---|
| Becker 2026 | 2 | 0.285 | 5.202 | 0.183 | 0.1759 | Low conversion/yield error, but extreme WHSV and only two conditions; useful challenge test, not broad validation. |
| Dang 2020 | 26 | 3.351 | 17.594 | 3.291 | 0.0813 | Model underpredicts yield, especially for high-performing phase-resolved conditions; all rows are outside the original pressure domain. |
| Sun 2015 | 24 | 0.684 | 15.078 | 0.674 | 0.0298 | Conversion transfers well, but methanol selectivity is generally overpredicted. Most responses were digitized from figures. |
| Sun 2020 | 1 | 5.687 | 7.180 | 3.285 | 0.1875 | One out-of-domain condition; challenge test only. |
| Wei 2025 | 9 | 0.320 | 11.951 | 0.609 | 0.0149 | Confirms the earlier result: total conversion transfers well, but the methanol-versus-CO product split does not. |
| Yang 2020 | 26 | 2.856 | 26.218 | 2.733 | unavailable | Predictions are exploratory because the source calls the flow quantity GHSV and its mass-normalized WHSV basis still needs confirmation. The model also cannot distinguish cubic from rhombohedral phase. |

## Scientific conclusion

The unchanged Ghosh model does **not** provide a generally transferable prediction of methanol selectivity across the collected unsupported-In2O3 studies.

The pattern is more specific than total model failure:

1. CO2 conversion often transfers reasonably well.
2. Methanol-versus-CO branching transfers poorly.
3. Because methanol yield combines conversion and selectivity, opposing errors can cancel and produce a deceptively moderate yield error.
4. A low yield MAE must therefore not be treated as proof that the kinetic mechanism or all reaction-specific parameters are validated.
5. Phase and preparation matter, but the current Ghosh model has no phase, morphology, surface-area, vacancy-density, or preparation input.

The result supports retaining the plug-flow reactor and three-reaction architecture as a starting point. It does not support treating the published numerical parameters as universal unsupported-In2O3 constants.

## Why parameters were not immediately tweaked

Changing the model to fit all 88 rows at once would use the same observations for fitting and validation. That would erase the independent test and could produce parameters that average chemically different cubic, hexagonal, and rhombohedral catalysts without physical meaning.

The next modification should therefore follow a prespecified structure:

1. verify Yang's GHSV/WHSV mass basis;
2. keep the original Ghosh reproduction fixed as a reference model;
3. choose compatible training studies before optimization;
4. retain at least one complete study as an untouched validation set;
5. test whether separate methanol/RWGS scaling factors or phase-specific effects are necessary;
6. constrain all refitted kinetic values to physically defensible ranges;
7. quantify parameter correlations and uncertainty; and
8. reject any adjustment that improves yield only through cancellation of conversion and selectivity errors.

## Files

- `results/ghosh_external_validation_all_studies/methanol_output_table.csv`: concise condition-by-condition outputs and errors.
- `results/ghosh_external_validation_all_studies/methanol_outputs_by_condition.csv`: complete audit table with every source and model field.
- `results/ghosh_external_validation_all_studies/study_summary.csv`: study-level errors.
- `results/ghosh_external_validation_all_studies/validation_metrics.csv`: all response and subgroup metrics.
- `results/ghosh_external_validation_all_studies/validation_decision.json`: machine-readable decision.
- `results/ghosh_external_validation_all_studies/validation_summary.md`: automatically generated summary.
