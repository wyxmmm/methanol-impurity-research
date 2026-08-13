# Mentor summary: unsupported-In2O3 Ghosh diagnostic

## What was tested

The published Ghosh unsupported-In2O3 PFR was kept completely locked and run
against 88 clean-feed conditions from six external studies. No external point
was used to refit a kinetic or adsorption parameter.

The audit separated catalyst phase, preparation, study, original numeric
domain, inert content, and whether the observed response was directly reported,
calculated, or graph-digitized.

## Yang correction

Yang's 26 rows were initially held because the article called the flow variable
GHSV. The supplied main article resolves the issue: Figure 2 explicitly gives
the unit as mL g-catalyst^-1 h^-1. The rows are therefore valid
mass-normalized-flow transfer tests. They remain lower-certainty because the
responses are digitized and physical catalyst mass is unreported.

## Result

All 88 simulations ran. This is software success, not experimental validation.

| Response | MAE | Main interpretation |
|---|---:|---|
| CO2 conversion | 2.124 percentage points | Transfers unevenly by study and phase |
| Methanol selectivity | 18.479 percentage points | Main failure; methanol/RWGS split is not transferable |
| Methanol yield | 2.067 percentage points | Moderate error partly hides opposing conversion/selectivity and cross-study errors |

The failure is directional: Dang is largely underpredicted, while Yang, Sun,
and Wei are often overpredicted in methanol selectivity. A single unrestricted
refit would average chemically different catalyst preparations rather than
identify a universal parameter set.

Phase appears important, but it cannot yet be separated from study: only Dang
supplies hexagonal evidence and only Yang supplies rhombohedral evidence.

## Decision

The next calibration experiment, if continued, should adjust only two global
quantities: a methanol-rate multiplier and an RWGS-rate multiplier. It should
start with cubic unsupported In2O3, use bounded/regularized parameters, and
select the structure through nested whole-study validation. The original locked
model remains the benchmark.

A phase-aware calibration should not yet be fitted. There are too few
independent non-cubic studies.

This work supports the clean-model methodology but does not itself model H2S
or the supported T1-001 In2O3/ZrO2 catalyst. The eventual impurity model still
requires a catalyst-matched clean baseline followed by a separately fitted H2S
retention layer.

