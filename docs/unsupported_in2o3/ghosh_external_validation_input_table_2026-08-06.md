# Ghosh-model input table for all collected unsupported-In2O3 conditions

**Checkpoint date:** 2026-08-06  
**Purpose:** Prepare every collected condition for a transparent test of the published Ghosh reactor model, with methanol yield as the primary comparison target.

## Files produced

- `data/processed/unsupported_in2o3/ghosh_all_collected_input_points.csv` contains 180 records: the 174 consolidated condition-level rows plus the six Ghosh SI input-only conditions.
- `data/processed/unsupported_in2o3/ghosh_yield_validation_candidates.csv` contains the 88 external clean unsupported-In2O3 conditions that have all four mass-normalized reactor inputs and an observed carbon-based methanol-yield target.

No source row was deleted or overwritten. Missing experimental values remain missing.

## Exact ReactorCase inputs

| ReactorCase field | Table column | Meaning |
|---|---|---|
| `run_id` | `reactorcase_run_id` | Unique condition identifier |
| `pressure_bar_reported` | `pressure_bar_reported` | Reported total reactor pressure in bar |
| `temperature_c` | `temperature_c` | Reactor temperature in degrees Celsius |
| `whsv_ml_gcat_h` | `whsv_ml_gcat_h` | Mass-normalized inlet gas flow in mL gcat^-1 h^-1 |
| `h2_co2_ratio` | `h2_co2_ratio` | Inlet molar H2/CO2 ratio |
| `catalyst_mass_g` | `catalyst_mass_g_for_reactorcase` | Reported physical mass when available; otherwise a documented 1 g normalization when WHSV is already mass-normalized |

`catalyst_mass_g_reported` always preserves the physical value from the source. A value of 1 g in `catalyst_mass_g_for_reactorcase` does not claim that the paper used 1 g. It is only a scale normalization when mass-normalized flow is already known.

## Observed methanol-yield target

The validation target is stored in `observed_meoh_yield_for_validation_percent`.

If the paper reports carbon-based methanol yield directly, the reported value is preserved. Otherwise, the table calculates:

```text
observed MeOH yield (%) = observed CO2 conversion (%)
                          * observed MeOH selectivity (%) / 100
```

The table preserves the reported and calculated values in separate columns and records which one supplies the comparison target.

## Yield-validation candidate summary

| Study | Rows | Phase(s) | Temperature (degC) | Pressure (bar) | H2/CO2 | WHSV (mL gcat^-1 h^-1) | Reported catalyst mass (g) | Inert | Observed yield range (%) | Rows inside Ghosh numeric domain |
|---|---:|---|---:|---:|---:|---:|---:|---|---:|---:|
| Becker 2026 | 2 | cubic | 300 | 20 | 3 | 351,000-422,000 | 0.0043-0.0051 | 20% N2 | 0.168-0.334 | 0 |
| Dang 2020 | 26 | cubic, hexagonal | 240-360 | 50 | 1-6 | 4,500-20,000 | 1.0 | 3% N2 in the temperature series; none recorded in other series | 3.133-16.262 | 0 |
| Sun 2015 | 24 | cubic | 250-350 | 10-40 | 3 | 15,000 | 0.2 | 20% N2 | 0.070-2.820 | 18 |
| Sun 2020 | 1 | cubic | 300 | 50 | 4 | 21,000 | 0.2 | 5% N2 | 5.870 | 0 |
| Wei 2025 | 9 | cubic | 220-300 | 10-50 | 3 | 7,200 | 0.5 | 4% N2 | 0.952-4.305 | 3 |
| Yang 2020 | 26 | cubic, rhombohedral | 260-360 | 20-50 | 4 | 8,000-32,000 | not reported | none recorded | 0.378-2.625 | 20 |
| **Total** | **88** |  |  |  |  |  |  |  |  | **41** |

The 88 rows contain 23 non-digitized conditions and 65 graph-digitized conditions. Extraction method and precision are retained for every row so those evidence types can be analyzed separately.

The machine-readable simulation gate further separates these candidates:

| Simulation gate | Rows |
|---|---:|
| Ready with the inert-aware wrapper | 50 |
| Ready with the current H2/CO2-only ReactorCase | 12 |
| Hold until Yang's GHSV/WHSV mass basis is confirmed | 26 |

