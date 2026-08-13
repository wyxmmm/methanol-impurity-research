# Part A: Locked Ghosh-model diagnostic audit

**Checkpoint date:** 2026-08-12

**Model:** Ghosh et al. 2021 unsupported-In2O3 LHHW PFR

**Parameter status:** locked; no kinetic, adsorption, or thermodynamic
parameter was fitted, optimized, or selected from the external data.

## Question answered

This checkpoint asks why the published clean unsupported-In2O3 model transfers
differently across external clean-feed studies. It is a diagnostic of the clean
baseline, not an H2S model and not an In2O3/ZrO2 model.

## Durable inputs preserved

The controlled 88-row candidate table, catalyst-descriptor table, and previous
locked-run output were read without modification. SHA-256 hashes before and
after the analysis were identical. All 88 input IDs occur exactly once in the
new audit and residual tables.

The new condition-level audit preserves the original fields and appends:

- audited space-velocity status;
- catalyst phase and preparation family;
- source-reported versus normalized catalyst-mass status;
- inert status;
- numeric-domain status;
- response-specific evidence provenance;
- Yang source-resolution status; and
- scientific interpretation status.

No source value was replaced. In particular, the original Yang `simulation_gate`
remains visible alongside the new `simulation_gate_audited` field.

## Checkpoint 1: evidence composition

| Item | Count |
|---|---:|
| External conditions | 88 |
| Independent studies | 6 |
| Cubic conditions | 56 |
| Hexagonal conditions | 19 |
| Rhombohedral conditions | 13 |
| Conditions inside every original Ghosh numeric range | 41 |
| Conditions outside or incomplete relative to that range | 47 |
| Graph-digitized rows | 65 |
| Non-graph-digitized rows | 23 |
| Solver failures | 0 |

The row-level evidence class gives precedence to graph digitization and then to
calculated/derived outputs. Response-specific provenance is also retained
because, for example, a directly reported conversion and selectivity can yield
a calculated methanol yield in the same row.

## Checkpoint 2: Yang GHSV/WHSV investigation

The supplied Yang main article is a seven-page corrected proof with DOI
`10.1016/j.cclet.2020.05.031`. Figure 2's caption explicitly reports the
temperature series at `16,000 mL g^-1 h^-1`; panel (e) labels the GHSV series
with the same mass-normalized unit.

This resolves the specific question that caused the previous hold: the plotted
space velocity is not merely an undefined reactor-volume GHSV in h^-1. It is a
gas-volume flow normalized by catalyst mass. A declared 1 g normalization
therefore preserves the feed-to-catalyst ratio used for conversion,
selectivity, and yield. It does not create a physical absolute methanol flow,
because the actual catalyst mass and total flow remain unreported.

Decision:

- all 26 Yang rows are released from the unit hold;
- they are included in primary residual summaries;
- they remain explicitly lower-certainty because all response values are
  graph-digitized;
- their physical absolute methanol flow remains unavailable; and
- the SI is still useful for synthesis and detailed product tables, but is no
  longer a blocker for the mass-normalized-flow interpretation.

## Checkpoint 3: locked residual results

Residual means prediction minus observation. All values below are percentage
points.

| Response | n | MAE | RMSE | Bias | Study-balanced MAE |
|---|---:|---:|---:|---:|---:|
| CO2 conversion | 88 | 2.124 | 3.219 | -0.508 | 2.197 |
| Methanol selectivity | 88 | 18.479 | 20.780 | +6.907 | 13.870 |
| Methanol yield | 88 | 2.067 | 2.685 | +0.036 | 1.796 |

The observed medians are 5.1% conversion, 48.165% methanol selectivity, and
1.85% methanol yield. Consequently, the conversion MAE is smaller in absolute
percentage points than the selectivity MAE but is not negligible relative to
the low conversion scale.

### Complete-study direction of error

| Study | n | Conversion MAE / bias | Selectivity MAE / bias | Yield MAE / bias |
|---|---:|---:|---:|---:|
| Becker 2026 | 2 | 0.285 / -0.285 | 5.202 / -5.202 | 0.183 / -0.183 |
| Dang 2020 | 26 | 3.351 / -3.194 | 17.594 / -15.801 | 3.291 / -3.224 |
| Sun 2015 | 24 | 0.684 / +0.142 | 15.078 / +12.334 | 0.674 / +0.674 |
| Sun 2020 | 1 | 5.687 / -5.687 | 7.180 / +7.180 | 3.285 / -3.285 |
| Wei 2025 | 9 | 0.320 / -0.287 | 11.951 / +10.715 | 0.609 / +0.462 |
| Yang 2020 | 26 | 2.856 / +1.685 | 26.218 / +24.208 | 2.733 / +2.705 |

This sign reversal is central. A single untargeted parameter change could
improve one catalyst preparation while worsening another.

