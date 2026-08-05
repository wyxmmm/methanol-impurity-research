# Catalyst 1 completion protocol

## Catalyst identity

Catalyst 1 is unsupported In2O3 used for gas-phase CO2 hydrogenation to
methanol. The primary source is Ghosh et al. (2021), DOI
`10.1016/j.cej.2021.129120`. In that experiment, unsupported In2O3 was
physically mixed with commercial silica in a 2:1 In2O3:silica mass ratio. The
silica is treated as an inert bed diluent, not as an active ZrO2-type support.

Internal identifier: `C1-U-In2O3-GHOSH`.

The model must not be labeled as supported In2O3, In2O3/ZrO2,
Cu/ZnO/Al2O3, a sulfur-poisoning model, or a universal catalyst model.

## Phase 1: scientific question

Within the experimentally supported operating range, can a plug-flow kinetic
model predict the clean-reactor performance of unsupported In2O3 for CO2
hydrogenation?

Required inputs are temperature, total pressure, H2/CO2 feed ratio, WHSV or
equivalent inlet flow, catalyst mass, and catalyst parameter-set identifier.
Required outputs are CO2 conversion; methanol flow, mole fraction,
selectivity, and productivity; CO and CH4 production and selectivity; outlet
composition; prediction-domain status; evidence-range information; and
validation status.

H2S/SO2 poisoning, water or CO cofeed, aging, regeneration, supported
In2O3/ZrO2, other catalysts, and unsupported extrapolation are excluded from
the initial Catalyst 1 claim.

## Phase 2: initial operating domain

| Variable | Initial domain |
| --- | --- |
| Temperature | 200-400 C |
| Pressure | 20-40 bar reported pressure |
| H2/CO2 ratio | 2-6 |
| WHSV | 6000-16000 mL gcat^-1 h^-1 |
| Reactor | Continuous gas-phase fixed bed |
| Feed | H2 and CO2 |
| Catalyst | Unsupported In2O3, Ghosh preparation family |
| Primary products | CH3OH, CO, CH4, and H2O |

The program must distinguish exact reported conditions, interpolation near
reported conditions, in-range but weakly supported combinations, and
out-of-domain requests. Out-of-domain predictions are refused by default.

## Phase 3: model architecture

The reactor is represented as one-dimensional, pseudo-homogeneous,
isothermal, isobaric, steady-state plug flow with no axial dispersion and
negligible heat- and mass-transfer resistance.

The reactions are:

1. CO2 + 3 H2 <=> CH3OH + H2O
2. CO2 + H2 <=> CO + H2O
3. CO2 + 4 H2 <=> CH4 + 2 H2O

The starting kinetic structure is the published single-site LHHW model with
competitive adsorption. The first parameter set uses the published Ghosh
values without refitting. The primary interpretation uses Table 4 adsorption
enthalpies, reported pressure as absolute, total composite bed mass, a 1-bar
standard state, NASA-7 equilibrium thermochemistry, and 22,414 mL/mol for
standard inlet-volume conversion. Every prediction records these assumptions.

## Phase 4: evidence eligibility

A direct validation study should report unsupported or bulk In2O3 without an
active support or metallic promoter, gas-phase CO2 hydrogenation in a
continuous flow reactor, temperature, pressure, H2/CO2 ratio, catalyst mass,
flow or space velocity, conversion or outlet CO2, methanol production, CO
production or selectivity, and the rate-normalization basis.

Preparation, calcination, pretreatment, surface area, particle size, inert
diluent, reactor dimensions, time on stream, condensation treatment, carbon
balance, and uncertainty are strongly preferred.

Evidence tiers are:

- Tier A: sufficiently compatible outside study with condition-level outputs;
- Tier B: unsupported In2O3 with meaningful preparation or morphology differences;
- Tier C: mechanistic or reaction-order evidence without complete outputs;
- Tier D: supported or different catalysts used for architecture only.

## Phase 5: complete the dataset

The Ghosh 32-condition calibration/reproduction set is complete. The six SI
validation inputs are complete, but their measured outputs are not tabulated
and anonymous parity points cannot be mapped reliably to individual runs.