## Why the table contains more than the six ReactorCase fields

The five numerical inputs plus `run_id` are sufficient to make the present code return a number. They are not sufficient to prove that the comparison is scientifically valid. The table therefore also preserves:

- catalyst identity and In2O3 phase;
- inert species and fraction;
- water and CO cofeed fractions;
- source catalyst mass and total flow;
- observed conversion, selectivity, yield, and STY;
- source location, DOI, and extraction method;
- Ghosh-domain status;
- catalyst-transfer status; and
- whole-study holdout group.

## Important compatibility findings

### 1. Inert gas

Fifty of the 88 candidate rows include N2. The original `ReactorCase` assumes that the inlet contains only H2 and CO2, so those rows require the inert-aware wrapper already tested during the Wei validation. Ignoring N2 would use incorrect reactant partial pressures.

### 2. Catalyst phase and preparation

The Ghosh model contains no phase input. Running hexagonal or rhombohedral In2O3 with the unchanged Ghosh parameters is a transfer test of the Ghosh architecture and parameter set. It is not evidence that the model accounts for phase.

Even cubic external catalysts differ from Ghosh in preparation, particle form, pretreatment, and bed dilution. The table labels them qualified transfers rather than identical catalysts.

### 3. Catalyst-mass basis

Ghosh obtained its best source reproduction when the full 1 g In2O3/silica composite bed was used as the kinetic mass. Most external studies report flow per gram of active In2O3 and treat quartz sand, SiC, or another material as an inert diluent.

The primary input column preserves each study's reported mass-normalized flow. The table also contains `whsv_composite_basis_sensitivity_ml_gcat_h`, equal to two-thirds of the external WHSV, for a predefined Ghosh-composite-equivalent sensitivity test. This alternative is an uncertainty scenario, not a corrected value.

### 4. Numeric extrapolation

Only 41 of the 88 candidate conditions fall inside all four Ghosh numeric ranges:

- 200-400 degC;
- 20-40 bar;
- H2/CO2 of 2-6; and
- WHSV of 6,000-16,000 mL gcat^-1 h^-1.

The remaining 47 must be labeled extrapolation tests before their predictions are inspected.

### 5. GHSV versus mass-normalized flow

Martin reports conventional GHSV for many rows without enough information to convert it to the mass-normalized WHSV required by `ReactorCase`; those conditions remain in the master table but are blocked. Yang's source uses GHSV terminology for the extracted space-velocity series, so its mass basis should be rechecked against the original source/SI before those values are treated as exact WHSV inputs.

This check is enforced in the `space_velocity_basis_status` and `simulation_gate` columns. The 26 Yang conditions are retained as yield-validation candidates but are placed on hold rather than marked ready to run.

## Status of every collected evidence branch

| Status | Rows |
|---|---:|
| External clean yield-validation candidate | 88 |
| Ghosh source reproduction | 32 |
| CO-containing feed branch excluded | 18 |
| Missing required mass-normalized ReactorCase input | 10 |
| Water-cofeed branch excluded | 10 |
| Ghosh SI inputs with condition-level outputs unavailable | 6 |
| Supporting-only rows | 5 |
| Duplicate conditions excluded | 4 |
| Complete inputs but no observed carbon-yield target | 4 |
| Doped/descriptor extension excluded | 3 |
| **Total** | **180** |

## Recommended validation order

1. Keep the 32 Ghosh rows as source reproduction only.
2. Preserve the completed nine-row Wei test as the first external study. Its conversion transferred well, but the unchanged model failed the methanol/CO product split.
3. Test Sun 2015 as a complete held-out study using the inert-aware wrapper and a separate digitization sensitivity analysis.
4. Test Yang 2020 with cubic and rhombohedral results reported separately, after verifying the space-velocity mass basis.
5. Test Dang 2020 with cubic and hexagonal results reported separately; identify the 50 bar conditions as pressure extrapolation.
6. Treat Becker 2026 and Sun 2020 as extreme/single-condition challenge tests rather than model calibration data.

Do not refit the Ghosh parameters while a paper is serving as a validation study. If later refitting is attempted, training studies must be selected first and at least one complete paper must remain untouched.
