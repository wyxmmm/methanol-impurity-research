# Ghosh model reproduction and supported-catalyst transfer decision

Checkpoint date: 2026-08-03; external-transfer diagnostic updated 2026-08-12

## Plain-language result

I first checked whether the code could reproduce the paper from which the
equations and parameters came. It could. I then kept those parameters fixed
and ran 88 conditions collected from six other papers. The program ran every
condition, but methanol selectivity often differed substantially from the
measurements. This means the code is reproducible while the numerical model is
still specific to the Ghosh catalyst rather than a general In2O3 predictor.

## Result in one sentence

The published unsupported-In2O3 model reproduces the Ghosh catalyst, but a
locked test across 88 conditions from six outside studies shows that its
numerical parameters do not provide a general cross-study product-selectivity
model. They also cannot be transferred as a validated model for supported
In2O3/ZrO2 or T1-001.

## Calibration reproduction

All 32 conditions in Ghosh Table 2 were simulated with the published
single-site parameters and no refitting. Under the primary source
interpretation, errors were:

| Response | Mean absolute error | RMSE | Bias |
| --- | ---: | ---: | ---: |
| CO2 conversion | 0.712 percentage points | 1.480 | -0.148 |
| MeOH selectivity | 3.732 percentage points | 6.770 | -1.927 |
| CO selectivity | 3.538 percentage points | 6.493 | +1.853 |
| CH4 selectivity | 0.288 percentage points | 0.432 | +0.076 |

The 300 °C, 40 bar, H2/CO2 = 3, WHSV = 9000 standard case predicts 5.689%
CO2 conversion and 66.262% MeOH selectivity, compared with reported values of
6.27% and 66.31%. Integration from 100 to 1600 RK4 steps changes the reported
outputs by less than the displayed precision, so the residual error is not a
numerical-integration artifact.

This is a source reproduction, not independent model validation. The same
dataset was used by the authors to estimate the parameters, although the
article is internally inconsistent about the role of Series 5.

## Source-ambiguity sensitivity

| Interpretation | Conversion MAE | MeOH-selectivity MAE |
| --- | ---: | ---: |
| Primary: Table 4, absolute pressure, total composite mass | 0.712 | 3.732 |
| Reported pressure treated as gauge | 0.728 | 3.826 |
| Only the active In2O3 mass integrated | 2.199 | 5.550 |
| Prose-swapped adsorption enthalpies | 0.895 | 4.439 |

This supports the selected primary convention, but does not eliminate the
unpublished-thermochemistry or pressure-convention uncertainty.

## Ghosh supplementary validation status

The six SI Table S3 conditions have been simulated and saved. A numerical
held-out score is not scientifically identifiable from the supplied files:
the SI gives inputs only, and the main article gives anonymous parity points
without condition labels. The code does not digitize and falsely pair those
points with the six runs.

## Locked external-transfer diagnostic

The unchanged published parameters were applied to 88 clean-feed conditions
from six outside unsupported-In2O3 studies. No kinetic, adsorption, or
thermodynamic parameter was fitted, optimized, or selected using those
conditions. Every row produced a numerical solution.

Residual means prediction minus observation. Errors are percentage points.

| Response | n | MAE | RMSE | Bias | Study-balanced MAE |
| --- | ---: | ---: | ---: | ---: | ---: |
| CO2 conversion | 88 | 2.124 | 3.219 | -0.508 | 2.197 |
| MeOH selectivity | 88 | 18.479 | 20.780 | +6.907 | 13.870 |
| MeOH yield | 88 | 2.067 | 2.685 | +0.036 | 1.796 |

The model's largest transfer weakness is methanol/RWGS branching. MeOH-
selectivity MAE remains 19.881 percentage points for the 41 conditions inside
the original numeric operating ranges, so extrapolation alone does not explain
the error. Directly reported/non-digitized observations also show substantial
selectivity error, so graph digitization is not the sole cause.

Study-level residuals reverse sign: the model underpredicts some preparation
families and overpredicts others. Apparent phase effects are not separately
identifiable because the hexagonal and rhombohedral evidence each comes from
only one study; phase, preparation, morphology, and study protocol are
confounded. Pooled yield bias is near zero partly because conversion and
selectivity errors cancel across conditions, not because individual yields
are uniformly accurate.

The predefined alternative adsorption-enthalpy assignment from the Ghosh
prose was tested without fitting. It changed conversion, selectivity, and
yield MAE to 2.154, 18.864, and 2.019 percentage points, respectively. Because
it slightly improves yield only by worsening the two component responses, the
published Table 4 assignment remains the locked reference.

