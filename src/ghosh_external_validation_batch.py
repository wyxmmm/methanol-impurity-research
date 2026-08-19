"""Run the locked Ghosh model across all external In2O3 yield candidates.

The published kinetic and adsorption parameters remain unchanged.  This batch
runner only supplies each study's reactor conditions, carries a reported inert
fraction when present, derives predicted methanol yield, and records external
comparison errors.  Rows with unresolved source-unit questions are predicted
for completeness but remain explicitly labeled exploratory.
"""

from __future__ import annotations

import argparse
import json
import math
from pathlib import Path
from typing import Any, Iterable

import numpy as np
import pandas as pd

from src.ghosh_in2o3_pfr import ReactorCase, simulate_case


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_INPUT = (
    ROOT
    / "data"
    / "processed"
    / "unsupported_in2o3"
    / "ghosh_yield_validation_candidates.csv"
)
DEFAULT_OUTPUT_DIR = ROOT / "results" / "ghosh_external_validation_all_studies"

REQUIRED_COLUMNS = {
    "study_id",
    "reactorcase_run_id",
    "pressure_bar_reported",
    "temperature_c",
    "whsv_ml_gcat_h",
    "h2_co2_ratio",
    "catalyst_mass_g_for_reactorcase",
    "inert_species",
    "inert_mole_fraction",
    "observed_co2_conversion_percent",
    "observed_meoh_selectivity_percent",
    "observed_meoh_yield_for_validation_percent",
    "observed_meoh_sty_g_gcat_h",
    "ghosh_numeric_domain_status",
    "simulation_gate",
}

RESPONSE_COLUMNS = {
    "co2_conversion": (
        "observed_co2_conversion_percent",
        "co2_conversion_percent_pred",
        "percentage_points",
    ),
    "meoh_selectivity": (
        "observed_meoh_selectivity_percent",
        "meoh_selectivity_percent_pred",
        "percentage_points",
    ),
    "meoh_yield": (
        "observed_meoh_yield_for_validation_percent",
        "meoh_yield_percent_pred",
        "percentage_points_of_inlet_CO2",
    ),
    "meoh_sty": (
        "observed_meoh_sty_g_gcat_h",
        "meoh_productivity_g_gcat_h_pred",
        "g_MeOH_gcat^-1_h^-1",
    ),
}


def _number(value: object, *, default: float | None = None) -> float | None:
    if pd.isna(value):
        return default
    number = float(value)
    return number if math.isfinite(number) else default


def load_candidates(path: Path = DEFAULT_INPUT) -> pd.DataFrame:
    data = pd.read_csv(path)
    missing = REQUIRED_COLUMNS - set(data.columns)
    if missing:
        raise ValueError(f"Missing required candidate columns: {sorted(missing)}")
    if data.empty:
        raise ValueError("Candidate input table is empty")
    if data["reactorcase_run_id"].duplicated().any():
        raise ValueError("reactorcase_run_id must be unique")
    return data


def _prediction_interpretation(row: pd.Series) -> str:
    if str(row["simulation_gate"]).startswith("hold_"):
        return "exploratory_prediction_pending_space_velocity_basis_confirmation"
    if str(row["ghosh_numeric_domain_status"]) != "inside_Ghosh_numeric_domain":
        return "external_transfer_extrapolation"
    return "external_transfer_inside_Ghosh_numeric_domain"


def predict_rows(data: pd.DataFrame, *, integration_steps: int = 800) -> pd.DataFrame:
    records: list[dict[str, Any]] = []
    for row in data.itertuples(index=False):
        source = row._asdict()
        inert_fraction = _number(source.get("inert_mole_fraction"), default=0.0) or 0.0
        inert_species = source.get("inert_species")
        if pd.isna(inert_species) or not str(inert_species).strip():
            inert_species = "none"
        case = ReactorCase(
            run_id=str(source["reactorcase_run_id"]),
            pressure_bar_reported=float(source["pressure_bar_reported"]),
            temperature_c=float(source["temperature_c"]),
            whsv_ml_gcat_h=float(source["whsv_ml_gcat_h"]),
            h2_co2_ratio=float(source["h2_co2_ratio"]),
            catalyst_mass_g=float(source["catalyst_mass_g_for_reactorcase"]),
            inert_mole_fraction=float(inert_fraction),
            inert_species=str(inert_species),
        )
        try:
            prediction = simulate_case(case, integration_steps=integration_steps)
            solver_converged = True
            solver_message = "success"
        except Exception as exc:  # preserve a failed row instead of losing it
            prediction = {}
            solver_converged = False
            solver_message = f"{type(exc).__name__}: {exc}"

        record: dict[str, Any] = dict(source)
        record.update(
            {
                "solver_converged": solver_converged,
                "solver_message": solver_message,
                "integration_steps": integration_steps,
                "prediction_interpretation": _prediction_interpretation(
                    pd.Series(source)
                ),
                "parameter_refit_performed": False,
                "parameter_set": "Ghosh_2021_published_single_site_locked",
                "absolute_methanol_flow_interpretation": (
                    "physical_source_mass"
                    if _number(source.get("catalyst_mass_g_reported")) is not None
                    else "normalized_1g_equivalent_not_physical_source_mass"
                ),
            }
        )
        record.update(prediction)

        if solver_converged:
            for response, (observed_col, predicted_col, _) in RESPONSE_COLUMNS.items():
                observed = _number(record.get(observed_col))
                predicted = _number(record.get(predicted_col))
                if observed is None or predicted is None:
                    record[f"{response}_signed_error_pred_minus_obs"] = None
                    record[f"{response}_absolute_error"] = None
                else:
                    residual = predicted - observed
                    record[f"{response}_signed_error_pred_minus_obs"] = residual
                    record[f"{response}_absolute_error"] = abs(residual)
        records.append(record)

    result = pd.DataFrame(records)
    if len(result) != len(data) or result["reactorcase_run_id"].duplicated().any():
        raise AssertionError("Every input row must produce exactly one output row")
    return result


