# Locked Ghosh-model predictions for all external In2O3 studies

## Run status

- Input conditions: 88
- Independent external studies: 6
- Solver failures: 0
- Rows inside every Ghosh numeric range: 41
- Kinetic or adsorption parameters refitted: no

Every row was predicted with the published Ghosh single-site parameter set. Reported inert gas was carried through the reactor when present. Yang predictions were generated for completeness but remain exploratory until the source's GHSV/WHSV mass basis is confirmed.

## Overall errors

| Response | All rows MAE | In-domain MAE | Non-digitized MAE | Unit |
|---|---:|---:|---:|---|
| CO2 conversion | 2.124 | 1.646 | 1.983 | percentage points |
| MeOH selectivity | 18.479 | 19.881 | 14.968 | percentage points |
| MeOH yield | 2.067 | 1.699 | 1.967 | percentage points of inlet CO2 |
| MeOH STY | 0.0565 | 0.0333 | 0.0792 | g MeOH gcat^-1 h^-1 |

These pooled values are diagnostics only. They combine different catalyst preparations and phases, so the complete-study results below are the primary external-transfer evidence.

After excluding the 26 Yang rows with unresolved GHSV/WHSV mass basis, the 62 ready rows have conversion MAE 1.817 percentage points, MeOH-selectivity MAE 15.233 percentage points, and MeOH-yield MAE 1.788 percentage points. The unchanged model therefore transfers total conversion more successfully than the methanol/CO product split.

## Complete-study results

| Study | Yield rows | Conversion MAE (pp) | MeOH selectivity MAE (pp) | MeOH yield MAE (pp) | MeOH STY MAE |
|---|---:|---:|---:|---:|---:|
| BECKER-2026 | 2 | 0.285 | 5.202 | 0.183 | 0.1759 |
| DANG-2020 | 26 | 3.351 | 17.594 | 3.291 | 0.0813 |
| SUN-2015 | 24 | 0.684 | 15.078 | 0.674 | 0.0298 |
| SUN-2020 | 1 | 5.687 | 7.180 | 3.285 | 0.1875 |
| WEI-2025 | 9 | 0.320 | 11.951 | 0.609 | 0.0149 |
| YANG-2020 | 26 | 2.856 | 26.218 | 2.733 | — |

## Interpretation rules

- This is locked external testing, not refitting.
- Ghosh's 32 source rows are not included in these external errors.
- A prediction outside the original numeric domain remains an extrapolation even if the solver converges.
- Hexagonal and rhombohedral rows test transfer to a different phase; the Ghosh equations have no phase parameter.
- Graph-digitized observations remain lower-certainty comparisons.
- MAPE is intentionally not reported because several observed yields and conversions are close to zero.