This checkpoint establishes software reproducibility and diagnoses transfer
failure; it does not experimentally validate a universal unsupported-In2O3
model. Any future calibration should begin with the locked Ghosh model as the
benchmark and test only a predeclared, bounded pair of MeOH and RWGS rate
multipliers. Training and validation must keep complete studies together and
must judge conversion and selectivity separately rather than optimizing yield
alone. Phase-specific deviations are not currently identifiable.

## What the newly supplied supported-catalyst papers add

### Martin et al. 2016

For 9.2 wt% In on monoclinic ZrO2 at 300 °C, 50 bar, H2/CO2 = 4, and
GHSV = 16000 h^-1, the SI reports 0.295 g MeOH gcat^-1 h^-1, 5.2% CO2
conversion, 99.8% MeOH selectivity, and a 1000 h test. Particle-size and
flow tests also support the absence of transport limitation. This is strong
clean-catalyst evidence, but the approximately 100% selectivity differs
sharply from unsupported Ghosh In2O3 under nearby conditions.

### Wesner et al. 2023

Wesner reconstructs both the Schühle/Alfa-Aesar (`S-AA`) and Martin/
Saint-Gobain (`M-SG`) preparations in one reactor. Its 20-point ascending and
descending ramps confirm that preparation route, support supplier, pressure,
and cycling history materially change conversion, productivity, and
selectivity. This is the best bridge to T1-001, but it is an empirical bridge,
not an intrinsic rate-parameter transfer.

### Jiang et al. 2020

At 250 °C and 50 bar over 9 wt% In2O3/m-ZrO2, adding only 0.1 mol% water
increased MeOH STY from 2.75 to 3.42 mol kgcat^-1 h^-1. This demonstrates a
product/feed-composition effect absent from the Ghosh calibration and shows
why a supported-catalyst model needs explicit evidence for water behavior.

### Tsoukalou et al. 2022

At 300 °C and 25 bar gauge, the intrinsic MeOH selectivity extrapolated to
zero conversion was 60% for m-ZrO2:In, 23% for In2O3/t-ZrO2, and 13% for
In2O3/am-ZrO2. The m-ZrO2:In MeOH STY decreased from 1.46 to
1.10 g MeOH gIn2O3^-1 h^-1 as contact time increased from 0.08 to
0.24 s g mL^-1, while conversion increased from 3.7% to 7.9%. This makes the
support phase and preparation part of the kinetic identity, not a cosmetic
descriptor.

## Transfer decision

The Ghosh equations remain a useful *architecture*: a PFR material balance,
three competing reactions, reversibility, and competitive adsorption. The
published Ghosh numerical parameters are not validated for T1-001 because:

- unsupported In2O3 and supported In2O3/ZrO2 have different active interfaces;
- In loading, support phase, support supplier, preparation, and dispersion
  materially change activity and selectivity;
- rate normalizations differ among gcat, gIn, and gIn2O3;
- the supported studies do not provide one compatible multivariable kinetic
  matrix from which all Ghosh parameters can be re-estimated;
- none of these clean studies supplies additional H2S poisoning kinetics.

## Scientifically defensible current code layers

`ghosh_in2o3_pfr.py` is the clean reactor simulator for the unsupported Ghosh
catalyst. The separate T1-001 supported-catalyst sulfur analysis is not part
of this Catalyst 1 release. Multiplying a Ghosh PFR prediction by a T1 sulfur
retention factor would combine two different catalysts and is not validated.

## Next research decision

For a final-output model of T1-001, the most defensible next step is not to
refit Ghosh parameters to a handful of heterogeneous supported-catalyst
points. Instead:

1. use the bounded T1 calculator for the exact sulfur scenarios already
   measured;
2. seek a condition-level kinetic dataset for the same Schühle-style
   In2O3/m-ZrO2 preparation, including conversion and outlet composition;
3. if that cannot be obtained, present the Ghosh simulator and the T1 sulfur
   calculator as two bounded case studies rather than a universal combined
   model.

## Reproducible artifacts

- `results/unsupported_in2o3/ghosh_pfr/calibration_predictions.csv`
- `results/unsupported_in2o3/ghosh_pfr/calibration_metrics.json`
- `results/unsupported_in2o3/ghosh_pfr/source_ambiguity_sensitivity.csv`
- `results/unsupported_in2o3/ghosh_pfr/validation_input_predictions.csv`
- `results/unsupported_in2o3/ghosh_pfr/integration_convergence.csv`
- `results/unsupported_in2o3/ghosh_pfr/model_reproduction_decision.json`
