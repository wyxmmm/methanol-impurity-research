# Catalyst 1 completion protocol

Status updated through the 2026-08-12 external-transfer diagnostic.

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

The independent unsupported-In2O3 comparison dataset is assembled for the
current transfer test. It contains 88 clean-feed conditions from six outside
studies: 56 cubic, 19 hexagonal, and 13 rhombohedral conditions. Forty-one
conditions are inside every original Ghosh numeric range, and 65 response rows
were digitized from graphs. Catalyst preparation, phase, provenance, repeated
conditions, and study identity are preserved.

This dataset is complete for the Part A comparison, but it is not a uniform
Tier A validation set. The catalyst preparations differ, and the hexagonal and
rhombohedral conditions each come from only one study. These differences limit
what can be attributed to phase or transferred to a general catalyst model.

## Phase 6: implementation verification

Status: complete for the published-source reproduction and current external
comparison. All current automated tests pass.

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

Status: external transfer testing is complete; general external validation was
not achieved.

The unchanged Ghosh parameters were applied to all 88 outside conditions with
no refitting. All conditions produced numerical solutions. Mean absolute
errors were 2.124 percentage points for CO2 conversion, 18.479 for MeOH
selectivity, and 2.067 for MeOH yield. The study-balanced MAEs were 2.197,
13.870, and 1.796 percentage points, respectively.

Complete studies remained identifiable; rows from one catalyst batch were not
randomly divided and presented as independent studies.

Report conversion and selectivity errors in percentage points, RMSE, bias,
productivity ratios or log error, residual plots, study-level summaries, and
experimental uncertainty. Do not use MAPE for near-zero responses.

Provisional targets, to be confirmed before final validation, are conversion
MAE no greater than 2 percentage points, MeOH-selectivity MAE no greater than
10 points, median MeOH-productivity error around 25% or less, correct
qualitative operating-condition trends, and no systematic residual pattern
indicating missing chemistry.

The locked model exceeded the provisional conversion and MeOH-selectivity
targets. The result is therefore an unsuccessful general transfer test, not a
validated universal unsupported-In2O3 model.

## Phase 9: diagnose failure before refitting

Status: complete for the Part A diagnostic.

If external validation fails, check unit conventions, standard volume,
absolute/gauge pressure, total versus active mass, inert dilution,
condensation correction, preparation, surface area and particle size,
pretreatment, transport assumptions, missing pathways, and genuine
study-to-study variability. Explanations require evidence, not only improved
fit.

The current evidence indicates that methanol/RWGS branching is the clearest
transfer weakness. Large selectivity error remains inside the original numeric
domain and in non-digitized observations, so extrapolation and graph reading
are not sufficient explanations. Yang's mass-normalized flow basis was
resolved from the main article, and inert handling was not the dominant
residual pattern. Phase and preparation remain plausible contributors but are
confounded with study identity.

## Phase 10: decide whether refitting is justified

Status: unrestricted refitting is not justified and no external parameter was
refitted in Part A.

Refit only when multiple compatible condition-level datasets exist, units and
catalyst bases are reconciled, an entire study can remain held out,
parameters are identifiable, and uncertainty can be reported. Select training
studies before optimization, use physical parameter bounds, inspect
correlations, compare against the published set, reject physically
unreasonable solutions, and save a versioned parameter set plus training-data
fingerprint.

Otherwise retain the published parameters and label the model source-specific.

The present evidence supports keeping the published parameter set as the
locked benchmark. A later proof-of-concept may test only a predeclared,
bounded pair of MeOH and RWGS rate multipliers using complete-study
validation. Phase-specific parameters are not currently identifiable.

## Phase 11: uncertainty

Status: partial.

Keep numerical, parameter, source-ambiguity, experimental, and cross-study
transfer uncertainties separate. Do not combine them into a statistical
confidence interval without enough evidence. Use clearly labeled sensitivity
or scenario ranges when formal uncertainty is unavailable.

Numerical convergence and predefined source ambiguities have been tested.
Transfer uncertainty is visible across studies, phases, and preparations.
Most sources do not provide enough replicate or measurement uncertainty to
construct a combined statistical confidence interval.

## Phase 12: domain protection

Status: partial.

The public interface must validate inputs, classify evidence proximity,
refuse unsupported extrapolation by default, report catalyst and parameter
identifiers, distinguish reproduction from external prediction, attach units
and model-version metadata, and warn that no impurity effect is included.

The current code rejects invalid physical inputs and labels external rows as
inside or outside the original numeric ranges. A complete public interface
that refuses every unsupported extrapolation and classifies exact versus weak
interpolation is still unfinished.

## Phase 13: versioned release

Status: not complete.

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

Current decision: **Outcome B, source-specific but reproducible.** The Ghosh
source reproduction succeeded, but the locked model did not meet the
provisional external-transfer targets across the outside studies. This status
can change only if a later, predefined model and whole-study validation provide
new evidence.

## Phase 15: gate before another catalyst or impurity

Status: not yet satisfied for attaching an impurity response to this clean
model.

A second catalyst can be added after the interface is stable, catalyst
identity and parameters are separated, validation status is machine-readable,
assumptions are explicit, and a new catalyst does not require rewriting the
reactor engine.

An impurity module requires an established clean model for the same catalyst,
known concentration and exposure, compatible clean and poisoned baselines,
preserved independence groups, and no silent borrowing from another catalyst.

The unsupported-In2O3 model cannot be used as the clean baseline for the
In2O3/ZrO2 impurity experiments. A working impurity model must use a clean
baseline and poisoned observations from the same catalyst family.