### Numeric-domain comparison

| Domain | Response | n | MAE | Bias |
|---|---|---:|---:|---:|
| Inside | Conversion | 41 | 1.646 | +1.111 |
| Inside | Selectivity | 41 | 19.881 | +17.094 |
| Inside | Yield | 41 | 1.699 | +1.681 |
| Outside/incomplete | Conversion | 47 | 2.542 | -1.920 |
| Outside/incomplete | Selectivity | 47 | 17.255 | -1.980 |
| Outside/incomplete | Yield | 47 | 2.389 | -1.398 |

Operating outside the original range worsens conversion and yield on average,
but it does not explain the selectivity failure: selectivity MAE is also large
inside the original numeric ranges.

### Phase comparison and its limitation

| Phase | Studies | n | Conversion MAE | Selectivity MAE | Yield MAE |
|---|---:|---:|---:|---:|---:|
| Cubic | 6 | 56 | 1.608 | 17.138 | 1.428 |
| Hexagonal | 1 | 19 | 2.182 | 19.818 | 3.272 |
| Rhombohedral | 1 | 13 | 4.262 | 22.294 | 3.063 |

The apparent phase differences cannot be identified as phase effects:
hexagonal rows come only from Dang, and rhombohedral rows come only from Yang.
Phase, paper, preparation, morphology, and experimental protocol are therefore
confounded.

### Observation provenance

Response-specific comparisons show:

- conversion MAE 1.983 for 23 directly reported/non-digitized observations
  versus 2.174 for 65 digitized observations;
- selectivity MAE 15.322 for 22 directly reported observations versus 19.721
  for 65 digitized observations; and
- yield MAE 2.068 for 21 calculated/derived observations and 2.103 for 65
  digitized observations. Only two yield points are classed as entirely direct,
  so their 0.914 MAE cannot support a broad comparison.

Digitization adds uncertainty, but the branching problem is also present in
non-digitized results. It is not only a graph-reading artifact.

## Checkpoint 4: residual patterns

The diagnostic plots show every individual condition; no smoothing curve is
used. Marker shapes distinguish evidence class, colors distinguish phase, and
black edges identify lower-certainty Yang points.

Descriptive rank correlations are not causal tests. The pooled results show
the strongest associations for:

- selectivity residual versus pressure: Spearman rho = -0.503;
- yield residual versus pressure: rho = -0.473;
- selectivity residual versus temperature: rho = +0.471; and
- yield residual versus temperature: rho = +0.506.

These pooled relationships are partly produced by different studies occupying
different operating ranges. Within-study patterns include:

- Wei selectivity residual versus temperature: rho = +0.858;
- Yang selectivity residual versus temperature: rho = +0.587;
- Yang yield residual versus temperature: rho = +0.724;
- Sun 2015 yield residual versus pressure: rho = +0.700; and
- Dang selectivity residual versus WHSV: rho = -0.541.

These patterns justify testing temperature and branching behavior in a future
calibration, but do not identify a universal activation-energy error.

Inert-fraction associations are weak in the pooled data (absolute rho below
0.13 for all three responses). Only a few studies and inert fractions are
represented, so this finding means there is no current evidence that the inert
implementation is the dominant error; it is not proof that inert handling is
universally correct.

## Yield error cancellation

The exact yield-error decomposition was calculated for every row:

```text
yield error = conversion contribution
              + selectivity contribution
              + interaction contribution
```

Thirty-two of 88 rows have opposite-signed conversion and selectivity
contributions. Cross-study cancellation is also visible: Dang's mean yield
bias is -3.224 points while Yang's is +2.705 points, producing an all-row mean
yield bias close to zero. The small pooled signed bias therefore does not mean
the model predicts individual yields accurately.

## Predefined adsorption-enthalpy sensitivity

The Ghosh source has a documented inconsistency between its Table 4 and prose
assignment of the H2 and CO2 adsorption enthalpies. Both assignments were run
without fitting.

| Assignment | Conversion MAE | Selectivity MAE | Yield MAE |
|---|---:|---:|---:|
| Published Table 4 | 2.124 | 18.479 | 2.067 |
| Published prose, swapped | 2.154 | 18.864 | 2.019 |

The swapped assignment slightly improves yield MAE while worsening conversion
and selectivity. Selecting it on yield alone would repeat the error-cancellation
problem. The published Table 4 assignment remains the locked reference.

## Checkpoint 5: failure-mode diagnosis

### Direct evidence

1. **Methanol/RWGS branching is the clearest weakness.** Selectivity MAE is
   18.479 points and remains 19.881 points inside the source numeric domain,
   whereas conversion MAE is 2.124 points.