def _metrics_for_group(
    group: pd.DataFrame,
    *,
    scope: str,
    study_id: str,
) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    for response, (observed_col, predicted_col, unit) in RESPONSE_COLUMNS.items():
        subset = group.loc[
            group["solver_converged"].eq(True)
            & group[observed_col].notna()
            & group[predicted_col].notna()
        ].copy()
        if subset.empty:
            continue
        observed = subset[observed_col].to_numpy(float)
        predicted = subset[predicted_col].to_numpy(float)
        residual = predicted - observed
        records.append(
            {
                "scope": scope,
                "study_id": study_id,
                "response": response,
                "n": len(subset),
                "mae": float(np.mean(np.abs(residual))),
                "rmse": float(np.sqrt(np.mean(residual**2))),
                "bias_pred_minus_obs": float(np.mean(residual)),
                "median_absolute_error": float(np.median(np.abs(residual))),
                "observed_min": float(np.min(observed)),
                "observed_max": float(np.max(observed)),
                "predicted_min": float(np.min(predicted)),
                "predicted_max": float(np.max(predicted)),
                "unit": unit,
            }
        )
    return records


def summarize_metrics(predictions: pd.DataFrame) -> pd.DataFrame:
    records: list[dict[str, Any]] = []
    records.extend(_metrics_for_group(predictions, scope="all_rows", study_id="ALL"))
    inside = predictions.loc[
        predictions["ghosh_numeric_domain_status"].eq("inside_Ghosh_numeric_domain")
    ]
    records.extend(
        _metrics_for_group(inside, scope="inside_Ghosh_numeric_domain", study_id="ALL")
    )
    non_digitized = predictions.loc[
        ~predictions["extraction_method"].fillna("").str.contains("digitized", case=False)
    ]
    records.extend(
        _metrics_for_group(non_digitized, scope="non_digitized_rows", study_id="ALL")
    )
    ready = predictions.loc[~predictions["simulation_gate"].str.startswith("hold_")]
    records.extend(
        _metrics_for_group(
            ready,
            scope="ready_rows_excluding_unit_hold",
            study_id="ALL",
        )
    )
    inside_ready = ready.loc[
        ready["ghosh_numeric_domain_status"].eq("inside_Ghosh_numeric_domain")
    ]
    records.extend(
        _metrics_for_group(
            inside_ready,
            scope="inside_domain_ready_rows",
            study_id="ALL",
        )
    )
    for study_id, group in predictions.groupby("study_id", sort=True):
        records.extend(
            _metrics_for_group(group, scope="complete_held_out_study", study_id=str(study_id))
        )
    return pd.DataFrame(records)


def _study_summary(metrics: pd.DataFrame) -> pd.DataFrame:
    study = metrics.loc[metrics["scope"].eq("complete_held_out_study")].copy()
    pivot = study.pivot(index="study_id", columns="response", values="mae")
    counts = study.pivot(index="study_id", columns="response", values="n")
    output = pd.DataFrame(index=pivot.index)
    for response in RESPONSE_COLUMNS:
        output[f"{response}_n"] = counts.get(response)
        output[f"{response}_mae"] = pivot.get(response)
    return output.reset_index()