The incomplete dataset block is independent unsupported-In2O3 evidence.
Candidate sources include Martin bulk-In2O3 experiments, Frei
unsupported-In2O3 experiments, and additional studies found through targeted
research. Each source must be audited for catalyst identity, preparation,
conditions, outputs, units, normalization, graph digitization, repeated
samples, independence groups, evidence tier, and incompatibilities.

## Phase 6: implementation verification

Required mathematical checks include elemental conservation, selectivity
closure, nonnegative flows, reverse-reaction behavior, positive equilibrium
constants, reference-temperature corrections, and unit consistency.

Required numerical checks include integration convergence, deterministic
results, successful execution of all 32 conditions, and clear rejection of
invalid inputs. The current 800-to-1600-step change is below 1e-12 percentage
points for the main outputs.

## Phase 7: primary-source reproduction

This phase is complete. With published parameters and no refitting, mean
absolute errors across the 32 conditions are 0.712 percentage points for CO2
conversion, 3.732 for MeOH selectivity, 3.538 for CO selectivity, and 0.288
for CH4 selectivity.

This is a `published-source reproduction`, not `independent validation`.

## Phase 8: external validation

The unchanged Ghosh parameters will first be applied to a compatible outside
study. The entire outside study remains held out; rows from one catalyst batch
must not be scattered across training and testing.

Report conversion and selectivity errors in percentage points, RMSE, bias,
productivity ratios or log error, residual plots, study-level summaries, and
experimental uncertainty. Do not use MAPE for near-zero responses.

Provisional targets, to be confirmed before final validation, are conversion
MAE no greater than 2 percentage points, MeOH-selectivity MAE no greater than
10 points, median MeOH-productivity error around 25% or less, correct
qualitative operating-condition trends, and no systematic residual pattern
indicating missing chemistry.

## Phase 9: diagnose failure before refitting

If external validation fails, check unit conventions, standard volume,
absolute/gauge pressure, total versus active mass, inert dilution,
condensation correction, preparation, surface area and particle size,
pretreatment, transport assumptions, missing pathways, and genuine
study-to-study variability. Explanations require evidence, not only improved
fit.

## Phase 10: decide whether refitting is justified

Refit only when multiple compatible condition-level datasets exist, units and
catalyst bases are reconciled, an entire study can remain held out,
parameters are identifiable, and uncertainty can be reported. Select training
studies before optimization, use physical parameter bounds, inspect
correlations, compare against the published set, reject physically
unreasonable solutions, and save a versioned parameter set plus training-data
fingerprint.

Otherwise retain the published parameters and label the model source-specific.

## Phase 11: uncertainty

Keep numerical, parameter, source-ambiguity, experimental, and cross-study
transfer uncertainties separate. Do not combine them into a statistical
confidence interval without enough evidence. Use clearly labeled sensitivity
or scenario ranges when formal uncertainty is unavailable.

## Phase 12: domain protection

The public interface must validate inputs, classify evidence proximity,
refuse unsupported extrapolation by default, report catalyst and parameter
identifiers, distinguish reproduction from external prediction, attach units
and model-version metadata, and warn that no impurity effect is included.

## Phase 13: versioned release

A Catalyst 1 release requires the curated source catalog, finalized dataset,
equations and parameters, executable model, external-validation results,
uncertainty analysis, tests, examples, limitations, chronological research
log, mentor-readable explanation, machine-readable decision, versioned
parameter set, and reproducible environment instructions.

The first complete release will be labeled `Catalyst-1 Unsupported-In2O3
v1.0`. Data, parameter, thermochemistry, or equation changes require a new
version.

## Phase 14: completion decision

- Outcome A: externally validated within the agreed criteria;
- Outcome B: source-specific but reproducible because outside validation is unavailable or unsuccessful;
- Outcome C: model form rejected after systematic unexplained external failure.

All are valid research outcomes. Only Outcome A supports broadly predictive
bounded use for unsupported In2O3.

## Phase 15: gate before another catalyst or impurity

A second catalyst can be added after the interface is stable, catalyst
identity and parameters are separated, validation status is machine-readable,
assumptions are explicit, and a new catalyst does not require rewriting the
reactor engine.

An impurity module requires an established clean model for the same catalyst,
known concentration and exposure, compatible clean and poisoned baselines,
preserved independence groups, and no silent borrowing from another catalyst.