2. **Total reaction-rate transfer is imperfect.** Conversion errors are small
   for Wei, Becker, and Sun 2015 but materially larger and systematically
   negative for Dang and positive for the rhombohedral Yang cohort.
3. **Temperature behavior is study-dependent.** Selectivity and yield
   residuals rise with temperature in Wei and Yang, but the same universal
   trend is not present in every study.
4. **Phase/preparation differences are plausible but not separately
   identifiable.** The non-cubic phases each occur in only one study.
5. **Extrapolation contributes but is not the sole cause.** Large selectivity
   error exists inside the original numeric domain.
6. **Yang flow normalization is not the remaining explanation.** The main
   article directly verifies mass-normalized units.
7. **Inert treatment is not currently the dominant pattern.** The evidence is
   limited and should not be overgeneralized.

### Scientific inference

The pattern is consistent with the published numerical rate balance being less
transferable than the PFR bookkeeping and reaction network. In particular, the
relative methanol and RWGS rates likely require catalyst-domain calibration.
This is an inference from residual structure, not proof that the published
mechanism is wrong. Different vacancy populations, facets, morphology,
pretreatment, and time on stream could all change the apparent branching.

## Checkpoint 6: candidate calibration structures

No candidate was fitted in Part A.

### Candidate 1: locked Ghosh reference

- **Adjustable parameters:** none.
- **Role:** permanent no-calibration benchmark.
- **Risk:** cannot capture cross-study branching differences.
- **Domain:** clean unsupported In2O3 only.
- **Validation:** every future calibrated model must outperform it on complete
  held-out studies for conversion and selectivity separately, not just yield.

### Candidate 2: two global reaction-rate multipliers

```text
r_MeOH* = alpha_MeOH x r_MeOH,Ghosh
r_RWGS* = alpha_RWGS x r_RWGS,Ghosh
```

- **Adjustable parameters:** two positive multipliers; methane parameters stay
  locked.
- **Physical interpretation:** limited correction to the relative methanol and
  RWGS rate magnitudes.
- **Data:** begin with cubic unsupported-In2O3 conditions and preserve
  response-specific evidence weights.
- **Identifiability risk:** the two multipliers can be correlated; yield alone
  cannot identify them.
- **Overfitting risk:** moderate with six external studies; control using
  bounded parameters, regularization, and nested whole-study validation.
- **Domain:** unsupported In2O3. It does not become In2O3/ZrO2 merely through
  calibration.
- **Decision:** this is the first structure that should be tested in Part B of
  the clean-model work, after its train/validation studies and bounds are
  declared.

### Candidate 3: phase-aware hierarchical deviations

```text
log(alpha_reaction,phase) = log(alpha_reaction,global)
                            + delta_reaction,phase
```

- **Adjustable parameters:** global multipliers plus shrunken phase deviations.
- **Potential benefit:** represent systematic phase-specific branching.
- **Current identifiability:** insufficient. Hexagonal and rhombohedral phases
  each have only one independent study.
- **Overfitting risk:** high; phase deviations would absorb study and
  preparation effects.
- **Decision:** defer until at least two independent studies per non-cubic
  phase are available.

## Recommendation

Limited calibration may proceed as an unsupported-In2O3 proof of concept, but
only with Candidate 2, cubic-first analysis, declared bounds/regularization,
and nested complete-study validation. Candidate 1 must remain the benchmark.
Candidate 3 is not currently defensible.

The clean model must then be frozen before an impurity layer is fitted. This
calibration cannot directly supply the clean baseline for the T1-001
In2O3/ZrO2 sulfur experiments. A separate catalyst-matching audit must decide
whether clean In2O3/ZrO2 evidence can support its own baseline or only a bounded
source-specific model.

## Verification boundary

The software tests and numerical runs establish reproducibility and data
integrity. They do not experimentally validate the chemistry. Experimental
validation requires predictions for complete source-independent studies using
compatible catalyst and output definitions.

## Outputs

- `results/ghosh_part_a_diagnostic_2026-08-12/input_provenance_audit.csv`
- `results/ghosh_part_a_diagnostic_2026-08-12/locked_residuals_by_condition.csv`
- `results/ghosh_part_a_diagnostic_2026-08-12/grouped_diagnostic_metrics.csv`
- `results/ghosh_part_a_diagnostic_2026-08-12/residual_trend_summary.csv`
- `results/ghosh_part_a_diagnostic_2026-08-12/adsorption_assignment_sensitivity_by_condition.csv`
- `results/ghosh_part_a_diagnostic_2026-08-12/adsorption_assignment_sensitivity_metrics.csv`
- `results/ghosh_part_a_diagnostic_2026-08-12/plots/`
- `results/ghosh_part_a_diagnostic_2026-08-12/data_integrity_manifest.json`
- `results/ghosh_part_a_diagnostic_2026-08-12/diagnostic_decision.json`