def _markdown(metrics: pd.DataFrame, predictions: pd.DataFrame) -> str:
    studies = _study_summary(metrics)

    def value(row: pd.Series, name: str, digits: int = 3) -> str:
        item = row.get(name)
        return "—" if pd.isna(item) else f"{float(item):.{digits}f}"

    rows = []
    for _, row in studies.iterrows():
        rows.append(
            "| "
            + " | ".join(
                [
                    str(row["study_id"]),
                    str(int(row["meoh_yield_n"])),
                    value(row, "co2_conversion_mae"),
                    value(row, "meoh_selectivity_mae"),
                    value(row, "meoh_yield_mae"),
                    value(row, "meoh_sty_mae", 4),
                ]
            )
            + " |"
        )

    all_metrics = metrics.loc[
        metrics["scope"].eq("all_rows") & metrics["study_id"].eq("ALL")
    ].set_index("response")
    inside_metrics = metrics.loc[
        metrics["scope"].eq("inside_Ghosh_numeric_domain")
        & metrics["study_id"].eq("ALL")
    ].set_index("response")
    non_digitized_metrics = metrics.loc[
        metrics["scope"].eq("non_digitized_rows") & metrics["study_id"].eq("ALL")
    ].set_index("response")
    ready_metrics = metrics.loc[
        metrics["scope"].eq("ready_rows_excluding_unit_hold")
        & metrics["study_id"].eq("ALL")
    ].set_index("response")

    def metric(frame: pd.DataFrame, response: str) -> float:
        return float(frame.loc[response, "mae"])

    return f"""# Locked Ghosh-model predictions for all external In2O3 studies

## Run status

- Input conditions: {len(predictions)}
- Independent external studies: {predictions['study_id'].nunique()}
- Solver failures: {int((~predictions['solver_converged']).sum())}
- Rows inside every Ghosh numeric range: {int(predictions['ghosh_numeric_domain_status'].eq('inside_Ghosh_numeric_domain').sum())}
- Kinetic or adsorption parameters refitted: no

Every row was predicted with the published Ghosh single-site parameter set. Reported inert gas was carried through the reactor when present. Yang predictions were generated for completeness but remain exploratory until the source's GHSV/WHSV mass basis is confirmed.

## Overall errors

| Response | All rows MAE | In-domain MAE | Non-digitized MAE | Unit |
|---|---:|---:|---:|---|
| CO2 conversion | {metric(all_metrics, 'co2_conversion'):.3f} | {metric(inside_metrics, 'co2_conversion'):.3f} | {metric(non_digitized_metrics, 'co2_conversion'):.3f} | percentage points |
| MeOH selectivity | {metric(all_metrics, 'meoh_selectivity'):.3f} | {metric(inside_metrics, 'meoh_selectivity'):.3f} | {metric(non_digitized_metrics, 'meoh_selectivity'):.3f} | percentage points |
| MeOH yield | {metric(all_metrics, 'meoh_yield'):.3f} | {metric(inside_metrics, 'meoh_yield'):.3f} | {metric(non_digitized_metrics, 'meoh_yield'):.3f} | percentage points of inlet CO2 |
| MeOH STY | {metric(all_metrics, 'meoh_sty'):.4f} | {metric(inside_metrics, 'meoh_sty'):.4f} | {metric(non_digitized_metrics, 'meoh_sty'):.4f} | g MeOH gcat^-1 h^-1 |

These pooled values are diagnostics only. They combine different catalyst preparations and phases, so the complete-study results below are the primary external-transfer evidence.

After excluding the 26 Yang rows with unresolved GHSV/WHSV mass basis, the 62 ready rows have conversion MAE {metric(ready_metrics, 'co2_conversion'):.3f} percentage points, MeOH-selectivity MAE {metric(ready_metrics, 'meoh_selectivity'):.3f} percentage points, and MeOH-yield MAE {metric(ready_metrics, 'meoh_yield'):.3f} percentage points. The unchanged model therefore transfers total conversion more successfully than the methanol/CO product split.

## Complete-study results

| Study | Yield rows | Conversion MAE (pp) | MeOH selectivity MAE (pp) | MeOH yield MAE (pp) | MeOH STY MAE |
|---|---:|---:|---:|---:|---:|
{chr(10).join(rows)}

## Interpretation rules

- This is locked external testing, not refitting.
- Ghosh's 32 source rows are not included in these external errors.
- A prediction outside the original numeric domain remains an extrapolation even if the solver converges.
- Hexagonal and rhombohedral rows test transfer to a different phase; the Ghosh equations have no phase parameter.
- Graph-digitized observations remain lower-certainty comparisons.
- MAPE is intentionally not reported because several observed yields and conversions are close to zero.
"""


def build_outputs(
    input_path: Path = DEFAULT_INPUT,
    output_dir: Path = DEFAULT_OUTPUT_DIR,
    *,
    integration_steps: int = 800,
) -> dict[str, Any]:
    source = load_candidates(input_path)
    predictions = predict_rows(source, integration_steps=integration_steps)
    metrics = summarize_metrics(predictions)
    study_summary = _study_summary(metrics)

    output_dir.mkdir(parents=True, exist_ok=True)
    predictions.to_csv(output_dir / "methanol_outputs_by_condition.csv", index=False)
    concise_columns = [
        "study_id",
        "source_run_id",
        "catalyst_id",
        "in2o3_phase",
        "temperature_c",
        "pressure_bar_reported",
        "whsv_ml_gcat_h",
        "h2_co2_ratio",
        "catalyst_mass_g_reported",
        "catalyst_mass_g_for_reactorcase",
        "inert_species",
        "inert_mole_fraction",
        "ghosh_numeric_domain_status",
        "simulation_gate",
        "prediction_interpretation",
        "observed_co2_conversion_percent",
        "co2_conversion_percent_pred",
        "co2_conversion_signed_error_pred_minus_obs",
        "observed_meoh_selectivity_percent",
        "meoh_selectivity_percent_pred",
        "meoh_selectivity_signed_error_pred_minus_obs",
        "observed_meoh_yield_for_validation_percent",
        "meoh_yield_percent_pred",
        "meoh_yield_signed_error_pred_minus_obs",
        "meoh_yield_absolute_error",
        "observed_meoh_sty_g_gcat_h",
        "meoh_productivity_g_gcat_h_pred",
        "meoh_outlet_mole_fraction_pred",
        "meoh_outlet_mol_s_pred",
        "meoh_outlet_g_h_pred",
        "absolute_methanol_flow_interpretation",
        "solver_converged",
        "extraction_method",
        "source_location",
        "doi",
    ]
    predictions.loc[:, concise_columns].to_csv(
        output_dir / "methanol_output_table.csv", index=False
    )
    metrics.to_csv(output_dir / "validation_metrics.csv", index=False)
    study_summary.to_csv(output_dir / "study_summary.csv", index=False)

    all_yield = metrics.loc[
        metrics["scope"].eq("all_rows")
        & metrics["study_id"].eq("ALL")
        & metrics["response"].eq("meoh_yield")
    ].iloc[0]
    ready_metrics = metrics.loc[
        metrics["scope"].eq("ready_rows_excluding_unit_hold")
        & metrics["study_id"].eq("ALL")
    ].set_index("response")
    decision = {
        "model": "Ghosh_2021_published_single_site_LHHW_PFR",
        "parameter_refit_performed": False,
        "external_conditions_predicted": int(len(predictions)),
        "external_studies": int(predictions["study_id"].nunique()),
        "solver_failures": int((~predictions["solver_converged"]).sum()),
        "inside_numeric_domain_rows": int(
            predictions["ghosh_numeric_domain_status"]
            .eq("inside_Ghosh_numeric_domain")
            .sum()
        ),
        "yield_mae_all_rows_percentage_points": float(all_yield["mae"]),
        "yield_bias_pred_minus_obs_percentage_points": float(
            all_yield["bias_pred_minus_obs"]
        ),
        "ready_rows_excluding_unit_hold": int(
            (~predictions["simulation_gate"].str.startswith("hold_")).sum()
        ),
        "ready_rows_conversion_mae_percentage_points": float(
            ready_metrics.loc["co2_conversion", "mae"]
        ),
        "ready_rows_meoh_selectivity_mae_percentage_points": float(
            ready_metrics.loc["meoh_selectivity", "mae"]
        ),
        "ready_rows_meoh_yield_mae_percentage_points": float(
            ready_metrics.loc["meoh_yield", "mae"]
        ),
        "study_balanced_metrics": {
            response: {
                "mean_study_mae": float(
                    study_summary[f"{response}_mae"].dropna().mean()
                ),
                "studies": int(
                    study_summary[f"{response}_mae"].notna().sum()
                ),
                "unit": RESPONSE_COLUMNS[response][2],
            }
            for response in RESPONSE_COLUMNS
        },
        "scientific_status": "unchanged Ghosh parameters do not provide general cross-study product-selectivity transfer; diagnose before refit",
        "unit_hold": "Yang 2020 predictions are exploratory pending GHSV/WHSV mass-basis confirmation",
    }
    (output_dir / "validation_decision.json").write_text(
        json.dumps(decision, indent=2) + "\n", encoding="utf-8"
    )
    (output_dir / "validation_summary.md").write_text(
        _markdown(metrics, predictions), encoding="utf-8"
    )
    return decision


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, default=DEFAULT_INPUT)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    parser.add_argument("--integration-steps", type=int, default=800)
    args = parser.parse_args()
    print(
        json.dumps(
            build_outputs(
                args.input,
                args.output_dir,
                integration_steps=args.integration_steps,
            ),
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
